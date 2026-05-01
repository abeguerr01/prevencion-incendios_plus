import pandas as pd
import argparse

input_file = "Output/Dataset/dataset_features.csv"
output_file = "Output/Dataset/dataset_filtrado.csv"
fecha_inicio = "2021-11-16"
fecha_fin = "2022-12-31"

def filtrar_csv(input_file, output_file, fecha_inicio, fecha_fin):
    # Leer CSV
    df = pd.read_csv(input_file)

    # Convertir columna fecha a datetime
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")

    # Convertir parámetros a datetime
    inicio = pd.to_datetime(fecha_inicio, format="%Y-%m-%d")
    fin = pd.to_datetime(fecha_fin, format="%Y-%m-%d")

    # Filtrar rango
    df_filtrado = df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)]

    # Guardar resultado
    df_filtrado.to_csv(output_file, index=False)

    print(f"Filas originales: {len(df)}")
    print(f"Filas filtradas: {len(df_filtrado)}")
    print(f"Archivo guardado en: {output_file}")

def run():
    filtrar_csv(input_file, output_file, fecha_inicio, fecha_fin)

if __name__ == "__main__":
    run()