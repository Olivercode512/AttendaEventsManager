# app/components/event_card.py - Componente reutilizable para mostrar un evento
from nicegui import ui
from config.supabase_client import supabase


def event_card(evento: dict, on_edit=None, on_delete=None):
    """
    Muestra una tarjeta de evento con detalles, botones de acción y expandable para más info.

    Parámetros:
    - evento: dict con los datos del evento (desde Supabase)
    - on_edit: callback opcional para editar (ej: lambda: ui.navigate.to('/edit_evento'))
    - on_delete: callback opcional para eliminar
    """
    with ui.card().classes('w-full shadow-lg rounded-xl p-6 mb-4 hover:shadow-2xl transition-shadow'):
        # Título del evento
        ui.label(f"{evento.get('fecha', 'Sin fecha')} - {evento.get('catering', 'Evento sin nombre')}") \
            .classes('text-xl font-bold text-primary')

        # Subtítulo con horas y lugar
        ui.label(
            f"{evento.get('hora_inicio', '?')} - {evento.get('hora_fin', '?')} | {evento.get('lugar', 'Lugar no especificado')}") \
            .classes('text-sm text-gray-600 mt-1')

        # Estado (badge)
        estado = evento.get('estado', 'Pendiente')
        color = 'positive' if estado == 'Confirmado' else 'warning' if estado == 'Pendiente' else 'negative'
        ui.badge(estado).props(f'color={color}').classes('mt-2')

        # Expandable con más detalles
        with ui.expansion('Ver más detalles', value=False).classes('mt-4'):
            with ui.row().classes('w-full gap-6'):
                with ui.column():
                    ui.label(f"Descripción: {evento.get('descripcion', 'Sin descripción')}").classes('text-gray-700')
                    ui.label(f"Horas estimadas: {evento.get('horas_estimadas', 0)} h").classes('text-gray-700')

                with ui.column():
                    ui.label(f"Coste total estimado: {evento.get('coste_total', 0)} €").classes('text-gray-700')
                    ui.label(f"Asignaciones: {len(evento.get('asignaciones', []))} personas").classes('text-gray-700')

        # Botones de acción
        with ui.row().classes('w-full mt-6 gap-4 justify-end'):
            if on_edit:
                ui.button('Editar', on_click=on_edit, icon='edit').props('color=primary flat')

            if on_delete:
                with ui.dialog() as dialog_delete:
                    with ui.card().classes('w-96 p-6'):
                        ui.label(
                            f"¿Eliminar permanentemente el evento '{evento.get('catering', 'Sin nombre')}'?").classes(
                            'text-lg font-bold')
                        with ui.row().classes('w-full mt-6 gap-4'):
                            ui.button('Cancelar', on_click=dialog_delete.hide).props('flat')
                            ui.button('Sí, eliminar', on_click=lambda: [on_delete(), dialog_delete.hide()]).props(
                                'color=negative flat')

                ui.button('Eliminar', on_click=dialog_delete.open, icon='delete').props('color=negative flat')

    return ui.context.client.elements[-1]  # Devuelve el elemento para poder encadenar si quieres