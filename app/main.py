# main.py - CORREGIDO: TODO UI dentro de @ui.page (soluciona RuntimeError)
from nicegui import ui, app
from core.auth import login, require_auth, logout
from components.header import render_header
from pages.camareros import *
from pages.clientes import *
from pages.eventos import *

# ===================== LOGO AUXILIAR =====================
def mostrar_logo(ancho=280):
    try:
        ui.image("assets/logo.png").style(f'width: {ancho}px; margin: auto;')
    except:
        ui.image("https://i.imgur.com/8e8Q8nB.png").style(f'width: {ancho}px; margin: auto;')

# ===================== LOGIN =====================
@ui.page('/')
def login_page():
    print("[DEBUG] Cargando página de login")

    ui.label('EventStaff Pro').classes('text-5xl text-center mt-16')
    ui.label('Panel de Coordinador').classes('text-2xl text-center text-gray-600 mt-4')

    with ui.card().classes('w-96 mx-auto mt-10 p-8 shadow-2xl rounded-xl'):
        email = ui.input('Email', placeholder='admin@eventstaff.pro').classes('w-full')
        password = ui.input('Contraseña', password=True, placeholder='Contraseña').classes('w-full mt-4')

        def try_login():
            print("[DEBUG TRY_LOGIN] Inicio intento")
            print(f"Email: '{email.value}'")
            print(f"Contraseña: '{password.value}'")

            user = login(email.value, password.value)
            print(f"Resultado: {user}")

            if user:
                app.storage.user['user'] = user
                ui.notify('¡Acceso correcto!', type='positive')
                ui.navigate.to('/dashboard')
            else:
                ui.notify('Email o contraseña incorrectos', type='negative')

        ui.button('Entrar', on_click=try_login).props('flat color=primary').classes('w-full mt-6')

# ===================== DASHBOARD =====================
@ui.page('/dashboard')
def dashboard_page():
    print("[DEBUG DASHBOARD] Entrando...")

    if not require_auth():
        return

    render_header(title="Dashboard")

    ui.notify("Has iniciado sesión correctamente", type='positive')

    try:
        nombre = app.storage.user['user'].get('nombre', 'Coordinador')
        ui.label(f"**Bienvenido, {nombre}**").classes('text-3xl mt-8')
    except KeyError:
        ui.label("Bienvenido (error al cargar nombre)").classes('text-3xl mt-8 text-red-500')

    ui.label("Selecciona una opción del menú lateral").classes('text-lg mt-4')

    with ui.left_drawer(value=True).classes('bg-gray-100 p-4'):
        mostrar_logo(180)
        try:
            nombre = app.storage.user['user'].get('nombre', 'Coordinador')
            ui.label(f"**{nombre}**").classes('text-lg font-bold')
        except KeyError:
            ui.label("**Coordinador**").classes('text-lg font-bold')

        ui.separator()

        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat').classes('w-full text-left')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat').classes('w-full text-left')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat').classes('w-full text-left')
        ui.button('Refuerzo Urgente', on_click=lambda: ui.navigate.to('/refuerzo')).props('flat').classes('w-full text-left')

        ui.separator()
        ui.button('Cerrar sesión', on_click=lambda: [app.storage.user.clear(), ui.navigate.to('/')]).props('flat color=negative').classes('w-full text-left')

# ===================== INICIO =====================
ui.run(
    title="EventStaff Pro",
    favicon="https://i.imgur.com/8e8Q8nB.png",
    port=8080,
    reload=True,
    storage_secret="mi_super_secreto_attenda_2026_oliver_xai_grok_987654"  # ¡CÁMBIALO POR TU CLAVE!
)