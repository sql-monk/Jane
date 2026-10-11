# Власність даних

Кожен модуль Jane володіє власним сховищем; інші модулі отримують ці дані лише через його версіонований API. Спільної бази немає. Нормативна карта — [contracts/docs/data-ownership.md](../../contracts/docs/data-ownership.md); тут — як це влаштовано в поточній реалізації та dev-стеку.

## Зміст

- [Хто чим володіє](#хто-чим-володіє)
- [Сховища модулів](#сховища-модулів)
- [Що зберігає Orchestrator](#що-зберігає-orchestrator)
- [Дедуплікація й повтори](#дедуплікація-й-повтори)
- [Ізоляція баз у dev-стеку](#ізоляція-баз-у-dev-стеку)

## Хто чим володіє

![Власні сховища модулів і доступ до чужих даних через API](../diagrams/platform/data-ownership.light.png#gh-light-mode-only)
![Власні сховища модулів і доступ до чужих даних через API](../diagrams/platform/data-ownership.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/platform/data-ownership.light.png), [темне](../diagrams/platform/data-ownership.dark.png); джерело — [data-ownership.drawio](../diagrams/platform/data-ownership.drawio).

Схеми власних сховищ окремих модулів (таблиці, зв'язки) — у `internals.md` модуля з [каталогу](../components/README.md).

## Сховища модулів

| Модуль | Сховище | Без зовнішнього сховища | API доступу |
|---|---|---|---|
| Orchestrator | PostgreSQL `jane_orchestrator` | неможливо | `orchestrator.v1` |
| Registry | PostgreSQL `jane_registry` + blob у S3/MinIO (бакет `jane-registry`, префікс `sha256/`) | `JANE_REGISTRY_DB=memory`, `JANE_REGISTRY_BLOB=filesystem` | `registry.v1` |
| LLM gateway | PostgreSQL `jane_llm` (схема `llm`) | `JANE_LLM_STORE=memory` | `llm.v1`, `handler.v1` |
| Assistant | PostgreSQL `jane_assistant` | без `STATE_DSN` — пам'ять | `assistant.v1` |
| Handler Runtime | PostgreSQL `jane_handler_runtime` | без `STATE_DSN` — пам'ять, один екземпляр | `handler.v1` |
| Web Collector | SQLite `state.db` у `state_dir` (типово `.jane/web-collector`) | — (файл локальний) | `collector.v1` |
| Telegram Collector | SQLite у `state_dir` (типово `.jane/telegram-collector`) | — (файл локальний) | `collector.v1` |
| Storage | цільові сховища за підключеннями: PostgreSQL, SQL Server, MongoDB, MinIO, S3, файли | файловий адаптер потребує лише каталогу | `handler.v1` (запис), `storage.v1` (читання) |
| Admin UI | лише стан браузера | — | споживач API |

Пояснення:

- **Handler Runtime** не має бізнес-даних: лише кеш результатів за `delivery_key`, кеш пакетів і прогони тестів.
- **Storage** зберігає бізнес-результати: RAW-об'єкти, актуальний стан сутностей, історію змін і записи доставок. Власний том Storage у dev-стеку (`storage-data`) містить RAW файлового адаптера й транзитні blob великих матеріалів.
- **Колектори** зберігають стан обходу: чергу, відомі URL, стан стратегій, курсори каналів, буфер непідтверджених матеріалів і Job збору. Кілька екземплярів Web Collector узгоджують ліміти хоста через спільний каталог стану.
- **Assistant** зберігає сесії; створені ним пакети належать Registry.

Розбіжність із картою власності даних: вона згадує PostgreSQL `jane_web_collector` для Web Collector і SQLite для Handler Runtime. У коді колектори мають лише SQLite, а Handler Runtime — PostgreSQL або пам'ять — [обмеження](../overview/limitations.md#розбіжності-з-тз-і-контрактами).

## Що зберігає Orchestrator

Orchestrator не зберігає вмісту матеріалів і результатів — лише ідентифікатори (`material_id`, `observation_id`, `object_id`, `canonical_key`) для простежуваності; вміст читається через `storage.v1`.

| Таблиця | Дані |
|---|---|
| `sources`, `tasks` | документи джерел і завдань, розклад |
| `runs`, `items` | запуски й елементи етапів (черга з lease, спроби, посилання на збережений RAW) |
| `connections`, `connection_sync` | реєстр підключень (лише `secret_refs`) і черга їх поширення виконавцям |
| `platform_limits` | ліміти платформи |
| `activations`, `audit_events` | активації версій і аудит |
| `problem_groups`, `unknown_materials` | групи проблем і реєстр невідомих матеріалів |
| `budget_sync` | черга поширення бюджетів LLM у LLM gateway |
| `idempotency_keys`, `schema_migrations` | ключі ідемпотентності API, версія схеми |

## Дедуплікація й повтори

| Ситуація | Відповідальний | Механізм |
|---|---|---|
| Той самий URL знайдено кількома стратегіями | колектор | черга з дедуплікацією за канонічним URL |
| Колектор повторно видав матеріал, бо курсор не підтверджено | Orchestrator | той самий `observation_id` → той самий елемент етапу й `delivery_key` |
| Воркер Orchestrator зник під час виклику обробника | Orchestrator і обробник | lease закінчується → повтор із тим самим `delivery_key`; обробник повертає збережений результат |
| Повторна доставка результату в сховище | Storage | постійний запис `delivery_key` разом із даними |
| Повтор LLM-запиту | LLM gateway | кеш за `Idempotency-Key`; бюджет не списується вдруге |
| Повторне отримання матеріалу з джерела | — | не дубль: нове спостереження й новий запис історії |
| Запізнілий результат | Storage | порядок `observed_at → sequence → observation_id`; старіше значення — лише в історію |
| Повторна публікація версії пакета | Registry | версії незмінні: `version_exists` |

Механіка повторів і доставки — [виконання завдання](task-execution.md#доставка-без-дублів).

## Ізоляція баз у dev-стеку

Один сервер PostgreSQL dev-стеку містить окрему базу й окрему роль для кожного сервісу; привілеї `PUBLIC` відкликано, тож роль сервісу не має доступу до чужих баз ([infra/postgres/provision.sql](../../infra/postgres/provision.sql)). База `jane_storage_results` — не власне сховище Storage, а цільове сховище для прикладів, до якого Storage підключається через підключення `results-pg`.
