from config.supabase_client import supabase

def get_eventos():
    return supabase.table("eventos").select("*").order("fecha", desc=True).execute().data

def get_camareros():
    return supabase.table("camareros").select("*").execute().data

def crear_evento(data):
    return supabase.table("eventos").insert(data).execute()