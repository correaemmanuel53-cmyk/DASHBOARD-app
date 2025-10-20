# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Tablero Demo - Planta Productiva", layout="wide")

# ---------------------------
# 1. Título y descripción
# ---------------------------
st.title("Tablero Demo — Monitorización de Planta Productiva")
st.markdown("""
Aplicación de demostración que muestra cómo crear componentes básicos en Streamlit:
título, texto, tabla, gráficos y widgets interactivos.
""")

# ---------------------------
# 2. Sidebar (controles globales)
# ---------------------------
st.sidebar.header("Filtros y Controles")

dias = st.sidebar.slider("Período (días)", min_value=1, max_value=30, value=7)
mostrar_mapa = st.sidebar.checkbox("Mostrar mapa de sensores", value=True)

variable = st.sidebar.selectbox("Variable a visualizar", ["temperatura", "vibracion", "consumo"])

# ---------------------------
# 3. Generar datos de ejemplo (simulando series temporales)
# ---------------------------
@st.cache_data(ttl=300)
def generar_datos(dias, n_sensores=5, seed=42):
    np.random.seed(seed)
    end = datetime.now()
    periods = dias * 24  # datos por hora
    idx = pd.date_range(end=end, periods=periods, freq="H")
    data = {}
    for s in range(1, n_sensores + 1):
        base_temp = 60 + 5 * s
        temp = base_temp + np.random.randn(periods).cumsum() * 0.1
        vib = np.abs(np.random.randn(periods) * (0.02 * s))
        cons = 100 + np.sin(np.linspace(0, 3.14 * dias, periods)) * 10 + np.random.randn(periods) * 2
        df_s = pd.DataFrame({
            "timestamp": idx,
            f"temp_s{s}": temp,
            f"vib_s{s}": vib,
            f"cons_s{s}": cons
        })
        data[f"s{s}"] = df_s
    combined = pd.DataFrame({"timestamp": idx})
    for s in data:
        combined = combined.join(data[s].set_index("timestamp"), on="timestamp")
    combined = combined.reset_index(drop=True)
    return combined

df = generar_datos(dias)

# ---------------------------
# 4. Mostrar tabla y estadísticas
# ---------------------------
st.subheader("Tabla de datos (muestra)")
st.dataframe(df.head(10))

st.subheader("Estadísticas resumidas")
st.write(df.describe().loc[["mean", "std", "min", "max"]])

# ---------------------------
# 5. Columnas: gráfico + controles
# ---------------------------
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("### Controles rápidos")
    st.write(f"Variable: **{variable}**")
    sensor_sel = st.selectbox("Seleccionar sensor", ["s1", "s2", "s3", "s4", "s5"])
    st.write("Sensor seleccionado:", sensor_sel)
    if st.button("Refrescar datos"):
        st.experimental_rerun()

with col1:
    st.subheader("Serie temporal")
    col_name = {
        "temperatura": f"temp_{sensor_sel}",
        "vibracion": f"vib_{sensor_sel}",
        "consumo": f"cons_{sensor_sel}"
    }[variable]

    st.line_chart(df.set_index("timestamp")[col_name])

    # ---------------------------
    # Nuevo: Bar chart con promedios diarios
    # ---------------------------
    st.subheader("Promedio diario")
    df_daily = df.copy()
    df_daily["fecha"] = df_daily["timestamp"].dt.date
    df_bar = df_daily.groupby("fecha")[col_name].mean().reset_index()

    st.bar_chart(df_bar.set_index("fecha"))

# ---------------------------
# 6. Mapa simple (coordenadas ficticias)
# ---------------------------
if mostrar_mapa:
    st.subheader("Mapa de sensores")
    lat0, lon0 = 6.2442, -75.5812  # Medellín (ejemplo)
    coords = pd.DataFrame({
        "lat": lat0 + np.random.randn(5) * 0.01,
        "lon": lon0 + np.random.randn(5) * 0.01,
        "sensor": [f"s{i}" for i in range(1, 6)]
    })
    st.map(coords.rename(columns={"lat": "lat", "lon": "lon"}))

# ---------------------------
# 7. Descarga de datos
# ---------------------------
@st.cache_data
def df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

csv = df_to_csv(df)
st.download_button("Descargar datos (.csv)", csv, file_name="datos_demo.csv", mime="text/csv")

st.markdown("---")
st.caption("Demo App de Streamlit — reemplaza los datos de ejemplo por lecturas reales desde InfluxDB para un tablero productivo.")
