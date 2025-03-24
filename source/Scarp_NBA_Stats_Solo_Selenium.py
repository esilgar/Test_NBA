# Importamos las librerías necesarias
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# By: Para buscar elementos por ID, nombre, clase, etc
from selenium.webdriver.support.ui import WebDriverWait
# WebDriverWait: Permite esperar a que algo ocurra en la página (como que cargue un elemento).
# Muy útil cuando hay contenido que tarda un poco en aparecer.
from selenium.webdriver.support import expected_conditions as EC
# expected_conditions as EC:  condiciones predefinidas que puedes usar con WebDriverWait, por ejemplo:

# - presence_of_element_located: espera a que el elemento exista en el DOM.
# - element_to_be_clickable: espera a que se pueda hacer clic en un botón.
# - visibility_of_element_located: espera a que un elemento sea visible.
from bs4 import BeautifulSoup #  Para leer y procesar el HTML (extraer tablas)
import pandas as pd
import time # Usamos sleep() para pausas breves si hace falta
import re # usaremos regular expressions para separar los campos de la tabla en formato dia/mes/año
import time as t # Usamos sleep() para pausas breves si hace falta

# INICIAMOS EL CONTADOR DE TIEMPO
start_time = t.time()
# Revisando el robots.txt hay algunos bots que no están permitidos, configuramos nuestro usre-agent
# Configurar opciones
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")

# Crear el driver (asume que chromedriver.exe está en el mismo directorio)
driver = webdriver.Chrome(options=options)

# Cargar la página
url = "https://www.nba.com/stats"
driver.get(url)
wait = WebDriverWait(driver, 10)

# Intentar cerrar el banner de cookies si aparece
# Cerrar banner de cookies si aparece
try:
    wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
except:
    pass



t.sleep(3)  # ⏳ Espera temporal por renderizado completo

# Intentar hacer clic en el botón "See All Player Stats"

# Esperar y luego hacer clic en "See All Player Stats"
try:
    see_all_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "See All Player Stats")))
    see_all_link.click()
    print("✔️ Click en 'See All Player Stats' exitoso")
except Exception as e:
    print("❌ No se pudo hacer click:", e)

# 3. Esperar que cargue la tabla
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Crom_body__UYOcU")))
print("✔️ Tabla detectada")

# Extraer headers de la tabla
headers_row = driver.find_element(By.CLASS_NAME, "Crom_headers__mzI_m")
headers_th = headers_row.find_elements(By.TAG_NAME, "th")

headers = []
for th in headers_th[1:]:
    if th.get_attribute("hidden"):
        continue
    header_name = th.text.strip()
    if not header_name:
        # Si no tiene texto, usamos el atributo "field"
        header_name = th.get_attribute("field")
    headers.append(header_name)

# Lista para almacenar todos los datos
all_data = []

# Loop de paginación, lo repetimos hasta llegar a la última página
while True:
    # Esperamos que la tabla de jugadores esté cargada
    tbody = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Crom_body__UYOcU")))
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    print(f"Número de jugadores en esta página: {len(rows)}")
    # Extraemos los datos de todas las filas visibles en esta página
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if not cols:
            continue
        player = cols[1].text.strip()
        stats = [td.text.strip() for td in cols[2:]]  # Ignora posición y nombre ya extraído
        all_data.append([player] + stats)

    # Intentar ir a la siguiente página
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, 'button[title="Next Page Button"]')
        # Si el botón está deshabilitado, significa que estamos en la última página
        if next_btn.get_attribute("disabled"):
            break  # Última página
        # Si no está deshabilitado, hacemos clic y esperamos que la tabla recargue
        next_btn.click()
        t.sleep(3)  # ⏳ Espera temporal por renderizado completo
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Crom_body__UYOcU")))
    except:
        break


# Cerramos navegador
driver.quit()

# Creamo DataFrame
df = pd.DataFrame(all_data, columns=["Player"] + headers[1:])

# Mostramos primeras filas
print(df.head())

# Guardamos en CSV
df.to_csv("nba_player_stats.csv", index=False, encoding="utf-8-sig")
print("\n✅ Proceso finalizado. Archivo guardado como 'nba_player_stats.csv'.")

# TIEMPO FINAL
end_time = t.time()
duration = end_time - start_time
print(f"⏱️ Tiempo total de ejecución: {duration:.2f} segundos")