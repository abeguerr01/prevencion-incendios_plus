@echo off
echo Verificando si Python está instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado. Instalando Python...
    winget install --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo Error al instalar Python. Instálalo manualmente desde https://www.python.org/
        pause
        exit /b 1
    )
    echo Python instalado. Reinicia el script si es necesario.
    pause
    exit /b 0
) else (
    echo Python ya está instalado.
)

echo Instalando requerimientos desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error al instalar requerimientos.
    pause
    exit /b 1
)

echo Ejecutando app.py...
python app.py