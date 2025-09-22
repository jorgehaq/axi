**Language:** English | [Español](./README.es.md)

# AXI - Analytics eXchange Interface

CSV data analysis API built with Django REST Framework. Upload CSV files and execute basic analytics with JWT authentication.

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework 3.15
- **Auth**: JWT (djangorestframework-simplejwt)
- **Analytics**: pandas + pyarrow
- **DB**: PostgreSQL (prod) / SQLite (dev)
- **Storage**: Google Cloud Storage (prod) / Local (dev)
- **Background**: Celery + Redis
- **Deploy**: Docker, Cloud Run, Cloud SQL
- **Docs**: drf-spectacular (Swagger)

## Architecture

```
axi/
├── axi/                    # Django configuration
├── apps/
│   ├── auth/              # OAuth2 authentication
│   ├── datasets/          # Core datasets API
│   └── analytics/         # Advanced analytics
├── scripts/               # Testing and utilities
└── makefiles/             # Environment commands
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Database
make -f makefiles/local.mk local-postgres-up
make -f makefiles/local.mk local-migrations

# Server
make -f makefiles/local.mk local-django
```

## API Endpoints

### Authentication
- `POST /api/token/` - Get JWT tokens
- `POST /api/token/refresh/` - Refresh token
- `GET /api/me/` - Current user

### Datasets
- `POST /api/v1/datasets/upload` - Upload CSV
- `GET /api/v1/datasets/{id}/preview` - First 5 rows
- `GET /api/v1/datasets/{id}/summary` - Numeric statistics
- `GET /api/v1/datasets/{id}/rows` - Rows with filters/pagination
- `GET /api/v1/datasets/{id}/correlation` - Correlations
- `GET /api/v1/datasets/{id}/trend` - Time trends
- `GET /api/v1/datasets/{id}/download-url/` - Download URL

### Filters and Pagination
```
/datasets/1/rows?f=country,eq,CO&sort=-amount&page=1&page_size=20
```

Operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `in`

## Environments

### Local
```bash
# Docker services (Redis, MinIO, Flower)
make -f makefiles/local.mk local-services

# Local PostgreSQL
make -f makefiles/local.mk local-postgres-up

# Tests
make -f makefiles/local.mk local-test-env
```

### Dev (GCP)
```bash
# Auto deploy via GitHub Actions (branch: dev)
git push origin dev

# Manual tests
make -f makefiles/dev.mk dev-test-real
```

CI/CD secrets for dev/prod are documented in `docs/ci-secrets.md`.

### Staging/Production
```bash
# Deploy via GitHub Actions (branch: main)
git push origin main
```

CI/CD secrets required for production are listed in `docs/ci-secrets.md`.

## Environment Variables

**Local** (`.env.local`):
```
ENVIRONMENT=local
DEBUG=true
DB_ENGINE=postgres
DB_HOST=127.0.0.1
USE_GCS=false
```

**Dev** (`.env.dev`):
```
ENVIRONMENT=dev
DB_ENGINE=postgres
DB_HOST=/cloudsql/PROJECT:REGION:INSTANCE
USE_GCS=true
GS_BUCKET_NAME=axi-dev-bucket
```

## Testing

```bash
# All environments
bash scripts/test_all_environment.sh local
bash scripts/test_all_environment.sh dev

# Specific tests
bash scripts/test_oauth2_integration.sh local
bash scripts/test_missing_endpoints.sh local
```

## GCP Configuration

1. **Cloud SQL**: PostgreSQL instance
2. **Cloud Storage**: File bucket
3. **Redis**: Memorystore for Celery
4. **Artifact Registry**: Docker images
5. **Cloud Run**: HTTP services

## Background Jobs

```bash
# Local development
make -f makefiles/local.mk local-services  # Redis + Celery
.venv/bin/python -m celery -A axi worker -l info

# Monitoring
curl localhost:5555  # Flower UI
```

## Data Structure

**Upload**:
```json
{
  "message": "File uploaded successfully",
  "id": 123
}
```

**Filtered rows**:
```json
{
  "page": 1,
  "page_size": 50,
  "total": 150,
  "results": [{"col1": "val1", "col2": "val2"}]
}
```

**Errors**:
```json
{
  "error": {
    "code": "bad_request",
    "message": "Missing columns: ['date']",
    "details": {}
  }
}
```

## Development

```bash
# Dependencies
make -f makefiles/local.mk local-install-deps

# Database
make -f makefiles/local.mk local-migrations

# Django server
make -f makefiles/local.mk local-django

# Full tests
make -f makefiles/local.mk local-test-env
```

## API Documentation

- Swagger: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Schema: `http://localhost:8000/api/schema/`
# Test deploy Mon Sep 22 04:41:03 UTC 2025
