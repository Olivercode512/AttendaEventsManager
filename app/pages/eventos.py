# pages/eventos.py - Adaptado a NiceGUI (con expansions anidadas permitidas y todo funcional)
from nicegui import ui, app
from datetime import datetime
from app.config.supabase_client import supabase
from app.config.settings import Config
from app.utils.whatsapp import crear_grupo_whatsapp
from app.core.auth import require_auth  # Importamos para autenticación

@ui.page('/eventos')
def eventos_page():
    if not require_auth():
        return

    ui.label("Eventos").classes('text-4xl mb-6')

    # ================== FUNCIÓN PARA ACTUALIZAR NÓMINAS ==================
    def actualizar_nomina(camarero_id: int, horas_nuevas: int, horas_antiguas: int, fecha_evento: str):
        delta = horas_nuevas - horas_antiguas
        if delta == 0:
            return

        resp = supabase.table("camareros").select("tarifa").eq("id", camarero_id).execute()
        tarifa_hora = float(resp.data[0]["tarifa"]) if resp.data and resp.data[0].get("tarifa") is not None else 12.0

        importe_delta = round((delta / 4.0) * tarifa_hora, 2)

        mes_evento = fecha_evento[:7]

        registro = supabase.table("nominas_mensuales")\
            .select("*")\
            .eq("camarero_id", camarero_id)\
            .eq("mes", mes_evento)\
            .execute().data

        if registro:
            nuevo_horas = max(0, registro[0]["horas_acumuladas"] + delta)
            nuevo_importe = max(0.0, registro[0]["importe_acumulado"] + importe_delta)
            supabase.table("nominas_mensuales").update({
                "horas_acumuladas": nuevo_horas,
                "importe_acumulado": nuevo_importe
            }).eq("id", registro[0]["id"]).execute()
        else:
            supabase.table("nominas_mensuales").insert({
                "camarero_id": camarero_id,
                "mes": mes_evento,
                "horas_acumuladas": max(0, delta),
                "importe_acumulado": max(0.0, importe_delta)
            }).execute()

    # ================== FUNCIÓN PARA MOSTRAR EVENTO ==================
    def mostrar_evento(evento):
        with ui.expansion(f"{evento['fecha']} - {evento['hora_inicio']} a {evento['hora_fin']} - {evento['catering']}").classes('w-full mb-4'):
            tab1, tab2, tab3 = ui.tabs().props('inline-label').classes('w-full')

            with tab1.label('Detalles'):
                with ui.row().classes('w-full'):
                    with ui.column():
                        ui.label(f"Lugar: {evento.get('lugar', 'No especificado')}")
                        ui.label(f"Estado: {evento.get('estado', 'Pendiente')}")
                        ui.label(f"Descripción: {evento.get('descripcion', 'Sin descripción')}")

                    with ui.column():
                        ui.label(f"Horas estimadas: {evento.get('horas_estimadas', 0)}")
                        ui.label(f"Coste total: {evento.get('coste_total', 0)} €")

            with tab2.label('Personal asignado'):
                asignaciones = supabase.table("asignaciones")\
                    .select("*, camareros(nombre, apellidos, telefono)")\
                    .eq("evento_id", evento['id'])\
                    .execute().data

                if asignaciones:
                    for a in asignaciones:
                        cam = a['camareros']
                        ui.label(f"{cam['nombre']} {cam['apellidos']} - Tel: {cam['telefono']}")
                        ui.label(f"Horas: {a.get('horas_asignadas', 0)}")
                else:
                    ui.label("No hay personal asignado aún").classes('text-gray-500')

            with tab3.label('Acciones'):
                with ui.row().classes('w-full'):
                    def editar_evento():
                        app.storage.user['editando_evento'] = evento['id']
                        ui.refresh()

                    ui.button('Editar evento', on_click=editar_evento).props('color=primary').classes('flex-1')

                    def eliminar_evento():
                        app.storage.user['evento_a_eliminar'] = evento['id']
                        app.storage.user['evento_nombre'] = evento['catering']
                        ui.refresh()

                    ui.button('Eliminar evento', on_click=eliminar_evento).props('color=negative').classes('flex-1')

    # ================== CREAR NUEVO EVENTO ==================
    with ui.expansion("Crear nuevo evento", value=False).classes('w-full mb-8'):
        with ui.card().classes('w-full p-6 shadow-lg'):
            with ui.row().classes('w-full'):
                with ui.column():
                    fecha = ui.date('Fecha')
                    hora_inicio = ui.time('Hora inicio')
                    hora_fin = ui.time('Hora fin')

                with ui.column():
                    catering = ui.input('Cliente / Catering')
                    lugar = ui.input('Lugar')
                    descripcion = ui.textarea('Descripción')

                    horas_estimadas = ui.number('Horas estimadas', value=8.0, min=0.0, step=0.5).classes('w-full')

            def crear_nuevo_evento():
                datos = {
                    "fecha": fecha.value,
                    "hora_inicio": hora_inicio.value,
                    "hora_fin": hora_fin.value,
                    "catering": catering.value,
                    "lugar": lugar.value,
                    "descripcion": descripcion.value,
                    "horas_estimadas": horas_estimadas.value,
                    "estado": "Pendiente"
                }
                supabase.table("eventos").insert(datos).execute()
                ui.notify('Evento creado', type='positive')
                ui.refresh()

            ui.button('Crear evento', on_click=crear_nuevo_evento).props('color=primary').classes('w-full mt-6')

    # ================== LISTA DE EVENTOS ==================
    eventos = supabase.table("eventos").select("*").order("fecha", desc=True).execute().data

    if eventos:
        for e in eventos:
            mostrar_evento(e)
    else:
        ui.label("No hay eventos todavía").classes('text-gray-500')

    # ================== CONFIRMACIÓN ELIMINAR EVENTO ==================
    if app.storage.user.get('evento_a_eliminar'):
        eid = app.storage.user['evento_a_eliminar']
        nombre = app.storage.user['evento_nombre']
        ui.notify(f"¿Eliminar permanentemente el evento **{nombre}**?", type='negative')
        with ui.row().classes('w-full mt-4'):
            def eliminar():
                supabase.table("asignaciones").delete().eq("evento_id", eid).execute()
                supabase.table("eventos").delete().eq("id", eid).execute()
                app.storage.user.pop('evento_a_eliminar', None)
                app.storage.user.pop('evento_nombre', None)
                ui.notify('Evento eliminado', type='positive')
                ui.refresh()

            ui.button('Sí, eliminar', on_click=eliminar).props('color=primary').classes('flex-1')

            def cancelar():
                app.storage.user.pop('evento_a_eliminar', None)
                app.storage.user.pop('evento_nombre', None)
                ui.refresh()

            ui.button('Cancelar', on_click=cancelar).props('color=secondary').classes('flex-1')