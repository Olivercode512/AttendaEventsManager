# app/components/header.py - Componente reutilizable para el header (barra superior) en NiceGUI
from nicegui import ui, app
from app.core.auth import require_auth, logout


def render_header(show_logout=True, title="EventStaff Pro"):
    """
    Renderiza la barra superior (header) con título, logo y botón de logout (opcional).

    Parámetros:
    - show_logout: bool - Muestra el botón de cerrar sesión (por defecto True)
    - title: str - Título de la página (por defecto "EventStaff Pro")
    """
    with ui.header().classes('bg-primary text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-6 py-3'):
            # Logo + Título
            with ui.row().classes('items-center gap-4'):
                try:
                    ui.image("assets/logo.png").classes('h-12')
                except:
                    ui.icon('event').classes('text-5xl')
                ui.label(title).classes('text-2xl font-bold')

            # Usuario y logout (solo si está autenticado y se pide mostrar)
            if show_logout and 'user' in app.storage.user:
                with ui.row().classes('items-center gap-4'):
                    user_name = app.storage.user['user'].get('nombre', 'Usuario')
                    ui.label(f"Bienvenido, {user_name}").classes('text-lg')

                    def handle_logout():
                        logout()
                        ui.notify('Sesión cerrada correctamente', type='positive')

                    ui.button('Cerrar sesión', on_click=handle_logout, icon='logout') \
                        .props('flat color=white').classes('text-white hover:bg-white/20')

            # Botón de menú móvil (para pantallas pequeñas, opcional)
            ui.button(icon='menu', on_click=lambda: app.storage.general['drawer_open'] = not app.storage.general.get(
                'drawer_open', False)) \
                    .props('flat color=white').classes('lg:hidden')

    # Drawer lateral para móvil (si lo usas)
    with ui.left_drawer(value=False).bind_value(app.storage.general, 'drawer_open').classes('bg-gray-800 text-white'):
        ui.label("Menú").classes('text-xl font-bold mb-4')
        ui.separator()
        ui.button('Dashboard', on_click=lambda: ui.navigate.to('/dashboard')).props('flat').classes(
            'text-white w-full text-left')
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/clientes')).props('flat').classes(
            'text-white w-full text-left')
        ui.button('Eventos', on_click=lambda: ui.navigate.to('/eventos')).props('flat').classes(
            'text-white w-full text-left')
        ui.button('Camareros', on_click=lambda: ui.navigate.to('/camareros')).props('flat').classes(
            'text-white w-full text-left')
        if show_logout:
            ui.separator()
            ui.button('Cerrar sesión', on_click=handle_logout).props('flat color=negative').classes(
                'text-white w-full text-left')