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

# Fecha final (hoy) y rango de días
dias = st.sidebar.slider("Período (días)", min_value=1, max_value=30, value=7)
mostrar_mapa = st.sidebar.checkbox("Mostrar mapa de sensores", value=True)

# Selección de variable a graficar
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
        # distintas medias por sensor
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
    # crear DataFrame agregado (ejemplo simple)
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
st.write(df.describe().loc[["mean","std","min","max"]])

# ---------------------------
# 5. Columnas: gráfico + controles
# ---------------------------
col1, col2 = st.columns([3,1])

with col2:
    st.markdown("### Controles rápidos")
    st.write(f"Variable: **{variable}**")
    sensor_sel = st.selectbox("Seleccionar sensor", ["s1","s2","s3","s4","s5"])
    st.write("Sensor seleccionado:", sensor_sel)
    if st.button("Refrescar datos"):
        # simple efecto visual, la función cache_data evita recálculo salvo que cambien inputs
        st.experimental_rerun()

with col1:
    st.subheader("Serie temporal")
    # Elegir columna según variable y sensor
    col_name = {
        "temperatura": f"temp_{sensor_sel}",
        "vibracion": f"vib_{sensor_sel}",
        "consumo": f"cons_{sensor_sel}"
    }[variable]
    # como en el ejemplo usamos sufijo sX sin guion, adaptamos
    # corregir nombre real:
    col_name = col_name.replace("_s","_s")
    # si no existe la columna, intentar con notación del ejemplo
    # (en nuestros datos columnas son temp_s1, vib_s1, cons_s1)
    st.line_chart(df.set_index("timestamp")[col_name])

# ---------------------------
# 6. Mapa simple (coordenadas ficticias)
# ---------------------------
if mostrar_mapa:
    st.subheader("Mapa de sensores")
    # generar 5 coordenadas alrededor de una ubicación
    lat0, lon0 = 6.2442, -75.5812  # Medellín (ejemplo)
    coords = pd.DataFrame({
        "lat": lat0 + np.random.randn(5) * 0.01,
        "lon": lon0 + np.random.randn(5) * 0.01,
        "sensor": [f"s{i}" for i in range(1,6)]
    })
    st.map(coords.rename(columns={"lat":"lat", "lon":"lon"}))

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
