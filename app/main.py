# main.py - Versión MINIMALISTA para probar que arranca (sin UI global)
from nicegui import ui, app
from core.auth import login, require_auth, logout
from components.header import render_header
from pages.camareros import *
from pages.clientes import *
from pages.eventos import *

# Auxiliar para logo (sin UI global)
def mostrar_logo(ancho=280):
    try:
        ui.image("assets/logo.png").style(f'width: {ancho}px; margin: auto;')
    except:
        ui.image("https://i.imgur.com/8e8Q8nB.png").style(f'width: {ancho}px; margin: auto;')

@ui.page('/')
def login_page():
    print("[DEBUG] Login page cargada")
    ui.label('EventStaff Pro - Login').classes('text-4xl text-center mt-10')
    ui.label('Introduce tus credenciales').classes('text-xl text-center')

    with ui.card().classes('w-96 mx-auto mt-8 p-6'):
        email = ui.input('Email').classes('w-full')
        password = ui.input('Contraseña', password=True).classes('w-full mt-4')

        def try_login():
            user = login(email.value, password.value)
            if user:
                app.storage.user['user'] = user
                ui.notify('Login OK', type='positive')
                ui.navigate.to('/dashboard')
            else:
                ui.notify('Credenciales incorrectas', type='negative')

        ui.button('Entrar', on_click=try_login).classes('w-full mt-6')

@ui.page('/dashboard')
def dashboard_page():
    print("[DEBUG] Dashboard cargado")
    if not require_auth():
        return

    render_header(title="Dashboard")

    ui.label('Bienvenido al Dashboard').classes('text-4xl mt-10 text-center')
    ui.label('El sidebar y header deberían aparecer si están en render_header o aquí').classes('text-lg text-center mt-4')

    with ui.left_drawer(value=True).classes('bg-gray-100 p-4'):
        mostrar_logo(180)
        ui.label('**Menú**').classes('text-lg font-bold mt-4')
        ui.separator()
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat').classes('w-full text-left')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat').classes('w-full text-left')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat').classes('w-full text-left')
        ui.separator()
        ui.button('Logout', on_click=lambda: [app.storage.user.clear(), ui.navigate.to('/')]).props('flat color=negative').classes('w-full text-left')

ui.run(
    title="EventStaff Pro",
    favicon="https://i.imgur.com/8e8Q8nB.png",
    storage_secret="tu_clave_super_segura_2026"  # ← CAMBIA ESTO YA
)