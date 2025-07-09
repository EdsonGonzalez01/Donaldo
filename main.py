#!/usr/bin/env python3
"""
Lanza los tres scrapers y guarda/actualiza sus CSV en la carpeta `files/`.
Si alguno falla, el proceso sale con código 1 para que GitHub Actions marque ERROR.
"""

from pathlib import Path
import time, sys

# Importa los tres extractores
from extractores.dgej   import extraer_datos as run_dgej
from extractores.tfja   import extraer_datos as run_tfja
from extractores.tjajal import extraer_datos as run_tjajal

FILES = Path(__file__).resolve().parent / "files"
FILES.mkdir(exist_ok=True)          # por si el runner parte de directorio vacío

def run_safe(fn, etiqueta, destino):
    try:
        print(f"🔄 [{etiqueta}] empezando…")
        df = fn()                   # el scraper devuelve un DataFrame
        ruta = FILES / destino
        df.to_csv(ruta, index=False)
        print(f"✅ [{etiqueta}] {len(df):,} filas → {ruta}")
    except Exception as e:
        print(f"❌ [{etiqueta}] fallo: {e}", file=sys.stderr)
        raise                      # propaga para que el workflow falle

def main():
    start = time.time()
    run_safe(run_dgej,   "DGEJ",   "actualizaciones_expedientes_dgej.csv")
    run_safe(run_tfja,   "TFJA",   "actualizaciones_expedientes_tfja.csv")
    run_safe(run_tjajal, "TJAJAL", "actualizaciones_expedientes_tjajal.csv")
    mins = (time.time() - start) / 60
    print(f"🏁 Todo listo en {mins:.2f} min")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
