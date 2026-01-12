import os
st.title("¡APP INICIADA! Prueba de debug")
st.write("Si ves esto, la app arrancó correctamente. El problema está después.")
st.balloons()
os.system("streamlit run app/main.py --server.port 8502")