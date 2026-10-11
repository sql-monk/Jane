# GET /v1/packages/{package_id}/versions

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L216). Не редагуйте вручну.

**Версії пакета**

| Властивість | Значення |
|---|---|
| operationId | `listPackageVersions` |
| Метод і шлях | `GET /v1/packages/{package_id}/versions` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | versions |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `status` | query | enum: `draft`, `approved`, `rejected`, `deprecated`, `yanked` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка версій (від новіших). | `PackageVersionList` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `PackageVersion` | так |  |
| `items[].package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].digest` | `string` | так | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `items[].status` | enum: `draft`, `approved`, `rejected`, `deprecated`, `yanked` | так | draft — опубліковано, не погоджено; approved — дозволено активувати в етапах; rejected — відхилено; deprecated — не рекомендується для нових прив'язок; yanked — заборонено для нових прив'язок (наявні прив'язки не ламаються, архів доступний). |
| `items[].test_status` | enum: `unknown`, `passed`, `failed` | так |  |
| `items[].manifest` | `package-manifest` | ні | Маніфест пакета обробника або правил колектора (ТЗ §7) — файл 'jane-package.json' у корені архіву пакета. Пакет незмінний після публікації; дайджест архіву обчислює репозиторій. Що є пакетом для кожного типу — contracts/docs/handler-packages.md. Секрети в пакеті заборонені (репозиторій відхиляє з secret_detected). |
| `items[].manifest.schema_version` | `"1"` | так |  |
| `items[].manifest.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].manifest.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].manifest.kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `items[].manifest.title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `items[].manifest.description` | `string` | ні | макс. довжина `10000` |
| `items[].manifest.tags` | array of `string` | ні |  |
| `items[].manifest.entry` | `PythonEntry` \| `StorageEntry` \| `LlmEntry` \| `CollectorRulesEntry` \| `ExecutorEntry` | так | Спосіб виконання; форма залежить від kind: extractor — PythonEntry; transform — PythonEntry або ExecutorEntry; storage — StorageEntry; llm — LlmEntry; collector-rules — CollectorRulesEntry. Відповідність kind ↔ entry додатково перевіряє репозиторій (validation_failed). |
| `items[].manifest.input` | `InputContract` | ні |  |
| `items[].manifest.params_schema` | `string` | ні | Шлях у пакеті до JSON Schema параметрів етапу.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `items[].manifest.output` | `OutputContract` | ні |  |
| `items[].manifest.dependencies` | `Dependencies` | ні |  |
| `items[].manifest.required_connections` | array of `ConnectionRequirement` | ні |  |
| `items[].manifest.access` | `object` | ні | Потрібні доступи під час виконання. За замовчуванням мережі немає. |
| `items[].manifest.tests` | array of `TestCase` | ні |  |
| `items[].manifest.provenance` | `Provenance` | так | Походження версії (ТЗ §7): хто і як її створив. |
| `items[].manifest.fork_of` | `package-ref` | ні | Батьківський пакет і вихідна версія форку (ТЗ §7). Встановлює репозиторій під час форку; далі переноситься в кожну версію форку без змін. |
| `items[].manifest.bindings_hint` | `object` | ні | Підказка, до яких матеріалів пакет доречно застосовувати. Не є прив'язкою: реальні прив'язки задаються в TaskConfig. |
| `items[].files` | array of `FileEntry` | ні |  |
| `items[].files[].path` | `string` | так | Відносний шлях усередині пакета, роздільник '/', без '..' і абсолютних шляхів.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `items[].files[].size_bytes` | `integer` | так | мін. `0` |
| `items[].files[].sha256` | `string` | так | шаблон `"^[a-f0-9]{64}$"` |
| `items[].size_bytes` | `integer` | ні | мін. `0` |
| `items[].created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].created_by` | `string` | ні | human \| llm \| import (з маніфесту) або ідентифікатор користувача. |
| `items[].published_by` | `string` | ні |  |
| `items[].status_history` | array of `object` | ні |  |
| `items[].status_history[].status` | enum: `draft`, `approved`, `rejected`, `deprecated`, `yanked` | так | draft — опубліковано, не погоджено; approved — дозволено активувати в етапах; rejected — відхилено; deprecated — не рекомендується для нових прив'язок; yanked — заборонено для нових прив'язок (наявні прив'язки не ламаються, архів доступний). |
| `items[].status_history[].at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].status_history[].by` | `string` | ні |  |
| `items[].status_history[].reason` | `string` | ні |  |
| `items[].test_reports` | array of `TestResultsRecord` | ні |  |
| `items[].test_reports[].runner` | `string` | ні |  |
| `items[].test_reports[].context` | `string` | ні | Де прогнано (наприклад на прив'язках певного етапу завдання). |
| `items[].test_reports[].report` | `TestReport` | так | Звіт прогону тестів пакета (без запису в робочі дані). |
| `items[].test_reports[].recorded_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].test_summary` | `TestSummary` | ні | Агрегат звітів тестів версії за контекстами (`TestResultsRecord.context`, наприклад `bindings:<task_id>/<stage_id>` — прогін на прив'язках етапу, `tests` — власні тести пакета). На відміну від `test_status` (стан останнього звіту) показує, чи пройшла версія **всюди**, де її перевіряли (ТЗ §9: зміни спільного пакета перевіряються для всіх його прив'язок). Для кожного контексту береться його останній звіт; звіти без `context` — один контекст без імені. `status`: `failed` — останній звіт хоч одного контексту має провалені кейси; `passed` — останній звіт кожного контексту пройшов (і звітів ≥ 1); інакше `unknown`. Віддається у повному поданні версії. |
| `items[].test_summary.status` | enum: `unknown`, `passed`, `failed` | так |  |
| `items[].test_summary.contexts` | array of `object` | так |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `versions`:

```json
{
  "items": [
    {
      "package_id": "shop-example.product-extractor",
      "version": "1.2.0",
      "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
      "status": "approved",
      "test_status": "passed",
      "created_at": "2026-09-27T09:40:00Z",
      "created_by": "llm"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
