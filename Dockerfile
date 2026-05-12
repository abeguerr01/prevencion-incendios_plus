FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar que la salida estándar se envíe directamente al terminal (útil para logs en Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias (por ejemplo, para compilar algunos paquetes si fuera necesario)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Variable de entorno para indicar a app.py que estamos en Docker
ENV DOCKER_ENV=1

# Exponer el puerto de Flask
EXPOSE 5000

# Comando por defecto
CMD ["python", "app.py"]
