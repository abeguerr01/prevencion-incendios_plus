import pandas as pd
import json
import math

def cargar_estaciones(ruta_json: str):
    with open(ruta_json, "r", encoding="utf-8") as f:
        estaciones = json.load(f)

    # Nos quedamos solo con estaciones con UTM válido
    estaciones_ok = []
    for e in estaciones:
        x = e.get("x_utm")
        y = e.get("y_utm")
        if x is None or y is None:
            continue
        try:
            e["x_utm"] = float(x)
            e["y_utm"] = float(y)
            estaciones_ok.append(e)
        except Exception:
            continue

    if not estaciones_ok:
        raise ValueError("No se encontraron estaciones con x_utm/y_utm válidos en el JSON.")
    return estaciones_ok


def estacion_mas_cercana(x: float, y: float, estaciones):
    min_dist = float("inf")
    mejor = None

    for e in estaciones:
        dx = e["x_utm"] - x
        dy = e["y_utm"] - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < min_dist:
            min_dist = dist
            mejor = e

    return mejor, min_dist


def añadir_estacion_mas_cercana_excel(
    ruta_excel_in: str,
    ruta_estaciones_json: str,
    ruta_excel_out: str,
    col_x: str = "CoordenadaX",
    col_y: str = "CoordenadaY",
):
    # Cargar excel y estaciones
    df = pd.read_excel(ruta_excel_in)
    estaciones = cargar_estaciones(ruta_estaciones_json) # estaciones = estaciones_v2.json

    # Comprobar columnas
    if col_x not in df.columns or col_y not in df.columns:
        raise ValueError(
            f"El Excel no tiene las columnas esperadas '{col_x}' y '{col_y}'. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    estaciones_nombre = []
    estaciones_indicativo = []
    distancias_m = []

    # Calcular estación más cercana por fila
    for i, fila in df.iterrows():
        try:
            x = float(fila[col_x])
            y = float(fila[col_y])
        except Exception:
            estaciones_nombre.append(None)
            estaciones_indicativo.append(None)
            distancias_m.append(None)
            continue

        est, dist = estacion_mas_cercana(x, y, estaciones)
        estaciones_nombre.append(est.get("nombre"))
        estaciones_indicativo.append(est.get("indicativo"))
        distancias_m.append(round(dist, 1))  # metros

    # Añadir columnas nuevas
    df["estacion_mas_cercana"] = estaciones_nombre
    df["indicativo_estacion"] = estaciones_indicativo
    df["distancia_estacion_m"] = distancias_m

    # Guardar
    df.to_excel(ruta_excel_out, index=False)

import glob, os

def crear_incendios_unico(
    ruta_excel_in: str | None = None,
    ruta_excel_out: str | None = None,
):
    """
    Procesa el archivo único de incendios 2015-2025.

    Si no se proporciona ``ruta_excel_in`` se busca cualquier fichero
    ``*.xlsx`` dentro de ``data/incendios``. Esto permite que el archivo
    se llame diferente siempre que sea el único xlsx presente.

    ``ruta_excel_out`` puede proporcionarse para evitar sobrescribir el
    fichero de entrada. Si se omite se genera añadiendo ``_con_estacion``
    al nombre de la entrada.
    """

    print("Procesando archivo único de incendios 2015-2025...")

    # elegir un archivo automáticamente si no se indica uno explícitamente
    if ruta_excel_in is None:
        # sólo consideramos archivos que empiezan por 'incendios' (los años pueden variar)
        pattern = os.path.join("data", "incendios", "incendios*.xlsx")
        files = glob.glob(pattern)
        if not files:
            raise FileNotFoundError(
                "No se encontró ningún archivo 'incendios*.xlsx' en 'data/incendios'. "
                "Coloca el fichero allí o pasa la ruta al invocar la función."
            )
        if len(files) > 1:
            print("Advertencia: hay varios archivos coincidentes, usando el primero:", files[0])
        ruta_excel_in = files[0]

    # construir ruta de salida si no se especificó
    if ruta_excel_out is None:
        base, ext = os.path.splitext(ruta_excel_in)
        ruta_excel_out = base + "_con_estacion" + ext
        print(f"Ruta de salida generada: {ruta_excel_out}")

    añadir_estacion_mas_cercana_excel(
        ruta_excel_in=ruta_excel_in,
        ruta_estaciones_json="data/estaciones_v2.json",
        ruta_excel_out=ruta_excel_out,
        col_x="CoordenadaX",
        col_y="CoordenadaY",
    )

    print("Proceso terminado.")


# Ejecutar
if __name__ == "__main__":
    crear_incendios_unico()
