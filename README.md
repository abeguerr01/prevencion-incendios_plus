# Proyecto de predicción de riesgo de incendios

## Autores y razón del proyecto

**Autores**:
- Alejadro Beguer
- Daniel Rivas
- Pau Hernandez
- David Martinez

**Razon del proyecto**:
Este proyecto ha sido creado con la razon de participar en la primera edición de "Datathon UpData CLM"-  
Con este proyecto hemos conseguido clasificar a la fase final en donde hemos conseguido llegar 3 equipos de FP de toda la Castilla - La Mancha

---

## Detalles

### 1. Requisitos previos

- **Python 3.10+**.
- Conexión a Internet (para descargar dependencias y, si se usa, datos de AEMET).
- `git` (opcional, solo para clonar el repositorio).

Estructura mínima esperada:

- Carpeta `data/` con:
  - `data/estaciones.json`
  - `data/incendios/Incendios-2015-2025.xlsx` (u otro nombre, el script lo detecta).

### 2. Instalación de dependencias

#### 2.1. Windows

1. Abre una terminal en la carpeta del proyecto, por ejemplo:

   ```bash
   cd D:\USER\Documents\GitHub\prevencion_incendios
   ```

2. (Opcional pero recomendado) Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Ejecuta el instalador de dependencias:

   ```bash
   install_dependencies_WINDOWS.bat
   ```

Esto actualizará `pip` e instalará **todas** las librerías definidas en `requirements.txt`.

#### 2.2. Linux

1. Abre una terminal en la carpeta del proyecto:

   ```bash
   cd /ruta/a/prevencion_incendios
   ```

2. (Opcional pero recomendado) Crea y activa un entorno virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Da permisos de ejecución al script (solo la primera vez):

   ```bash
   chmod +x install_dependencies_LINUX.sh
   ```

4. Lanza el instalador:

   ```bash
   ./install_dependencies_LINUX.sh
   ```

### 3. Ejecución del pipeline completo

Con las dependencias instaladas y desde la raíz del proyecto:

```bash
python main.py
```

El proceso ejecuta, en orden:

1. **Configuración de estaciones y descarga de datos AEMET** (si está activado en `main.py`).
2. **Procesamiento de datos de incendios** (`scripts/creador_incendios_v2.py`).
3. **Creación del dataset base** (`scripts/crearDataset.py`).
4. **Aplicación de fórmulas y generación de `dataset_features.csv`**.
5. **Entrenamiento del modelo CatBoost** y guardado en:
   - `Output/modelo/modelo_incendios_catboost.cbm`
   - `Output/modelo/features_modelo.json`
6. **Filtrado por fecha** y generación de `Output/Dataset/dataset_filtrado.csv`.
7. **Predicción y análisis**, guardando las alertas en:
   - `Output/resultados/predicion.csv`

Al final verás por consola un resumen de métricas (ROC-AUC, PR-AUC, recall, etc.) y ejemplos de las fechas/estaciones con mayor probabilidad de incendio.

### 4. Notas útiles

- Si quieres **desactivar la descarga de datos de AEMET** (por ejemplo, si ya tienes los ficheros generados), puedes comentar temporalmente las llamadas correspondientes en `main.py`.
- Si cambias los ficheros de entrada (`data/incendios`, datos AEMET, etc.), simplemente vuelve a ejecutar:

  ```bash
  python main.py
  ```

  para regenerar dataset, reentrenar el modelo y obtener nuevas predicciones.
