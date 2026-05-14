#!/bin/bash
echo "Verificando si Python está instalado..."
if ! command -v python3 &> /dev/null; then
    echo "Python no está instalado. Instalando Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip
    if [ $? -ne 0 ]; then
        echo "Error al instalar Python. Instálalo manualmente."
        exit 1
    fi
    echo "Python instalado."
else
    echo "Python ya está instalado."
fi

echo "Instalando requerimientos desde requirements.txt..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error al instalar requerimientos."
    exit 1
fi

echo "Ejecutando app.py..."
python3 app.py