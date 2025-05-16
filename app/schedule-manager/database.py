from decouple import config
from supabase import create_client, Client

url = config("SUPERBASE_URL")
key = config("SUPABASE_KEY")

supabase: Client = create_client(url, key)
