# main.py - Versión FINAL ajustada con tu sidebar/header + debug + storage_secret
from nicegui import ui, app
from core.auth import login, require_auth, logout
from components.header import render_header  # Solo una vez

# ===================== LOGO SEGURO =====================
def mostrar_logo(ancho=280):
    try:
        ui.image("assets/logo.png").style(f'width: {ancho}px; margin: auto;')
    except:
        ui.image("https://i.imgur.com/8e8Q8nB.png").style(f'width: {ancho}px; margin: auto;')

# ===================== PÁGINA DE LOGIN =====================
@ui.page('/')
def login_page():
    print("[DEBUG] Cargando página de login")

    ui.label('EventStaff Pro').classes('text-5xl text-center mt-16')
    ui.label('Panel de Coordinador').classes('text-2xl text-center text-gray-600 mt-4')

    with ui.card().classes('w-96 mx-auto mt-10 p-8 shadow-2xl rounded-xl'):
        email = ui.input('Email', placeholder='admin@eventstaff.pro').classes('w-full')
        password = ui.input('Contraseña', password=True, placeholder='Contraseña').classes('w-full mt-4')

        def try_login():
            print("\n" + "="*60)
            print("[DEBUG TRY_LOGIN] INICIO DE INTENTO DE LOGIN")
            print(f"Email ingresado: '{email.value}'")
            print(f"Contraseña ingresada (longitud {len(password.value)}): '{password.value}'")

            user = login(email.value, password.value)

            print(f"Resultado de login(): {user}")
            print("="*60 + "\n")

            if user:
                print("[DEBUG TRY_LOGIN] LOGIN EXITOSO → Guardando usuario en storage")
                print(f"Datos guardados: {user}")
                app.storage.user['user'] = user
                ui.notify('¡Acceso correcto!', type='positive')
                ui.navigate.to('/dashboard')
            else:
                print("[DEBUG TRY_LOGIN] LOGIN FALLIDO → No se guardó nada")
                ui.notify('Email o contraseña incorrectos', type='negative')

        ui.button('Entrar', on_click=try_login).props('flat color=primary').classes('w-full mt-6')

# ===================== DASHBOARD CON TU SIDEBAR Y HEADER =====================
@ui.page('/dashboard')
def dashboard_page():
    print("\n" + "="*60)
    print("[DEBUG DASHBOARD] Entrando a dashboard_page")
    print(f"Contenido actual de app.storage.user: {app.storage.user}")
    print("="*60 + "\n")

    if not require_auth():
        print("[DEBUG DASHBOARD] require_auth → FALSE (redirigiendo a login)")
        return

    print("[DEBUG DASHBOARD] require_auth → TRUE (acceso permitido)")

    # Tu header (ya lo tienes)
    render_header(title="Dashboard")

    # Mensaje de bienvenida
    ui.notify("Has iniciado sesión correctamente", type='positive')

    # Mostrar nombre con manejo de error
    try:
        user_name = app.storage.user['user'].get('nombre', 'Coordinador')
        print(f"[DEBUG DASHBOARD] Nombre del usuario: {user_name}")
        ui.label(f"**Bienvenido, {user_name}**").classes('text-3xl mt-8')
    except KeyError as e:
        print(f"[ERROR DASHBOARD] KeyError al acceder a storage.user['user']: {e}")
        ui.notify("Error: no se encontró el usuario en la sesión", type='negative')
        ui.label("Bienvenido (error al cargar nombre)").classes('text-3xl mt-8 text-red-500')

    ui.label("Selecciona una opción del menú lateral para empezar a gestionar").classes('text-lg mt-4')

    # Tu sidebar (ya lo tenías, lo mantengo igual)
    with ui.left_drawer(value=True).classes('bg-gray-100 p-4'):
        mostrar_logo(180)
        try:
            user_name = app.storage.user['user'].get('nombre', 'Coordinador')
            ui.label(f"**{user_name}**").classes('text-lg font-bold')
        except:
            ui.label("**Usuario**").classes('text-lg font-bold')

        ui.separator()

        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat').classes('w-full text-left')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat').classes('w-full text-left')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat').classes('w-full text-left')
        ui.button('Refuerzo Urgente', on_click=lambda: ui.navigate.to('/refuerzo')).props('flat').classes('w-full text-left')

        ui.separator()
        ui.button('Cerrar sesión', on_click=lambda: [app.storage.user.clear(), ui.navigate.to('/')]).props('flat color=negative').classes('w-full text-left')

# Ejecutar la app
ui.run(
    title="EventStaff Pro",
    favicon="https://i.imgur.com/8e8Q8nB.png",
    port=8080,           # Para local; Render usa $PORT automáticamente
    reload=True,         # Solo para desarrollo local
    storage_secret="tu_clave_secreta_super_segura_1234567890"  # ← Cámbiala por una tuya larga y única
)