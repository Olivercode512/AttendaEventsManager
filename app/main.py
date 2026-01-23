import streamlit as st
from core.auth import login

# Configuración de la página
st.set_page_config(
    page_title="EventStaff Pro",
    page_icon="https://i.imgur.com/8e8Q8nB.png",
    layout="centered"
)

# Logo seguro
def mostrar_logo(ancho=280):
    try:
        st.image("assets/logo.png", width=ancho, use_container_width=False)
    except:
        st.image("https://i.imgur.com/8e8Q8nB.png", width=ancho, use_container_width=False)

# Login centrado
if "user" not in st.session_state:
    st.markdown("<div style='margin-top: 5rem;'></div>", unsafe_allow_html=True)

    with st.container():
        col_logo = st.columns([1, 2, 1])[1]
        with col_logo:
            mostrar_logo(280)

        st.markdown("<h1 style='text-align: center; margin-top: 20px;'>EventStaff Pro</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #666;'>Panel de Coordinador</h3>", unsafe_allow_html=True)

        st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", value="admin@eventstaff.pro", placeholder="admin@eventstaff.pro")
            pwd = st.text_input("Contraseña", type="password", value="1234", placeholder="Contraseña")

            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                user = login(email, pwd)
                if user:
                    st.session_state.user = user
                    st.success("¡Acceso correcto!")
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")

    st.stop()

# Sidebar
with st.sidebar:
    mostrar_logo(180)
    st.write(f"**{st.session_state.user.get('nombre', 'Coordinador')}**")
    st.divider()

    st.page_link("pages/clientes.py", label="Clientes", icon="📊")
    st.page_link("pages/eventos.py", label="Eventos", icon="📅")
    st.page_link("pages/camareros.py", label="Camareros", icon="👥")
    st.page_link("pages/refuerzo.py", label="Refuerzo Urgente", icon="📞")

    st.divider()
    if st.button("Cerrar sesión", use_container_width=True):
        del st.session_state.user
        st.rerun()

# Contenido principal
st.title("Bienvenido a EventStaff Pro")
st.success("Has iniciado sesión correctamente")
st.markdown("""
Selecciona una opción del menú lateral para empezar a gestionar:
- Crear eventos
- Asignar camareros
- Generar grupos de WhatsApp automáticos
- Buscar refuerzos urgentes
""")