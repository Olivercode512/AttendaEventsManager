# app/components/event_card.py - Convertido a Streamlit
import streamlit as st
from config.supabase_client import supabase

def event_card(evento: dict, on_edit=None, on_delete=None):
    with st.container():
        st.write(f"**{evento['nombre']}**")
        st.write(f"Fecha: {evento['fecha']}")
        st.write(f"Hora inicio: {evento['hora_inicio']}")
        st.write(f"Hora fin: {evento['hora_fin']}")
        st.write(f"Lugar: {evento['lugar']}")

        if on_edit:
            if st.button("Editar", key=f"edit_event_{evento['id']}"):
                on_edit()

        if on_delete:
            if st.button("Eliminar", key=f"delete_event_{evento['id']}"):
                on_delete()