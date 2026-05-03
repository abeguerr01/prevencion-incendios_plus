import requests
import json
import time
from collections import defaultdict
from datetime import datetime
import math


def prec_a_float(prec):
    if prec is None:
        return 0.0
    prec = prec.strip()
    if prec.lower() == "ip" or prec == "":
        return 0.0
    return float(prec.replace(",", "."))


def añadir_prec_efectiva_7_dias(datos, alpha=0.4):
    """
    datos: lista de diccionarios (JSON de AEMET)
    alpha: coeficiente de decaimiento exponencial
    Añade el campo 'prec_efectiva_7_dias'
    """

    estaciones = defaultdict(list)
    for d in datos:
        estaciones[d["indicativo"]].append(d)
        
    for indicativo, registros in estaciones.items():
        registros.sort(key=lambda x: datetime.strptime(x["fecha"], "%Y-%m-%d"))

        precs = [prec_a_float(r.get("prec")) for r in registros]

        for i, registro in enumerate(registros):
            inicio = max(0, i - 6)

            prec_efectiva = 0.0
            for j in range(inicio, i + 1):
                n = i - j
                prec_efectiva += precs[j] * math.exp(-alpha * n)

            registro["prec_efectiva_7_dias"] = round(prec_efectiva, 2)

    return datos


def identificadores(provincia):
    """
    provincia: "GUADALAJARA" | "TOLEDO" | "CIUDADAD REAL" | "CUENCA" | "ALBACETE" 
    """
    with open("data/estaciones.json", "r", encoding="utf-8") as f:
        estaciones = json.load(f)

    string_estaciones = ""
    for estacion in estaciones:
        if estacion.get("provincia") == provincia:
            string_estaciones +=  estacion.get("indicativo") + ","
    return string_estaciones[:-1]


def solicitud(fecha_ini, fecha_fin, id_estaciones, api):
    """
    fecha_ini: "AAAA-MM-DD"
    fecha_fin: "AAAA-MM-DD"
    id_estaciones: "identificacion1,identificacion2,...."
    """
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/"
    url += fecha_ini + "T00%3A00%3A00UTC/fechafin/" + fecha_fin + "T23%3A59%3A59UTC/estacion/" + id_estaciones

    mi_api_key = api
    querystring = {"api_key": mi_api_key}

    headers = {'cache-control': "no-cache"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    response = response.json()

    while response["estado"] != 200:
        response = requests.request("GET", url, headers=headers, params=querystring)
        response = response.json()

    url_datos = response["datos"]
    response = requests.request("GET", url_datos, headers=headers)

    return response.json()


def printear(mensaje):
    print(mensaje)



def run():
    provincia = "GUADALAJARA"
    id_estaciones = identificadores(provincia)

    with open("data/config.json", "r", encoding="utf-8") as archivo:
        config = json.load(archivo)
    api = config.get("AEMET", {}).get("api", "").strip()

    if not api:
        with open("data/APIs.json", "r", encoding="utf-8") as archivo:
            japi = json.load(archivo)
        api = japi.get("Alejandro", "")

    anyo_inicio = "2015"
    anyo_actual = "2025"
    anyo = int(anyo_inicio)

    while anyo <= int(anyo_actual):
        anyo_str = str(anyo)

        enero = anyo_str + "-01-01"
        junio = anyo_str + "-06-30"
        julio = anyo_str + "-07-01"
        diciembre = anyo_str + "-12-31"

        response_1 = solicitud(enero, junio, id_estaciones, api)
        time.sleep(10)

        response_2 = solicitud(julio, diciembre, id_estaciones, api)
        time.sleep(10)

        response_1 = añadir_prec_efectiva_7_dias(response_1)
        response_2 = añadir_prec_efectiva_7_dias(response_2)

        with open(f"Output/AEMET/{anyo_str}_{provincia}_1.json", "w", encoding="utf-8") as f:
            json.dump(response_1, f, ensure_ascii=False, indent=2)

        with open(f"Output/AEMET/{anyo_str}_{provincia}_2.json", "w", encoding="utf-8") as f:
            json.dump(response_2, f, ensure_ascii=False, indent=2)

        anyo += 1
