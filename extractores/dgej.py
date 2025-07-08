import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from pathlib import Path


def extraer_datos():
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir.parent / "files" / "actualizaciones_expedientes_dgej.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    expedientes_path = script_dir.parent / "files" / "expedientes_dgej.csv"
    
    start_time = time.time()
    # Leer URLs del archivo
    df = pd.read_csv(expedientes_path, encoding='utf-8-sig')
    urls = df['URL'].dropna().tolist()

    urls = set(urls)  # Eliminar duplicados

    urls = [url.strip() for url in urls if isinstance(url, str) and url.strip()]

    base_url = "https://www.dgej.cjf.gob.mx/siseinternet/Actuaria/VerAcuerdo.aspx"

    resultados = []

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')

            tabla = soup.find('table', id='grvAcuerdos')
            if not tabla:
                print(f"⚠ No se encontró tabla en {url}")
                continue

            filas = tabla.find_all('tr')[1:]  # Saltar encabezado

            for fila in filas:
                columnas = fila.find_all('td')
                if len(columnas) < 6:
                    continue

                fecha_auto = columnas[1].get_text(strip=True)
                fecha_publicacion = columnas[3].get_text(strip=True)
                resumen = columnas[4].get_text(strip=True)

                # Extraer argumentos de la función DoVerAcuerdo(...)
                link = columnas[5].find('a')
                sintesis = ''
                num_expediente = ''
                if link and 'DoVerAcuerdo' in link.get('href', ''):
                    match = re.search(r'DoVerAcuerdo\((.*?)\)', link.get('href'))
                    if match:
                        args = [x.strip().strip('"') for x in match.group(1).split(',')]
                        if len(args) == 7:
                            url_sintesis = (
                                f"{base_url}?listaAcOrd={args[1]}&listaCatOrg={args[0]}"
                                f"&listaNeun={args[2]}&listaAsuId={args[3]}"
                                f"&listaFAuto={args[4].split()[0]}&listaFPublicacion={args[5].split()[0]}"
                                f"&listaExped={args[6]}"
                            )
                            try:
                                r_sintesis = requests.get(url_sintesis, timeout=10)
                                r_sintesis.raise_for_status()
                                s_soup = BeautifulSoup(r_sintesis.content, 'html.parser')
                                span = s_soup.find('span', id='lblAcuerdo')
                                sintesis = span.get_text(strip=True, separator="\n") if span else 'No encontrada'
                                span_expediente = s_soup.find('span', id='lblNoExp')
                                num_expediente = span_expediente.get_text(strip=True) if span_expediente else 'No encontrada'
                            except Exception as e:
                                sintesis = f'Error al cargar síntesis: {str(e)}'

                resultados.append({
                    'URL origen': url,
                    'Fecha de auto': fecha_auto,
                    'Fecha de publicación': fecha_publicacion,
                    'Número de expediente': num_expediente,
                    'Resumen': resumen,
                    'Síntesis completa': sintesis
                })

        except Exception as e:
            print(f"❌ Error al procesar {url}: {e}")
            resultados.append({
                'URL origen': url,
                'Fecha de auto': '',
                'Fecha de publicación': '',
                'Número de expediente': '',
                'Resumen': f'Error general: {str(e)}',
                'Síntesis completa': ''
            })



    # Guardar solo en CSV
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_path, index=False, encoding='utf-8-sig')

    end_time = time.time()
    elapsed_time = end_time - start_time
    return {
        'status': 'success',
        'message': f"Archivo generado: actualizaciones_expedientes_dgej.csv",
        'elapsed_time': elapsed_time
    }
