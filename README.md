# Proyecto de predicción de riesgo de incendios

## Autores y razón del proyecto

**Autor**: `Alejadro Beguer Ruiz`

**Razón del proyecto**:
Este proyecto ha sido modificado a partir del proyecto ["prediccion-incendios"](https://github.com/abeguerr01/prediccion_incendios), en el cual he participado yo mismo, con la razon de mejorarlo y presentarlo como trabajo de fin de grado del grado superior de desarrollo de aplicaciones multiplataforma. La principal mejora añadida en esta versión es una interfaz gráfica que facilita la configuración y el uso del análisis.

## Tecnologías usadas

- Python 3.10+
- Flask para la aplicación web
- pywebview para la interfaz de escritorio
- pandas, openpyxl, requests para procesamiento y lectura de datos
- scikit-learn y CatBoost para entrenamiento y predicción
- LightGBM, pyproj para cálculos geoespaciales y análisis

## Qué hace el proyecto

Esta aplicación procesa datos meteorológicos y de incendios para generar un dataset, entrenar un modelo de CatBoost y realizar predicciones de riesgo de incendios. Incluye una interfaz web local para:

- configurar parámetros de descarga de datos
- iniciar el proceso de análisis
- visualizar registros y resultados
- descargar predicciones en CSV

## Requisitos previos

- Python 3.10 o superior (si no usas Docker)
- Docker y Docker Compose (opcional, para despliegue en contenedor)
- Conexión a Internet para instalar dependencias y, opcionalmente, descargar datos AEMET
- Carpeta `data/` con los ficheros de entrada necesarios

## Instalación de dependencias

### Windows

1. Abre PowerShell o CMD en la raíz del proyecto.
2. (Opcional) Crea y activa un entorno virtual:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Ejecuta el instalador de dependencias:

   ```powershell
   install_dependencies_WINDOWS.bat
   ```

### Linux

1. Abre una terminal en la raíz del proyecto.
2. (Opcional) Crea y activa un entorno virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Da permisos al instalador (solo la primera vez):

   ```bash
   chmod +x install_dependencies_LINUX.sh
   ```

4. Ejecuta el instalador:

   ```bash
   ./install_dependencies_LINUX.sh
   ```

### Instalación manual

Si prefieres instalar manualmente las dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Uso

### Ejecutar con Docker Compose

Si tienes Docker instalado, puedes arrancar la aplicación de forma muy sencilla sin necesidad de instalar dependencias locales:

```bash
docker-compose up -d --build
```

Una vez levantado el contenedor, podrás acceder a la interfaz desde cualquier navegador web en [http://localhost:5000](http://localhost:5000).
Tus resultados y configuraciones se guardarán automáticamente en tu equipo gracias a los volúmenes de Docker.

Para detener la ejecución, utiliza:

```bash
docker-compose down
```

### Ejecutar la aplicación localmente

Desde la raíz del proyecto:

```bash
python app.py
```

Esto iniciará el servidor Flask y abrirá la interfaz de usuario.

### Ejecutar el pipeline completo de datos y modelo

El pipeline principal se puede ejecutar con:

```bash
python -m scripts.run
```

### Resultados generados

- `Output/modelo/modelo_incendios_catboost.cbm`
- `Output/modelo/features_modelo.json`
- `Output/Dataset/dataset_filtrado.csv`
- `Output/resultados/prediccion.csv`
- `Output/resultados/resumen_prediccion.txt`

## Estructura del proyecto

- `app.py` - servidor Flask y arranque del frontend
- `requirements.txt` - dependencias Python
- `data/` - datos de entrada, configuración y archivos AEMET
- `scripts/` - módulos que generan dataset, entrenan el modelo y ejecutan predicciones
- `Output/` - resultados y archivos generados
- `templates/` - vistas HTML de la aplicación web
- `static/` - recursos de estilo CSS

## Notas importantes

- Asegúrate de tener los datos de entrada en `data/` antes de ejecutar el pipeline.
- La descarga de datos AEMET se controla desde `data/config.json`.
- Si ya tienes los datos descargados, puedes desactivar la descarga en el pipeline para acelerar la ejecución.

## Licencia

Incluye aquí la licencia del proyecto si tienes una definida.