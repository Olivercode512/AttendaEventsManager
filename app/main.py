# main.py - Adaptado a NiceGUI (login centrado, sidebar, dashboard)
from nicegui import ui, app
from core.auth import login  # Mantenemos tu función original
from components.header import render_header
from components.header import render_header

# Configuración de la página (equivalente a st.set_page_config)
# ui.context.client.request.headers['title'] = "EventStaff Pro"
# ui.context.client.request.headers['icon'] = "https://i.imgur.com/8e8Q8nB.png"

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
    # Espacio superior para bajar un poco el contenido (equivalente a markdown margin)
    ui.label().style('margin-top: 5rem;')

    # Todo centrado horizontalmente
    with ui.card().classes('w-1/2 mx-auto p-8 shadow-xl rounded-lg'):
        # Logo centrado
        mostrar_logo(280)

        # Título centrado
        ui.label("EventStaff Pro").classes('text-4xl text-center mt-5')
        ui.label("Panel de Coordinador").classes('text-xl text-center text-gray-600')

        # Formulario centrado
        email = ui.input('Email', placeholder="admin@eventstaff.pro").classes('w-full mt-6')
        pwd = ui.input('Contraseña', password=True, placeholder="Contraseña").classes('w-full mt-4')

        def try_login():
            user = login(email.value, pwd.value)
            if user:
                app.storage.user['user'] = user
                ui.notify('¡Acceso correcto!', type='positive')
                ui.navigate.to('/dashboard')
            else:
                ui.notify('Email o contraseña incorrectos', type='negative')

        ui.button('Entrar', on_click=try_login).props('color=primary').classes('w-full mt-6')

# ===================== DASHBOARD CON SIDEBAR =====================
@ui.page('/dashboard')
def dashboard_page():
    if 'user' not in app.storage.user:
        ui.navigate.to('/')

    # Contenido principal
    ui.label("Bienvenido a EventStaff Pro").classes('text-3xl mt-8')

    ui.notify("Has iniciado sesión correctamente",type='positive').classes('mt-4')

    ui.markdown("""
Selecciona una opción del menú lateral para empezar a gestionar:
- Crear eventos
- Asignar camareros
- Generar grupos de WhatsApp automáticos
- Buscar refuerzos urgentes
""").classes('mt-4')

    # Sidebar (left drawer)
    with ui.left_drawer(value=True).classes('bg-gray-100 p-4'):
        mostrar_logo(180)
        ui.label(f"**{app.storage.user['user'].get('nombre', 'Coordinador')}**").classes('text-lg font-bold')
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
    storage_secret="tu_clave_secreta_super_segura_1234567890"  # ← Añade ESTA línea
)