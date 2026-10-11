# Схеми й тести пакета

Схеми задають форму параметрів, вхідних даних і результату пакета; тести показують, що пакет дає очікуваний результат на конкретних прикладах. Registry перевіряє, що схеми валідні й тести описані коректно, але сам тести не запускає: їх виконує виконавець пакета, а звіт записується у версію.

## Зміст

- [Схеми](#схеми)
- [Тестові випадки](#тестові-випадки)
- [Що вимагає Registry](#що-вимагає-registry)
- [Запуск тестів](#запуск-тестів)
- [Звіти тестів у версії](#звіти-тестів-у-версії)

## Схеми

Усі схеми — файли JSON Schema 2020-12 усередині пакета; маніфест посилається на них шляхом `PackagePath`.

| Поле маніфесту | Що описує | Хто застосовує |
|---|---|---|
| `params_schema` | Параметри етапу завдання; типові значення — через `default` | Виконавець перед викликом |
| `input.data_schema` | Вхідні дані `data` | Виконавець |
| `output.entities[].schema` | Поля `EntityRecord.fields` однієї сутності | Виконавець; невідповідність — `failed` / `schema_mismatch` |
| `output.data_schema` | Довільний вихід (`llm`, `transform`) | Виконавець |
| `entry.output_schema` | Структурований вихід моделі (`llm`) | LLM gateway |

Правила для схем сутностей:

- одна схема на `entity_type`;
- кожне поле з `key_fields` має бути в `required` схеми — інакше Registry відхиляє версію з `key_field_not_required`;
- `additionalProperties: false` робить схему суворою: екстрактор не зможе повернути поле, якого немає в схемі.

Схема сутності `product` пакета [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/schemas/product.schema.json):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "product (лише ціна й наявність)",
  "type": "object",
  "additionalProperties": false,
  "required": ["sku"],
  "properties": {
    "sku": {"type": "string", "minLength": 1},
    "price": {
      "type": "object",
      "additionalProperties": false,
      "required": ["amount", "currency"],
      "properties": {
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"}
      }
    },
    "availability": {"type": "string", "enum": ["in_stock", "out_of_stock", "preorder", "unknown"]}
  }
}
```

Сам результат обробника (`HandlerResult`, `EntityRecord`) визначено в [handler-result.schema.json](../../../contracts/schemas/handler-result.schema.json) і [entity.schema.json](../../../contracts/schemas/entity.schema.json); його описує [довідник handler.v1](../api/handler/README.md).

## Тестові випадки

Тест — елемент масиву `tests` маніфесту (поля — [Структура й маніфест](manifest.md#tests)). Вхід задається одним із полів `input`:

| Вхід | Коли використовувати | Приклад |
|---|---|---|
| `file` + `media_type` + `url` | Сирий файл (HTML-сторінка); метадані матеріалу будуються автоматично | [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/jane-package.json) |
| `material` | Повний JSON `Material` (повідомлення Telegram, нестандартні метадані) | [examples.telegram-event-extractor](../../../examples/packages/examples.telegram-event-extractor/jane-package.json) |
| `entities`, `data` | Вхід для пакетів, що приймають сутності або дані (`storage`, `transform`) | [jane.storage-postgresql](../../../services/storage/adapters/postgres/src/jane_storage_postgres/package/jane-package.json) |

Очікування:

- `expected_status` — `success`, `empty`, `unrecognized` або `failed`; обов'язкове.
- `expected` — JSON з очікуваним `output`, наприклад `{"entities": [...]}`. Порівняння ігнорує `provenance` і `observation` сутностей.
- `compare: exact` (типово) — результат має збігтися повністю; `subset` — кожне очікуване поле має збігтися, зайві поля допустимі.
- `origin` — `human`, `llm` або `problem_sample`. Проблемний матеріал, через який створено нову версію, додають як тест з `origin: problem_sample`.

Очікуваний результат тесту `product-phone-alpha`:

```json
{
  "entities": [
    {
      "entity_type": "product",
      "fields": {
        "sku": "phone-alpha",
        "price": {"amount": 299.0, "currency": "UAH"},
        "availability": "in_stock"
      },
      "completeness": "partial",
      "key": {"scope": "local", "natural": {"sku": "phone-alpha"}}
    }
  ]
}
```

## Що вимагає Registry

| Правило | Код помилки |
|---|---|
| `extractor` і `llm`: щонайменше один тест `success` і один `empty` або `unrecognized` | `tests_required` |
| Імена тестів унікальні | `duplicate_test` |
| Файли `input.*` і `expected` є в пакеті | `missing_file` |
| `expected` — валідний JSON | — |

Вимогу щодо `success` + `empty`/`unrecognized` вимикає `JANE_REGISTRY_REQUIRE_TESTS=false`; решта перевірок діє завжди. Пакети `storage`, `transform` і `collector-rules` можуть не мати тестів (як [examples.testsite-web-rules](../../../examples/packages/examples.testsite-web-rules/jane-package.json) з `"tests": []`).

## Запуск тестів

Registry тести не запускає. Варіанти запуску:

| Спосіб | Що потрібно | Результат |
|---|---|---|
| `jane-handler-runtime test <каталог або zip>` | Handler Runtime як CLI; пісочниця Docker або `--backend subprocess --unsafe-no-sandbox` для довіреного коду | Текстовий звіт або `TestReport` у файлі `-o` |
| `POST /v1/test-runs` (`handler.v1`) | Запущений виконавець пакета | Job, результат якого — `TestReport` |

Обидва способи нічого не записують у робочі дані (`test_mode`). Запуск тестів екстрактора з архіву, експортованого з Registry (команда з [quickstart Registry](../../components/registry/quickstart.md)):

```powershell
uv run --package jane-handler-runtime jane-handler-runtime test .jane/registry-quickstart/export/examples.testsite-price-extractor-1.0.0.zip --backend subprocess --unsafe-no-sandbox -o .jane/registry-quickstart/report.json
```

```text
package examples.testsite-price-extractor@1.0.0 (sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9), backend=subprocess
  PASS product-phone-alpha: expected success, got success
  PASS product-laptop-four-out-of-stock: expected success, got success
  PASS category-page-empty: expected empty, got empty
  PASS product-without-price-unrecognized: expected unrecognized, got unrecognized
4 passed, 0 failed
```

`--backend subprocess --unsafe-no-sandbox` виконує код без ізоляції — лише для пакетів із цього репозиторію. Робочий режим — пісочниця Docker або Podman; опис — у документації Handler Runtime.

## Звіти тестів у версії

Звіт записують у версію запитом `POST /v1/packages/{id}/versions/{version}/test-results` (scope `registry:write`). Тіло — `TestResultsRecord`:

| Поле | Зміст |
|---|---|
| `report` | `TestReport` з [handler-result.schema.json](../../../contracts/schemas/handler-result.schema.json); обов'язкове |
| `context` | Де перевірено: ім'я прив'язки, середовище (`local`, `task-a/extract`) |
| `runner` | Хто запускав |
| `recorded_at` | Час; якщо немає — ставить Registry |

Registry перевіряє `report` за схемою, а `report.package` — на збіг із версією: інший `package_id@version` дає `422 validation_failed`, інший `digest` — `422 digest_mismatch`. Звіти лише додаються, версія не змінюється.

Як обчислюється стан:

- `test_status` версії — стан останнього записаного звіту: `failed`, якщо в ньому є хоч один невдалий випадок; `passed`, якщо є вдалі; інакше `unknown`.
- `test_summary.status` — за останнім звітом **кожного** `context`: `passed`, лише якщо всі контексти `passed`; `failed`, якщо хоч один `failed`; інакше `unknown`. Так спільний пакет, перевірений на кількох прив'язках, не стає `passed` через один успішний контекст.

Orchestrator дозволяє автоматичну активацію версії лише за `test_summary.status = passed` ([Публікація й статуси](publication.md#погодження-й-активація)).
