import streamlit as st
import datetime
import random
from streamlit_autorefresh import st_autorefresh

# ---- CONFIG ----
st.set_page_config(page_title="Control de Luces", layout="centered")

# ---- SIMULACIÓN DE SENSOR ----
# En una versión real, estos valores vendrían de tu Arduino/Raspberry
porcentaje_luz = 50


# ---- ESTADO DE LA APP ----
if "intensidad" not in st.session_state:
    st.session_state.intensidad = 50  # valor inicial de intensidad
if "color" not in st.session_state:
    st.session_state.color = "Blanco frío"
if "modo_automatico" not in st.session_state:
    st.session_state.modo_automatico = False
if "encendido" not in st.session_state:
    st.session_state.encendido = True

# ---- INTERFAZ ----
st.title("💡 Control de Luces Inteligentes")

# Placeholder para porcentaje de luz
st.metric("Porcentaje de luz detectada", f"{porcentaje_luz}%")

# ---- RELOJ DIGITAL EN TIEMPO REAL ----
# Auto-refresh cada 1 segundo
st_autorefresh(interval=1000, key="reloj_refresh")
hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f"<h1 style='text-align:center; font-size:60px;'>{hora_actual}</h1>", unsafe_allow_html=True)

# ---- CONTROL DE INTENSIDAD ----
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("➖") and st.session_state.encendido:
        if st.session_state.intensidad > 0:
            st.session_state.intensidad -= 10
with col3:
    if st.button("➕") and st.session_state.encendido:
        if st.session_state.intensidad < 100:
            st.session_state.intensidad += 10

with col2:
    # Mostrar ----- si está apagado, de lo contrario la intensidad
    intensidad_mostrar = f"{st.session_state.intensidad}%" if st.session_state.encendido else "-----"
    st.write(f"**Intensidad:** {intensidad_mostrar}")

# ---- BOTONES DE CONTROL ----
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("⏻"):
        st.session_state.encendido = not st.session_state.encendido
    
with col5:
    if st.button("🎨RANDOM"):
        if st.session_state.color == "Blanco frío":
            st.session_state.color = "Luz cálida"
        elif st.session_state.color == "Luz cálida":
            st.session_state.color = "Luz azul"
        else:
            st.session_state.color = "Blanco frío"

with col6:
    if st.button("AUTO"):
        st.session_state.modo_automatico = not st.session_state.modo_automatico

# ---- MOSTRAR ESTADO ----
st.subheader("Estado actual")
st.write(f"💡 **Encendido:** {'Sí' if st.session_state.encendido else 'No'}")
st.write(f"🎨 **Color actual:** {st.session_state.color}")
st.write(f"🤖 **Modo automático:** {'Activado' if st.session_state.modo_automatico else 'Desactivado'}")

# ---- BOTÓN PARA SELECCIÓN MANUAL DE COLOR ----
if st.button("🎨"):
    st.switch_page("seleccion_color")  # solo el nombre del archivo sin .py
