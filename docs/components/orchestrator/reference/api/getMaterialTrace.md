# GET /v1/materials/{material_id}/trace

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L867). Не редагуйте вручну.

**Простежуваність матеріалу — спостереження → етапи → результати → версії пакетів**

| Властивість | Значення |
|---|---|
| operationId | `getMaterialTrace` |
| Метод і шлях | `GET /v1/materials/{material_id}/trace` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | traces |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `material_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Слід матеріалу. | `MaterialTrace` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `material_id` | `string` | так |  |
| `source_id` | `string` | ні |  |
| `url` | `string` | ні |  |
| `observations` | array of `object` | так |  |
| `observations[].observation_id` | `string` | так |  |
| `observations[].run_id` | `string` | ні |  |
| `observations[].task_id` | `string` | ні |  |
| `observations[].fetched_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `observations[].content_sha256` | `string` | ні |  |
| `observations[].stages` | array of `object` | так |  |
| `observations[].stages[].stage_id` | `string` | так |  |
| `observations[].stages[].handler` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `observations[].stages[].invocation_id` | `string` | ні |  |
| `observations[].stages[].result_status` | enum: `success`, `empty`, `unrecognized`, `failed` | ні |  |
| `observations[].stages[].item_id` | `string` | ні | Діагностика (R25) — елемент запуску (StageItem.item_id). |
| `observations[].stages[].status` | enum: `queued`, `leased`, `running`, `completed`, `retrying`, `failed`, `skipped`, `cancelled` | ні |  |
| `observations[].stages[].attempts` | `integer` | ні | мін. `0` |
| `observations[].stages[].available_at` | `string` (date-time) | ні | Діагностика (R25), як StageItem.available_at. |
| `observations[].stages[].attempt_history` | array of `AttemptEvent` | ні | Діагностика (R25): події взяття елемента в роботу й повторів у порядку часу — щоб довести, що повтор почався не раніше backoff. Обмежена конфігурацією оркестратора (`engine.attempt_history_max`, зберігаються перші події); не впливає на виконання. |
| `observations[].stages[].outputs` | array of `object` | ні |  |

Приклад `trace`:

```json
{
  "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
  "source_id": "shop-example",
  "url": "https://shop.example.test/product/a-100",
  "observations": [
    {
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
      "task_id": "shop-catalog",
      "fetched_at": "2026-09-27T10:00:05Z",
      "content_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
      "stages": [
        {
          "stage_id": "store-raw",
          "handler": {
            "package_id": "jane.storage-files",
            "version": "1.0.0"
          },
          "invocation_id": "inv_01J9ZQ4C00000000000000C2",
          "result_status": "success",
          "outputs": [
            {
              "kind": "stored_object",
              "object_id": "obj_01J9ZQ4C00000000000000D1",
              "connection_id": "raw-files"
            }
          ]
        },
        {
          "stage_id": "extract-products",
          "handler": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          },
          "invocation_id": "inv_01J9ZQ4B00000000000000A1",
          "result_status": "success",
          "item_id": "itm_01J9ZQ4B0000000000000001",
          "status": "completed",
          "attempts": 2,
          "attempt_history": [
            {
              "event": "claimed",
              "at": "2026-09-27T10:00:06.010Z",
              "attempt": 1
            },
            {
              "event": "retry_scheduled",
              "at": "2026-09-27T10:00:06.500Z",
              "attempt": 1,
              "available_at": "2026-09-27T10:00:09.500Z",
              "delay_ms": 3000,
              "code": "upstream_unavailable"
            },
            {
              "event": "claimed",
              "at": "2026-09-27T10:00:09.530Z",
              "attempt": 2
            },
            {
              "event": "completed",
              "at": "2026-09-27T10:00:09.910Z",
              "attempt": 2
            }
          ],
          "outputs": [
            {
              "kind": "entity",
              "entity_type": "product",
              "canonical_key": "shop-example|{\"sku\":\"A-100\"}"
            }
          ]
        },
        {
          "stage_id": "store-products",
          "handler": {
            "package_id": "jane.storage-postgresql",
            "version": "1.0.0"
          },
          "invocation_id": "inv_01J9ZQ4C00000000000000C1",
          "result_status": "success",
          "outputs": [
            {
              "kind": "entity",
              "entity_type": "product",
              "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
              "connection_id": "results-pg"
            }
          ]
        }
      ]
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
