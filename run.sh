#!/bin/bash

# Script para ejecutar main.py con sudo (para poder usar el puerto 80)
clear
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    PYTHON=".venv/bin/python3"
else
    echo "No existe entorno virtual"
    exit 1
fi

sudo "$PYTHON" main.py
