# analizar_actualizaciones.py

import pandas as pd

# Leer archivo generado
df = pd.read_csv("actualizaciones_expedientes.csv")

# Normalizar nombres de columnas
df.columns = [col.strip().replace("  ", " ") for col in df.columns]

# Filtro por fecha
fecha_filtro = "29-04-2025"  # Puedes cambiar esta fecha
df_filtrado = df[df["Fecha de publicación"] == fecha_filtro]

# Mostrar resultados
print(f"\n📅 Resultados para la fecha {fecha_filtro}:")
print(df_filtrado)

# Guardar filtro si se desea
df_filtrado.to_csv(f"actualizaciones_{fecha_filtro}.csv", index=False, encoding="utf-8-sig")
