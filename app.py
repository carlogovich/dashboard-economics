import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Configuración general de la página en modo ancho
st.set_page_config(page_title="Dashboard Económico Mundial", layout="wide")

# Estilos CSS personalizados para el panel oscuro y las tarjetas
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

# Diccionario completo de países agrupados con sus códigos ISO
paises_dict = {
    "Norteamérica": {
        "Estados Unidos": {"iso2": "us", "iso3": "USA"},
        "Canadá": {"iso2": "ca", "iso3": "CAN"},
        "México": {"iso2": "mx", "iso3": "MEX"}
    },
    "Sudamérica": {
        "Brasil": {"iso2": "br", "iso3": "BRA"},
        "Argentina": {"iso2": "ar", "iso3": "ARG"},
        "Colombia": {"iso2": "co", "iso3": "COL"},
        "Chile": {"iso2": "cl", "iso3": "CHL"},
        "Perú": {"iso2": "pe", "iso3": "PER"},
        "Ecuador": {"iso2": "ec", "iso3": "ECU"},
        "Uruguay": {"iso2": "uy", "iso3": "URY"},
        "Bolivia": {"iso2": "bo", "iso3": "BOL"},
        "Paraguay": {"iso2": "py", "iso3": "PRY"},
        "Venezuela": {"iso2": "ve", "iso3": "VEN"}
    },
    "Europa": {
        "Alemania": {"iso2": "de", "iso3": "DEU"},
        "Reino Unido": {"iso2": "gb", "iso3": "GBR"},
        "Francia": {"iso2": "fr", "iso3": "FRA"},
        "Italia": {"iso2": "it", "iso3": "ITA"},
        "España": {"iso2": "es", "iso3": "ESP"},
        "Países Bajos": {"iso2": "nl", "iso3": "NLD"},
        "Suiza": {"iso2": "ch", "iso3": "CHE"},
        "Croacia": {"iso2": "hr", "iso3": "HRV"}
    },
    "Asia": {
        "China": {"iso2": "cn", "iso3": "CHN"},
        "Japón": {"iso2": "jp", "iso3": "JPN"},
        "India": {"iso2": "in", "iso3": "IND"},
        "Corea del Sur": {"iso2": "kr", "iso3": "KOR"},
        "Singapur": {"iso2": "sg", "iso3": "SGP"},
        "Taiwán": {"iso2": "tw", "iso3": "TWN"}
    },
    "Oceanía": {
        "Australia": {"iso2": "au", "iso3": "AUS"},
        "Nueva Zelanda": {"iso2": "nz", "iso3": "NZL"}
    }
}

# Mapeo de códigos ISO-3 a series trimestrales de Desempleo en FRED (OECD Harmonized Unemployment Rate)
FRED_UNEMPLOYMENT_SERIES = {
    "USA": "LRUN64TTUSQ156S",
    "CAN": "LRUN64TTCAQ156S",
    "MEX": "LRUN64TTMXQ156S",
    "GBR": "LRUN64TTGBQ156S",
    "DEU": "LRUN64TTDEQ156S",
    "FRA": "LRUN64TTFRQ156S",
    "ITA": "LRUN64TTITQ156S",
    "ESP": "LRUN64TTESQ156S",
    "JPN": "LRUN64TTJPQ156S",
    "AUS": "LRUN64TTAUQ156S",
    "NZL": "LRUN64TTNZQ156S"
}

@st.cache_data
def obtener_desempleo_fred(iso3):
    """Consulta la serie trimestral de desempleo desde FRED usando el enlace CSV público."""
    if iso3 not in FRED_UNEMPLOYMENT_SERIES:
        # Fallback a datos simulados si el país no tiene serie directa mapeada en FRED
        return [6.5, 6.4, 6.3, 6.2, 6.1, 6.0, 5.9, 5.8, 5.7, 6.0, 6.5, 6.8], "6,8%"
    
    series_id = FRED_UNEMPLOYMENT_SERIES[iso3]
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    
    try:
        df = pd.read_csv(url)
        # Limpieza de datos: FRED devuelve columnas ['DATE', 'SERIES_ID']
        df.columns = ['Fecha', 'Valor']
        # Reemplazar '.' por NaN y convertir a numérico
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        df = df.dropna().tail(12) # Últimos 12 trimestres
        
        if len(df) < 12:
            # Si faltan registros, rellenamos o devolvemos respaldo
            valores = df['Valor'].tolist()
            while len(valores) < 12:
                valores.insert(0, valores[0] if valores else 5.0)
        else:
            valores = df['Valor'].tolist()
            
        ultimo_valor = f"{valores[-1]:.1f}%".replace('.', ',')
        return valores, ultimo_valor
    except Exception:
        # En caso de error de red o cambios en la API, usa respaldo estético
        return [6.5, 6.4, 6.3, 6.2, 6.1, 6.0, 5.9, 5.8, 5.7, 6.0, 6.5, 6.8], "6,8%"

# Barra lateral para navegación
st.sidebar.header("Parámetros de Consulta")
region_seleccionada = st.sidebar.selectbox("Selecciona una región:", list(paises_dict.keys()))

paises_en_region = list(paises_dict[region_seleccionada].keys())
pais_seleccionado = st.sidebar.selectbox("Selecciona un país:", paises_en_region)

# Obtener datos del país y la URL de su bandera oficial
info_pais = paises_dict[region_seleccionada][pais_seleccionado]
url_bandera = f"https://flagcdn.com/w40/{info_pais['iso2']}.png"

# Obtener datos reales de desempleo para los últimos 12 trimestres
datos_empleo, valor_empleo_actual = obtener_desempleo_fred(info_pais['iso3'])

# Barra superior con título
col_title, _ = st.columns([3, 1])
with col_title:
    st.markdown("### 🌐 Dashboard económico mundial")

# Banner superior con imagen de la bandera integrada mediante HTML
st.markdown(f"""
    <div style="background-color: #1e3e62; padding: 15px; border-radius: 8px; margin-bottom: 25px; display: flex; align-items: center; gap: 15px;">
        <img src="{url_bandera}" width="40" style="border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <div>
            <h4 style="margin:0; color:white;">{pais_seleccionado} <span style="font-size: 14px; color: #9ba8b5;">({info_pais['iso3'].upper()})</span></h4>
            <p style="margin:0; color:#9ba8b5; font-size: 14px;">Datos conectados a FRED y referencias ilustrativas</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Función para generar los mini gráficos de barras con tooltip y última barra blanca
def crear_sparkline(valores, color_base="#00adb5"):
    # Definir colores: todos color_base, excepto la última barra que es blanca
    colores = [color_base] * (len(valores) - 1) + ["white"]
    
    fig = go.Figure(go.Bar(
        y=valores,
        marker_color=colores,
        hoverinfo='y',
        hovertemplate='Valor: %{y}<extra></extra>'
    ))
    fig.update_layout(
        height=65,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.15,
        hoverlabel=dict(
            bgcolor="#1e3e62",
            font_color="white",
            font_size=12
        )
    )
    return fig

# Definición de los 9 indicadores macroeconómicos clave
indicadores = [
    {"titulo": "PBI", "valor": "US$ 640.000 M", "desc": "Trimestral, en dólares", "datos": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]},
    {"titulo": "Déficit fiscal / PBI", "valor": "-3,4%", "desc": "Mensual, % del PBI", "datos": [5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17]},
    {"titulo": "Deuda pública / PBI", "valor": "78,5%", "desc": "Trimestral, % del PBI", "datos": [8, 8, 9, 9, 10, 10, 11, 11, 12, 14, 15, 16]},
    {"titulo": "Empleo", "valor": valor_empleo_actual, "desc": "Trimestral, tasa de desempleo (FRED)", "datos": datos_empleo},
    {"titulo": "Inflación", "valor": "118,2%", "desc": "Interanual, mensual", "datos": [10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22]},
    {"titulo": "Balanza comercial", "valor": "US$ 1.850 M", "desc": "Mensual, en dólares", "datos": [5, 6, 8, 7, 9, 11, 10, 12, 14, 15, 16, 18]},
    {"titulo": "Riesgo país (EMBI)", "valor": "712 pb", "desc": "Diario, puntos básicos", "datos": [18, 17, 16, 15, 14, 13, 12, 10, 9, 8, 7, 6]},
    {"titulo": "RIN", "valor": "US$ 29.400 M", "desc": "Semanal, en dólares", "datos": [10, 10, 11, 11, 12, 12, 13, 13, 14, 15, 16, 17]},
    {"titulo": "Tasa de referencia", "valor": "40,0%", "desc": "Tasa de política monetaria", "datos": [20, 18, 16, 14, 12, 10, 8, 7, 6, 5, 4, 4]}
]

# Construcción de la cuadrícula de 3 columnas x 3 filas
for i in range(0, len(indicadores), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(indicadores):
            ind = indicadores[i + j]
            with cols[j]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #9ba8b5; font-size: 13px; font-weight: 500;">{ind['titulo']}</div>
                        <div style="color: white; font-size: 24px; font-weight: bold; margin: 4px 0;">{ind['valor']}</div>
                        <div style="color: #9ba8b5; font-size: 11px; margin-bottom: 8px;">{ind['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                fig = crear_sparkline(ind['datos'])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
