# Відтворювані приклади Jane: каталог, перевірка цін, події з Telegram

Приклади WP-14 до критерію 5 ТЗ §12 («окремі завдання повного збору товарів і періодичної перевірки
цін») і до сценарію «події з Telegram». Усе потрібне лежить у цьому каталозі: пакети, їхні тести,
документи джерел і завдань, закріплені фактичні дайджести та скрипт, що проходить увесь шлях через
публічні API сервісів. Зовнішні сайти, LLM і реальний Telegram не потрібні.

| Позначка | Значення |
|---|---|
| **Р** | реальний компонент Jane (registry, orchestrator, web-collector, handler-runtime, storage, telegram-collector) |
| **З** | замінник зовнішньої системи: testsite замість інтернет-магазину, записаний backend Telegram |

## Що в каталозі

| Шлях | Що це |
|---|---|
| [`packages/examples.testsite-web-rules`](packages/examples.testsite-web-rules) | правила Web Collector (`collector-rules`): категорії testsite з пагінацією → картки товарів; хост `testsite:8080` compose-мережі |
| [`packages/examples.testsite-catalog-extractor`](packages/examples.testsite-catalog-extractor) | екстрактор **повної картки** товару: `sku`, `title`, `price`, `availability`, `category`, `url`, `completeness: full`; 6 тестів маніфесту |
| [`packages/examples.testsite-price-extractor`](packages/examples.testsite-price-extractor) | екстрактор **лише ціни й наявності**: `sku`, `price`, `availability`, `completeness: partial`; 4 тести |
| [`packages/examples.telegram-rules`](packages/examples.telegram-rules), [`packages/examples.telegram-event-extractor`](packages/examples.telegram-event-extractor) | правила каналу й екстрактор подій із рядків «Подія: назва \| дата [час] \| місце» (без LLM) |
| [`packages.lock.json`](packages.lock.json) | версії й **фактичні** дайджести всіх п'яти пакетів прикладів і двох пакетів збереження |
| [`documents/`](documents) | `connections.json`, джерела `source.*.json`, завдання `task.testsite-catalog.json`, `task.testsite-price-check.json`, `task.telegram-events.json` — валідні проти `contracts/schemas`, закріплені на дайджести з lock |
| [`telegram/recordings/`](telegram/recordings) | записаний канал `jane_events_example` (3 повідомлення) для backend `recorded` (**З**) |
| [`telegram/connection.telegram-account.json`](telegram/connection.telegram-account.json) | шаблон підключення для реального Telegram (лише `secret_refs`) |
| [`jane_examples.py`](jane_examples.py) | перевірка без сервісів, перерахунок дайджестів і прогін проти стеку |
| [`tests/`](tests) | тести прикладів без Docker |

Дайджест — `sha256` **канонічного архіву registry** (`jane_registry.archive`: zip без стиснення,
відсортовані шляхи, фіксовані час і права; той самий алгоритм у `jane-registry archive <тека>`).
Маніфести записані в канонічній JSON-формі, тож публікація zip-архівом і JSON-тілом дає той самий
дайджест. SDK `build_archive` зараз стискає deflate і дає **інший** дайджест (відкритий запит WP-05 → WP-06),
тому для завдань він не підходить.

Два завдання мають одне джерело `testsite-shop`, отже й один `key.scope` сутностей: перевірка цін оновлює
ті самі товари, що зібрав каталог. Каталог (`testsite-catalog`) — категорії → RAW усіх сторінок у files,
повні картки в PostgreSQL, розклад cron щонеділі о 03:00 (Europe/Kyiv). Перевірка цін
(`testsite-price-check`) — лише 4 задані URL, лише ціна й наявність, окремий розклад (`interval`, 1 год),
без повторного обходу каталогу.

## Перевірка без сервісів

```text
uv sync --all-packages
uv run --all-packages python examples/jane_examples.py check
uv run --all-packages pytest examples -q          # входить і в just unit / just check
```

`check` звіряє маніфести й правила зі схемами контрактів, проганяє тести пакетів у процесі, перераховує
дайджести й перевіряє, що кожен документ закріплений на версію й дайджест із lock. Після зміни пакета:
`jane_examples.py lock` (оновлює lock і документи), для сторінок testsite — `jane_examples.py snapshot`.
Остаточна перевірка пакета в пісочниці без інших сервісів — CLI runtime:
`uv run --package jane-handler-runtime jane-handler-runtime test examples/packages/<пакет>` (потрібен образ
`jane-handler-runtime build-image`).

## Відтворення з чистого checkout

Потрібні Docker (Compose v2) і `uv`; Windows і Linux однаково. Стек ізольований: власна назва
compose-проєкту, порти обирає Docker (лише `127.0.0.1`), паролі генеруються у `.jane/stack-<проєкт>.json`.
Сервіси працюють у `AUTH_MODE=api_key` (ADR-0005): там же генеруються ключі API, і драйвер звертається до
registry, orchestrator і storage з ключем оператора `JANE_API_KEY_ADMIN` цього стеку.

```text
uv sync --all-packages
uv run --all-packages python deploy/profiles/stack.py up --project jane-examples --profile dev-laptop --telegram
uv run --all-packages python examples/jane_examples.py demo --project jane-examples
uv run --all-packages python examples/jane_examples.py telegram --project jane-examples
uv run --all-packages python deploy/profiles/stack.py down --project jane-examples
```

1. `stack.py up` — `infra/compose.yaml` (WP-01) + [`deploy/profiles/compose.stack.yaml`](../deploy/profiles/compose.stack.yaml):
   testsite, registry (PostgreSQL + MinIO), storage, handler-runtime (образ пісочниці
   `<проєкт>-python-extractor:1`), web-collector, orchestrator і з `--telegram` telegram-collector на
   записаному backend. Профіль лімітів `dev-laptop` отримують як `LIMITS_FILE` усі сервіси стеку (див.
   [профілі](../deploy/profiles/README.md)). Перший запуск збирає образи (кілька хвилин).
2. `demo`:
   - **publish** — створює пакети в registry, публікує канонічні архіви (`application/zip`), перевіряє
     `digest` відповіді й завантаженого архіву проти lock, переводить версії в `approved`;
   - **apply** — `PUT /v1/connections/{id}` (RAW `raw-files`, результати `results-pg`), `POST /v1/sources`,
     `POST /v1/task-validations` і `POST /v1/tasks` для каталогу;
   - **catalog** — `POST /v1/tasks/testsite-catalog/runs`, очікування `GET /v1/runs/{id}`;
   - **price-check** — створює завдання перевірки цін із `schedule.start_at` = зараз + 15 с (каденція з
     документа не змінюється) і чекає на запуск із `trigger: schedule`, тобто перевіряє саме розклад;
   - **verify** — через `storage.v1`: 23 RAW-сторінки каталогу, 16 повних карток, для кожного з 4 товарів
     перевірки цін — один запис історії з `completeness: partial` лише з `sku`, `price`, `availability`
     від пакета `examples.testsite-price-extractor`; `applied_fields` підтверджує застосування `price` та
     `availability`, а `title`, `category`, `url` лишаються. Якщо є необов'язкове `field_orders`, воно
     додатково показує, що `price` оновлено спостереженням перевірки, а `title` — ні. Також `GET /v1/limits/effective`:
     частота з рівня `source`, `crawl.max_pages_per_run` з рівня `task`; розклад каталогу не змінився.
3. `telegram` — джерело й завдання подій, запуск 1 читає історію (3 повідомлення → 2 події), потім скрипт
   редагує повідомлення 1 і додає повідомлення 4 у копії запису (`.jane/telegram-recordings-<проєкт>/`),
   запуск 2 (`mode: incremental`) бачить рівно 2 нові спостереження; подія з повідомлення 1 оновлюється
   (версія 2, два записи історії), а не дублюється.
4. `stack.py down` прибирає контейнери, томи, мережу, зібрані образи, образ пісочниці, файл стеку й копію
   запису; друкує `leftovers` і завершується з кодом 1, якщо щось лишилося.

Підсумок кожного кроку — `.jane/examples-<проєкт>.json` (без секретів). Очікуваний вивід `verify`:
`"ok": true`, `"raw_objects": 23`, `"entities": 16`, `"platform_profile": "dev-laptop"`.

Що у виводі очікувано і не є помилкою:

- Час у рядках журналу скрипта (`[12:34:56Z] …`) — UTC, як і мітки часу API.
- `telegram` спершу повторює `publish` і `apply` (вони ідемпотентні). Після `demo` registry відповідає 409 на вже
  створені пакети й версії (у підсумку `"package": "existed"`, `"version_publish": 409`), а оркестратор —
  `orchestrator: source testsite-shop -> 409` і `task testsite-catalog -> 409` (при повторному `telegram` на тому
  самому стеку — також для джерела й завдання `telegram-events`).
- Лічильники запуску каталогу (`catalog.counters` у підсумку, `GET /v1/runs/{id}`): `materials: 23`,
  `unknown_materials: 7`. Ці 7 — сторінки категорій із пагінацією (`/catalog/<категорія>/`, `?page=2`, `?page=3`):
  їх збережено як RAW, але екстрактор прив'язано лише до `*/product/*`, а передача невідомих сторінок у LLM вимкнена
  (`forward_unknown_to_llm: false`). 23 = 16 карток + 7 категорій.
- `stack.py down` файл підсумку **не видаляє** (`leftovers` його не рахує): `.jane/examples-<проєкт>.json`
  лишається для звіту. Окремий `verify` бере з нього запуски `catalog` і `price-check`, тож перед новим стеком
  з тим самим ім'ям проєкту видаліть файл або запускайте `demo` повністю.

Кроки можна запускати окремо (`publish`, `apply`, `catalog`, `price-check`, `verify`) і на стеку, піднятому
інакше, якщо він має той самий ланцюжок і файл `.jane/stack-<проєкт>.json` з адресами
(`services.<name>.url`). Документи використовують адреси compose-мережі (`http://testsite:8080`).

## Реальний Telegram (не перевірено на реальному сервісі)

Записаний backend — замінник Telegram (**З**). Для реального каналу доступ надає людина змінними середовища;
секретів у файлах і Git немає.

1. Тестовий обліковий запис і `StringSession` Telethon створюються поза Jane. Задайте в середовищі, з якого
   запускаєте стек: `JANE_SECRET_TG_API_HASH`, `JANE_SECRET_TG_SESSION`, а також
   `JANE_TELEGRAM_BACKEND=telethon` і `JANE_TELEGRAM_EXTRAS=--extra telethon` (образ колектора з Telethon;
   оркестратор тоді синхронізує підключення `telegram_account` з колектором).
2. `stack.py up ... --telegram` (оверлей передає ці змінні лише в telegram-collector).
3. Скопіюйте [`telegram/connection.telegram-account.json`](telegram/connection.telegram-account.json), задайте
   справжній `params.api_id` (не секрет) і виконайте `PUT /v1/connections/tg-main` в оркестраторі.
4. Опублікуйте нову версію правил (наприклад `examples.telegram-rules@1.1.0`) з вашим каналом у
   `channels[].username` і `"account_connection_id": "tg-main"`; у джерелі задайте цей `locator`,
   `collector_rules` з новим дайджестом і `"connections": {"account": "tg-main"}`. Секрети залишаються
   посиланнями `env:JANE_SECRET_*`; колектор приймає лише змінні з цим префіксом
   ([README telegram-collector](../services/telegram-collector/README.md#підключення-обліковий-запис)).
5. Далі `POST /v1/tasks/telegram-events/runs` так само, як у записаному сценарії. Обмеження flood-wait —
   `limits.telegram.max_flood_wait_seconds` профілю й джерела.

## Обмеження

- testsite детермінований: ціна на ньому не змінюється, тому приклад доводить часткове оновлення через
  історію й порядок полів (`field_orders`), а не через нове значення ціни. Керована зміна ціни на testsite —
  запит до власника testsite (WP-01) у звіті WP-14.
- Частоту джерела `testsite-shop` піднято до 2 запитів/с лише тому, що це локальний контрольований сайт.
  Для реального сайту беріть обмеження з його правил (`robots.txt`, домовленості); профілі WP-14 не дають
  дозволу на вищу частоту.
- LLM-етапи (аналіз проблем, невідомі сторінки) у прикладах вимкнені; LLM-шлях подій —
  `jane.llm-event-extractor` за LLM-шлюзом, тут не відтворюється.
