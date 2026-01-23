# pages/camareros.py - Versión profesional con Streamlit: CRUD para camareros, validación, layout limpio y sin anidamiento de expanders
import streamlit as st
import re
from config.supabase_client import supabase
from config.settings import Config
import urllib.parse
from core.auth import require_auth

if not require_auth():
    st.switch_page("main.py")

st.title("Ficha de Empleados")

# ================== AÑADIR NUEVO CAMARERO ==================
with st.expander("Añadir nuevo camarero", expanded=True):
    with st.form(key="nuevo_camarero_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
        with col2:
            tarifa_hora = st.number_input("Tarifa €/h", min_value=0.0, step=0.5, value=10.0)
            iban = st.text_input("IBAN")
            nif = st.text_input("NIF")

        # Sección de valoración (sin expander anidado, usando subheader y tabs para profesionalidad)
        st.subheader("Valoración inicial (opcional)")
        tab1, tab2 = st.tabs(["Puntuación", "Comentario"])
        with tab1:
            puntuacion = st.slider("Puntuación (1-5)", min_value=1, max_value=5, value=3)
        with tab2:
            comentario = st.text_area("Comentario inicial")

        submitted = st.form_submit_button("Guardar camarero")

    if submitted:
        if not nombre:
            st.error("El nombre es obligatorio")
        elif not re.match(r'^\d{9}$', telefono):
            st.error("Teléfono debe tener 9 dígitos")
        elif not re.match(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', email.upper()):
            st.error("Email inválido")
        elif tarifa_hora <= 0:
            st.error("Tarifa debe ser positiva")
        elif not re.match(r'^[A-Z]{2}\d{20}$', iban.upper()):
            st.error("IBAN inválido (ES + 22 dígitos)")
        elif not re.match(r'^\d{8}[A-Z]$', nif.upper()):
            st.error("NIF inválido (8 dígitos + letra)")
        else:
            data = {
                "nombre": nombre,
                "telefono": telefono,
                "email": email,
                "tarifa_hora": tarifa_hora,
                "iban": iban,
                "nif": nif,
                "puntuacion": puntuacion,
                "comentario": comentario
            }
            supabase.table("camareros").insert(data).execute()
            st.success("Camarero guardado correctamente")
            st.rerun()

# ================== LISTADO DE CAMAREROS ==================
camareros = supabase.table("camareros").select("*").execute().data

if not camareros:
    st.info("No hay camareros registrados.")
else:
    for camarero in camareros:
        with st.expander(f"{camarero['nombre']} - Tarifa: {camarero['tarifa_hora']} €/h"):
            # Layout profesional con columnas
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Teléfono: {camarero['telefono']}")
                st.write(f"Email: {camarero['email']}")
                st.write(f"IBAN: {camarero['iban']}")
                st.write(f"NIF: {camarero['nif']}")
            with col2:
                # Sección de valoración (usando tabs en lugar de expander anidado)
                st.subheader("Valoración")
                tab_val, tab_com = st.tabs(["Puntuación", "Comentario"])
                with tab_val:
                    st.slider("Puntuación actual (1-5)", min_value=1, max_value=5, value=camarero.get('puntuacion', 3), disabled=True)
                with tab_com:
                    st.text_area("Comentario actual", value=camarero.get('comentario', ''), disabled=True)

            # Botones de acción
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Editar", key=f"edit_{camarero['id']}"):
                    # Lógica de edición (puedes usar st.session_state para modo edición)
                    st.session_state['editing_id'] = camarero['id']
                    st.session_state['edit_nombre'] = camarero['nombre']
                    # ... inicializa otros campos ...
                    st.rerun()  # O abre un form modal si usas extras

            with col_btn2:
                if st.button("Eliminar", key=f"delete_{camarero['id']}"):
                    supabase.table("camareros").delete().eq("id", camarero['id']).execute()
                    st.success("Camarero eliminado correctamente")
                    st.rerun()

        # Modo edición (ejemplo básico, fuera del expander para evitar nesting)
        if st.session_state.get('editing_id') == camarero['id']:
            st.subheader("Editando camarero")
            with st.form(key="edit_form"):
                edit_nombre = st.text_input("Nombre completo", value=st.session_state.get('edit_nombre', ''))
                # ... otros campos ...
                if st.form_submit_button("Guardar cambios"):
                    update_data = {"nombre": edit_nombre}  # ... añade otros ...
                    supabase.table("camareros").update(update_data).eq("id", camarero['id']).execute()
                    st.success("Cambios guardados")
                    del st.session_state['editing_id']
                    st.rerun()