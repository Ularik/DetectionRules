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
3. **Внешний Backend API** (`BACKEND_API_URL`, singleton `backend_api` в `src/connectors/backend_api_connector.py`) — прокси для статуса и тестирования правил, MITRE, инцидентов, событий, сценариев, организаций и др. Клиент на aiohttp: таймаут по умолчанию 20 с, `raise_for_status`, ответ 204 → `None`, Pydantic-тела сериализуются через `model_dump(mode='json', by_alias=True)`. Query-параметры (dict или Pydantic-модель) приводятся в `_prepare_params`: `None` отбрасывается, `datetime`/`date` → ISO-строка, `bool` → `true`/`false`, `Enum` → значение (aiohttp принимает в query только str/int/float).

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
- Зависимости (`src/dependencies.py`): `AuthUserDep` / `get_current_user` (любой аутентифицированный), `get_admin_user` / `AdminUserDep` (только `ADMIN`, иначе 403), `get_editor_user` / `EditorUserDep` (`ADMIN` или `ANALYST`, иначе 403), `get_analyst_user` (только `ANALYST`, сейчас не используется).
- **Реальное покрытие авторизацией:**
  - только `ADMIN`: всё под `/api/rules/admin/*`, `PUT /api/engine-settings/` и `POST /api/engine-settings/reset`;
  - `ADMIN` или `ANALYST`: всё под `/api/rules/analyst/*`; изменяющие ручки `/correlation-rules` (`POST /`, `POST /test`, `PUT /{id}`, `DELETE /{id}`, `PATCH /{id}/status`), `/supersession-rules` (`POST /`, `POST /test`, `PUT /{id}`, `DELETE /{id}`, `PATCH /{id}/status`) `/ioc` (`POST /`, `PATCH /{id}`) `/assets` (`POST /`, `PUT /{id}`, `DELETE /{id}`) и `POST /engine-settings/validate`;
  - любой вошедший пользователь: `/users/me`, чтение `/rules` (`GET /`, `GET /{rule_id}`, `GET /enums/*`) и `/correlation-rules` (`GET /`, `GET /{id}`), `GET /engine-settings/`;
  - **без проверки токена**: `POST /users/`, `GET /users/`, `GET /users/{id}`, чтение `/ioc` и `/supersession-rules`, `/audits`, `/scenarios`, `/incidents`, `/organizations`, `/attack-types`, `/events`, `/mitre`, `/sources`, `/normalization-profiles`, `/data-quality`, чтение `/assets`, `GET /correlation-rules/sequence`, `/group-by-fields` и `/scenario-types`.
  `VIEWER` — только чтение: изменять правила обнаружения, корреляции, подавления и IOC не может.
- Пагинация `PaginationDep`: `limit` 1–19 (по умолчанию 10), `offset` ≥ 0. Применяется в `/rules` и `/audits`; остальные списки используют собственные параметры (`IncidentParams`, `ScenarioQueryParams`, `IocQueryDep` и т.д.).
- CORS: `allow_origins=["*"]` вместе с `allow_credentials=True`.

## 5. Версионирование правил и аудит

Для `detection_rules` каждое создание/изменение порождает **новую строку** с новым `unique_id`; неизменяемый идентификатор правила — `rule_id`.

Создание: строка в PG → запись аудита → документ в ES → `db.save()`.
Обновление: чтение текущего документа из ES (404, если нет; из него берутся `created_by`/`created_at`) → новая строка в PG (`rule_id` берётся из пути) → поиск последней записи аудита правила → новая запись аудита с `before_id` = предыдущая → у предыдущей `after_id` = новая → обновление документа в ES по `rule_id` → `db.save()`.
В ES-документ вместо id авторов пишутся имена (`created_by`, `updated_by`).
Для правил корреляции аналогичная цепочка в `correlation_audit`: версия правила пишется в `correlation_rules` при создании (`created`), изменении (`updated`), смене статуса (`status_changed`) и удалении (`deleted`, снимок до удаления). Чтение — `/api/audits/correlation-rules*` (`CorrelationAuditService`): список с фильтрами `action`/`author_id` и пагинацией, история одного правила, детальная запись с версией правила и `changes` — списком `{field, old, new}` относительно записи `before_id` (служебные поля id/даты/авторы не сравниваются). Отсутствующая запись → 404 (`AuditNotFoundException`, теперь и для `/audits/{id}`).

Смена статуса и тест правила выполняются через внешний API (`PATCH /detection-rules/{id}/status`, `POST /detection-rules/test`).

## 6. Модель данных (PostgreSQL)

**detection_rules** — `unique_id` (PK), `rule_id` (str 50), `enabled`, `rule_type`, `scope`, `match_type`, `pattern` (str 500), `fields[]`, `case_sensitive`, `condition_mode` (`all|any`), `conditions` (JSONB, список `{field, operator, value, case_sensitive}`), `category`, `attack_type`, `scenario_type`, `mitre_ids[]`, `tactics[]`, `severity_hint` (enum `info|low|medium|high|critical`), `confidence` (0–100, CHECK), `description`, `explanation_template`, `recommendations[]`, `enabled_reason`, `false_positive_notes`, `tags[]`, `created_at`, `updated_at`. Схема запроса повторяет `DetectionRule` из API движка: обязательны `rule_id`, `category`, `attack_type`, `description`, остальное с дефолтами движка.

**users** — `id`, `username` (unique, 50), `hashed_password` (bytes), `role` (`UserRoles`), `created_at`, `updated_at`.

**audit** — `id`, `author_id` → users, `action` (по умолчанию `create`), `resource_type`, `rule_general_id`, `rule_unique_id` → detection_rules, `before_id` / `after_id` → audit (SET NULL), `created_at`, `updated_at`.

**correlation_rules** — `id`, `correlation_id`, `enabled`, `scenario_type` (индекс), `description`, `window_seconds`, `sequence` (JSONB), `group_by` (JSONB), `min_unique_categories` (по умолчанию 1), `severity` (тот же enum), `confidence`, `recommendations` (JSONB), `tags` (JSONB), `mitre_ids` (JSONB, по умолчанию `[]`), `created_by`, `updated_by`, `created_at`, `updated_at`.

**correlation_audit** — аналог `audit` для правил корреляции (`correlation_id`, `correlation_unique_id` → correlation_rules, `before_id` / `after_id`).

Временные метки частично считаются в часовом поясе `Asia/Bishkek`. Миграции — `src/migrations/versions/` (Alembic, конфиг `alembic.ini`).

## 7. API (все пути с префиксом `/api`)

| Префикс | Эндпоинты |
|---|---|
| `/users` | `POST /login`, `POST /`, `GET /`, `GET /roles`, `GET /me`, `GET /{id}`, `DELETE /logout` |
| `/rules` | `GET /` (поиск: `pattern`, `rule_id`, `description` + пагинация), `GET /{rule_id}`, `GET /enums/severity-hints`, `GET /enums/detection-categories`, `GET /enums/detection-scopes` (прокси `/detection-categories`, `/detection-scopes`) |
| `/rules/admin` (ADMIN) | `POST /`, `PUT /{rule_id}`, `DELETE /{rule_id}`, `PATCH /{rule_id}` (статус), `POST /test` |
| `/rules/analyst` (ADMIN, ANALYST) | `POST /`, `PUT /{rule_id}` |
| `/audits` | `GET /engine` (журнал аудита внешнего API, прокси `GET /audit`: `size` по умолчанию 100, `resource_type`, `action`, `resource_id`, `organization_id`; ответ — список `EngineAuditSchema` со снимками `before`/`after`; нужен вход), `GET /correlation-rules`, `GET /correlation-rules/rule/{correlation_id}`, `GET /correlation-rules/{audit_id}` (история правил корреляции, нужен вход), `GET /rule/{rule_id}` (фильтр `action`: `created|updated`), `GET /`, `GET /{id}` |
| `/ioc` | `POST /`, `GET /`, `GET /{ioc_id}`, `PATCH /{ioc_id}` |
| `/supersession-rules` | `GET /`, `POST /`, `POST /test`, `GET /suppression-match-fields`, `GET /suppression-action-fields`, `GET /{super_id}`, `PUT /{super_id}`, `DELETE /{super_id}`, `PATCH /{super_id}/status` |
| `/correlation-rules` | `GET /`, `GET /sequence`, `GET /group-by-fields`, `GET /scenario-types`, `GET /{correlation_id}`, `POST /`, `POST /test`, `PUT /{correlation_id}`, `DELETE /{correlation_id}`, `PATCH /{correlation_id}/status` |
| `/scenarios` | `GET /`, `GET /{id}`, `GET /{id}/events` |
| `/incidents` | `GET /`, `GET /daily_count_incidents`, `GET /{inc_id}`, `GET /{inc_id}/events`, `GET /{inc_id}/artifacts` (`page` ≥ 1, `size` 1–200, по умолчанию 50; прокси `/hunting/incidents/{id}/artifacts`, ответ `IncidentArtifactsResponseSchema`), `PATCH /{inc_id}/status` |
| `/organizations` | `GET /`, `GET /agents`, `GET /{id}`, `POST /`, `PUT /{organization_id}`, `DELETE /{organization_id}` |
| `/attack-types` | `GET /` |
| `/events` | `GET /`, `GET /{index_name}/{event_id}` |
| `/mitre` | `GET /mitre`, `POST /sync-mitre` (итоговые пути: `/api/mitre/mitre`, `/api/mitre/sync-mitre`) |
| `/sources` | `GET /`, `POST /`, `GET /{source_id}/health`, `GET /{source_id}/sample-events`, `GET /{source_id}`, `PUT /{source_id}`, `DELETE /{source_id}` |
| `/normalization-profiles` | `GET /` (`enabled_only`), `POST /`, `GET /fields`, `POST /test`, `GET /{profile_name}`, `PUT /{profile_name}`, `DELETE /{profile_name}` |
| `/data-quality` | `GET /summary` (`hours` по умолчанию 24, `organization_id`, `source_id`, `profile_name`), `GET /sources` (`hours`, `organization_id`, `profile_name`), `GET /sources/{source_id}` (те же параметры) — прокси `/data-quality/*` внешнего API, ответы отдаются как есть |
| `/assets` | `GET /` (`enabled_only`, `asset_type`, `criticality`), `POST /` (201), `GET /{asset_id}`, `PUT /{asset_id}`, `DELETE /{asset_id}` — прокси `/assets` внешнего API; тело `AssetCreateUpdateSchema` (обязательны `organization_id`, `name`, `ip`; `asset_type` — `server|web_server|database|workstation|firewall|waf|ips|router|switch|domain_controller|wazuh_manager|elasticsearch|application|other`, `criticality` `low|medium|high|critical` (по умолчанию `medium`), `environment` `prod|test|dev|stage|lab`); `asset_id` генерирует внешний API; ответы отдаются как есть |
| `/engine-settings` | `GET /` (любой вошедший), `PUT /` (ADMIN), `POST /validate` (ADMIN, ANALYST), `POST /reset` (ADMIN) — прокси `/engine-settings*` внешнего API; тело `PUT`/`validate` — `EngineSettingsSchema` (`EngineSettings` движка): `settings_id` (по умолчанию `default`), `correlation` (`aggregation_window_seconds` 60, `attack_ttl_seconds` 900, `campaign_ttl_seconds` 1800; > 0), `ioc_scoring` (`boost_critical/high/medium/low` 10/10/5/0, `min_score_critical/high/medium/low` 90/70/50/30, 0–100), `asset_scoring` (`boost_*` 10/5/0/0, 0–100), `decision` (`critical/high/medium/low_score` 90/70/50/30, 0–100), `attack_tracker` (`attack_timeout_minutes` 15, `campaign_timeout_minutes` 30; > 0); пороги `decision` и `min_score_*` в `ioc_scoring` должны убывать (critical ≥ high ≥ medium ≥ low), иначе 422 — проверка дублирует проверку движка, чтобы текст ошибки не терялся; `updated_by` мы подставляем из имени текущего пользователя, но движок его игнорирует и пишет своего пользователя (сейчас `dev`), `updated_at` ставит движок. Ответы (в doc.json схемы пустые, сверено по фактическим ответам): `GET /` — `EngineSettingsResponseSchema` (настройки + `updated_by`, `updated_at`); `POST /validate` — `{valid, settings}` (`EngineSettingsValidateResponseSchema`); `PUT /` — `{success, settings}` (`EngineSettingsUpdateResponseSchema`); `POST /reset` — в OpenAPI описан как `{success, settings}` по аналогии с PUT, на живом движке не проверялся, отдаётся как есть |

Ограничения доступа см. в разделе 4. Порядок объявления маршрутов важен: статические пути (`/roles`, `/me`, `/sequence`, `/group-by-fields`, `/scenario-types`, `/suppression-match-fields`, `/suppression-action-fields`, `/daily_count_incidents`, `/agents`) стоят перед параметрическими `/{id}`.
`/correlation-rules`: тело `POST`/`PUT` соответствует `CorrelationRuleCreate`/`CorrelationRuleUpdate` API движка (обязательны `scenario_type`, `description`, `window_seconds`, `severity` — enum `critical|high|medium|low|info`, `confidence`; дополнительно у нас требуются непустые `sequence` и `group_by`; необязательный `mitre_ids` — список техник MITRE, значения из `GET /api/mitre/mitre`). Правило в `POST /test` — `CorrelationRuleTestData` движка: те же поля, но без `mitre_ids`. Ответы: `GET /`, `GET /{id}`, `POST /` (201), `PUT /{id}`, `PATCH /{id}/status` — правило `CorrelationRuleESSchema`; `DELETE /{id}` — `{correlation_id, deleted}`; в правиле есть `mitre_ids` (сохраняется в версии правила в PG и участвует в `changes` аудита); внешний API на `POST`/`PUT` отвечает `{status, rule, similar_rule_ids, warnings}`, на `PATCH /status` — `{status, rule}`, на `DELETE` — `{success, correlation_id}`, 404 — `Correlation rule not found`; `POST /test` — `{matched, scenario_type, severity, confidence, recommendations}`; `GET /sequence` — список `{value, label}`; `GET /group-by-fields` — `{items: [{value, label, description}], count}`; `GET /scenario-types` — `{items: [{value, label}], count}` (прокси `/reference/scenario-types`).
`/supersession-rules` (прокси `/suppression-rules` внешнего API; в его doc.json схемы ответов пустые, сверено по фактическим ответам): `GET /`, `GET /{id}` — правило `SuppressionRuleSchema` (`reason`, все поля `action` кроме `suppressed` могут быть null); `POST /` (201), `PUT /{id}`, `PATCH /{id}/status` — `{success, rule}`; `DELETE /{id}` — `{success, suppression_id}`; `POST /test` — `{matched, mode, reason, result: {severity, decision, risk_score, action, suppressed}}` (при `matched=false` остальное null); отсутствующее правило → 404. Запросы: `POST /` и `rule` в `/test` — обязательны `description` и `match` (хотя бы одно условие, `dst_port` 1–65535), `enabled` по умолчанию `true`, `action` необязателен, все его поля опциональны (`mode` только `suppress`; `decision` `malicious|suspicious|benign`; `severity` `critical|high|medium|low|info`; `action` `block|investigate|monitor|ignore`; `risk_score` 0–100; `suppressed` по умолчанию `true`). `PUT /{id}` — тело `SuppressionRuleUpdate`: `description`, `match` (обязательны, `match` передаётся целиком), `reason`, `action`, `tags`; `action` — объект `SuppressionAction`, как в `POST /` (рекомендуемый вариант), либо строка `block|investigate|monitor|ignore` вместе с плоскими `decision`, `risk_score`, `suppressed`, `suppression_reason` (старый формат, оставлен для совместимости), либо null; `enabled` через PUT не меняется, неуказанные необязательные поля сбрасываются. `GET /suppression-action-fields` — прокси справочника полей `action` `{items: [{field, path, label, description, type, ui_control, multiple, required, default, values, reference, min, max}], count, frontend_rules}`.
`GET /users/` принимает параметр `department_id`, `GET /rules/` — `pattern`, `rule_id`, `description` (ответ всегда `RuleApiResponseSchema` `{total, has_next, items}`: при `rule_id` — страница из 0 или 1 правила, иначе поиск: `pattern` по полю `pattern`, `description` по полю `description`; `offset + limit` не больше 10000).

## 8. Ошибки

Исключения объявлены в `src/exceptions/exceptions.py`: `NoResultException` → `ObjectNotFoundException` → (`RuleNotFoundException`, `AuditNotFoundException`), `UserNotFoundException`; `UniqueObjIsExistException` → `RuleAlreadyExistException`; `HasNotRightsException`; `InvalidSearchParamsException`; `StorageUnavailableException`. У каждого есть русскоязычное поле `detail`.

`setup_exceptions` (`exception_handler.py`) возвращает `JSONResponse` вида `{"detail": "..."}` (схема `ErrorResponseSchema` в `src/exceptions/schemas.py`):

| Исключение | HTTP |
|---|---|
| `RuleNotFoundException` | 404 |
| `AuditNotFoundException` | 404 |
| `RuleAlreadyExistException` | 400 |
| `InvalidSearchParamsException` | 400 |
| `StorageUnavailableException` (ES недоступен или вернул ошибку) | 503 |
| `aiohttp.ClientResponseError` внешнего API: 404 | 404 |
| то же: 400 / 409 / 422 | тот же код |
| то же: 401 / 403 / 5xx | 502 |
| `aiohttp.ClientConnectionError` | 502 |
| `TimeoutError` (таймаут запроса к внешнему API) | 504 |

Ошибки Elasticsearch переводятся в исключения приложения в `src/repositories/elastic/base.py` (`_handle_es_errors`): `BadRequestError` → `InvalidSearchParamsException`, ошибки соединения и прочие `ApiError` → `StorageUnavailableException`; отсутствующий индекс при поиске даёт пустую выдачу.
Остальные (`ObjectNotFoundException`, `UserNotFoundException`, `HasNotRightsException`) обработчиков не имеют, если только сервис не конвертирует их сам (как `RuleService.find_one`: `ObjectNotFoundException` → `RuleNotFoundException`).
Для OpenAPI ошибки описываются на роутах через `responses=error_responses(...)`.

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
- Опечатки в тегах Swagger («Истороия изменений», «Айок») — косметика, но видна в документации.
- `/rules/admin` доступен только `ADMIN`; `/rules/analyst` — `ADMIN` и `ANALYST`.
- Большинство эндпоинтов, включая создание пользователей (`POST /users/`), не требуют аутентификации (см. раздел 4).
- В `src/users/api.py` две функции названы `get_me` (для `/me` и `/{id}`); работает, так как регистрация идёт по декоратору.
- В `update_rule` `resource_type` аудита заполняется значением `rule_id`.
