# Handler Runtime: залежності

Handler Runtime потребує лише контейнерної платформи з образом профілю виконання. Решта залежностей — опційні: вони потрібні для окремих джерел пакетів і вмісту або для кількох екземплярів.

## Зміст

- [Огляд](#огляд)
- [Обов'язкові](#обовязкові)
- [Опційні](#опційні)
- [Бібліотеки Python](#бібліотеки-python)
- [Поведінка за недоступності](#поведінка-за-недоступності)

## Огляд

| Залежність | Обов'язковість | Навіщо | Сумісна версія |
|---|---|---|---|
| Docker Engine або Podman | обов'язкова для бекенда `docker` | контейнер пісочниці на кожен виклик | Docker Engine API; перевірено Docker Desktop 29.8 |
| Образ профілю `python-extractor@1` | обов'язкова | Python, SDK і бібліотеки пісочниці | збирається з репозиторію, базовий образ `python:3.12.12-slim-bookworm` |
| Каталог контрактів `contracts/` | обов'язкова | JSON Schema запитів, маніфесту, сутностей | з тієї самої ревізії, що й код |
| Registry | опційна | пакети за `package_id` і `version` | `registry.v1` |
| PostgreSQL | опційна | спільний стан кількох екземплярів | dev-стек — `postgres:18` |
| Каталоги `file://` і HTTP(S)-хости | опційні | вміст матеріалів і архіви пакетів за посиланням | — |

## Обов'язкові

### Контейнерна платформа

Бекенд `docker` (типовий) працює через Docker Engine API бібліотекою `docker` для Python: створює контейнер, копіює в нього пакет і вхідні дані, запускає, чекає, читає журнали й видаляє. Адреса — `JANE_HANDLER_RUNTIME_DOCKER_HOST`, інакше `DOCKER_HOST` або типовий сокет платформи (named pipe Docker Desktop на Windows, `/var/run/docker.sock` на Linux).

- **Docker Desktop** на Windows — Linux-контейнери; перевірено версію 29.8.
- **Docker Engine** на Linux — у dev-стеку сокет хоста монтується в контейнер сервісу (`infra/compose.yaml`, змінні `JANE_DOCKER_SOCKET` і `JANE_DOCKER_GID`).
- **Podman** — через сумісний з Docker API сокет у `JANE_HANDLER_RUNTIME_DOCKER_HOST`; не перевірено.
- **gVisor** — `JANE_HANDLER_RUNTIME_DOCKER_RUNTIME=runsc`, якщо runtime встановлено в рушії; не перевірено.

Доступ до сокета Docker рівнозначний правам адміністратора хоста. Для продакшну розгляньте rootless Podman, окремий вузол для Handler Runtime або socket-proxy з мінімальними правами.

Бекенд `subprocess` контейнерної платформи не потребує, але не ізолює код — див. [configuration.md](configuration.md#бекенд-пісочниці).

### Образ профілю виконання

Образ збирає команда `jane-handler-runtime build-image` з файлів репозиторію: [Dockerfile](../../../services/handler-runtime/sandbox/python-extractor-1/Dockerfile), [requirements.txt](../../../services/handler-runtime/sandbox/python-extractor-1/requirements.txt) і коду [jane-extractor-sdk](../extractor-sdk/README.md). Під час виконання в образ нічого не встановлюється: у пісочниці немає мережі.

Опис профілю — [python-extractor-1.json](../../../services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json): версія Python, точні версії бібліотек і версія SDK. Unit-тест перевіряє, що `requirements.txt` збігається з цим описом. Той самий опис публікує `GET /v1/info` у `capabilities.runtime_profiles`, і за ним Registry перевіряє `dependencies.python` маніфестів.

### Контракти

Сервіс перевіряє запити й результати за JSON Schema з `contracts/schemas` і читає `contracts/openapi/handler.v1.yaml` для `TestRunRequest`. У checkout каталог знаходиться автоматично; в образі сервісу він лежить у `/app/contracts` (`JANE_HANDLER_RUNTIME_CONTRACTS_DIR`). Без контрактів сервіс не стартує.

## Опційні

### Registry

Потрібен, якщо запит не містить `package_archive`. Сервіс завантажує `GET /v1/packages/{package_id}/versions/{version}/archive` з `Authorization: Bearer <JANE_HANDLER_RUNTIME_REGISTRY_TOKEN>`, звіряє `ETag` з дайджестом архіву й `handler.digest`, якщо його задано. Без `JANE_HANDLER_RUNTIME_REGISTRY_URL` у `capabilities.package_sources` лише `package_archive`. Опис Registry — [Registry](../registry/README.md).

### PostgreSQL

Потрібен для кількох екземплярів за балансувальником: ключі ідемпотентності, job і результати викликів спільні, повторну доставку обробляє будь-який екземпляр. Без `JANE_HANDLER_RUNTIME_STATE_DSN` стан у пам'яті процесу. Схема даних — [internals.md](internals.md#стан-сервісу).

Робота з PostgreSQL у цій документації не перевірялася запуском; схему й поведінку описано за кодом `state.py` і `jane_kit.stores.postgres`.

### Вміст за посиланням

- `file://` — лише всередині каталогів `JANE_HANDLER_RUNTIME_BLOB_ROOTS`; шлях нормалізується, вихід за межі через `..` чи символьні посилання заборонено. Порожній список (типово) — `file://` відхиляється.
- `download_url` — лише до хостів `JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST`, без переадресацій. Порожній список (типово) — завантаження відхиляються.
- `s3://` без `download_url` не читається: сервіс не має облікових даних сховищ.

Розмір і `sha256` з `ContentRef` перевіряються для кожного читання.

## Бібліотеки Python

Версії з [pyproject.toml](../../../services/handler-runtime/pyproject.toml); у дужках — версії з `uv.lock` ревізії `c59d26d`.

| Пакет | Вимога | Призначення |
|---|---|---|
| Python | `>=3.12` | інтерпретатор сервісу; образ сервісу — `python:3.12-slim` |
| `jane-kit` | workspace | HTTP-застосунок, автентифікація, ліміти, ідемпотентність, job, PostgreSQL-сховища — [jane-kit](../jane-kit/README.md) |
| `jane-extractor-sdk` | workspace | канонічний архів, матеріал із файлу, порівняння тестів, протокол раннера — [jane-extractor-sdk](../extractor-sdk/README.md) |
| `docker` | `>=7.1` (7.2.0) | клієнт Docker Engine API |
| `packaging` | `>=24.0` (26.3) | розбір PEP 508 залежностей маніфесту |
| `httpx` | `>=0.27` (0.28.1) | Registry і `download_url` |
| `jsonschema`, `referencing` | `>=4.23` (4.26.0), `>=0.35` | перевірка за схемами |
| `psycopg[binary,pool]` | `>=3.2` (3.3.6) | PostgreSQL |

## Поведінка за недоступності

| Що недоступне | Поведінка |
|---|---|
| Docker Engine | `GET /v1/health` — `sandbox: down`, HTTP 503; виклик — 503 `service_unavailable` з `Retry-After` (`packages.unavailable_retry_after_seconds`); CLI — код виходу 2 |
| Образ профілю | 503 `service_unavailable`: `sandbox image '<тег>' not found; build it: jane-handler-runtime build-image` |
| Профіль не налаштовано | 422 `dependency_not_allowed` з переліком доступних профілів |
| Registry не відповідає або 5xx | 502 `upstream_unavailable` (retryable); версії немає — 404 `not_found` |
| Registry не налаштовано, `package_archive` немає | 422 `validation_failed` |
| PostgreSQL | сервіс не стартує (міграція під час запуску); у роботі — `state: down` у health і помилки запитів |
| Каталог `file://` або хост `download_url` | 422 `validation_failed`, якщо не дозволено; 404, якщо файлу немає; 502 за помилки читання чи тайм-ауту |

Помилки до запуску пісочниці повертаються як HTTP-помилка у форматі problem+json ([модель помилок](../../../contracts/docs/errors.md)). Після запуску будь-яка проблема коду пакета — це `HandlerResult` зі `status: failed` ([internals.md](internals.md#класифікація-результату)).
