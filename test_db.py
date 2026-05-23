import asyncio
from app.db.supabase_client import get_supabase_client
import uuid
import datetime

async def main():
    client = get_supabase_client()
    data = {
        "id": str(uuid.uuid4()),
        "filename": "test.png",
        "vendor": "Test Vendor",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    # Try inserting only the existing columns (id, filename, vendor, created_at)
    try:
        print("Attempting insert of valid columns...")
        res = client.table("extractions").insert(data).execute()
        print("Insert returned successfully!")
        print("Response data:", res.data)
    except Exception as e:
        print("Insert failed with exception:")
        print("Exception class:", type(e))
        print("Exception message:", str(e))
        if hasattr(e, 'message'):
            print("Error message attribute:", e.message)
        if hasattr(e, 'code'):
            print("Error code attribute:", e.code)

if __name__ == "__main__":
    asyncio.run(main())


