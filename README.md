**Language:** English | [Español](./README.es.md)

# Analytics API — KISS CSV Analytics (Django + DRF + JWT)

Simple, comprehensible, and production-ready(ish) analytics API for CSV files. Built step-by-step (KISS) to showcase clean architecture, tests, and a Cloud Run deploy path.

## Table of Contents

- [Overview](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#overview)
    
- [Features](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#features)
    
- [Stack](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#stack)
    
- [Project Structure](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#project-structure)
    
- [Getting Started (Local)](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#getting-started-local)
    
- [Docker (PostgreSQL + App)](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#docker-postgresql--app)
    
- [Configuration](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#configuration)
    
- [API](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#api)
    
    - [Auth (JWT)](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#auth-jwt)
        
    - [Core Endpoints](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#core-endpoints)
        
    - [Filters, Sorting & Pagination](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#filters-sorting--pagination)
        
    - [Errors](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#errors)
        
- [Testing](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#testing)
    
- [Deployment (GCP Cloud Run + Cloud SQL)](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#deployment-gcp-cloud-run--cloud-sql)
    
- [CI/CD (GitHub Actions)](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#cicd-github-actions)
    
- [Roadmap & Phases](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#roadmap--phases)
    
- [Troubleshooting](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#troubleshooting)
    
- [License](https://chatgpt.com/g/g-p-6897c134da5481918061f0f4f562300b-1-axis-v2-final-linkedin/c/6897c224-006c-8327-bd00-6923a009040d#license)
    

---

## Overview

This API lets authenticated users upload CSVs and run **basic analytics**:

- preview first rows,
    
- numeric summaries (count/mean/std),
    
- filtered/paginated row listing,
    
- simple correlations,
    
- date trends (daily/weekly/monthly).
    

Designed to be **easy to reason about** and **incrementally upgradeable**.

## Features

- Django 5 + DRF 3.15
    
- JWT (access/refresh) with owner-only permissions
    
- CSV analytics via pandas
    
- Swagger UI (`/api/docs/`) powered by drf-spectacular
    
- Consistent error shape + basic logging
    
- Dockerized app + Postgres with `docker-compose`
    
- Cloud Run ready (gunicorn entrypoint)
    

## Stack

- **Backend**: Django, Django REST Framework
    
- **Auth**: `djangorestframework-simplejwt`
    
- **Docs**: `drf-spectacular`
    
- **Analytics**: pandas (+ pyarrow backend)
    
- **DB**: SQLite (dev) → PostgreSQL (prod)
    
- **Deploy**: Docker, Cloud Run, Cloud SQL
    
- **CI/CD**: GitHub Actions (optional)
    

## Project Structure

```
analytics_api/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── manage.py
├── requirements.txt
├── .env.example
├── analytics_api/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── core/
│   ├── admin.py
│   ├── models.py          # Token removed in F4; JWT now
│   ├── services.py        # CSV read, filters, sort, pagination, analytics
│   ├── serializers.py     # Input validation for query params
│   ├── permissions.py     # Owner-only access
│   ├── errors.py          # DRF exception handler
│   ├── views.py           # DRF API views
│   ├── urls.py
│   └── tests.py
└── media/
```

## Getting Started (Local)

Requirements: Python 3.11+, pip, virtualenv.

```bash
git clone <your-repo-url> && cd analytics_api
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Migrate and run (SQLite by default)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit:

- Health: `http://127.0.0.1:8000/health/`
    
- Docs: `http://127.0.0.1:8000/api/docs/`
    

## Docker (PostgreSQL + App)

Local dev with Postgres:

```bash
docker compose up --build
# App:     http://127.0.0.1:8000
# Admin:   http://127.0.0.1:8000/admin
# Docs:    http://127.0.0.1:8000/api/docs/
```

Create admin inside the container:

```bash
docker compose exec web python manage.py createsuperuser
```

## Configuration

Environment variables (see `.env.example` / `.env.gcp.example`):

```
DJANGO_DEBUG=true|false
SECRET_KEY=<django-secret>

# DB: sqlite (default) or postgres
DB_ENGINE=sqlite|postgres
DB_NAME=analytics
DB_USER=analytics
DB_PASSWORD=change-me
DB_HOST=db                # or /cloudsql/PROJECT:REGION:INSTANCE (GCP)
DB_PORT=5432

ALLOWED_HOSTS=*
LOG_LEVEL=INFO
WEB_CONCURRENCY=3         # gunicorn workers (prod)
```

## API

### Auth (JWT)

Obtain tokens:

```
POST /api/token/
{
  "username": "admin",
  "password": "******"
}
→ { "access": "...", "refresh": "..." }
```

Refresh:

```
POST /api/token/refresh/
{ "refresh": "<refresh>" }
→ { "access": "..." }
```

Current user:

```
GET /api/me/      # Authorization: Bearer <access>
→ { "id": 1, "username": "admin", "email": "..." }
```

### Core Endpoints

All require `Authorization: Bearer <access>` except `/health/`.

- `POST /upload` — multipart form, field `file` (CSV).  
    → `{ "message": "File uploaded successfully", "id": <int> }`
    
- `GET /data/{id}/preview` — first 5 rows.  
    → `{ "id": 1, "rows": [ {...}, ... ] }`
    
- `GET /data/{id}/summary` — numeric `count/mean/std`.  
    → `{ "id": 1, "summary": { "col1": {"count":..., "mean":..., "std":...}, ... } }`
    
- `GET /data/{id}/rows` — filtered/sorted/paginated rows.  
    Query params:
    
    - `columns=a,b,c`
        
    - `f=col,op,val` (repeatable). `op ∈ {eq,ne,gt,gte,lt,lte,contains,in}`
        
        - `in` uses `|` separator: `status,in,active|pending`
            
    - `sort=colA,-colB`
        
    - `page=1&page_size=50 (<=100)`  
        → `{ "page":1,"page_size":50,"total":N,"pages":X,"items":[...],... }`
        
- `GET /data/{id}/correlation?cols=a,b,c` — Pearson over numeric cols.  
    → `{ "id":1, "correlation": { "a": {"a":1.0,"b":0.7}, ... } }`
    
- `GET /data/{id}/trend?date=<dateCol>&value=<numCol>&freq=D|W|M&agg=sum|mean|count`
    
    - For `agg=count`, `value` is optional.  
        → `{ "id":1, "trend":[ {"date":"2024-01-01T00:00:00","amount":10.0}, ... ] }`
        

### Filters, Sorting & Pagination

Examples:

```
GET /data/1/rows?columns=date,amount,country&f=country,eq,CO&sort=-amount&page=1&page_size=20
GET /data/1/correlation?cols=amount,price
GET /data/1/trend?date=date&value=amount&freq=W&agg=sum
```

### Errors

Consistent error envelope:

```json
{
  "error": {
    "code": "bad_request|unauthorized|forbidden|not_found|server_error",
    "message": "Human readable message",
    "details": { ... }    // optional
  }
}
```

## Testing

```bash
# Run all tests
python manage.py test
```

## Deployment (GCP Cloud Run + Cloud SQL)

1. Build and push image to Artifact Registry:
    
    ```bash
    IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$(git rev-parse --short HEAD)"
    gcloud auth configure-docker $REGION-docker.pkg.dev
    docker build -t $IMAGE .
    docker push $IMAGE
    ```
    
2. Deploy to Cloud Run (with Cloud SQL socket):
    
    ```bash
    gcloud run deploy $SERVICE_NAME \
      --image $IMAGE \
      --region $REGION \
      --platform managed \
      --allow-unauthenticated \
      --add-cloudsql-instances $PROJECT:$REGION:$INSTANCE \
      --set-env-vars DJANGO_DEBUG=false,SECRET_KEY=<secret> \
      --set-env-vars DB_ENGINE=postgres,DB_NAME=<db>,DB_USER=<user>,DB_PASSWORD=<pass>,DB_HOST=/cloudsql/$PROJECT:$REGION:$INSTANCE,DB_PORT= \
      --set-env-vars LOG_LEVEL=INFO,WEB_CONCURRENCY=3,ALLOWED_HOSTS="*"
    ```
    

## CI/CD (GitHub Actions)

Workflow at `.github/workflows/deploy.yml` builds on every push to `main` and deploys to Cloud Run using Workload Identity Federation. Configure repository **Secrets**:

- `GCP_PROJECT_ID`, `GCP_REGION`, `GAR_REPO`, `CLOUD_RUN_SERVICE`
    
- `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT`
    
- `CLOUD_SQL_INSTANCE`
    
- `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
    

## Roadmap & Phases

- **Phase 1**: Minimal Django + Token auth (done)
    
- **Phase 2**: pandas preview/summary + Postgres + Docker (done)
    
- **Phase 3**: Filters, pagination, correlations, trends + tests (done)
    
- **Phase 4**: DRF + JWT + Swagger + logging + error normalization (done)
    
- **Phase 5**: Cloud Run + Cloud SQL + CI/CD (ready)
    

## Troubleshooting

- **Invalid CSV / parse errors** → API returns `400` with `error.message`.
    
- **No numeric columns for summary/correlation** → empty result or `{}`.
    
- **JWT 401** → ensure `Authorization: Bearer <access>`. Refresh token at `/api/token/refresh/`.
    
- **Cloud SQL connection** → verify `DB_HOST=/cloudsql/PROJECT:REGION:INSTANCE` and that Cloud Run service has Cloud SQL Client IAM role.
    
- **Static files in prod** → WhiteNoise runs at startup (`collectstatic` in `entrypoint.sh`).
    

## License

Choose your license (MIT recommended).  
If you want, I can add `LICENSE` and update this section.

---

### Quick cURL cheats

```bash
# Token
ACCESS=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<pass>"}' | jq -r .access)

# Upload
curl -s -X POST http://127.0.0.1:8000/upload \
  -H "Authorization: Bearer $ACCESS" -F "file=@sample.csv" | jq

# Preview / Summary
curl -s "http://127.0.0.1:8000/data/1/preview" -H "Authorization: Bearer $ACCESS" | jq
curl -s "http://127.0.0.1:8000/data/1/summary" -H "Authorization: Bearer $ACCESS" | jq

# Rows (filters/sort/pagination)
curl -s "http://127.0.0.1:8000/data/1/rows?columns=date,amount&f=country,eq,CO&sort=-amount&page=1&page_size=20" \
  -H "Authorization: Bearer $ACCESS" | jq

# Correlation / Trend
curl -s "http://127.0.0.1:8000/data/1/correlation?cols=amount,price" -H "Authorization: Bearer $ACCESS" | jq
curl -s "http://127.0.0.1:8000/data/1/trend?date=date&value=amount&freq=W&agg=sum" -H "Authorization: Bearer $ACCESS" | jq
```
