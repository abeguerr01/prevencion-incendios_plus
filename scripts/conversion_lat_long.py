from pyproj import Transformer
import json

# AEMET -> decimal

def aemet_a_decimal(coord: str) -> float:
    hemi = coord[-1].upper()
    nums = coord[:-1]

    if hemi in ("N", "S"):
        if len(nums) != 6:
            raise ValueError(f"Latitud con longitud inesperada: {coord}")
        deg = int(nums[0:2])
        minute = int(nums[2:4])
        sec = int(nums[4:6])

    elif hemi in ("E", "W"):
        if len(nums) == 7:
            deg = int(nums[0:3])
            minute = int(nums[3:5])
            sec = int(nums[5:7])
        elif len(nums) == 6:
            deg = int(nums[0:2])
            minute = int(nums[2:4])
            sec = int(nums[4:6])
        else:
            raise ValueError(f"Longitud con longitud inesperada: {coord}")
    else:
        raise ValueError(f"Hemisferio inválido en {coord}")

    dec = deg + minute / 60 + sec / 3600
    if hemi in ("S", "W"):
        dec *= -1
    return dec


# AEMET -> UTM

#Esto sirve porque todas las estaciones de CLM están en el uso 30
transformer = Transformer.from_crs(
    "EPSG:4326",   # Lat/Lon
    "EPSG:25830",  # UTM huso 30 - ETRS89
    always_xy=True
)

def aemet_a_utm(lat_aemet: str, lon_aemet: str):
    lat = aemet_a_decimal(lat_aemet)
    lon = aemet_a_decimal(lon_aemet)
    x, y = transformer.transform(lon, lat)
    return x, y


# : procesar fichero de estaciones

def crear_estaciones_v2(ruta_entrada: str):
    ruta_entrada = "data/estaciones.json"
    ruta_salida = "data/estaciones_v2.json"
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        estaciones = json.load(f)

    estaciones_v2 = []

    for est in estaciones:
        est_nueva = est.copy()

        try:
            lat = est["latitud"]
            lon = est["longitud"]

            x_utm, y_utm = aemet_a_utm(lat, lon)

            est_nueva["x_utm"] = round(x_utm, 3)
            est_nueva["y_utm"] = round(y_utm, 3)

        except Exception as e:
            # Si algo falla, lo dejamos explícito
            
            est_nueva["x_utm"] = None
            est_nueva["y_utm"] = None
            est_nueva["error_utm"] = str(e)

        estaciones_v2.append(est_nueva)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(estaciones_v2, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    crear_estaciones_v2("data/estaciones.json")