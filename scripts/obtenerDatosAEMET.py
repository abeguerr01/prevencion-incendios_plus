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
    if not datos or not isinstance(datos, list):
        return datos

    estaciones = defaultdict(list)
    for d in datos:
        if "indicativo" in d and "fecha" in d:
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
    with open("data/estaciones.json", "r", encoding="utf-8-sig") as f:
        estaciones = json.load(f)

    string_estaciones = ""
    for estacion in estaciones:
        if estacion.get("provincia") == provincia:
            string_estaciones += estacion.get("indicativo") + ","
    return string_estaciones[:-1]

def solicitud(fecha_ini, fecha_fin, id_estaciones, api, max_retries=5):
    url_base = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/"
    url = f"{url_base}{fecha_ini}T00%3A00%3A00UTC/fechafin/{fecha_fin}T23%3A59%3A59UTC/estacion/{id_estaciones}"
    
    headers = {
        'cache-control': "no-cache",
        'User-Agent': 'Mozilla/5.0'
    }
    querystring = {"api_key": api}

    for intento in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            
            if response.status_code == 200:
                res_json = response.json()
                
                if res_json.get("estado") == 200:
                    url_datos = res_json.get("datos")
                    res_datos = requests.get(url_datos, headers=headers, timeout=30)
                    if res_datos.status_code == 200:
                        return res_datos.json()
                
                elif res_json.get("estado") == 429:
                    print(f"Límite de peticiones alcanzado. Reintentando...")
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print(f"Fallo de conexión en intento {intento + 1}. Reintentando...")
        
        time.sleep(5 * (intento + 1))
    
    return []

def run():
    provincia = "GUADALAJARA"
    id_estaciones = identificadores(provincia)

    try:
        with open("data/config.json", "r", encoding="utf-8-sig") as archivo:
            config = json.load(archivo)
        api = config.get("AEMET", {}).get("api", "").strip()
    except FileNotFoundError:
        api = ""

    if not api:
        with open("data/APIs.json", "r", encoding="utf-8-sig") as archivo:
            japi = json.load(archivo)
        api = japi.get("Alejandro", "")

    anyo_inicio = 2015
    anyo_actual = 2025
    
    for anyo in range(anyo_inicio, anyo_actual + 1):
        anyo_str = str(anyo)
        print(f"Procesando: {anyo_str}")

        e1_ini, e1_fin = f"{anyo_str}-01-01", f"{anyo_str}-06-30"
        e2_ini, e2_fin = f"{anyo_str}-07-01", f"{anyo_str}-12-31"

        res1 = solicitud(e1_ini, e1_fin, id_estaciones, api)
        time.sleep(5)

        res2 = solicitud(e2_ini, e2_fin, id_estaciones, api)
        time.sleep(5)

        if res1:
            res1 = añadir_prec_efectiva_7_dias(res1)
            with open(f"Output/AEMET/{anyo_str}_{provincia}_1.json", "w", encoding="utf-8") as f:
                json.dump(res1, f, ensure_ascii=False, indent=2)

        if res2:
            res2 = añadir_prec_efectiva_7_dias(res2)
            with open(f"Output/AEMET/{anyo_str}_{provincia}_2.json", "w", encoding="utf-8") as f:
                json.dump(res2, f, ensure_ascii=False, indent=2)