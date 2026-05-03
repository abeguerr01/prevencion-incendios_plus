import json
import os

import scripts.obtenerDatosEGIF as egif
import scripts.obtenerDatosAEMET as aemet
import scripts.creador_prec_7 as prec7
import scripts.conversion_lat_long as c_latlon
import scripts.creador_incendios_v2 as civ2
import scripts.crearDataset as cDataset
import scripts.anadir_formulas_dataset_final as afdf
import scripts.entrenar_modelo_catboost as entrenarModelo
import scripts.filtrar_fecha as ff
import scripts.predictor_analizador as predictor

ROOT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(ROOT_DIR, "data", "config.json")


def cargar_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = cargar_config()
    print("--- Iniciando proceso secuencial ---")

    print(" [1/8] Configurando estaciones y obteniendo datos AEMET...")
    c_latlon.crear_estaciones_v2(os.path.join(ROOT_DIR, "data", "estaciones.json"))
    aemet.run()

    egif_config = config.get("EGIF", {})
    if egif_config.get("activo", False):
        print(" [2/8] Ejecutando EGIF...")
        egif.run()
    else:
        print(" [2/8] EGIF desactivado; se omite obtenerDatosEGIF.py")

    print(" [3/8] Procesando datos de incendios...")
    civ2.crear_incendios_unico()

    print(" [4/8] Creando el Dataset base...")
    cDataset.crearDataset()

    print(" [5/8] Aplicando fórmulas al dataset final...")
    afdf.run()

    print(" [6/8] Entrenando el modelo CatBoost...")
    entrenarModelo.run()

    print(" [7/8] Filtrando por fecha...")
    ff.run()

    print(" [8/8] Ejecutando predictor analizador...")
    predictor.predecir()

    print("--- Proceso finalizado con éxito ---")


if __name__ == "__main__":
    main()
