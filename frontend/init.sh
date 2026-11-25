#!/usr/bin/env bash
# Script de instalación de dependencias requerido por la cátedra para Frontend
set -e

echo "=== Instalando dependencias de Frontend Cine Paradiso ==="
pip install -r "$(dirname "$0")/requirements.txt"
echo "=== Instalación finalizada con éxito ==="

