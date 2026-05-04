from flask import Flask, render_template, request, redirect, url_for
import json
import os
import threading

import main as project_main

ROOT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(ROOT_DIR, "data", "config.json")

app = Flask(__name__)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)


@app.route("/")
def index():
    message = request.args.get("message", "")
    running = False
    thread = app.config.get("PROCESS_THREAD")
    if thread and thread.is_alive():
        running = True
    return render_template("index.html", running=running, message=message)


@app.route("/start", methods=["POST"])
def start_process():
    thread = app.config.get("PROCESS_THREAD")
    if thread and thread.is_alive():
        return redirect(url_for("index", message="El proceso ya está en ejecución."))

    worker = threading.Thread(target=project_main.main, daemon=True)
    worker.start()
    app.config["PROCESS_THREAD"] = worker
    return redirect(url_for("index", message="Proceso iniciado en segundo plano."))


@app.route("/config", methods=["GET", "POST"])
def config():
    config_data = load_config()
    message = ""

    if request.method == "POST":
        config_data["AEMET"] = {"api": request.form.get("api", "").strip()}
        egif = config_data.get("EGIF", {})
        egif["activo"] = request.form.get("activo") == "on"
        egif["anio_inicio"] = int(request.form.get("anio_inicio", egif.get("anio_inicio", 2015)))
        egif["anio_fin"] = int(request.form.get("anio_fin", egif.get("anio_fin", 2024)))
        egif["ComunidadAutonoma"] = request.form.get("ComunidadAutonoma", "").strip() or None
        egif["Provincia"] = request.form.get("Provincia", "").strip() or None
        egif["Municipio"] = request.form.get("Municipio", "").strip() or None
        egif["ComarcaIsla"] = request.form.get("ComarcaIsla", "").strip() or None
        egif["borrarDirectorio"] = request.form.get("borrarDirectorio") == "on"
        egif["nameZip"] = request.form.get("nameZip", egif.get("nameZip", "Xlsx")).strip()
        egif["nameCSV"] = request.form.get("nameCSV", egif.get("nameCSV", "fichero")).strip()
        egif["nameJson"] = request.form.get("nameJson", egif.get("nameJson", "archivo")).strip()
        config_data["EGIF"] = egif
        save_config(config_data)
        message = "Configuración guardada correctamente."

    return render_template("config.html", config=config_data, message=message)

@app.route("/results")
def results():
    import pandas as pd
    import os
    results_path = os.path.join(ROOT_DIR, "Output", "resultados", "predicion.csv")
    if os.path.exists(results_path):
        try:
            df = pd.read_csv(results_path)
            # Ordenar para mostrar primero los que tienen mayor predicción o simplemente coger las primeras filas
            if "pred_incendio" in df.columns:
                df = df.sort_values(by="pred_incendio", ascending=False)
            table_html = df.head(100).to_html(classes="styled-table", index=False)
            return render_template("results.html", table_html=table_html, exists=True)
        except Exception as e:
            return render_template("results.html", message=f"Error leyendo resultados: {str(e)}", exists=False)
    else:
        return render_template("results.html", message="El archivo de predicción aún no ha sido generado.", exists=False)

if __name__ == "__main__":
    import threading
    import webview
    
    def start_server():
        # Iniciamos la app de Flask en el puerto 5000 (usando 127.0.0.1)
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    # Creamos un hilo para ejecutar el servidor Flask en segundo plano
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Creamos la ventana con pywebview apuntando a la URL local
    webview.create_window(
        'Prevención de Incendios - Panel de Control', 
        'http://127.0.0.1:5000/',
        width=1024,
        height=768,
        min_size=(800, 600)
    )
    
    # Iniciamos pywebview
    webview.start(debug=False)
