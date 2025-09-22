SHELL := /bin/bash

.PHONY: \
  staging-run staging-celery staging-test-env

staging-run:
	set -a; [ -f .env.staging ] && . .env.staging; set +a; ENVIRONMENT=staging .venv/bin/python manage.py runserver 8000

staging-celery:
	set -a; [ -f .env.staging ] && . .env.staging; set +a; ENVIRONMENT=staging celery -A axi worker -l info

staging-test-env:
	bash scripts/test_all_environment.sh staging -q

