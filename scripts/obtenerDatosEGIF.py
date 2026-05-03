import asyncio
import os
import glob
import zipfile
import json
import pandas as pd
from playwright.async_api import async_playwright

async def scraper():
    with open("data/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    dataScraper = config.get("EGIF", {})

    anio_inicio = dataScraper["anio_inicio"]
    anio_fin = dataScraper["anio_fin"]
    comunidadAutonoma = dataScraper["ComunidadAutonoma"]
    provincia = dataScraper["Provincia"]
    municipio = dataScraper["Municipio"]
    comarcaIsla = dataScraper["ComarcaIsla"]

    nameCSV = dataScraper["nameCSV"]
    nameJson = dataScraper["nameJson"]

    nameZip = f"{dataScraper['nameZip']}.zip"
    output_dir = "Output/EGIF"
    path_zip = os.path.join(output_dir, nameZip)

    if os.path.exists(output_dir) and dataScraper.get("borrarDirectorio", False):
        try:
            for archivo in os.listdir(output_dir):
                ruta = os.path.join(output_dir, archivo)
                if os.path.isfile(ruta):
                    os.remove(ruta)
            print(f"Directorio {output_dir}, vaciado")
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Directorio {output_dir}, creado")
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

            print(f"Inyectando años mediante JS: {anio_inicio} - {anio_fin}")
            await page.evaluate(f"""() => {{
                const d = document.getElementById('txtNumAnioDesde');
                const h = document.getElementById('txtNumAnioHasta');
                if(d) {{ d.value = '{anio_inicio}'; d.dispatchEvent(new Event('change')); }}
                if(h) {{ h.value = '{anio_fin}'; h.dispatchEvent(new Event('change')); }}
            }}""")

            print(f"\nSeleccionando datos de la region\nComunidad Autonoma = {comunidadAutonoma}\nProvincia = {provincia}\nMunicipio = {municipio}\nComarca/Isla = {comarcaIsla}\n")

            if comunidadAutonoma is not None and str(comunidadAutonoma).strip():
                await page.locator('input.default').nth(0).fill(comunidadAutonoma)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("comunidad obtenida")

            if provincia is not None and str(provincia).strip():
                await page.locator('input.default').nth(0).fill(provincia)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("provincia filtrado")

            if municipio is not None and str(municipio).strip() and municipio != 'None':
                await page.locator('input.default').nth(0).fill(municipio)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("municipio filtrado")

            if comarcaIsla is not None and str(comarcaIsla).strip() and comarcaIsla != 'None':
                await page.locator('input.default').nth(0).fill(comarcaIsla)
                await page.locator('input.default').nth(0).press('ArrowLeft')
                await page.locator('input.default').nth(0).press('Enter')
            print("comarca filtrado")

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
            await download.save_as(path_zip)

            print("Descomprimiendo...")
            with zipfile.ZipFile(path_zip, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print(f"Proceso finalizado. Datos en carpeta '{output_dir}'.")

            patron = os.path.join(output_dir, "Xlsx_*.xlsx")
            filesXlsx = glob.glob(patron)
            nameXlsx = filesXlsx[0]
            df = pd.read_excel(nameXlsx)

            df.to_csv(f"{output_dir}/{nameCSV}.csv", index=False, encoding="utf-8")
            json_data = df.to_json(orient='records', indent=4, force_ascii=False)
            with open(f"{output_dir}/{nameJson}.json", "w", encoding="utf-8") as f:
                f.write(json_data)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()


def run():
    asyncio.run(scraper())

if __name__ == "__main__":
    asyncio.run(scraper())
