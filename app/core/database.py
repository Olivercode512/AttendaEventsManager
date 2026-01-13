# app/database.py - Adaptado a NiceGUI (sin cambios en lógica, solo import)
from config.supabase_client import supabase  # Mantenemos tu cliente de Supabase

def get_eventos():
    """Obtiene todos los eventos ordenados por fecha descendente"""
    return supabase.table("eventos").select("*").order("fecha", desc=True).execute().data

def get_camareros():
    """Obtiene todos los camareros"""
    return supabase.table("camareros").select("*").execute().data

def crear_evento(data):
    """Crea un nuevo evento en la base de datos"""
    return supabase.table("eventos").insert(data).execute()