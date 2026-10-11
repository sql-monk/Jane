# GET /v1/tasks

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L200). Не редагуйте вручну.

**Завдання (з фільтром за джерелом або пакетом, що використовується в етапах)**

| Властивість | Значення |
|---|---|
| operationId | `listTasks` |
| Метод і шлях | `GET /v1/tasks` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | tasks |

`package_id` — лише завдання, у яких хоча б один етап (або правила колектора) посилається на цей пакет; разом із `package_version` — на цю точну версію. Так адмінка й асистент знаходять усі прив'язки спільного пакета (ТЗ §9: перевірка на всіх прив'язках). У відповіді `package_stages` перелічує такі етапи.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `source_id` | query | `string` | ні |  |
| `package_id` | query | `string` | ні |  |
| `package_version` | query | `string` | ні | Лише разом із package_id. |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка завдань. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `TaskSummary` | так |  |
| `items[].task_id` | `string` | так |  |
| `items[].title` | `string` | так |  |
| `items[].source_id` | `string` | так |  |
| `items[].enabled` | `boolean` | так |  |
| `items[].schedule` | `Schedule` | ні |  |
| `items[].schedule.type` | enum: `manual`, `once`, `cron`, `interval` | так |  |
| `items[].schedule.at` | `string` (date-time) | ні | Для once. |
| `items[].schedule.cron` | `string` | ні | П'ять полів cron (хв год день міс день_тижня) для type=cron.; шаблон `"^\\S+( \\S+){4}$"` |
| `items[].schedule.interval_seconds` | `integer` | ні | Для type=interval.; мін. `1` |
| `items[].schedule.timezone` | `string` | ні | IANA, наприклад Europe/Kyiv.; типово `"UTC"` |
| `items[].schedule.start_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].schedule.end_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].schedule.enabled` | `boolean` | ні | типово `true` |
| `items[].schedule.overlap` | enum: `skip`, `queue`, `allow` | ні | Що робити, якщо попередній запуск ще триває (allow обмежується limits.concurrency.max_parallel_runs_per_task).; типово `"skip"` |
| `items[].next_run_at` | `string` (date-time) | ні |  |
| `items[].package_stages` | array of `object` | ні | Етапи, що посилаються на пакет із фільтра package_id (лише коли фільтр задано). |
| `items[].package_stages[].stage_id` | `string` | так |  |
| `items[].package_stages[].package` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `items[].last_run` | `object` | ні |  |
| `items[].last_run.run_id` | `string` | ні |  |
| `items[].last_run.status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | ні |  |
| `items[].last_run.finished_at` | `string` (date-time) | ні |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `byPackage`:

```json
{
  "items": [
    {
      "task_id": "shop-catalog",
      "title": "Повний збір каталогу Shop Example",
      "source_id": "shop-example",
      "enabled": true,
      "package_stages": [
        {
          "stage_id": "extract-products",
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          }
        }
      ]
    }
  ],
  "next_cursor": null
}
```

Приклад `list`:

```json
{
  "items": [
    {
      "task_id": "shop-catalog",
      "title": "Повний збір каталогу Shop Example",
      "source_id": "shop-example",
      "enabled": true,
      "schedule": {
        "type": "cron",
        "cron": "0 2 * * 0",
        "timezone": "Europe/Kyiv"
      },
      "next_run_at": "2026-10-04T02:00:00+03:00",
      "last_run": {
        "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
        "status": "succeeded",
        "finished_at": "2026-09-27T11:40:00Z"
      }
    },
    {
      "task_id": "shop-price-check",
      "title": "Щоденна перевірка цін",
      "source_id": "shop-example",
      "enabled": true,
      "schedule": {
        "type": "interval",
        "interval_seconds": 86400
      }
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
