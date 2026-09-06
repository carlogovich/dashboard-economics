import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Dashboard Económico Mundial - FMI Real",
    layout="wide"
)

def _html(raw: str) -> str:
    return "\n".join(line.strip() for line in raw.strip().splitlines())

st.markdown(
    _html("""
    <style>
    .stApp {
        background-color: #0b192c;
        color: white;
    }
    .metric-card {
        background-color: #1e3e62;
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 0px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
    """),
    unsafe_allow_html=True
)

# ============================================================
# DICCIONARIO DE PAÍSES
# ============================================================

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

# ============================================================
# CONEXIÓN DIRECTA A LA API DEL FMI (SIN DATOS INVENTADOS)
# ============================================================

@st.cache_data
def obtener_serie_fmi(iso3, indicador_codigo):
    """
    Consulta la API REST de IFS del FMI para un país e indicador específico.
    Si la API no responde o no contiene datos, retorna estructuras vacías 
    para evitar cualquier tipo de estimación o dato fabricado.
    """
    try:
        url = f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.{iso3}.{indicador_codigo}?"
        response = requests.get(url, timeout=6)
        
        if response.status_code == 200:
            data = response.json()
            dataset = data.get('CompactData', {}).get('DataSet', {})
            series = dataset.get('Series', {})
            
            # Manejo de estructura cuando viene como lista o diccionario único
            if isinstance(series, list):
                series = series[0]
                
            obs = series.get('Obs', [])
            if not obs:
                return [], [], "Sin datos"
                
            ultimas_obs = obs[-12:]
            valores = [float(o['@OBS_VALUE']) for o in ultimas_obs]
            fechas = [o['@TIME_PERIOD'] for o in ultimas_obs]
            
            ultimo_str = f"{valores[-1]:.2f}".replace(".", ",")
            return valores, fechas, ultimo_str
        else:
            return [], [], "Error API"
    except Exception:
        return [], [], "Sin conexión"

# ============================================================
# BARRA LATERAL
# ============================================================

st.sidebar.header("Parámetros de Consulta")

region_seleccionada = st.sidebar.selectbox(
    "Selecciona una región:",
    list(paises_dict.keys())
)

paises_en_region = list(paises_dict[region_seleccionada].keys())
pais_seleccionado = st.sidebar.selectbox("Selecciona un país:", paises_en_region)

info_pais = paises_dict[region_seleccionada][pais_seleccionado]
url_bandera = f"https://flagcdn.com/w40/{info_pais['iso2']}.png"

# ============================================================
# EXTRACCIÓN DE DATOS REALES (FMI - IFS)
# Códigos estándar FMI: LUR_PT (Desempleo), PCPI_PC_CP_A_PT (Inflación IPC), etc.
# ============================================================

iso3_actual = info_pais["iso3"]

# Ejemplo con Tasa de Desempleo (FMI IFS)
valores_desempleo, fechas_desempleo, valor_desemp_str = obtener_serie_fmi(iso3_actual, "LUR_PT")

# ============================================================
# TÍTULO Y BANNER
# ============================================================

col_title, _ = st.columns([3, 1])
with col_title:
    st.markdown("### 🌐 Dashboard Económico Mundial (Datos Oficiales FMI)")

banner_html = f"""
<div style="background-color:#1e3e62; padding:5px 15px; border-radius:6px; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
    <img src="{url_bandera}" width="30" style="border-radius:12px; box-shadow:0 1px 2px rgba(0,0,0,0.2);">
    <div style="line-height:1.1;">
        <div style="margin:0; color:white; font-size:16px; font-weight:600;">
            {pais_seleccionado} <span style="font-size:18px; color:#9ba8b5;">({iso3_actual})</span>
        </div>
        <div style="margin:1px 0 0 0; color:#9ba8b5; font-size:12px;">
            Conectado a la API REST de Estadísticas Financieras Internacionales (IFS) del FMI
        </div>
    </div>
</div>
"""
st.markdown(_html(banner_html), unsafe_allow_html=True)

if not valores_desempleo:
    st.warning(f"⚠️ No se encontró la serie de desempleo en tiempo real para {pais_seleccionado} ({iso3_actual}) en los registros actuales del FMI. No se muestran datos estimados.")

# ============================================================
# FUNCIÓN DE GRÁFICOS SPARKLINE
# ============================================================

def crear_sparkline(valores, categorias=None, color_base="#00adb5"):
    if not valores:
        valores = [0]
        categorias = ["N/D"]
        
    colores = [color_base] * (len(valores) - 1) + ["white"]
    
    fig = go.Figure(
        go.Bar(
            x=categorias,
            y=valores,
            marker_color=colores,
            hoverinfo="x+y",
            hovertemplate="Período: %{x}<br>Valor: %{y}<extra></extra>"
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=5, r=5, t=0, b=12),
        xaxis=dict(visible=True, showticklabels=True, tickfont=dict(size=11, color="#9ba8b5"), tickangle=-30),
        yaxis=dict(visible=False, rangemode="tozero"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.15,
        hoverlabel=dict(bgcolor="#1e3e62", font_color="white", font_size=12)
    )
    return fig

# ============================================================
# INDICADORES CONECTADOS
# ============================================================

indicadores = [
    {
        "titulo": "Tasa de Desempleo (FMI)",
        "valor": f"{valor_desemp_str}%" if valor_desemp_str not in ["Sin datos", "Error API", "Sin conexión"] else "N/D",
        "desc": "Estadísticas Financieras Internacionales (IFS)",
        "datos": valores_desempleo,
        "cat": fechas_desempleo
    }
]

# ============================================================
# RENDERIZADO DE TARJETAS
# ============================================================

for ind in indicadores:
    card_html = f"""
    <div class="metric-card" style="max-width: 400px;">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
            <div style="color:#9ba8b5; font-size:14px; font-weight:500;">{ind["titulo"]}</div>
            <div style="color:white; font-size:16px; font-weight:bold;">{ind["valor"]}</div>
        </div>
        <div style="color:#9ba8b5; font-size:13px; margin-top:3px;">{ind["desc"]}</div>
    </div>
    """
    st.markdown(_html(card_html), unsafe_allow_html=True)
    
    fig = crear_sparkline(ind["datos"], categorias=ind["cat"])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
