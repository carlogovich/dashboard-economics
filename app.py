# Banner superior con imagen de la bandera
st.markdown(f"""
    <div style="
        background-color: #1e3e62;
        padding: 5px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <img src="{url_bandera}" width="20" style="
            border-radius: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        ">
        <div style="line-height: 1.1;">
            <div style="
                margin: 0;
                color: white;
                font-size: 12px;
                font-weight: 600;
            ">
                {pais_seleccionado}
                <span style="
                    font-size: 9px;
                    color: #9ba8b5;
                ">({info_pais['iso3'].upper()})</span>
            </div>
            <div style="
                margin: 1px 0 0 0;
                color: #9ba8b5;
                font-size: 8px;
            ">
                Datos conectados a FRED y referencias ilustrativas
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)
