import asyncio
from supabase import create_client, Client
from app.config import settings
from app.schemas.invoice import InvoiceData

_supabase_client: Client = None

def get_supabase_client() -> Client:
    """
    Returns a lazily initialized Supabase client instance.
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return _supabase_client

async def save_extraction(filename: str, invoice: InvoiceData) -> dict:
    """
    Inserts a row into the extractions table.
    """
    client = get_supabase_client()
    
    invoice_dict = invoice.model_dump()
    data = {
        "filename": filename,
        "vendor": invoice.vendor,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "due_date": invoice.due_date,
        "total_amount": invoice.total_amount,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "currency": invoice.currency,
        "line_items": invoice_dict["line_items"],
        "payment_terms": invoice.payment_terms,
        "notes": invoice.notes,
        "confidence_score": invoice.confidence_score,
        "raw_json": invoice_dict,
    }
    
    response = await asyncio.to_thread(
        client.table("extractions").insert(data).execute
    )
    
    if response.data:
        return response.data[0]
    return {}

async def get_extractions(limit: int = 20) -> list:
    """
    Queries extractions table ordered by created_at desc.
    """
    client = get_supabase_client()
    
    response = await asyncio.to_thread(
        client.table("extractions")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute
    )
    
    return response.data

async def get_extraction_by_id(extraction_id: str) -> dict | None:
    """
    Queries extractions table for a single row by id.
    """
    client = get_supabase_client()
    
    response = await asyncio.to_thread(
        client.table("extractions")
        .select("*")
        .eq("id", extraction_id)
        .execute
    )
    
    if response.data:
        return response.data[0]
    return None


