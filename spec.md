# Техническая спецификация: DetectionRules

## 1. Назначение

REST API для управления правилами обнаружения угроз (SIEM/SOC): правила (detection rules), правила корреляции, правила подавления (supersession), IOC, а также просмотр сценариев, инцидентов, событий, организаций, типов атак и справочника MITRE. Ведётся история изменений (аудит) и разграничение доступа по ролям.

## 2. Стек

| Область | Технологии |
|---|---|
| Язык / рантайм | Python 3.12 (образ `python:3.12.2-slim`) |
| Web | FastAPI 0.136, Starlette 1.1, Uvicorn 0.48 |
| БД | PostgreSQL 17, SQLAlchemy 2.0 (async), asyncpg, Alembic 1.18 |
| Поиск | Elasticsearch 8.19 (`elasticsearch` async client) |
| HTTP-клиент | aiohttp 3.13 |
| Валидация / конфиг | pydantic 2.13, pydantic-settings |
| Безопасность | PyJWT, bcrypt |
| Мониторинг | sentry-sdk |
| Инструменты | ruff, pyright (в requirements, конфигурации нет) |

Redis указан в конфигурации (`REDIS_HOST/PORT`), но в рассмотренном коде не используется напрямую.

## 3. Архитектура

Сервис — тонкий слой над тремя источниками данных:

1. **PostgreSQL** — источник истины для версий правил, аудита, пользователей, правил корреляции.
2. **Elasticsearch** — актуальная копия правил; чтение и поиск правил идут отсюда (`src/repositories/elastic/`).
3. **Внешний Backend API** (`BACKEND_API_URL`, singleton `backend_api` в `src/connectors/backend_api_connector.py`) — прокси для статуса и тестирования правил, MITRE, инцидентов, событий, сценариев, организаций и др. Клиент на aiohttp: таймаут по умолчанию 20 с, `raise_for_status`, ответ 204 → `None`, Pydantic-тела сериализуются через `model_dump(mode='json', by_alias=True)`.

### Слои

```
src/<feature>/api.py  →  src/services/<feature>_service.py  →  репозитории PG / ES / backend_api
        (router)               (наследник BaseService)
```

- Схемы — `src/<feature>/schemas.py`, модели SQLAlchemy — `src/<feature>/models.py`.
- Роутеры подключаются в `src/main.py` с префиксом `/api`.
- `BaseService(db)` даёт `self.db` (DbManager), `self.es` (ElasticManager), `self.main_backend` (backend_api).
- `DbManager` (`src/utils/db_manager.py`) — async context manager с одной сессией и всеми PG-репозиториями (`ruleModel`, `usersModel`, `auditModel`, `correlationModel`, `correlationAuditModel`). **На выходе всегда `rollback()`**, поэтому изменения сохраняются только после явного `await db.save()`.
- Lifespan (`src/main.py`): подключение к Elasticsearch и Backend API; ошибка `health()` внешнего API только логируется, старт не прерывается.

## 4. Аутентификация и роли

- Логин: `POST /api/users/login` проверяет пароль (bcrypt, выполняется в `ThreadPoolExecutor` на 4 потока), выдаёт JWT (`exp` = `ACCESS_TOKEN_EXPIRE_MINUTES`) и ставит cookie `access_token` (`secure=False`); токен также возвращается в теле ответа. Выход — `DELETE /api/users/logout` удаляет cookie.
- Токен читается из cookie (`get_token`), декодируется `AuthService.decode_token` → `UserInCookiesSchema` (содержит `user_id`, `username`, `role`). Ошибки: нет токена → 401 «Вы не передали токен аутентификации», просрочен → 401 «Сессия истекла, войдите снова», невалиден → 401 «Некорректный токен доступа».
- Роли (`UserRoles`): `ADMIN`, `ANALYST`, `VIEWER` (по умолчанию `VIEWER`).
- Зависимости (`src/dependencies.py`): `AuthUserDep` (любой аутентифицированный), `get_admin_user` (только `ADMIN`, иначе 403), `get_analyst_user` (только `ANALYST`, иначе 403). Проверка — точное совпадение роли, т.е. `ADMIN` не имеет доступа к маршрутам аналитика.
- **Реальное покрытие авторизацией:**
  - только `ADMIN`: всё под `/api/rules/admin/*`;
  - только `ANALYST`: всё под `/api/rules/analyst/*`;
  - любой вошедший пользователь: `/users/me`, а также `/correlation-rules` (`GET /`, `GET /{id}`, `POST`, `PUT` — нужен для данных автора);
  - **без проверки токена**: `POST /users/`, `GET /users/`, `GET /users/{id}`, `/rules` (чтение), `/audits`, `/ioc`, `/supersession-rules`, `/scenarios`, `/incidents`, `/organizations`, `/attack-types`, `/events`, `/mitre`, `GET /correlation-rules/sequence` и `/group-by-fields`.
  Роль `VIEWER` нигде отдельно не проверяется.
- Пагинация `PaginationDep`: `limit` 1–19 (по умолчанию 10), `offset` ≥ 0. Применяется в `/rules` и `/audits`; остальные списки используют собственные параметры (`IncidentParams`, `ScenarioQueryParams`, `IocQueryDep` и т.д.).
- CORS: `allow_origins=["*"]` вместе с `allow_credentials=True`.

## 5. Версионирование правил и аудит

Для `detection_rules` каждое создание/изменение порождает **новую строку** с новым `unique_id`; неизменяемый идентификатор правила — `rule_id`.

Создание: строка в PG → запись аудита → документ в ES → `db.save()`.
Обновление: новая строка в PG → поиск последней записи аудита правила → новая запись аудита с `before_id` = предыдущая → у предыдущей `after_id` = новая → `db.save()` → обновление документа в ES по `rule_id`.
В ES-документ вместо id авторов пишутся имена (`created_by`, `updated_by`).
Для правил корреляции аналогичная цепочка в `correlation_audit`.

Смена статуса и тест правила выполняются через внешний API (`PATCH /detection-rules/{id}/status`, `POST /detection-rules/test`).

## 6. Модель данных (PostgreSQL)

**detection_rules** — `unique_id` (PK), `rule_id` (str 50), `enabled`, `rule_type`, `scope`, `match_type`, `pattern` (str 500), `fields[]`, `case_sensitive`, `category`, `attack_type`, `scenario_type`, `mitre_ids[]`, `tactics[]`, `severity_hint` (enum `info|low|medium|high|critical`), `confidence` (0–100, CHECK), `description`, `explanation_template`, `recommendations[]`, `tags[]`, `created_at`, `updated_at`.

**users** — `id`, `username` (unique, 50), `hashed_password` (bytes), `role` (`UserRoles`), `created_at`, `updated_at`.

**audit** — `id`, `author_id` → users, `action` (по умолчанию `create`), `resource_type`, `rule_general_id`, `rule_unique_id` → detection_rules, `before_id` / `after_id` → audit (SET NULL), `created_at`, `updated_at`.

**correlation_rules** — `id`, `correlation_id`, `enabled`, `scenario_type` (индекс), `description`, `window_seconds`, `sequence` (JSONB), `group_by` (JSONB), `min_unique_categories` (по умолчанию 1), `severity` (тот же enum), `confidence`, `recommendations` (JSONB), `tags` (JSONB), `created_by`, `updated_by`, `created_at`, `updated_at`.

**correlation_audit** — аналог `audit` для правил корреляции (`correlation_id`, `correlation_unique_id` → correlation_rules, `before_id` / `after_id`).

Временные метки частично считаются в часовом поясе `Asia/Bishkek`. Миграции — `src/migrations/versions/` (Alembic, конфиг `alembic.ini`).

## 7. API (все пути с префиксом `/api`)

| Префикс | Эндпоинты |
|---|---|
| `/users` | `POST /login`, `POST /`, `GET /`, `GET /roles`, `GET /me`, `GET /{id}`, `DELETE /logout` |
| `/rules` | `GET /` (поиск: `pattern`, `rule_id`, `description` + пагинация), `GET /{rule_id}`, `GET /enums/severity-hints` |
| `/rules/admin` (ADMIN) | `POST /`, `PUT /{rule_id}`, `DELETE /{rule_id}`, `PATCH /{rule_id}` (статус), `POST /test` |
| `/rules/analyst` (ANALYST) | `POST /`, `PUT /{rule_id}` |
| `/audits` | `GET /rule/{rule_id}`, `GET /`, `GET /{id}` |
| `/ioc` | `POST /`, `GET /`, `GET /{ioc_id}`, `PATCH /{ioc_id}` |
| `/supersession-rules` | `GET /`, `POST /`, `GET /suppression-match-fields`, `GET /{super_id}`, `PUT /{super_id}` |
| `/correlation-rules` | `GET /`, `GET /sequence`, `GET /group-by-fields`, `GET /{correlation_id}`, `POST /`, `PUT /{correlation_id}` |
| `/scenarios` | `GET /`, `GET /{id}`, `GET /{id}/events` |
| `/incidents` | `GET /`, `GET /daily_count_incidents`, `GET /{inc_id}`, `GET /{inc_id}/events`, `PATCH /{inc_id}/status` |
| `/organizations` | `GET /`, `GET /agents`, `GET /{id}`, `POST /`, `PUT /{organization_id}`, `DELETE /{organization_id}` |
| `/attack-types` | `GET /` |
| `/events` | `GET /`, `GET /{index_name}/{event_id}` |
| `/mitre` | `GET /mitre`, `POST /sync-mitre` (итоговые пути: `/api/mitre/mitre`, `/api/mitre/sync-mitre`) |

Ограничения доступа см. в разделе 4. Порядок объявления маршрутов важен: статические пути (`/roles`, `/me`, `/sequence`, `/group-by-fields`, `/suppression-match-fields`, `/daily_count_incidents`, `/agents`) стоят перед параметрическими `/{id}`.
`GET /users/` принимает параметр `department_id`, `GET /rules/` — `pattern`, `rule_id`, `description` (при `rule_id` возвращается один документ из ES, иначе поиск по тексту).

## 8. Ошибки

Исключения объявлены в `src/exceptions/exceptions.py`: `NoResultException` → `ObjectNotFoundException` → (`RuleNotFoundException`, `AuditNotFoundException`), `UserNotFoundException`; `UniqueObjIsExistException` → `RuleAlreadyExistException`; `HasNotRightsException`. У каждого есть русскоязычное поле `detail`.

`setup_exceptions` (`exception_handler.py`) регистрирует обработчики **только для двух** исключений:

| Исключение | HTTP |
|---|---|
| `RuleNotFoundException` | 404 |
| `RuleAlreadyExistException` | 400 |

Остальные (`ObjectNotFoundException`, `AuditNotFoundException`, `UserNotFoundException`, `HasNotRightsException`) обработчиков не имеют, если только сервис не конвертирует их сам (как `RuleService.find_one`: `ObjectNotFoundException` → `RuleNotFoundException`). Обработчики не возвращают ответ, а делают `raise HTTPException(...)` внутри обработчика, поведение такого подхода стоит проверить. Ошибки внешнего API (`aiohttp.ClientResponseError`) в HTTP-ответы не преобразуются.

## 9. Конфигурация (`.env`, `src/config.py`)

Обязательные переменные (приложение не стартует без них):

- `MODE` — `TEST` | `LOCAL` | `PROD` | `DOCKER`
- `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_HOST_DOCKER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `ES_HOST`, `ES_USER`, `ES_PASSWORD`, `ES_VERIFY_CERTS` (по умолчанию `False`)
- `BACKEND_API_URL`
- `REDIS_HOST`, `REDIS_PORT`
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

`DB_URL` собирается как `postgresql+asyncpg://user:password@POSTGRES_HOST:port/db`. В `src/database.py` при `MODE=DOCKER` в нём подставляется `POSTGRES_HOST_DOCKER` вместо `POSTGRES_HOST`; при `MODE=TEST` используется `NullPool`. Модуль создаёт два движка: обычный (с пулом) и `engine_null_pool`; `AsyncSession` (с `expire_on_commit=False`) — фабрика сессий для `DbManager`.

## 10. Запуск и развёртывание

- Локально: `pip install -r requirements.txt`, `alembic upgrade head`, `uvicorn src.main:app --reload` (из корня репозитория).
- Docker: `docker-compose up` поднимает `postgres` (17-alpine), `backend` (`ularchik/detection_rules_back`, команда: `alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000`), `frontend` (`ularchik/detection_rules_front`, порт 3000) и `nginx` (порт 80, конфиг `./nginx.conf`).
- Elasticsearch, Redis и внешний Backend API в `docker-compose.yml` **не входят** и должны быть доступны отдельно.

## 11. Известные особенности

- Автотестов и настроенных линтеров нет (`src/services/test_rules_service.py` — сервис функции «тест правила», не набор тестов).
- Дублирование в путях MITRE: `/api/mitre/mitre`.
- Опечатки в тегах Swagger («ПРавила корреляции», «Истороия изменений», «Айок») — косметика, но видна в документации.
- Роли `ADMIN` и `ANALYST` взаимоисключающие на маршрутах `/rules/admin` и `/rules/analyst`.
- Большинство эндпоинтов, включая создание пользователей (`POST /users/`), не требуют аутентификации (см. раздел 4).
- В `src/users/api.py` две функции названы `get_me` (для `/me` и `/{id}`); работает, так как регистрация идёт по декоратору.
- Обработчики исключений делают `raise HTTPException` вместо возврата ответа; покрыты только `RuleNotFoundException` и `RuleAlreadyExistException`.
- В `update_rule` `resource_type` аудита заполняется значением `rule_id`.
