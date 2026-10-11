# jane-kit: інтеграція

Як сервіс використовує кожну можливість бібліотеки, як викликає інші сервіси й перевіряє себе контрактними тестами. Приклади коду на цій сторінці зібрано в один скрипт і виконано з `uv run --all-packages python` на ревізії `48389a3`; показаний вивід — з цього запуску.

## Зміст

- [Збирання застосунку](#збирання-застосунку)
- [Автентифікація й scopes](#автентифікація-й-scopes)
- [Помилки](#помилки)
- [Ідемпотентність](#ідемпотентність)
- [Асинхронні job](#асинхронні-job)
- [Пагінація](#пагінація)
- [Health, метрики, журнали](#health-метрики-журнали)
- [Секрети й ContentRef](#секрети-й-contentref)
- [Сховища для кількох екземплярів](#сховища-для-кількох-екземплярів)
- [Клієнти інших сервісів](#клієнти-інших-сервісів)
- [Контрактні тести й моки](#контрактні-тести-й-моки)
- [Інтеграційні тести з dev-стеком](#інтеграційні-тести-з-dev-стеком)
- [Композиція в Jane і заміна](#композиція-в-jane-і-заміна)

## Збирання застосунку

`create_app(settings, ...)` повертає FastAPI-застосунок із підключеними журналами, трасуванням, помилками Problem, `/v1/health`, `/v1/info`, `/metrics` і автентифікацією.

| Параметр | Призначення |
|---|---|
| `settings` | Екземпляр підкласу `JaneSettings` |
| `title`, `version` | Назва в OpenAPI; версія в `/v1/info` (типово `0.1.0`) |
| `api_versions` | Перелік у `/v1/info` (типово `("v1",)`) |
| `capabilities` | Словник або функція без аргументів для `/v1/info.capabilities` |
| `lifespan` | Власний async context manager старту й зупинки |
| `limits` | `ResolvedLimits` сервісу — публікується в `/v1/info.limits` |
| `configure_logs` | `False` — не чіпати налаштування журналів (тести) |
| `auth_scopes` | Таблиця `"METHOD /path" -> scope` для всіх маршрутів |
| `authenticator` | Готовий `Authenticator` замість зібраного з налаштувань (тести) |

Після створення доступні `app.state.settings`, `app.state.health` (реєстр перевірок) і `app.state.metrics` (якщо `metrics_enabled`). Запуск — `jane_kit.service.run(app, settings)`: uvicorn на `settings.host:settings.port` з журналами бібліотеки. Мінімальний приклад — [швидкий старт](quickstart.md).

Типова модель лімітів сервісу збирає вбудовані групи:

```python
from pydantic_settings import SettingsConfigDict

from jane_kit.config import JaneSettings, Limits, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits
from jane_kit.pagination import PageLimits


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix="DEMO_", extra="ignore", env_nested_delimiter="__")
    service_name: str = "demo"


class DemoLimits(Limits):
    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()
    pages: PageLimits = PageLimits()


settings = Settings()
resolved = resolve_limits(DemoLimits, *settings.platform_layers("DEMO_LIMITS__"))
limits = resolved.limits
```

## Автентифікація й scopes

Є два способи перевіряти scopes.

**Таблиця сервісу** (рекомендовано): `create_app(..., auth_scopes={...})`. На старті `check_scopes` вимагає рядок для кожного маршруту — інакше `AuthConfigError`; маршрут без рядка під час запиту отримує `403` (fail closed). Значення — один scope або кортеж «будь-який із»; порожній кортеж (`AUTHENTICATED`) — будь-який чинний токен. Вбудовані маршрути (`GET /v1/info`, OpenAPI-сторінки) додаються автоматично.

Таблиці операцій усіх контрактів готові в `jane_kit.auth_scopes`: `COLLECTOR`, `HANDLER`, `STORAGE`, `LLM`, `ASSISTANT`, `REGISTRY`, `ORCHESTRATOR`. Сервіс, що реалізує кілька API, об'єднує їх:

```python
from jane_kit.auth_scopes import HANDLER, STORAGE, merge

scopes = merge(HANDLER, STORAGE)
print(scopes["POST /v1/invocations"])  # ('handler:invoke',)
```

Тест бібліотеки `test_auth_scopes.py` тримає кожну таблицю рівною полям `x-jane-scope` її контракту.

**Перевірка в обробнику** — коли таблиці немає (`auth_scopes=None`): залежність `require(...)` повертає `Principal` виклику.

```python
from fastapi import Depends

from jane_kit.auth import Principal, require


@app.delete("/v1/cache")
async def clear_cache(caller: Principal = Depends(require("demo:admin"))) -> dict[str, str]:
    return {"cleared_by": caller.name}
```

`principal_of(request)` повертає `Principal` без перевірки scope. Для викликів інших сервісів власним токеном — `bearer_header(token)`. Параметри режимів — [конфігурація](configuration.md#автентифікація).

## Помилки

Сервіс кидає `JaneError` або підклас — бібліотека перетворює його на відповідь `application/problem+json` з `type` = `urn:jane:problem:<code>`, `trace_id` і `instance`. Статус і `retryable` беруться з каталогу `KNOWN_CODES` (дзеркало [contracts/docs/errors.md](../../../contracts/docs/errors.md)).

| Клас | Код | Статус |
|---|---|---|
| `BadRequest` | `bad_request` | 400 |
| `Unauthenticated` | `unauthenticated` | 401 |
| `Forbidden` | `forbidden` | 403 |
| `NotFound` | `not_found` | 404 |
| `Conflict` | `conflict` | 409 |
| `ValidationFailed` | `validation_failed` | 422 |
| `LimitExceeded` | `limit_exceeded` | 422 |
| `RateLimited` | `rate_limited` | 429 |
| `UpstreamUnavailable` | `upstream_unavailable` | 502 |
| `ServiceUnavailable` | `service_unavailable` | 503 |
| `Timeout` | `timeout` | 504 |

Інший код — `JaneError("...", code="digest_mismatch")`. Аргументи: `detail`, `errors` (список `FieldError` з `pointer` або `parameter`), `details`, `retry_after_seconds` (додає заголовок `Retry-After`), `headers`. Помилки валідації FastAPI стають `422 validation_failed` з JSON Pointer у `errors[].pointer`, неправильний JSON — `400 bad_request`, `404`/`405` маршрутизації — Problem із відповідним кодом, необроблений виняток — `500 internal_error` і запис у журнал.

## Ідемпотентність

`idempotent(request, store, handler)` виконує `handler` один раз на `Idempotency-Key`:

- той самий ключ і те саме тіло — збережена відповідь і `Idempotency-Replayed: true`;
- той самий ключ з іншим тілом — `422 idempotency_key_reused`;
- запит із ключем ще виконується — `409 idempotency_in_progress` (`retryable: true`);
- без заголовка — `422 validation_failed` (`required=False` виконує без ключа);
- `handler` упав — ключ звільняється, повтор можливий.

Відбиток запиту — SHA-256 методу, шляху й тіла. Приклад разом із job — у наступному розділі. Для одного екземпляра — `InMemoryIdempotencyStore`, для кількох — [спільні сховища](#сховища-для-кількох-екземплярів). Нижчий рівень без FastAPI — `run_idempotent(store, key, fingerprint, handler)`.

## Асинхронні job

`JobRunner` виконує корутини в циклі подій процесу з лімітами `JobLimits`; `jobs_router(runner)` додає `GET /v1/jobs/{job_id}` і `POST /v1/jobs/{job_id}/cancel` за `common.yaml`.

```python
from typing import Any

from fastapi import Request, Response
from pydantic import BaseModel

from jane_kit.idempotency import IDEMPOTENCY_HEADER, InMemoryIdempotencyStore, StoredResponse, idempotent
from jane_kit.jobs import JobContext, JobRunner, jobs_router
from jane_kit.service import create_app

runner = JobRunner(limits=limits.jobs)
idem = InMemoryIdempotencyStore(limits.idempotency)
app = create_app(
    settings,
    limits=resolved,
    auth_scopes={
        "POST /v1/reports": "demo:write",
        "GET /v1/items": "demo:read",
        "GET /v1/jobs/{job_id}": "demo:read",
        "POST /v1/jobs/{job_id}/cancel": "demo:write",
    },
)
app.include_router(jobs_router(runner))


class ReportRequest(BaseModel):
    pages: int = 3


@app.post("/v1/reports", status_code=202)
async def start_report(body: ReportRequest, request: Request) -> Response:
    async def handler() -> StoredResponse:
        async def work(ctx: JobContext) -> dict[str, Any]:
            for page in range(body.pages):
                await ctx.check_cancelled()
                await ctx.progress(page + 1, body.pages, unit="pages")
            return {"pages": body.pages}

        job = await runner.submit("report", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER))
        return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})

    return await idempotent(request, idem, handler, limits=limits.idempotency)
```

Поведінка з цим кодом (виклики через `TestClient`, `Idempotency-Key: r-1`):

```text
POST /v1/reports {"pages": 2}  -> 202 /v1/jobs/job_ef6b6cd93bf74201b3711114a33aa416
POST /v1/reports {"pages": 2}  -> 202, Idempotency-Replayed: true, той самий job_id
POST /v1/reports {"pages": 5}  -> 422 idempotency_key_reused
POST /v1/reports без ключа     -> 422 validation_failed
GET  /v1/jobs/<id>             -> succeeded {'pages': 2}
```

Можливості `JobContext`: `progress(completed, total, unit=, message=, counters=)`, `cancelled()`, `check_cancelled()` (кидає `JobCancelledError`). Результат job — словник, що повертає корутина; великий результат передавайте як `ContentRef` у `result_ref`. Відповідь `202` без ідемпотентності — `accepted(job)`. Стани й переходи — [будова](internals.md#стани-job).

## Пагінація

```python
from jane_kit.pagination import clamp_limit, decode_cursor, encode_cursor

ITEMS = [f"item-{i}" for i in range(7)]


@app.get("/v1/items")
async def list_items(limit: int | None = None, cursor: str | None = None) -> dict[str, Any]:
    size = clamp_limit(limit, limits.pages)
    start = decode_cursor(cursor) if cursor else 0
    chunk = ITEMS[start : start + size]
    nxt = start + size
    return {"items": chunk, "next_cursor": encode_cursor(nxt) if nxt < len(ITEMS) else None}
```

```text
GET /v1/items?limit=3              -> {'items': ['item-0', 'item-1', 'item-2'], 'next_cursor': 'Mw'}
GET /v1/items?limit=3&cursor=Mw    -> {'items': ['item-3', 'item-4', 'item-5'], 'next_cursor': 'Ng'}
GET /v1/items?cursor=%%%           -> 422 validation_failed
```

Курсор — base64url від JSON позиції (для клієнта непрозорий). `limit` понад `max_page_size` обрізається, а не відхиляється. Модель відповіді — `Page[T]`.

## Health, метрики, журнали

```python
app.state.health.add("disk", lambda: True)
app.state.health.add("cache", lambda: "degraded", critical=False)
exports = app.state.metrics.counter("exports_total", "Exports by format", ["format"])
exports.labels("csv").inc()
```

```text
GET /v1/health -> {'status': 'degraded', 'checks': {'disk': {'status': 'ok'}, 'cache': {'status': 'degraded'}}}
GET /metrics   -> jane_exports_total{format="csv"} 1.0
```

Перевірка повертає `True`/`False`, рядок `ok`/`degraded`/`down` або кидає виняток; може бути async. Некритична перевірка (`critical=False`) робить сервіс щонайбільше `degraded`. `down` дає HTTP `503`. Метрики: `counter`, `gauge`, `histogram` з простором імен `jane`.

Журнали — JSON-рядок на запис. Додати поля до всіх записів блоку — `bind_context(source_id=..., task_id=...)`; поля конкретного запису — `extra={...}`. Вхідний `traceparent` продовжує трасу, `trace_id` потрапляє в журнали й Problem; вихідний виклик отримує `child_traceparent(trace_id)` (це робить `ServiceClient`). Формат і назви метрик — [експлуатація](operations.md).

## Секрети й ContentRef

`SecretPolicy` обмежує `secret_refs` керованих підключень: `env:` лише для змінних із префіксом `JANE_SECRET_`, `file:` лише всередині `/run/secrets`, `vault:` відхиляється. `violations(refs)` дає `FieldError` з кодом `secret_ref_not_allowed` для відповіді `422` на `PUT /v1/connections/{id}`; `resolve(ref)` повертає значення або `None`. `HostAllowlist` і `OriginAllowlist` обмежують, куди підключення може надіслати секрет.

`ContentReader.read(ref, max_bytes=...)` читає `ContentRef`: `inline` (UTF-8 або base64), `blob` з `download_url` (лише хости allowlist, без редиректів) або `file://` (лише всередині `blob_roots`); перевіряє `size_bytes` і `sha256`. `s3://` без `download_url` не читається — у бібліотеки немає облікових даних сховищ. `ContentWriter.ref(body, media_type, name)` вирішує, як доставити вміст: inline до `inline_max_bytes`, інакше транзитний blob у `FileTransitStore` (`<root>/<producer>/<YYYY>/<MM>/<DD>/<name><ext>`); `FileTransitStore.cleanup(ttl)` прибирає старі файли. Транзит у S3/MinIO бібліотека не реалізує. Параметри — [конфігурація](configuration.md#читання-contentref-і-секрети).

## Сховища для кількох екземплярів

Сховища в пам'яті підходять одному екземпляру. Кілька екземплярів ділять job і ключі через таблиці власної бази сервісу:

| Клас | База | Для кого |
|---|---|---|
| `PgIdempotencyStore`, `PgJobStore` | PostgreSQL (`jane-kit[postgres]`) | Сервіси з власною базою PostgreSQL |
| `SqliteIdempotencyStore`, `SqliteJobStore` | Файл SQLite (WAL) | Екземпляри на одному вузлі зі спільним файлом стану |
| `SqliteWorkJobStore` | Файл SQLite | Job, що віддзеркалює «робочий рядок» сервісу (збирання колектора) |

Підключення PostgreSQL у lifespan сервісу (з `LeaseLimits` у моделі лімітів як група `state`):

```python
import asyncio
from contextlib import asynccontextmanager

from jane_kit.stores import heartbeat_loop
from jane_kit.stores.postgres import PgDatabase, PgIdempotencyStore, PgJobStore, migrate

db = PgDatabase(settings.database_dsn, max_size=10, connect_timeout_ms=5_000)
idem = PgIdempotencyStore(db.tx, owner=settings.instance_id, in_progress_lease_s=limits.state.in_progress_lease_ms / 1000)
jobs = PgJobStore(
    db.tx,
    owner=settings.instance_id,
    lease_s=limits.state.job_lease_ms / 1000,
    retention_s=limits.jobs.job_retention_seconds,
)
runner = JobRunner(store=jobs, limits=limits.jobs)


@asynccontextmanager
async def lifespan(app):
    db.open()
    migrate(db.tx, "demo-schema", idem, jobs)
    beat = asyncio.create_task(
        heartbeat_loop([idem.heartbeat, jobs.heartbeat, jobs.sweep], limits.state.heartbeat_interval_ms / 1000)
    )
    yield
    beat.cancel()
    await runner.shutdown()
    db.close()
```

`settings.database_dsn` — поле, яке сервіс оголошує сам. Цей фрагмент окремо не виконувався; робочі приклади того самого підключення — `app.py` LLM gateway (`services/llm/src/jane_llm/app.py`) і Orchestrator (`services/orchestrator/src/jane_orchestrator/app.py`). PostgreSQL-сховища використовують Orchestrator, Registry, LLM gateway, Assistant і Handler Runtime, SQLite-сховища — колектори. Правила оренди й fencing — [будова](internals.md#сховища-стану).

## Клієнти інших сервісів

`ServiceClient(base_url, limits=ClientLimits(), headers=...)` — async-клієнт із тайм-аутами з `ClientLimits`, повторами для безпечних методів і запитів з `Idempotency-Key`, урахуванням `Retry-After`, передаванням `traceparent` і `X-Request-ID`. Помилкова відповідь стає `RemoteError` з розібраним `Problem` і властивістю `retryable`. `wait_for_job(location)` опитує job до кінцевого стану.

```python
import httpx

from jane_kit.clients import ServiceClient

async with ServiceClient("http://handler", transport=httpx.ASGITransport(app=mock)) as client:
    print(await client.get_json("/v1/health"))
    body = await client.post_json("/v1/invocations", invocation, idempotency_key=client.new_idempotency_key())
```

```text
{'status': 'ok', 'checks': {'state_store': {'status': 'ok'}}}
success ['delivery_key', 'diagnostics', 'duplicate', 'finished_at', 'handler', 'handler_kind']
RemoteError 404 not_found False      # get_json("/v1/jobs/x", headers={"Prefer": "code=404"})
```

Тут `mock` — мок `handler.v1` з наступного розділу, `invocation` — приклад [invocation-extract.json](../../../contracts/examples/openapi/invocation-extract.json). У робочому коді `transport` не передають, а `headers=bearer_header(token)` додає токен.

**Згенерований клієнт.** `jane-codegen` будує пакет `client.py` з async-методом на кожну операцію (назва — `operationId` у snake_case) поверх `ServiceClient`:

```powershell
just contracts-gen storage services/<сервіс>/src/jane_<сервіс>/_generated/storage
```

```text
$ uv run --all-packages jane-codegen client contracts/openapi/storage.v1.yaml --out .../gen/storage --no-models
generated ...\gen\storage
```

Згенерований клас — `JaneStorageReadApiClient` з методами `list_entities`, `get_object`… Для контрактів Jane рецепт генерує клієнт без Pydantic-моделей (`--no-models`): `datamodel-code-generator` не приймає багатофайлові контракти. Каталоги `_generated/` ruff і mypy пропускають; код не редагують, а генерують знову. Для довільної специфікації з моделями — `just gen-client <spec> <out>` або `jane-codegen models <spec> --out <file.py>`.

## Контрактні тести й моки

- `OpenAPISpec.load(path)` — документ із `$ref` між файлами; `validate_component(name, body)`, `validate_request`, `validate_response`.
- `ContractClient(spec, TestClient(app))` перевіряє кожну відповідь справжнього сервісу проти контракту (`ContractViolation`), `uncovered()` перелічує операції без викликів. Тест позначають `@pytest.mark.contract`.
- `build_mock_app(spec)` — ASGI-мок сусіда: перший приклад першої успішної відповіді, інший — заголовком `Prefer: code=404` або `Prefer: example=<name>`; невалідне тіло запиту — `422`.
- `contracts_dir()` знаходить `contracts/` поточного checkout (або `JANE_CONTRACTS_DIR`).

```python
from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec, build_mock_app, contracts_dir

common = OpenAPISpec.load(contracts_dir() / "openapi" / "common.yaml")
with TestClient(app) as c:
    common.validate_component("Health", c.get("/v1/health").json())
    common.validate_component("ServiceInfo", c.get("/v1/info").json())

mock = build_mock_app(OpenAPISpec.load(contracts_dir() / "openapi" / "handler.v1.yaml"))
```

Правило Jane: мок — лише для сусідів і лише з контракту; сам компонент не мокають. Повний приклад контрактного тесту — [templates/service/tests/test_contract.py](../../../templates/service/tests/test_contract.py). Валідація даних за JSON Schema в робочому коді — `ContractSchemas.locate(...)`, правила колектора — `CollectorSchemas` і `RulesLoader`.

## Інтеграційні тести з dev-стеком

`jane_kit.devstack.load_stack()` повертає `StackInfo` (адреси й облікові дані стеку `just up`) або `None`, якщо стек не запущено, — тест тоді пропускається. `just integration` передає файл стеку через `JANE_STACK_FILE`, тому тест не підхопить чужий стек. `StackInfo.url("postgres")`, `StackInfo.get("db-orchestrator", "db_dsn")`; ключі API — змінні `JANE_API_KEY_<IDENTITY>` (`api_key_var("admin")`). Команди — [перевірки](../../development/checks.md#dev-стек).

## Композиція в Jane і заміна

- Усі сервіси Jane (`services/*`) і шаблон сервісу підключають `jane-kit` як залежність workspace; спільну логіку не дублюють у сервісах.
- Сторонній Python-сервіс на FastAPI може використати бібліотеку так само, як у [швидкому старті](quickstart.md), щоб отримати конвенції Jane без власного коду.
- Бібліотека не є обов'язковою для сумісності: сервіс іншою мовою замінює модуль Jane, якщо виконує його контракт із [contracts](../contracts/README.md) — `/v1`, Problem, `Idempotency-Key`, job, scopes. Перевірка — контрактні тести проти OpenAPI (`ContractClient` або schemathesis).
