# Типи пакетів

Усі пакети мають однаковий маніфест, версії, тести, походження й форки; відрізняються поле `kind`, форма `entry` і виконавець. Нормативна таблиця типів — [handler-packages.md](../../../contracts/docs/handler-packages.md); поля `entry` — [Структура й маніфест](manifest.md#entry).

## Зміст

- [Огляд](#огляд)
- [extractor](#extractor)
- [transform](#transform)
- [storage](#storage)
- [llm](#llm)
- [collector-rules](#collector-rules)

## Огляд

| kind | Вміст пакета | Виконавець | entry |
|---|---|---|---|
| `extractor` | Python-код у `src/`, схеми сутностей і параметрів, тести | Handler Runtime у пісочниці | `PythonEntry` |
| `transform` | Python-код або посилання на операцію сервісу | Handler Runtime або сервіс з `executor` | `PythonEntry` або `ExecutorEntry` |
| `storage` | Маніфест і конфігурація: адаптер, що записувати, формати; коду немає | Storage | `StorageEntry` |
| `llm` | Інструкції, шаблон входу, схема виходу, псевдонім моделі; коду немає | LLM gateway | `LlmEntry` |
| `collector-rules` | Файл правил обходу | Web Collector або Telegram Collector | `CollectorRulesEntry` |

Registry не виконує жоден пакет: він зберігає версії й віддає архів. Виконавець отримує архів від Registry або напряму від клієнта (наприклад, у `HandlerInvocation.package_archive`) і сам перевіряє `digest`.

## extractor

Екстрактор — Python-функція, що з матеріалу витягує сутності. Handler Runtime виконує її в контейнерній пісочниці без мережі, з бібліотеками профілю runtime.

- `entry`: `{"runtime": "python", "module": "<модуль відносно src/>", "callable": "<функція>"}`; Registry перевіряє, що в пакеті є `src/<модуль>.py` або `src/<модуль>/__init__.py`.
- Обов'язкові `output.entities[]` і `dependencies` (умова схеми) та тести `success` + `empty`/`unrecognized` (перевірка Registry).
- Код пишуть з [jane-extractor-sdk](../../../libs/extractor-sdk/README.md): сигнатура функції, типи результату й помічники описані в README SDK.

Приклади: [examples.testsite-catalog-extractor](../../../examples/packages/examples.testsite-catalog-extractor/jane-package.json), [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/jane-package.json), [examples.telegram-event-extractor](../../../examples/packages/examples.telegram-event-extractor/jane-package.json).

## transform

Перетворення даних або сутностей між етапами. Форма `PythonEntry` виконується Handler Runtime так само, як екстрактор; `ExecutorEntry` (`executor`, `operation`) посилається на операцію сервісу, що реалізує `handler.v1`. У репозиторії немає прикладу пакета `transform`.

## storage

Пакет збереження не містить коду: адаптери живуть у сервісі Storage, а пакет задає, який адаптер використати й що записувати.

- `entry`: `{"executor": "storage", "adapter": "postgresql", "writes": "raw_and_entities", "format": {...}, "history": true}`.
- Конкретне сховище етап задає через підключення: пакет оголошує лише `required_connections` (наприклад `{"name": "target", "kind": "postgresql"}`).
- Формати RAW і сутностей — [storage-adapter.md](../../../contracts/docs/storage-adapter.md).

Стандартні пакети `jane.storage-files`, `jane.storage-postgresql`, `jane.storage-sqlserver`, `jane.storage-mongodb`, `jane.storage-minio`, `jane.storage-s3` вбудовані в Storage, наприклад [jane.storage-postgresql](../../../services/storage/adapters/postgres/src/jane_storage_postgres/package/jane-package.json).

## llm

LLM-пакет описує запит до моделі: файл довірених інструкцій, шаблон недовірених вхідних даних і схему структурованого виходу. LLM gateway виконує його й перетворює вихід моделі на сутності за правилом розділу «Пакет llm» у [handler-packages.md](../../../contracts/docs/handler-packages.md).

- `entry`: `{"executor": "llm", "instructions": "prompts/instructions.md", "input_template": "prompts/input.md", "output_schema": "schemas/output.schema.json", "model": "default"}`.
- `model` — псевдонім з конфігурації LLM gateway, а не назва провайдера.
- Тести обов'язкові, як для екстрактора. Варто мати тест на ін'єкцію: вхід із текстом на кшталт «ignore previous instructions» має дати звичайний результат, як тест `prompt-injection-is-data` вбудованого пакета.

Приклад: вбудований пакет [jane.llm-event-extractor](../../../services/llm/packages/jane.llm-event-extractor/jane-package.json) з каталогами `prompts/`, `schemas/`, `tests/`.

## collector-rules

Правила колектора версіонуються як пакет, щоб на них поширювались ті самі версії, тести, форки й погодження, що й на обробники.

- `entry`: `{"collector": "web", "rules": "rules.json"}` або `"collector": "telegram"`.
- Файл правил відповідає [collector-rules.schema.json](../../../contracts/schemas/collector-rules.schema.json); Registry перевіряє його під час публікації, помилки повертаються з `pointer` `/files/rules.json/...`.
- Без Registry колектор приймає ті самі правила inline або з локального файла.

Приклади: [examples.testsite-web-rules](../../../examples/packages/examples.testsite-web-rules/jane-package.json), [examples.telegram-rules](../../../examples/packages/examples.telegram-rules/jane-package.json).
