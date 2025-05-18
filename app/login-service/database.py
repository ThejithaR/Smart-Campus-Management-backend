from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("Supabase URL:", SUPABASE_URL)
print("Supabase Key:", SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

logger.info(f"Initializing Supabase client with URL: {SUPABASE_URL}")

# Initialize Supabase client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def get_user_by_email(email: str):
    try:
        response = supabase.table('users').select('*, roles(*)').eq('email', email).execute()
        print("Querying user:", email)
        print("Response data:", response.data)
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return None

def get_role_by_name(role_name: str):
    try:
        response = supabase.table('roles').select('*').eq('name', role_name).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching role: {str(e)}")
        return None

async def create_user(email: str, name: str, role_id: str):
    try:
        # Split name into first and last name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role_id': role_id,
            'created_date': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('users').insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return None 