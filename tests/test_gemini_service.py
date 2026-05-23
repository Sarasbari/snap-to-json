import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.services.gemini_service import extract_invoice_data, GeminiExtractionError

@pytest.mark.asyncio
async def test_extract_invoice_data_success():
    # Mock response object returned by generate_content_async
    mock_response = MagicMock()
    mock_response.text = '{"vendor": "Mock Vendor", "invoice_number": "INV-100", "total_amount": 150.0}'
    
    # Mock GenerativeModel and its generate_content_async method
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    # Patch genai.GenerativeModel and genai.configure
    with patch("google.generativeai.GenerativeModel", return_value=mock_model) as mock_model_class, \
         patch("google.generativeai.configure") as mock_configure:
         
        dummy_bytes = b"dummy image content"
        result = await extract_invoice_data(dummy_bytes, "image/png")
        
        # Verify 1. Init Gemini client using settings.GEMINI_API_KEY
        mock_configure.assert_called_once()
        
        # Verify 2. Use model: "gemini-2.5-flash"
        mock_model_class.assert_called_once_with("gemini-2.5-flash")
        
        # Verify 4. Send image as inline_data with correct base64 data
        mock_model.generate_content_async.assert_called_once()
        call_args, call_kwargs = mock_model.generate_content_async.call_args
        contents = call_kwargs.get("contents", call_args[0] if call_args else [])
        
        assert len(contents) == 2
        # Prompt checking
        assert "invoice data extraction expert" in contents[0]
        # Image checking
        assert contents[1]["inline_data"]["mime_type"] == "image/png"
        assert isinstance(contents[1]["inline_data"]["data"], str)
        
        # Verify 5. Return response.text (raw string)
        assert result == '{"vendor": "Mock Vendor", "invoice_number": "INV-100", "total_amount": 150.0}'

@pytest.mark.asyncio
async def test_extract_invoice_data_raw_string():
    mock_response = MagicMock()
    mock_response.text = '```json\n{"vendor": "Cleaned Vendor"}\n```'
    
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    with patch("google.generativeai.GenerativeModel", return_value=mock_model), \
         patch("google.generativeai.configure"):
         
        result = await extract_invoice_data(b"dummy image", "image/jpeg")
        assert result == '```json\n{"vendor": "Cleaned Vendor"}\n```'

@pytest.mark.asyncio
async def test_extract_invoice_data_exception_handling():
    mock_model = MagicMock()
    # Simulate Gemini throwing an error
    mock_model.generate_content_async = AsyncMock(side_effect=Exception("API Error"))
    
    with patch("google.generativeai.GenerativeModel", return_value=mock_model), \
         patch("google.generativeai.configure"):
         
        with pytest.raises(GeminiExtractionError) as exc_info:
            await extract_invoice_data(b"dummy image", "image/png")
            
        assert "Error during Gemini extraction" in str(exc_info.value)

