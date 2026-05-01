import json
from datetime import datetime, timedelta
import math
import os

def calcula_Pefectiva(lluvias):
    if not isinstance(lluvias, list) or len(lluvias) != 7:
        return 0.0
    resultado = 0.0
    for k in range(1, 8):
        resultado += float(lluvias[k - 1]) * math.exp(-0.4 * (k - 1))
    return resultado

def prec_a_float(x):
    if x is None or x == "Ip":
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x.replace(",", "."))
        except ValueError:
            return 0.0
    return 0.0

def cargar_a_indice(ficheros):
    idx = {}
    for path in ficheros:
        with open(path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        for e in datos:
            idx[(e.get("indicativo"), e.get("fecha"))] = prec_a_float(e.get("prec"))
    return idx

def pon_prec_previas_7_con_fuentes(fichero_objetivo, ficheros_fuente, fichero_salida):
    with open(fichero_objetivo, "r", encoding="utf-8") as f:
        datos = json.load(f)

    idx = cargar_a_indice(ficheros_fuente)

    for e in datos:
        indic = e.get("indicativo")
        fecha_dt = datetime.strptime(e["fecha"], "%Y-%m-%d")

        lluvia_7d = []
        for k in range(1, 8):
            fecha_prev = (fecha_dt - timedelta(days=k)).strftime("%Y-%m-%d")
            dato = idx.get((indic, fecha_prev), 0.0)
            e[f"prec_dia_{k}"] = dato
            lluvia_7d.append(dato)

        e["prec_efectiva"] = calcula_Pefectiva(lluvia_7d)

    # Crear carpeta salida si no existe
    os.makedirs(os.path.dirname(fichero_salida), exist_ok=True)

    with open(fichero_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def siguiente_fichero(nombre_base):
    partes = nombre_base.split("_")
    year = int(partes[0])
    provincia = partes[1]
    mitad = partes[2]

    if mitad == "1":
        return f"{year}_{provincia}_2"
    elif mitad == "2":
        return f"{year + 1}_{provincia}_1"
    else:
        raise ValueError(f"Formato no esperado: {nombre_base}")

def crear_v2():
    provincias = ["GUADALAJARA"] # Meter todas las provincias

    for provincia in provincias:
        anterior = f"2015_{provincia}_1"
        actual   = f"2015_{provincia}_2"

        while actual != f"2026_{provincia}_1":
            fichero_actual = f"Output/AEMET/{actual}.json"
            fichero_anterior = f"Output/AEMET/{anterior}.json"
            salida = f"Output/AEMET/v2/{actual}_v2.json"

            # Si no existe el actual, no se puede procesar: saltamos al siguiente
            if not os.path.exists(fichero_actual):
                print("Falta ACTUAL, salto:", fichero_actual)
                anterior = actual
                actual = siguiente_fichero(actual)
                continue

            # Fuentes: siempre el actual, y el anterior solo si existe
            fuentes = [fichero_actual]
            if os.path.exists(fichero_anterior):
                fuentes.append(fichero_anterior)
            else:
                print("Aviso: falta ANTERIOR:", fichero_anterior, "-> se usará solo el actual")

            pon_prec_previas_7_con_fuentes(
                fichero_objetivo=fichero_actual,
                ficheros_fuente=fuentes,
                fichero_salida=salida
            )

            print("OK:", salida)

            anterior = actual
            actual = siguiente_fichero(actual)

if __name__ == "__name__":
    crear_v2()