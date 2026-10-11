# Експлуатація Jane

Розділ описує експлуатацію платформи загалом: запуск і зупинку, моніторинг, ліміти, оновлення, резервування, масштабування, безпеку й діагностику. Експлуатацію окремого модуля — його health-check, власні метрики, параметри й типові збої — описує `operations.md` у комплекті модуля, посилання нижче.

Інструкції перевірено на dev-стеку `infra/compose.yaml` (Windows 11, Docker Desktop, Docker Engine 29.8.0, ревізія `48389a3`, 2026-10-11). Production-розгортання (Kubernetes, керовані бази, зовнішній IdP) у репозиторії не описано й не перевірялося.

## Зміст

- [Сторінки розділу](#сторінки-розділу)
- [Модель експлуатації](#модель-експлуатації)
- [Власність даних](#власність-даних)
- [Експлуатація модулів](#експлуатація-модулів)

## Сторінки розділу

| Сторінка | Питання |
|---|---|
| [Запуск і зупинка](running.md) | як підняти стек, окремі сервіси, режим Orchestrator без планувальника |
| [Моніторинг](monitoring.md) | health, метрики Prometheus, журнали JSON, трасування |
| [Ліміти й профілі](limits.md) | рівні лімітів, жорсткі стелі, зміна без зміни коду |
| [Перевірка профілів](limits-validation.md) | вимірювання профілю harness L1–L8 і результати приймання |
| [Оновлення й міграції](upgrades.md) | як оновити сервіс і як сервіси оновлюють свої схеми |
| [Резервування й відновлення](backup-restore.md) | що резервувати за власністю даних і як відновити |
| [Масштабування](scaling.md) | які сервіси працюють кількома екземплярами й за яких умов |
| [Безпека експлуатації](security.md) | ключі API, scopes, секрети `env:`/`file:`, allowlist-и |
| [Типові проблеми](troubleshooting.md) | симптоми, причини, діагностика |

Довідка про сам dev-стек — [infra/README.md](../../infra/README.md); профілі лімітів — [deploy/profiles/README.md](../../deploy/profiles/README.md).

## Модель експлуатації

- **Кожен сервіс — окремий процес** із власним HTTP API `/v1`, конфігурацією через змінні середовища `JANE_<СЕРВІС>_*` і власним сховищем стану. Спільної бази немає.
- **Однакова обв'язка.** Усі сервіси створюються фабрикою `jane_kit.service.create_app`, тому мають однакові `GET /v1/health`, `GET /v1/info`, `GET /metrics`, формат журналів, автентифікацію й модель помилок.
- **Схеми даних сервіс оновлює сам** під час старту: окремого кроку міграції немає, зворотних міграцій теж немає.
- **Ліміти не зашиті в код.** Кожен ліміт має безпечне типове значення в моделі `Limits` сервісу; профіль `PlatformLimits` і змінні середовища змінюють його без перезбирання образу.
- **Orchestrator — не обов'язкова залежність.** Колектори, обробники й Registry працюють і без нього; Orchestrator лише поєднує їх у завдання.

## Власність даних

Що резервувати й відновлювати, визначає власність даних: кожен сервіс володіє лише своїм сховищем. Повна карта з відповідальністю за повтори — [contracts/docs/data-ownership.md](../../contracts/docs/data-ownership.md). Розміщення в dev-стеку:

| Сервіс | Власне сховище в dev-стеку | Що там лежить |
|---|---|---|
| Orchestrator | база `jane_orchestrator` | джерела, завдання, запуски, черга елементів, підключення (лише `secret_refs`), ліміти платформи, аудит |
| Registry | база `jane_registry` (схема `jane_registry`) + бакет `jane-registry` у MinIO | метадані пакетів і версій, звіти тестів; незмінні архіви версій за SHA-256 |
| LLM gateway | база `jane_llm` (схема `llm`) | провайдери, псевдоніми моделей, бюджети, облік витрат, кеш ідемпотентності |
| Assistant | база `jane_assistant` | сесії підключення джерел, job, кеш ідемпотентності |
| Handler Runtime | база `jane_handler_runtime` | кеш ідемпотентності, job, збережені результати викликів; бізнес-даних немає |
| Web Collector | том `web-collector-data` (`state.db`) | черга обходу, стан стратегій, буфер матеріалів, job |
| Telegram Collector | том `telegram-collector-data` (`state.db`) | курсори каналів, буфер, job |
| Storage | цільові сховища підключень; том `storage-data` | бізнес-результати користувача: сутності, історія, RAW, записи доставок |

Storage не має власної бази стану: бізнес-результати живуть у сховищах, на які вказують підключення (у dev-стеку — файли в томі `storage-data` і база `jane_storage_results`). Ці дані належать користувачеві, їх резервують засобами відповідного сховища.

![Власність даних у dev-стеку: сервіси, бази й томи](../diagrams/operations/data-ownership.light.png#gh-light-mode-only)
![Власність даних у dev-стеку: сервіси, бази й томи](../diagrams/operations/data-ownership.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/operations/data-ownership.light.png), [темне](../diagrams/operations/data-ownership.dark.png); джерело — [data-ownership.drawio](../diagrams/operations/data-ownership.drawio).

## Експлуатація модулів

| Модуль | Експлуатація |
|---|---|
| Web Collector | [operations.md](../components/web-collector/operations.md) |
| Telegram Collector | [operations.md](../components/telegram-collector/operations.md) |
| Storage | [operations.md](../components/storage/operations.md) |
| Handler Runtime | [operations.md](../components/handler-runtime/operations.md) |
| LLM gateway | [operations.md](../components/llm/operations.md) |
| Registry | [operations.md](../components/registry/operations.md) |
| Orchestrator | [operations.md](../components/orchestrator/operations.md) |
| Assistant | [operations.md](../components/assistant/operations.md) |
