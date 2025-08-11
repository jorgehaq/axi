**Idioma:** [English](./README.md) | Español

# Analytics API — Analítica KISS de CSV (Django + DRF + JWT)

API simple, entendible y lista “para mostrar” que permite subir CSVs y correr **analítica básica**. Construida paso a paso (KISS) para demostrar arquitectura limpia, tests y despliegue a Cloud Run.

## Tabla de Contenido
- [Resumen](#resumen)
- [Características](#características)
- [Stack](#stack)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Inicio rápido (Local)](#inicio-rápido-local)
- [Docker (PostgreSQL + App)](#docker-postgresql--app)
- [Configuración](#configuración)
- [API](#api)
  - [Auth (JWT)](#auth-jwt)
  - [Endpoints principales](#endpoints-principales)
  - [Filtros, orden y paginación](#filtros-orden-y-paginación)
  - [Errores](#errores)
- [Testing](#testing)
- [Despliegue (GCP Cloud Run + Cloud SQL)](#despliegue-gcp-cloud-run--cloud-sql)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Roadmap y fases](#roadmap-y-fases)
- [Solución de problemas](#solución-de-problemas)
- [Licencia](#licencia)
- [cURL rápidos](#curl-rápidos)

---

## Resumen
La API permite a usuarios autenticados subir archivos CSV y ejecutar **analítica básica**:
- ver las primeras filas (preview),
- estadísticas numéricas (count/mean/std),
- listado de filas con filtros y paginación,
- correlaciones simples,
- tendencias por fecha (diaria/semanal/mensual).

Diseñada para ser **fácil de razonar** y **crecer por fases**.

## Características
- Django 5 + DRF 3.15
- JWT (access/refresh) con permisos de “dueño” (owner-only)
- Analítica de CSV con pandas (backend pyarrow)
- Swagger UI (`/api/docs/`) con drf-spectacular
- Formato de error consistente + logging básico
- App dockerizada + Postgres con `docker-compose`
- Lista para Cloud Run (gunicorn + entrypoint)

## Stack
- **Backend**: Django, Django REST Framework  
- **Auth**: `djangorestframework-simplejwt`  
- **Docs**: `drf-spectacular`  
- **Analytics**: pandas (+ pyarrow)  
- **DB**: SQLite (dev) → PostgreSQL (prod)  
- **Deploy**: Docker, Cloud Run, Cloud SQL  
- **CI/CD**: GitHub Actions (opcional)

## Estructura del proyecto
```

analytics_api/  
├── Dockerfile  
├── docker-compose.yml  
├── entrypoint.sh  
├── manage.py  
├── requirements.txt  
├── .env.example  
├── analytics_api/  
│ ├── settings.py  
│ ├── urls.py  
│ └── wsgi.py / asgi.py  
├── core/  
│ ├── admin.py  
│ ├── models.py # Token removido en Fase 4; ahora JWT  
│ ├── services.py # Lectura CSV, filtros, orden, paginación, analytics  
│ ├── serializers.py # Validación de query params  
│ ├── permissions.py # Acceso solo del dueño  
│ ├── errors.py # Manejador de excepciones DRF  
│ ├── views.py # Vistas DRF  
│ ├── urls.py  
│ └── tests.py  
└── media/

````

## Inicio rápido (Local)
Requisitos: Python 3.11+, pip, virtualenv.

```bash
git clone <tu-repo> && cd analytics_api
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Migrar y levantar (SQLite por defecto)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
````

Visita:

- Health: `http://127.0.0.1:8000/health/`
    
- Docs: `http://127.0.0.1:8000/api/docs/`
    

## Docker (PostgreSQL + App)

Dev local con Postgres:

```bash
docker compose up --build
# App:     http://127.0.0.1:8000
# Admin:   http://127.0.0.1:8000/admin
# Docs:    http://127.0.0.1:8000/api/docs/
```

Crear admin dentro del contenedor:

```bash
docker compose exec web python manage.py createsuperuser
```

## Configuración

Variables de entorno (ver `.env.example` / `.env.gcp.example`):

```
DJANGO_DEBUG=true|false
SECRET_KEY=<django-secret>

# DB: sqlite (default) o postgres
DB_ENGINE=sqlite|postgres
DB_NAME=analytics
DB_USER=analytics
DB_PASSWORD=change-me
DB_HOST=db                # o /cloudsql/PROJECT:REGION:INSTANCE (GCP)
DB_PORT=5432

ALLOWED_HOSTS=*
LOG_LEVEL=INFO
WEB_CONCURRENCY=3         # workers de gunicorn (prod)
```

## API

### Auth (JWT)

Obtener tokens:

```
POST /api/token/
{
  "username": "admin",
  "password": "******"
}
→ { "access": "...", "refresh": "..." }
```

Refrescar:

```
POST /api/token/refresh/
{ "refresh": "<refresh>" }
→ { "access": "..." }
```

Usuario actual:

```
GET /api/me/      # Authorization: Bearer <access>
→ { "id": 1, "username": "admin", "email": "..." }
```

### Endpoints principales

Todos requieren `Authorization: Bearer <access>` excepto `/health/`.

- `POST /upload` — multipart form, campo `file` (CSV).  
    → `{ "message": "File uploaded successfully", "id": <int> }`
    
- `GET /data/{id}/preview` — primeras 5 filas.  
    → `{ "id": 1, "rows": [ {...}, ... ] }`
    
- `GET /data/{id}/summary` — `count/mean/std` de columnas numéricas.  
    → `{ "id": 1, "summary": { "col1": {"count":..., "mean":..., "std":...}, ... } }`
    
- `GET /data/{id}/rows` — filas con filtros/orden/paginación.  
    Params:
    
    - `columns=a,b,c`
        
    - `f=col,op,val` (repetible). `op ∈ {eq,ne,gt,gte,lt,lte,contains,in}`
        
        - `in` usa `|`: `status,in,active|pending`
            
    - `sort=colA,-colB`
        
    - `page=1&page_size=50 (<=100)`  
        → `{ "page":1,"page_size":50,"total":N,"pages":X,"items":[...],... }`
        
- `GET /data/{id}/correlation?cols=a,b,c` — Pearson sobre columnas numéricas.  
    → `{ "id":1, "correlation": { "a": {"a":1.0,"b":0.7}, ... } }`
    
- `GET /data/{id}/trend?date=<colFecha>&value=<colNum>&freq=D|W|M&agg=sum|mean|count`
    
    - Con `agg=count`, `value` es opcional.  
        → `{ "id":1, "trend":[ {"date":"2024-01-01T00:00:00","amount":10.0}, ... ] }`
        

### Filtros, orden y paginación

Ejemplos:

```
GET /data/1/rows?columns=date,amount,country&f=country,eq,CO&sort=-amount&page=1&page_size=20
GET /data/1/correlation?cols=amount,price
GET /data/1/trend?date=date&value=amount&freq=W&agg=sum
```

### Errores

Envoltorio consistente:

```json
{
  "error": {
    "code": "bad_request|unauthorized|forbidden|not_found|server_error",
    "message": "Mensaje legible",
    "details": { ... }    // opcional
  }
}
```

## Testing

```bash
python manage.py test
```

## Despliegue (GCP Cloud Run + Cloud SQL)

1. Build & push a Artifact Registry:
    
    ```bash
    IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$(git rev-parse --short HEAD)"
    gcloud auth configure-docker $REGION-docker.pkg.dev
    docker build -t $IMAGE .
    docker push $IMAGE
    ```
    
2. Deploy a Cloud Run (con socket de Cloud SQL):
    
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

Workflow en `.github/workflows/deploy.yml` que construye en cada push a `main` y despliega a Cloud Run con Workload Identity Federation. Configura los **Secrets**:

- `GCP_PROJECT_ID`, `GCP_REGION`, `GAR_REPO`, `CLOUD_RUN_SERVICE`
    
- `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT`
    
- `CLOUD_SQL_INSTANCE`
    
- `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
    

## Roadmap y fases

- **Fase 1**: Django mínimo + Token auth (listo)
    
- **Fase 2**: pandas preview/summary + Postgres + Docker (listo)
    
- **Fase 3**: Filtros, paginación, correlaciones, trends + tests (listo)
    
- **Fase 4**: DRF + JWT + Swagger + logging + errores consistentes (listo)
    
- **Fase 5**: Cloud Run + Cloud SQL + CI/CD (listo)
    

## Solución de problemas

- **CSV inválido / parse errors** → la API responde `400` con `error.message`.
    
- **Sin columnas numéricas** → resultado vacío o `{}`.
    
- **JWT 401** → usa `Authorization: Bearer <access>`. Refresca en `/api/token/refresh/`.
    
- **Cloud SQL** → verifica `DB_HOST=/cloudsql/PROJECT:REGION:INSTANCE` y rol **Cloud SQL Client** en el servicio.
    
- **Estáticos en prod** → WhiteNoise corre en startup (`collectstatic` en `entrypoint.sh`).
    

## Licencia

Elige tu licencia (MIT recomendado).

---

## cURL rápidos

```bash
# Token
ACCESS=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<pass>"}' | jq -r .access)

# Subir CSV
curl -s -X POST http://127.0.0.1:8000/upload \
  -H "Authorization: Bearer $ACCESS" -F "file=@sample.csv" | jq

# Preview / Summary
curl -s "http://127.0.0.1:8000/data/1/preview" -H "Authorization: Bearer $ACCESS" | jq
curl -s "http://127.0.0.1:8000/data/1/summary" -H "Authorization: Bearer $ACCESS" | jq

# Filas (filtros/orden/paginación)
curl -s "http://127.0.0.1:8000/data/1/rows?columns=date,amount&f=country,eq,CO&sort=-amount&page=1&page_size=20" \
  -H "Authorization: Bearer $ACCESS" | jq

# Correlación / Trend
curl -s "http://127.0.0.1:8000/data/1/correlation?cols=amount,price" -H "Authorization: Bearer $ACCESS" | jq
curl -s "http://127.0.0.1:8000/data/1/trend?date=date&value=amount&freq=W&agg=sum" -H "Authorization: Bearer $ACCESS" | jq
```
