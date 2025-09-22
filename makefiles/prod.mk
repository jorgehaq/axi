SHELL := /bin/bash

.PHONY: \
  prod-run prod-celery prod-test-env

prod-run:
	set -a; [ -f .env.prod ] && . .env.prod; set +a; ENVIRONMENT=prod .venv/bin/python manage.py runserver 8000

prod-celery:
	set -a; [ -f .env.prod ] && . .env.prod; set +a; ENVIRONMENT=prod celery -A axi worker -l info

prod-test-env:
	bash scripts/test_all_environment.sh prod -q

