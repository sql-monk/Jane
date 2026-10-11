# Handler Runtime: інтеграція

Handler Runtime реалізує спільний API обробників `handler.v1`. Сторінка показує виклики зі стороннього застосунку, місце сервісу в Jane і вимоги до сумісної заміни. Повний опис операцій, схем і помилок — [довідник handler.v1](../../reference/api/handler/README.md).

## Зміст

- [Самостійне використання](#самостійне-використання)
- [Синхронний виклик](#синхронний-виклик)
- [Асинхронний виклик і job](#асинхронний-виклик-і-job)
- [Тест-прогони](#тест-прогони)
- [Повторна доставка](#повторна-доставка)
- [Вхідні дані](#вхідні-дані)
- [Помилки](#помилки)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Самостійне використання

Застосунку потрібні лише Handler Runtime і пакет екстрактора. Пакет можна передати:

- **архівом у запиті** — `package_archive`: канонічний zip inline у base64, `file://` у каталогах `BLOB_ROOTS` або `download_url` з дозволеного хоста; Registry не потрібен;
- **за ідентифікатором** — лише `handler.package_id` і `handler.version`; сервіс завантажує архів із Registry (`JANE_HANDLER_RUNTIME_REGISTRY_URL`).

`handler.digest` необов'язковий; якщо його задано, архів із будь-якого джерела має мати саме цей дайджест, інакше 422 `digest_mismatch`. Канонічний архів і дайджест будує `jane_extractor_sdk.package.build_archive` і `digest_of` — так само, як Registry.

Приклади нижче виконано 2026-10-11 на ревізії `c59d26d`, сервіс слухав `127.0.0.1:18300` з `auth_mode=none`. З автентифікацією додайте заголовок `Authorization: Bearer <ключ>` з областю `handler:invoke` або `handler:test` ([configuration.md](configuration.md#процес-і-автентифікація)).

## Синхронний виклик

Мінімальний запит (вміст `package_archive.data` і матеріалу скорочено). Скрипт, що формує такий запит із каталогу пакета й файлу, — у [quickstart.md](quickstart.md#http-сервіс):

```json
{
  "handler": {"package_id": "example.hello-title", "version": "0.1.0"},
  "package_archive": {"kind": "inline", "media_type": "application/zip", "encoding": "base64", "data": "UEsDBBQAAAAAAAAAIQ..."},
  "inputs": [
    {
      "kind": "material",
      "material": {
        "material_id": "web:37f58c3315be7800d9d1452bf60ed101",
        "observation_id": "obs_local_dd9a7e22010e41c06df7332a",
        "source": {"kind": "web"},
        "locator": {"url": "https://example.test/a"},
        "fetched_at": "2026-10-11T10:03:56Z",
        "format": {"media_type": "text/html"},
        "content": {"kind": "inline", "media_type": "text/html", "encoding": "utf-8", "data": "<html><head><title>Hello, Jane</title></head><body></body></html>\n"}
      }
    }
  ],
  "delivery": {"delivery_key": "demo-0001"}
}
```

```bash
curl -s -X POST http://127.0.0.1:18300/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: demo-0001' --data-binary @request.json
```

Відповідь 200 — `HandlerResult` (уривок; `observation` і `provenance` сутності пропущено):

```json
{
  "invocation_id": "inv_af29308accf6403abf11997e4c3910aa",
  "handler": {"package_id": "example.hello-title", "version": "0.1.0", "digest": "sha256:37716453a0e53f686ac9ea34ba7313872e377e155a7b1db9af9fd3aed8f7bf78"},
  "handler_kind": "extractor",
  "status": "success",
  "inputs": [{"kind": "material", "material_id": "web:37f58c3315be7800d9d1452bf60ed101", "observation_id": "obs_local_dd9a7e22010e41c06df7332a", "content_sha256": "dd9a7e22010e41c06df7332a5068de4ecd5f5c272cb7ea09cd2340667b926038"}],
  "output": {
    "entities": [
      {
        "entity_type": "page",
        "fields": {"url": "https://example.test/a", "title": "Hello, Jane"},
        "key": {"scope": "local", "natural": {"url": "https://example.test/a"}},
        "schema": "example.hello-title@0.1.0#page"
      }
    ]
  },
  "test_mode": false,
  "duplicate": false,
  "delivery_key": "demo-0001",
  "diagnostics": {"metrics": {"duration_ms": 2469, "output_bytes": 248, "cpu_ms": 440, "peak_memory_mb": 23.5}}
}
```

Кожна сутність отримує від сервісу `key` (з `key_fields` маніфесту, якщо пакет його не задав), `observation` (з `observation_id`, `fetched_at` і ревізії матеріалу), `schema` і `provenance` з пакетом, дайджестом та `invocation_id`; якщо в `context.trace` є `run_id` і `stage_id`, вони теж потрапляють у `provenance`. Чотири стани результату й причини `failed` — [internals.md](internals.md#класифікація-результату).

Якщо пісочниця не встигла за `limits.timeouts.sync_response_max_ms` (типово 25 с), відповідь — 202 з job, як в асинхронному режимі. Збережений результат доступний за `GET /v1/invocations/{invocation_id}`:

```bash
curl -s http://127.0.0.1:18300/v1/invocations/inv_af29308accf6403abf11997e4c3910aa
```

## Асинхронний виклик і job

З `"mode": "async"` сервіс одразу відповідає 202 і заголовком `Location`:

```bash
curl -s -i -X POST http://127.0.0.1:18300/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: demo-0002' --data-binary @request-async.json
```

```text
HTTP/1.1 202 Accepted
location: /v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47
content-type: application/json

{"job_id":"job_2932f7c5bf2a46fb9dc3813440324b47","kind":"invocation","status":"queued","created_at":"2026-10-11T10:04:36.453794Z","idempotency_key":"demo-0002","links":{"self":"/v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47","cancel":"/v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47/cancel"},"labels":{"invocation_id":"inv_7e38cd8d74b24c088b62647c08935250"}}
```

Опитуйте `GET /v1/jobs/{job_id}` до кінцевого стану: `succeeded`, `failed` або `cancelled`. Уривок відповіді (без поля `result`, у якому лежить `HandlerResult`):

```bash
curl -s http://127.0.0.1:18300/v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47
```

```json
{"job_id": "job_2932f7c5bf2a46fb9dc3813440324b47", "kind": "invocation", "status": "succeeded", "created_at": "2026-10-11T10:04:36.453794Z", "updated_at": "2026-10-11T10:04:42.820888Z", "started_at": "2026-10-11T10:04:36.453794Z", "finished_at": "2026-10-11T10:04:42.820888Z", "idempotency_key": "demo-0002", "links": {"self": "/v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47", "cancel": "/v1/jobs/job_2932f7c5bf2a46fb9dc3813440324b47/cancel"}, "labels": {"invocation_id": "inv_7e38cd8d74b24c088b62647c08935250"}}
```

Job `succeeded` означає, що виклик відбувся: `result.status` може бути й `failed`. Job `failed` — виклик не завершився: рушій недоступний, перевищено `jobs.job_timeout_ms` або екземпляр-власник зник. `POST /v1/jobs/{job_id}/cancel` переводить job у `cancelling`, зупиняє контейнер виклику (за міткою `io.jane.invocation-id`) і завершує job як `cancelled`. Стани — [internals.md](internals.md#стани-job).

## Тест-прогони

`POST /v1/test-runs` проганяє тести маніфесту (`"tests": "all"`, `"none"` або список назв) і додаткові випадки `extra_cases` завжди в тестовому режимі. Відповідь — завжди 202 з job; `result` — `TestReport`.

```json
{
  "handler": {"package_id": "example.hello-title", "version": "0.1.0"},
  "package_archive": {"kind": "inline", "media_type": "application/zip", "encoding": "base64", "data": "UEsDBBQAAAAAAAAAIQ..."},
  "tests": "all"
}
```

```bash
curl -s -i -X POST http://127.0.0.1:18300/v1/test-runs -H 'Content-Type: application/json' -H 'Idempotency-Key: test-run-0001' --data-binary @test-run.json
```

```text
HTTP/1.1 202 Accepted
location: /v1/jobs/job_469d513a55d04d4c8f2e02d651dad6c8
content-type: application/json

{"job_id":"job_469d513a55d04d4c8f2e02d651dad6c8","kind":"test_run","status":"queued","created_at":"2026-10-11T10:04:36.217756Z","idempotency_key":"test-run-0001","links":{"self":"/v1/jobs/job_469d513a55d04d4c8f2e02d651dad6c8","cancel":"/v1/jobs/job_469d513a55d04d4c8f2e02d651dad6c8/cancel"}}
```

Підсумок `result` завершеного job (скорочено до назв і статусів випадків):

```json
{"passed": 2, "failed": 0, "cases": [{"name": "with-title", "expected_status": "success", "actual_status": "success", "passed": true}, {"name": "no-title", "expected_status": "empty", "actual_status": "empty", "passed": true}]}
```

Кожен випадок — окремий запуск пісочниці. Вихід порівнюється з очікуваним у режимі `exact` або `subset` без полів `observation`, `provenance`, `schema`; розбіжності — у `differences` з JSON Pointer. Тест-прогін не пише в робочі дані: сервіс узагалі нічого не пише, крім власного стану job.

## Повторна доставка

`Idempotency-Key` обов'язковий для `POST /v1/invocations` і має дорівнювати `delivery.delivery_key`; для `POST /v1/test-runs` він теж обов'язковий.

| Ситуація | Відповідь |
|---|---|
| той самий ключ і те саме тіло, виклик завершено | збережена відповідь, `Idempotency-Replayed: true`, у `HandlerResult` — `duplicate: true`; пісочниця не запускається |
| той самий ключ, async-job уже завершився | 200 з результатом job замість 202 |
| той самий ключ, виклик ще виконується | 409 `idempotency_in_progress` (retryable) |
| той самий ключ, інше тіло | 422 `idempotency_key_reused` |
| ключ не дорівнює `delivery_key` або відсутній | 422 `validation_failed` |

Ключ пам'ятається `idempotency.idempotency_ttl_seconds` (типово добу). У режимі пам'яті — лише в межах одного процесу.

## Вхідні дані

| `inputs[].kind` | Що отримує код пакета | Як передати вміст |
|---|---|---|
| `material` | документ `Material` | `content` inline (`utf-8` або `base64`) чи blob (`file://`, `download_url`) |
| `entities` | сам об'єкт входу | `entities` або посилання `entities_ref` |
| `data` | сам об'єкт входу | `data` або посилання `data_ref` |

Пакет приймає лише види з `input.accepts` маніфесту (типово `material`) і типи вмісту з `input.media_types` (шаблони на кшталт `text/*`). Blob-вміст сервіс завантажує й перевіряє сам, до запуску пісочниці; код пакета отримує байти через `ctx.bytes()`. Параметри `params` перевіряються за `params_schema` пакета після підстановки типових значень верхнього рівня.

## Помилки

До запуску пісочниці сервіс повертає HTTP-помилку у форматі problem+json ([модель помилок](../../../contracts/docs/errors.md)):

| Код | HTTP | Причина |
|---|---|---|
| `validation_failed` | 422 | запит не відповідає схемі, недійсний маніфест, `params`, вид чи тип входу, `access.network` не `none`, недоступний `file://`, немає ні архіву, ні Registry |
| `dependency_not_allowed` | 422 | профіль недоступний або `dependencies.python` не задовольняє профіль |
| `digest_mismatch` | 422 | дайджест архіву не збігається з `handler.digest` або `ETag` Registry |
| `limit_exceeded` | 422 | вміст входу більший за `packages.max_input_bytes` або `package_archive` — за `packages.max_archive_bytes` (архів із Registry понад ліміт — `validation_failed`) |
| `not_found` | 404 | версії немає в Registry, файлу `file://` немає, тест із `tests` відсутній у маніфесті |
| `upstream_unavailable` | 502 | Registry чи завантаження вмісту не відповідає |
| `service_unavailable` | 503 | контейнерний рушій або образ недоступні, черга job повна |

Приклад відповіді без заголовка `Idempotency-Key`:

```json
{"type":"urn:jane:problem:validation_failed","title":"Validation failed","status":422,"detail":"Idempotency-Key header is required","instance":"/v1/invocations","code":"validation_failed","retryable":false,"errors":[{"parameter":"Idempotency-Key","message":"required"}],"trace_id":"ed0d396c8228bd2e06767293a93ff2a8"}
```

Після запуску пісочниці будь-яка проблема коду пакета — це 200 з `status: failed` і `failure.kind`.

## Композиція в Jane

У платформі Handler Runtime — виконавець етапів типу екстрактор і перетворення. Сервіс нікого не викликає, крім Registry (за пакетами) і контейнерного рушія; сутності далі зберігає окремий етап Storage, який запускає Orchestrator.

| Хто викликає | Що | Налаштування з боку викликача |
|---|---|---|
| Orchestrator | `POST /v1/invocations` для етапів, `GET /v1/jobs/{job_id}`, синхронізація підключень (отримує 501 і пропускає сервіс) | виконавець `{"executor": "handler-runtime", "role": "handler", "base_url": "http://handler-runtime:8000", "capabilities": {"handler_kinds": ["extractor", "transform"], "default": true}}` — приклад в `infra/compose.local.example.yaml` |
| Assistant | `POST /v1/test-runs` для чернеток пакетів (inline-архів) | `JANE_ASSISTANT_HANDLER_RUNTIME_URL` |
| Registry | читає `GET /v1/info`, щоб перевіряти `dependencies.python` за профілем | `JANE_REGISTRY_RUNTIME_PROFILES` |
| Admin UI | через proxy dev-стеку `/api/handler-runtime/...` | — |

Сам Handler Runtime бере пакети з Registry з токеном `JANE_HANDLER_RUNTIME_REGISTRY_TOKEN` (у dev-стеку — ключ з областю `registry:read`) і читає RAW сервісу Storage через спільний том лише для читання (`BLOB_ROOTS`). Опис етапів і доставки — [Orchestrator](../orchestrator/README.md); композиція платформи — [архітектура](../../architecture/README.md).

## Заміна сумісною реалізацією

Інший виконавець Python-пакетів (наприклад, на іншій технології пісочниці) може замінити Handler Runtime, якщо:

- реалізує `handler.v1`: `POST /v1/invocations` (sync і async), `GET /v1/invocations/{invocation_id}`, `POST /v1/test-runs`, `/v1/jobs/*`, `/v1/health`, `/v1/info`; `/v1/connections*` можуть відповідати 501 `not_implemented`;
- дотримується ідемпотентності за `delivery_key` і повертає `duplicate: true` на повторну доставку;
- класифікує результат чотирма статусами й `failure.kind` з `handler-result.schema.json`;
- виконує пакети за маніфестом і протоколом раннера SDK ([протокол раннера](../extractor-sdk/internals.md#протокол-раннера)) і публікує профілі в `capabilities.runtime_profiles`.

Перевірка відповідності контракту — контрактні тести `services/handler-runtime/tests/test_contract.py` як зразок і [contracts](../contracts/README.md). Викликачі змінюють лише `base_url` виконавця.
