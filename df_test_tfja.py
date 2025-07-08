import pandas as pd 

# Concatenar resultados
df_final = pd.concat(todos_df, ignore_index=True)

# Guardar en CSV
df_final.to_csv("actualizaciones_expedientes.csv", index=False, encoding="utf-8-sig")
print("✅ Archivo generado: actualizaciones_expedientes.csv")

# Ejemplo de filtrado por fecha (opcional)
fecha_filtro = "02-05-2025"  # Cambia aquí la fecha deseada
df_filtrado = df_final[df_final["Fecha de publicación"] == fecha_filtro]

# Mostrar resultados filtrados
print(f"\n📆 Resultados para la fecha {fecha_filtro}:")
print(df_filtrado)