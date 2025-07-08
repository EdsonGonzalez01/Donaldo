from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def consultar_expediente_selenium(expediente_completo, sala):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Puedes comentar para ver el navegador
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    driver = webdriver.Chrome(options=options)

    try:
        # print(f"🌐 Cargando sitio para expediente {expediente_completo} - Sala: {sala}")
        driver.get("https://tjajal.gob.mx/boletines")
        wait = WebDriverWait(driver, 20)

        # Ingresar expediente completo
        campo_expediente = wait.until(EC.presence_of_element_located((By.NAME, "NExpediente")))
        campo_expediente.clear()
        campo_expediente.send_keys(expediente_completo)
        # print("✅ Expediente ingresado completo")

        # Seleccionar sala
        select_sala = Select(driver.find_element(By.NAME, "Sala"))
        sala_valor = sala.strip().upper()
        select_sala.select_by_value(sala_valor)
        # print(f"✅ Sala seleccionada por value: {sala_valor}")

        # Clic en botón filtrar
        boton_filtrar = driver.find_element(By.ID, "btn_filtrar")
        boton_filtrar.click()
        # print("✅ Botón 'Filtrar' clickeado")

        # Esperar y hacer clic en la fila tdtoggle (manejando stale element)
        try:
            # print("⏳ Esperando resultados...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#boletinsTables td.tdtoggle")))
            time.sleep(1)  # espera adicional

            # Volver a localizar el elemento para evitar stale reference
            fila = driver.find_element(By.CSS_SELECTOR, "#boletinsTables td.tdtoggle")
            driver.execute_script("arguments[0].scrollIntoView(true);", fila)
            time.sleep(0.5)
            fila = driver.find_element(By.CSS_SELECTOR, "#boletinsTables td.tdtoggle")

            try:
                collapse_div = fila.find_element(By.CSS_SELECTOR, "div.collapse")
                if "display: block" in collapse_div.get_attribute("style"):
                    print("🟢 Detalles ya visibles, no se requiere clic")
                else:
                    driver.execute_script("arguments[0].click();", fila)
                    # print("✅ Fila clickeada para mostrar detalles")
            except:
                driver.execute_script("arguments[0].click();", fila)
                print("⚠️ Collapse no encontrado, clic forzado en fila")

        except Exception as e:
            print(f"❌ No se pudo hacer clic en la fila para expediente {expediente_completo}: {e}")
            driver.save_screenshot(f"error_click_fila_{expediente_completo.replace('/', '_')}.png")
            return []

        # Esperar y parsear detalles
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.timeline-box")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # INFO GENERAL
        info_general_div = soup.select_one("section#timeline article.timeline-box")
        info_general_data = {
            "fecha_expediente": "",
            "rubro": "",
            "actor": "",
            "demandados": "",
            "terceros": ""
        }

        if info_general_div:
            for p in info_general_div.find_all("p"):
                texto = p.get_text(strip=True)
                if "Fecha del Expediente" in texto:
                    info_general_data["fecha_expediente"] = texto.replace("Fecha del Expediente:", "").strip()
                elif "Rubro del acto reclamado" in texto:
                    info_general_data["rubro"] = texto.replace("Rubro del acto reclamado:", "").strip()
                elif "Actor" in texto:
                    info_general_data["actor"] = texto.replace("Actor:", "").strip()
                elif "Demandados" in texto:
                    info_general_data["demandados"] = texto.replace("Demandados:", "").strip()
                elif "Terceros" in texto:
                    info_general_data["terceros"] = texto.replace("Terceros:", "").strip()

        # EVENTOS
        fechas = soup.select("section#timeline div.timeline-date")
        articulos = soup.select("section#timeline article.timeline-box")

        resultados = []

        for fecha_div, articulo in zip(fechas, articulos):
            texto_fecha = fecha_div.get_text(strip=True)
            if texto_fecha.lower().startswith("información general"):
                continue

            datos = {
                "expediente": expediente_completo,
                "sala": sala,
                "fecha_publicacion": texto_fecha,
                "fecha_acuerdo": "",
                "detalle": ""
            }

            contenido = articulo.find("div", class_="portfolio-item")
            if contenido:
                for p in contenido.find_all("p"):
                    texto = p.get_text(strip=True)
                    if "Fecha Acuerdo" in texto:
                        datos["fecha_acuerdo"] = texto.replace("Fecha Acuerdo:", "").strip()
                    elif "Fecha Publicación" in texto:
                        continue
                    else:
                        datos["detalle"] += texto + " "

            datos.update(info_general_data)
            resultados.append(datos)

        return resultados

    except Exception as e:
        print(f"❌ Error general con expediente {expediente_completo}: {e}")
        driver.save_screenshot(f"error_general_{expediente_completo.replace('/', '_')}.png")
        return []

    finally:
        driver.quit()

def extraer_datos():
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir.parent / "files" / "actualizaciones_expedientes_tjajal.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    expedientes_path = script_dir.parent / "files" / "expedientes_tjajal.csv"

    df_lista = pd.read_csv(expedientes_path, encoding='utf-8-sig')
    expedientes = df_lista["expediente"].tolist()
    salas = df_lista["sala"].tolist()

    todos_resultados = []
    start_time = time.time()

    for expediente_completo, sala in zip(expedientes, salas):
        try:
            resultados = consultar_expediente_selenium(expediente_completo.strip(), sala.strip())
            todos_resultados.extend(resultados)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error procesando expediente {expediente_completo}: {e}")

    end_time = time.time()
    elapsed = end_time - start_time

    if todos_resultados:
        df_final = pd.DataFrame(todos_resultados)
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        # print(f"✅ Archivo generado: {output_path.name}")
    else:
        print("⚠️ No se encontró información en ninguno de los expedientes")

    return {
        "status": "success" if todos_resultados else "warning",
        "message": f"{len(todos_resultados)} registros extraídos",
        "elapsed_time": elapsed
    }
