# components/header.py - Convertido a Streamlit
import streamlit as st
from core.auth import logout

def render_header(show_logout=True, title="EventStaff Pro"):
    st.header(title)
    if show_logout:
        if st.button('Cerrar sesión'):
            logout()
            st.rerun()