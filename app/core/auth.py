# app/core/auth.py - Adaptado a NiceGUI (sin Streamlit, usa app.storage.user)
from config.supabase_client import supabase  # Mantenemos tu cliente de Supabase
from nicegui import ui, app

def login(email: str, password: str):
    """
    Función de login igual que la original, pero sin try-except innecesario
    """
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        if res.data and res.data[0]["password"] == password:
            return res.data[0]
        return None
    except Exception as e:
        print(f"Error en login: {e}")  # Para debug en logs de Render
        return None

def require_auth():
    """
    Verifica si hay usuario logueado.
    Si no, redirige al login.
    """
    if 'user' not in app.storage.user or not app.storage.user['user']:
        ui.navigate.to('/')
        return False
    return True

# Función auxiliar para cerrar sesión (puedes llamarla desde el sidebar)
def logout():
    app.storage.user.clear()
    ui.notify('Sesión cerrada', type='positive')
    ui.navigate.to('/')