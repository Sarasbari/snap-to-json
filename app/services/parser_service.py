import json
import re
from app.schemas.invoice import InvoiceData

def parse_invoice_response(raw_text: str) -> InvoiceData:
    """
    Parses raw text/JSON from Gemini into structured InvoiceData.
    """
    try:
        if not raw_text:
            return _empty_invoice_data()

        # 1. Strip any markdown fences (triple-backtick json blocks) if present
        # 2. Strip leading/trailing whitespace
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        parsed_dict = None

        # 3. Try json.loads(cleaned_text)
        try:
            parsed_dict = json.loads(cleaned_text)
        except Exception:
            pass

        # 4. If it fails, try to extract JSON from the string using a regex: find first { ... } block
        if not isinstance(parsed_dict, dict):
            match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
            if match:
                try:
                    parsed_dict = json.loads(match.group(1))
                except Exception:
                    pass

        # 5. If still fails, return InvoiceData() with all None fields
        if not isinstance(parsed_dict, dict):
            return _empty_invoice_data()

        # 6. Validate against InvoiceData using model_validate()
        try:
            invoice_data = InvoiceData.model_validate(parsed_dict)
        except Exception:
            return _empty_invoice_data()

        # 7. Set confidence_score based on how many fields are non-null (ratio of filled fields)
        # Calculate ratio based on all fields of InvoiceData (excluding confidence_score itself)
        fields_to_check = [f for f in InvoiceData.model_fields.keys() if f != "confidence_score"]
        if fields_to_check:
            non_null_count = sum(1 for f in fields_to_check if getattr(invoice_data, f) is not None)
            invoice_data.confidence_score = float(non_null_count) / len(fields_to_check)
        else:
            invoice_data.confidence_score = 0.0

        # 8. Return the InvoiceData object
        return invoice_data

    except Exception:
        # Handle all exceptions — never let this function throw
        return _empty_invoice_data()

def _empty_invoice_data() -> InvoiceData:
    """Returns an InvoiceData model with all fields set to None / safe defaults."""
    return InvoiceData(
        vendor=None,
        invoice_number=None,
        invoice_date=None,
        due_date=None,
        total_amount=None,
        subtotal=None,
        tax_amount=None,
        currency=None,
        line_items=[],
        payment_terms=None,
        notes=None,
        confidence_score=0.0
    )

class ParserService:
    def parse_gemini_response(self, response_text: str) -> InvoiceData:
        """
        Parses raw text/JSON from Gemini into structured InvoiceData.
        """
        return parse_invoice_response(response_text)

