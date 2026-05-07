import os
import json
from datetime import date

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
)




DEFAULT_MODEL_PATH = "Output/modelo/modelo_incendios_catboost.cbm"
DEFAULT_FEATURES_PATH = "Output/modelo/features_modelo.json"

TARGET_COL = "inicio_incendio"


DROP_COLS = ["fecha", "nombre", "provincia", TARGET_COL,  "incendio", "racha","sin_doy", "cos_doy", "anio","tmax_media_7d", "incendios_7d_estacion", "anomalia_tmax_mes", "viento_fuerte", "x_utm", "y_utm"]


REMOVE_ALL_INCEND_FEATURES = False 


def _today_local() -> pd.Timestamp:
    return pd.Timestamp(date.today())


def load_model_and_features(model_path: str, features_path: str):
    # Por si se cuela ("ruta",) como tupla:
    if isinstance(model_path, tuple) and len(model_path) == 1:
        model_path = model_path[0]
    if isinstance(features_path, tuple) and len(features_path) == 1:
        features_path = features_path[0]

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No existe el modelo en: {model_path}")
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"No existe el JSON de features en: {features_path}")

    model = CatBoostClassifier()
    model.load_model(model_path)

    with open(features_path, "r", encoding="utf-8") as f:
        feature_list = json.load(f)

    if not isinstance(feature_list, list) or not feature_list:
        raise ValueError("features_modelo.json no contiene una lista válida de features.")

    return model, feature_list


def prepare_X(df: pd.DataFrame, feature_list: list) -> pd.DataFrame:
    
    X = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")

    # Solo numéricas
    X = X.select_dtypes(include=[np.number]).copy()

    # Anti-leakage: quitar cualquier columna con 'incend' en el nombre
    if REMOVE_ALL_INCEND_FEATURES:
        cols_inc = [c for c in X.columns if "incend" in c.lower()]
        if cols_inc:
            X = X.drop(columns=cols_inc, errors="ignore")

    # Alinear orden y set de columnas
    X = X.reindex(columns=feature_list, fill_value=0)

    return X


def predict(df: pd.DataFrame, model, feature_list: list, threshold: float) -> pd.DataFrame:
    X = prepare_X(df, feature_list)
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= threshold).astype(int)

    out = df.copy()
    out["prob_incendio"] = proba
    out["pred_incendio"] = pred
    return out


def evaluate(df_labeled: pd.DataFrame, model, feature_list: list, threshold: float) -> dict:
    if TARGET_COL not in df_labeled.columns:
        raise ValueError(f"No existe la columna target '{TARGET_COL}' para evaluar.")

    y_true = df_labeled[TARGET_COL].astype(int).values
    X = prepare_X(df_labeled, feature_list)
    y_score = model.predict_proba(X)[:, 1]
    y_pred = (y_score >= threshold).astype(int)

    metrics = {}

    if len(np.unique(y_true)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_score))
        metrics["pr_auc"] = float(average_precision_score(y_true, y_score))
    else:
        metrics["roc_auc"] = None
        metrics["pr_auc"] = None

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )

    metrics.update({
        "threshold": float(threshold),
        "n": int(len(y_true)),
        "positivos": int(y_true.sum()),
        "negativos": int((y_true == 0).sum()),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "tasa_alertas_predichas": float(np.mean(y_pred)),
    })
    return metrics


def pretty_print_eval(metrics: dict) -> str:
    out = "\n====================\n"
    out += "EVALUACIÓN\n"
    out += "====================\n"
    out += f"N={metrics['n']} | Positivos={metrics['positivos']} | Negativos={metrics['negativos']}\n"
    out += f"Umbral={metrics['threshold']:.3f}\n"
    if metrics["roc_auc"] is not None:
        out += f"ROC-AUC={metrics['roc_auc']:.4f} | PR-AUC={metrics['pr_auc']:.4f}\n"
    else:
        out += "ROC-AUC/PR-AUC: No calculable (solo hay una clase en y_true).\n"

    out += f"Recall={metrics['recall']:.4f} | F1={metrics['f1']:.4f}\n"
    out += f"TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']} TP={metrics['tp']}\n"
    print(out)
    return out


def alert_summary(df_pred: pd.DataFrame, top_k: int = 15) -> str:
    if "pred_incendio" not in df_pred.columns or "prob_incendio" not in df_pred.columns:
        return ""

    alerts = df_pred[df_pred["pred_incendio"] == 1].copy()
    n_alerts = len(alerts)
    n_total = len(df_pred)

    out = "\n====================\n"
    out += "PREDICCIÓN / ALERTAS\n"
    out += "====================\n"
    out += f"Filas={n_total} | Alertas (pred_incendio=1)={n_alerts}\n"

    if n_alerts == 0:
        out += "No se predicen incendios con el umbral actual.\n"
        print(out)
        return out

    alerts = alerts.sort_values("prob_incendio", ascending=False).head(top_k)

    cols_show = []
    for c in ["fecha", "estacion", "nombre", "provincia", "prob_incendio"]:
        if c in alerts.columns:
            cols_show.append(c)

    out += "\n TOP alertas (más probables):\n"
    out += alerts[cols_show].to_string(index=False) + "\n"
    print(out)
    return out


def build_output_csv(df_pred: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve SOLO:
      fecha, estacion, nombre, provincia, pred_incendio, incendio_real

    incendio_real:
      - si existe 'inicio_incendio' -> se copia
      - si no existe -> NaN
    """
    df_out = pd.DataFrame()

    for col in ["fecha", "estacion", "nombre", "provincia"]:
        df_out[col] = df_pred[col] if col in df_pred.columns else pd.Series([pd.NA] * len(df_pred))

    df_out["pred_incendio"] = df_pred["pred_incendio"]

    if TARGET_COL in df_pred.columns:
        df_out["incendio_real"] = df_pred[TARGET_COL]
    else:
        df_out["incendio_real"] = pd.Series([pd.NA] * len(df_pred))

    return df_out


def run_pipeline(
    input_csv: str,
    model_path: str,
    features_path: str,
    output_csv: str | None,
    threshold: float,
):
    df = pd.read_csv(input_csv)

    # Parse fecha si existe
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    today = _today_local()

    model, feature_list = load_model_and_features(model_path, features_path)

    has_target = TARGET_COL in df.columns

    df_pred = predict(df, model, feature_list, threshold=threshold)
    
    txt_out = ""

    # Evaluación si procede
    did_eval = False
    if has_target:
        if "fecha" in df.columns and df["fecha"].notna().any():
            past_mask = df["fecha"] <= today
            df_past = df.loc[past_mask].copy()
            if len(df_past) > 0:
                metrics = evaluate(df_past, model, feature_list, threshold=threshold)
                txt_out += pretty_print_eval(metrics)
                did_eval = True
            else:
                print("\nNo hay filas con fecha pasada para evaluar.")
        else:
            metrics = evaluate(df, model, feature_list, threshold=threshold)
            txt_out += pretty_print_eval(metrics)
            did_eval = True

    # Alertas siempre
    txt_out += alert_summary(df_pred)
    
    # Guardar resumen en TXT
    resumen_path = "Output/resultados/resumen_prediccion.txt"
    os.makedirs(os.path.dirname(resumen_path), exist_ok=True)
    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write(txt_out)

    # Guardar salida (CSV reducido)
    if output_csv:
        os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
        df_out = build_output_csv(df_pred)
        df_out.to_csv(output_csv, index=False)
        print(f"\n Guardado CSV reducido en: {output_csv}")


def predecir():
    # Ajusta aquí tus rutas
    input_csv = "Output/Dataset/dataset_filtrado.csv"  # o dataset_filtrado_sin_info.csv
    model_path = "Output/modelo/modelo_incendios_catboost.cbm"
    features_path = "Output/modelo/features_modelo.json"
    output_csv = "Output/resultados/predicion.csv"
    threshold = 0.45

    run_pipeline(
        input_csv=input_csv,
        model_path=model_path,
        features_path=features_path,
        output_csv=output_csv,
        threshold=threshold,
    )


if __name__ == "__main__":
    predecir()