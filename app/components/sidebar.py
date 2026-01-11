# app/components/sidebar.py
import streamlit as st

def render_sidebar():
    with st.sidebar:
        try:
            st.image("assets/logo.png", width=180)
        except:
            st.write("Logo no encontrado")
        st.write(f"**{st.session_state.user.get('nombre', 'Admin')}**")
        st.page_link("pages/clientes.py", label="Clientes", icon="Chart")
        st.page_link("pages/eventos.py", label="Eventos", icon="Calendar")
        st.page_link("pages/camareros.py", label="Camareros", icon="People")
        st.page_link("pages/refuerzo.py", label="Refuerzo", icon="Phone")
        if st.button("Cerrar sesión"):
            del st.session_state.user
            st.rerun()