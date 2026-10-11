# POST /v1/packages/{package_id}/versions/{version}/status

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L479). Не редагуйте вручну.

**Змінити статус версії (погодити, відхилити, позначити застарілою) з аудитом**

| Властивість | Значення |
|---|---|
| operationId | `setPackageVersionStatus` |
| Метод і шлях | `POST /v1/packages/{package_id}/versions/{version}/status` |
| Scope | `registry:approve` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | versions |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `version` | path | `string` | так |  |
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `StatusChange`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `status` | enum: `approved`, `rejected`, `deprecated`, `yanked` | так |  |
| `reason` | `string` | ні | макс. довжина `2000` |

Приклад `approve`:

```json
{
  "status": "approved",
  "reason": "all tests passed on 3 bindings"
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Оновлена версія. | `PackageVersion` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `digest` | `string` | так | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `status` | enum: `draft`, `approved`, `rejected`, `deprecated`, `yanked` | так | draft — опубліковано, не погоджено; approved — дозволено активувати в етапах; rejected — відхилено; deprecated — не рекомендується для нових прив'язок; yanked — заборонено для нових прив'язок (наявні прив'язки не ламаються, архів доступний). |
| `test_status` | enum: `unknown`, `passed`, `failed` | так |  |
| `manifest` | `package-manifest` | ні | Маніфест пакета обробника або правил колектора (ТЗ §7) — файл 'jane-package.json' у корені архіву пакета. Пакет незмінний після публікації; дайджест архіву обчислює репозиторій. Що є пакетом для кожного типу — contracts/docs/handler-packages.md. Секрети в пакеті заборонені (репозиторій відхиляє з secret_detected). |
| `manifest.schema_version` | `"1"` | так |  |
| `manifest.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `manifest.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `manifest.kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `manifest.title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `manifest.description` | `string` | ні | макс. довжина `10000` |
| `manifest.tags` | array of `string` | ні |  |
| `manifest.entry` | `PythonEntry` \| `StorageEntry` \| `LlmEntry` \| `CollectorRulesEntry` \| `ExecutorEntry` | так | Спосіб виконання; форма залежить від kind: extractor — PythonEntry; transform — PythonEntry або ExecutorEntry; storage — StorageEntry; llm — LlmEntry; collector-rules — CollectorRulesEntry. Відповідність kind ↔ entry додатково перевіряє репозиторій (validation_failed). |
| `manifest.input` | `InputContract` | ні |  |
| `manifest.input.accepts` | array of enum: `material`, `entities`, `data` | ні | мін. елементів `1` |
| `manifest.input.media_types` | array of `string` | ні | Підтримувані медіатипи матеріалу (можна з '*': 'text/*'). |
| `manifest.input.content_kinds` | array of `string` | ні |  |
| `manifest.input.entity_types` | array of `string` | ні | Для accepts=entities: які типи сутностей приймає. |
| `manifest.input.data_schema` | `string` | ні | Відносний шлях усередині пакета, роздільник '/', без '..' і абсолютних шляхів.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `manifest.params_schema` | `string` | ні | Шлях у пакеті до JSON Schema параметрів етапу.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `manifest.output` | `OutputContract` | ні |  |
| `manifest.output.entities` | array of `object` | ні |  |
| `manifest.output.data_schema` | `string` | ні | Схема довільного виходу (llm, transform).; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `manifest.dependencies` | `Dependencies` | ні |  |
| `manifest.dependencies.runtime_profile` | `string` | ні | Профіль образу виконання handler-runtime, наприклад 'python-extractor@1'. Профіль визначає версію Python і набір дозволених бібліотек (docs/adr/0003-python-sandbox.md).; шаблон `"^[a-z0-9-]+@[0-9]+$"` |
| `manifest.dependencies.python` | array of `string` | ні | Вимоги PEP 508 з точною або обмеженою версією; мають бути задоволені профілем (інакше dependency_not_allowed). Встановлення з мережі під час виконання немає. |
| `manifest.dependencies.packages` | array of `package-ref` | ні | Інші пакети репозиторію, від яких залежить цей (зафіксовані версії). |
| `manifest.required_connections` | array of `ConnectionRequirement` | ні |  |
| `manifest.required_connections[].name` | `string` | так | Логічне ім'я, яке етап завдання зв'язує з connection_id.; шаблон `"^[a-z][a-z0-9_]{0,63}$"` |
| `manifest.required_connections[].kind` | `string` | так | шаблон `"^[a-z][a-z0-9_]{1,31}$"` |
| `manifest.required_connections[].purpose` | `string` | ні | макс. довжина `500` |
| `manifest.required_connections[].optional` | `boolean` | ні | типово `false` |
| `manifest.access` | `object` | ні | Потрібні доступи під час виконання. За замовчуванням мережі немає. |
| `manifest.access.network` | enum: `none`, `allowlist` | ні | типово `"none"` |
| `manifest.access.hosts` | array of `string` | ні | Для network=allowlist: дозволені хости (runtime може відмовити, якщо політика платформи забороняє). |
| `manifest.tests` | array of `TestCase` | ні |  |
| `manifest.tests[].name` | `string` | так | шаблон `"^[A-Za-z0-9._-]{1,100}$"` |
| `manifest.tests[].input` | `object` | так | Вхід тесту: material — JSON Material (вміст inline або файл через content_file); file — сирий файл + мінімальні метадані; entities/data — JSON-файл. |
| `manifest.tests[].params` | `object` | ні |  |
| `manifest.tests[].expected_status` | enum: `success`, `empty`, `unrecognized`, `failed` | так |  |
| `manifest.tests[].expected` | `string` | ні | JSON з очікуваним output (наприклад {"entities": [...]}); порівняння ігнорує provenance й observation.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `manifest.tests[].compare` | enum: `exact`, `subset` | ні | subset — кожне очікуване поле має збігтися, зайві поля допустимі.; типово `"exact"` |
| `manifest.tests[].origin` | enum: `human`, `llm`, `problem_sample` | ні | Звідки тест: написаний людиною, згенерований LLM або доданий із проблемного прикладу. |
| `manifest.provenance` | `Provenance` | так | Походження версії (ТЗ §7): хто і як її створив. |
| `manifest.provenance.created_by` | enum: `human`, `llm`, `import` | так |  |
| `manifest.provenance.authors` | array of `string` | ні |  |
| `manifest.provenance.created_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `manifest.provenance.based_on` | `package-ref` | ні | Попередня версія, з якої зроблено цю. |
| `manifest.provenance.change_summary` | `string` | ні | макс. довжина `4000` |
| `manifest.provenance.llm` | `object` | ні |  |
| `manifest.provenance.upstream_port` | `object` | ні | Для версії форку, створеної явним перенесенням змін батька. |
| `manifest.fork_of` | `package-ref` | ні | Батьківський пакет і вихідна версія форку (ТЗ §7). Встановлює репозиторій під час форку; далі переноситься в кожну версію форку без змін. |
| `manifest.fork_of.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `manifest.fork_of.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `manifest.fork_of.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `manifest.bindings_hint` | `object` | ні | Підказка, до яких матеріалів пакет доречно застосовувати. Не є прив'язкою: реальні прив'язки задаються в TaskConfig. |
| `manifest.bindings_hint.source_kinds` | array of `string` | ні |  |
| `manifest.bindings_hint.domains` | array of `string` | ні |  |
| `manifest.bindings_hint.url_patterns` | array of `string` | ні |  |
| `files` | array of `FileEntry` | ні |  |
| `files[].path` | `string` | так | Відносний шлях усередині пакета, роздільник '/', без '..' і абсолютних шляхів.; шаблон `"^(?!/)(?!.*(^\|/)\\.\\.(/\|$))[A-Za-z0-9._/-]{1,300}$"` |
| `files[].size_bytes` | `integer` | так | мін. `0` |
| `files[].sha256` | `string` | так | шаблон `"^[a-f0-9]{64}$"` |
| `size_bytes` | `integer` | ні | мін. `0` |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `created_by` | `string` | ні | human \| llm \| import (з маніфесту) або ідентифікатор користувача. |
| `published_by` | `string` | ні |  |
| `status_history` | array of `object` | ні |  |
| `status_history[].status` | enum: `draft`, `approved`, `rejected`, `deprecated`, `yanked` | так | draft — опубліковано, не погоджено; approved — дозволено активувати в етапах; rejected — відхилено; deprecated — не рекомендується для нових прив'язок; yanked — заборонено для нових прив'язок (наявні прив'язки не ламаються, архів доступний). |
| `status_history[].at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `status_history[].by` | `string` | ні |  |
| `status_history[].reason` | `string` | ні |  |
| `test_reports` | array of `TestResultsRecord` | ні |  |
| `test_reports[].runner` | `string` | ні |  |
| `test_reports[].context` | `string` | ні | Де прогнано (наприклад на прив'язках певного етапу завдання). |
| `test_reports[].report` | `TestReport` | так | Звіт прогону тестів пакета (без запису в робочі дані). |
| `test_reports[].report.package` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `test_reports[].report.passed` | `integer` | так | мін. `0` |
| `test_reports[].report.failed` | `integer` | так | мін. `0` |
| `test_reports[].report.cases` | array of `TestCaseResult` | так |  |
| `test_reports[].report.started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `test_reports[].report.finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `test_reports[].recorded_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `test_summary` | `TestSummary` | ні | Агрегат звітів тестів версії за контекстами (`TestResultsRecord.context`, наприклад `bindings:<task_id>/<stage_id>` — прогін на прив'язках етапу, `tests` — власні тести пакета). На відміну від `test_status` (стан останнього звіту) показує, чи пройшла версія **всюди**, де її перевіряли (ТЗ §9: зміни спільного пакета перевіряються для всіх його прив'язок). Для кожного контексту береться його останній звіт; звіти без `context` — один контекст без імені. `status`: `failed` — останній звіт хоч одного контексту має провалені кейси; `passed` — останній звіт кожного контексту пройшов (і звітів ≥ 1); інакше `unknown`. Віддається у повному поданні версії. |
| `test_summary.status` | enum: `unknown`, `passed`, `failed` | так |  |
| `test_summary.contexts` | array of `object` | так |  |
| `test_summary.contexts[].context` | `string` | ні | Відсутнє — звіти без context. |
| `test_summary.contexts[].test_status` | enum: `unknown`, `passed`, `failed` | так |  |
| `test_summary.contexts[].recorded_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `test_summary.contexts[].runner` | `string` | ні |  |
| `test_summary.contexts[].reports` | `integer` | так | Скільки звітів записано для цього контексту (діє останній).; мін. `1` |

Приклад `version`:

```json
{
  "package_id": "shop-example.product-extractor",
  "version": "1.2.0",
  "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
  "status": "approved",
  "test_status": "passed",
  "manifest": {
    "schema_version": "1",
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "kind": "extractor",
    "title": "Shop Example product cards",
    "entry": {
      "runtime": "python",
      "module": "product_extractor.main",
      "callable": "extract"
    },
    "output": {
      "entities": [
        {
          "entity_type": "product",
          "schema": "schemas/product.schema.json",
          "key_fields": [
            "sku"
          ]
        }
      ]
    },
    "dependencies": {
      "runtime_profile": "python-extractor@1",
      "python": [
        "selectolax>=0.3,<0.4"
      ]
    },
    "provenance": {
      "created_by": "llm"
    }
  },
  "files": [
    {
      "path": "jane-package.json",
      "size_bytes": 1520,
      "sha256": "1f2e3d4c5b6a79880f1e2d3c4b5a69788f9e0d1c2b3a49586f7e8d9c0b1a2f3e"
    },
    {
      "path": "src/product_extractor/main.py",
      "size_bytes": 2210,
      "sha256": "2a3b4c5d6e7f80910a1b2c3d4e5f60718a9b0c1d2e3f40516a7b8c9d0e1f2a3b"
    }
  ],
  "size_bytes": 18422,
  "created_at": "2026-09-27T09:40:00Z",
  "created_by": "llm",
  "status_history": [
    {
      "status": "draft",
      "at": "2026-09-27T09:40:00Z",
      "by": "assistant"
    },
    {
      "status": "approved",
      "at": "2026-09-27T10:15:00Z",
      "by": "admin@example.org",
      "reason": "tests passed"
    }
  ],
  "test_summary": {
    "status": "passed",
    "contexts": [
      {
        "context": "bindings:shop-catalog/extract-products",
        "test_status": "passed",
        "recorded_at": "2026-09-27T10:10:00Z",
        "runner": "assistant",
        "reports": 1
      },
      {
        "context": "tests",
        "test_status": "passed",
        "recorded_at": "2026-09-27T10:09:00Z",
        "runner": "handler-runtime@0.1.0",
        "reports": 2
      }
    ]
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `409`.
