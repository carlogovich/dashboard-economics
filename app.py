import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general de la página
st.set_page_config(page_title="Dashboard Económico Global", layout="wide")

st.title("🌐 Dashboard Económico Global")
st.markdown("Bienvenido a tu panel de control macroeconómico. Aquí consultaremos y visualizaremos los principales indicadores de los países.")

# Panel lateral (Sidebar) para controles
st.sidebar.header("Parámetros de Consulta")
pais = st.sidebar.selectbox(
    "Selecciona un país:",
    ["Perú", "Estados Unidos", "Brasil", "Chile", "Alemania", "Japón"]
)

indicador = st.sidebar.selectbox(
    "Selecciona el indicador:",
    ["PIB (USD)", "Inflación (%)", "Desempleo (%)"]
)

st.sidebar.markdown("---")
if st.sidebar.button("Cargar Datos"):
    st.success(f"Cargando datos para {pais} - {indicador}...")
else:
    st.info("Selecciona los parámetros en la barra lateral y presiona 'Cargar Datos'.")

# Sección principal con datos de prueba estáticos mientras conectamos la API
st.subheader(f"Evolución histórica: {indicador} en {pais}")

# Creamos un gráfico de ejemplo rápido con Plotly
df_demo = pd.DataFrame({
    "Año": [2021, 2022, 2023, 2024, 2025],
    "Valor": [100, 105, 112, 118, 125]
})

fig = px.line(df_demo, x="Año", y="Valor", markers=True, title=f"Tendencia de {indicador}")
st.plotly_chart(fig, use_container_width=True)
