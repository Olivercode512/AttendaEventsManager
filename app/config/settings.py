import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

    @staticmethod
    def validate():
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY")