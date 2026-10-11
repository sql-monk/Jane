# GET /v1/storage-status

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L344). Не редагуйте вручну.

**Остання явна перевірка сховища та статистика об’єктів**

| Властивість | Значення |
|---|---|
| operationId | `getStorageStatus` |
| Метод і шлях | `GET /v1/storage-status` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | objects |

GET не відкриває адаптер і не обходить сховище. POST /v1/storage-status/checks запускає Job для health та статистики, оновлює process-local snapshot. Connection test перевіряє лише health. Зміна визначення та рестарт скидають snapshot. Статистика охоплює лише об’єкти namespace підключення: payload bytes, не зайнятий диск або сутності. Непідтримувані агрегати мають null і причину. Час фіксує свіжість, запис нових об’єктів не оновлює snapshot.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | query | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Останній стан або unknown до перевірки. | `StorageStatus` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `connection_id` | `string` | так |  |
| `kind` | `string` | так |  |
| `availability` | enum: `unknown`, `available`, `unavailable` | так |  |
| `checked_at` | `string \| null` (date-time) | так |  |
| `message` | `string \| null` | так |  |
| `entity_statistics` | `EntityStatistics` | ні |  |
| `entity_statistics.entity_count` | `integer \| null` | так | мін. `0` |
| `entity_statistics.total_size_bytes` | `integer \| null` | так | мін. `0` |
| `entity_statistics.types` | `array \| null` | так |  |
| `entity_statistics.size_basis` | `string \| null` | так | postgresql_relation_with_indexes — фізичний розмір таблиці актуальних станів з індексами; snapshot_documents — байти JSON-файлів станів. Не включає історію, RAW чи delivery. |
| `entity_statistics.checked_at` | `string \| null` (date-time) | так |  |
| `entity_statistics.unavailable_reason` | `string \| null` | так |  |
| `statistics` | `object` | так |  |
| `statistics.object_count` | `integer \| null` | так | мін. `0` |
| `statistics.total_size_bytes` | `integer \| null` | так | мін. `0` |
| `statistics.checked_at` | `string \| null` (date-time) | так |  |
| `statistics.scope` | enum: `connection_objects` | так |  |
| `statistics.unavailable_reason` | `string \| null` | так |  |

Приклад `unknown`:

```json
{
  "connection_id": "raw-files",
  "kind": "filesystem",
  "availability": "unknown",
  "checked_at": null,
  "message": null,
  "statistics": {
    "object_count": null,
    "total_size_bytes": null,
    "checked_at": null,
    "scope": "connection_objects",
    "unavailable_reason": "not_checked"
  }
}
```

Приклад `available`:

```json
{
  "connection_id": "raw-files",
  "kind": "filesystem",
  "availability": "available",
  "checked_at": "2026-10-11T08:00:00Z",
  "message": null,
  "statistics": {
    "object_count": 1,
    "total_size_bytes": 151,
    "checked_at": "2026-10-11T08:00:00Z",
    "scope": "connection_objects",
    "unavailable_reason": null
  }
}
```

Приклад `unavailable`:

```json
{
  "connection_id": "results-pg",
  "kind": "postgresql",
  "availability": "unavailable",
  "checked_at": "2026-10-11T08:00:00Z",
  "message": "connection check failed",
  "statistics": {
    "object_count": null,
    "total_size_bytes": null,
    "checked_at": null,
    "scope": "connection_objects",
    "unavailable_reason": "check_failed"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
