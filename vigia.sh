#!/bin/bash
# 1. Navegar a la carpeta del proyecto
cd /Users/d.s/Documents/rss
# 2. Activar tu entorno virtual
source venv/bin/activate
# 3. Ejecutar la ingesta y guardar rastro en un log
echo "--- Ejecución: $(date) ---" >> vigia_log.txt
python3 motor_ingesta.py >> vigia_log.txt 2>&1
