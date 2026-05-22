import asyncio
import datetime
import uuid
import logging
from supabase import create_client, Client
from app.config import settings
from app.schemas.invoice import InvoiceData

logger = logging.getLogger(__name__)

# In-memory fallback database for offline/local testing when Supabase is unreachable
_in_memory_db = []
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
    Inserts a row into the extractions table. Falls back to in-memory store on connection failure.
    """
    invoice_dict = invoice.model_dump()
    data = {
        "id": str(uuid.uuid4()),
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
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    try:
        client = get_supabase_client()
        response = await asyncio.to_thread(
            client.table("extractions").insert(data).execute
        )
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.warning(f"Supabase connection failed: {e}. Storing extraction in-memory instead.")
        _in_memory_db.insert(0, data)
        return data
        
    return {}

async def get_extractions(limit: int = 20) -> list:
    """
    Queries extractions table ordered by created_at desc. Falls back to in-memory store on connection failure.
    """
    try:
        client = get_supabase_client()
        response = await asyncio.to_thread(
            client.table("extractions")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute
        )
        return response.data
    except Exception as e:
        logger.warning(f"Supabase connection failed: {e}. Returning in-memory extractions.")
        return _in_memory_db[:limit]

async def get_extraction_by_id(extraction_id: str) -> dict | None:
    """
    Queries extractions table for a single row by id. Falls back to in-memory search on connection failure.
    """
    try:
        client = get_supabase_client()
        response = await asyncio.to_thread(
            client.table("extractions")
            .select("*")
            .eq("id", extraction_id)
            .execute
        )
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.warning(f"Supabase connection failed: {e}. Searching in-memory extractions.")
        for item in _in_memory_db:
            if item["id"] == extraction_id:
                return item
    return None
