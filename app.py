import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Actualizaciones TFJA", layout="wide")

st.title("📄 Buscador de Actualizaciones TFJA por Fecha")
st.caption("Selecciona una fecha para ver actualizaciones de expedientes")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("actualizaciones_expedientes.csv")
    df.columns = [col.strip().replace("  ", " ") for col in df.columns]
    df["Fecha de publicación"] = pd.to_datetime(df["Fecha de publicación"], dayfirst=True, errors="coerce")
    return df

df = cargar_datos()

# Selector de fecha
fecha = st.date_input("Selecciona una fecha")
df_filtrado = df[df["Fecha de publicación"] == pd.to_datetime(fecha)]

st.markdown(f"### Resultados para: {fecha.strftime('%d-%m-%Y')} ({len(df_filtrado)} encontrados)")

# Mostrar en expanders
if df_filtrado.empty:
    st.info("No se encontraron resultados para esa fecha.")
else:
    for _, row in df_filtrado.iterrows():
        with st.expander(f"📁 {row['No. expediente']} - {row['Fecha de publicación'].date()}"):
            st.markdown(f"""
**Parte actora:** {row['Parte actora']}  
**Demandada:** {row['Parte demandada']}  
**Notificada:** {row['Parte notificada']}  
**Sala:** {row['Sala']}  
**Magistrado:** {row['Magistrado']}  
**Secretario:** {row['Secretario']}  
**Síntesis:**  {row['Síntesis']}
""")

# Opción de descarga a Excel
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

if not df_filtrado.empty:
    excel_data = convertir_a_excel(df_filtrado)
    st.download_button(
        label="⬇️ Descargar resultados en Excel",
        data=excel_data,
        file_name=f"actualizaciones_{fecha.strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
