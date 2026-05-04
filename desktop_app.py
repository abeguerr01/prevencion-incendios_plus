import webview
import threading
from app import app
import sys

def start_server():
    # Iniciamos la app de Flask en el puerto 5000
    app.run(host='127.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
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
    webview.start(debug=True)
