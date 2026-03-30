#!/bin/bash

# Aborta se der erro
set -e

echo "Aguardando Banco de Dados..."
# Em produção o banco já está disponível (Render PostgreSQL); localmente use wait-for-it se necessário
# ou em docker local podemos usar wait-for-it

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando o servidor gunicorn..."
exec gunicorn ordo_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
