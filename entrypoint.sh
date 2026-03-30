#!/bin/bash

# Aborta se der erro
set -e

echo "Aguardando Banco de Dados..."
# Aqui poderia ter um script pra esperar a porta do banco, mas se for supabase cloud estará sempre on
# ou em docker local podemos usar wait-for-it

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando o servidor gunicorn para AWS..."
exec gunicorn ordo_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
