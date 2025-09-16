hablame de [PROJECT] lo que hace, tecnologias usadas, ambientes, data, bd etc muy compacto y sintetizado

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

**Endpoints clave:**

- POST /datasets/upload
- GET /datasets/{id}/summary
- POST /analytics/correlations
- GET /docs (drf-spectacular)

**Ambientes:**

- Local: Docker Compose
- Dev/Staging/Prod: Cloud Run auto-deploy
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

**Environments:**

- Local: Docker compose
- Dev/Staging/Prod: Cloud Run + Cloud SQL

**Database:**

- Reads from AXI PostgreSQL (no separate DB)
- Stores insight cache in Redis
- SQL execution sandboxed (read-only, whitelist)

**Security:**

- JWT from AXI (token forwarding)
- Input sanitization for SQL injection prevention
- Rate limiting on LLM calls

**Implementation time:** 1-2 weeks

**AIDE (AI-Driven Engine)**

- FastAPI: 8001
- PostgreSQL: 5433 (separate instance)
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

**Ambientes:**

- Local: Docker + MySQL
- Dev/Staging/Prod: Cloud Run + Cloud SQL

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

- Local: Docker Kafka cluster
- Dev/Staging: Cloud Run + Pub/Sub
- Prod: GCP Pub/Sub + Cloud Functions

**Data:**

- Event schemas (Pydantic)
- Async processing pipelines
- Circuit breaker patterns
- Dead letter queues

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
- PostgreSQL: 5434

**ECHO - Event-Coordinated Hybrid Orchestrator**

- makefile: kafka-setup, event-replay, consumer-test targets
- arquitectura: /events/{producers,consumers,schemas}/, /handlers/, /sagas/
- patrones: Saga pattern, Event Sourcing, CQRS, Dead Letter Queue
- reliability: idempotency keys, retry with exponential backoff
- monitoring: event tracing, consumer lag metrics
- testing: event replay, consumer isolation tests
- serialization: Avro schemas, schema registry
 
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
- Schema isolation: `tenant_{id}`
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

- Local: Docker Compose
- Dev/Staging/Prod: Cloud Run + Cloud SQL
- Tenant-specific quotas and rate limits

**Value:** Demonstrates SaaS architecture, data isolation, enterprise scalability patterns

**MINT (Multi-tenant Intelligence Network Terminal)**

- FastAPI: 8007
- PostgreSQL: 5435
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

- Local: `localhost:3000` → ADTECH API
- Dev: Auto-deploy to Firebase/Vercel
- Staging: Pre-prod validation
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

**Integration:** Other services POST events via async HTTP client with circuit breaker.

**Environments:**

- Local: Docker Compose MongoDB
- Dev/Prod: MongoDB Atlas
- Export: Scheduled BigQuery sync

**Performance:** 10K+ events/minute, sub-100ms queries with indexes on timestamp+service+user_id.


**MLOG (MongoDB Audit & Analytics)**

- FastAPI: 8008
- MongoDB: 27017
- Redis: 6384
- React dashboard: 3002

**MLOG - MongoDB Audit & Analytics**

- makefile: index-analyze, aggregation-test targets
- arquitectura: /aggregations/, /indexes/, /migrations/
- patrones: Aggregation Builder pattern, Index optimization, Time-series collections
- performance: compound indexes, aggregation pipeline optimization
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

**AXI**: Circuit breaker + correlation IDs + bulk CSV processing **AIDE**: Rate limiting LLM calls + cache strategies + prompt versioning **GRASP**: Query complexity limits + DataLoader patterns + field permissions **ECHO**: Dead letter queues + saga patterns + event replay **MINT**: Schema-per-tenant + quota enforcement + tenant metrics isolation **NEXUS**: Error boundaries + MSW mocking + performance budgets


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



**Pytest configurado en:**

AXI - pytest fixtures, mocks externos, coverage >90% AIDE - async-test target, load-test, prompt-test ECHO - event replay, consumer isolation tests MINT - tenant-test target, schema validation MLOG - aggregation-test, index performance tests

**Faltantes pytest:**

GRASP - solo menciona "GraphQL query testing, resolver unit tests" NEXUS - tiene "component testing, integration tests" pero no especifica pytest ADUI - no especifica framework testing

**Recomendación:**

pytest para todos los backends Python (AXI, AIDE, GRASP, ECHO, MINT, MLOG)

- pytest-asyncio para FastAPI async
- pytest-django para Django
- pytest-cov para coverage
- pytest-mock para mocking
- pytest-xdist para parallel execution

Frontend mantén Jest/Vitest según stack React.

## Github

$ git config --global --list
user.email=44485505+jorgehaq@users.noreply.github.com
user.name=Jorge Alvarez


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