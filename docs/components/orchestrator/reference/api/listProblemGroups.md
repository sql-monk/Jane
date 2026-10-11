# GET /v1/problem-groups

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L996). Не редагуйте вручну.

**Проблемні матеріали, згруповані за джерелом і характером проблеми**

| Властивість | Значення |
|---|---|
| operationId | `listProblemGroups` |
| Метод і шлях | `GET /v1/problem-groups` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | problems |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `source_id` | query | `string` | ні |  |
| `status` | query | enum: `open`, `in_progress`, `resolved`, `ignored`, `unresolved` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка груп. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `ProblemGroup` | так |  |
| `items[].group_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].source_id` | `string` | так |  |
| `items[].package` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `items[].package.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].package.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].package.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `items[].problem` | enum: `unrecognized`, `failed` | так |  |
| `items[].failure_kind` | `string` | ні |  |
| `items[].signature` | `string` | так |  |
| `items[].count` | `integer` | так | мін. `0` |
| `items[].first_seen_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].last_seen_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].status` | enum: `open`, `in_progress`, `resolved`, `ignored`, `unresolved` | так |  |
| `items[].assistant_job_id` | `string` | ні |  |
| `items[].note` | `string` | ні | Останнє пояснення з `PATCH /v1/problem-groups/{group_id}` (людина чи асистент). |
| `items[].samples` | array of `object` | ні |  |
| `items[].samples[].material_id` | `string` | ні |  |
| `items[].samples[].observation_id` | `string` | ні |  |
| `items[].samples[].invocation_id` | `string` | ні |  |
| `items[].samples[].stored_object_id` | `string` | ні |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `groups`:

```json
{
  "items": [
    {
      "group_id": "pg_01J9ZW0000000000000000001",
      "source_id": "shop-example",
      "package": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0"
      },
      "problem": "unrecognized",
      "signature": "missing-selector:.price",
      "count": 37,
      "first_seen_at": "2026-09-26T10:00:00Z",
      "last_seen_at": "2026-09-27T10:00:06Z",
      "status": "open",
      "samples": [
        {
          "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
          "observation_id": "obs_01J9ZQ4A0000000000000001",
          "invocation_id": "inv_01J9ZQ4B00000000000000A3"
        }
      ]
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
