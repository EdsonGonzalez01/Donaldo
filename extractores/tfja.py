# generar_actualizaciones.py

from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
import io 


def extraer_datos():
    start_time = time.time()
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir.parent / "files" / "actualizaciones_expedientes_tfja.csv"
    expedientes_path = script_dir.parent / "files" / "expedientes_tfja.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Leer expedientes desde CSV
    expedientes = pd.read_csv(expedientes_path).iloc[:, 0].tolist()

    expedientes = [exp.strip() for exp in expedientes if isinstance(exp, str) and exp.strip()]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    def obtener_tabla_expediente(expediente):
        try:
            driver.get("https://www.tfja.gob.mx/boletin/jurisdiccional/")
            time.sleep(2)

            input_box = driver.find_element(By.ID, "IdnumeroExp")
            input_box.clear()
            input_box.send_keys(expediente)

            boton = driver.find_element(By.ID, "btnExpediente")
            driver.execute_script("arguments[0].click();", boton)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tabla = soup.find("div", {"id": "tabNumExp"}).find("table")
            df = pd.read_html(io.StringIO(str(tabla)))[0]
            df["Expediente"] = expediente
            return df

        except Exception as e:
            print(f"❌ Error con expediente {expediente}: {e}")
            return pd.DataFrame()

    todos_df = []
    for exp in expedientes:
        # print(f"🔎 Consultando expediente: {exp}")
        df_exp = obtener_tabla_expediente(exp)
        if not df_exp.empty:
            todos_df.append(df_exp)

    driver.quit()

    df_final = pd.concat(todos_df, ignore_index=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')

    end_time = time.time()
    elapsed_time = end_time - start_time
    return {
        'status': 'success',
        'message': f"Archivo generado: actualizaciones_expedientes_tfja.csv",
        'elapsed_time': elapsed_time
    }
