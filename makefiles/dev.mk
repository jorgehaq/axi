SHELL := /bin/bash

.PHONY: \
  dev-install-deps dev-deploy dev-migrate dev-logs dev-sql-proxy dev-redis-cli dev-test-env dev-run dev-celery dev-test-real

include .env.dev
export

# Local development with dev config
dev-install-deps:
	.venv/bin/python -m pip install -r requirements.txt

dev-run:
	set -a; [ -f .env.dev ] && . .env.dev; set +a; ENVIRONMENT=dev .venv/bin/python manage.py runserver 8000

dev-celery:
	set -a; [ -f .env.dev ] && . .env.dev; set +a; ENVIRONMENT=dev celery -A axi worker -l info

# GCP dev deployment
dev-deploy:
	gcloud run deploy axi-dev-api \
		--source . \
		--region us-central1 \
		--platform managed \
		--allow-unauthenticated

dev-migrate:
	gcloud run jobs execute migrate-dev \
		--region us-central1 \
		--wait

dev-logs:
	gcloud run services logs tail axi-dev-api --region us-central1

# GCP dev utilities
dev-sql-proxy:
	gcloud sql connect axi-dev-db --user=axi_dev

dev-redis-cli:
	@echo "Redis IP: $(shell gcloud redis instances describe axi-dev-redis --region=us-central1 --format='value(host)')"
	@echo "Use: redis-cli -h <IP> -p 6379"

# Tests
dev-test-env:
	bash scripts/test_all_environment.sh dev

dev-test-real:
	bash scripts/test_dev_real.sh
