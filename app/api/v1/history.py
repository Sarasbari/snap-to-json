from fastapi import APIRouter
from app.schemas.response import APIResponse
from app.schemas.invoice import InvoiceData
from typing import List

router = APIRouter()

@router.get("/history", response_model=APIResponse[List[InvoiceData]])
async def get_history():
    """
    Endpoint to retrieve history of parsed invoices from Supabase.
    """
    # Stub response
    stub_list = [
        InvoiceData(
            invoice_number="INV-STUB-001",
            vendor_name="Acme Corp",
            line_items=[]
        )
    ]
    return APIResponse(
        success=True,
        message="History retrieved successfully (Stub)",
        data=stub_list
    )
