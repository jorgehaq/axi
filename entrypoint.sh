#!/usr/bin/env bash
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Gunicorn para producción
exec gunicorn analytics_api.wsgi:application \
  --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-3} --timeout 120