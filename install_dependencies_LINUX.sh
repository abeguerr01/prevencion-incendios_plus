#!/bin/bash

# Obtener el directorio donde está el script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "===================================================="
echo "    Instalador de Dependencias Python (Linux)"
echo "===================================================="

# Buscar python3 o python
if command -v python3 >/dev/null 2>&1; then
    PYCMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYCMD="python"
else
    echo "[ERROR] Python no esta instalado. Instalalo con: sudo apt install python3"
    echo ""
    read -n 1 -s -r -p "Presione una tecla para continuar..."
    exit 1
fi

# Verificar el archivo requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "[ERROR] No se encontro el archivo requirements.txt en $DIR"
    echo ""
    read -n 1 -s -r -p "Presione una tecla para continuar..."
    exit 1
fi

echo "[+] Actualizando pip..."
$PYCMD -m pip install --upgrade pip

echo "[+] Instalando librerias desde requirements.txt..."
$PYCMD -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================================="
    echo "    [EXITO] Todas las librerias se instalaron bien."
    echo "===================================================="
else
    echo ""
    echo "[!] Hubo errores durante la instalacion."
fi

echo ""
# Mensaje solicitado
read -n 1 -s -r -p "Presione una tecla para continuar..."
echo ""
exit 0