# app/config/supabase_client.py - Adaptado a NiceGUI / Render
from supabase import create_client
import os

# Carga las variables de entorno (Render las inyecta directamente)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validación básica (opcional pero muy útil en producción)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en las variables de entorno")

# Cliente de Supabase (global, como en tu original)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)