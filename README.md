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

## Instalación

Para instrucciones de instalación, consulta el archivo [setup/README.md](setup/README.md).

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