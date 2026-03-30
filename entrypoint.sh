#!/bin/bash

# Aborta se der erro
set -e

echo "Aguardando Banco de Dados..."
# O container web só sobe após o db passar no health check (pg_isready) via docker-compose.prod.yml

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando o servidor gunicorn..."
exec gunicorn ordo_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
