import pytest
from app.services.parser_service import parse_invoice_response
from app.schemas.invoice import InvoiceData

def test_parse_invoice_response_clean_json():
    raw_json = '{"vendor": "Google", "invoice_number": "G-101", "total_amount": 250.5}'
    result = parse_invoice_response(raw_json)
    
    assert isinstance(result, InvoiceData)
    assert result.vendor == "Google"
    assert result.invoice_number == "G-101"
    assert result.total_amount == 250.5
    # confidence score should be calculated
    assert result.confidence_score > 0.0

def test_parse_invoice_response_markdown_fences():
    raw_markdown = '```json\n{\n  "vendor": "Microsoft",\n  "invoice_number": "MS-999"\n}\n```'
    result = parse_invoice_response(raw_markdown)
    
    assert isinstance(result, InvoiceData)
    assert result.vendor == "Microsoft"
    assert result.invoice_number == "MS-999"

def test_parse_invoice_response_regex_fallback():
    raw_dirty = 'Some explanation text here before JSON:\n{\n  "vendor": "Amazon",\n  "invoice_number": "AMZ-555"\n}\nSome trailing explanation here.'
    result = parse_invoice_response(raw_dirty)
    
    assert isinstance(result, InvoiceData)
    assert result.vendor == "Amazon"
    assert result.invoice_number == "AMZ-555"

def test_parse_invoice_response_validation_failure():
    # vendor needs to be a string or null, line_items should be list of LineItem, etc.
    # What if line_items contains invalid dict or a string?
    raw_invalid = '{"vendor": "Invalid", "line_items": "this should be a list"}'
    result = parse_invoice_response(raw_invalid)
    
    assert isinstance(result, InvoiceData)
    # Check that fallback empty model was returned
    assert result.vendor is None
    assert result.confidence_score == 0.0

def test_parse_invoice_response_complete_failure():
    # Non-JSON content
    raw_nonsense = 'This is just some random text with no JSON objects at all.'
    result = parse_invoice_response(raw_nonsense)
    
    assert isinstance(result, InvoiceData)
    assert result.vendor is None
    assert result.confidence_score == 0.0

def test_parse_invoice_response_confidence_calculation():
    # Only vendor and currency (default: None, overridden to None or default?)
    # Wait, in _empty_invoice_data we set currency=None.
    # If we load {"vendor": "Test Vendor", "currency": "USD"}, the non-null count is 2 (vendor and currency).
    # Since confidence score is non_null_count / 11, it should be 2/11 = 0.1818...
    raw = '{"vendor": "Test Vendor", "currency": "USD"}'
    result = parse_invoice_response(raw)
    
    assert result.vendor == "Test Vendor"
    assert result.currency == "USD"
    # non_null fields: vendor, currency, and line_items (defaulted to []) (total 3)
    # 3 / 11 = 0.2727272727272727
    assert result.confidence_score == pytest.approx(3 / 11)

