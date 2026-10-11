# Storage: будова

Будова сервісу, алгоритм запису, формати й гарантії. Протокол між ядром і адаптерами нормативно описано в [storage-adapter.md](../../../contracts/docs/storage-adapter.md) і [storage_adapter.py](../../../contracts/python/src/jane_contracts/storage_adapter.py); тут — як його використовує ядро.

## Зміст

- [Компоненти коду](#компоненти-коду)
- [Поділ ядро — адаптер](#поділ-ядро--адаптер)
- [Алгоритм запису сутності](#алгоритм-запису-сутності)
- [Злиття й порядок спостережень](#злиття-й-порядок-спостережень)
- [Об'єкти й ключі](#обєкти-й-ключі)
- [Дедуплікація доставок](#дедуплікація-доставок)
- [Вміст за посиланням](#вміст-за-посиланням)
- [Підключення й адаптери](#підключення-й-адаптери)
- [Пакети збереження](#пакети-збереження)
- [Стан сервісу](#стан-сервісу)
- [Гарантії](#гарантії)

## Компоненти коду

Пакет `jane_storage` ([services/storage/src/jane_storage](../../../services/storage/src/jane_storage/)):

| Модуль | Призначення |
|---|---|
| `app.py` | FastAPI-застосунок: `handler.v1`, `storage.v1`, підключення, job, метрики |
| `handler.py` | `StorageHandler`: вибір пакета, перевірка запиту (`prepare`), виконання входів (`execute`), `HandlerResult` |
| `engine.py` | `StorageEngine`: дедуплікація, злиття, коміт сутності з повтором `CONFLICT`, запис об'єкта |
| `merge.py` | `merge` — чиста функція злиття `EntityRecord` у знімок; `validate_record` |
| `keys.py` | Канонічний ключ, ключ об'єкта, `object_id`, ключі доставки частин |
| `formats.py` | Формат RAW (`auto`, `original`, `html`, `json`), побудова `RawObject` і документів `data` |
| `codec.py` | JSON-кодування знімків, подій, доставок і `WriteAck` (`entity_ack`) — однакове для всіх адаптерів |
| `content.py` | `ContentReader`: `inline`, `file:///`, `s3://`, `download_url` з перевіркою розміру й SHA-256 |
| `connections.py` | `ConnectionRegistry` (описи, розв'язання секретів) і `AdapterPool` (відкриті адаптери) |
| `policy.py` | Політика `secret_refs` і allowlist мережевих адрес підключень |
| `adapters.py` | Пошук адаптерів і пакетів за entry points |
| `packages.py` | Пакети збереження: каталог, канонічний архів, CLI `jane-storage-packages` |
| `registry_packages.py` | Завантаження й перевірка пакетів із Registry, кеш за digest |
| `compat/` | Набір сумісності C-01…C-16 для пакетів адаптерів |
| `settings.py` | Параметри процесу й ліміти |

## Поділ ядро — адаптер

| Ядро | Адаптер |
|---|---|
| Перевірка `HandlerInvocation`, пакета й параметрів | Підключення за `ResolvedConnection` (секрети вже розв'язані) |
| Розв'язання `secret_refs`, політика хостів | `ensure_schema`: таблиці, колекції, бакет, каталоги |
| Канонічний ключ, ключі об'єктів і доставок | Атомарний `commit_entity`: унікальність доставки + CAS версії + подія історії |
| Злиття, `cleared`, порядок, `stale_fields` | Ідемпотентний `put_object` за `object_key` |
| Формат RAW | Зберігання байтів як є |
| Повтор `CONFLICT` | Класифікація помилок: `AdapterError(retryable=…)` |
| `test_mode` без звернення до адаптера | — |
| Читання `storage.v1`, перевірка підтримки за наявністю методів | Необов'язково: каталог типів і пошук (`EntityDiscoveryAdapter`), статистика (`StorageStatisticsAdapter`) — є у `filesystem`, `postgresql`, `mongodb` |

Адаптер не знає семантики злиття. Завдяки цьому всі шість сховищ поводяться однаково, а набір сумісності перевіряє адаптер разом зі справжнім ядром.

## Алгоритм запису сутності

![Запис сутності: дедуплікація, злиття, повтор CONFLICT і повторна доставка](../../diagrams/storage/write-sequence.light.png#gh-light-mode-only)
![Запис сутності: дедуплікація, злиття, повтор CONFLICT і повторна доставка](../../diagrams/storage/write-sequence.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/storage/write-sequence.light.png), [темне](../../diagrams/storage/write-sequence.dark.png); джерело — [write-sequence.drawio](../../diagrams/storage/write-sequence.drawio).

Для кожного `EntityRecord` із ключем доставки `<delivery_key>#<n>` ([engine.py](../../../services/storage/src/jane_storage/engine.py)):

1. `get_delivery` — запис доставки вже є → повернути збережене підтвердження зі `status: duplicate`.
2. `read_entity` → поточний знімок або нічого.
3. `merge` → новий знімок із `version + 1`, переліки `applied` і `stale`.
4. `commit_entity(new, expected_version, event)` атомарно перевіряє доставку й версію та додає подію історії.
5. `CONFLICT` (інший запис змінив версію) → пауза за `limits.conflict_retries` і повтор із кроку 2; `DUPLICATE` → як у кроці 1; `COMMITTED` → `WriteAck` зі статусом `written`, `partially_stale` або `stale`.
6. Вичерпані спроби → `AdapterError(retryable=True)` → `HandlerResult.failed` з `connection_error`; Orchestrator повторить виклик тим самим ключем.

Пауза між спробами: `min(initial_backoff_ms × multiplier^(n−1), max_backoff_ms)`, із `jitter` — помножена на випадкове число від 0 до 1.

Входи одного виклику обробляються по черзі в порядку `inputs`; виконані записи не відкочуються, якщо пізніший вхід не вдався.

## Злиття й порядок спостережень

`merge` ([merge.py](../../../services/storage/src/jane_storage/merge.py)) — чиста функція без вводу-виводу:

1. Поле з `fields` встановлює значення.
2. Поле, якого немає ні в `fields`, ні в `cleared`, не змінюється.
3. Поле з `cleared` видаляється з `fields` і додається в `cleared_fields`; нове значення знімає його з `cleared_fields`.
4. Кожне поле, також очищене, пам'ятає порядок свого останнього зміненого спостереження (`field_orders`). Оновлення застосовується, лише якщо порядок запису **строго новіший**; інакше поле потрапляє в `stale`.
5. Новий знімок завжди має `version + 1`, навіть коли всі поля застарілі: так історія зберігає й запізнілі спостереження.

Порядок — кортеж `(observed_at, sequence або −1, observation_id)` (`order_tuple` протоколу). Порядок визначається окремо для кожного поля: запис може оновити `price` і бути запізнілим для `title`.

Знімок сутності (`EntityState` у `storage.v1`): `entity_type`, `canonical_key`, `key`, `fields`, `field_orders`, `cleared_fields`, `version`, `updated_at`. Подія історії: повний `record`, `received_at`, `delivery_key`, `applied_fields`, `stale_fields`.

## Об'єкти й ключі

| Ключ | Як утворюється | Приклад |
|---|---|---|
| Канонічний ключ сутності | `scope + "\|" + JSON(natural)` із сортованими ключами, без пробілів, Unicode без екранування | `shop-example\|{"sku":"A-100"}` |
| Ключ RAW-об'єкта | `<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<розширення>`; дата — `fetched_at` в UTC; символи поза `[A-Za-z0-9._-]` → `_` | `shop-example/2026/10/11/web_quickstart-a-100/obs_quickstart_0001.html` |
| Без `source.source_id` | Сегмент `_standalone` | `_standalone/2026/…` |
| Документ `writes: data` | `data/<source_id>/data_<sha256(delivery_key)[:32]>/part<n>.json` | — |
| `object_id` | `obj_` + перші 32 символи SHA-256 ключа об'єкта — однаковий у всіх адаптерах | `obj_358c44b3866e4b33bd68301a1b96b90e` |

Ключі безпечні для імен файлів на Windows і Linux: зарезервовані імена (`con`, `nul`, `com1`…) отримують префікс `_`.

`put_object` ідемпотентний за ключем: той самий ключ і SHA-256 → наявний запис; той самий ключ з іншим SHA-256 → `AdapterError(retryable=False)`. Тому повторне отримання сторінки з новим `observation_id` — новий об'єкт, а повторна технічна доставка — той самий.

## Дедуплікація доставок

Записи доставки (`DeliveryRecord`) адаптер зберігає разом із даними й **безстроково**. Для сутності запис доставки, знімок і подія історії комітяться атомарно; для об'єкта — `put_object`, потім `record_delivery` (вставка, якщо ключа немає). У `acks` лежить документ підтвердження без `status` і `target`; на повтор ядро додає `status: duplicate` і поточну ціль.

Окремо від цього кожен екземпляр тримає в пам'яті ключі `Idempotency-Key` (`idempotency.idempotency_ttl_seconds`): вони лише відхиляють той самий ключ з іншим тілом (`422`) і паралельний дубль (`409`). Повторний виклик після завершення виконується знову й отримує збережені підтвердження адаптера — тому дедуплікація працює між екземплярами й після перезапуску. Відбиток тіла не враховує `context` (номер спроби, трасування).

## Вміст за посиланням

`ContentReader` ([content.py](../../../services/storage/src/jane_storage/content.py)) читає `ContentRef` входу:

| Вид | Звідки | Умова |
|---|---|---|
| `inline` | Поле `data` (`utf-8` або `base64`) | — |
| `blob` `file:///…` | Локальний файл | Лише всередині `JANE_STORAGE_CONTENT_FILES_DIR` або власного транзитного каталогу; шлях розв'язується, вихід за межі заборонено |
| `blob` `s3://бакет/ключ` | Транзитне підключення | `JANE_STORAGE_TRANSIT_CONNECTION_ID` типу `s3`/`minio` |
| `blob` з `download_url` | HTTP(S) | Хост у `JANE_STORAGE_DOWNLOAD_HOST_ALLOWLIST`; без переадресацій і проксі з оточення |

Розмір перевіряється до й під час читання (`objects.max_object_bytes`), потім звіряються `sha256` і `size_bytes`, якщо їх указано. Протилежний напрям — видача великого RAW без постійного URI — пише власний транзитний blob у `<JANE_STORAGE_TRANSIT_DIR>/storage/` з іменем за вмістом; фонове завдання видаляє прострочені blob кожні `transfer.transit_cleanup_interval_seconds`.

## Підключення й адаптери

![Ядро Storage, API запису й читання, адаптери та зовнішні залежності](../../diagrams/storage/components.light.png#gh-light-mode-only)
![Ядро Storage, API запису й читання, адаптери та зовнішні залежності](../../diagrams/storage/components.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/storage/components.light.png), [темне](../../diagrams/storage/components.dark.png); джерело — [components.drawio](../../diagrams/storage/components.drawio).

- `ConnectionRegistry` тримає описи підключень у пам'яті (з файлу й `PUT`), ETag кожного опису — SHA-256 документа. Секрети розв'язуються лише під час відкриття адаптера.
- `AdapterPool` тримає один відкритий адаптер на ключ `(підключення, ETag, опції)`. Опції — параметри `adapters.*` сервісу плюс простір етапу (`prefix`, `schema`, `table_prefix`) і `entities_format`. `ensure_schema` викликається один раз на ключ.
- Виклик тримає адаптер «в оренді» до кінця: змінене або видалене підключення виводить старий адаптер з обігу, але закриває його лише після завершення робіт на ньому.
- Адаптер знаходиться за `kind` в entry point `jane.storage.adapters`; клас має `kind`, що дорівнює імені entry point, і `capabilities == {"objects", "entities", "history"}`, інакше сервіс не стартує.

## Пакети збереження

Джерело пакета для виклику, у порядку ([handler.py](../../../services/storage/src/jane_storage/handler.py)):

1. `package_archive` запиту — недовірений ZIP, читається в межах `packages.*`, без символьних посилань і небезпечних шляхів.
2. Вбудований каталог: пакети встановлених адаптерів і `JANE_STORAGE_PACKAGE_DIRS`. Для вбудованого `package_id@version` інший `digest` у запиті — `digest_mismatch` без звернення до Registry.
3. Registry (`GET /v1/packages/{id}/versions/{v}/archive`), якщо задано `JANE_STORAGE_REGISTRY_URL`. Завантаження без переадресацій, з перевіркою `ETag`, digest і вмісту; кеш у пам'яті за digest (LRU), паралельні запити однієї версії ділять одне завантаження.

Пакет не з вбудованих може посилатися лише на встановлений адаптер. Digest пакета — SHA-256 канонічного ZIP його файлів (сортовані шляхи, фіксований час, без стиснення) — той самий алгоритм, що в Registry. Маніфест: `kind: storage`, `entry.executor: storage`, `entry.adapter`, `entry.writes` (`raw`, `entities`, `raw_and_entities`, `data`), `entry.history` лише `true`, жодних `dependencies`.

## Стан сервісу

Власної бази Storage не має. Бізнес-дані лежать у цільових сховищах (структура — [адаптери](adapters.md)), а сервіс тримає лише службовий стан:

| Стан | Де | Після перезапуску |
|---|---|---|
| Підключення з `PUT` | Пам'ять | Втрачаються; підключення з файлу читаються знову |
| Відкриті адаптери, пули з'єднань | Пам'ять | Відкриваються на першому виклику |
| Ключі `Idempotency-Key` | Пам'ять | Втрачаються; дедуплікацію забезпечують записи доставок у сховищі |
| Job і результати `GET /v1/invocations/{id}` | Пам'ять | Втрачаються |
| Кеш пакетів Registry | Пам'ять | Завантажуються знову |
| Власні транзитні blob | `JANE_STORAGE_TRANSIT_DIR/storage/` | Лишаються до `transit_ttl_seconds` |

## Гарантії

- **Повторна доставка без дублів.** Той самий `delivery_key` (і ключ частини) не створює другого запису ні в стані, ні в історії, ні серед об'єктів — також після перезапуску й на іншому екземплярі.
- **Атомарність коміту сутності.** Знімок, подія історії й запис доставки з'являються разом або не з'являються. Як це досягнуто в кожному сховищі — [адаптери](adapters.md).
- **Запізніле не перезаписує новіше.** Старіше значення поля потрапляє лише в історію зі `stale_fields`.
- **Пропуск не є видаленням.** Видалення — лише через `cleared`.
- **Однакова поведінка адаптерів.** Сценарії C-01…C-16 обов'язкові для всіх шести адаптерів.
- **Порядок списку сутностей не гарантується між адаптерами** (files, postgresql і mongodb — за `canonical_key`, sqlserver — за хешем ключа, minio і s3 — за ключем об'єкта); курсор не переноситься між адаптерами.
- **Без гарантії** транзакційності між входами одного виклику: виконані записи лишаються, повтор їх пропускає.
