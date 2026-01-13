# pages/eventos.py - Versión completa adaptada a NiceGUI (todo funcional)
from nicegui import ui, app
from datetime import datetime
from config.supabase_client import supabase
from app.utils.whatsapp import crear_grupo_whatsapp
from app.core.auth import require_auth
from app.components.header import render_header  # Si tienes el header

@ui.page('/eventos')
def eventos_page():
    if not require_auth():
        return

    # Header (opcional, si lo tienes)
    render_header(title="Eventos")

    ui.label("Eventos").classes('text-4xl font-bold mb-8 text-center')

    # ================== CREAR NUEVO EVENTO ==================
    with ui.expansion("Crear nuevo evento", value=False).classes('w-full mb-10 bg-gray-50 rounded-xl shadow-md'):
        with ui.card().classes('w-full p-8'):
            with ui.row().classes('w-full gap-6'):
                with ui.column().classes('flex-1'):
                    fecha = ui.date('Fecha').classes('w-full')
                    hora_inicio = ui.time('Hora inicio').classes('w-full')
                    hora_fin = ui.time('Hora fin').classes('w-full')

                with ui.column().classes('flex-1'):
                    catering = ui.input('Cliente / Catering').classes('w-full')
                    lugar = ui.input('Lugar').classes('w-full')
                    descripcion = ui.textarea('Descripción').classes('w-full h-32')
                    horas_estimadas = ui.number('Horas estimadas', value=8.0, min=0.0, step=0.5).classes('w-full')

            def crear_evento():
                if not catering.value.strip():
                    ui.notify('El nombre del cliente/catering es obligatorio', type='negative')
                    return

                datos = {
                    "fecha": str(fecha.value),
                    "hora_inicio": str(hora_inicio.value),
                    "hora_fin": str(hora_fin.value),
                    "catering": catering.value.strip(),
                    "lugar": lugar.value.strip(),
                    "descripcion": descripcion.value.strip(),
                    "horas_estimadas": horas_estimadas.value,
                    "estado": "Pendiente"
                }
                supabase.table("eventos").insert(datos).execute()
                ui.notify('Evento creado correctamente', type='positive')
                ui.refresh()

            ui.button('Crear evento', on_click=crear_evento).props('color=primary').classes('w-full mt-8 py-3 text-lg')

    # ================== LISTA DE EVENTOS ==================
    eventos = supabase.table("eventos").select("*").order("fecha", desc=True).execute().data

    if not eventos:
        ui.label("No hay eventos todavía").classes('text-xl text-gray-500 text-center mt-10')
    else:
        for evento in eventos:
            with ui.expansion(f"{evento['fecha']} - {evento['hora_inicio']} a {evento['hora_fin']} - {evento['catering']}")\
                    .classes('w-full mb-6 bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow'):
                tab1, tab2, tab3 = ui.tabs().props('inline-label').classes('w-full mb-4')

                with tab1:
                    with ui.row().classes('w-full gap-8'):
                        with ui.column():
                            ui.label(f"Lugar: {evento.get('lugar', 'No especificado')}").classes('text-gray-700')
                            ui.label(f"Estado: {evento.get('estado', 'Pendiente')}").classes('text-gray-700')
                            ui.label(f"Descripción: {evento.get('descripcion', 'Sin descripción')}").classes('text-gray-700')

                        with ui.column():
                            ui.label(f"Horas estimadas: {evento.get('horas_estimadas', 0)} h").classes('text-gray-700')
                            ui.label(f"Coste total estimado: {evento.get('coste_total', 0)} €").classes('text-gray-700')

                with tab2:
                    asignaciones = supabase.table("asignaciones")\
                        .select("*, camareros(nombre, apellidos, telefono)")\
                        .eq("evento_id", evento['id'])\
                        .execute().data

                    if asignaciones:
                        for a in asignaciones:
                            cam = a['camareros']
                            ui.label(f"{cam['nombre']} {cam['apellidos']} - Tel: {cam['telefono']}").classes('text-gray-700')
                            ui.label(f"Horas asignadas: {a.get('horas_asignadas', 0)}").classes('text-gray-500')
                    else:
                        ui.label("No hay personal asignado aún").classes('text-gray-500 italic')

                with tab3:
                    with ui.row().classes('w-full gap-4 justify-end'):
                        def editar():
                            app.storage.user['editando_evento'] = evento['id']
                            ui.refresh()  # O redirige a una página de edición

                        ui.button('Editar evento', on_click=editar).props('color=primary flat')

                        def eliminar():
                            app.storage.user['evento_a_eliminar'] = evento['id']
                            app.storage.user['evento_nombre'] = evento['catering']
                            ui.refresh()

                        ui.button('Eliminar evento', on_click=eliminar).props('color=negative flat')

                        # Botón WhatsApp
                        enlace, nombre_grupo = crear_grupo_whatsapp(evento, asignaciones)
                        if enlace:
                            ui.button('Crear grupo WhatsApp', on_click=lambda: ui.open(enlace, new_tab=True))\
                                .props('color=green flat').classes('text-white')

    # ================== CONFIRMACIÓN ELIMINAR ==================
    if app.storage.user.get('evento_a_eliminar'):
        eid = app.storage.user['evento_a_eliminar']
        nombre = app.storage.user['evento_nombre']

        with ui.dialog(value=True).props('persistent'):
            with ui.card().classes('w-96 p-8'):
                ui.label(f"¿Eliminar permanentemente el evento **{nombre}**?").classes('text-xl font-bold mb-6')
                with ui.row().classes('w-full gap-4'):
                    def cancelar():
                        app.storage.user.pop('evento_a_eliminar', None)
                        app.storage.user.pop('evento_nombre', None)
                        ui.refresh()

                    ui.button('Cancelar', on_click=cancelar).props('flat')

                    def confirmar():
                        supabase.table("asignaciones").delete().eq("evento_id", eid).execute()
                        supabase.table("eventos").delete().eq("id", eid).execute()
                        app.storage.user.pop('evento_a_eliminar', None)
                        app.storage.user.pop('evento_nombre', None)
                        ui.notify('Evento eliminado', type='positive')
                        ui.refresh()

                    ui.button('Sí, eliminar', on_click=confirmar).props('color=negative flat')