from flask import Flask, render_template, request, redirect, url_for, send_file
import subprocess
import json
import sys
import os
import threading
import webview

import scripts.run as run
    
ROOT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(ROOT_DIR, "data", "config.json")

app = Flask(__name__)

#region Redirecciñon inicial

@app.route('/')
def root():
    """Redirige a la pantalla de inicio"""
    return redirect(url_for('flk_index'))

#endregion

#region Renderizado de HTMLs

@app.route('/inicio')
def flk_index():
    """Accedemos a la pantalla principal"""
    return render_template("index.html")

@app.route('/ejecutando')
def flk_ejecutando():
    """Accedemos a la pantalla de ejecución"""
    return render_template("ejecutando.html")

@app.route('/stream_logs')
def stream_logs():
    def generate():
        process = subprocess.Popen(
            [sys.executable, '-u', '-m', 'scripts.run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=ROOT_DIR
        )
        for line in iter(process.stdout.readline, ''):
            yield f"data: {line.strip()}\n\n"
        process.stdout.close()
        process.wait()
        yield f"data: DONE\n\n"
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/registros')
def flk_registros():
    """Accedemos a la pantalla de registros"""
    txt_path = os.path.join(ROOT_DIR, "Output", "resultados", "resumen_prediccion.txt")
    resumen = ""
    fecha_registro = ""
    
    if os.path.exists(txt_path):
        import datetime
        timestamp = os.path.getmtime(txt_path)
        fecha_registro = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y a las %H:%M:%S')
        with open(txt_path, "r", encoding="utf-8") as f:
            resumen = f.read()

    return render_template("registros.html", resumen=resumen, fecha=fecha_registro)

@app.route('/descargar_prediccion')
def descargar_prediccion():
    """Descargar el archivo CSV de predicciones"""
    csv_path = os.path.join(ROOT_DIR, "Output", "resultados", "prediccion.csv")
    if not os.path.exists(csv_path):
        return "Archivo no encontrado", 404

    try:
        return send_file(csv_path, as_attachment=True, download_name="prediccion.csv")
    except TypeError:
        # Compatibilidad con versiones antiguas de Flask
        return send_file(csv_path, as_attachment=True, attachment_filename="prediccion.csv")

@app.route('/config')
def flk_config():
    """Accedemos a la pantalla de configuración"""
    return render_template("config.html")

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}, 500
            
    if request.method == 'POST':
        try:
            new_data = request.json
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
                current_data = json.load(f)
                
            # Merge values to not overwrite other fields like anio_inicio, etc.
            if "AEMET" in new_data:
                current_data["AEMET"]["api"] = new_data["AEMET"]["api"]
                
            if "EGIF" in new_data:
                egif = new_data["EGIF"]
                current_data["EGIF"]["activo"] = egif.get("activo", True)
                current_data["EGIF"]["ComunidadAutonoma"] = egif.get("ComunidadAutonoma")
                current_data["EGIF"]["Provincia"] = egif.get("Provincia")
                current_data["EGIF"]["Municipio"] = egif.get("Municipio")
                current_data["EGIF"]["ComarcaIsla"] = egif.get("ComarcaIsla")
                
            with open(CONFIG_PATH, "w", encoding="utf-8-sig") as f:
                json.dump(current_data, f, indent=4, ensure_ascii=False)
                
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}, 500

#endregion 


def start_server():
    """Arrancar el servidor Flask."""
    # debug=False y use_reloader=False son críticos cuando se usa con hilos y webview
    host = '0.0.0.0' if os.environ.get('DOCKER_ENV') else '127.0.0.1'
    app.run(host=host, port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    if os.environ.get('DOCKER_ENV'):
        start_server()
    else:
        t = threading.Thread(target=start_server, daemon=True)
        t.start()

        webview.create_window(
            'Predicción de Incendios - Panel de Control', 
            'http://127.0.0.1:5000/inicio',
            width=1024,
            height=768,
            min_size=(800, 600)
        )

        webview.start(debug=False)