import streamlit as st
import plotly.graph_objects as go

# Configuración general de la página en modo ancho
st.set_page_config(page_title="Dashboard Económico Mundial", layout="wide")

# Estilos CSS personalizados para simular el panel oscuro y las tarjetas
st.markdown("""
    <style>
    .stApp {
        background-color: #0b192c;
        color: white;
    }
    .metric-card {
        background-color: #1e3e62;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Barra superior con título y selector de país
col_title, col_select = st.columns([3, 1])
with col_title:
    st.markdown("### 🌐 Dashboard económico mundial")

with col_select:
    paises = ["Argentina", "Brasil", "Perú", "Chile", "Estados Unidos", "Alemania", "Japón"]
    pais_seleccionado = st.selectbox("País", paises, label_visibility="collapsed")

# Banner superior del país
st.markdown(f"""
    <div style="background-color: #1e3e62; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
        <h4 style="margin:0; color:white;">🇦🇷 {pais_seleccionado}</h4>
        <p style="margin:0; color:#9ba8b5; font-size: 14px;">Datos de referencia, valores ilustrativos</p>
    </div>
""", unsafe_allow_html=True)

# Función para generar los mini gráficos de barras (sparklines)
def crear_sparkline(valores, color="#00adb5"):
    fig = go.Figure(go.Bar(
        y=valores,
        marker_color=color,
        hoverinfo='none'
    ))
    fig.update_layout(
        height=65,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.15
    )
    return fig

# Definición de los 9 indicadores principales
indicadores = [
    {"titulo": "PBI", "valor": "US$ 640.000 M", "desc": "Trimestral, en dólares", "datos": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
    {"titulo": "Déficit fiscal / PBI", "valor": "-3,4%", "desc": "Mensual, % del PBI", "datos": [5, 6, 7, 8, 9, 10, 11, 12, 13, 15]},
    {"titulo": "Deuda pública / PBI", "valor": "78,5%", "desc": "Trimestral, % del PBI", "datos": [8, 8, 9, 9, 10, 10, 11, 11, 12, 14]},
    {"titulo": "Empleo", "valor": "6,8%", "desc": "Tasa de desempleo mensual", "datos": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6]},
    {"titulo": "Inflación", "valor": "118,2%", "desc": "Interanual, mensual", "datos": [10, 11, 12, 13, 14, 15, 16, 17, 18, 20]},
    {"titulo": "Balanza comercial", "valor": "US$ 1.850 M", "desc": "Mensual, en dólares", "datos": [5, 6, 8, 7, 9, 11, 10, 12, 14, 15]},
    {"titulo": "Riesgo país (EMBI)", "valor": "712 pb", "desc": "Diario, puntos básicos", "datos": [18, 17, 16, 15, 14, 13, 12, 10, 9, 8]},
    {"titulo": "RIN", "valor": "US$ 29.400 M", "desc": "Semanal, en dólares", "datos": [10, 10, 11, 11, 12, 12, 13, 13, 14, 15]},
    {"titulo": "Tasa de referencia", "valor": "40,0%", "desc": "Tasa de política monetaria", "datos": [20, 18, 16, 14, 12, 10, 8, 7, 6, 5]}
]

# Construcción de la cuadrícula de 3 columnas x 3 filas
for i in range(0, len(indicadores), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(indicadores):
            ind = indicadores[i + j]
            with cols[j]:
                # Tarjeta contenedora con HTML/CSS
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #9ba8b5; font-size: 13px; font-weight: 500;">{ind['titulo']}</div>
                        <div style="color: white; font-size: 24px; font-weight: bold; margin: 4px 0;">{ind['valor']}</div>
                        <div style="color: #9ba8b5; font-size: 11px; margin-bottom: 8px;">{ind['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Gráfico miniatura incrustado debajo del texto dentro de la misma columna
                fig = crear_sparkline(ind['datos'])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
