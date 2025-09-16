hablame de [PROJECT] lo que hace, tecnologias usadas, ambientes, data, bd etc muy compacto y sintetizado

## Estrategia de Operaciones (Ops) y Base de Datos

**Gestión de conexiones**
- Local: `pool_size=5`, `timeout=5s` para desarrollo controlado.
- Dev/Staging: `pool_size=10-15`, `timeout=15s` con auto-reintentos.
- Prod: `pool_size=20+`, `timeout=30s`, `max_connections_per_service` definido y `idle_cleanup` habilitado.

**Seguridad**
- Manejo de secretos centralizado en **GCP Secret Manager** (credenciales y API keys).
- Despliegues en **VPC** privada con segmentación de subredes por servicio.
- Reglas de firewall limitan el acceso a puertos de bases de datos solo a dependencias autorizadas.

**Monitoreo**
- Logs consolidados en Cloud Logging con `correlation_id` transversal para trazabilidad.
- Métricas de bases de datos rastrean `connection_pool_utilization` y `query_latency` en todos los entornos.
- Observabilidad extendida con dashboards Prometheus/Grafana, alerting en Cloud Monitoring (latencia, errores, saturación de colas) y SLIs/SLOs: uptime 99.9% para AXI, p99 <300 ms, error budget monitoreado por servicio.

**Documentación y arquitectura**
- ADRs versionados por proyecto (`docs/adr/*`) con formato standard (Context → Decisión → Consecuencias); ejemplo: Kafka vs Pub/Sub en ECHO.
- Diagramas C4 y de despliegue en `/docs/architecture/` actualizados por release.
- Benchmarks de performance publicados (latencia p95/p99, throughput) para AXI, AIDE, GRASP y ECHO.
- Runbooks de operaciones (`docs/runbooks/*.md`) para rollback, incident response y mitigación de cuellos de botella DB.

**Testing & Quality Gates**
- Cobertura unitaria ≥90% en backends y frontends clave.
- Suites integration/E2E automatizadas (pytest + Playwright) ejecutadas en Dev y Staging.
- Load testing semanal con k6/Locust en Staging simulando 1000 usuarios concurrentes, reportado en dashboards.
- CI/CD GitHub Actions con security scanning (Bandit, Snyk, Trivy) y OWASP ZAP DAST como gates obligatorios.

**Infraestructura & Deploy**
- Infraestructura versionada con Terraform + Terragrunt (`infrastructure/{dev,staging,prod}/`) cubriendo Cloud Run, Cloud SQL, Redis, Pub/Sub, GCS.
- Makefile central (raíz) con targets `start-all`, `test-all`, `deploy-all <env>` que orquestan scripts/start.sh y pipelines IaC.
- Pipelines blue-green/rolling mantienen versión previa activa hasta superar smoke tests y tráfico real, con rollback automático vía comando/webhook.
- Gestión y rotación automática de secretos vía Secret Manager y sync a runtime.

**Seguridad & Identidad**
- OAuth2/OIDC (Auth0 + GCP IAP) integrado con servicios backend y NEXUS.
- Escaneos SAST/DAST (incluye OWASP ZAP), dependabot alerts y rotación de claves/API cada 30 días.
- Endurecimiento de imágenes Docker y controles VPC Service Controls.
- Estrategia de circuit breakers y retries con exponential backoff aplicada a todos los microservicios (detallado en runbooks).

---

**AXI - Analytics eXperience Intelligence**

**Propósito:** API REST para upload CSV, análisis estadísticos y JWT auth

**Stack:**

- Django DRF + PostgreSQL + Redis cache + JWT auth
- Docker + Cloud Run + Cloud SQL + Secret Manager
- CI/CD GitHub Actions

**Data:**

- Models: DataFile, AnalysisResult, CustomUser, UserProfile
- SQL: Window functions, CTEs, índices compuestos
- Analytics: correlaciones, cohorts, summaries vía raw SQL
- Backups: estrategia **Point-in-time recovery (PITR)** con ventana de 30 días en producción.

**Endpoints clave:**

- POST /datasets/upload
- GET /datasets/{id}/summary
- POST /analytics/correlations
- GET /docs (drf-spectacular)

**Ambientes:**

- Local/Test: Docker Compose + PostgreSQL nativo Ubuntu (DB por servicio)
- CI/CD: GitHub Actions (unit tests con PostgreSQL Docker)
- Dev/Staging/Prod: Cloud Run auto-deploy + Cloud SQL
- start.sh por ambiente

**Valor:** Base sólida REST + SQL avanzado + auth enterprise + deploy GCP. Primer proyecto del portfolio (2-3 semanas).


AXI (Analytics eXperience Intelligence):
- Django: 8000
- PostgreSQL: 5432
- Redis: 6379

**AXI - Analytics eXperience Intelligence**

- makefile: test, lint, docker-build, migrate, seed-data targets
- arquitectura: /app/{models,views,serializers,services,tests}/, separate /config/, /scripts/
- patrones: Repository pattern para data access, Service layer para business logic, Factory para model creation
- testing: pytest fixtures, mocks para external APIs, coverage >90%
- logging: structured JSON logs, correlation IDs
- validation: Pydantic serializers, custom validators
- error handling: global exception handler, custom exception classes


**AXI no necesita frontend dedicado** - NEXUS ya lo cubre

___

**AIDE (AI-Driven Engine)**

**Purpose:** AI insights generation and NL→SQL conversion for analytics data

**Tech Stack:**

- FastAPI + async/await
- OpenAI/Claude APIs for LLM processing
- PostgreSQL (reuses AXI datasets)
- Redis (cache LLM responses)
- Pydantic validation

**Core Functions:**

- POST /insights/{dataset_id} → auto-generates 3-4 business insights
- POST /nl2sql → natural language to SQL conversion
- POST /analyze-dataset → statistical summaries with explanations

**Data Flow:** AXI datasets → AIDE processing → LLM enrichment → structured insights
- BigQuery integration para pipelines ML y almacenamiento de datasets enriquecidos usando jobs analíticos.

**Environments:**

- Local/Test: Docker Compose + PostgreSQL nativo Ubuntu (compartido)
- CI/CD: GitHub Actions (unit tests con PostgreSQL Docker)
- Dev/Staging/Prod: Cloud Run + Cloud SQL

**Database:**

- Reads from AXI PostgreSQL (no separate DB)
- Stores insight cache in Redis
- SQL execution sandboxed (read-only, whitelist)
- Export datasets → BigQuery → insights agregados para reporting avanzado.

**Security:**

- Claves OpenAI/Claude gestionadas con GCP Secret Manager, rotación cada 30 días y scoping por ambiente.
- JWT from AXI (token forwarding)
- Input sanitization for SQL injection prevention
- Rate limiting on LLM calls with service-level quotas to avoid abuse

**Implementation time:** 1-2 weeks

**AIDE (AI-Driven Engine)**

- FastAPI: 8001
- PostgreSQL: 5432 (shared instance)
- Redis: 6380

**AIDE (AI-Driven Engine)**

- makefile: async-test, load-test, prompt-test targets
- arquitectura: /src/{api,services,schemas,utils}/, /prompts/, /tests/
- patrones: Strategy pattern para LLM providers, Chain of Responsibility para prompt processing, Circuit Breaker para API calls
- async: proper connection pooling, background tasks
- caching: Redis with TTL, cache invalidation strategies
- rate limiting: token bucket algorithm
- monitoring: LLM token usage tracking

___

**GRASP - GraphQL API Platform**

**Función:** API GraphQL optimizada que reemplaza múltiples endpoints REST con queries flexibles de un solo request.

**Stack:**

- FastAPI + Strawberry GraphQL
- MySQL/PostgreSQL async (SQLAlchemy)
- DataLoader (N+1 query elimination)
- Redis caching

**Endpoints:**

- `/graphql` - Single GraphQL endpoint
- `/` - GraphiQL playground

**Data:**

- Types: Dataset, User, Analytics, Campaign
- Queries: datasets, dataset(id), analytics(filters)
- Mutations: createDataset, updateCampaign
- Subscriptions: real-time metrics

**Optimización:**

- DataLoader batch loading
- Query complexity limits
- Depth limiting
- Field-level caching
- Connection pooling para SQLAlchemy async con tamaño ajustado a patrones GraphQL

**Ambientes:**

- Local/Test: Docker Compose (FastAPI + MySQL) + PostgreSQL nativo Ubuntu para lecturas compartidas
- CI/CD: GitHub Actions (unit tests con MySQL/PostgreSQL Docker)
- Dev/Staging/Prod: Cloud Run + Cloud SQL (MySQL) integrado con PostgreSQL compartido

**Base datos:**

- Same schema as AXI but async connections
- Optimized indexes for GraphQL access patterns
- Connection pooling

**ROI:** Client fetches exact data needed, reduces bandwidth 40-60%, eliminates over-fetching.

**GRASP (GraphQL API Platform)**

- FastAPI: 8002
- MySQL: 3306
- Redis: 6381

**GRASP - GraphQL API Platform**

- makefile: schema-generate, query-complexity-check targets
- arquitectura: /graphql/{types,resolvers,mutations}/, /dataloaders/, /middleware/
- patrones: DataLoader pattern, Query optimization middleware, Schema stitching
- performance: query complexity analysis, depth limiting
- security: query whitelisting, field-level permissions
- testing: GraphQL query testing, resolver unit tests
- schema: federation-ready design






___

ECHO - Event-Coordinated Hybrid Orchestrator

**Purpose:** Event-driven orchestrator connecting AXI, MINT, AIDE, GRASP via Kafka

**Stack:**

- FastAPI microservices
- Kafka + Zookeeper (aiokafka)
- Redis (state/cache)
- PostgreSQL (event store)
- Docker Compose

**Components:**

- event-router (producer/consumer hub)
- notification (email/slack alerts)
- report-gen (PDF/JSON from events)
- monitor-bridge (metrics to MINT)

**Events:**

- dataset.uploaded (AXI → ECHO)
- correlation.calculated (AXI → ECHO)
- insight.generated (AIDE → ECHO)
- tenant.alert.raised (MINT → ECHO)

**Environments:**

- Local/Test: Docker Compose (Kafka cluster) + PostgreSQL nativo Ubuntu
- CI/CD: GitHub Actions (unit tests con Kafka/PostgreSQL Docker)
- Dev/Staging: Cloud Run + Pub/Sub + Cloud SQL (event store)
- Prod: GCP Pub/Sub + Cloud Functions + Cloud SQL

**Data:**

- Event schemas (Pydantic)
- Async processing pipelines
- Circuit breaker patterns
- Dead letter queues
- Streaming continuo hacia BigQuery warehouse para analytics históricos de eventos

**Database:** Events table: event_id, timestamp, source_service, payload, status

**Value:** Demonstrates microservices, async messaging, event sourcing, distributed systems **mastery**


**ECHO (Event-Coordinated Hybrid Orchestrator)**

- FastAPI event-router: 8003
- FastAPI notification: 8004
- FastAPI report-gen: 8005
- FastAPI monitor-bridge: 8006
- Kafka: 9092
- Zookeeper: 2181
- Redis: 6382
- PostgreSQL: 5432 (shared event store)

**ECHO - Event-Coordinated Hybrid Orchestrator**

- makefile: kafka-setup, event-replay, consumer-test targets
- arquitectura: /events/{producers,consumers,schemas}/, /handlers/, /sagas/
- patrones: Saga pattern, Event Sourcing, CQRS y Dead Letter Queues con sistema de event replay para reprocesar flujos fallidos
- reliability: idempotency keys, circuit breakers validados y retries con exponential backoff uniformes
- monitoring: event tracing, consumer lag metrics
- testing: event replay, consumer isolation tests
- serialization: Avro schemas, schema registry
- BigQuery habilita queries SQL petabyte-scale y dashboards agregados de eventos
 
---

**MINT - Multi-tenant Intelligence Network Terminal**

**Purpose:** SaaS monitoring platform with tenant isolation, real-time metrics, external data integration

**Tech Stack:**

- FastAPI + SQLAlchemy async
- PostgreSQL (schema-per-tenant)
- Redis (tenant-scoped caching)
- Kafka (event streaming)
- Alembic (migrations)

**Architecture:**

- Tenant resolver middleware (subdomain/header)
- Schema isolation: `tenant_{id}` con Alembic + procedimientos de rollout/rollback por cliente y migration locks para evitar concurrencia
- Multi-tenant data pipeline
- Real-time metrics engine

**Endpoints:**

- `GET /api/metrics` (auto-filtered by tenant)
- `POST /tenants` (schema provisioning)
- `WS /metrics/live/{tenant_id}`

**Data Model:**

- `tenants` (master table)
- Per-tenant schemas with isolated datasets
- Cross-tenant admin views

**Environments:**

- Local/Test: Docker Compose + PostgreSQL nativo Ubuntu (schema-per-tenant)
- CI/CD: GitHub Actions (unit tests con PostgreSQL Docker)
- Dev/Staging/Prod: Cloud Run + Cloud SQL
- Tenant-specific quotas and rate limits

**Value:** Demonstrates SaaS architecture, data isolation, enterprise scalability patterns

**MINT (Multi-tenant Intelligence Network Terminal)**

- FastAPI: 8007
- PostgreSQL: 5433 (dedicated instance)
- Redis: 6383
- Kafka: 9093

**MINT - Multi-tenant Intelligence Network Terminal**

- makefile: tenant-create, schema-migrate, tenant-test targets
- arquitectura: /tenants/{middleware,resolvers,models}/, /migrations/per-tenant/
- patrones: Tenant Context pattern, Schema per tenant, Row Level Security
- isolation: connection per tenant, schema validation
- migrations: tenant-aware Alembic, rollback strategies
- security: tenant data leakage prevention
- monitoring: per-tenant metrics, quota enforcement



---

# NEXUS - Frontend Hub

**Purpose:** Multi-API frontend consuming AXI, MINT, AIDE, GRASP, ECHO services

**Stack:**

- React 18 + TypeScript
- Vite build tool
- TanStack Query (API state)
- Axios interceptors
- Tailwind CSS
- Chart.js visualization

**Architecture:**

```
src/
├── features/{service}/api.ts hooks.ts
├── components/ui/
├── lib/axios.ts auth.ts
└── pages/Dashboard.tsx
```

**Environment:**

```
VITE_AXI_API_URL=localhost:8010/api/v1
VITE_GRASP_API_URL=localhost:8020/graphql
VITE_AIDE_API_URL=localhost:8030/api/v1
```

**Auth:** JWT Bearer tokens from AXI, stored in memory

**Data Sources:**

- AXI: PostgreSQL via REST (users, analytics, datasets)
- GRASP: MySQL via GraphQL (complex queries)
- AIDE: AI insights via REST
- MINT: Multi-tenant metrics
- ECHO: Event streams

**Deployment:** Vite build → Cloud Storage → CDN

**APIs Consumed:**

- POST /auth/token
- GET /users/me
- GET /analytics/reports
- POST /graphql
- WS /ws/realtime/

**Purpose:** Demonstrate full-stack integration of Python backend ecosystem


**NEXUS (Frontend Hub)**

- Vite dev server: 3000

**NEXUS - Frontend Hub**

- makefile: type-check, bundle-analyze, e2e-test targets
- arquitectura: /src/{features,shared,types}/, feature-based modules
- patrones: Feature-based architecture, Custom hooks, Error boundaries
- state: React Query cache strategies, optimistic updates
- performance: code splitting, lazy loading, memoization
- testing: MSW mocks, component testing, integration tests
- types: strict TypeScript, API contract validation

**Operación NEXUS**
- Consumo integral de APIs AXI, AIDE, GRASP, ECHO y MINT mediante TanStack Query y Axios interceptors.
- Deploy continuo a Firebase Hosting (branch `main`) con CDN global y demo pública monitorizada.
- Observabilidad front-to-back con Web Vitals, Lighthouse CI y correlación de logs hacia Cloud Logging/Grafana.



**NEXUS (puerto 3000) incluye:**

- AXI auth + datasets upload
- AIDE insights display
- GRASP GraphQL playground
- ECHO events monitor
- MINT tenant metrics


---

# ADTECH Frontend (ADUI)

**Purpose:** Real-time advertising analytics dashboard for campaign managers

**Core Features:**

- Campaign CRUD operations
- Live metrics monitoring
- Revenue tracking dashboards
- User/tenant management

**Tech Stack:**

- React 18 + TypeScript
- TailwindCSS + Chart.js
- React Query + WebSocket client
- JWT auth with refresh

**API Integration:**

- REST: `/api/v1/campaigns/`, `/api/v1/auth/`
- GraphQL: `/graphql/` complex queries
- WebSocket: `/ws/realtime/` live metrics
- Multi-tenant aware requests

**Data Visualization:**

- Real-time CTR, impressions, conversions
- Geographic campaign performance
- Revenue attribution charts
- Alert notifications

**State Management:**

- React Query for API caching
- Context for auth/user state
- WebSocket state for metrics

**Environments:**

- Local/Test: `localhost:3000` apuntando a APIs backend locales/cloud
- CI/CD: GitHub Actions (unit tests/Vitest, mocks)  
- Dev: Deploy automático a Firebase/Vercel (usa Cloud SQL backends)
- Staging: Pre-prod validation con servicios Cloud
- Prod: CDN distribution

**Database:** None - pure frontend consuming ADTECH MySQL backend

**Key Components:**

- CampaignMetrics cards
- RealTimeChart components
- DataTable with filtering
- Modal forms for CRUD

Implementation time: 1-2 weeks

**ADTECH Frontend (ADUI)**

- React dev server: 3001


**ADTECH Frontend (ADUI)**

- makefile: performance-audit, lighthouse-ci targets
- arquitectura: /components/{ui,charts,forms}/, /hooks/, /utils/
- patrones: Compound components, Render props, Custom hooks
- real-time: WebSocket reconnection logic, state synchronization
- performance: virtualization for large datasets, debounced inputs
- analytics: user interaction tracking
- accessibility: WCAG compliance, keyboard navigation



**ADUI AdTech** - Puerto 3001

- Campaign management
- Real-time metrics
- Ya definido en tu doc


___

MLOG - MongoDB Audit & Analytics Microservice

**Purpose:** Centralized event logging and analytics for distributed backend services.

**Stack:**

- FastAPI + Motor (async MongoDB driver)
- MongoDB Atlas + Redis cache
- React + TypeScript dashboard
- Docker + GCP Cloud Run

**Data Model:**

```python
{
  "timestamp": ISODate,
  "service": "axi|mint|aide|grasp|echo",
  "user_id": ObjectId,
  "action": "login|upload|query|error",
  "metadata": {},
  "session_id": UUID
}
```

**Collections:**

- audit_logs (events)
- daily_metrics (aggregations)
- user_sessions (tracking)

**Aggregation Pipeline:**

```python
[
  {"$match": {"service": "axi", "timestamp": {"$gte": start}}},
  {"$group": {"_id": "$action", "count": {"$sum": 1}}},
  {"$sort": {"count": -1}}
]
```

**Endpoints:**

- POST /events (bulk insert)
- GET /analytics/{service}
- GET /metrics/timeline

**Integration:** Other services POST events via async HTTP client con circuit breaker y jobs programados MongoDB → BigQuery para analytics históricos.

**Environments:**

- Local/Test: Docker Compose MongoDB + PostgreSQL nativo Ubuntu para correlaciones
- CI/CD: GitHub Actions (unit tests con MongoDB Docker)
- Dev/Staging/Prod: MongoDB Atlas (conectado a Cloud SQL/PostgreSQL shared)
- Export: Scheduled BigQuery sync

**Performance:** 10K+ events/minute, sub-100ms queries con indexes en timestamp+service+user_id y consultas BigQuery SQL sobre datos históricos.


**MLOG (MongoDB Audit & Analytics)**

- FastAPI: 8008
- MongoDB: 27017
- Redis: 6384
- React dashboard: 3002

**MLOG - MongoDB Audit & Analytics**

- makefile: index-analyze, aggregation-test targets implementados en CI/CD para validar desempeño de la base de datos
- arquitectura: /aggregations/, /indexes/, /migrations/
- patrones: Aggregation Builder pattern, Index optimization, Time-series collections
- performance: compound indexes, aggregation pipeline optimization y sharding por `timestamp` con **TTL indexes** para lifecycle management
- scalability: sharding strategies, read replicas
- data lifecycle: TTL indexes, archival strategies
- monitoring: slow query analysis, index usage stats



## MLOG Validation

**Definición cumplida**: Microservicio MongoDB para logging centralizado con FastAPI + Motor, analytics agregadas, cache Redis, auth JWT/API-key, métricas Prometheus, frontend React.

**Arquitectura sólida**:

- Repository pattern para data access
- Circuit breaker para resilience
- Rate limiting por IP
- Correlation IDs
- Multi-environment configs
- Docker multi-stage
- E2E testing

## Faltantes críticos MLOG

**Schema evolution**: Migrations para cambios de estructura de eventos **Bulk ingestion**: Endpoint `/events/batch` para high-throughput **Data partitioning**: Sharding por timestamp o service **Alert system**: Webhooks para anomalías en métricas **Audit trails**: Log de accesos a analytics endpoints


**Estado**: MLOG production-ready. Patterns aplicables a resto del portfolio para enterprise-grade distributed systems.


**MLOG Analytics** - Puerto 3002

- Timeline eventos + filtros
- Agregaciones por service
- Ya definido en tu doc


---

GENERAL

**Puertos disponibles para expansion:** 8009-8020, 3003-3010, 5436-5440, 6385-6390, 9094-9100, 27018-27020



--- 


## Aplicar a otros proyectos

**AXI**: Circuit breakers + correlation IDs + bulk CSV processing **AIDE**: Rate limiting LLM calls + cache strategies + prompt versioning **GRASP**: Query complexity limits + DataLoader patterns + field permissions **ECHO**: Dead letter queues + saga patterns + event replay + retries/backoff **MINT**: Schema-per-tenant + quota enforcement + tenant metrics isolation **NEXUS**: Error boundaries + MSW mocking + performance budgets


## Stack patterns extraíbles (from MLOG)


```python
# Rate limiting middleware (universal)
# Circuit breaker decorator (database/API calls)  
# Correlation middleware (distributed tracing)
# Repository pattern (data access abstraction)
# Multi-env config with file injection (secrets)
```

## Orden de implementación por dependencias

**1. AXI** - Base del ecosistema (datos + auth) **2. MLOG** - Logging centralizado (independiente) **3. AIDE** - Consume datasets de AXI **4. GRASP** - Reutiliza schema de AXI **5. MINT** - Multi-tenant independiente **6. ECHO** - Orquesta todos los anteriores **7. NEXUS** - Frontend unificado final


## Orden implementación revisado

1. **AXI** (backend completo)
2. **MLOG** (logging independiente)
3. **NEXUS** (frontend que consume AXI)
4. **AIDE** + integrar en NEXUS
5. **GRASP** + integrar en NEXUS
6. **MINT** + integrar en NEXUS
7. **ECHO** + integrar en NEXUS
8. **MLOG frontend** (puerto 3002)
9. **ADUI** (puerto 3001) si necesitas AdTech demo

**NEXUS cubre 80% casos uso**. Otros frontends solo para demos específicas.



**Testing cross-project**

- Pytest matrices por servicio: AXI (fixtures, coverage >90%), AIDE (async/load/prompt tests), GRASP (GraphQL resolver/integration), ECHO (event replay/consumer), MINT (tenant schema validation), MLOG (aggregation/index performance).
- Frontends NEXUS/ADUI cubiertos con Vitest + Playwright (component, integration, E2E) y reporting en CI.
- Reglas pytest: pytest-asyncio, pytest-django, pytest-cov, pytest-mock, pytest-xdist habilitados en `pytest.ini` compartido.
- Pipelines ejecutan smoke, integration y load tests (k6/Locust) antes de aprobar despliegues.

## Github

$ git config --global --list
user.email=44485505+jorgehaq@users.noreply.github.com
user.name=Jorge Alvarez

- CI pipelines (GitHub Actions) ejecutan unit/integration/E2E, security scanning y despliegues controlados.
- Playwright + k6 jobs corren en Dev/Staging previo a promover a producción.


## Git Strategic


main
dev
features


## Redis - Keep Separated

Mantén Redis separado por proyecto (diferentes puertos) para:

- Cache key isolation
- TTL policies per service
- Independent scaling
- No cross-contamination



**Database allocation:**

```
PostgreSQL Shared (5432):
- axi_db
- aide_db  
- echo_db
- grasp_db

PostgreSQL MINT (5433):
- mint_master
- tenant_schemas
```

## Estrategia de ambientes y testing

- `LOCAL`: PostgreSQL nativo Ubuntu para desarrollo diario.
- `TEST`: PostgreSQL nativo Ubuntu con bases separadas por servicio.
- `CI/CD`: GitHub Actions ejecuta solo unit tests contra PostgreSQL Docker efímero.
- `DEV`: Cloud Run + Cloud SQL (instancia "portfolio-dev").
- `STAGING`: Cloud Run + Cloud SQL (instancia "portfolio-staging").
- `PROD`: Cloud Run + Cloud SQL (instancia "portfolio-prod").
- `Integration/E2E`: se corren en local o en ambientes Cloud (DEV/STAGING) según el caso.

# LOCAL (Development)
```
PostgreSQL local Ubuntu
├── axi_db_local
├── aide_db_local  
├── echo_db_local
└── grasp_db_local
```

# DEV (Integration Testing)
```
Cloud SQL Instance "portfolio-dev"
├── axi_db_dev
├── aide_db_dev
├── echo_db_dev
└── grasp_db_dev
```

# STAGING (Pre-production)
```
Cloud SQL Instance "portfolio-staging" 
├── axi_db_staging
├── aide_db_staging
├── echo_db_staging
└── grasp_db_staging
```

# PROD (Production)
```
Cloud SQL Instance "portfolio-prod"
├── axi_db_prod
├── aide_db_prod
├── echo_db_prod
└── grasp_db_prod
```

# Project root
```
├── .env.local
├── .env.dev  
├── .env.staging
├── .env.prod
└── .env.example
```
