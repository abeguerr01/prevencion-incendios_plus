import asyncio
import os
import glob
import zipfile
import json
import pandas as pd
from playwright.async_api import async_playwright

async def scraper():
    with open("data/config_EGIF.json", "r") as f:
        dataScraper = json.load(f)

    anio_inicio = dataScraper["anio_inicio"]
    anio_fin = dataScraper["anio_fin"]
    comunidadAutonoma = dataScraper["ComunidadAutonoma"]
    provincia = dataScraper["Provincia"]
    municipio = dataScraper["Municipio"]
    comarcaIsla = dataScraper["ComarcaIsla"]

    nameCSV = dataScraper["nameCSV"]
    nameJson = dataScraper["nameJson"]

    nameZip = f"{dataScraper["nameZip"]}.zip"
    output_dir = "Output/EGIF"
    path_zip = os.path.join(output_dir, nameZip)
    
    if os.path.exists(output_dir) and dataScraper["borrarDirectorio"]:
        try:
            for archivo in os.listdir(output_dir):
                ruta = os.path.join(output_dir, archivo)
                if os.path.isfile(ruta): # Solo borra si es un archivo
                    os.remove(ruta)
            print(f"Directorio {output_dir}, vaciado")
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
         if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Directorio {output_dir}, vaciado")
            except Exception as e:
                print(f"Error: {e}")
                return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("Navegando al sitio...")
            await page.goto("https://servicio.mapa.gob.es/incendios/Search/Publico", wait_until="networkidle")

            # Forzamos los valores directamente en el inyectando js
            # Esto ignora si el panel está colapsado o si el input es invisible
            print(f"Inyectando años mediante JS: {anio_inicio} - {anio_fin}")
            await page.evaluate(f"""() => {{
                const d = document.getElementById('txtNumAnioDesde');
                const h = document.getElementById('txtNumAnioHasta');
                if(d) {{ d.value = '{anio_inicio}'; d.dispatchEvent(new Event('change')); }}
                if(h) {{ h.value = '{anio_fin}'; h.dispatchEvent(new Event('change')); }}
            }}""")

            # 2. Seleccion de region
            print(f"\nSeleccionando datos de la region\nComunidad Autonoma = {comunidadAutonoma}\nProvincia = {provincia}\nMunicipio = {municipio}\nComarca/Isla = {comarcaIsla}\n")
            
            #Comunidad Autonoma
            if comunidadAutonoma and str(comunidadAutonoma).strip():
                await page.locator('input.default').nth(0).fill(comunidadAutonoma)
                await page.locator('input.default').nth(0).fill(comunidadAutonoma)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("comunidad obtenida")

            #Provincia
            if provincia and str(provincia).strip():
                await page.locator('input.default').nth(0).fill(provincia)
                await page.locator('input.default').nth(0).fill(provincia)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("provincia filtrado")

            #Municipio
            if municipio and str(municipio).strip():
                await page.locator('input.default').nth(0).fill(municipio)
                await page.locator('input.default').nth(0).fill(municipio)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("municipio filtrado")

            if comarcaIsla and str(comarcaIsla).strip():
                await page.locator('input.default').nth(0).fill(comarcaIsla)
                await page.locator('input.default').nth(0).fill(comarcaIsla)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("comarca filtrado")

            # 3. Click en Buscar
            print("Ejecutando búsqueda...")
            await page.click("#btnBusqueda")

            print("Esperando carga...")
            await page.wait_for_load_state("networkidle")
            await page.click("#idExportacionDatos")
            
            print("Seleccionando opcion...")
            await page.click("label[for='idTipoExportacionExcelResumen']")
            await page.wait_for_load_state("networkidle")

            print("Exportando...")
            await page.click("#btnExportarDatosFullxmlCapitulosZip")
            await page.wait_for_load_state("networkidle")

            print("Descargando...")
            async with page.expect_download() as download_info:
                await page.click("#btnDescargaXmlCapitulos")

            download = await download_info.value


            # Guardar el archivo donde quieras
            await download.save_as(path_zip)
            
            # Descomprimir
            print("Descomprimiendo...")
            with zipfile.ZipFile(path_zip, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print(f"Proceso finalizado. Datos en carpeta '{output_dir}'.")
            
            #archivo
            patron = os.path.join(output_dir, "Xlsx_*.xlsx")
            filesXlsx = glob.glob(patron)
            nameXlsx = filesXlsx[0] #Solo hay un xlsx
            df = pd.read_excel(nameXlsx)

            # Convertir a CSV y guardar
            df.to_csv(f"{output_dir}/{nameCSV}.csv", index=False, encoding="utf-8")

            # Convertir a JSON y guardar
            json_data = df.to_json(orient='records', indent=4, force_ascii=False)
            with open(f"{output_dir}/{nameJson}.json", "w", encoding="utf-8") as f:
                f.write(json_data)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

# Para arrancar desde otro archivo
def run():
    asyncio.run(run())

# Para arrancar desde este mismo archivo
if __name__ == "__main__":
    asyncio.run(scraper())