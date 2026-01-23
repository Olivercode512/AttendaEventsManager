# pages/camareros.py - Versión profesional y completa para Streamlit
import streamlit as st
import re
from config.supabase_client import supabase
from core.auth import require_auth

if not require_auth():
    st.switch_page("main.py")
    st.stop()

st.title("Ficha de Empleados")
st.markdown("Gestión completa de camareros: añadir, editar, eliminar y valorar.")

# ================== FORMULARIO AÑADIR NUEVO CAMARERO ==================
with st.expander("Añadir nuevo camarero", expanded=True):
    with st.form(key="nuevo_camarero_form", clear_on_submit=True):
        st.subheader("Datos personales")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo *", help="Obligatorio")
            telefono = st.text_input("Teléfono *", help="9 dígitos sin espacios")
            email = st.text_input("Email *", help="Correo válido")
        with col2:
            tarifa_hora = st.number_input("Tarifa €/h *", min_value=0.0, step=0.5, value=10.0)
            iban = st.text_input("IBAN", help="Formato ES + 22 dígitos")
            nif = st.text_input("NIF", help="8 dígitos + letra")

        st.subheader("Valoración inicial (opcional)")
        tab_punt, tab_com = st.tabs(["Puntuación", "Comentario"])
        with tab_punt:
            puntuacion = st.slider("Puntuación (1-5)", 1, 5, 3, step=1)
        with tab_com:
            comentario = st.text_area("Comentario inicial", height=100, placeholder="Notas sobre el camarero...")

        submitted = st.form_submit_button("Guardar camarero", use_container_width=True, type="primary")

    if submitted:
        errors = []
        if not nombre: errors.append("El nombre es obligatorio")
        if not telefono or not re.match(r'^\d{9}$', telefono): errors.append("Teléfono: exactamente 9 dígitos")
        if not email or not re.match(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$', email.upper()): errors.append("Email inválido")
        if tarifa_hora <= 0: errors.append("Tarifa debe ser mayor que 0")

        if errors:
            for err in errors:
                st.error(err)
        else:
            data = {
                "nombre": nombre.strip(),
                "telefono": telefono.strip(),
                "email": email.strip().lower(),
                "tarifa_hora": tarifa_hora,
                "iban": iban.strip().upper() if iban else None,
                "nif": nif.strip().upper() if nif else None,
                "puntuacion": puntuacion,
                "comentario": comentario.strip() if comentario else None
            }
            try:
                supabase.table("camareros").insert(data).execute()
                st.success(f"Camarero **{nombre}** añadido correctamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")

# ================== LISTADO DE CAMAREROS ==================
camareros = supabase.table("camareros").select("*").execute().data

if not camareros:
    st.info("No hay camareros registrados todavía.")
else:
    st.subheader(f"{len(camareros)} camareros registrados")

    for cam in camareros:
        with st.expander(f"{cam['nombre']} - {cam['tarifa_hora']} €/h"):
            col_info, col_acciones = st.columns([3, 1])

            with col_info:
                st.write(f"**Teléfono:** {cam['telefono']}")
                st.write(f"**Email:** {cam['email']}")
                st.write(f"**IBAN:** {cam.get('iban', 'No registrado')}")
                st.write(f"**NIF:** {cam.get('nif', 'No registrado')}")

                # Valoración en tabs
                st.subheader("Valoración")
                tab_p, tab_c = st.tabs(["Puntuación", "Comentario"])
                with tab_p:
                    st.metric("Puntuación actual", f"{cam.get('puntuacion', '-')}/5")
                with tab_c:
                    st.text_area("Comentario", value=cam.get('comentario', 'Sin comentario'), height=80, disabled=True)

            with col_acciones:
                # Botón eliminar con confirmación
                if st.button("Eliminar", key=f"del_{cam['id']}", type="primary", use_container_width=True):
                    st.session_state[f"confirm_delete_{cam['id']}"] = True
                    st.rerun()

                # Modal de confirmación
                if st.session_state.get(f"confirm_delete_{cam['id']}", False):
                    @st.dialog("¿Confirmar eliminación?")
                    def confirm_delete():
                        st.warning(f"¿Estás seguro de eliminar a **{cam['nombre']}**? Esta acción no se puede deshacer.")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Sí, eliminar", type="primary"):
                                supabase.table("camareros").delete().eq("id", cam['id']).execute()
                                st.success("Camarero eliminado")
                                del st.session_state[f"confirm_delete_{cam['id']}"]
                                st.rerun()
                        with col2:
                            if st.button("Cancelar"):
                                del st.session_state[f"confirm_delete_{cam['id']}"]
                                st.rerun()

                    confirm_delete()

                # Botón editar (abre formulario abajo)
                if st.button("Editar", key=f"edit_{cam['id']}", use_container_width=True):
                    st.session_state['editing_id'] = cam['id']
                    st.session_state['edit_data'] = cam
                    st.rerun()

        # ================== FORMULARIO EDICIÓN (fuera del expander) ==================
        if st.session_state.get('editing_id') == cam['id']:
            st.subheader(f"Editando: {cam['nombre']}")
            with st.form(key=f"edit_form_{cam['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_nombre = st.text_input("Nombre completo", value=cam['nombre'])
                    edit_telefono = st.text_input("Teléfono", value=cam['telefono'])
                    edit_email = st.text_input("Email", value=cam['email'])
                with col2:
                    edit_tarifa = st.number_input("Tarifa €/h", value=cam['tarifa_hora'], step=0.5)
                    edit_iban = st.text_input("IBAN", value=cam.get('iban', ''))
                    edit_nif = st.text_input("NIF", value=cam.get('nif', ''))

                st.subheader("Actualizar valoración")
                tab_p, tab_c = st.tabs(["Puntuación", "Comentario"])
                with tab_p:
                    edit_puntuacion = st.slider("Nueva puntuación", 1, 5, cam.get('puntuacion', 3))
                with tab_c:
                    edit_comentario = st.text_area("Nuevo comentario", value=cam.get('comentario', ''))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("Guardar cambios", type="primary"):
                        update_data = {
                            "nombre": edit_nombre,
                            "telefono": edit_telefono,
                            "email": edit_email,
                            "tarifa_hora": edit_tarifa,
                            "iban": edit_iban or None,
                            "nif": edit_nif or None,
                            "puntuacion": edit_puntuacion,
                            "comentario": edit_comentario or None
                        }
                        supabase.table("camareros").update(update_data).eq("id", cam['id']).execute()
                        st.success("Cambios guardados")
                        del st.session_state['editing_id']
                        del st.session_state['edit_data']
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("Cancelar"):
                        del st.session_state['editing_id']
                        del st.session_state['edit_data']
                        st.rerun()