from pydantic import BaseModel, Field, ConfigDict

class LineItem(BaseModel):
    description: str = Field(description="Description of the line item")
    quantity: float | None = Field(None, description="Quantity of the item")
    unit_price: float | None = Field(None, description="Unit price of the item")
    total: float | None = Field(None, description="Total cost of the line item")

class InvoiceData(BaseModel):
    vendor: str | None = Field(None, description="Name of the vendor/merchant")
    invoice_number: str | None = Field(None, description="Unique invoice identifier number")
    invoice_date: str | None = Field(None, description="Invoice date in ISO format (YYYY-MM-DD)")
    due_date: str | None = Field(None, description="Invoice payment due date in ISO format (YYYY-MM-DD)")
    total_amount: float | None = Field(None, description="Total amount payable including tax")
    subtotal: float | None = Field(None, description="Subtotal amount before tax")
    tax_amount: float | None = Field(None, description="Total tax amount")
    currency: str | None = Field("INR", description="Currency code (e.g., INR, USD)")
    line_items: list[LineItem] = Field(default_factory=list, description="List of line items in the invoice")
    payment_terms: str | None = Field(None, description="Terms of payment (e.g., Net 30)")
    notes: str | None = Field(None, description="Additional notes or comments on the invoice")
    confidence_score: float | None = Field(None, description="Parser confidence score between 0.0 and 1.0")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vendor": "Acme Corporation",
                "invoice_number": "INV-2026-001",
                "invoice_date": "2026-05-22",
                "due_date": "2026-06-22",
                "total_amount": 1180.00,
                "subtotal": 1000.00,
                "tax_amount": 180.00,
                "currency": "INR",
                "line_items": [
                    {
                        "description": "Consulting Services",
                        "quantity": 10.0,
                        "unit_price": 100.00,
                        "total": 1000.00
                    }
                ],
                "payment_terms": "Net 30",
                "notes": "Thank you for your business!",
                "confidence_score": 0.95
            }
        }
    )

