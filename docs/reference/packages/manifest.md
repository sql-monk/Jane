# Структура пакета й маніфест

Пакет — zip-архів із маніфестом `jane-package.json` у корені. Маніфест описує тип пакета, спосіб виконання, вхід і вихід, залежності, тести й походження. Нормативна схема — [package-manifest.schema.json](../../../contracts/schemas/package-manifest.schema.json) (JSON Schema 2020-12); Registry перевіряє маніфест саме за нею й додатково виконує перевірки з розділу [Перевірки Registry понад схему](#перевірки-registry-понад-схему).

## Зміст

- [Файли пакета](#файли-пакета)
- [Шляхи у пакеті](#шляхи-у-пакеті)
- [Поля маніфесту](#поля-маніфесту)
- [Вкладені об'єкти](#вкладені-обєкти)
- [Перевірки Registry понад схему](#перевірки-registry-понад-схему)
- [Приклад маніфесту](#приклад-маніфесту)

## Файли пакета

Розташування файлів, крім маніфесту, — домовленість; Registry вимагає лише, щоб кожен файл, на який посилається маніфест, був у пакеті. Дерево пакета [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/):

```text
examples.testsite-price-extractor/
├── jane-package.json                  # маніфест (обов'язковий)
├── schemas/
│   ├── params.schema.json             # параметри етапу (params_schema)
│   └── product.schema.json            # поля сутності product (output.entities[].schema)
├── src/jane_example_price/
│   ├── __init__.py
│   └── main.py                        # entry.module = jane_example_price.main
└── tests/
    ├── product-phone-alpha/
    │   ├── page.html                  # вхід тесту (tests[].input.file)
    │   └── expected.json              # очікуваний вихід (tests[].expected)
    └── …
```

Інші типові каталоги: `prompts/` — інструкції й шаблон входу LLM-пакета, `rules.json` — правила колектора. Перелік за типами — [Типи пакетів](kinds.md).

## Шляхи у пакеті

Кожен шлях у маніфесті й у архіві має формат `PackagePath`:

- лише символи `A-Z a-z 0-9 . _ / -`, від 1 до 300 символів;
- роздільник `/`, без `/` на початку, без сегментів `..` і `.`, без `//` і `/` у кінці;
- шляхи, що відрізняються лише регістром літер, у одному пакеті заборонені (вони збігаються на Windows і macOS);
- симлінки, каталоги як окремі записи та зашифровані записи ZIP не приймаються.

Файли `.env`, ключі, токени й паролі в пакеті заборонені: Registry відхиляє такий пакет із `secret_detected` ([Залежності й доступи](dependencies.md#заборона-секретів)).

## Поля маніфесту

Верхній рівень не допускає невідомих полів (`additionalProperties: false`).

| Поле | Тип | Обов'язкове | Зміст |
|---|---|---|---|
| `schema_version` | рядок, константа `"1"` | так | Версія формату маніфесту |
| `package_id` | `Slug` | так | Ідентифікатор пакета: `a-z 0-9 . _ -`, до 100 символів |
| `version` | `SemVer` | так | Точна версія Semantic Versioning 2.0.0 |
| `kind` | `HandlerKind` | так | `extractor`, `storage`, `llm`, `transform` або `collector-rules` |
| `title` | рядок, 1–200 | так | Назва для людини |
| `description` | рядок, до 10000 | ні | Опис призначення |
| `tags` | масив рядків `^[a-z0-9][a-z0-9-]{0,40}$`, унікальні | ні | Мітки для пошуку (`GET /v1/packages?tag=`) |
| `entry` | один із `PythonEntry`, `StorageEntry`, `LlmEntry`, `CollectorRulesEntry`, `ExecutorEntry` | так | Спосіб виконання; форма залежить від `kind` |
| `input` | `InputContract` | ні | Що пакет приймає |
| `params_schema` | `PackagePath` | ні | JSON Schema параметрів етапу |
| `output` | `OutputContract` | для `extractor` — так | Які сутності або дані пакет повертає |
| `dependencies` | `Dependencies` | для `extractor` — так | Профіль runtime, Python-вимоги, залежності від інших пакетів |
| `required_connections` | масив `ConnectionRequirement` | ні | Потрібні підключення (лише ім'я й тип, без секретів) |
| `access` | об'єкт | ні | Мережевий доступ під час виконання |
| `tests` | масив `TestCase` | ні за схемою | Тестові випадки; для `extractor` і `llm` Registry вимагає щонайменше два |
| `provenance` | `Provenance` | так | Хто і з чого створив версію |
| `fork_of` | `PackageRef` | ні | Батько форку; задає лише Registry |
| `bindings_hint` | об'єкт | ні | Підказка, до яких матеріалів пакет доречний |

Пояснення до таблиці:

- Типи `Slug`, `SemVer`, `Digest`, `HandlerKind` визначено в [defs.schema.json](../../../contracts/schemas/common/defs.schema.json).
- `output` і `dependencies` обов'язкові лише для `kind: extractor` (умова `allOf` схеми).
- Вимогу до `tests` для `extractor` і `llm` перевіряє Registry, а не схема; її можна вимкнути налаштуванням `JANE_REGISTRY_REQUIRE_TESTS=false` ([конфігурація Registry](../../components/registry/configuration.md)).
- `bindings_hint` не прив'язує пакет до матеріалів: реальні прив'язки задає етап завдання в Orchestrator. Registry використовує `bindings_hint.domains` для пошуку `GET /v1/packages?domain=`.

## Вкладені об'єкти

### entry

Форму `entry` обирають за `kind`; відповідність `kind ↔ entry` перевіряє Registry (`entry_kind_mismatch`). Призначення кожного типу — [Типи пакетів](kinds.md).

| Форма | Поля | Обов'язкові | Для `kind` |
|---|---|---|---|
| `PythonEntry` | `runtime: "python"`, `module` (Python-модуль відносно `src/`), `callable` (ім'я функції) | усі три | `extractor`, `transform` |
| `ExecutorEntry` | `executor` (ім'я сервісу-виконавця), `operation` | `executor` | `transform` |
| `StorageEntry` | `executor: "storage"`, `adapter`, `writes`, `format`, `history` | `executor`, `adapter`, `writes` | `storage` |
| `LlmEntry` | `executor: "llm"`, `instructions`, `input_template`, `output_schema`, `model`, `temperature`, `max_output_tokens` | `executor`, `instructions`, `output_schema` | `llm` |
| `CollectorRulesEntry` | `collector`, `rules` | обидва | `collector-rules` |

Значення полів:

- `StorageEntry.adapter` — тип адаптера (`filesystem`, `postgresql`, `sqlserver`, `mongodb`, `minio`, `s3`); `writes` — `raw`, `entities`, `raw_and_entities` або `data`; `format.raw` — `original`, `html` або `json`; `format.entities` — `json` (типово) або `jsonl`; `history` — зберігати історію оновлень сутностей (типово `true`). Формати RAW описано в [storage-adapter.md](../../../contracts/docs/storage-adapter.md).
- `LlmEntry.instructions`, `input_template`, `output_schema` — `PackagePath` до файлів пакета; `model` — псевдонім моделі з конфігурації LLM gateway (`default`, `cheap`, `strong`), а не провайдер; `temperature` — від 0 до 2; `max_output_tokens` — ціле від 1.
- `CollectorRulesEntry.collector` — `web` або `telegram`; `rules` — `PackagePath` до файлу за [collector-rules.schema.json](../../../contracts/schemas/collector-rules.schema.json).

### input

| Поле | Тип | Зміст |
|---|---|---|
| `accepts` | масив з `material`, `entities`, `data`, щонайменше один | Види входу |
| `media_types` | масив рядків | Медіатипи матеріалу, можна з `*`: `text/*` |
| `content_kinds` | масив рядків | Види вмісту матеріалу (`page`, `message`) |
| `entity_types` | масив рядків | Для `accepts: entities` — типи сутностей на вході |
| `data_schema` | `PackagePath` | Схема вхідних даних `data` |

`media_types` також використовується пошуком `GET /v1/packages?media_type=`.

### output

| Поле | Тип | Зміст |
|---|---|---|
| `entities[]` | масив об'єктів | Типи сутностей, які повертає пакет |
| `entities[].entity_type` | рядок `^[a-z][a-z0-9_]{0,63}$`, обов'язкове | Тип сутності |
| `entities[].schema` | `PackagePath`, обов'язкове | JSON Schema 2020-12 полів сутності |
| `entities[].key_fields` | масив рядків, щонайменше один, обов'язкове | Поля природного ключа |
| `entities[].description` | рядок | Опис |
| `data_schema` | `PackagePath` | Схема довільного виходу (`llm`, `transform`) |

Як писати ці схеми — [Схеми й тести](schemas-and-tests.md#схеми).

### dependencies

| Поле | Тип | Зміст |
|---|---|---|
| `runtime_profile` | рядок `^[a-z0-9-]+@[0-9]+$` | Профіль образу виконання, наприклад `python-extractor@1` |
| `python` | масив рядків до 200 символів | Вимоги PEP 508, які мають задовольнятися профілем |
| `packages` | масив `PackageRef` | Інші пакети Registry з точними версіями |

Правила перевірки — [Залежності й доступи](dependencies.md).

### access і required_connections

| Поле | Тип | Зміст |
|---|---|---|
| `access.network` | `none` (типово) або `allowlist` | Мережевий доступ під час виконання |
| `access.hosts` | масив рядків | Для `allowlist` — дозволені хости |
| `required_connections[].name` | рядок `^[a-z][a-z0-9_]{0,63}$`, обов'язкове | Логічне ім'я, яке етап зв'язує з `connection_id` |
| `required_connections[].kind` | `ConnectionKind`, обов'язкове | Тип підключення: `postgresql`, `s3`, `filesystem`, `llm_provider`… |
| `required_connections[].purpose` | рядок до 500 | Для чого підключення |
| `required_connections[].optional` | boolean, типово `false` | Чи можна виконати пакет без підключення |

`ConnectionRequirement` визначено в [connection.schema.json](../../../contracts/schemas/common/connection.schema.json).

### tests

| Поле | Тип | Обов'язкове | Зміст |
|---|---|---|---|
| `name` | рядок `^[A-Za-z0-9._-]{1,100}$` | так | Ім'я, унікальне в пакеті |
| `input` | об'єкт, щонайменше одне поле | так | Вхід тесту |
| `input.material` | `PackagePath` | ні | JSON `Material` |
| `input.file` | `PackagePath` | ні | Сирий файл; разом із `media_type` і `url` |
| `input.media_type`, `input.url` | рядок, URI | ні | Метадані для `file` |
| `input.entities`, `input.data` | `PackagePath` | ні | JSON із сутностями або даними |
| `params` | об'єкт | ні | Параметри етапу для тесту |
| `expected_status` | `success`, `empty`, `unrecognized`, `failed` | так | Очікуваний стан результату |
| `expected` | `PackagePath` | ні | JSON з очікуваним `output` |
| `compare` | `exact` (типово) або `subset` | ні | Як порівнювати з `expected` |
| `origin` | `human`, `llm`, `problem_sample` | ні | Звідки тест |

### provenance

| Поле | Тип | Обов'язкове | Зміст |
|---|---|---|---|
| `created_by` | `human`, `llm`, `import` | так | Хто створив версію |
| `authors` | масив рядків | ні | Автори |
| `created_at` | `Timestamp` | ні | Час створення |
| `based_on` | `PackageRef` | ні | Попередня версія, з якої зроблено цю |
| `change_summary` | рядок до 4000 | ні | Що змінено |
| `llm.provider`, `llm.model` | рядок | ні | Модель, яка створила версію |
| `llm.assistant_job_id` | `Id` | ні | Job асистента |
| `llm.reason` | `onboarding`, `improvement`, `unknown_material`, `upstream_port` | ні | Причина створення |
| `upstream_port.parent_version` | `SemVer` | так, якщо є `upstream_port` | Перенесена версія батька |
| `upstream_port.requested_by` | рядок | ні | Хто запросив перенесення |

Правила заповнення — [Походження й форки](provenance-and-forks.md).

### fork_of і посилання на пакет

`fork_of`, `provenance.based_on` і `dependencies.packages[]` мають тип `PackageRef` ([package-ref.schema.json](../../../contracts/schemas/common/package-ref.schema.json)): `package_id` і `version` обов'язкові, `digest` (`sha256:` і 64 шістнадцяткові символи) — необов'язковий. Діапазони версій і `latest` заборонені.

### bindings_hint

| Поле | Тип | Зміст |
|---|---|---|
| `source_kinds` | масив `SourceKind` | Види джерел (`web`, `telegram`) |
| `domains` | масив рядків | Домени; пошук `domain=` збігається також із піддоменами |
| `url_patterns` | масив рядків | Шаблони URL |

## Перевірки Registry понад схему

Після перевірки за схемою Registry ([validation.py](../../../services/registry/src/jane_registry/validation.py)) перевіряє:

| Перевірка | Код у `errors[]` |
|---|---|
| `entry` відповідає `kind` | `entry_kind_mismatch` |
| Кожен файл, на який посилається маніфест, є в пакеті | `missing_file` |
| Для `runtime: python` є `src/<module>.py` або `src/<module>/__init__.py` | `missing_file` |
| Файли схем — валідний JSON і валідна JSON Schema 2020-12 | `invalid_schema` |
| Кожне поле з `key_fields` є в `required` схеми сутності | `key_field_not_required` |
| Файл правил `collector-rules` відповідає `collector-rules.schema.json` | `schema` або `invalid_rules` |
| Імена тестів унікальні | `duplicate_test` |
| Файли `expected` — валідний JSON | — |
| `extractor` і `llm` мають тест `success` і тест `empty` або `unrecognized` | `tests_required` |
| `package_id` і `kind` маніфесту збігаються з пакетом, у який публікують | — |
| `fork_of` відсутній у звичайному пакеті й незмінний у форку | — |

Усі ці помилки повертаються як `422 validation_failed` з `errors[].pointer` на поле (`/manifest/...` або `/files/...`). Повний порядок перевірок публікації — [Публікація й статуси](publication.md#перевірки-під-час-публікації).

## Приклад маніфесту

Маніфест [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/jane-package.json) (уривок: без полів `description` і двох із чотирьох тестів):

```json
{
  "schema_version": "1",
  "package_id": "examples.testsite-price-extractor",
  "version": "1.0.0",
  "kind": "extractor",
  "title": "Jane test site: price and availability only",
  "tags": ["examples", "testsite", "products", "prices"],
  "entry": {"runtime": "python", "module": "jane_example_price.main", "callable": "extract"},
  "input": {"accepts": ["material"], "media_types": ["text/html"], "content_kinds": ["page"]},
  "params_schema": "schemas/params.schema.json",
  "output": {
    "entities": [
      {"entity_type": "product", "schema": "schemas/product.schema.json", "key_fields": ["sku"]}
    ]
  },
  "dependencies": {"runtime_profile": "python-extractor@1", "python": []},
  "access": {"network": "none"},
  "tests": [
    {
      "name": "product-phone-alpha",
      "input": {
        "file": "tests/product-phone-alpha/page.html",
        "media_type": "text/html",
        "url": "http://testsite:8080/product/phone-alpha"
      },
      "expected_status": "success",
      "expected": "tests/product-phone-alpha/expected.json",
      "compare": "exact",
      "origin": "human"
    },
    {
      "name": "category-page-empty",
      "input": {
        "file": "tests/category-laptops/page.html",
        "media_type": "text/html",
        "url": "http://testsite:8080/catalog/laptops/"
      },
      "expected_status": "empty",
      "origin": "human"
    }
  ],
  "provenance": {
    "created_by": "human",
    "authors": ["WP-14"],
    "created_at": "2026-09-30T00:00:00Z",
    "change_summary": "Partial price and availability update for the reproducible price-check example."
  },
  "bindings_hint": {"source_kinds": ["web"], "url_patterns": ["/product/*"]}
}
```
