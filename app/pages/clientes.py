# pages/clientes.py - Adaptado a NiceGUI (con expansions anidadas permitidas)
from nicegui import ui, app
from config.supabase_client import supabase
from config.settings import Config
from app.core.auth import require_auth  # Importamos para autenticación

@ui.page('/clientes')
def clientes_page():
    if not require_auth():
        return

    ui.label("👥 Gestión de Clientes").classes('text-4xl mb-6')

    # ================== AÑADIR NUEVO CLIENTE ==================
    with ui.expansion("Añadir nuevo cliente", value=True).classes('w-full mb-8'):
        with ui.card().classes('w-full p-6 shadow-lg'):
            with ui.row().classes('w-full'):
                with ui.column():
                    nombre = ui.input('Nombre del cliente / catering', placeholder="Boda Ana y Pedro").classes('w-full')
                    contacto = ui.input('Persona de contacto', placeholder="Ana García").classes('w-full')
                with ui.column():
                    telefono = ui.input('Teléfono', placeholder="+34 600 123 456").classes('w-full')
                    email = ui.input('Email', placeholder="ana@example.com").classes('w-full')

            notas = ui.textarea('Notas adicionales (opcionales)', placeholder="Preferencias, alergias, comentarios...").classes('w-full mt-4 h-24')

            def guardar_cliente():
                if not nombre.value.strip():
                    ui.notify('El nombre del cliente es obligatorio', type='negative')
                    return
                datos = {
                    "nombre": nombre.value.strip(),
                    "contacto": contacto.value.strip(),
                    "telefono": telefono.value.strip(),
                    "email": email.value.strip(),
                    "notas": notas.value.strip() if notas.value.strip() else None
                }
                supabase.table("clientes").insert(datos).execute()
                ui.notify('Cliente guardado correctamente', type='positive')
                ui.refresh()

            ui.button('Guardar cliente', on_click=guardar_cliente).props('color=primary').classes('w-full mt-6')

    # ================== LISTA DE CLIENTES ==================
    clientes = supabase.table("clientes").select("*").execute().data

    if clientes:
        for cl in clientes:
            with ui.expansion(f"{cl['nombre']} - Contacto: {cl.get('contacto', 'No disponible')}").classes('w-full mb-4'):
                with ui.row().classes('w-full'):
                    with ui.column():
                        ui.label(f"Teléfono: {cl.get('telefono', 'No disponible')}")
                        ui.label(f"Email: {cl.get('email', 'No disponible')}")

                    with ui.column():
                        ui.label(f"Notas: {cl.get('notas', 'Ninguna')}")

                # Editar cliente
                ui.label('Editar cliente').classes('text-xl mt-6 mb-4')
                with ui.card().classes('w-full p-4 shadow-md'):
                    with ui.row().classes('w-full'):
                        with ui.column():
                            edit_nombre = ui.input('Nombre del cliente / catering', value=cl.get('nombre', '')).classes('w-full')
                            edit_contacto = ui.input('Persona de contacto', value=cl.get('contacto', '')).classes('w-full')
                        with ui.column():
                            edit_telefono = ui.input('Teléfono', value=cl.get('telefono', '')).classes('w-full')
                            edit_email = ui.input('Email', value=cl.get('email', '')).classes('w-full')

                    edit_notas = ui.textarea('Notas adicionales', value=cl.get('notas', '')).classes('w-full mt-4 h-24')

                    with ui.row().classes('w-full mt-6'):
                        def guardar_edicion():
                            datos_edit = {
                                "nombre": edit_nombre.value.strip(),
                                "contacto": edit_contacto.value.strip(),
                                "telefono": edit_telefono.value.strip(),
                                "email": edit_email.value.strip(),
                                "notas": edit_notas.value.strip() if edit_notas.value.strip() else None
                            }
                            supabase.table("clientes").update(datos_edit).eq("id", cl['id']).execute()
                            ui.notify('Cliente actualizado', type='positive')
                            ui.refresh()

                        ui.button('Guardar cambios', on_click=guardar_edicion).props('color=primary').classes('flex-1')

                        def confirmar_eliminar():
                            app.storage.user['cliente_a_eliminar'] = cl['id']
                            app.storage.user['nombre_cliente_eliminar'] = cl['nombre']
                            ui.refresh()

                        ui.button('Eliminar', on_click=confirmar_eliminar).props('color=negative').classes('flex-1')

# ================== CONFIRMACIÓN ELIMINAR CLIENTE ==================
if app.storage.user.get('cliente_a_eliminar'):
    cid = app.storage.user['cliente_a_eliminar']
    nombre = app.storage.user['nombre_cliente_eliminar']
    ui.notify(f"¿Eliminar permanentemente al cliente **{nombre}**?", type='negative')
    with ui.row().classes('w-full mt-4'):
        def eliminar_cliente():
            supabase.table("clientes").delete().eq("id", cid).execute()
            app.storage.user.pop('cliente_a_eliminar', None)
            app.storage.user.pop('nombre_cliente_eliminar', None)
            ui.notify('Cliente eliminado', type='positive')
            ui.refresh()

        ui.button('Sí, eliminar', on_click=eliminar_cliente).props('color=primary').classes('flex-1')

        def cancelar_eliminar():
            app.storage.user.pop('cliente_a_eliminar', None)
            app.storage.user.pop('nombre_cliente_eliminar', None)
            ui.refresh()

        ui.button('Cancelar', on_click=cancelar_eliminar).props('color=secondary').classes('flex-1')