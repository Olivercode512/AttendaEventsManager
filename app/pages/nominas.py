# pages/nominas.py - Adaptado a NiceGUI (con selector de mes y tabla dinámica)
from nicegui import ui, app
from datetime import datetime
from config.supabase_client import supabase
from core.auth import require_auth  # Para autenticación

@ui.page('/nominas')
def nominas_page():
    if not require_auth():
        return

    ui.label("💼 Nóminas Mensuales").classes('text-4xl mb-6')

    # Selector de mes
    hoy = datetime.now()
    mes_actual = hoy.strftime("%Y-%m")
    mes = ui.input('Mes (formato YYYY-MM)', value=mes_actual, placeholder="Ejemplo: 2025-12").classes('w-48')

    def ver_nomina():
        if not mes.value:
            ui.notify('Introduce un mes válido (YYYY-MM)', type='negative')
            return

        datos = supabase.table("nominas_mensuales")\
            .select("*, camareros(nombre, apellidos, tarifa)")\
            .eq("mes", mes.value)\
            .execute().data

        if not datos:
            ui.notify(f"No hay horas cargadas en {mes.value}", type='warning')
            tabla.clear()
            total_label.set_text("Total a pagar: 0 €")
            return

        filas = []
        total_mes = 0
        for d in datos:
            horas_decimal = d["horas_acumuladas"] / 4.0
            nombre = f"{d['camareros']['nombre']} {d['camareros'].get('apellidos', '')}".strip()
            tarifa = d['camareros'].get('tarifa', 12.0)
            importe = round(d["importe_acumulado"], 2)
            filas.append({
                "Empleado": nombre,
                "Horas": round(horas_decimal, 2),
                "Tarifa €/h": tarifa,
                "A cobrar €": importe
            })
            total_mes += importe

        # Actualizar tabla
        tabla.clear()
        for fila in filas:
            with tabla.add_slot('body-row'):
                ui.td(fila["Empleado"])
                ui.td(fila["Horas"])
                ui.td(fila["Tarifa €/h"])
                ui.td(fila["A cobrar €"])

        total_label.set_text(f"**Total a pagar en {mes.value}: {round(total_mes, 2)} €**")

    ui.button('Ver nómina del mes', on_click=ver_nomina).props('color=primary').classes('mt-4 mb-6')

    # Tabla de resultados
    tabla = ui.table(columns=[
        {'name': 'empleado', 'label': 'Empleado', 'field': 'Empleado'},
        {'name': 'horas', 'label': 'Horas', 'field': 'Horas'},
        {'name': 'tarifa', 'label': 'Tarifa €/h', 'field': 'Tarifa €/h'},
        {'name': 'cobrar', 'label': 'A cobrar €', 'field': 'A cobrar €'}
    ], rows=[]).classes('w-full text-left').props('dense')

    # Label para total
    total_label = ui.markdown("**Total a pagar: 0 €**").classes('text-xl mt-6 font-bold')