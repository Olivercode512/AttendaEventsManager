# app/config/settings.py - Adaptado a NiceGUI / Render (solo env vars)
import os

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    @staticmethod
    def validate():
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en las variables de entorno")

# Validación automática al importar (opcional, pero útil)
Config.validate()