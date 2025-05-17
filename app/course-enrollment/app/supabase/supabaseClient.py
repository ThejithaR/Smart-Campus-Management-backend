import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from app.config import SUPABASE_PROJECT_URL, SUPABASE_PROJECT_API_KEY

url: str = SUPABASE_PROJECT_URL
key: str = SUPABASE_PROJECT_API_KEY
supabase: Client = create_client(
    url, 
    key,
    options=ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
        schema="public",
    )
)