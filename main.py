#import scripts.obtenerDatosEGIF as egif
import scripts.obtenerDatosAEMET as aemet
import scripts.creador_prec_7 as prec7
import scripts.conversion_lat_long as c_latlon
import scripts.creador_incendios_v2 as civ2
import scripts.crearDataset as cDataset
import scripts.anadir_formulas_dataset_final as afdf
import scripts.entrenar_modelo_catboost as entrenarModelo
import scripts.filtrar_fecha as ff
import scripts.predictor_analizador as predictor

def main():
    print("--- Iniciando proceso secuencial ---")

    # 1. Datos AEMET y geolocalización
    print(" [1/8] Configurando estaciones y obteniendo datos AEMET...")
    c_latlon.crear_estaciones_v2("data/estaciones.json")
    aemet.run()
    prec7.crear_v2()

    # 2. Web incendios
    print(" [2/8] Procesando datos de incendios...")
    # egif.run() # Descomentar si es necesario
    civ2.crear_incendios_unico()
    # 3. Dataset
    print(" [3/8] Creando el Dataset base...")
    cDataset.crearDataset()

    # 4. Fórmulas
    print(" [4/8] Aplicando fórmulas al dataset final...")
    afdf.run()

    print(" [5/8] Entrenando el modelo CatBoost...")
    entrenarModelo.run() 

    # 6. Filtrado
    print(" [6/8] Filtrando por fecha...")
    ff.run() 

    # 7. Predicción
    print(" [7/8] Ejecutando predictor analizador...")
    predictor.predecir()

    print("--- Proceso finalizado con éxito ---")

#Ejecutar
if __name__ == "__main__":
    main()