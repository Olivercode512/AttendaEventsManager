# pages/eventos.py  ← VERSIÓN FINAL DEFINITIVA (enlaces externos corregidos + botón Cancelar + todo funcional)
import streamlit as st
from datetime import datetime
from supabase import create_client
from config.settings import Config
from utils.whatsapp import crear_grupo_whatsapp

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

st.title("Eventos")

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
        if delta > 0:
            supabase.table("nominas_mensuales").insert({
                "camarero_id": camarero_id,
                "mes": mes_evento,
                "horas_acumuladas": delta,
                "importe_acumulado": importe_delta
            }).execute()

# ================== CREAR NUEVO EVENTO ==================
with st.expander("Crear nuevo evento", expanded=True):
    with st.form("nuevo_evento"):
        col1, col2 = st.columns(2)
        with col1:
            catering = st.text_input("Nombre del catering / cliente", placeholder="Boda Ana S.L.")
            lugar = st.text_input("Lugar del evento", placeholder="Finca Sant Salvador")
        with col2:
            fecha = st.date_input("Fecha", datetime.now())

        st.markdown("### Horario del evento")
        col_hora1, col_hora2 = st.columns(2)
        with col_hora1:
            inicio = st.time_input("Hora inicio", value=datetime.now().time(), key="hora_inicio_nuevo")
        with col_hora2:
            fin = st.time_input("Hora fin", value=datetime.now().time(), key="hora_fin_nuevo")

        num_coches = st.number_input(
            "¿Cuántos coches se necesitan para transportar camareros? (0 = ninguno)",
            min_value=0, value=0, step=1, key="num_coches_nuevo"
        )

        st.markdown("### Maître del evento")
        nombre_maitre = st.text_input("Nombre del maître (viene del catering)", placeholder="Carlos Ruiz...")

        st.markdown("### Asignar personal")
        todos_camareros = supabase.table("camareros")\
            .select("id, nombre, apellidos, telefono, email")\
            .eq("activo", True)\
            .execute().data

        opciones = {f"{c['nombre']} {c.get('apellidos','')}": c for c in todos_camareros}

        st.markdown("**Seleccionar responsables**")
        responsables_seleccionados = st.multiselect(
            "Responsables (tienen rol de responsable + tarea)",
            options=list(opciones.keys()),
            default=[], key="responsables_nuevo"
        )

        if st.session_state.get("responsables_prev_nuevo") != responsables_seleccionados:
            st.session_state.responsables_prev_nuevo = responsables_seleccionados.copy()
            st.rerun()

        st.markdown("**Seleccionar camareros normales**")
        camareros_disponibles = {k: v for k, v in opciones.items() if k not in responsables_seleccionados}
        camareros_seleccionados = st.multiselect(
            "Camareros normales",
            options=list(camareros_disponibles.keys()),
            default=[], key="camareros_nuevo"
        )

        tareas = {}
        personal_total = responsables_seleccionados + camareros_seleccionados
        if personal_total:
            st.markdown("### Asignar tarea a cada persona")
            for nombre in personal_total:
                rol_texto = " (Responsable)" if nombre in responsables_seleccionados else ""
                tareas[nombre] = st.selectbox(
                    f"Tarea para {nombre}{rol_texto}",
                    options=[
                        "Montaje + Servicio",
                        "Servicio",
                        "Servicio + Cierre",
                        "Montaje + Servicio + Cierre"
                    ],
                    index=0,
                    key=f"tarea_nuevo_{nombre}"
                )

        if st.form_submit_button("Crear evento + grupo WhatsApp", type="primary"):
            if not catering.strip() or not lugar.strip():
                st.error("Catering y lugar son obligatorios")
            else:
                datos_evento = {
                    "catering": catering.strip(),
                    "lugar": lugar.strip(),
                    "fecha": str(fecha),
                    "hora_inicio": inicio.strftime("%H:%M"),
                    "hora_fin": fin.strftime("%H:%M"),
                    "num_coches": num_coches,
                    "nombre_maitre": nombre_maitre.strip() if nombre_maitre.strip() else None
                }

                res = supabase.table("eventos").insert(datos_evento).execute()
                evento_id = res.data[0]["id"]

                camareros_para_whatsapp = []
                for nombre in personal_total:
                    c = opciones[nombre]
                    rol = "Responsable" if nombre in responsables_seleccionados else "Camarero"
                    tarea = tareas.get(nombre, "Servicio")
                    supabase.table("asignaciones").insert({
                        "evento_id": evento_id,
                        "camarero_id": c["id"],
                        "rol": rol,
                        "tarea": tarea,
                        "horas_trabajadas": 0
                    }).execute()
                    camareros_para_whatsapp.append(c)

                if camareros_para_whatsapp:
                    enlace, nombre_grupo = crear_grupo_whatsapp(datos_evento, camareros_para_whatsapp, "Attenda Events")
                    st.success(f"¡Evento creado! → {nombre_grupo}")
                    st.balloons()
                    st.markdown(f"### [ABRIR GRUPO WHATSAPP]({enlace})")
                    st.code(enlace, language=None)
                else:
                    st.info("Evento creado sin personal asignado")

                st.rerun()

# ================== LISTA DE EVENTOS ==================
st.markdown("### Eventos")

eventos = supabase.table("eventos").select("*").order("fecha", desc=True).execute().data

if not eventos:
    st.info("No hay eventos creados aún.")
else:
    hoy = datetime.now().date()

    proximos = [e for e in eventos if datetime.strptime(e['fecha'], "%Y-%m-%d").date() > hoy]
    en_directo = [e for e in eventos if datetime.strptime(e['fecha'], "%Y-%m-%d").date() == hoy]
    finalizados = [e for e in eventos if datetime.strptime(e['fecha'], "%Y-%m-%d").date() < hoy]

    tab_proximos, tab_directo, tab_finalizados = st.tabs([
        f"📅 Próximamente ({len(proximos)})",
        f"🔥 En directo ({len(en_directo)})",
        f"🏁 Finalizados ({len(finalizados)})"
    ])

    def mostrar_evento(evento):
        catering = evento.get("catering", "Sin catering")
        lugar = evento.get("lugar", "Sin lugar")
        fecha = evento.get("fecha", "Sin fecha")
        hora_inicio = evento.get("hora_inicio", "?")
        hora_fin = evento.get("hora_fin", "?")

        with st.expander(f"**{catering}** – {lugar} – {fecha} ({hora_inicio}-{hora_fin})"):
            asignaciones = supabase.table("asignaciones")\
                .select("*, camareros(nombre, apellidos, telefono, email)")\
                .eq("evento_id", evento['id'])\
                .execute().data

            responsables_asignados = len([a for a in asignaciones if a.get("rol") == "Responsable"])
            camareros_asignados = len([a for a in asignaciones if a.get("rol") == "Camarero"])

            st.write(f"**Camareros que vienen:** {camareros_asignados}")
            st.write(f"**Responsables que vienen:** {responsables_asignados}")
            st.write(f"**Personal total que viene:** {camareros_asignados + responsables_asignados}")
            st.write(f"**Coches para transportar camareros:** {evento.get('num_coches', 0)}")
            st.write(f"**Maître:** {evento.get('nombre_maitre') or 'No asignado'}")

            key_toggle = f"toggle_personal_{evento['id']}"
            currently_visible = st.session_state.get(key_toggle, False)
            button_label = "👥 Ocultar personal asignado" if currently_visible else "👥 Ver personal asignado"

            if st.button(button_label, type="primary", key=f"btn_toggle_{evento['id']}"):
                nuevo_estado = not currently_visible
                st.session_state[key_toggle] = nuevo_estado
                st.rerun()

            # Botones Editar y Eliminar evento
            col_edit_del = st.columns(2)
            with col_edit_del[0]:
                if st.button("✏️ Editar evento", type="secondary", key=f"edit_btn_{evento['id']}"):
                    st.session_state.editando_evento = evento['id']
                    st.rerun()
            with col_edit_del[1]:
                if st.button("🗑️ Eliminar evento", type="primary", key=f"del_btn_{evento['id']}"):
                    st.session_state.evento_a_eliminar = evento['id']
                    st.session_state.evento_nombre = catering
                    st.rerun()

            # Formulario edición evento
            if st.session_state.get("editando_evento") == evento['id']:
                with st.form("form_editar_evento"):
                    st.markdown("### ✏️ Editar evento")
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_catering = st.text_input("Catering / cliente", value=catering)
                        nuevo_lugar = st.text_input("Lugar", value=lugar)
                    with col2:
                        nueva_fecha = st.date_input("Fecha", value=datetime.strptime(fecha, "%Y-%m-%d"))

                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        nueva_inicio = st.time_input("Hora inicio", value=datetime.strptime(hora_inicio, "%H:%M"))
                    with col_h2:
                        nueva_fin = st.time_input("Hora fin", value=datetime.strptime(hora_fin, "%H:%M"))

                    nuevo_coches = st.number_input("Coches necesarios", min_value=0, value=evento.get("num_coches", 0))
                    nuevo_maitre = st.text_input("Maître", value=evento.get("nombre_maitre") or "")

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Guardar cambios", type="primary"):
                            supabase.table("eventos").update({
                                "catering": nuevo_catering.strip(),
                                "lugar": nuevo_lugar.strip(),
                                "fecha": str(nueva_fecha),
                                "hora_inicio": nueva_inicio.strftime("%H:%M"),
                                "hora_fin": nueva_fin.strftime("%H:%M"),
                                "num_coches": nuevo_coches,
                                "nombre_maitre": nuevo_maitre.strip() if nuevo_maitre.strip() else None
                            }).eq("id", evento['id']).execute()
                            del st.session_state.editando_evento
                            st.success("Evento actualizado")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.editando_evento
                            st.rerun()

            if st.session_state.get(key_toggle, False):
                if asignaciones:
                    # RESPONSABLES
                    responsables = [a for a in asignaciones if a.get("rol") == "Responsable"]
                    if responsables:
                        col_title_add = st.columns([8, 2])
                        with col_title_add[0]:
                            st.markdown("#### 👤 Responsables por tarea")
                        with col_title_add[1]:
                            if st.button("➕ Agregar", key=f"add_resp_{evento['id']}"):
                                st.session_state.agregar_responsable = evento['id']
                                st.rerun()

                        busqueda_resp = st.text_input("🔍 Buscar responsable", key=f"busq_resp_{evento['id']}")
                        responsables_filtrados = responsables
                        if busqueda_resp:
                            lower = busqueda_resp.lower()
                            responsables_filtrados = [a for a in responsables if lower in f"{a['camareros']['nombre']} {a['camareros'].get('apellidos','')}".lower()]

                        if responsables_filtrados:
                            tareas_responsables = sorted(set(a.get("tarea", "Servicio") for a in responsables_filtrados))
                            tabs_responsables = st.tabs([f"{tarea} ({sum(1 for a in responsables_filtrados if a.get('tarea') == tarea)})" for tarea in tareas_responsables])

                            for tab, tarea in zip(tabs_responsables, tareas_responsables):
                                with tab:
                                    for a in [p for p in responsables_filtrados if p.get("tarea") == tarea]:
                                        nombre = f"{a['camareros'].get('nombre','')} {a['camareros'].get('apellidos','')}".strip()
                                        telefono = (a['camareros'].get('telefono') or '').strip()
                                        email = (a['camareros'].get('email') or '').strip()
                                        horas_actual = a.get("horas_trabajadas", 0)
                                        horas = horas_actual // 4
                                        minutos = (horas_actual % 4) * 15

                                        col_nom_quit = st.columns([8.5, 1.5])
                                        with col_nom_quit[0]:
                                            with st.expander(f"**{nombre}**"):
                                                st.markdown("**Horas realizadas en el evento**")
                                                col_horas = st.columns([1, 1, 2, 3])
                                                with col_horas[0]:
                                                    nueva_horas = st.number_input("Horas", min_value=0, value=horas, step=1,
                                                                                  key=f"horas_resp_{a['id']}_{evento['id']}")
                                                with col_horas[1]:
                                                    nueva_minutos = st.number_input("Min", min_value=0, max_value=45, value=minutos, step=15,
                                                                                    key=f"min_resp_{a['id']}_{evento['id']}")
                                                with col_horas[2]:
                                                    st.write("")

                                                nuevo_total = nueva_horas * 4 + (nueva_minutos // 15)

                                                with col_horas[3]:
                                                    if st.button("💰 Cargar", key=f"cargar_resp_{a['id']}_{evento['id']}", type="primary"):
                                                        if nuevo_total != horas_actual:
                                                            supabase.table("asignaciones").update({"horas_trabajadas": nuevo_total}).eq("id", a['id']).execute()
                                                            actualizar_nomina(a["camarero_id"], nuevo_total, horas_actual, evento["fecha"])
                                                            delta_h = (nuevo_total - horas_actual) // 4
                                                            delta_m = (nuevo_total - horas_actual) % 4 * 15
                                                            if delta_h >= 0:
                                                                st.success(f"✅ +{delta_h}h {delta_m}min cargadas a nómina")
                                                            else:
                                                                st.success(f"⚠️ -{abs(delta_h)}h {abs(delta_m)}min corregidas en nómina")
                                                            st.rerun()
                                                        else:
                                                            st.info("Las horas no han cambiado")

                                                col_acc = st.columns([1, 1, 1, 1])
                                                with col_acc[0]:
                                                    if telefono:
                                                        tel_clean = telefono.lstrip('+').replace(' ', '').replace('-', '')
                                                        st.markdown(f'<a href="tel:{tel_clean}" target="_blank">☎️</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[1]:
                                                    if telefono:
                                                        tel_clean = telefono.lstrip('+').replace(' ', '').replace('-', '')
                                                        st.markdown(f'<a href="https://wa.me/{tel_clean}" target="_blank">💬</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[2]:
                                                    if email:
                                                        st.markdown(f'<a href="mailto:{email}" target="_blank">✉️</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[3]:
                                                    if st.button("✏️", key=f"edit_resp_{a['id']}"):
                                                        st.session_state.edit_tarea_id = a['id']
                                                        st.session_state.edit_tarea_evento = evento['id']
                                                        st.rerun()

                                        with col_nom_quit[1]:
                                            if st.button("🗑️", type="secondary", key=f"quit_resp_{a['id']}"):
                                                supabase.table("asignaciones").delete().eq("id", a['id']).execute()
                                                st.success(f"{nombre} quitado")
                                                st.rerun()

                    # CAMAREROS
                    camareros = [a for a in asignaciones if a.get("rol") == "Camarero"]
                    if camareros:
                        col_title_add_cam = st.columns([8, 2])
                        with col_title_add_cam[0]:
                            st.markdown("#### 👥 Camareros por tarea")
                        with col_title_add_cam[1]:
                            if st.button("➕ Agregar", key=f"add_cam_{evento['id']}"):
                                st.session_state.agregar_camarero = evento['id']
                                st.rerun()

                        busqueda_cam = st.text_input("🔍 Buscar camarero", key=f"busq_cam_{evento['id']}")
                        camareros_filtrados = camareros
                        if busqueda_cam:
                            lower = busqueda_cam.lower()
                            camareros_filtrados = [a for a in camareros if lower in f"{a['camareros']['nombre']} {a['camareros'].get('apellidos','')}".lower()]

                        if camareros_filtrados:
                            tareas_cam = sorted(set(a.get("tarea", "Servicio") for a in camareros_filtrados))
                            tabs_cam = st.tabs([f"{t} ({sum(1 for a in camareros_filtrados if a.get('tarea') == t)})" for t in tareas_cam])

                            for tab, tarea in zip(tabs_cam, tareas_cam):
                                with tab:
                                    for a in [p for p in camareros_filtrados if p.get("tarea") == tarea]:
                                        nombre = f"{a['camareros'].get('nombre','')} {a['camareros'].get('apellidos','')}".strip()
                                        telefono = (a['camareros'].get('telefono') or '').strip()
                                        email = (a['camareros'].get('email') or '').strip()
                                        horas_actual = a.get("horas_trabajadas", 0)
                                        horas = horas_actual // 4
                                        minutos = (horas_actual % 4) * 15

                                        col_nom_quit = st.columns([8.5, 1.5])
                                        with col_nom_quit[0]:
                                            with st.expander(f"**{nombre}**"):
                                                st.markdown("**Horas realizadas en el evento**")
                                                col_horas = st.columns([1, 1, 2, 3])
                                                with col_horas[0]:
                                                    nueva_horas = st.number_input("Horas", min_value=0, value=horas, step=1,
                                                                                  key=f"horas_cam_{a['id']}_{evento['id']}")
                                                with col_horas[1]:
                                                    nueva_minutos = st.number_input("Min", min_value=0, max_value=45, value=minutos, step=15,
                                                                                    key=f"min_cam_{a['id']}_{evento['id']}")
                                                with col_horas[2]:
                                                    st.write("")

                                                nuevo_total = nueva_horas * 4 + (nueva_minutos // 15)

                                                with col_horas[3]:
                                                    if st.button("💰 Cargar", key=f"cargar_cam_{a['id']}_{evento['id']}", type="primary"):
                                                        if nuevo_total != horas_actual:
                                                            supabase.table("asignaciones").update({"horas_trabajadas": nuevo_total}).eq("id", a['id']).execute()
                                                            actualizar_nomina(a["camarero_id"], nuevo_total, horas_actual, evento["fecha"])
                                                            delta_h = (nuevo_total - horas_actual) // 4
                                                            delta_m = (nuevo_total - horas_actual) % 4 * 15
                                                            if delta_h >= 0:
                                                                st.success(f"✅ +{delta_h}h {delta_m}min cargadas a nómina")
                                                            else:
                                                                st.success(f"⚠️ -{abs(delta_h)}h {abs(delta_m)}min corregidas en nómina")
                                                            st.rerun()
                                                        else:
                                                            st.info("Las horas no han cambiado")

                                                col_acc = st.columns([1, 1, 1, 1])
                                                with col_acc[0]:
                                                    if telefono:
                                                        tel_clean = telefono.lstrip('+').replace(' ', '').replace('-', '')
                                                        st.markdown(f'<a href="tel:{tel_clean}" target="_blank">☎️</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[1]:
                                                    if telefono:
                                                        tel_clean = telefono.lstrip('+').replace(' ', '').replace('-', '')
                                                        st.markdown(f'<a href="https://wa.me/{tel_clean}" target="_blank">💬</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[2]:
                                                    if email:
                                                        st.markdown(f'<a href="mailto:{email}" target="_blank">✉️</a>', unsafe_allow_html=True)
                                                    else:
                                                        st.write("—")
                                                with col_acc[3]:
                                                    if st.button("✏️", key=f"edit_cam_{a['id']}"):
                                                        st.session_state.edit_tarea_id = a['id']
                                                        st.session_state.edit_tarea_evento = evento['id']
                                                        st.rerun()

                                        with col_nom_quit[1]:
                                            if st.button("🗑️", type="secondary", key=f"quit_cam_{a['id']}"):
                                                supabase.table("asignaciones").delete().eq("id", a['id']).execute()
                                                st.success(f"{nombre} quitado")
                                                st.rerun()

                else:
                    st.info("Sin personal asignado aún")

            # ================== AGREGAR RESPONSABLE CON CANCELAR ==================
            if st.session_state.get("agregar_responsable") == evento['id']:
                with st.form("add_resp_form"):
                    st.markdown("### ➕ Agregar responsable")
                    ids_asignados = [a["camarero_id"] for a in asignaciones]
                    disponibles = supabase.table("camareros").select("id, nombre, apellidos").eq("activo", True).not_.in_("id", ids_asignados).execute().data
                    if not disponibles:
                        st.info("No hay más camareros disponibles.")
                        if st.button("Cancelar"):
                            del st.session_state.agregar_responsable
                            st.rerun()
                    else:
                        opciones = {f"{c['nombre']} {c.get('apellidos','')}": c['id'] for c in disponibles}
                        sel = st.selectbox("Persona", options=list(opciones.keys()))
                        tarea = st.selectbox("Tarea", options=["Montaje + Servicio", "Servicio", "Servicio + Cierre", "Montaje + Servicio + Cierre"])

                        col_agregar, col_cancelar = st.columns(2)
                        with col_agregar:
                            if st.form_submit_button("Agregar", type="primary"):
                                supabase.table("asignaciones").insert({
                                    "evento_id": evento['id'],
                                    "camarero_id": opciones[sel],
                                    "rol": "Responsable",
                                    "tarea": tarea,
                                    "horas_trabajadas": 0
                                }).execute()
                                del st.session_state.agregar_responsable
                                st.success("Responsable agregado")
                                st.rerun()
                        with col_cancelar:
                            if st.form_submit_button("Cancelar"):
                                del st.session_state.agregar_responsable
                                st.rerun()

            # ================== AGREGAR CAMARERO CON CANCELAR ==================
            if st.session_state.get("agregar_camarero") == evento['id']:
                with st.form("add_cam_form"):
                    st.markdown("### ➕ Agregar camarero")
                    ids_asignados = [a["camarero_id"] for a in asignaciones]
                    disponibles = supabase.table("camareros").select("id, nombre, apellidos").eq("activo", True).not_.in_("id", ids_asignados).execute().data
                    if not disponibles:
                        st.info("No hay más camareros disponibles.")
                        if st.button("Cancelar"):
                            del st.session_state.agregar_camarero
                            st.rerun()
                    else:
                        opciones = {f"{c['nombre']} {c.get('apellidos','')}": c['id'] for c in disponibles}
                        sel = st.selectbox("Persona", options=list(opciones.keys()))
                        tarea = st.selectbox("Tarea", options=["Montaje + Servicio", "Servicio", "Servicio + Cierre", "Montaje + Servicio + Cierre"])

                        col_agregar, col_cancelar = st.columns(2)
                        with col_agregar:
                            if st.form_submit_button("Agregar", type="primary"):
                                supabase.table("asignaciones").insert({
                                    "evento_id": evento['id'],
                                    "camarero_id": opciones[sel],
                                    "rol": "Camarero",
                                    "tarea": tarea,
                                    "horas_trabajadas": 0
                                }).execute()
                                del st.session_state.agregar_camarero
                                st.success("Camarero agregado")
                                st.rerun()
                        with col_cancelar:
                            if st.form_submit_button("Cancelar"):
                                del st.session_state.agregar_camarero
                                st.rerun()

            # ================== EDITOR DE TAREA ==================
            if st.session_state.get("edit_tarea_id") and st.session_state.get("edit_tarea_evento") == evento['id']:
                asignacion = supabase.table("asignaciones")\
                    .select("*, camareros(nombre, apellidos)")\
                    .eq("id", st.session_state.edit_tarea_id)\
                    .execute().data[0]

                nombre = f"{asignacion['camareros'].get('nombre','')} {asignacion['camareros'].get('apellidos','')}".strip()
                tarea_actual = asignacion.get("tarea", "Servicio")

                st.markdown(f"### ✏️ Editar tarea de **{nombre}**")

                nueva_tarea = st.selectbox(
                    "Selecciona la nueva tarea",
                    options=[
                        "Montaje + Servicio",
                        "Servicio",
                        "Servicio + Cierre",
                        "Montaje + Servicio + Cierre"
                    ],
                    index=["Montaje + Servicio", "Servicio", "Servicio + Cierre", "Montaje + Servicio + Cierre"].index(tarea_actual)
                )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Guardar tarea", type="primary"):
                        supabase.table("asignaciones").update({"tarea": nueva_tarea}).eq("id", asignacion['id']).execute()
                        del st.session_state.edit_tarea_id
                        del st.session_state.edit_tarea_evento
                        st.success(f"Tarea de {nombre} actualizada a **{nueva_tarea}**")
                        st.rerun()
                with col_cancel:
                    if st.button("Cancelar"):
                        del st.session_state.edit_tarea_id
                        del st.session_state.edit_tarea_evento
                        st.rerun()

    with tab_proximos:
        if proximos:
            for e in proximos:
                mostrar_evento(e)
        else:
            st.info("No hay eventos próximos.")

    with tab_directo:
        if en_directo:
            for e in en_directo:
                mostrar_evento(e)
        else:
            st.info("No hay eventos en directo hoy.")

    with tab_finalizados:
        if finalizados:
            for e in finalizados:
                mostrar_evento(e)
        else:
            st.info("No hay eventos finalizados.")

# ================== CONFIRMACIÓN ELIMINAR EVENTO ==================
if st.session_state.get("evento_a_eliminar"):
    eid = st.session_state.evento_a_eliminar
    nombre = st.session_state.evento_nombre
    st.error(f"¿Eliminar permanentemente el evento **{nombre}**?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sí, eliminar", type="primary"):
            supabase.table("asignaciones").delete().eq("evento_id", eid).execute()
            supabase.table("eventos").delete().eq("id", eid).execute()
            del st.session_state.evento_a_eliminar
            del st.session_state.evento_nombre
            st.success("Evento eliminado")
            st.rerun()
    with c2:
        if st.button("Cancelar"):
            del st.session_state.evento_a_eliminar
            del st.session_state.evento_nombre
            st.rerun()