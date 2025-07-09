#!/usr/bin/env python3
from pathlib import Path
import time, sys

from extractores.dgej   import extraer_datos as run_dgej
from extractores.tfja   import extraer_datos as run_tfja
from extractores.tjajal import extraer_datos as run_tjajal

FILES = Path(__file__).resolve().parent / "files"
FILES.mkdir(exist_ok=True)

def run_safe(fn, label):
    try:
        inicio = time.time()
        print(f"🔄 [{label}] empezando…")
        fn()                                   # el scraper escribe su CSV
        seg = time.time() - inicio
        print(f"✅ [{label}] listo en {seg:.1f}s")
    except Exception as e:
        print(f"❌ [{label}] fallo: {e}", file=sys.stderr)
        raise

def main():
    start = time.time()
    run_safe(run_dgej,   "DGEJ")
    run_safe(run_tfja,   "TFJA")
    run_safe(run_tjajal, "TJAJAL")
    print(f"🏁 Todo terminó en {(time.time()-start)/60:.2f} min")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
