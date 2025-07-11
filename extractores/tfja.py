#!/usr/bin/env python3
# extractores/tfja.py
import time
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

def extraer_datos():
    """
    Extrae las actualizaciones de expedientes del TFJA y guarda:
      - actualizaciones_expedientes_tfja.csv
      - links_no_encontrados_tfja.csv
    Devuelve un dict con estado, mensaje y tiempo.
    """
    start = time.time()
    base_dir = Path(__file__).resolve().parent.parent / "files"
    base_dir.mkdir(exist_ok=True)

    # Archivos de entrada y salida
    in_csv = base_dir / "expedientes_tfja.csv"
    out_csv = base_dir / "actualizaciones_expedientes_tfja.csv"
    failures_csv = base_dir / "links_no_encontrados_tfja.csv"

    # Leer números de expediente
    expedientes = (
        pd.read_csv(in_csv, header=None)
        .iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    resultados = []
    fallos = []

    for exp in expedientes:
        url = f"https://www.tfja.gob.mx/boletin/jurisdiccional/?expediente={exp}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            tabla = soup.select_one("div#tabNumExp table")
            if tabla is None:
                raise ValueError("Tabla TFJA no encontrada")
            df = pd.read_html(str(tabla))[0]
            df["Expediente"] = exp
            resultados.append(df)
        except Exception as e:
            fallos.append({"Expediente": exp, "URL": url, "Error": str(e)})

    # Guardar resultados
    if resultados:
        pd.concat(resultados, ignore_index=True).to_csv(out_csv, index=False, encoding="utf-8-sig")
    if fallos:
        pd.DataFrame(fallos).to_csv(failures_csv, index=False, encoding="utf-8-sig")

    elapsed = time.time() - start
    return {
        "status": "success",
        "message": f"TFJA: {out_csv.name}, fallos en {failures_csv.name}",
        "time": elapsed
    }
