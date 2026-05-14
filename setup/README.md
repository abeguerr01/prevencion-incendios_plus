# Instalación del Proyecto de Predicción de Riesgo de Incendios

Este documento explica cómo instalar y ejecutar el proyecto. Hay dos métodos principales: usando Docker (recomendado para simplicidad) o instalación manual (compilando/configurando el código tú mismo).

## Método 1: Usando Docker

Este método utiliza Docker Compose para ejecutar la aplicación en un contenedor, sin necesidad de instalar dependencias locales.

### Requisitos previos
- Docker instalado en tu sistema.
- Docker Compose instalado.

### Pasos
1. Asegúrate de tener Docker y Docker Compose instalados.
2. Ejecuta el script correspondiente a tu sistema operativo desde la carpeta `setup/`:
   - **Windows**: `run_docker_compose_windows.bat`
   - **Linux**: `run_docker_compose_linux.sh`

Estos scripts ejecutan `docker-compose up` para iniciar los servicios definidos en `docker-compose.yml`.

Una vez ejecutado, accede a la aplicación en [http://localhost:5000](http://localhost:5000).

Para detener: ejecuta `docker-compose down` en la terminal.

## Método 2: Instalación Normal (Compilando/Configurando el Código Tú Mismo)

Este método instala Python y las dependencias manualmente en tu sistema local.

### Requisitos previos
- Conexión a Internet para descargar dependencias.
- Permisos de administrador (para instalar Python si no está presente).

### Pasos
1. Ejecuta el script correspondiente a tu sistema operativo desde la carpeta `setup/`:
   - **Windows**: `install_and_run.bat`
   - **Linux**: `install_and_run_linux.sh`

Estos scripts:
- Verifican si Python está instalado y lo instalan si no (en Windows usa winget, en Linux usa apt).
- Instalan las dependencias desde `requirements.txt`.
- Ejecutan `app.py` para iniciar la aplicación.

Si ya tienes Python y las dependencias instaladas, los scripts solo ejecutarán `app.py`.

### Instalación Manual Alternativa
Si prefieres hacerlo manualmente:
- Instala Python 3.10+.
- Crea un entorno virtual (opcional): `python -m venv .venv` y actívalo.
- Instala dependencias: `pip install -r requirements.txt`.
- Ejecuta: `python app.py`.

## Notas
- Asegúrate de tener los datos de entrada en `data/` antes de ejecutar.
- Para más detalles técnicos, consulta el README principal.