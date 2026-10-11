# Приклади Jane

Відтворювані приклади платформи: пакети обробників, документи джерел і завдань та сценарії, що виконують їх на запущеному стеку. Основний приклад — повний каталог товарів і окрема перевірка цін за розкладом на тестовому магазині (критерій 5 ТЗ §12). Покроковий запуск із реальним виводом — [наскрізний сценарій](../docs/getting-started/end-to-end.md).

## Зміст

- [Склад](#склад)
- [Пакети](#пакети)
- [Документи](#документи)
- [Команди `jane_examples.py`](#команди-jane_examplespy)
- [Сценарій Telegram](#сценарій-telegram)
- [Приклади з реальними джерелами](#приклади-з-реальними-джерелами)
- [Тести](#тести)

## Склад

| Шлях | Що містить |
|---|---|
| `jane_examples.py` | сценарій: офлайн-перевірки й виконання прикладів на стеку |
| `packages/` | пакети прикладів: правила колекторів і екстрактори |
| `packages.lock.json` | версії й дайджести канонічних архівів пакетів, зокрема `jane.storage-files` і `jane.storage-postgresql` |
| `documents/` | джерела, завдання й підключення для Orchestrator |
| `telegram/` | підключення облікового запису й записаний канал для бекенда `recorded` |
| `shops/` | ціни ноутбуків п'яти реальних магазинів — [shops/README.md](shops/README.md) |
| `channels/` | дописи публічних Telegram-каналів через реальний обліковий запис |
| `sites/` | скрипти декларативного опису реальних сайтів; самих описів сайтів у репозиторії поки немає |
| `tests/` | тести прикладів без сервісів |

## Пакети

| Пакет | Вид | Призначення |
|---|---|---|
| `examples.testsite-web-rules` | `collector-rules` | обхід тестового магазину: сторінки категорій із пагінацією (стратегія `listing`) |
| `examples.testsite-catalog-extractor` | `extractor` | повна картка товару: `sku`, `title`, `price`, `availability`, `category`, `url` |
| `examples.testsite-price-extractor` | `extractor` | лише `price` і `availability` як часткове оновлення (`completeness: partial`) |
| `examples.telegram-rules` | `collector-rules` | канал `jane_events_example`: історія, нові повідомлення, редагування |
| `examples.telegram-event-extractor` | `extractor` | події з повідомлень каналу |

Тестові сторінки екстракторів (`tests/<випадок>/page.html`) — рендер справжнього тестового сайту `tests/fixtures/testsite`. Формат пакетів — [довідник пакетів](../docs/reference/packages/README.md).

## Документи

| Файл | Що описує |
|---|---|
| `documents/connections.json` | підключення `raw-files` (файли на томі Storage) і `results-pg` (база `jane_storage_results`; облікові дані — `env:JANE_SECRET_DEV_PG_*`) |
| `documents/source.testsite-shop.json` | джерело `testsite-shop`: правила колектора й ліміт частоти джерела |
| `documents/task.testsite-catalog.json` | завдання `testsite-catalog`: збір → RAW у файли; сторінки `*/product/*` → екстрактор каталогу → PostgreSQL; розклад cron |
| `documents/task.testsite-price-check.json` | завдання `testsite-price-check`: 4 URL товарів → екстрактор цін → PostgreSQL; розклад щогодини |
| `documents/source.telegram-events.json`, `documents/task.telegram-events.json` | джерело й завдання Telegram-прикладу |

Посилання на пакети в документах зафіксовано версією й дайджестом із `packages.lock.json`. Документи не містять значень секретів. Як Orchestrator виконує такі завдання — [виконання завдання](../docs/architecture/task-execution.md).

## Команди `jane_examples.py`

Без сервісів:

| Команда | Дія |
|---|---|
| `check` | маніфести й тести пакетів, дайджести проти `packages.lock.json`, документи проти схем `contracts/` |
| `lock` | перераховує дайджести й записує їх у `packages.lock.json` і документи |
| `snapshot` | оновлює тестові сторінки екстракторів із тестового сайту |

```powershell
uv run --all-packages python examples/jane_examples.py check
```

```text
examples: ok
```

На запущеному стеку (`--project` — назва стеку з `deploy/profiles/stack.py up`):

| Команда | Дія |
|---|---|
| `demo` | `publish` → `apply` → `catalog` → `price-check` → `verify` |
| `publish` | публікує й погоджує пакети в Registry, звіряє дайджести |
| `apply` | створює підключення, джерело `testsite-shop` і завдання каталогу в Orchestrator |
| `catalog` | запускає завдання каталогу й чекає завершення |
| `price-check` | створює завдання перевірки цін і чекає його першого запуску за розкладом |
| `verify` | перевіряє RAW, картки товарів і часткові оновлення через API Storage й Orchestrator |
| `telegram` | `publish` → `apply` → два запуски Telegram-завдання |

Параметри онлайн-команд: `--timeout` — секунд на один запуск (типово 600), `--first-check-in` — секунд до першого запуску перевірки цін (типово 15). Підсумок записується в `.jane/examples-<project>.json`.

Стек для прикладів піднімає `deploy/profiles/stack.py`: звичайний `just up` без зв'язування сервісів не підходить — [платформа з Admin UI](../docs/getting-started/platform.md#звязування-сервісів).

```powershell
uv run --all-packages python deploy/profiles/stack.py up --project jane-examples
uv run --all-packages python examples/jane_examples.py demo --project jane-examples
```

Перевірений вивід і розбір результату — [наскрізний сценарій](../docs/getting-started/end-to-end.md#2-виконання-сценарію). Команда нижче видаляє стек разом з усіма даними, ключами й образами:

```powershell
uv run --all-packages python deploy/profiles/stack.py down --project jane-examples
```

## Сценарій Telegram

Команда `telegram` використовує бекенд `recorded` Telegram Collector — замінник Telegram, що відтворює записаний канал `telegram/recordings/jane_events_example.json`. Перший запуск читає історію (3 повідомлення); потім сценарій редагує повідомлення 1 і додає повідомлення 4 у записі, а другий запуск має побачити саме ці 2 спостереження. Редагування оновлює наявну подію, а не додає нову. Стек потрібен із Telegram Collector:

```powershell
uv run --all-packages python deploy/profiles/stack.py up --project jane-examples --telegram
uv run --all-packages python examples/jane_examples.py telegram --project jane-examples
```

Сценарій Telegram у цій документації не виконувався.

## Приклади з реальними джерелами

| Каталог | Що робить | Потребує |
|---|---|---|
| [shops](shops/README.md) | ціни ноутбуків Rozetka, Allo, Цитрус, Фокстрот, MOYO | стек зі зв'язуванням `infra/compose.local.yaml` |
| `channels/` | дописи публічних Telegram-каналів: історія, потім нові й відредаговані кожні 15 хвилин | Telethon-колектор і секрети облікового запису в `.jane/secrets` (`scripts/tg_session.py`) |

Скрипт `channels/setup_channels.py --project <p> --api-id <id> [канал …]` генерує пакет правил для кожного каналу в `channels/packages/`, публікує його разом із `channels.telegram-posts` і пакетами збереження, створює підключення `tg-main`, джерела й завдання та запускає кожне завдання один раз. Не перевірено в цій документації: потрібен реальний обліковий запис Telegram.

## Тести

Тести прикладів не потребують сервісів: перевіряють маніфести й тести пакетів, відповідність дайджестів, актуальність тестових сторінок, документи без секретів і узгодженість завдань. Вони входять у `just unit`.

```powershell
uv run --all-packages pytest examples/tests -q
```

Підсумок перевірочного запуску (2026-10-11, Windows 11):

```text
34 passed, 1 skipped in 34.27s
```

Пропущено тест `test_sites.py`: описів сайтів `examples/sites/*.json` у репозиторії ще немає.
