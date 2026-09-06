import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Dashboard Económico Mundial",
    layout="wide"
)

# ============================================================
# HELPER: aplanar bloques de HTML
# ------------------------------------------------------------
# Streamlit interpreta 4+ espacios de indentación al inicio de
# una línea como "bloque de código" (regla clásica de Markdown),
# así que cualquier HTML multilínea con sangría se muestra como
# texto crudo en vez de renderizarse. Esta función quita la
# indentación de cada línea antes de pasarla a st.markdown.
# ============================================================

def _html(raw: str) -> str:
    return "\n".join(line.strip() for line in raw.strip().splitlines())


# ============================================================
# ESTILOS CSS
# ============================================================

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
# SERIES DE DESEMPLEO EN FRED
# ============================================================

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
    "NZL": "LRUN64TTNZQ156S",
    "CHE": "LRUN64TTCHQ156S",
    "HRV": "LRUN64TTHRQ156S",
    "KOR": "LRUN64TTKRQ156S"
}


# ============================================================
# OBTENER DESEMPLEO DESDE FRED
# ============================================================

@st.cache_data
def obtener_desempleo_fred(iso3):

    if iso3 not in FRED_UNEMPLOYMENT_SERIES:

        fechas_simuladas = []

        for anio in range(2023, 2026):
            for q in range(1, 5):
                fechas_simuladas.append(f"{anio}.Q{q}")

        fechas_simuladas = fechas_simuladas[-12:]

        base_val = 6.8

        if iso3 == "ARG":
            base_val = 7.5
        elif iso3 == "BRA":
            base_val = 8.2
        elif iso3 == "COL":
            base_val = 10.5
        elif iso3 == "CHL":
            base_val = 8.5
        elif iso3 == "PER":
            base_val = 6.5

        valores_simulados = [
            round(
                base_val + (i * 0.05 if i % 2 == 0 else -0.05),
                1
            )
            for i in range(12)
        ]

        ultimo_str = f"{valores_simulados[-1]:.1f}%".replace(".", ",")

        return (
            valores_simulados,
            fechas_simuladas,
            ultimo_str
        )

    series_id = FRED_UNEMPLOYMENT_SERIES[iso3]

    url = (
        f"https://fred.stlouisfed.org/graph/"
        f"fredgraph.csv?id={series_id}"
    )

    try:

        df = pd.read_csv(url)

        df.columns = ["Fecha", "Valor"]

        df["Valor"] = pd.to_numeric(
            df["Valor"],
            errors="coerce"
        )

        df = df.dropna().tail(12)

        if len(df) < 12:

            fechas_simuladas = [
                f"2024.Q{((i % 4) + 1)}"
                for i in range(12)
            ]

            valores = [6.0] * 12

            return (
                valores,
                fechas_simuladas,
                "6,0%"
            )

        valores = df["Valor"].tolist()

        fechas_dt = pd.to_datetime(df["Fecha"])

        fechas = [
            f"{dt.year}.Q{dt.quarter}"
            for dt in fechas_dt
        ]

        ultimo_valor = f"{valores[-1]:.1f}%".replace(".", ",")

        return (
            valores,
            fechas,
            ultimo_valor
        )

    except Exception:

        fechas_fallback = [
            f"2024.Q{((i % 4) + 1)}"
            for i in range(12)
        ]

        valores_fallback = [
            6.5, 6.4, 6.3, 6.2,
            6.1, 6.0, 5.9, 5.8,
            5.7, 6.0, 6.5, 6.8
        ]

        return (
            valores_fallback,
            fechas_fallback,
            "6,8%"
        )


# ============================================================
# BARRA LATERAL
# ============================================================

st.sidebar.header("Parámetros de Consulta")

region_seleccionada = st.sidebar.selectbox(
    "Selecciona una región:",
    list(paises_dict.keys())
)

paises_en_region = list(
    paises_dict[region_seleccionada].keys()
)

pais_seleccionado = st.sidebar.selectbox(
    "Selecciona un país:",
    paises_en_region
)

info_pais = paises_dict[
    region_seleccionada
][pais_seleccionado]

url_bandera = (
    f"https://flagcdn.com/w40/"
    f"{info_pais['iso2']}.png"
)


# ============================================================
# DATOS DE DESEMPLEO
# ============================================================

datos_empleo, fechas_empleo, valor_empleo_actual = (
    obtener_desempleo_fred(
        info_pais["iso3"]
    )
)


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

col_title, _ = st.columns([3, 1])

with col_title:
    st.markdown("### 🌐 Dashboard económico mundial")


# ============================================================
# BANNER DEL PAÍS
# ============================================================

banner_html = f"""
<div style="background-color:#1e3e62; padding:5px 15px; border-radius:6px; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
    <img src="{url_bandera}" width="30" style="border-radius:12px; box-shadow:0 1px 2px rgba(0,0,0,0.2);">
    <div style="line-height:1.1;">
        <div style="margin:0; color:white; font-size:16px; font-weight:600;">
            {pais_seleccionado}
            <span style="font-size:18px; color:#9ba8b5;">({info_pais["iso3"].upper()})</span>
        </div>
        <div style="margin:1px 0 0 0; color:#9ba8b5; font-size:12px;">
            Datos conectados a FRED y referencias ilustrativas
        </div>
    </div>
</div>
"""

st.markdown(_html(banner_html), unsafe_allow_html=True)


# ============================================================
# FUNCIÓN PARA CREAR LOS GRÁFICOS
# ALTURA = 140 PX
# ============================================================

def crear_sparkline(
    valores,
    categorias=None,
    color_base="#00adb5"
):

    colores = (
        [color_base] * (len(valores) - 1)
        + ["white"]
    )

    fig = go.Figure(
        go.Bar(
            x=categorias,
            y=valores,
            marker_color=colores,
            hoverinfo="x+y",
            hovertemplate=(
                "Período: %{x}"
                "<br>Valor: %{y}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(

        height=140,

        margin=dict(
            l=5,
            r=5,
            t=0,
            b=12
        ),

        xaxis=dict(
            visible=True,
            showticklabels=True,
            tickfont=dict(
                size=8,
                color="#9ba8b5"
            ),
            tickangle=0
        ),

        yaxis=dict(
            visible=False,
            rangemode="tozero"
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        bargap=0.15,

        hoverlabel=dict(
            bgcolor="#1e3e62",
            font_color="white",
            font_size=12
        )
    )

    return fig


# ============================================================
# INDICADORES MACROECONÓMICOS
# ============================================================

indicadores = [

    {
        "titulo": "PBI",
        "valor": "US$ 640.000 M",
        "desc": "Trimestral, en dólares",
        "datos": [
            10, 11, 12, 13,
            14, 15, 16, 17,
            18, 19, 20, 21
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Déficit fiscal / PBI",
        "valor": "-3,4%",
        "desc": "Mensual, % del PBI",
        "datos": [
            5, 6, 7, 8,
            9, 10, 11, 12,
            13, 15, 16, 17
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Deuda pública / PBI",
        "valor": "78,5%",
        "desc": "Trimestral, % del PBI",
        "datos": [
            8, 8, 9, 9,
            10, 10, 11, 11,
            12, 14, 15, 16
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Tasa de desempleo",
        "valor": valor_empleo_actual,
        "desc": "Trimestral, tasa de desempleo",
        "datos": datos_empleo,
        "cat": fechas_empleo
    },

    {
        "titulo": "Inflación",
        "valor": "118,2%",
        "desc": "Interanual, mensual",
        "datos": [
            10, 11, 12, 13,
            14, 15, 16, 17,
            18, 20, 21, 22
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Balanza comercial",
        "valor": "US$ 1.850 M",
        "desc": "Mensual, en dólares",
        "datos": [
            5, 6, 8, 7,
            9, 11, 10, 12,
            14, 15, 16, 18
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Riesgo país (EMBI)",
        "valor": "712 pb",
        "desc": "Diario, puntos básicos",
        "datos": [
            18, 17, 16, 15,
            14, 13, 12, 10,
            9, 8, 7, 6
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "RIN",
        "valor": "US$ 29.400 M",
        "desc": "Semanal, en dólares",
        "datos": [
            10, 10, 11, 11,
            12, 12, 13, 13,
            14, 15, 16, 17
        ],
        "cat": fechas_empleo
    },

    {
        "titulo": "Tasa de referencia",
        "valor": "40,0%",
        "desc": "Tasa de política monetaria",
        "datos": [
            20, 18, 16, 14,
            12, 10, 8, 7,
            6, 5, 4, 4
        ],
        "cat": fechas_empleo
    }
]


# ============================================================
# CUADRÍCULA 3 × 3
# ============================================================

for i in range(0, len(indicadores), 3):

    cols = st.columns(3)

    for j in range(3):

        if i + j < len(indicadores):

            ind = indicadores[i + j]

            with cols[j]:

                # ====================================================
                # TARJETA DEL INDICADOR
                #
                # FILA 1: TÍTULO + VALOR
                # FILA 2: DESCRIPCIÓN
                # ====================================================

                card_html = f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; white-space:nowrap;">
                        <div style="color:#9ba8b5; font-size:11px; font-weight:500; overflow:hidden; text-overflow:ellipsis;">
                            {ind["titulo"]}
                        </div>
                        <div style="color:white; font-size:16px; font-weight:bold; line-height:1;">
                            {ind["valor"]}
                        </div>
                    </div>
                    <div style="color:#9ba8b5; font-size:9px; margin-top:3px;">
                        {ind["desc"]}
                    </div>
                </div>
                """

                st.markdown(_html(card_html), unsafe_allow_html=True)

                # ====================================================
                # GRÁFICO
                # ALTURA = 140 PX
                # ====================================================

                fig = crear_sparkline(
                    ind["datos"],
                    categorias=ind["cat"]
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )
