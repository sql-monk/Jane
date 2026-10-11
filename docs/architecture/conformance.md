# Відповідність архітектури ТЗ

Сторінка зіставляє вимоги ТЗ з поточним кодом і виділяє межі, які впливають на інтеграцію або розгортання.

## Реалізована основа

| Вимога | Реалізація | Джерело |
|---|---|---|
| §4: автономні модулі | Колектори приймають правила, Runtime — локальний пакет і входи | [колектор](../../contracts/openapi/collector.v1.yaml), [Runtime packages](../../services/handler-runtime/src/jane_handler_runtime/packages.py) |
| §4: власність стану | Власні сервісні бази/каталоги, взаємодія через API | [provision.sql](../../infra/postgres/provision.sql), [Executors](../../services/orchestrator/src/jane_orchestrator/executors.py) |
| §4: асинхронність | Job, polling, cancellation | [Job](../../contracts/schemas/common/job.schema.json), [jobs](../../libs/jane-kit/src/jane_kit/jobs.py) |
| §5–§6: RAW, сутності й часткові оновлення | Storage adapters, порядок полів, явне `cleared` | [merge](../../services/storage/src/jane_storage/merge.py) |
| §7: пакети, версії та форки | Registry з незмінними версіями й походженням | [Registry service](../../services/registry/src/jane_registry/service.py) |
| §8–§9: дослідження й вдосконалення | Assistant workflows та LLM gateway | [onboarding](../../services/assistant/src/jane_assistant/onboarding.py), [improvement](../../services/assistant/src/jane_assistant/improvement.py) |
| §11: повторна доставка й відновлення | Leases, stable keys, retry та acknowledgements | [Engine](../../services/orchestrator/src/jane_orchestrator/engine.py) |
| §13.1: конфігуровані ліміти | Профілі, deep merge, hard caps, provenance | [limits](../../contracts/schemas/common/limits.schema.json), [merge_limits](../../services/orchestrator/src/jane_orchestrator/limits.py) |

Наявність реалізації підтверджена статичним читанням джерел. Фактичне приймання сценаріїв, зовнішніх сервісів і профілів ресурсів має окремі runtime-докази; DOC-04 не запускав ці сценарії.

## Окремі записи про межі реалізації

### C-01 — Масштабування колекторів між вузлами

**Вимога:** ТЗ §4 передбачає незалежне масштабування кількома екземплярами. **Поточний механізм:** Web і Telegram використовують спільний SQLite-файл та leases. **Межа:** це підтверджує координацію процесів зі спільним станом; розподілена база або довільне багатовузлове файлове середовище потребує окремої реалізації чи перевірки. Автоматичного масштабування через ізольовані SQLite-файли немає.

Джерела: [Web state](../../services/web-collector/src/jane_web_collector/state.py), [Telegram state](../../services/telegram-collector/src/jane_telegram_collector/state.py). Наслідки: [масштабування](deployment.md#кілька-екземплярів).

### C-02 — Залежності й мережа Python-пакета

**Вимога:** ТЗ §7 дозволяє пакету декларувати залежності й доступи. **Поточний механізм:** Runtime виконує Python у дозволеному image profile, Docker backend використовує `network_mode=none`. **Межа:** декларація доступу в маніфесті не вмикає мережу або встановлення довільної бібліотеки під час invocation; потрібна підтримка профілем і політикою Runtime.

Джерела: [manifest](../../contracts/schemas/package-manifest.schema.json), [profiles](../../services/handler-runtime/src/jane_handler_runtime/profiles/), [Docker backend](../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py). Рішення: [ADR-0003](../adr/0003-python-sandbox.md).

### C-03 — Розповсюдження пакетів: відкрите питання ТЗ закрите реалізацією

**Початкове питання:** ТЗ §13.2 залишає вибір технології репозиторію пакетів відкритим. **Поточне рішення:** Registry має PostgreSQL backend для метаданих та S3/MinIO або files backend для content-addressed артефактів, незмінні версії й API export. **Наслідок:** це вже фактичний вибір реалізації; опис не повинен представляти його як майбутню невизначеність.

Джерела: [postgres](../../services/registry/src/jane_registry/postgres.py), [blobs](../../services/registry/src/jane_registry/blobs.py), [export](../../services/registry/src/jane_registry/export.py). Рішення: [ADR-0002](../adr/0002-package-registry.md).

### C-04 — Довговічний стан залежить від backend

**Вимога:** ТЗ §11 передбачає відновлення після збоїв. **Поточний механізм:** Runtime, Assistant, LLM і Registry мають memory-режими поряд із PostgreSQL. **Межа:** memory зберігає стан одного процесу до його завершення; довговічність і координація кількох екземплярів потребують PostgreSQL-конфігурації. Це умова підтримуваного режиму, а не гарантія будь-якого запуску.

Джерела: [Runtime settings](../../services/handler-runtime/src/jane_handler_runtime/settings.py), [Assistant settings](../../services/assistant/src/jane_assistant/settings.py), [LLM settings](../../services/llm/src/jane_llm/settings.py), [Registry settings](../../services/registry/src/jane_registry/settings.py).

## Перевірена ревізія

Основа: `91876d1c369e91838cee9204658cc92a248adf95`, дата 2026-10-11. Зауваження про runtime-перевірки та render gate наведено у [DOC-04](../delivery/documentation/DOC-04.md). Окремих доведених читань чужих внутрішніх таблиць у досліджених шляхах взаємодії не виявлено; спільні blob-томи описані як транспорт [ContentRef](data.md#передавання-вмісту).
