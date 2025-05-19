import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Actualizaciones TFJA y TJAJAL", layout="wide")
st.title("📄 Buscador de Actualizaciones por Fecha")
st.caption("Filtra y visualiza actualizaciones por tribunal de forma independiente")

# 📂 Cargar archivos
@st.cache_data
def cargar_tjajal():
    df = pd.read_csv("files/actualizaciones_expedientes_tjajal.csv")

    # Limpiar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("á", "a")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
        .str.replace("ñ", "n")
        .str.replace("  ", " ")
        .str.replace(" ", "_")
    )

    # Convertir fecha_acuerdo a datetime
    df["fecha_acuerdo"] = pd.to_datetime(df["fecha_acuerdo"], errors="coerce", dayfirst=True)
    return df

@st.cache_data
def cargar_tfja():
    df = pd.read_csv("files/actualizaciones_expedientes_tfja.csv")

    # Limpiar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("á", "a")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
        .str.replace("ñ", "n")
        .str.replace("  ", " ")
        .str.replace(" ", "_")
    )

    # Renombrar y convertir fecha de publicación
    if "fecha_de_publicacion" in df.columns:
        df.rename(columns={"fecha_de_publicacion": "fecha_publicacion"}, inplace=True)

    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"], errors="coerce", dayfirst=True)
    return df

df_tjajal = cargar_tjajal()
df_tfja = cargar_tfja()

# 🔍 Selector de fecha
fecha = st.date_input("Selecciona una fecha")

# 📘 TJAJAL
st.subheader("📘 TJAJAL (filtrado por fecha de acuerdo)")
tjajal_filtrado = df_tjajal[df_tjajal["fecha_acuerdo"].dt.date == fecha]

if not tjajal_filtrado.empty:
    st.dataframe(tjajal_filtrado)
else:
    st.info("No hay resultados para TJAJAL en esa fecha.")

# 📙 TFJA
st.subheader("📙 TFJA (filtrado por fecha de publicación)")
tfja_filtrado = df_tfja[df_tfja["fecha_publicacion"].dt.date == fecha]

if not tfja_filtrado.empty:
    st.dataframe(tfja_filtrado)
else:
    st.info("No hay resultados para TFJA en esa fecha.")

# 🔽 Función de exportación
def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

# ⬇️ Botones de descarga
if not tjajal_filtrado.empty:
    st.download_button(
        label="⬇️ Descargar TJAJAL",
        data=exportar_excel(tjajal_filtrado),
        file_name=f"tjajal_{fecha.strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if not tfja_filtrado.empty:
    st.download_button(
        label="⬇️ Descargar TFJA",
        data=exportar_excel(tfja_filtrado),
        file_name=f"tfja_{fecha.strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
