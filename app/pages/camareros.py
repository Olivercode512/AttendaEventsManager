# pages/camareros.py - Versión corregida (KeyError 'observaciones' solucionado)
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
            tarifa = st.number_input("Tarifa €/hora", min_value=0.0, value=12.0, step=0.1)
        with col4:
            observaciones = st.text_area("Observaciones", height=100)

        if st.form_submit_button("Guardar camarero", type="primary"):
            if not nombre.strip():
                st.error("El nombre es obligatorio")
            else:
                datos = {
                    "nombre": nombre.strip(),
                    "apellidos": apellidos.strip(),
                    "telefono": telefono.strip(),
                    "email": email.strip(),
                    "dni": dni.strip(),
                    "residencia": residencia.strip(),
                    "nacionalidad": nacionalidad.strip(),
                    "idiomas": idiomas.strip(),
                    "tiene_coche": tiene_coche,
                    "curso_prl": curso_prl,
                    "numero_ss": numero_ss.strip(),
                    "tarifa": tarifa,
                    "observaciones": observaciones.strip() if observaciones.strip() else None
                }
                supabase.table("camareros").insert(datos).execute()
                st.success("¡Camarero añadido!")
                st.rerun()

# ================== LISTA DE CAMAREROS ==================
camareros = supabase.table("camareros").select("*").execute().data

if camareros:
    st.subheader("Lista de camareros")
    for c in camareros:
        with st.expander(f"{c['nombre']} {c['apellidos']} - Tel: {c['telefono']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Email: {c.get('email', 'No disponible')}")
                st.write(f"DNI: {c.get('dni', 'No disponible')}")
                st.write(f"Residencia: {c.get('residencia', 'No disponible')}")
                st.write(f"Nacionalidad: {c.get('nacionalidad', 'No disponible')}")
                st.write(f"Idiomas: {c.get('idiomas', 'No disponible')}")
            with col2:
                st.write(f"Tiene coche: {'Sí' if c.get('tiene_coche') else 'No'}")
                st.write(f"Curso PRL: {'Sí' if c.get('curso_prl') else 'No'}")
                st.write(f"Nº SS: {c.get('numero_ss', 'No disponible')}")
                st.write(f"Tarifa: {c.get('tarifa', 12.0)} €/h")
                st.write(f"Observaciones: {c.get('observaciones') or 'Ninguna'}")  # ← CORRECCIÓN AQUÍ

            # Editar camarero (el resto igual)
            with st.form(f"edit_{c['id']}"):
                st.subheader("Editar camarero")
                col1, col2 = st.columns(2)
                with col1:
                    edit_nombre = st.text_input("Nombre", value=c.get('nombre', ''), key=f"nom_{c['id']}")
                    edit_apellidos = st.text_input("Apellidos", value=c.get('apellidos', ''), key=f"ape_{c['id']}")
                    edit_telefono = st.text_input("Teléfono", value=c.get('telefono', ''), key=f"tel_{c['id']}")
                    edit_email = st.text_input("Email", value=c.get('email', ''), key=f"email_{c['id']}")
                    edit_dni = st.text_input("DNI", value=c.get('dni', ''), key=f"dni_{c['id']}")
                with col2:
                    edit_residencia = st.text_input("Residencia", value=c.get('residencia', ''), key=f"res_{c['id']}")
                    edit_nacionalidad = st.text_input("Nacionalidad", value=c.get('nacionalidad', ''), key=f"nac_{c['id']}")
                    edit_idiomas = st.text_input("Idiomas", value=c.get('idiomas', ''), key=f"idi_{c['id']}")
                    edit_coche = st.checkbox("Tiene coche", value=c.get('tiene_coche', False), key=f"coche_{c['id']}")
                    edit_prl = st.checkbox("Curso PRL", value=c.get('curso_prl', False), key=f"prl_{c['id']}")

                col3, col4 = st.columns(2)
                with col3:
                    edit_ss = st.text_input("Nº SS", value=c.get('numero_ss', ''), key=f"ss_{c['id']}")
                    edit_tarifa = st.number_input("Tarifa €/h", value=c.get('tarifa', 12.0), step=0.1, key=f"tar_{c['id']}")
                with col4:
                    edit_obs = st.text_area("Observaciones", value=c.get('observaciones', ''), height=100, key=f"obs_{c['id']}")

                col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.form_submit_button("Guardar cambios", type="primary"):
                        datos_edit = {
                            "nombre": edit_nombre.strip(),
                            "apellidos": edit_apellidos.strip(),
                            "telefono": edit_telefono.strip(),
                            "email": edit_email.strip(),
                            "dni": edit_dni.strip(),
                            "residencia": edit_residencia.strip(),
                            "nacionalidad": edit_nacionalidad.strip(),
                            "idiomas": edit_idiomas.strip(),
                            "tiene_coche": edit_coche,
                            "curso_prl": edit_prl,
                            "numero_ss": edit_ss.strip(),
                            "tarifa": edit_tarifa,
                            "observaciones": edit_obs.strip() if edit_obs.strip() else None
                        }
                        supabase.table("camareros").update(datos_edit).eq("id", c['id']).execute()
                        st.success("Camarero actualizado")
                        st.rerun()
                with col_del:
                    if st.form_submit_button("Eliminar", type="secondary"):
                        st.session_state.camarero_a_eliminar = c['id']
                        st.session_state.nombre_a_eliminar = f"{c['nombre']} {c['apellidos']}"
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