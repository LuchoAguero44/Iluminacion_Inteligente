import streamlit as st

st.title("🎨 Selección manual de color")

# Lista de colores con su HEX
colores = {
    "Rojo": "#FF0000",
    "Verde": "#00FF00",
    "Azul": "#0000FF",
    "Amarillo": "#FFFF00",
    "Naranja": "#FFA500",
    "Rosa": "#FFC0CB",
    "Morado": "#800080",
    "Cian": "#00FFFF",
    "Blanco": "#FFFFFF",
    "Negro": "#000000",
    "Gris": "#808080",
    "Lima": "#00FF7F",
    "Violeta": "#8A2BE2",
    "Turquesa": "#40E0D0",
    "Marrón": "#A52A2A"
}

st.write("Selecciona un color:")

# Mostrar colores en filas de 5 columnas
cols = st.columns(5)
i = 0
for nombre, hex_code in colores.items():
    with cols[i % 5]:
        if st.button(f"{nombre}\n{hex_code}", key=hex_code, help=hex_code):
            st.session_state.color = hex_code
            st.success(f"Color cambiado a {nombre} ({hex_code})")
    i += 1

# También permitimos elegir un color libre
st.write("---")
color_libre = st.color_picker("O elige cualquier color:", "#ffffff")
if st.button("Aplicar color libre"):
    st.session_state.color = color_libre
    st.success(f"Color cambiado a {color_libre}")
