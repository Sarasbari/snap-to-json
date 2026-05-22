from fastapi import APIRouter, UploadFile, File
from app.schemas.response import APIResponse
from app.schemas.invoice import InvoiceData

router = APIRouter()

@router.post("/extract", response_model=APIResponse[InvoiceData])
async def extract_invoice(file: UploadFile = File(...)):
    """
    Endpoint to upload an invoice image and extract structured data using Gemini.
    """
    # Stub response
    stub_data = InvoiceData(
        invoice_number="INV-STUB-123",
        vendor="Stub Vendor Inc.",
        line_items=[]
    )
    return APIResponse(
        success=True,
        data=stub_data,
        processing_time_ms=120.5
    )
