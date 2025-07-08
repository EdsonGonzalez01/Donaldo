#!/usr/bin/env python3
"""
Orquestador que lanza los 3 scrapers y deja cada CSV
en files/actualizaciones_expedientes_<tribunal>.csv
"""

import sys, time, pathlib
from extractores.dgej   import extraer_datos as run_dgej
from extractores.tfja   import extraer_datos as run_tfja
from extractores.tjajal import extraer_datos as run_tjajal
import pandas as pd

BASE  = pathlib.Path(__file__).resolve().parent
FILES = BASE / "files"

def safely(fn, label):
    try:
        print(f"🔄 Extrayendo {label}…")
        return fn()
    except Exception as e:
        print(f"❌ {label} falló:", e, file=sys.stderr)
        raise   # deja que el workflow falle

def main() -> None:
    start = time.time()
    FILES.mkdir(exist_ok=True)

    safely(run_dgej,   "DGEJ")
    safely(run_tfja,   "TFJA")
    safely(run_tjajal, "TJAJAL")

    # Combinar en un solo CSV (opcional pero útil para Streamlit)
    csvs = FILES.glob("actualizaciones_expedientes_*.csv")
    df   = pd.concat((pd.read_csv(f) for f in csvs), ignore_index=True)
    df.to_csv(FILES / "actualizaciones_expedientes.csv", index=False)

    mins = (time.time() - start) / 60
    print(f"✅ Extracción completada en {mins:.2f} min.")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)      # hace fallar el job de Actions
