# pages/camareros.py
import streamlit as st
import re
from supabase import create_client
from config.settings import Config
import urllib.parse

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

st.title("FICHA DE EMPLEADOS")

# ================== AÑADIR NUEVO CAMARERO ==================
with st.expander("Añadir nuevo camarero", expanded=True):
    with st.form("nuevo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos", value="")
            telefono = st.text_input("Teléfono", placeholder="+34 609 159 167")
            email = st.text_input("Email")
            dni = st.text_input("DNI")
        with col2:
            residencia = st.text_input("Lugar de residencia")
            nacionalidad = st.text_input("Nacionalidad")
            idiomas = st.text_input("Idiomas")
            tiene_coche = st.checkbox("Tiene coche")
            curso_prl = st.checkbox("Tiene curso PRL")

        col3, col4 = st.columns(2)
        with col3:
            numero_ss = st.text_input("Nº Seguridad Social")
            iban = st.text_input("IBAN")
        with col4:
            tarifa = st.number_input("Tarifa neta (€/hora)", min_value=8.0, value=12.0, step=0.5)

        if st.form_submit_button("Guardar camarero", type="primary"):
            if not nombre.strip():
                st.error("Nombre obligatorio")
            else:
                datos = {"nombre": nombre.strip(), "activo": True}
                if apellidos.strip(): datos["apellidos"] = apellidos.strip()
                if telefono.strip(): datos["telefono"] = telefono.strip()
                if email.strip(): datos["email"] = email.strip()
                if dni.strip(): datos["dni"] = dni.strip()
                if residencia.strip(): datos["residencia"] = residencia.strip()
                if nacionalidad.strip(): datos["nacionalidad"] = nacionalidad.strip()
                if idiomas.strip(): datos["idiomas"] = idiomas.strip()
                datos["tiene_coche"] = tiene_coche
                datos["curso_prl"] = curso_prl
                if numero_ss.strip(): datos["numero_ss"] = numero_ss.strip()
                if iban.strip(): datos["iban"] = iban.strip()
                datos["tarifa_neta"] = tarifa

                supabase.table("camareros").insert(datos).execute()
                st.success(f"¡{nombre} añadido!")
                st.balloons()

# ================== BUSCADOR EN TIEMPO REAL ==================
st.markdown("### Buscar camarero")
busqueda = st.text_input(
    "",
    placeholder="Escribe nombre o apellidos...",
    key="buscador_camareros"
)

# Cargar todos los camareros
camareros = supabase.table("camareros").select("*").order("nombre").execute().data

# Filtrar según búsqueda
camareros_mostrar = camareros
if busqueda.strip():
    termino = busqueda.strip().lower()
    camareros_mostrar = [
        c for c in camareros
        if termino in (c.get("nombre") or "").lower() or
           termino in (c.get("apellidos") or "").lower()
    ]

st.markdown(f"**Mostrando {len(camareros_mostrar)} de {len(camareros)} camareros**")

# ================== LISTA DE CAMAREROS CON TODO ==================
for c in camareros_mostrar:
    nombre_completo = f"{c.get('nombre', '')} {c.get('apellidos', '')}".strip()
    tel = c.get("telefono") or "Sin teléfono"

    # === MEDIA DE VALORACIÓN CON ESTRELLITAS ===
    feedback = supabase.table("feedback_camareros")\
        .select("valoracion")\
        .eq("camarero_id", c['id'])\
        .execute().data

    if feedback:
        media = sum(f["valoracion"] for f in feedback) / len(feedback)
        media_redondeada = round(media, 1)
        estrellas_llenas = "⭐" * int(media_redondeada)
        media_texto = f" – **{media_redondeada}/5** {estrellas_llenas} ({len(feedback)} valoraciones)"
    else:
        media_texto = " – Sin valoraciones"

    with st.expander(f"**{nombre_completo}** – {tel}{media_texto}"):
        col1, col2, col3 = st.columns([5, 2, 2])  # Espacio amplio

        # ================== EDICIÓN ==================
        with col1:
            with st.form(key=f"edit_{c['id']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    nuevo_nombre = st.text_input("Nombre", value=c.get('nombre', ''), key=f"n_{c['id']}")
                    nuevo_apellidos = st.text_input("Apellidos", value=c.get('apellidos', ''), key=f"a_{c['id']}")
                    nuevo_telefono = st.text_input("Teléfono", value=c.get('telefono', ''), key=f"t_{c['id']}")
                    nuevo_email = st.text_input("Email", value=c.get('email', ''), key=f"e_{c['id']}")
                    nuevo_dni = st.text_input("DNI", value=c.get('dni', ''), key=f"d_{c['id']}")
                with col_b:
                    nuevo_residencia = st.text_input("Residencia", value=c.get('residencia', ''), key=f"r_{c['id']}")
                    nuevo_nacionalidad = st.text_input("Nacionalidad", value=c.get('nacionalidad', ''), key=f"na_{c['id']}")
                    nuevo_idiomas = st.text_input("Idiomas", value=c.get('idiomas', ''), key=f"i_{c['id']}")
                    nuevo_coche = st.checkbox("Tiene coche", value=c.get('tiene_coche', False), key=f"coche_{c['id']}")
                    nuevo_prl = st.checkbox("Curso PRL", value=c.get('curso_prl', False), key=f"prl_{c['id']}")

                col_c, col_d = st.columns(2)
                with col_c:
                    nuevo_ss = st.text_input("Nº SS", value=c.get('numero_ss', ''), key=f"ss_{c['id']}")
                    nuevo_iban = st.text_input("IBAN", value=c.get('iban', ''), key=f"iban_{c['id']}")
                with col_d:
                    nuevo_tarifa = st.number_input("Tarifa neta", min_value=8.0, value=float(c.get('tarifa_neta', 12.0)), step=0.5, key=f"tarifa_{c['id']}")

                if st.form_submit_button("Guardar cambios", type="secondary"):
                    datos = {"nombre": nuevo_nombre.strip()}
                    if nuevo_apellidos.strip(): datos["apellidos"] = nuevo_apellidos.strip()
                    if nuevo_telefono.strip(): datos["telefono"] = nuevo_telefono.strip()
                    if nuevo_email.strip(): datos["email"] = nuevo_email.strip()
                    if nuevo_dni.strip(): datos["dni"] = nuevo_dni.strip()
                    if nuevo_residencia.strip(): datos["residencia"] = nuevo_residencia.strip()
                    if nuevo_nacionalidad.strip(): datos["nacionalidad"] = nuevo_nacionalidad.strip()
                    if nuevo_idiomas.strip(): datos["idiomas"] = nuevo_idiomas.strip()
                    datos["tiene_coche"] = nuevo_coche
                    datos["curso_prl"] = nuevo_prl
                    if nuevo_ss.strip(): datos["numero_ss"] = nuevo_ss.strip()
                    if nuevo_iban.strip(): datos["iban"] = nuevo_iban.strip()
                    datos["tarifa_neta"] = nuevo_tarifa

                    supabase.table("camareros").update(datos).eq("id", c['id']).execute()
                    st.success("¡Datos actualizados!")
                    st.rerun()

        # ================== COMUNICACIÓN ==================
        with col2:
            if c.get('telefono'):
                tel_clean = c['telefono'].lstrip('+').replace(' ', '')
                st.link_button("Llamar", f"tel:{c['telefono']}", use_container_width=True)
                st.link_button("WhatsApp", f"https://wa.me/{tel_clean}", use_container_width=True)

            if c.get('email') and c['email'].strip():
                email = c['email'].strip()
                asunto = urllib.parse.quote("Attenda Events – Información importante")
                cuerpo = urllib.parse.quote(
                    f"Hola {c.get('nombre', '')},\n\n"
                    "Te escribimos desde Attenda Events.\n\n"
                    "Aquí tienes información importante sobre próximos eventos o detalles importantes:\n\n"
                    "¡Gracias!\n"
                    "El equipo de Attenda Events"
                )
                enlace_email = f"https://mail.google.com/mail/?view=cm&fs=1&to={email}&su={asunto}&body={cuerpo}"
                st.link_button("Enviar email", enlace_email, use_container_width=True)
            else:
                st.write("Sin email")

            activo = st.toggle("Disponible", value=c.get('activo', True), key=f"act_{c['id']}")
            if activo != c.get('activo', True):
                supabase.table("camareros").update({"activo": activo}).eq("id", c['id']).execute()
                st.rerun()

        # ================== ACCIONES ==================
        with col3:
            if st.button("Asignar a evento", key=f"asignar_{c['id']}", use_container_width=True):
                if not c.get('activo'):
                    st.toast("Camarero no disponible")
                else:
                    st.session_state.camarero_para_asignar = c['id']
                    st.switch_page("pages/eventos.py")

            if st.button("Eliminar camarero", key=f"eliminar_{c['id']}", type="secondary", use_container_width=True):
                st.session_state.camarero_a_eliminar = c['id']
                st.session_state.nombre_a_eliminar = nombre_completo
                st.rerun()

        # ================== FEEDBACK CON ESTRELLITAS ==================
        st.markdown("### Feedback de eventos")
        feedback_res = supabase.table("feedback_camareros")\
            .select("*, eventos!inner(cliente, fecha)")\
            .eq("camarero_id", c['id'])\
            .order("fecha", desc=True)\
            .execute().data

        if feedback_res:
            for f in feedback_res:
                estrellas = "⭐" * f["valoracion"] + "☆" * (5 - f["valoracion"])
                with st.container():
                    st.write(f"**{f['eventos']['cliente']}** – {f['eventos']['fecha']}")
                    st.write(f"{estrellas} ({f['valoracion']}/5)")
                    if f["comentario"]:
                        st.caption(f"_{f['comentario']}_")
                    st.markdown("---")
        else:
            st.info("Aún no tiene feedback")

        # Añadir nuevo feedback
        with st.expander("Añadir valoración", expanded=False):
            with st.form(key=f"fb_form_{c['id']}"):
                eventos_res = supabase.table("eventos").select("id, cliente, fecha").execute().data
                opciones = {f"{e['cliente']} – {e['fecha']}": e['id'] for e in eventos_res}
                evento_nombre = st.selectbox("Evento", [""] + list(opciones.keys()), key=f"fb_evento_{c['id']}")
                valoracion = st.slider("Valoración", 1, 5, 3, key=f"fb_stars_{c['id']}")
                comentario = st.text_area("Comentario (opcional)", key=f"fb_com_{c['id']}", height=100)

                if st.form_submit_button("Guardar valoración", type="primary"):
                    if not evento_nombre:
                        st.error("Selecciona un evento")
                    else:
                        evento_id = opciones[evento_nombre]
                        supabase.table("feedback_camareros").insert({
                            "camarero_id": c['id'],
                            "evento_id": evento_id,
                            "valoracion": valoracion,
                            "comentario": comentario.strip() if comentario.strip() else None
                        }).execute()
                        st.success("¡Valoración guardada!")
                        st.balloons()
                        st.rerun()

# ================== CONFIRMACIÓN ELIMINAR ==================
if st.session_state.get("camarero_a_eliminar"):
    c_id = st.session_state.camarero_a_eliminar
    nombre = st.session_state.nombre_a_eliminar
    st.error(f"¿Eliminar permanentemente a **{nombre}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sí, eliminar", type="primary"):
            supabase.table("camareros").delete().eq("id", c_id).execute()
            del st.session_state.camarero_a_eliminar
            del st.session_state.nombre_a_eliminar
            st.success("Camarero eliminado")
            st.rerun()
    with col2:
        if st.button("Cancelar"):
            del st.session_state.camarero_a_eliminar
            del st.session_state.nombre_a_eliminar
            st.rerun()