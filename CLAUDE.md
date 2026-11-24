# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Перед рефакторингом или работой с кодом всегда читай файл @spec.md
## Commands

Python 3.12 (Docker image) / FastAPI, async SQLAlchemy + asyncpg, Alembic. No test suite, linter, or formatter is configured (`src/services/test_rules_service.py` is a service for the "test rule" feature, not a pytest file).

- Install: `pip install -r requirements.txt`
- Run locally: `uvicorn src.main:app --reload` (run from repo root; imports are `src.*`)
- Migrations: `alembic upgrade head`; create one with `alembic revision --autogenerate -m "msg"` (files land in `src/migrations/versions/`)
- Full stack: `docker-compose up` (postgres, backend, frontend, nginx). The backend container runs `alembic upgrade head` before uvicorn. Note: Elasticsearch, Redis and the external Backend API are **not** in docker-compose.

Configuration is read from `.env` via `src/config.py` (pydantic-settings). Required: `MODE` (TEST/LOCAL/PROD/DOCKER), Postgres vars (incl. `POSTGRES_HOST_DOCKER`), `ES_HOST/ES_USER/ES_PASSWORD`, `BACKEND_API_URL`, `REDIS_HOST/PORT`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`. The app fails at import if any is missing.

## Architecture

A detection-rules management API (rules, correlation rules, supersession rules, IOC, scenarios, incidents, events, organizations, attack types, MITRE, users, audit). It is a **thin layer over three backends**, and which one a feature uses is the key thing to know:

1. **PostgreSQL** (via `DbManager`) — source of truth for rule versions, audit history, users, correlation rules.
2. **Elasticsearch** — current/searchable copy of rules (`src/repositories/elastic/`); reads for rules go here.
3. **External "main backend" HTTP API** (`src/connectors/backend_api_connector.py`, `backend_api` singleton, base URL `BACKEND_API_URL`) — many features (rule status, rule testing, MITRE, incidents, events, scenarios, organizations, etc.) are pure proxies: the service calls `self.main_backend.get/post/patch(...)` and validates the response with a Pydantic schema. Adding such a feature usually means only a router + schemas + a service with proxy calls.

### Layering (per feature package, e.g. `src/mitre/`)

`src/<feature>/api.py` (router, mounted under `/api` in `src/main.py`) → `src/services/<feature>_service.py` (extends `BaseService`) → repositories / ES / backend API. Schemas live in `src/<feature>/schemas.py`; SQLAlchemy models in `models.py` where Postgres is used. New routers must be registered in `src/main.py`.

- `BaseService(db)` gives every service `self.db` (DbManager), `self.es` (ElasticManager) and `self.main_backend` (backend_api).
- `DbManager` (`src/utils/db_manager.py`) is an async context manager holding one session and all PG repositories (`ruleModel`, `auditModel`, `correlationModel`, ...). It **rolls back on exit**, so writes only persist if the service calls `await self.db.save()` (commit). New repositories must be added to `DbManager.__aenter__`.
- Routers get the manager through `DBDep`; auth through `AuthUserDep` / `get_current_user`; role gates via `get_admin_user` (ADMIN only) and `get_editor_user` / `EditorUserDep` (ADMIN or ANALYST). JWT is read from the `access_token` cookie. See `src/dependencies.py` (also `PaginationDep`, limit must be 0<limit<20).
- Auth is opt-in per route: `/rules/admin/*` is ADMIN-only; `/rules/analyst/*` and all write routes of `/correlation-rules`, `/supersession-rules`, `/ioc` need ADMIN or ANALYST (VIEWER is read-only); reads of `/rules` and `/correlation-rules` and `/users/me` need any logged-in user; most other routers (incl. `POST /users/`) have no auth dependency. Add `AuthUserDep` / a role dep explicitly on new routes that need protection.
- Lifespan in `src/main.py` connects Elasticsearch (`src/init.py:elastic_manager`) and the backend API session; `health()` failure is only logged, not fatal.

### Rule versioning / audit flow (`src/services/rules_services.py`)

Rules are versioned: each create/update inserts a **new row with a new `unique_id`** in Postgres, writes an audit row (`before_id`/`after_id` link the history chain), then writes/updates the ES doc keyed by the stable `rule_id`, with author names (not ids) in `created_by`/`updated_by`. Correlation rules follow the same pattern with `correlation_audit`. Rules router composes `admin` and `analyst` sub-routers with role dependencies (`src/rules/api.py`).

### Misc

- Errors: custom exceptions in `src/exceptions/exceptions.py`; `setup_exceptions` (`exception_handler.py`) only maps `RuleNotFoundException` (404) and `RuleAlreadyExistException` (400). Any other custom exception (e.g. `AuditNotFoundException`, `UserNotFoundException`) needs a handler added there or it surfaces as a 500. Backend API errors (`aiohttp.ClientResponseError`) are re-raised unmapped.
- `src/database.py`: with `MODE=DOCKER`, `POSTGRES_HOST` in the DB URL is replaced by `POSTGRES_HOST_DOCKER`; `MODE=TEST` uses `NullPool`.
- Route order matters: static paths (`/me`, `/roles`, `/sequence`, `/agents`, ...) are declared before `/{id}` routes in each router.
- User-facing messages, comments and commit messages are in Russian; keep that convention.
- CORS is wide open (`allow_origins=["*"]` with credentials).
