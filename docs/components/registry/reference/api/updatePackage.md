# PATCH /v1/packages/{package_id}

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L175). Не редагуйте вручну.

**Змінити налаштування пакета (назва, опис, заборона автозмін, застарілість)**

| Властивість | Значення |
|---|---|
| operationId | `updatePackage` |
| Метод і шлях | `PATCH /v1/packages/{package_id}` |
| Scope | `registry:write` |
| Ідемпотентність | — |
| Теги | packages |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `If-Match` | header | `string` | ні | ETag ресурсу для оптимістичного блокування. Розбіжність — 412 `precondition_failed`. |

## Тіло запиту

Тип вмісту `application/merge-patch+json`, схема `PackagePatch`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `title` | `string` | ні |  |
| `description` | `string` | ні |  |
| `auto_changes_allowed` | `boolean` | ні |  |
| `deprecated` | `boolean` | ні |  |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `forbidAuto`:

```json
{
  "auto_changes_allowed": false
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Оновлений пакет. | `Package` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `title` | `string` | так |  |
| `description` | `string` | ні |  |
| `latest_version` | `string \| null` | ні |  |
| `auto_changes_allowed` | `boolean` | так | false — автоматичні зміни (версії від LLM) заборонені для цього пакета (ТЗ §9). |
| `deprecated` | `boolean` | так |  |
| `fork_of` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `fork_of.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `fork_of.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `fork_of.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `forks_count` | `integer` | ні | мін. `0` |
| `owner` | `string` | ні |  |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `package`:

```json
{
  "package_id": "shop-example.product-extractor",
  "kind": "extractor",
  "title": "Shop Example product cards",
  "latest_version": "1.2.0",
  "auto_changes_allowed": true,
  "deprecated": false,
  "forks_count": 1,
  "created_at": "2026-09-20T08:00:00Z",
  "updated_at": "2026-09-27T09:40:00Z"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `412`, `422`.
