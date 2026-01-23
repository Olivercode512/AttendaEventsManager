from supabase import create_client
from .settings import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)