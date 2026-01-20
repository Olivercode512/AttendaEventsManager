# main.py - Versión completa con debug, storage_secret y correcciones para producción
from nicegui import ui, app
from core.auth import login  # Mantenemos tu función original
from components.header import render_header


# ===================== LOGO SEGURO =====================
def mostrar_logo(ancho=280):
    try:
        ui.image("assets/logo.png").style(f'width: {ancho}px; margin: auto;')
    except:
        # Logo VIP online (siempre funciona)
        ui.image("https://i.imgur.com/8e8Q8nB.png").style(f'width: {ancho}px; margin: auto;')


# ===================== LOGIN PERFECTAMENTE CENTRADO =====================
@ui.page('/')
def login_page():
    print("[DEBUG] Cargando página de login")

    ui.label('EventStaff Pro').classes('text-5xl text-center mt-16')
    ui.label('Panel de Coordinador').classes('text-2xl text-center text-gray-600 mt-4')

    with ui.card().classes('w-96 mx-auto mt-10 p-8 shadow-2xl rounded-xl'):
        email = ui.input('Email', placeholder='admin@eventstaff.pro').classes('w-full')
        password = ui.input('Contraseña', password=True, placeholder='Contraseña').classes('w-full mt-4')

        def try_login():
            print("[DEBUG TRY_LOGIN] Iniciando intento de login")
            print(f"[DEBUG TRY_LOGIN] Email ingresado: '{email.value}'")
            print(f"[DEBUG TRY_LOGIN] Contraseña ingresada: '{password.value}' (longitud: {len(password.value)})")

            user = login(email.value, password.value)

            print(f"[DEBUG TRY_LOGIN] Resultado de login(): {user}")

            if user:
                print("[DEBUG TRY_LOGIN] Usuario válido → guardando en storage.user")
                print(f"[DEBUG TRY_LOGIN] Datos del usuario guardado: {user}")
                app.storage.user['user'] = user
                ui.notify('¡Acceso correcto!', type='positive')
                ui.navigate.to('/dashboard')
            else:
                print("[DEBUG TRY_LOGIN] Login fallido - no se guardó nada en storage")
                ui.notify('Email o contraseña incorrectos', type='negative')

        ui.button('Entrar', on_click=try_login).props('flat color=primary').classes('w-full mt-6')


# ===================== DASHBOARD CON SIDEBAR =====================
@ui.page('/dashboard')
def dashboard_page():
    print("[DEBUG DASHBOARD] Entrando a dashboard_page")

    if not require_auth():
        print("[DEBUG DASHBOARD] require_auth devolvió False → redirigido")
        return

    print("[DEBUG DASHBOARD] require_auth OK - continuando")
    print(f"[DEBUG DASHBOARD] Contenido de storage.user: {app.storage.user}")

    render_header(title="Dashboard")

    # Mensaje de bienvenida
    ui.notify("Has iniciado sesión correctamente", type='positive')

    # Mostrar nombre del usuario con manejo de error
    try:
        user_name = app.storage.user['user'].get('nombre', 'Coordinador')
        print(f"[DEBUG DASHBOARD] Nombre del usuario: {user_name}")
        ui.label(f"**Bienvenido, {user_name}**").classes('text-3xl mt-8')
    except KeyError as e:
        print(f"[ERROR DASHBOARD] KeyError al acceder a storage.user['user']: {e}")
        ui.notify("Error: no se encontró el usuario en la sesión", type='negative')
        ui.label("Error al cargar el nombre del usuario").classes('text-red-500')

    ui.label("Selecciona una opción del menú lateral para empezar a gestionar").classes('text-lg mt-4')

    # Sidebar (drawer izquierdo)
    with ui.left_drawer(value=True).classes('bg-gray-100 p-4'):
        mostrar_logo(180)
        ui.label(f"**{app.storage.user['user'].get('nombre', 'Coordinador')}**").classes('text-lg font-bold')
        ui.separator()

        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat').classes('w-full text-left')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat').classes('w-full text-left')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat').classes('w-full text-left')
        ui.button('Refuerzo Urgente', on_click=lambda: ui.navigate.to('/refuerzo')).props('flat').classes(
            'w-full text-left')

        ui.separator()
        ui.button('Cerrar sesión', on_click=lambda: [app.storage.user.clear(), ui.navigate.to('/')]).props(
            'flat color=negative').classes('w-full text-left')


# Ejecutar la app
ui.run(
    title="EventStaff Pro",
    favicon="https://i.imgur.com/8e8Q8nB.png",
    port=8080,  # Para local; Render usa $PORT automáticamente
    reload=True,  # Solo para desarrollo local
    storage_secret="tu_clave_secreta_super_segura_1234567890"  # ← Añade ESTA línea
)
)