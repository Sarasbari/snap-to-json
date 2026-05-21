from app.schemas.invoice import InvoiceData

class ParserService:
    def parse_gemini_response(self, response_text: str) -> InvoiceData:
        """
        Parses raw text/JSON from Gemini into structured InvoiceData.
        """
        # Stub implementation
        return InvoiceData(
            invoice_number="INV-STUB",
            vendor_name="Stub Vendor",
            line_items=[]
        )
