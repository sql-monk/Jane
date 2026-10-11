# GET /v1/invocations/{invocation_id}

> Згенеровано `scripts/docs_reference.py` з [handler.v1.yaml](../../../../contracts/openapi/handler.v1.yaml#L178). Не редагуйте вручну.

**Прочитати збережений результат виклику**

| Властивість | Значення |
|---|---|
| operationId | `getInvocation` |
| Метод і шлях | `GET /v1/invocations/{invocation_id}` |
| Scope | `handler:invoke` |
| Ідемпотентність | — |
| Теги | invocations |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `invocation_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Результат виклику. | `handler-result` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `invocation_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `handler` | `package-ref` | так | Фактично виконана версія (digest заповнено завжди). |
| `handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `handler_kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `status` | enum: `success`, `empty`, `unrecognized`, `failed` | так |  |
| `inputs` | array of `InputRef` | так | Посилання на вхідні дані в порядку запиту. |
| `inputs[].kind` | enum: `material`, `entities`, `data` | так |  |
| `inputs[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `inputs[].observation_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `inputs[].content_sha256` | `string` | ні | шаблон `"^[a-f0-9]{64}$"` |
| `inputs[].from_invocation_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `output` | `HandlerOutput` | ні | Вихід за типом обробника: extractor — entities; llm — data (+ usage); storage — writes; transform — data або entities. Великий вихід — через *_ref. |
| `output.entities` | array of `entity` | ні |  |
| `output.entities[].entity_type` | `string` | так | Тип сутності зі схеми результату пакета (наприклад 'product', 'price', 'event').; шаблон `"^[a-z][a-z0-9_]{0,63}$"` |
| `output.entities[].schema` | `string` | ні | Посилання на схему сутності всередині пакета: '&lt;package_id>@&lt;version>#&lt;entity_type>'. |
| `output.entities[].key` | `EntityKey` | так | Ідентичність об'єкта. natural — значення ключових полів схеми (наприклад {"sku": "A-1"}); scope — простір імен (зазвичай source_id), щоб однакові SKU різних джерел не злилися. Сховище будує канонічний рядок ключа: scope + '\|' + пари natural, відсортовані за іменем, серіалізовані як JSON без пробілів. |
| `output.entities[].fields` | `object` | так | Значення полів. Відсутнє поле — без змін; null заборонено (для очищення — 'cleared'). |
| `output.entities[].cleared` | array of `string` | ні | Поля, які треба явно очистити в поточному стані. |
| `output.entities[].completeness` | enum: `full`, `partial` | ні | full — обробник заявляє, що передав усі поля, які знайшов у матеріалі (інформативно; семантику злиття не змінює); partial — лише частину полів (наприклад, завдання перевірки ціни).; типово `"partial"` |
| `output.entities[].observation` | `ObservationOrder` | так | Порядок спостережень. Порівняння: спочатку observed_at (час отримання матеріалу колектором), потім sequence (ревізія джерела, якщо є), потім observation_id лексикографічно. Більше — новіше. Час обробки чи доставки в порівнянні не бере участі. |
| `output.entities[].provenance` | `Provenance` | ні |  |
| `output.entities[].confidence` | `number` | ні | мін. `0`; макс. `1` |
| `output.entities_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `output.data` | — | ні |  |
| `output.data_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `output.writes` | array of `WriteAck` | ні |  |
| `output.writes[].status` | enum: `written`, `duplicate`, `stale`, `partially_stale`, `simulated` | так | written — записано; duplicate — цей delivery_key уже записано, повтор без ефекту; stale — запізніле спостереження, лише в історії; partially_stale — частину полів застосовано, частину ні; simulated — test_mode, запису не було. |
| `output.writes[].target` | `object` | так |  |
| `output.writes[].object` | `StoredObjectRef` | ні | Посилання на збережений об'єкт (RAW або документ результатів), за яким його можна прочитати через storage API або повторно обробити. |
| `output.writes[].entity` | `object` | ні |  |
| `output.writes[].applied_fields` | array of `string` | ні |  |
| `output.writes[].stale_fields` | array of `string` | ні |  |
| `output.writes[].delivery_key` | `string` | ні |  |
| `unrecognized` | `object` | ні | Заповнюється, коли status = unrecognized. |
| `unrecognized.partial` | `boolean` | так | true — частину даних розібрано (вони в output), false — формат не розпізнано взагалі. |
| `unrecognized.reason` | `string` | ні |  |
| `unrecognized.signature` | `string` | ні | Короткий відбиток характеру проблеми для групування (наприклад 'missing-selector:.price'). |
| `failure` | `object` | ні | Заповнюється, коли status = failed. |
| `failure.kind` | enum: `execution_error`, `schema_mismatch`, `timeout`, `resource_exceeded`, `sandbox_violation`, `dependency_error`, `connection_error`, `budget_exhausted`, `invalid_params` | так |  |
| `failure.message` | `string` | так |  |
| `failure.retryable` | `boolean` | ні |  |
| `failure.details` | `object` | ні |  |
| `diagnostics` | `Diagnostics` | ні |  |
| `diagnostics.messages` | array of `DiagnosticMessage` | ні |  |
| `diagnostics.messages[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `diagnostics.messages[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `diagnostics.messages[].message` | `string` | так | макс. довжина `4000` |
| `diagnostics.messages[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `diagnostics.messages[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `diagnostics.messages[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `diagnostics.validation_errors` | array of `object` | ні | Невідповідності виходу схемі пакета (для failure.kind = schema_mismatch). |
| `diagnostics.validation_errors[].pointer` | `string` | так |  |
| `diagnostics.validation_errors[].message` | `string` | так |  |
| `diagnostics.validation_errors[].schema_pointer` | `string` | ні |  |
| `diagnostics.metrics` | `object` | ні |  |
| `diagnostics.metrics.duration_ms` | `integer` | ні | мін. `0` |
| `diagnostics.metrics.cpu_ms` | `integer` | ні | мін. `0` |
| `diagnostics.metrics.peak_memory_mb` | `number` | ні | мін. `0` |
| `diagnostics.metrics.output_bytes` | `integer` | ні | мін. `0` |
| `diagnostics.logs_ref` | `InlineContent` \| `BlobContent` | ні | stdout/stderr виконання (обрізані до limits.sandbox.max_output_bytes). |
| `usage` | `Usage` | ні |  |
| `usage.llm` | `object` | ні |  |
| `usage.llm.provider` | `string` | ні |  |
| `usage.llm.model` | `string` | ні |  |
| `usage.llm.input_tokens` | `integer` | ні | мін. `0` |
| `usage.llm.output_tokens` | `integer` | ні | мін. `0` |
| `usage.llm.cost` | `Money` | ні |  |
| `delivery_key` | `string` | ні |  |
| `duplicate` | `boolean` | ні | true — цей delivery_key уже виконано; повернуто збережений результат без повторного ефекту. |
| `test_mode` | `boolean` | ні |  |
| `started_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `success`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A1",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "success",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "entities": [
      {
        "entity_type": "product",
        "schema": "shop-example.product-extractor@1.2.0#product",
        "key": {
          "scope": "shop-example",
          "natural": {
            "sku": "A-100"
          }
        },
        "fields": {
          "sku": "A-100",
          "title": "Kettle A-100",
          "price": {
            "amount": 1299.0,
            "currency": "UAH"
          },
          "availability": "in_stock",
          "url": "https://shop.example.test/product/a-100"
        },
        "completeness": "full",
        "observation": {
          "observation_id": "obs_01J9ZQ4A0000000000000001",
          "observed_at": "2026-09-27T10:00:05Z",
          "material_id": "web:3704326c60776c53169680099e2eed31",
          "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "provenance": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0",
            "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
          },
          "invocation_id": "inv_01J9ZQ4B00000000000000A1",
          "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
          "stage_id": "extract-products"
        },
        "confidence": 0.98
      }
    ]
  },
  "diagnostics": {
    "messages": [
      {
        "level": "info",
        "code": "extract.selector_fallback",
        "message": "used og:title as title fallback",
        "material_id": "web:3704326c60776c53169680099e2eed31"
      }
    ],
    "metrics": {
      "duration_ms": 412,
      "cpu_ms": 180,
      "peak_memory_mb": 61.5,
      "output_bytes": 812
    }
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`.
