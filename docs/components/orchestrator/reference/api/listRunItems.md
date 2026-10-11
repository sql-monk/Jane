# GET /v1/runs/{run_id}/items

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L769). Не редагуйте вручну.

**Елементи запуску — матеріал на етапі, спроби, результат, помилка**

| Властивість | Значення |
|---|---|
| operationId | `listRunItems` |
| Метод і шлях | `GET /v1/runs/{run_id}/items` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | runs, traces |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `run_id` | path | `string` | так |  |
| `stage_id` | query | `string` | ні |  |
| `status` | query | enum: `queued`, `leased`, `running`, `completed`, `retrying`, `failed`, `skipped`, `cancelled` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка елементів. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `StageItem` | так |  |
| `items[].item_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].stage_id` | `string` | так |  |
| `items[].material_id` | `string` | ні |  |
| `items[].observation_id` | `string` | ні |  |
| `items[].status` | enum: `queued`, `leased`, `running`, `completed`, `retrying`, `failed`, `skipped`, `cancelled` | так |  |
| `items[].result_status` | enum: `success`, `empty`, `unrecognized`, `failed` | ні |  |
| `items[].attempts` | `integer` | так | мін. `0` |
| `items[].handler` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `items[].handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `items[].invocation_id` | `string` | ні |  |
| `items[].delivery_key` | `string` | ні |  |
| `items[].error` | `problem` | ні | Єдина модель помилки всіх API Jane: RFC 9457 (application/problem+json) з розширеннями 'code', 'retryable', 'errors', 'trace_id'. Клієнт приймає рішення за 'code' (стабільний машинний код), а не за 'title'/'detail'. Невідомий 'code' обробляється за HTTP-статусом і 'retryable'. |
| `items[].error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `items[].error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `items[].error.status` | `integer` | так | мін. `400`; макс. `599` |
| `items[].error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `items[].error.instance` | `string` (uri-reference) | ні |  |
| `items[].error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `items[].error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `items[].error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `items[].error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `items[].error.trace_id` | `string` | ні |  |
| `items[].error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `items[].started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].available_at` | `string` (date-time) | ні | Діагностика (R25). Найраніший момент, коли елемент у стані queued/retrying можна взяти в роботу (кінець backoff). |
| `items[].attempt_history` | array of `AttemptEvent` | ні | Діагностика (R25): події взяття елемента в роботу й повторів у порядку часу — щоб довести, що повтор почався не раніше backoff. Обмежена конфігурацією оркестратора (`engine.attempt_history_max`, зберігаються перші події); не впливає на виконання. |
| `items[].attempt_history[].event` | `string` | так | Розширюваний перелік (толерантний читач): `claimed` — воркер узяв елемент (нова спроба); `lease_reclaimed` — оренду загиблого воркера перехоплено (не нова спроба); `retry_scheduled` — повтор після помилки, елемент чекає до `available_at`; `in_progress_parked` — виконавець ще обробляє той самий `delivery_key`, перевірка — після `available_at`; `completed`, `failed` — фінал. |
| `items[].attempt_history[].at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].attempt_history[].attempt` | `integer` | ні | Номер спроби (StageItem.attempts) на момент події.; мін. `0` |
| `items[].attempt_history[].available_at` | `string` (date-time) | ні | Для `retry_scheduled` / `in_progress_parked` — коли елемент знову можна взяти. |
| `items[].attempt_history[].delay_ms` | `integer` | ні | Затримка до `available_at` за політикою повторів (або engine-налаштуванням для in_progress).; мін. `0` |
| `items[].attempt_history[].code` | `string` | ні | Код помилки (Problem.code), що спричинив повтор чи фінальну помилку. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `items`:

```json
{
  "items": [
    {
      "item_id": "itm_01J9ZQ4B0000000000000001",
      "stage_id": "extract-products",
      "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "status": "completed",
      "result_status": "unrecognized",
      "attempts": 1,
      "handler": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0"
      },
      "invocation_id": "inv_01J9ZQ4B00000000000000A3",
      "delivery_key": "1d7c2a9e5b0f4c3e8a6d2b1f0e9c8d7a",
      "started_at": "2026-09-27T10:00:06Z",
      "finished_at": "2026-09-27T10:00:06Z",
      "attempt_history": [
        {
          "event": "claimed",
          "at": "2026-09-27T10:00:06.010Z",
          "attempt": 1
        },
        {
          "event": "completed",
          "at": "2026-09-27T10:00:06.420Z",
          "attempt": 1
        }
      ]
    },
    {
      "item_id": "itm_01J9ZQ4B0000000000000002",
      "stage_id": "extract-products",
      "material_id": "web:0a1b2c3d4e5f60718293a4b5c6d7e8f9",
      "observation_id": "obs_01J9ZQ4A0000000000000002",
      "status": "retrying",
      "attempts": 1,
      "handler": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0"
      },
      "delivery_key": "2e8d3b0f6c1a5d4f9b7e3c2a1f0d9e8b",
      "error": {
        "type": "urn:jane:problem:upstream_unavailable",
        "title": "Executor call failed",
        "status": 502,
        "code": "upstream_unavailable",
        "retryable": true
      },
      "started_at": "2026-09-27T10:00:06Z",
      "available_at": "2026-09-27T10:00:09.512Z",
      "attempt_history": [
        {
          "event": "claimed",
          "at": "2026-09-27T10:00:06.011Z",
          "attempt": 1
        },
        {
          "event": "retry_scheduled",
          "at": "2026-09-27T10:00:06.512Z",
          "attempt": 1,
          "available_at": "2026-09-27T10:00:09.512Z",
          "delay_ms": 3000,
          "code": "upstream_unavailable"
        }
      ]
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
