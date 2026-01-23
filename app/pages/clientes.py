# pages/clientes.py
import streamlit as st
from supabase import create_client
from config.settings import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

st.title("👥 Gestión de Clientes")

# ================== AÑADIR NUEVO CLIENTE ==================
with st.expander("Añadir nuevo cliente", expanded=True):
    with st.form("nuevo_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del cliente / catering", placeholder="Boda Ana y Pedro")
            contacto = st.text_input("Persona de contacto", placeholder="Ana García")
        with col2:
            telefono = st.text_input("Teléfono", placeholder="+34 600 123 456")
            email = st.text_input("Email", placeholder="ana@example.com")

        notas = st.text_area("Notas adicionales (opcionales)", placeholder="Preferencias, alergias, comentarios...")

        if st.form_submit_button("Guardar cliente", type="primary"):
            if not nombre.strip():
                st.error("El nombre del cliente es obligatorio")
            else:
                datos = {
                    "nombre": nombre.strip(),
                    "contacto": contacto.strip() if contacto.strip() else None,
                    "telefono": telefono.strip() if telefono.strip() else None,
                    "email": email.strip() if email.strip() else None,
                    "notas": notas.strip() if notas.strip() else None
                }
                supabase.table("clientes").insert(datos).execute()
                st.success("¡Cliente añadido correctamente!")
                st.rerun()

# ================== LISTADO DE CLIENTES ==================
st.markdown("### Lista de clientes")

clientes = supabase.table("clientes").select("*").order("nombre").execute().data

if not clientes:
    st.info("Aún no hay clientes registrados.")
else:
    for cliente in clientes:
        with st.expander(f"**{cliente['nombre']}** {'👤 ' + cliente['contacto'] if cliente['contacto'] else ''}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Contacto:** {cliente.get('contacto') or '—'}")
                st.write(f"**Teléfono:** {cliente.get('telefono') or '—'}")
            with col2:
                st.write(f"**Email:** {cliente.get('email') or '—'}")

            if cliente.get('notas'):
                st.write("**Notas:**")
                st.caption(cliente['notas'])

            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️ Editar", key=f"edit_{cliente['id']}"):
                    st.session_state.editando_cliente = cliente['id']
                    st.rerun()
            with col_del:
                if st.button("🗑️ Eliminar", type="secondary", key=f"del_{cliente['id']}"):
                    st.session_state.cliente_a_eliminar = cliente['id']
                    st.session_state.nombre_cliente_eliminar = cliente['nombre']
                    st.rerun()

            # Formulario de edición
            if st.session_state.get("editando_cliente") == cliente['id']:
                with st.form(f"editar_cliente_{cliente['id']}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        nuevo_nombre = st.text_input("Nombre", value=cliente['nombre'])
                        nuevo_contacto = st.text_input("Contacto", value=cliente.get('contacto') or "")
                    with col_e2:
                        nuevo_telefono = st.text_input("Teléfono", value=cliente.get('telefono') or "")
                        nuevo_email = st.text_input("Email", value=cliente.get('email') or "")

                    nuevas_notas = st.text_area("Notas", value=cliente.get('notas') or "")

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Guardar cambios", type="primary"):
                            datos_actualizados = {
                                "nombre": nuevo_nombre.strip(),
                                "contacto": nuevo_contacto.strip() if nuevo_contacto.strip() else None,
                                "telefono": nuevo_telefono.strip() if nuevo_telefono.strip() else None,
                                "email": nuevo_email.strip() if nuevo_email.strip() else None,
                                "notas": nuevas_notas.strip() if nuevas_notas.strip() else None
                            }
                            supabase.table("clientes").update(datos_actualizados).eq("id", cliente['id']).execute()
                            del st.session_state.editando_cliente
                            st.success("Cliente actualizado")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.editando_cliente
                            st.rerun()

# ================== CONFIRMACIÓN ELIMINAR CLIENTE ==================
if st.session_state.get("cliente_a_eliminar"):
    cid = st.session_state.cliente_a_eliminar
    nombre = st.session_state.nombre_cliente_eliminar
    st.error(f"¿Eliminar permanentemente al cliente **{nombre}**?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sí, eliminar", type="primary"):
            supabase.table("clientes").delete().eq("id", cid).execute()
            del st.session_state.cliente_a_eliminar
            del st.session_state.nombre_cliente_eliminar
            st.success("Cliente eliminado")
            st.rerun()
    with c2:
        if st.button("Cancelar"):
            del st.session_state.cliente_a_eliminar
            del st.session_state.nombre_cliente_eliminar
            st.rerun()