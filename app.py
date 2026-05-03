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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
