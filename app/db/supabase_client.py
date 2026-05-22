from supabase import create_client, Client
from app.config import settings

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
