# pages/camareros.py - Adaptado a NiceGUI (con anidamiento de expansions permitido)
from nicegui import ui, app
import re
from app.config.supabase_client import supabase
from app.config.settings import Config
import urllib.parse
from app.core.auth import require_auth  # Importamos para autenticación

@ui.page('/camareros')
def camareros_page():
    if not require_auth():
        return

    ui.label("FICHA DE EMPLEADOS").classes('text-4xl mb-6')

    # ================== AÑADIR NUEVO CAMARERO ==================
    with ui.expansion("Añadir nuevo camarero", value=True).classes('w-full mb-8'):
        with ui.card().classes('w-full p-6 shadow-lg'):
            with ui.row().classes('w-full'):
                with ui.column():
                    nombre = ui.input('Nombre').classes('w-full')
                    apellidos = ui.input('Apellidos').classes('w-full')
                    telefono = ui.input('Teléfono', placeholder="+34 609 159 167").classes('w-full')
                    email = ui.input('Email').classes('w-full')
                    dni = ui.input('DNI').classes('w-full')

                with ui.column():
                    residencia = ui.input('Lugar de residencia').classes('w-full')
                    nacionalidad = ui.input('Nacionalidad').classes('w-full')
                    idiomas = ui.input('Idiomas').classes('w-full')
                    tiene_coche = ui.checkbox('Tiene coche')
                    curso_prl = ui.checkbox('Tiene curso PRL')

            with ui.row().classes('w-full mt-4'):
                with ui.column():
                    numero_ss = ui.input('Nº Seguridad Social').classes('w-full')
                    tarifa = ui.number('Tarifa €/hora', value=12.0, min=0.0, step=0.1).classes('w-full')
                with ui.column():
                    observaciones = ui.textarea('Observaciones').classes('w-full h-24')

            def guardar_camarero():
                if not nombre.value.strip():
                    ui.notify('El nombre es obligatorio', type='negative')
                    return
                datos = {
                    "nombre": nombre.value.strip(),
                    "apellidos": apellidos.value.strip(),
                    "telefono": telefono.value.strip(),
                    "email": email.value.strip(),
                    "dni": dni.value.strip(),
                    "residencia": residencia.value.strip(),
                    "nacionalidad": nacionalidad.value.strip(),
                    "idiomas": idiomas.value.strip(),
                    "tiene_coche": tiene_coche.value,
                    "curso_prl": curso_prl.value,
                    "numero_ss": numero_ss.value.strip(),
                    "tarifa": tarifa.value,
                    "observaciones": observaciones.value.strip() if observaciones.value.strip() else None
                }
                supabase.table("camareros").insert(datos).execute()
                ui.notify('¡Camarero añadido!', type='positive')
                ui.refresh()

            ui.button('Guardar camarero', on_click=guardar_camarero).props('color=primary').classes('w-full mt-6')

# ================== LISTA DE CAMAREROS ==================
camareros = supabase.table("camareros").select("*").execute().data

if camareros:
    for c in camareros:
        with ui.expansion(f"{c['nombre']} {c['apellidos']} - Tel: {c['telefono']}").classes('w-full mb-4'):
            with ui.row().classes('w-full'):
                with ui.column():
                    ui.label(f"Email: {c.get('email', 'No disponible')}")
                    ui.label(f"DNI: {c.get('dni', 'No disponible')}")
                    ui.label(f"Residencia: {c.get('residencia', 'No disponible')} ")
                    ui.label(f"Nacionalidad: {c.get('nacionalidad', 'No disponible')} ")
                    ui.label(f"Idiomas: {c.get('idiomas', 'No disponible')} ")

                with ui.column():
                    ui.label(f"Tiene coche: {'Sí' if c.get('tiene_coche') else 'No'}")
                    ui.label(f"Curso PRL: {'Sí' if c.get('curso_prl') else 'No'}")
                    ui.label(f"Nº SS: {c.get('numero_ss', 'No disponible')} ")
                    ui.label(f"Tarifa: {c.get('tarifa', 12.0)} €/h")
                    ui.label(f"Observaciones: {c.get('observaciones') or 'Ninguna'}")

            # Editar camarero (adaptado a form con button)
            ui.label('Editar camarero').classes('text-xl mt-6 mb-4')
            with ui.card().classes('w-full p-4 shadow-md'):
                with ui.row().classes('w-full'):
                    with ui.column():
                        edit_nombre = ui.input('Nombre', value=c.get('nombre', '')).classes('w-full')
                        edit_apellidos = ui.input('Apellidos', value=c.get('apellidos', '')).classes('w-full')
                        edit_telefono = ui.input('Teléfono', value=c.get('telefono', '')).classes('w-full')
                        edit_email = ui.input('Email', value=c.get('email', '')).classes('w-full')
                        edit_dni = ui.input('DNI', value=c.get('dni', '')).classes('w-full')

                    with ui.column():
                        edit_residencia = ui.input('Residencia', value=c.get('residencia', '')).classes('w-full')
                        edit_nacionalidad = ui.input('Nacionalidad', value=c.get('nacionalidad', '')).classes('w-full')
                        edit_idiomas = ui.input('Idiomas', value=c.get('idiomas', '')).classes('w-full')
                        edit_coche = ui.checkbox('Tiene coche', value=c.get('tiene_coche', False))
                        edit_prl = ui.checkbox('Curso PRL', value=c.get('curso_prl', False))

                with ui.row().classes('w-full mt-4'):
                    with ui.column():
                        edit_ss = ui.input('Nº SS', value=c.get('numero_ss', '')).classes('w-full')
                        edit_tarifa = ui.number('Tarifa €/h', value=c.get('tarifa', 12.0), step=0.1, min=0.0).classes('w-full')
                    with ui.column():
                        edit_obs = ui.textarea('Observaciones', value=c.get('observaciones', '')).classes('w-full h-24')

                with ui.row().classes('w-full mt-6'):
                    def guardar_cambios():
                        datos_edit = {
                            "nombre": edit_nombre.value.strip(),
                            "apellidos": edit_apellidos.value.strip(),
                            "telefono": edit_telefono.value.strip(),
                            "email": edit_email.value.strip(),
                            "dni": edit_dni.value.strip(),
                            "residencia": edit_residencia.value.strip(),
                            "nacionalidad": edit_nacionalidad.value.strip(),
                            "idiomas": edit_idiomas.value.strip(),
                            "tiene_coche": edit_coche.value,
                            "curso_prl": edit_prl.value,
                            "numero_ss": edit_ss.value.strip(),
                            "tarifa": edit_tarifa.value,
                            "observaciones": edit_obs.value.strip() if edit_obs.value.strip() else None
                        }
                        supabase.table("camareros").update(datos_edit).eq("id", c['id']).execute()
                        ui.notify('Camarero actualizado', type='positive')
                        ui.refresh()

                    ui.button('Guardar cambios', on_click=guardar_cambios).props('color=primary').classes('flex-1')

                    def confirmar_eliminar():
                        app.storage.user['camarero_a_eliminar'] = c['id']
                        app.storage.user['nombre_a_eliminar'] = f"{c['nombre']} {c['apellidos']}"
                        ui.refresh()

                    ui.button('Eliminar', on_click=confirmar_eliminar).props('color=negative').classes('flex-1')

            # Añadir valoración (anidada dentro del expander, NiceGUI lo permite)
            with ui.expansion('Añadir valoración', value=False).classes('w-full mt-4'):
                valoracion = ui.number('Valoración (0-5)', value=0, min=0, max=5, step=1).classes('w-full')
                comentario = ui.textarea('Comentario').classes('w-full h-24')
                evento_id = ui.number('ID del evento', value=0, min=0).classes('w-full')

                def guardar_valoracion():
                    datos_val = {
                        "camarero_id": c['id'],
                        "evento_id": evento_id.value,
                        "valoracion": valoracion.value,
                        "comentario": comentario.value.strip() if comentario.value.strip() else None
                    }
                    supabase.table("valoraciones").insert(datos_val).execute()
                    ui.notify('¡Valoración guardada!', type='positive')
                    ui.refresh()

                ui.button('Guardar valoración', on_click=guardar_valoracion).props('color=primary').classes('w-full mt-4')

# ================== CONFIRMACIÓN ELIMINAR ==================
if app.storage.user.get('camarero_a_eliminar'):
    c_id = app.storage.user['camarero_a_eliminar']
    nombre = app.storage.user['nombre_a_eliminar']
    ui.notify(f"¿Eliminar permanentemente a **{nombre}**?", type='negative')
    with ui.row().classes('w-full mt-4'):
        def eliminar():
            supabase.table("camareros").delete().eq("id", c_id).execute()
            app.storage.user.pop('camarero_a_eliminar', None)
            app.storage.user.pop('nombre_a_eliminar', None)
            ui.notify('Camarero eliminado', type='positive')
            ui.refresh()

        ui.button('Sí, eliminar', on_click=eliminar).props('color=primary').classes('flex-1')

        def cancelar():
            app.storage.user.pop('camarero_a_eliminar', None)
            app.storage.user.pop('nombre_a_eliminar', None)
            ui.refresh()

        ui.button('Cancelar', on_click=cancelar).props('color=secondary').classes('flex-1')