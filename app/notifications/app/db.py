import os
from supabase import create_client
from dotenv import load_dotenv

# Load the .env file from the "services" directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# Ensure the credentials are available
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key is missing. Check your .env file.")

# Initialize the Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Connected to Supabase")