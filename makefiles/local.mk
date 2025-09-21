SHELL := /bin/bash

.PHONY: \
  local-services local-install-deps local-django local-celery local-flower local-redis local-postgres-up local-test-env

include .env.local
export


# requirements
local-install-deps:
	.venv/bin/python -m pip install -r requirements.txt


# docker 
local-services:
	docker compose -f docker/docker-compose.local.yml up -d

local-celery:
	docker compose -f docker/docker-compose.local.yml logs -f celery

local-flower:
	docker compose -f docker/docker-compose.local.yml logs -f flower

local-redis:
	docker compose -f docker/docker-compose.local.yml logs -f redis


# postgres
local-postgres-up:
	bash scripts/local/postgres.sh up

local-postgres-down:
	bash scripts/local/postgres.sh down

local-postgres-status:
	bash scripts/local/postgres.sh status

# django

local-migrations:
	.venv/bin/python manage.py makemigrations
	.venv/bin/python manage.py migrate

local-django:
	.venv/bin/python manage.py runserver 8000

# tests
local-test-env:
	bash scripts/test_all_environment.sh local
