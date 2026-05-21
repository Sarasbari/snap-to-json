from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client
# Note: Ensure SUPABASE_URL and SUPABASE_ANON_KEY are set correctly in your environment
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
