# app/components/sidebar.py - Adaptado a NiceGUI (cajón lateral izquierdo)
from nicegui import ui, app

def render_sidebar():
    with ui.left_drawer(value=True).classes('bg-gray-100 p-6 w-64 shadow-xl'):
        # Logo
        try:
            ui.image("assets/logo.png").classes('w-40 mx-auto mb-6')
        except:
            ui.label("Logo no encontrado").classes('text-center text-gray-500 mb-6')

        # Nombre del usuario (de storage)
        user_name = app.storage.user.get('user', {}).get('nombre', 'Admin')
        ui.label(f"**{user_name}**").classes('text-xl font-bold text-center mb-6')

        ui.separator().classes('my-4')

        # Enlaces a páginas (botones full-width)
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat align=left').classes('w-full text-left mb-2')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat align=left').classes('w-full text-left mb-2')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat align=left').classes('w-full text-left mb-2')
        ui.button('Refuerzo Urgente', on_click=lambda: ui.navigate.to('/refuerzo')).props('flat align=left').classes('w-full text-left mb-2')

        ui.separator().classes('my-6')

        # Botón cerrar sesión
        def logout():
            app.storage.user.clear()
            ui.navigate.to('/')

        ui.button('Cerrar sesión', on_click=logout).props('flat color=negative').classes('w-full text-left')