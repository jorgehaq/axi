SHELL := /bin/bash

.PHONY: \
  dev-install-deps dev-run dev-celery dev-test-env

# Export environment from .env.dev for each command
dev-install-deps:
	.venv/bin/python -m pip install -r requirements.txt

dev-run:
	set -a; [ -f .env.dev ] && . .env.dev; set +a; ENVIRONMENT=dev .venv/bin/python manage.py runserver 8000

dev-celery:
	set -a; [ -f .env.dev ] && . .env.dev; set +a; ENVIRONMENT=dev celery -A axi worker -l info

dev-test-env:
	bash scripts/test_all_environment.sh dev -q

