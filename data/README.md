# Configuración — config_EGIF.json

Este archivo explica los campos que debe contener `data/config_EGIF.json` para que el script `scripts/obtenerDatosEGIF.py` descargue y procese los datos de incendios del servicio EGIF.

## Resumen
El scrapper consulta el servicio público del Ministerio y exporta un ZIP con un archivo XLSX que luego se convierte a CSV y JSON. Los resultados se guardan en `Output/EGIF`.

## Ejemplo de config_EGIF.json
```json
{
  "anio_inicio": 2015,
  "anio_fin": 2024,
  "ComunidadAutonoma": "ANDALUCIA",
  "Provincia": "",
  "Municipio": "",
  "ComarcaIsla": "",
  "borrarDirectorio": true,
  "nameZip": "EGIF_export",
  "nameCSV": "incendios",
  "nameJson": "incendios"
}
```

- `anio_inicio` (int, obligatorio): año desde el que buscar.
- `anio_fin` (int, obligatorio): año hasta el que buscar.
- `ComunidadAutonoma` (string): nombre de la comunidad (ej.: `ANDALUCIA`, `ARAGON`, `CATALUÑA`, `MADRID`, etc.). Si no procede, dejar `""` o `null`.
- `Provincia` (string): provincia dentro de la comunidad. Dejar `""` o `null` si no procede.
- `Municipio` (string): municipio. Dejar `""` o `null` si no procede.
- `ComarcaIsla` (string): comarca o isla. Dejar `""` o `null` si no procede.
- `borrarDirectorio` (bool, obligatorio): si `true`, vacía `Output/EGIF` al iniciar.
- `nameZip` (string, obligatorio): nombre base del ZIP (el script añade `.zip`).
- `nameCSV` (string, obligatorio): nombre del archivo CSV de salida (sin extensión).
- `nameJson` (string, obligatorio): nombre del archivo JSON de salida (sin extensión).

## Salida
- Carpeta: `Output/EGIF`
- Archivos generados:
  - `<nameZip>.zip` (descargado)
  - `Xlsx_*.xlsx` (contenido del ZIP)
  - `<nameCSV>.csv`
  - `<nameJson>.json`

## Dependencias e instalación
Instalar paquetes necesarios (desde la raíz del proyecto en Windows):
```powershell
pip install pandas openpyxl playwright
python -m playwright install
```
(Agregar otras dependencias si el proyecto tiene `requirements.txt`.)

## Uso
Desde la raíz del proyecto:
```powershell
python .\scripts\obtenerDatosEGIF.py
```
El script lee `data/config_EGIF.json`, realiza la búsqueda y guarda los resultados en `Output/EGIF`.

## Notas y errores comunes
- `nameZip` no debe incluir la extensión, el script añade `.zip`.
- Si recibes errores relacionados con la descarga, asegúrate de ejecutar `python -m playwright install` y de que la web no haya cambiado la estructura.