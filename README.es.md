**Idioma:** [English](./README.md) | Español

# AXI - Analytics eXchange Interface

API de análisis de datos CSV construida con Django REST Framework. Permite subir archivos CSV y ejecutar análisis básicos con autenticación JWT.

## Stack Técnico

- **Backend**: Django 5.0, Django REST Framework 3.15
- **Auth**: JWT (djangorestframework-simplejwt)
- **Analytics**: pandas + pyarrow
- **DB**: PostgreSQL (prod) / SQLite (dev)
- **Storage**: Google Cloud Storage (prod) / Local (dev)
- **Background**: Celery + Redis
- **Deploy**: Docker, Cloud Run, Cloud SQL
- **Docs**: drf-spectacular (Swagger)

## Arquitectura

```
axi/
├── axi/                    # Configuración Django
├── apps/
│   ├── auth/              # Autenticación OAuth2
│   ├── datasets/          # Core API datasets
│   └── analytics/         # Análisis avanzados
├── scripts/               # Testing y utilidades
└── makefiles/             # Comandos por ambiente
```

## Instalación Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Base de datos
make -f makefiles/local.mk local-postgres-up
make -f makefiles/local.mk local-migrations

# Servidor
make -f makefiles/local.mk local-django
```

## API Endpoints

### Autenticación
- `POST /api/token/` - Obtener JWT tokens
- `POST /api/token/refresh/` - Refrescar token
- `GET /api/me/` - Usuario actual

### Datasets
- `POST /api/v1/datasets/upload` - Subir CSV
- `GET /api/v1/datasets/{id}/preview` - Primeras 5 filas
- `GET /api/v1/datasets/{id}/summary` - Estadísticas numéricas
- `GET /api/v1/datasets/{id}/rows` - Filas con filtros/paginación
- `GET /api/v1/datasets/{id}/correlation` - Correlaciones
- `GET /api/v1/datasets/{id}/trend` - Tendencias temporales
- `GET /api/v1/datasets/{id}/download-url/` - URL de descarga

### Filtros y Paginación
```
/datasets/1/rows?f=country,eq,CO&sort=-amount&page=1&page_size=20
```

Operadores: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `in`

## Ambientes

### Local
```bash
# Servicios Docker (Redis, MinIO, Flower)
make -f makefiles/local.mk local-services

# PostgreSQL local
make -f makefiles/local.mk local-postgres-up

# Tests
make -f makefiles/local.mk local-test-env
```

### Dev (GCP)
```bash
# Deploy automático via GitHub Actions (branch: dev)
git push origin dev

# Tests manuales
make -f makefiles/dev.mk dev-test-real
```

Los secretos de CI/CD para dev y prod están documentados en `docs/ci-secrets.md`.

### Staging/Production
```bash
# Deploy via GitHub Actions (branch: main)
git push origin main
```

Los secretos necesarios para producción están listados en `docs/ci-secrets.md`.

## Variables de Entorno

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
# Todos los ambientes
bash scripts/test_all_environment.sh local
bash scripts/test_all_environment.sh dev

# Específicos
bash scripts/test_oauth2_integration.sh local
bash scripts/test_missing_endpoints.sh local
```

## Configuración GCP

1. **Cloud SQL**: PostgreSQL instancia
2. **Cloud Storage**: Bucket para archivos
3. **Redis**: Memorystore para Celery
4. **Artifact Registry**: Imágenes Docker
5. **Cloud Run**: Servicios HTTP

## Background Jobs

```bash
# Desarrollo local
make -f makefiles/local.mk local-services  # Redis + Celery
.venv/bin/python -m celery -A axi worker -l info

# Monitoring
curl localhost:5555  # Flower UI
```

## Estructura de Datos

**Upload**:
```json
{
  "message": "File uploaded successfully",
  "id": 123
}
```

**Rows con filtros**:
```json
{
  "page": 1,
  "page_size": 50,
  "total": 150,
  "results": [{"col1": "val1", "col2": "val2"}]
}
```

**Errores**:
```json
{
  "error": {
    "code": "bad_request",
    "message": "Missing columns: ['date']",
    "details": {}
  }
}
```

## Desarrollo

```bash
# Dependencias
make -f makefiles/local.mk local-install-deps

# Base de datos
make -f makefiles/local.mk local-migrations

# Servidor Django
make -f makefiles/local.mk local-django

# Tests completos
make -f makefiles/local.mk local-test-env
```

## Documentación API

- Swagger: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Schema: `http://localhost:8000/api/schema/`
