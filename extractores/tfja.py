# generar_actualizaciones.py

from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

            wait = WebDriverWait(driver, 10)

            iframe = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "iframe[src*='jurisdiccional']")
                )
            )
            driver.switch_to.frame(iframe)

            # 2) Esperar a que aparezca el input con el ID correcto
            input_box = wait.until(
                EC.presence_of_element_located((By.ID, "IdNumeroExp"))
            )
            input_box.clear()
            input_box.send_keys(expediente)

            # 3) Hacer clic en el botón usando WebDriverWait
            boton = wait.until(
                EC.element_to_be_clickable((By.ID, "btnExpediente"))
            )
            boton.click()

            # 4) Esperar a que se renderice la tabla de resultados
            wait.until(
                EC.presence_of_element_located((By.ID, "tabNumExp"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tabla = soup.find("div", id="tabNumExp").find("table")
            df = pd.read_html(io.StringIO(str(tabla)))[0]
            df["Expediente"] = expediente

        finally:
            driver.switch_to.default_content()

        return df

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
