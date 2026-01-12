# pages/nominas.py
import streamlit as st
from datetime import datetime
from supabase import create_client
from config.settings import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

st.title("💼 Nóminas Mensuales")

# Seleccionar mes
hoy = datetime.now()
mes_actual = hoy.strftime("%Y-%m")
mes = st.text_input("Mes (formato YYYY-MM)", value=mes_actual, help="Ejemplo: 2025-12")

if st.button("Ver nómina del mes"):
    datos = supabase.table("nominas_mensuales")\
        .select("*, camareros(nombre, apellidos, tarifa)")\
        .eq("mes", mes)\
        .execute().data

    if not datos:
        st.info(f"No hay horas cargadas en {mes}")
    else:
        filas = []
        total_mes = 0
        for d in datos:
            horas_decimal = d["horas_acumuladas"] / 4.0
            nombre = f"{d['camareros']['nombre']} {d['camareros'].get('apellidos','')}".strip()
            tarifa = d['camareros'].get('tarifa', 12.0)
            importe = round(d["importe_acumulado"], 2)
            filas.append({
                "Empleado": nombre,
                "Horas": round(horas_decimal, 2),
                "Tarifa €/h": tarifa,
                "A cobrar €": importe
            })
            total_mes += importe

        st.table(filas)
        st.markdown(f"### **Total a pagar en {mes}: {round(total_mes, 2)} €**")