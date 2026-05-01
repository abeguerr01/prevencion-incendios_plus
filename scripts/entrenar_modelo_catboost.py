import os
import json
import numpy as np
import pandas as pd

from catboost import CatBoostClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

# CONFIG / RUTAS

DATA_PATH = "Output/Dataset/dataset_features.csv"
OUT_DIR = "Output/modelo"
os.makedirs(OUT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(OUT_DIR, "modelo_incendios_catboost.cbm")
FEATURES_PATH = os.path.join(OUT_DIR, "features_modelo.json")

MAX_DATE = "2022-12-31"

TRAIN_FRAC = 0.70
VALID_FRAC = 0.15

REMOVE_ALL_INCEND_FEATURES = False

# FEATURES / TARGET
TARGET = "inicio_incendio"

# Anti-leakage
DROP_COLS = ["fecha", "nombre", "provincia", TARGET, "incendio", "racha", "sin_doy", "cos_doy", "anio", "tmax_media_7d", "incendios_7d_estacion", "anomalia_tmax_mes", "viento_fuerte", "x_utm", "y_utm"]

def make_Xy(d: pd.DataFrame):
    X = d.drop(columns=[c for c in DROP_COLS if c in d.columns], errors="ignore")
    y = d[TARGET].astype(int)

    # Solo numéricas (CatBoost puede con categóricas, pero aquí ya las quitamos)
    X = X.select_dtypes(include=[np.number]).copy()

    if REMOVE_ALL_INCEND_FEATURES:
        cols_inc = [c for c in X.columns if "incend" in c.lower()]
        if cols_inc:
            print("Quitando columnas con 'incend':", cols_inc)
            X = X.drop(columns=cols_inc)

    return X, y

def print_metrics(name, y_true, y_prob, y_pred):
    print(f"\n=== {name} ===")
    print("ROC-AUC:", roc_auc_score(y_true, y_prob))
    print("PR-AUC :", average_precision_score(y_true, y_prob))

    acc = accuracy_score(y_true, y_pred)
    print(f"Accuracy (porcentaje total de acierto): {acc:.4f} ({acc*100:.2f}%)")

    # confusion_matrix devuelve [[TN, FP],
    #                           [FN, TP]]
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    # % acierto cuando HAY incendio = Recall/TPR = TP/(TP+FN)
    recall_pos = tp / (tp + fn) if (tp + fn) > 0 else float("nan")

    # % acierto cuando NO hay incendio = Especificidad/TNR = TN/(TN+FP)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else float("nan")

    # Extra útil: precisión cuando predice incendio = TP/(TP+FP)
    precision_pos = tp / (tp + fp) if (tp + fp) > 0 else float("nan")

    print(f"% acierta cuando HAY incendio (Recall/TPR): {recall_pos:.4f} ({recall_pos*100:.2f}%)")
    print(f"% acierta cuando NO hay incendio (Especificidad/TNR): {specificity:.4f} ({specificity*100:.2f}%)")

def run():
    # 1) CARGAR DATASET

    df = pd.read_csv(DATA_PATH, parse_dates=["fecha"])
    df = df[df["fecha"] <= MAX_DATE].copy()
    df = df.sort_values("fecha").reset_index(drop=True)

    # 2) SPLIT ESTRATIFICADO 70/15/15 (asegurando positivos en cada partición)
    #    Primero separamos TEST, luego partimos TRAIN+VALID.
    train_valid, test = train_test_split(
        df,
        test_size=1 - (TRAIN_FRAC + VALID_FRAC),  # ~0.15
        stratify=df[TARGET],
        random_state=42,
    )

    # De lo que queda (TRAIN+VALID), sacamos VALID manteniendo el 15% total aprox.
    valid_size_rel = VALID_FRAC / (TRAIN_FRAC + VALID_FRAC)
    train, valid = train_test_split(
        train_valid,
        test_size=valid_size_rel,
        stratify=train_valid[TARGET],
        random_state=42,
    )

    print("Rango TRAIN:", train["fecha"].min(), "->", train["fecha"].max())
    print("Rango VALID:", valid["fecha"].min(), "->", valid["fecha"].max())
    print("Rango TEST :", test["fecha"].min(),  "->", test["fecha"].max())

    print("Train positives:", train["inicio_incendio"].mean())
    print("Valid positives:", valid["inicio_incendio"].mean())
    print("Test positives :", test["inicio_incendio"].mean())

    # Nº de positivos por partición
    train_pos = int(train["inicio_incendio"].sum())
    valid_pos = int(valid["inicio_incendio"].sum())
    test_pos  = int(test["inicio_incendio"].sum())

    # Para poder entrenar y evaluar necesitamos al menos algo de señal
    if train_pos == 0 or test_pos == 0:
        raise ValueError(
            "Train o Test no tienen ejemplos positivos. Revisa MAX_DATE, "
            "la construcción del dataset o los porcentajes de split."
        )

    has_valid_pos = valid_pos > 0
    if not has_valid_pos:
        print(
            "\n[AVISO] La partición de VALIDACIÓN no contiene positivos "
            "(solo clase 0). Se entrenará sin usar VALID como eval_set y "
            "no se reportarán métricas de VALID."
        )

    # FEATURES / TARGET.

    X_train, y_train = make_Xy(train)
    X_valid, y_valid = make_Xy(valid)
    X_test,  y_test  = make_Xy(test)

    # Alinear columnas por seguridad
    X_valid = X_valid.reindex(columns=X_train.columns, fill_value=0)
    X_test  = X_test.reindex(columns=X_train.columns, fill_value=0)

    print("Nº features:", X_train.shape[1])

    # Guardar lista de features (orden exacto)
    with open(FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(list(X_train.columns), f, ensure_ascii=False, indent=2)


    # 4) CLASS WEIGHTS

    pos = int(y_train.sum())
    neg = int((y_train == 0).sum())
    scale_pos_weight = float(neg / max(pos, 1))
    class_weights = [1.0, scale_pos_weight]

    print("scale_pos_weight =", scale_pos_weight)
    print("class_weights =", class_weights)


    # 5) ENTRENAR CATBOOST

    model = CatBoostClassifier(
        iterations=2000,
        learning_rate=0.03,
        depth=6,
        loss_function="Logloss",
        eval_metric="AUC",
        class_weights=class_weights,
        random_seed=42,
        verbose=200
    )

    # Si VALID no tiene positivos, evitamos usarlo como conjunto de validación
    # para el early stopping y simplemente entrenamos sobre TRAIN.
    if has_valid_pos:
        model.fit(
            X_train, y_train,
            eval_set=(X_valid, y_valid),
            use_best_model=True
        )
    else:
        model.fit(X_train, y_train)


    # 6) EVALUAR

    pred_test  = model.predict_proba(X_test)[:, 1]

    THRESH = 0.45  
    yhat_test  = (pred_test  >= THRESH).astype(int)



    if has_valid_pos:
        pred_valid = model.predict_proba(X_valid)[:, 1]
        yhat_valid = (pred_valid >= THRESH).astype(int)
        print_metrics("VALID", y_valid, pred_valid, yhat_valid)
    else:
        print("\n=== VALID ===")
        print("No se evalúa VALID porque no contiene ejemplos positivos (solo clase 0).")

    print_metrics("TEST",  y_test,  pred_test,  yhat_test)


    # 7) GUARDAR MODELO

    model.save_model(MODEL_PATH)
    print(f"\n Modelo guardado en: {MODEL_PATH}")
    print(f"Features guardadas en: {FEATURES_PATH}")


    # 8) TOP FEATURES

    importances = pd.Series(model.get_feature_importance(), index=X_train.columns).sort_values(ascending=False)
    print("\nTop 20 features:")
    print(importances.head(20).to_string())

if __name__ == "__main__":
    run()