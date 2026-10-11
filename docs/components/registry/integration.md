# Registry: інтеграція

Registry — звичайний HTTP-сервіс із контрактом `registry.v1`: сторонній застосунок може зберігати в ньому власні пакети, шукати їх і завантажувати архіви, не запускаючи решту Jane. У складі Jane він — спільне джерело версій пакетів для Orchestrator, Assistant, Admin UI й виконавців. Деталі кожної операції — [довідник API Registry](reference/api/README.md); контракт — [registry.v1.yaml](../../../contracts/openapi/registry.v1.yaml).

## Зміст

- [Конвенції API](#конвенції-api)
- [Автентифікація](#автентифікація)
- [Клієнт на Python](#клієнт-на-python)
- [Пошук пакетів](#пошук-пакетів)
- [Читання версії й файлів](#читання-версії-й-файлів)
- [Звіти тестів](#звіти-тестів)
- [Перенесення змін батька](#перенесення-змін-батька)
- [Місце в Jane](#місце-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Конвенції API

| Конвенція | У Registry |
|---|---|
| Версія API | префікс `/v1` |
| Помилки | `application/problem+json` з `code`, `retryable`, `errors[]`, `trace_id` ([errors.md](../../../contracts/docs/errors.md)) |
| Ідемпотентність | заголовок `Idempotency-Key` обов'язковий для кожного `POST`; повтор повертає збережену відповідь із `Idempotency-Replayed: true` |
| Пагінація | `?limit=&cursor=`, відповідь `{"items": [...], "next_cursor": ...}`; типово 50, найбільше 500 |
| Асинхронні операції | `POST …/upstream-ports` повертає `202` і job; стан — `GET /v1/jobs/{job_id}` |
| Оптимістичне блокування | `PATCH /v1/packages/{id}` приймає `If-Match` з `ETag` пакета (`"r<revision>"`); розбіжність — `412 precondition_failed` |
| Розмір тіла | до `transfer.max_request_body_bytes` (типово 30 MiB), більше — `413 payload_too_large` |

## Автентифікація

Запити передають `Authorization: Bearer <токен>`. Режим задає `JANE_REGISTRY_AUTH_MODE` ([configuration.md](configuration.md#автентифікація)):

| Scope | Операції |
|---|---|
| `registry:read` | усі `GET`, зокрема архіви, diff і job |
| `registry:write` | створення й зміна пакета, публікація, форк, звіти тестів, перенесення змін, скасування job |
| `registry:approve` | зміна статусу версії; увімкнення `auto_changes_allowed` для пакета, де воно було вимкнене |

`/v1/health` доступний без токена, `/metrics` — без токена, якщо не вимкнено `JANE_REGISTRY_METRICS_PUBLIC`. Ключ API може мати атрибут `actor` (`human`, `llm`, `import`): клієнт з `actor: llm` публікує лише версії з `provenance.created_by: llm` ([Походження й форки](../../reference/packages/provenance-and-forks.md#хто-може-публікувати-автоматично)).

У dev-стеку (`just up … registry`) режим `api_key`; запит без ключа дає `401`:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:63986/v1/packages
```

```text
401
```

Адресу й ключ адміністратора стеку показує `just env` (`JANE_STACK_REGISTRY_URL`, `JANE_STACK_AUTH_ADMIN_API_KEY`).

## Клієнт на Python

Мінімальний сторонній клієнт: створює пакет правил, публікує версію JSON-тілом і перевіряє дайджест завантаженого архіву. Потрібен лише `httpx`; Registry запущено як у [quickstart](quickstart.md).

```python
import hashlib
import json
import uuid

import httpx

REGISTRY = "http://127.0.0.1:18400"
rules = {"collector": "telegram", "channels": [{"username": "jane_events_example"}]}
manifest = {
    "schema_version": "1",
    "package_id": "my.channel-rules",
    "version": "1.0.0",
    "kind": "collector-rules",
    "title": "My channel rules",
    "entry": {"collector": "telegram", "rules": "rules.json"},
    "provenance": {"created_by": "human"},
}

with httpx.Client(base_url=REGISTRY, timeout=30) as client:

    def post(path: str, body: dict) -> httpx.Response:
        # a new key per logical operation; reuse it when retrying the same operation
        return client.post(path, json=body, headers={"Idempotency-Key": str(uuid.uuid4())})

    r = post("/v1/packages", {"package_id": "my.channel-rules", "kind": "collector-rules", "title": "My channel rules"})
    print("create:", r.status_code)
    r = post(
        "/v1/packages/my.channel-rules/versions",
        {"manifest": manifest, "files": {"rules.json": {"encoding": "utf-8", "data": json.dumps(rules) + "\n"}}},
    )
    r.raise_for_status()
    version = r.json()
    print("publish:", r.status_code, version["version"], version["status"], version["digest"])

    archive = client.get("/v1/packages/my.channel-rules/versions/1.0.0/archive")
    actual = "sha256:" + hashlib.sha256(archive.content).hexdigest()
    print("archive:", len(archive.content), "bytes, digest matches:", actual == version["digest"])
```

Запуск (файл збережено як `client_example.py`):

```powershell
uv run --with httpx --no-project python client_example.py
```

```text
create: 201
publish: 201 1.0.0 draft sha256:b9d0191dd8d5b97a2c02f726a731dc9087eefb86de866f952f37bda245b007fe
archive: 573 bytes, digest matches: True
```

Для повторних спроб використовуйте той самий `Idempotency-Key`, що й у першій спробі: тоді повтор після обриву зв'язку не створить дубль. Готовий типізований клієнт генерує `just contracts-gen registry <каталог>`.

## Пошук пакетів

`GET /v1/packages` фільтрує за полями пакета й маніфесту його останньої версії:

| Параметр | Збіг |
|---|---|
| `kind` | тип пакета |
| `q` | підрядок без урахування регістру в `package_id`, назві, описі, тегах, типах сутностей |
| `tag` | точний тег |
| `entity_type` | тип сутності з `output.entities[]` |
| `media_type` | медіатип із `input.media_types`, з урахуванням `text/*` і `*/*` |
| `domain` | домен із `bindings_hint.domains` або його піддомен |
| `fork_of` | лише форки вказаного пакета |

Пакети сортуються за `package_id`. Запит після [quickstart](quickstart.md):

```bash
curl -s "http://127.0.0.1:18400/v1/packages?kind=extractor&entity_type=product&media_type=text/html"
```

```json
{"items":[{"package_id":"examples.testsite-price-extractor","kind":"extractor","title":"Jane test site: price and availability only","latest_version":"1.0.0","auto_changes_allowed":true,"deprecated":false,"created_at":"2026-10-11T10:31:02.234Z","updated_at":"2026-10-11T10:31:11.845Z"},{"package_id":"my.price-extractor","kind":"extractor","title":"My price extractor","latest_version":"1.0.0","auto_changes_allowed":false,"deprecated":false,"created_at":"2026-10-11T10:31:12.095Z","updated_at":"2026-10-11T10:31:12.318Z","fork_of":{"package_id":"examples.testsite-price-extractor","version":"1.0.0","digest":"sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"}}],"next_cursor":null}
```

Наявність пакета в результатах пошуку не означає, що його застосовують: прив'язки задає етап завдання в Orchestrator.

## Читання версії й файлів

| Запит | Відповідь |
|---|---|
| `GET /v1/packages/{id}` | Пакет, `ETag`, `forks_count` |
| `GET /v1/packages/{id}/versions?status=` | Версії від новіших до старіших, без маніфесту |
| `GET /v1/packages/{id}/versions/{v}` | Повна версія: `manifest`, `files` (шлях, розмір, sha256), `status_history`, `test_reports`, `test_summary` |
| `GET /v1/packages/{id}/versions/{v}/archive` | Канонічний ZIP; `ETag` і `X-Jane-Package-Digest` = `digest` |
| `GET /v1/packages/{id}/versions/{v}/file?path=<шлях>` | Один файл: `text/plain; charset=utf-8` для тексту, інакше `application/octet-stream` |

Приклад читання одного файлу:

```bash
curl -s "http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions/1.0.0/file?path=schemas/params.schema.json"
```

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "examples.testsite-price-extractor params",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "default_currency": {
      "description": "Валюта, якщо сторінка її не вказує.",
      "type": "string",
      "pattern": "^[A-Z]{3}$",
      "default": "UAH"
    }
  }
}
```

## Звіти тестів

Registry не запускає тести; виконавець або CI записує `TestReport` у версію. Звіт, отриманий `jane-handler-runtime test … -o report.json`, загортається в `{"runner": …, "context": …, "report": …}`:

```bash
curl -s -X POST http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions/1.0.0/test-results -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-tests-1' --data-binary @.jane/registry-quickstart/test-results.json
```

Уривок відповіді (поля версії `version`, `status`, `test_status`, `test_summary`):

```json
{
  "version": "1.0.0",
  "status": "approved",
  "test_status": "passed",
  "test_summary": {
    "status": "passed",
    "contexts": [
      {"test_status": "passed", "reports": 1, "context": "local", "recorded_at": "2026-10-11T10:00:18.218Z", "runner": "jane-handler-runtime test"}
    ]
  }
}
```

Правила обчислення `test_status` і `test_summary` — [Схеми й тести](../../reference/packages/schemas-and-tests.md#звіти-тестів-у-версії).

## Перенесення змін батька

Перенесення — асинхронна команда з опитуванням job. Послідовність, виконана на форку з [quickstart](quickstart.md) після того, як у батька з'явилася версія `1.1.0`, а у форку — власна `1.1.0`:

1. Перевірити, чи є нові версії батька:

   ```bash
   curl -s http://127.0.0.1:18400/v1/packages/my.price-extractor/upstream
   ```

   ```json
   {"fork_of":{"package_id":"examples.testsite-price-extractor","version":"1.0.0","digest":"sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"},"last_ported_version":"1.0.0","parent_latest_version":"1.1.0","newer_parent_versions":["1.1.0"]}
   ```

2. Запустити перенесення:

   ```bash
   curl -s -i -X POST http://127.0.0.1:18400/v1/packages/my.price-extractor/upstream-ports -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-port-1' -d '{"parent_version": "1.1.0", "new_version": "1.2.0"}'
   ```

   Уривок (заголовки `date`, `server`, `x-request-id` прибрано):

   ```text
   HTTP/1.1 202 Accepted
   location: /v1/jobs/job_4082f049d51043c99db815c1ae557f43
   content-type: application/json

   {"job_id":"job_4082f049d51043c99db815c1ae557f43","kind":"upstream_port","status":"queued","created_at":"2026-10-11T09:59:09.069390Z","idempotency_key":"qs-port-1","links":{"self":"/v1/jobs/job_4082f049d51043c99db815c1ae557f43","cancel":"/v1/jobs/job_4082f049d51043c99db815c1ae557f43/cancel"},"labels":{"package_id":"my.price-extractor"}}
   ```

3. Опитувати `GET /v1/jobs/{job_id}`, доки `status` не стане `succeeded`, `failed` або `cancelled`. Уривок успішного job (без поля `result`):

   ```json
   {"job_id": "job_4082f049d51043c99db815c1ae557f43", "kind": "upstream_port", "status": "succeeded", "progress": {"completed": 2, "total": 2, "unit": "steps", "message": "published 1.2.0"}, "labels": {"package_id": "my.price-extractor"}}
   ```

   `result` містить нову версію `1.2.0` форку (`status: draft`) з `provenance.upstream_port.parent_version: "1.1.0"`. За конфлікту `status: failed`, а `error.code` — `upstream_conflict` з переліком конфліктних файлів ([приклад](../../reference/packages/provenance-and-forks.md#перенесення-змін-батька)).

Перенесена версія не активується автоматично: її, як і будь-яку іншу, перевіряють тестами, погоджують і активують в етапі.

## Місце в Jane

Registry не викликає інші сервіси Jane (крім читання профілів runtime) — до нього звертаються:

| Клієнт | Що робить | Налаштування адреси |
|---|---|---|
| Admin UI | Перегляд пакетів, diff, зміна статусів, форки | через proxy dev-стеку |
| Assistant | Шукає пакети, публікує нові версії й форки (`actor: llm`), погоджує версії за політикою автоактивації | `JANE_ASSISTANT_REGISTRY_URL` |
| Orchestrator | Читає версію перед активацією в етапі: статус, `digest`, `test_summary` | виконавець з `role: registry` у `JANE_ORCHESTRATOR_EXECUTORS` |
| Handler Runtime | Завантажує архів екстрактора за `package_id@version`, перевіряє `digest`; публікує профілі runtime для Registry | `JANE_HANDLER_RUNTIME_REGISTRY_URL` |
| LLM gateway, Storage | Завантажують архіви LLM-пакетів і пакетів збереження, яких немає серед вбудованих | `JANE_LLM_REGISTRY_URL`, `JANE_STORAGE_REGISTRY_URL` |
| Web Collector, Telegram Collector | Завантажують пакети `collector-rules` | `JANE_WEB_COLLECTOR_REGISTRY_URL`, `JANE_TELEGRAM_COLLECTOR_REGISTRY_URL` |

Кожен із цих модулів може працювати й без Registry, отримавши пакет або правила іншим способом ([Експорт і сумісність](../../reference/packages/export-and-compatibility.md#автономне-використання)). Базовий `infra/compose.yaml` адрес Registry сусідам не задає; приклад повного зв'язування — [infra/compose.local.example.yaml](../../../infra/compose.local.example.yaml).

## Заміна сумісною реалізацією

Інша реалізація може замінити Registry для всіх клієнтів Jane, якщо:

- реалізує операції [registry.v1.yaml](../../../contracts/openapi/registry.v1.yaml) з тими самими кодами помилок, ідемпотентністю й job;
- обчислює `digest` за тим самим алгоритмом канонічного ZIP ([Версії, архів і дайджест](../../reference/packages/versions-and-archive.md#канонічний-архів)) — інакше дайджести в етапах завдань і `packages.lock.json` прикладів не збігатимуться;
- перевіряє маніфест за [package-manifest.schema.json](../../../contracts/schemas/package-manifest.schema.json) і не приймає секрети;
- повідомляє можливості в `GET /v1/info` (`capabilities.handler_kinds`, `archive`, `upstream_ports`).

Для розробки клієнтів без справжнього Registry є мок за прикладами контракту:

```powershell
just contracts-mock registry --port 18410
```

```text
jane mock 'registry' on http://127.0.0.1:18410 (19 operations)
```

Мок відповідає прикладами з OpenAPI (наприклад, `GET /v1/packages` повертає пакет `shop-example.product-extractor`), стану не зберігає й перевірок не виконує.
