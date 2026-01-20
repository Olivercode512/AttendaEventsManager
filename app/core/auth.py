# app/core/auth.py - Adaptado a NiceGUI + DEBUG para ver qué falla en login
from config.supabase_client import supabase
from nicegui import ui, app


def login(email: str, password: str):
    """
    Función de login con debug detallado para ver qué pasa en producción
    """
    print(f"[DEBUG LOGIN] Intentando login con email: '{email}' | password: '{password}'")

    try:
        # Consulta a Supabase
        print("[DEBUG LOGIN] Ejecutando consulta a tabla 'usuarios'...")
        res = supabase.table("usuarios").select("*").eq("email", email).execute()

        print(f"[DEBUG LOGIN] Respuesta de Supabase: {res}")
        print(f"[DEBUG LOGIN] Datos encontrados: {res.data}")

        if res.data and len(res.data) > 0:
            user = res.data[0]
            stored_password = user.get("password")
            print(f"[DEBUG LOGIN] Usuario encontrado: {user.get('email')}")
            print(f"[DEBUG LOGIN] Contraseña almacenada en BD: '{stored_password}'")

            if stored_password == password:
                print("[DEBUG LOGIN] ¡CONTRASEÑA COINCIDE! Login exitoso")
                return user
            else:
                print("[DEBUG LOGIN] Contraseña NO coincide")
                return None
        else:
            print("[DEBUG LOGIN] No se encontró ningún usuario con ese email")
            return None

    except Exception as e:
        print(f"[ERROR LOGIN] Excepción al consultar Supabase: {str(e)}")
        return None


def require_auth():
    """
    Verifica si hay usuario logueado. Si no, redirige al login.
    """
    print(f"[DEBUG AUTH] Verificando auth - storage.user: {app.storage.user}")
    if 'user' not in app.storage.user or not app.storage.user['user']:
        print("[DEBUG AUTH] No hay usuario en storage → redirigiendo a login")
        ui.navigate.to('/')
        return False
    print("[DEBUG AUTH] Usuario encontrado en storage → acceso permitido")
    return True


def logout():
    print("[DEBUG AUTH] Cerrando sesión - limpiando storage.user")
    app.storage.user.clear()
    ui.notify('Sesión cerrada', type='positive')
    ui.navigate.to('/')