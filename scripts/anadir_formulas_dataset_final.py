import json
import numpy as np
import pandas as pd


# CONFIG

INPUT_JSON_PATH = "Output/Dataset/dataset_final.json"
STATIONS_JSON_PATH = "data/estaciones_v2.json"
OUTPUT_CSV_PATH = "Output/Dataset/dataset_features.csv"

RADIO_METROS = 30000
TRAIN_END_DATE = "2022-12-31"

WINDOWS_SUM_DAYS = [3, 7, 14, 30]
WINDOWS_DRY_DAYS = [7, 14, 30]
WINDOWS_TMAX_MEAN_DAYS = [3, 5, 7]
TROPICAL_NIGHTS_DAYS = 5

# UTILIDADES

def coerce_numeric_series(s: pd.Series) -> pd.Series:
    if not (pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s)):
        return s
    ss = s.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(ss, errors="coerce")

def run():
    # 1) CARGA DATASET PRINCIPAL

    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data).rename(columns={
        "indicativo": "estacion",
        "Inicio_incendio": "inicio_incendio",
        "Incendio": "incendio",
    })

    df["estacion"] = df["estacion"].astype(str).str.strip()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    for col in df.columns:
        if col in ["estacion", "nombre", "provincia", "fecha"]:
            continue
        df[col] = coerce_numeric_series(df[col])

    df["inicio_incendio"] = df.get("inicio_incendio", 0).fillna(0).astype(int)
    df["incendio"] = df.get("incendio", 0).fillna(0).astype(int)

    # Asegurar columnas clave
    for c in ["tmax", "tmin", "tmed", "hrMin", "hrMax", "hrMedia", "prec_efectiva", "velmedia", "racha", "sol"]:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = df[c].astype("float64")

    if "dir" not in df.columns:
        df["dir"] = np.nan
    df["dir"] = df["dir"].fillna(-1).round().astype("Int64")

    static_cols = [c for c in ["nombre", "provincia", "altitud"] if c in df.columns]


    # 2) REINDEX DIARIO POR ESTACIÓN

    parts = []
    for est, g in df.groupby("estacion", sort=False):
        g = g.sort_values("fecha").copy()

        # Rango diario completo
        full_idx = pd.date_range(g["fecha"].min(), g["fecha"].max(), freq="D")

        # Reindex
        g = g.set_index("fecha").reindex(full_idx)
        g["fecha"] = g.index
        g["estacion"] = est

        # Columnas estáticas forward/back fill
        for c in static_cols:
            g[c] = g[c].ffill().bfill()

        # Target: días sin fila -> 0
        g["inicio_incendio"] = g["inicio_incendio"].fillna(0).astype(int)
        g["incendio"] = g["incendio"].fillna(0).astype(int)

        # Mes
        g["mes"] = g["fecha"].dt.month

        parts.append(g.reset_index(drop=True))

    df = pd.concat(parts, ignore_index=True)
    df = df.sort_values(["estacion", "fecha"]).reset_index(drop=True)


    # 3) IMPUTACIÓN

    df["prec_efectiva"] = df["prec_efectiva"].fillna(0.0)
    df["velmedia"] = df["velmedia"].fillna(0.0)
    df["racha"] = df["racha"].fillna(0.0)

    sol_med = df.groupby(["estacion", "mes"])["sol"].transform("median")
    df["sol"] = df["sol"].fillna(sol_med).fillna(df["sol"].median())

    for c in ["hrMin", "hrMax", "hrMedia", "tmax", "tmin", "tmed"]:
        med = df.groupby(["estacion", "mes"])[c].transform("median")
        df[c] = df[c].fillna(med).fillna(df[c].median())


    # 4) ESTACIONALIDAD

    df["dia_del_ano"] = df["fecha"].dt.dayofyear
    df["sin_doy"] = np.sin(2 * np.pi * df["dia_del_ano"] / 365.0)
    df["cos_doy"] = np.cos(2 * np.pi * df["dia_del_ano"] / 365.0)
    df["anio"] = df["fecha"].dt.year


    # 5) ROLLING POR DÍAS REALES

    parts = []
    for est, g in df.groupby("estacion", sort=False):
        g = g.sort_values("fecha").copy().set_index("fecha")

        # lluvia acumulada
        for w in WINDOWS_SUM_DAYS:
            g[f"lluvia_{w}d"] = g["prec_efectiva"].shift(1).rolling(f"{w}D").sum()

        # días sin lluvia
        g["sin_lluvia_flag"] = (g["prec_efectiva"] == 0).astype(int)
        for w in WINDOWS_DRY_DAYS:
            g[f"dias_sin_lluvia_{w}d"] = g["sin_lluvia_flag"].shift(1).rolling(f"{w}D").sum()

        # medias tmax
        for w in WINDOWS_TMAX_MEAN_DAYS:
            g[f"tmax_media_{w}d"] = g["tmax"].shift(1).rolling(f"{w}D").mean()

        # noches tropicales
        g["noche_tropical_flag"] = (g["tmin"] > 20).astype(int)
        g["noches_tropicales_5d"] = g["noche_tropical_flag"].shift(1).rolling(f"{TROPICAL_NIGHTS_DAYS}D").sum()

        # incendios estación
        g["incendios_7d_estacion"] = g["inicio_incendio"].shift(1).rolling("7D").sum()
        g["incendios_30d_estacion"] = g["inicio_incendio"].shift(1).rolling("30D").sum()

        g = g.drop(columns=["sin_lluvia_flag", "noche_tropical_flag"], errors="ignore")
        g = g.reset_index()

        parts.append(g)

    df = pd.concat(parts, ignore_index=True)
    df = df.sort_values(["estacion", "fecha"]).reset_index(drop=True)

    # rellenar NaN rolling con 0
    cols_roll = [c for c in df.columns if c.startswith(("lluvia_", "dias_sin_lluvia_", "tmax_media_", "incendios_"))] + ["noches_tropicales_5d"]
    df[cols_roll] = df[cols_roll].fillna(0.0)


    # 6) ÍNDICES y NO-LEAKAGE

    df["indice_sequedad"] = df["tmax"] * (100.0 - df["hrMin"])

    train_end = pd.to_datetime(TRAIN_END_DATE)
    train_mask = df["fecha"] <= train_end

    # media mensual tmax train-only
    tmax_mean_train = (
        df.loc[train_mask]
        .groupby(["estacion", "mes"])["tmax"].mean()
        .rename("tmax_media_train_mes")
        .reset_index()
    )
    df = df.merge(tmax_mean_train, on=["estacion", "mes"], how="left")

    tmax_mean_train_global_month = (
        df.loc[train_mask]
        .groupby("mes")["tmax"].mean()
        .rename("tmax_media_train_mes_global")
        .reset_index()
    )
    df = df.merge(tmax_mean_train_global_month, on="mes", how="left")

    df["tmax_media_train_mes"] = df["tmax_media_train_mes"].fillna(df["tmax_media_train_mes_global"])
    df["anomalia_tmax_mes"] = df["tmax"] - df["tmax_media_train_mes"]
    df = df.drop(columns=["tmax_media_train_mes_global"], errors="ignore")

    # min/max train-only por estación
    minmax_train = (
        df.loc[train_mask]
        .groupby("estacion")["indice_sequedad"]
        .agg(sequedad_min_train="min", sequedad_max_train="max")
        .reset_index()
    )
    df = df.merge(minmax_train, on="estacion", how="left")

    global_min = df.loc[train_mask, "indice_sequedad"].min()
    global_max = df.loc[train_mask, "indice_sequedad"].max()
    df["sequedad_min_train"] = df["sequedad_min_train"].fillna(global_min)
    df["sequedad_max_train"] = df["sequedad_max_train"].fillna(global_max)

    den = (df["sequedad_max_train"] - df["sequedad_min_train"])
    df["indice_combustibilidad"] = (df["indice_sequedad"] - df["sequedad_min_train"]) / den
    df.loc[den == 0, "indice_combustibilidad"] = 0.0
    df["indice_combustibilidad"] = df["indice_combustibilidad"].replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(0, 1)

    df["evaporacion_estimada"] = (df["tmax"] - df["tmin"]) * (100.0 - df["hrMedia"]) / 100.0


    # 7) VIENTO PELIGROSO

    def p90(series: pd.Series) -> float:
        s = series.dropna().to_numpy()
        return float(np.percentile(s, 90)) if s.size else np.nan

    df["racha_p90_estacion"] = df.groupby("estacion")["racha"].transform(p90)
    df["racha_relativa_p90"] = np.where(df["racha_p90_estacion"] > 0,
                                        df["racha"] / df["racha_p90_estacion"], 0.0)
    df["racha_relativa_p90"] = np.clip(df["racha_relativa_p90"], 0, 3)
    df["viento_fuerte"] = (df["racha"] > df["racha_p90_estacion"]).astype(int)


    # 8) COORDENADAS + incendios_7d_radio (UTM)

    with open(STATIONS_JSON_PATH, "r", encoding="utf-8") as f:
        est_data = json.load(f)

    estaciones = pd.DataFrame(est_data)[["indicativo", "x_utm", "y_utm"]].rename(columns={"indicativo": "estacion"})
    estaciones["estacion"] = estaciones["estacion"].astype(str).str.strip()
    estaciones["x_utm"] = pd.to_numeric(estaciones["x_utm"], errors="coerce")
    estaciones["y_utm"] = pd.to_numeric(estaciones["y_utm"], errors="coerce")
    estaciones = estaciones.dropna(subset=["x_utm", "y_utm"]).drop_duplicates(subset=["estacion"])

    df = df.merge(estaciones, on="estacion", how="left")

    stations_in_df = sorted(set(df["estacion"].unique()).intersection(set(estaciones["estacion"].unique())))
    coords = estaciones.set_index("estacion").loc[stations_in_df][["x_utm", "y_utm"]].to_numpy()
    n = len(stations_in_df)

    if n == 0:
        df["incendios_7d_radio"] = 0.0
    else:
        dx = coords[:, 0].reshape(-1, 1) - coords[:, 0].reshape(1, -1)
        dy = coords[:, 1].reshape(-1, 1) - coords[:, 1].reshape(1, -1)
        dist = np.sqrt(dx * dx + dy * dy)
        A = (dist <= RADIO_METROS).astype(int)

        pivot = df.pivot_table(index="fecha", columns="estacion", values="inicio_incendio", aggfunc="sum").fillna(0.0)
        for s in stations_in_df:
            if s not in pivot.columns:
                pivot[s] = 0.0
        pivot = pivot[stations_in_df]

        M = pivot.shift(1).rolling("7D").sum()
        radio = M.to_numpy().dot(A.T)

        radio_df = pd.DataFrame(radio, index=M.index, columns=stations_in_df)
        radio_long = radio_df.reset_index().melt(id_vars="fecha", var_name="estacion", value_name="incendios_7d_radio")

        df = df.merge(radio_long, on=["fecha", "estacion"], how="left")
        df["incendios_7d_radio"] = df["incendios_7d_radio"].fillna(0.0)


    # 9) EXPORT

    df = df.drop(columns=["tmax_media_train_mes", "sequedad_min_train", "sequedad_max_train"], errors="ignore")
    df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")

    print(f"OK -> CSV guardado en: {OUTPUT_CSV_PATH}")
    print(f"Filas: {len(df):,} | Columnas: {len(df.columns)}")
    print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    run()