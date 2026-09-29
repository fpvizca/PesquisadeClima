#!/usr/bin/env bash
# ============================================
# Pesquisa de Clima Vizca - Inicializacao (Linux)
# ============================================
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Arquivo .env criado a partir de .env.example"
    echo "IMPORTANTE: defina o SECRET_KEY antes de usar em producao."
fi

PYTHON="${PYTHON:-python3}"
VENV=".venv"

if [ ! -d "$VENV" ]; then
    echo "Criando ambiente virtual..."
    $PYTHON -m venv "$VENV"
    "$VENV/bin/pip" install --upgrade pip
    "$VENV/bin/pip" install -r requirements.txt
fi

echo "Aplicando migracoes no banco..."
"$VENV/bin/python" migrar.py

if [ "${FLASK_DEBUG:-false}" = "true" ]; then
    echo "Iniciando em modo debug..."
    exec "$VENV/bin/python" app.py
fi

PORT="${PORT:-5005}"
WORKERS="${WORKERS:-4}"
echo "Iniciando gunicorn na porta $PORT com $WORKERS workers..."
exec "$VENV/bin/gunicorn" \
    --bind "0.0.0.0:$PORT" \
    --workers "$WORKERS" \
    --timeout 180 \
    --access-logfile - \
    --error-logfile - \
    app:app
