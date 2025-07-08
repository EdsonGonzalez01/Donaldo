import pandas as pd
import requests
from bs4 import BeautifulSoup

# Leer URLs desde el Excel
df = pd.read_excel('files/urls.xlsx', sheet_name='Hoja1')
urls = df['URL'].dropna().tolist()

# Lista de resultados
resultados = []

for url in urls:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar la tabla de acuerdos
        tabla = soup.find('table', id='grvAcuerdos')
        if not tabla:
            resultados.append({'URL': url, 'Último resumen': 'Tabla no encontrada'})
            continue

        filas = tabla.find_all('tr')[1:]  # Omitir encabezado
        if not filas:
            resultados.append({'URL': url, 'Último resumen': 'Sin filas'})
            continue

        # Tomar la última fila (último acuerdo)
        ultima_fila = filas[-1]
        columnas = ultima_fila.find_all('td')

        if len(columnas) >= 5:
            resumen = columnas[4].get_text(strip=True)
        else:
            resumen = 'Columna de resumen no encontrada'

        resultados.append({'URL': url, 'Último resumen': resumen})

    except Exception as e:
        resultados.append({'URL': url, 'Último resumen': f'Error: {str(e)}'})

# Guardar resultados
df_resultados = pd.DataFrame(resultados)
df_resultados.to_excel('files/ultimo_resumen_por_url.xlsx', index=False)

print("Resumen más reciente extraído. Guardado en 'files/ultimo_resumen_por_url.xlsx'")
