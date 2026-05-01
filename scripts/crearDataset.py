import pandas as pd
import glob
import json
import os


def cargarArchivos():
    # Cargar Excel de incendios
    dfxl = pd.read_excel("data/Incendios/Incendios_v2.xlsx", sheet_name="Sheet1")

    archivos = glob.glob("Output/AEMET/v2/*.json")

    if not archivos:
        raise FileNotFoundError("No se encontraron archivos JSON en Output/AEMET/v2/")

    dataframes = []
    for archivo in archivos:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        df = pd.DataFrame(datos)
        dataframes.append(df)

    dfjs = pd.concat(dataframes, ignore_index=True)

    return dfxl, dfjs


def añadirCamposIncendio(dfxl, dfjs):
    dfxl = dfxl.copy()

    dfxl["FechaInicio"] = pd.to_datetime(
        dfxl["Detectado"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    ).dt.normalize()

    dfxl["FechaFin"] = pd.to_datetime(
        dfxl["Extinguido"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    ).dt.normalize()

    dfxl["FechaFin"] = dfxl["FechaFin"].fillna(dfxl["FechaInicio"])

    dfjs = dfjs.copy()
    dfjs["fecha"] = pd.to_datetime(dfjs["fecha"], errors="coerce").dt.normalize()

    dias_con_incendio    = set()
    dias_inicio_incendio = set()

    for _, row in dfxl.iterrows():
        indic      = row.get("indicativo_estacion")
        fecha_ini  = row["FechaInicio"]
        fecha_fin  = row["FechaFin"]

        if pd.isna(indic) or pd.isna(fecha_ini):
            continue

        dias_inicio_incendio.add((indic, fecha_ini))

        fecha_actual = fecha_ini
        while fecha_actual <= fecha_fin:
            dias_con_incendio.add((indic, fecha_actual))
            fecha_actual += pd.Timedelta(days=1)

    dfjs["Incendio"] = dfjs.apply(
        lambda r: 1 if (r["indicativo"], r["fecha"]) in dias_con_incendio else 0,
        axis=1
    )
    dfjs["Inicio_incendio"] = dfjs.apply(
        lambda r: 1 if (r["indicativo"], r["fecha"]) in dias_inicio_incendio else 0,
        axis=1
    )

    return dfjs


def crearDataset():
    print("Cargando archivos...")
    dfxl, dfjs = cargarArchivos()

    print(f"  - Registros meteorológicos: {len(dfjs)}")
    print(f"  - Registros de incendios:   {len(dfxl)}")

    print("Añadiendo campos de incendio...")
    dfjs = añadirCamposIncendio(dfxl, dfjs)

    print(f"  - Días con incendio activo:   {dfjs['Incendio'].sum()}")
    print(f"  - Días de inicio de incendio: {dfjs['Inicio_incendio'].sum()}")

    # Guardar el dataset final
    os.makedirs("Output/Dataset", exist_ok=True)
    salida = "Output/Dataset/dataset_final.json"
    dfjs["fecha"] = dfjs["fecha"].dt.strftime("%Y-%m-%d")
    dfjs.to_json(salida, orient="records", force_ascii=False, indent=2)
    print(f"Dataset guardado en: {salida}")

    return dfjs


if __name__ == "__main__":
    crearDataset()