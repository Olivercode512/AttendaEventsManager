# app/utils/whatsapp.py  ← VERSIÓN CORREGIDA Y FUNCIONAL
import urllib.parse

def crear_grupo_whatsapp(evento, camareros, empresa="Attenda Events"):
    """
    Genera el enlace de grupo WhatsApp y el nombre sugerido
    """
    # Construir nombre del grupo
    cliente = evento.get("catering", "Evento")
    lugar = evento.get("lugar", "Sin lugar")
    fecha = evento.get("fecha", "Sin fecha")
    hora_inicio = evento.get("hora_inicio", "?")
    hora_fin = evento.get("hora_fin", "?")

    nombre_grupo = f"{fecha} – {hora_inicio}-{hora_fin} – {cliente} – {lugar}"

    # Recoger teléfonos válidos
    telefonos = []
    for c in camareros:
        tel = c.get("telefono")
        if tel:
            tel_clean = tel.lstrip('+').replace(' ', '').replace('-', '')
            if len(tel_clean) >= 10:
                telefonos.append(tel_clean)

    if not telefonos:
        return None, nombre_grupo

    # Crear enlace de grupo
    numeros = ",".join(telefonos)
    texto = urllib.parse.quote(f"Grupo {empresa} - {nombre_grupo}")
    enlace = f"https://chat.whatsapp.com/invite?phone=&text={texto}&numbers={numeros}"

    return enlace, nombre_grupo