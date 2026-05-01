@echo off
title Instalador de Dependencias Python
setlocal
pushd "%~dp0" >nul

set "PYCMD="

rem Buscar python o el lanzador py
where python >nul 2>&1 && set "PYCMD=python"
if "%PYCMD%"=="" (
    where py >nul 2>&1 && set "PYCMD=py -3"
)

if "%PYCMD%"=="" (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    goto :SALIDA
)

rem Verificamos que ahora el nombre sea el correcto
if not exist "requirements.txt" (
    echo [ERROR] No se encontro el archivo requirements.txt.
    echo Asegurate de que el nombre este bien escrito en la carpeta.
    goto :SALIDA
)

echo ====================================================
echo    Iniciando instalacion de dependencias...
echo ====================================================

echo [+] Actualizando pip...
%PYCMD% -m pip install --upgrade pip

echo [+] Instalando librerias desde requirements.txt...
%PYCMD% -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ====================================================
    echo    [EXITO] Todas las librerias se instalaron bien.
    echo ====================================================
) else (
    echo.
    echo [!] Hubo algunos errores durante la instalacion.
)

:SALIDA
echo.
echo ====================================================
echo Dale a cualquier tecla para continuar...
echo ====================================================
pause >nul
popd >nul
exit