# PATCH /v1/problem-groups/{group_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1058). Не редагуйте вручну.

**Змінити статус групи (ignored, resolved) або прив'язати job вдосконалення**

| Властивість | Значення |
|---|---|
| operationId | `updateProblemGroup` |
| Метод і шлях | `PATCH /v1/problem-groups/{group_id}` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | problems |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `group_id` | path | `string` | так |  |

## Тіло запиту

Тип вмісту `application/merge-patch+json`, схема `object`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `status` | enum: `open`, `in_progress`, `resolved`, `ignored`, `unresolved` | ні |  |
| `assistant_job_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `note` | `string` | ні | Пояснення людини чи асистента; зберігається й повертається в `ProblemGroup.note`. |

Приклад `inProgress`:

```json
{
  "status": "in_progress",
  "assistant_job_id": "job_01J9ZX0000000000000000IMP",
  "note": "version shop-example.product-extractor@1.2.1 awaits manual approval"
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Оновлена група (з `note`, якщо її задано цим або попереднім PATCH). | `ProblemGroup` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `group_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `source_id` | `string` | так |  |
| `package` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `package.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `package.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `package.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `problem` | enum: `unrecognized`, `failed` | так |  |
| `failure_kind` | `string` | ні |  |
| `signature` | `string` | так |  |
| `count` | `integer` | так | мін. `0` |
| `first_seen_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `last_seen_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `status` | enum: `open`, `in_progress`, `resolved`, `ignored`, `unresolved` | так |  |
| `assistant_job_id` | `string` | ні |  |
| `note` | `string` | ні | Останнє пояснення з `PATCH /v1/problem-groups/{group_id}` (людина чи асистент). |
| `samples` | array of `object` | ні |  |
| `samples[].material_id` | `string` | ні |  |
| `samples[].observation_id` | `string` | ні |  |
| `samples[].invocation_id` | `string` | ні |  |
| `samples[].stored_object_id` | `string` | ні |  |

Приклад `group`:

```json
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
  "status": "in_progress",
  "assistant_job_id": "job_01J9ZX0000000000000000IMP",
  "note": "version shop-example.product-extractor@1.2.1 awaits manual approval",
  "first_seen_at": "2026-09-26T10:00:00Z",
  "last_seen_at": "2026-09-27T10:00:06Z",
  "samples": []
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
