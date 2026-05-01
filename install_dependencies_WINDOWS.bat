@echo off
REM Instalador de dependencias Python (Windows)

REM Cambiar al directorio donde está este script
cd /d "%~dp0"

echo ====================================================
echo     Instalador de Dependencias Python (Windows)
echo ====================================================

REM Detectar comando de Python
where python >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYCMD=python"
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PYCMD=python3"
    ) else (
        echo [ERROR] No se encontro Python en el PATH.
        echo Instala Python 3 y marca la opcion "Add python to PATH".
        pause
        exit /b 1
    )
)

REM Comprobar requirements.txt
if not exist "requirements.txt" (
    echo [ERROR] No se encontro el archivo requirements.txt en %cd%
    pause
    exit /b 1
)

echo [+] Actualizando pip...
%PYCMD% -m pip install --upgrade pip

echo [+] Instalando librerias desde requirements.txt...
%PYCMD% -m pip install -r requirements.txt

if %ERRORLEVEL%==0 (
    echo.
    echo ====================================================
    echo     [EXITO] Todas las librerias se instalaron bien.
    echo ====================================================
) else (
    echo.
    echo [!] Hubo errores durante la instalacion.
)

echo.
pause
exit /b 0

