import streamlit as st
from config.supabase_client import supabase

def login(email: str, password: str):
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        if res.data and res.data[0]["password"] == password:
            return res.data[0]
    except:
        return None
    return None

def require_auth():
    if "user" not in st.session_state:
        st.switch_page("app/main.py")