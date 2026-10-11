# GET /v1/packages

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L38). Не редагуйте вручну.

**Пошук пакетів**

| Властивість | Значення |
|---|---|
| operationId | `listPackages` |
| Метод і шлях | `GET /v1/packages` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | packages |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `kind` | query | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | ні |  |
| `q` | query | `string` | ні | Повнотекстовий пошук за id, назвою, описом, тегами. |
| `tag` | query | `string` | ні |  |
| `entity_type` | query | `string` | ні | Пакети, що видають сутності цього типу. |
| `media_type` | query | `string` | ні |  |
| `domain` | query | `string` | ні | Збіг із bindings_hint.domains. |
| `fork_of` | query | `string` | ні | Лише форки вказаного пакета. |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка пакетів. | `PackageList` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `Package` | так |  |
| `items[].package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `items[].title` | `string` | так |  |
| `items[].description` | `string` | ні |  |
| `items[].latest_version` | `string \| null` | ні |  |
| `items[].auto_changes_allowed` | `boolean` | так | false — автоматичні зміни (версії від LLM) заборонені для цього пакета (ТЗ §9). |
| `items[].deprecated` | `boolean` | так |  |
| `items[].fork_of` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `items[].fork_of.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].fork_of.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].fork_of.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `items[].forks_count` | `integer` | ні | мін. `0` |
| `items[].owner` | `string` | ні |  |
| `items[].labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `items[].created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].updated_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `search`:

```json
{
  "items": [
    {
      "package_id": "shop-example.product-extractor",
      "kind": "extractor",
      "title": "Shop Example product cards",
      "latest_version": "1.2.0",
      "auto_changes_allowed": true,
      "deprecated": false,
      "created_at": "2026-09-20T08:00:00Z",
      "updated_at": "2026-09-27T09:40:00Z"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
