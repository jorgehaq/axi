```bash
#!/usr/bin/env bash
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Leer el puerto que Cloud Run nos dice (8080)
# Si no existe la variable, usar 8000 (para desarrollo local)
PORT=${PORT:-8000}

# Gunicorn para producción
exec gunicorn analytics_api.wsgi:application \
  --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-3} --timeout 120