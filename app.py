import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO

st.set_page_config(page_title="Actualizaciones TFJA, TJAJAL y DGEJ",
                   page_icon="📄",
                   layout="wide")

st.title("📄 Buscador de Actualizaciones por Fecha")
st.caption("Filtra y visualiza actualizaciones por tribunal de forma independiente")

FILES = Path(__file__).parent / "files"

# -------------- utilidades -----------------
def limpiar_columnas(col):
    return (col.str.strip()
               .str.lower()
               .str.normalize("NFKD")
               .str.encode("ascii", "ignore")
               .str.decode()
               .str.replace("  ", " ")
               .str.replace(" ", "_"))

def exportar_excel(df):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return out.getvalue()

# -------------- loaders -----------------
@st.cache_data(ttl=600)                         # refresca cada 10 min
def cargar_csv(nombre, fecha_col, encoding="utf-8"):
    df = pd.read_csv(FILES / nombre, encoding=encoding)
    df.columns = limpiar_columnas(df.columns)

    # Renombrar columna de fecha si es necesaria
    if fecha_col not in df.columns and "fecha_de_publicacion" in df.columns:
        df.rename(columns={"fecha_de_publicacion": fecha_col}, inplace=True)

    df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce", dayfirst=True)
    return df

df_tjajal = cargar_csv("actualizaciones_expedientes_tjajal.csv",
                       fecha_col="fecha_acuerdo")
df_tfja   = cargar_csv("actualizaciones_expedientes_tfja.csv",
                       fecha_col="fecha_publicacion")
df_dgej   = cargar_csv("actualizaciones_expedientes_dgej.csv",
                       fecha_col="fecha_publicacion", encoding="utf-8-sig")

# -------------- filtros -----------------
st.sidebar.header("🔍 Filtro de fecha")
fecha = st.sidebar.date_input("Selecciona una fecha", value=pd.Timestamp.today())

# botón para vaciar caché si hace falta ver lo último sin esperar TTL
if st.sidebar.button("🔄 Recargar datos ahora"):
    st.cache_data.clear()
    st.experimental_rerun()

# -------------- vistas -----------------
def seccion(titulo, df, col_fecha, slug):
    st.subheader(titulo)
    filtrado = df[df[col_fecha].dt.date == fecha]
    if filtrado.empty:
        st.info("Sin resultados para esa fecha.")
    else:
        st.dataframe(filtrado, use_container_width=True)
        st.download_button(
            label="⬇️ Descargar",
            data=exportar_excel(filtrado),
            file_name=f"{slug}_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

seccion("📘 TJAJAL (fecha de acuerdo)", df_tjajal, "fecha_acuerdo", "tjajal")
seccion("📙 TFJA  (fecha de publicación)", df_tfja, "fecha_publicacion", "tfja")
seccion("📕 DGEJ  (fecha de publicación)", df_dgej, "fecha_publicacion", "dgej")
