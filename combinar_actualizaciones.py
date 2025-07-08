import pandas as pd

# 1. Cargar los archivos
df_tfja = pd.read_csv("files/actualizaciones_expedientes_tfja.csv")
df_tjajal = pd.read_csv("files/actualizaciones_expedientes_tjajal.csv")

# 2. Renombrar columnas de TFJA para igualarlas con TJAJAL
df_tfja = df_tfja.rename(columns={
    'No. expediente': 'expediente',
    'Parte actora': 'actor',
    'Parte demandada': 'demandados',
    'Parte notificada': 'terceros',
    'Fecha de  publicación': 'fecha_publicacion',
    'Síntesis': 'detalle',
    'Sala': 'sala'
})

# 3. Seleccionar solo las columnas comunes
columnas_comunes = ['expediente', 'sala', 'fecha_publicacion', 'detalle', 'actor', 'demandados', 'terceros']
df_tfja = df_tfja[columnas_comunes].copy()
df_tjajal = df_tjajal[columnas_comunes].copy()

# 4. Agregar columna de origen
df_tfja['origen'] = 'TFJA'
df_tjajal['origen'] = 'TJAJAL'

# 5. Unir ambos DataFrames
df_combinado = pd.concat([df_tfja, df_tjajal], ignore_index=True)

# 6. Guardar el resultado combinado
df_combinado.to_csv("actualizaciones_combinadas.csv", index=False)

print("✅ Archivos combinados correctamente en 'actualizaciones_combinadas.csv'")
