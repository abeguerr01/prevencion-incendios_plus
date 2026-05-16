import os
import sys
import shutil

def setup_and_chdir():
    """
    Configura el directorio de datos en AppData, copiando la estructura inicial
    si es la primera vez que se ejecuta. Luego cambia el directorio de trabajo (CWD)
    a AppData para que todas las rutas relativas apunten allí.
    Retorna (EXE_DIR, APPDATA_DIR).
    """
    # 1. Determinar el directorio base (EXE si es PyInstaller, o la raíz del proyecto)
    if getattr(sys, 'frozen', False):
        # Si está congelado por PyInstaller
        base_dir = sys._MEIPASS
    else:
        # Asumiendo que este script está en la carpeta 'scripts'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    # 2. Determinar la carpeta AppData
    if os.name == 'nt':
        appdata_base = os.getenv('APPDATA')
    else:
        # Fallback para Linux/macOS
        appdata_base = os.path.join(os.path.expanduser('~'), '.config')
        
    appdata_dir = os.path.join(appdata_base, 'prediccion_incendios-plus')
    
    # 3. Crear el directorio AppData si no existe
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)
        
    # 4. Copiar carpetas base si no existen en AppData
    for folder in ['data', 'Output', 'catboost_info']:
        src = os.path.join(base_dir, folder)
        dst = os.path.join(appdata_dir, folder)
        
        if os.path.exists(src) and not os.path.exists(dst):
            # Si es un directorio, copiamos el árbol completo
            if os.path.isdir(src):
                shutil.copytree(src, dst)
        elif not os.path.exists(dst):
            # Si no existe en origen ni destino, creamos la carpeta vacía para evitar errores
            os.makedirs(dst)
            
    # 5. Cambiar el directorio de trabajo actual
    os.chdir(appdata_dir)
    
    return base_dir, appdata_dir
