# Storage: адаптери

Шість початкових адаптерів Storage: параметри підключення, секрети, дані, які кожен створює, як досягається атомарність коміту, версії сервісів і обмеження. Усі адаптери мають `capabilities = {"objects", "entities", "history"}` і проходять однаковий набір сумісності C-01…C-16 ([новий адаптер](new-adapter.md)).

## Зміст

- [Огляд](#огляд)
- [Спільні параметри](#спільні-параметри)
- [filesystem](#filesystem)
- [postgresql](#postgresql)
- [sqlserver](#sqlserver)
- [mongodb](#mongodb)
- [s3](#s3)
- [minio](#minio)
- [Як перевірити адаптер](#як-перевірити-адаптер)

## Огляд

| `kind` | Пакет Python | Пакет збереження | Сховище в dev-стеку | Атомарність коміту | `locator` об'єкта |
|---|---|---|---|---|---|
| `filesystem` | `jane-storage-files` | `jane.storage-files` | Каталог | Файл-блокування на ключ + `os.replace` | `{"path"}` |
| `postgresql` | `jane-storage-postgres` | `jane.storage-postgresql` | PostgreSQL 18 | Одна транзакція | `{"table", "id"}` |
| `sqlserver` | `jane-storage-sqlserver` | `jane.storage-sqlserver` | SQL Server 2022 | Один пакет T-SQL у транзакції | `{"table", "id"}` |
| `mongodb` | `jane-storage-mongodb` | `jane.storage-mongodb` | MongoDB 8.0 | Намір у `_deliveries` + CAS одного документа + `pending` | `{"collection", "id"}` |
| `s3` | `jane-storage-s3` | `jane.storage-s3` | SeaweedFS 4.47 (замінник S3) | Умовні `PutObject` + `pending` | `{"bucket", "key"}` |
| `minio` | `jane-storage-minio` | `jane.storage-minio` | MinIO `RELEASE.2026-08-04` | Як `s3` | `{"bucket", "key"}` |

Образи — з [infra/compose.yaml](../../../infra/compose.yaml); драйвери й їхні версії — [залежності](dependencies.md#цільові-сховища). Постійний URI вмісту (`content_uri`) мають лише `filesystem` (`file:///`) і `s3`/`minio` (`s3://`); для баз даних великий RAW віддається через транзитний blob ([інтеграція](integration.md#читання-результатів)).

## Спільні параметри

- **Простір імен.** Параметр етапу (`prefix` або `schema` + `table_prefix`) перекриває однойменний `params` підключення; читання `storage.v1` бачить лише простір із `params` підключення.
- **Опції пулу й тайм-аутів** (`pool_*`, `*_timeout_ms`, `lock_*`) задаються групою `adapters.*` конфігурації сервісу, яка перекриває `params` підключення — [конфігурація](configuration.md#ліміти).
- **Секрети** — лише через `secret_refs`; імена секретів наведено в розділі кожного адаптера.
- **Мережеві адреси** мають бути в `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` — [політика](configuration.md#політика-секретів-і-хостів).
- **Записи доставок** зберігаються безстроково; адаптери їх не прибирають.

## filesystem

Зберігає все у файлах під `<base_path>/<prefix>`: RAW — як файли, сутності, історію й записи доставок — як JSON-документи. Код — [jane_storage_files](../../../services/storage/adapters/files/src/jane_storage_files/__init__.py).

| `params` | Обов'язковий | Значення |
|---|---|---|
| `base_path` | так | Каталог сховища; відносний шлях рахується від робочого каталогу сервісу |
| `prefix` | ні | Підкаталог усередині `base_path`; без `..`, абсолютних шляхів, `\` і `:` |

Секретів і мережевих адрес немає. Параметр етапу `format.entities: jsonl` веде історію одним файлом JSON Lines на сутність.

Структура каталогу:

| Шлях | Вміст |
|---|---|
| `entities/<entity_type>/<sha256(canonical_key)>.json` | Знімок сутності |
| `history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json` | Подія історії (`format.entities: json`) |
| `history/<entity_type>/<sha256(canonical_key)>.jsonl` | Події історії рядками (`format.entities: jsonl`) |
| `deliveries/<sha256(delivery_key)>.json` | Запис доставки |
| `objects/<object_key>` | Байти RAW або документа |
| `objects/<object_key>.meta.json` | Опис об'єкта й метадані `Material`; маркер завершеного запису |
| `index/objects/<object_id>.json` | `object_id` → `object_key` |
| `locks/…/<назва>.lock` | Тимчасові файли-блокування |

Атомарність: кожен документ пишеться в тимчасовий файл у тому самому каталозі з `fsync` і переноситься `os.replace` (на Windows — з повторами, поки файл тримає читач). `commit_entity` і `put_object` виконуються під файлом-блокуванням ключа (`O_CREAT | O_EXCL`); блокування, старше `lock_stale_ms`, вважається покинутим після збою й ламається. Порядок коміту — доставка, подія історії, знімок; запис доставки без підтвердженого знімка вважається незавершеним і виконується знову.

Обмеження: розрахований на один вузол або спільний каталог із коректними `O_EXCL` і `os.replace`; на мережевих файлових системах це не перевірялося. Вміст об'єкта читається в пам'ять цілком.

## postgresql

Таблиці в схемі `schema` (типово `public`) з префіксом `table_prefix` (типово `jane_`). Код — [jane_storage_postgres](../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py).

| `params` | Типово | Значення |
|---|---|---|
| `host`, `port` | `localhost`, `5432` | Сервер |
| `database` | — | База |
| `schema` | `public` | Схема; `^[a-z_][a-z0-9_]{0,62}$` |
| `table_prefix` | `jane_` | Префікс таблиць; `^[a-z_][a-z0-9_]{0,30}$` або порожній |
| `sslmode` | `prefer` | Режим TLS asyncpg; `disable` вимикає TLS |
| `layout` | не задано | Реляційна розкладка поверх таблиць рушія; підтримується лише `news` ([розкладка news](#розкладка-news)). Лише параметр підключення: з розкладкою етап не може перевизначити `schema` чи `table_prefix`. Невідоме значення — неповторювана помилка `open` |

Секрети: `username`, `password`. Користувачу потрібні права створити схему (якщо її немає) і таблиці або вже створені таблиці.

![Таблиці адаптера PostgreSQL: сутності, історія, доставки, об'єкти](../../diagrams/storage/postgres-er.light.png#gh-light-mode-only)
![Таблиці адаптера PostgreSQL: сутності, історія, доставки, об'єкти](../../diagrams/storage/postgres-er.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/storage/postgres-er.light.png), [темне](../../diagrams/storage/postgres-er.dark.png); джерело — [postgres-er.drawio](../../diagrams/storage/postgres-er.drawio).

| Таблиця | Ключ | Вміст |
|---|---|---|
| `<prefix>entities` | `(entity_type, canonical_key)` | Поточний стан: `scope`, `key`, `fields`, `field_orders`, `cleared_fields` (jsonb), `version`, `updated_at`; індекс `(entity_type, scope, canonical_key COLLATE "C")` |
| `<prefix>entity_history` | `(entity_type, canonical_key, version)` | Кожне прийняте оновлення, також запізніле: `record`, `delivery_key`, `received_at`, `applied_fields`, `stale_fields` |
| `<prefix>deliveries` | `delivery_key` | `recorded_at`, `acks` (jsonb) |
| `<prefix>objects` | `object_id`; унікальний `object_key` | Опис, `metadata` (jsonb) і байти в `content` (bytea); індекс `(stored_at, object_id)` |

Структуру перевірено на PostgreSQL 18 (`\d` після першого запису). Зовнішніх ключів немає: зв'язки логічні — `delivery_key` історії збігається з ключем запису доставки, `acks` містять сутність або об'єкт.

Атомарність: `commit_entity` — одна транзакція: `INSERT … ON CONFLICT DO NOTHING` у доставки (нічого не вставлено → `DUPLICATE`), CAS знімка (`UPDATE … WHERE version = $expected` або `INSERT … ON CONFLICT DO NOTHING` для нової сутності; нічого не змінено → `CONFLICT`) і вставка в історію. `ensure_schema` ідемпотентний і серіалізований advisory-блокуванням.

Помилки з'єднання, тайм-аути, `SerializationError`, `DeadlockDetectedError` — повторювані; помилки автентифікації — ні.

### Розкладка news

Параметр підключення `layout: "news"` вмикає реляційну проєкцію новин у тій самій схемі (дизайн — [news-pg.md](../../delivery/news-pg.md), код — [news_layout](../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/__init__.py)). Підключення `results-news` dev-стеку: схема `news`, `layout: "news"`, решта як у `results-pg` ([конфігурація](configuration.md#підключення)). Потрібен PostgreSQL 15 або новіший (`UNIQUE NULLS NOT DISTINCT`).

- **Джерело істини — таблиці рушія.** `<prefix>entities`, `<prefix>entity_history`, `<prefix>deliveries` і `<prefix>objects` працюють як без розкладки: злиття, CAS, доставки, `/v1/entities`, пошук і статистика їх не помічають. Реляційні таблиці — модель для SQL-споживачів; стан із них не відновлюється, бо перетворення типів втрачає оригінальний рядок (наприклад, `+03:00` у часі).
- **Коли пишеться.** Усередині транзакції `commit_entity`, після успішного CAS і вставки в історію, для типів `article`, `post`, `news_article`, `news_event`. `DUPLICATE` і `CONFLICT` проєкцію не змінюють. Будь-яка помилка проєкції відкочує весь коміт, тож проєкція завжди відповідає стану. Інші типи, наприклад `product`, пишуться лише в таблиці рушія.
- **Міграції.** Нумеровані міграції розкладки застосовує `ensure_schema` у своїй транзакції під тим самим advisory-блокуванням і додатковим блокуванням схеми; застосовані версії — у `<schema>.jane_layout_migrations (layout, version, applied_at)`. Схему з новішою версією, ніж знає адаптер, він відхиляє неповторюваною помилкою.
- **Імена таблиць** — без `table_prefix`: схема `news` окрема, а суфікси таблиць рушія (`entities`, `entity_history`, `deliveries`, `objects`) з назвами проєкції не збігаються за жодного префікса. Розкладка одна на схему: `layout` береться лише з підключення, а якщо етап перевизначає `schema` чи `table_prefix` підключення з розкладкою іншим значенням, `open` повертає неповторювану помилку. Інакше етап писав би в ту саму проєкцію з інших таблиць рушія, а перебудова з таблиць підключення втратила б ці сутності. Для іншого простору імен потрібне окреме підключення.

| Таблиця | Вміст |
|---|---|
| `source` | `source_id` (= `key.scope`) PK, `kind`, `name`, `site`, `channel`, `first_seen_at`, `last_seen_at` |
| `tag`, `topic` | `tag_id` / `topic_id` (identity), `name` UNIQUE |
| `named_entity` | `named_entity_id`, `canonical_name`, `entity_kind`; UNIQUE NULLS NOT DISTINCT `(canonical_name, entity_kind)` |
| `article` | `article_id`, `canonical_key` UNIQUE, `source_id` → `source`, `url`, `site`, `title`, `lead`, `body` (поле `text`), `author`, `section`, `language`, `image`, `published_at`, `modified_at`; UNIQUE `(source_id, url)` |
| `article_tag` | `(article_id, position)` PK, `tag_id` → `tag` |
| `post` | `post_id`, `canonical_key`, `source_id`, `channel`, `message_id`, `url`, `title`, `body`, `views`, `forwarded_from`, `has_media`, `edited`, `published_at`; UNIQUE `(source_id, channel, message_id)` |
| `post_link` | `(post_id, position)` PK, `url` |
| `news_event` | `news_event_id`, `canonical_key`, `scope`, `event_id`, `summary`, `identity_kind`, `grouping_method`, `identity_confidence`, `event_date`, `event_time`, `primary_actor`, `action`, `object`, `location`, `country`; UNIQUE `(scope, event_id)` |
| `news_article` | `news_article_id`, `canonical_key`, `source_id`, `url`, `material_id`, `content_sha256`, `headline`, `headline_ukrainian`, `summary`, `source_language`, `analysis_language`, `reporting_kind`, `region`, `transport`, `published_at`, `fetched_at`, `edited_at`, `evidence_validation`, `event_id` (без FK), `grouping_status`/`_method`/`_reason`, `sentiment_label`/`_confidence`/`_explanation`; UNIQUE `(source_id, url)` |
| `news_article_event` | 1:1 з `news_article`: що стаття каже про подію (`summary`, `identity_*`, `event_date`, `event_time`, `primary_actor`, `action`, `object`, `location`, `country`, `date_resolution_*`) |
| `news_article_topic`, `news_article_location` | `(news_article_id, position)` PK; `topic_id` → `topic` / `name` |
| `news_article_mention` | `mention_id`, `news_article_id`, `position` (UNIQUE разом), `named_entity_id` → `named_entity`, `name`, `role`, `attitude`, `attitude_confidence`, `factual_impact` |
| `evidence` | `evidence_id`, `news_article_id`, `subject` (`event` / `event_time` / `sentiment` / `mention`), `mention_id` (для `mention`), `position`, `quote`, `reason`, `attribution` |

Кожна таблиця сутності має також `version`, `updated_at` і `extra jsonb`. Дочірні таблиці посилаються на батьківську з `ON DELETE CASCADE`. Індекси: `published_at`, `(source_id, published_at)`, `url` у таблицях сутностей; `event_id` у `news_article` і `news_event`; `event_date`; зовнішні ключі дочірніх таблиць; `post_link.url`, `news_article_location.name`. Пошук за `named_entity.canonical_name` обслуговує унікальний індекс, де ця колонка перша. Подання: `news_article_with_event` (`news_article` LEFT JOIN `news_event` за `event_id`, колонки події з префіксом `event_`) і `article_analysis` (`article` JOIN `news_article` за `url`).

Правила проєкції:

- батьківський рядок — upsert за `canonical_key` (сурогатний id не змінюється); дочірні рядки щоразу видаляються й вставляються заново;
- довідники — `INSERT … ON CONFLICT DO NOTHING` у сталому порядку й пошук id; без гонок під READ COMMITTED і без блокування рядка довідника до кінця транзакції;
- `source` створюється до батьківського рядка, а оновлюється останнім кроком. Атрибути (`article` дає `kind=web` і `site`, `post` — `kind=telegram` і `channel`, `news_article` — `source_kind` і `source_name`) задає найновіший за `updated_at` знімок: знімок, не старший за `last_seen_at`, перезаписує ті атрибути, що має, а старіший лише заповнює порожні. `NULL` не затирає збережене значення. `first_seen_at`/`last_seen_at` лише розширюються за `updated_at` знімка. Вирази читають заблокований рядок, тож коміти, що завершилися не в порядку годинника, дають той самий результат;
- поле, якого немає у знімку (також очищене), дає `NULL`;
- невідоме поле (на верхньому рівні чи всередині відомого об'єкта) і значення, що не лягає в тип колонки (число в текстовій колонці, нерозбірний час), потрапляють в `extra` за шляхом поля: `published_at`, `event.canonical.foo`, `tags[2]`, `entities[0].evidence[1].page`; колонка тоді `NULL`. Елемент списку, що не дає рядка, теж іде в `extra`, а `position` решти — початковий індекс;
- час — строгий RFC 3339 зі зсувом → `timestamptz` (понад 6 знаків дробу — лише нулі); `event_date` → `date`; `event_time` (`HH:MM` або `HH:MM:SS`) → `time`.

Перебудова очищає проєкцію (`TRUNCATE … RESTART IDENTITY`) і заново розкладає всі знімки чотирьох типів з `<prefix>entities` в одній транзакції, курсором у порядку `(updated_at, entity_type, canonical_key)`, тобто в тому порядку, в якому жива проєкція бачила їх востаннє. `first_seen_at`/`last_seen_at` доповнюються з історії (`received_at` версії дорівнює `updated_at` її знімка). Одночасні коміти чекають на таблицях проєкції й після перебудови розкладають свої новіші знімки.

Результат збігається з живою проєкцією тих самих записів, крім трьох відмінностей:

- сурогатні id нові;
- рядки довідників, на які ніщо не посилається, зникають;
- атрибут `source` (`name`, `kind`, `site`, `channel`), який мала лише попередня версія якоїсь сутності, а її поточний знімок цього поля вже не має (очищене або не того типу), наживо зберігає старе значення. Після перебудови він береться з найновішого поточного знімка, що його має, або стає `NULL`: перебудова бачить лише поточні знімки.

Запуск:

```powershell
$env:PGPASSWORD = "<пароль>"   # або --password-env <ЗМІННА>; у командному рядку пароля немає
uv run python -m jane_storage_postgres.news_layout rebuild --host <host> --port 5432 --database jane_storage_results --user <user> --schema news
```

Інші параметри: `--table-prefix` (типово `jane_`), `--sslmode` (типово `prefer` або `PGSSLMODE`), `--batch-size` (знімків за запит, типово 500), `--command-timeout-ms`. Без аргументів беруться `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`. Результат — JSON із кількістю знімків за типами. З коду: `PostgresAdapter.rebuild_layout()` або `news_layout.rebuild(con, schema=…, table_prefix=…)`.

## sqlserver

Таблиці в схемі `schema` (типово `dbo`) з префіксом `table_prefix` (типово `jane_`), драйвер pymssql (FreeTDS у wheel для Windows і Linux). Код — [jane_storage_sqlserver](../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py).

| `params` | Типово | Значення |
|---|---|---|
| `host`, `port` | `localhost`, `1433` | Сервер |
| `database` | — (обов'язковий) | База; `^[A-Za-z0-9_-]{1,128}$` |
| `schema`, `table_prefix` | `dbo`, `jane_` | Простір імен |
| `encryption` | не задано | FreeTDS: `off`, `request`, `require` |
| `tds_version` | `7.4` | Версія протоколу TDS |

Секрети: `username`, `password`.

| Таблиця | Ключ | Вміст |
|---|---|---|
| `<prefix>entities` | `(entity_type, key_hash)` | `scope_hash`, `canonical_key`, `version`, `updated_at`, `doc` — знімок JSON (`nvarchar(max)`) |
| `<prefix>entity_history` | `(entity_type, key_hash, version)` | `delivery_key`, `doc` — подія історії JSON |
| `<prefix>deliveries` | `delivery_hash` | `delivery_key`, `recorded_at`, `doc` — запис доставки JSON |
| `<prefix>objects` | `object_id` | `object_key`, `stored_at`, `source_hash`, `material_hash`, `sha256`, `size_bytes`, `meta` (JSON), `content` (`varbinary(max)`) |

Ключі не мають обмеження довжини, а ключ індексу SQL Server — 900/1700 байт, тому індекси побудовано на SHA-256 (`key_hash`, `delivery_hash`). Час зберігається рядком RFC 3339 UTC фіксованої ширини (`char(27)`), щоб сортування було хронологічним на будь-якій версії TDS.

Атомарність: `commit_entity` — один пакет T-SQL з `XACT_ABORT ON`: вставка доставки (дубль ключа → `DUPLICATE`), CAS знімка (`UPDATE … WHERE version = @expected` або `INSERT`; нічого не змінено чи дубль → `CONFLICT`) і вставка історії. Жертва взаємоблокування (1205) повертається як `CONFLICT`: нічого не записано, ядро повторює. `ensure_schema` серіалізовано `sp_getapplock` з межею `lock_timeout_ms`.

Неповторювані помилки: 18456 (вхід), 4060 (база), 229 і 262 (права), 208 (немає об'єкта).

## mongodb

Окрема колекція на кожен тип сутності, історія — поруч, службові колекції — окремо; база — `database` (типово `jane`), префікс `prefix` типово порожній. Реплікасет не потрібен: адаптер не використовує багатодокументних транзакцій. Код — [jane_storage_mongodb](../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py).

Пакет збереження — `jane.storage-mongodb@2.0.0`. Розкладку 1.x (`jane_entities`, `jane_entity_history`, `jane_deliveries`, …) версія 2 не читає й не переносить.

| `params` | Типово | Значення |
|---|---|---|
| `host` | `localhost` | `hostname[:port]` або рядок `mongodb://…` / `mongodb+srv://…` |
| `port` | `27017` | Порт |
| `database` | `jane` | База; `^[A-Za-z0-9_-]{1,63}$` |
| `prefix` | порожній | Префікс колекцій; `^[A-Za-z_][A-Za-z0-9_]{0,40}$` або порожній |
| `auth_source` | `admin` | База автентифікації (якщо задано `username`) |
| `tls` | `false` | TLS |
| `replica_set`, `direct_connection` | не задано | Параметри драйвера |
| `chunk_bytes` | 4 МіБ | Розмір фрагмента RAW, від 1 байта до 15 МіБ |

Секрети: `username`, `password` (необов'язкові). Користувачу потрібна роль `readWrite` на базу: вона дає створення колекцій та індексів, `listCollections` і `$collStats`.

| Колекція | `_id` | Вміст |
|---|---|---|
| `<prefix><entity_type>`, наприклад `product_book` | `sha256(canonical_key)` | Знімок сутності; `search_text` для пошуку; `pending` до перенесення події |
| `<prefix><entity_type>.history` | `<sha256(canonical_key)>\|<version:012d>` | Подія історії; `key_hash`, `version` |
| `<prefix>_deliveries` | `sha256(delivery_key)` | Запис доставки — назавжди; до перенесення коміту сутності — намір `intent` |
| `<prefix>_objects` | `object_id` | Опис об'єкта; маркер завершеного запису |
| `<prefix>_object_chunks` | `<object_id>:<sha256>:<n>` | Байти RAW фрагментами по `chunk_bytes`; документ BSON — до 16 МіБ |

**Простір імен.** `entity_type` відповідає `^[a-z][a-z0-9_]{0,63}$`: не починається з `_` і не містить крапки. Тому за будь-якого префікса колекція типу не збігається ні зі службовою (`<prefix>_…`), ні з історичною (`<prefix>….history`).

Простір `<prefix>*` належить одному підключенню: кожна колекція `<prefix><entity_type>` — тип у каталозі. З порожнім префіксом це вся база. Кілька підключень в одній базі можливі лише з префіксами, жоден з яких не є початком іншого.

Тип `system` потребує непорожнього префікса: MongoDB резервує імена `system.*`, тому колекції `system.history` бути не може. Запис такого типу з порожнім префіксом — неповторювана помилка.

**Індекси.** Індекси колекції типу створюються під час першого запису цього типу в процесі; адаптер пам'ятає, які типи вже мають індекси. `ensure_schema` створює їх і для переданих типів (ядро передає порожній перелік).

| Колекція | Індекси |
|---|---|
| `<prefix><entity_type>` | `canonical_key` — порядок і курсор списків і пошуку; `key.scope` + `canonical_key`; `updated_at`; частковий `pending.delivery_key` — коміти, ще не перенесені |
| `<prefix><entity_type>.history` | Унікальний `key_hash` + `version` |
| `<prefix>_objects` | `stored_at` + `_id` |
| `<prefix>_object_chunks` | `object_id` + `sha256` + `n` |

**Атомарність.** Знімок сутності — єдина точка коміту. `commit_entity`:

1. Читає знімок, потім документ ключа в `_deliveries`. Ключ у `pending` знімка або запис доставки → `DUPLICATE`. Порядок важливий: перенесення пише запис доставки раніше, ніж знімає `pending`, тож ключ, закомічений іншим екземпляром, видно в одному з двох читань.
2. Завершує `pending` попереднього коміту сутності, якщо він лишився. Версія не збігається → `CONFLICT`.
3. Пише в `_deliveries` намір `{delivery_key, intent: {entity_type, entity_id}}` або замінює ним інший намір того самого ключа. Запис доставки вже є → `DUPLICATE`. Намір нічого не комітить: він лише вказує на єдиний знімок, у `pending` якого може опинитися цей ключ.
4. Виконує `replace_one({_id, version: expected})` або `insert_one` для нової сутності; дубль `_id` → `CONFLICT`. Документ несе новий стан, подію історії й підтвердження доставки в `pending`.
5. Переносить подію: вставляє її в історію, замінює намір записом доставки й знімає `pending`. Кожен крок ідемпотентний.

**Ключі доставки.** `get_delivery` не сканує колекції типів: він читає `_deliveries` за `_id`.

- Запис доставки — це відповідь.
- Намір веде до одного знімка. Ключ у його `pending` означає, що коміт відбувся; перенесення завершується на місці.
- Якщо ключа в `pending` немає, документ ключа перечитується: перенесення могло замінити намір між двома читаннями.
- Намір, що лишився, означає «не доставлено»: коміт ще триває або впав до CAS. Наступна спроба з тим самим ключем його замінює.

Збій посередині коміту нічого не губить: `get_delivery`, читання історії й наступний коміт сутності спершу завершують перенесення. Записи доставок зберігаються безстроково; наміри стають записами доставки під час перенесення.

**Каталог і пошук** — `GET /v1/entity-types` і `search` у `GET /v1/entities`.

- Типи беруться з переліку колекцій простору, без службових і `.history`, з точною кількістю `count_documents`. З `scope` рахуються документи з цим `key.scope`. Типи без сутностей не показуються, курсор — за назвою типу.
- Пошук — буквальний підрядок без урахування регістру, на сервері до пагінації. Поле `search_text` містить `casefold()` від JSON із `canonical_key`, `key` і `fields` — той самий текст, який ядро перевіряє для точного ключа. Фільтр — `$indexOfBytes` від терміна в `$literal`: шаблонів немає, тож символи регулярних виразів, `%` і `_` збігаються лише самі з собою.
- Списки й пошук упорядковані за `canonical_key` бінарно, як `COLLATE "C"` у PostgreSQL. `scope` і `updated_since` фільтруються на сервері.
- Текстового індексу немає: пошук переглядає документи вибраного типу.

**Статистика** — `POST /v1/storage-status/checks`.

- Об'єкти: кількість і сума `size_bytes` документів `_objects`.
- Сутності: точні кількості за типами й `size_basis: mongodb_collections_with_indexes` — сума `storageSize + totalIndexSize` колекцій типів із `$collStats`, тобто стиснений обсяг на диску з індексами. Історія, доставки й RAW не входять.
- Кожну колекцію пораховано у свій момент, без спільного знімка: для знімка потрібен реплікасет.
- Якщо `$collStats` не повертає розмірів, уся статистика сутностей — `null` з причиною `statistics_check_failed`, а не нуль.

**Обмеження.** Документ стану з `pending` (копія запису) і `search_text` (копія ключа й полів) має вміститися в 16 МіБ BSON. Тому практична межа однієї сутності — кілька мебібайтів.

## s3

Документи й байти в бакеті `bucket` під префіксом `prefix`. Атомарність — лише умовними `PutObject` (`If-None-Match: *` для створення, `If-Match: <ETag>` для заміни). Код — [jane_storage_s3](../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py).

| `params` | Типово | Значення |
|---|---|---|
| `bucket` | — (обов'язковий) | Ім'я бакета |
| `region` | `us-east-1` | Регіон |
| `endpoint` | не задано (AWS за регіоном) | URL S3-сумісного сервісу; тоді потрібен `addressing_style: path` |
| `addressing_style` | `auto` | `auto`, `path`, `virtual` |
| `prefix` | не задано | Префікс ключів; без `..` |
| `create_bucket` | `false` | Створити бакет, якщо його немає |
| `sse`, `sse_kms_key_id` | не задано | Шифрування на сервері: `AES256` або `aws:kms` |
| `verify_tls` | `true` | Перевірка сертифіката або шлях до CA |
| `claim_attempts` | `3` | Скільки разів прибрати покинуту заявку доставки й заявити ключ знову |

Секрети: `access_key`, `secret_key` (обов'язкові), `session_token` (необов'язковий).

| Ключ у бакеті | Вміст |
|---|---|
| `entities/<entity_type>/<sha256(canonical_key)>.json` | Знімок сутності (+ `pending`: подія цієї версії до перенесення) |
| `history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json` | Подія історії; версії суцільні `1..version` |
| `deliveries/<sha256(delivery_key)>.json` | Запис доставки (+ `claim_id`, `claimed_at` заявки) |
| `objects/<object_key>` | Байти (метадані `x-amz-meta-sha256`) |
| `objects/<object_key>.meta.json` | Опис об'єкта й метадані `Material` |
| `index/objects/<object_id>.json` | Опис об'єкта для пошуку за `object_id` і списків |

`commit_entity`:

1. Заявка доставки: `PUT deliveries/<h>.json` з `If-None-Match: *`. Ключ уже є: завершена доставка → `DUPLICATE`; заявка коміту, що ще триває, → `CONFLICT`; покинута заявка (програла гонку або старша за `lock_stale_ms`) прибирається, заявка повторюється.
2. CAS знімка: `PUT entities/…json` з `If-Match` прочитаного ETag (`If-None-Match: *` для нової сутності). Знімок несе подію історії в `pending` — це єдина точка коміту. `412` → власна заявка видаляється (компенсація) → `CONFLICT`.
3. Перенесення: `PUT history/…/<version>.json`, потім зняття `pending` умовним записом. Збій тут нічого не губить: читачі й наступний коміт спершу завершують перенесення.

### Розкладка й атомарність

Розкладка ключів і кроки коміту наведено вище; нормативний опис — [storage-adapter.md: об'єктні сховища](../../../contracts/docs/storage-adapter.md#обєктні-сховища-minio-s3-і-файлова-система). Межа: компенсація видаляє власну заявку умовним `DeleteObject` з `If-Match`. Сервіси без умовного видалення ігнорують заголовок (MinIO) або відхиляють його — тоді видалення безумовне, і лишається вузьке вікно гонки, у якому можна видалити чужу заявку, записану між читанням і видаленням.

Перевірено на SeaweedFS (S3-сумісний замінник, не MinIO); на AWS S3 у межах цієї документації не перевірялося.

## minio

Той самий протокол і код, що `s3` (`MinioAdapter` наслідує `S3Adapter`), з іншим профілем ([jane_storage_minio](../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py)):

| | `s3` | `minio` |
|---|---|---|
| `params.endpoint` | необов'язковий | обов'язковий |
| `addressing_style` типово | `auto` | `path` |
| `create_bucket` типово | `false` | `true` |
| `sse`, `sse_kms_key_id` | приймаються | відхиляються (KMS MinIO — налаштування сервера) |

Розкладка ключів і секрети — як у [s3](#s3).

## Як перевірити адаптер

Набір сумісності кожного адаптера — `services/storage/adapters/<назва>/tests/test_compat.py`. Файловий адаптер не потребує сервісів і входить у `just test storage`. Інші запускаються з dev-стеком в окремому compose-проєкті.

Приклад для PostgreSQL (перевірено 2026-10-11 на Windows, проєкт `jane-doc-storage`):

```powershell
just up --project jane-doc-storage postgres
just integration --project jane-doc-storage services/storage/adapters/postgres
```

```text
stack project: jane-doc-storage
$ uv run --all-packages pytest -m integration services/storage/adapters/postgres -q
.................                                                        [100%]
17 passed in 45.71s
```

Для інших адаптерів підставте сервіс dev-стеку й каталог: `sqlserver`, `mongodb`, `minio`, `s3` (SeaweedFS). Ці набори в межах цієї документації не запускалися.

Команда нижче зупиняє стек і **видаляє його томи** з усіма записаними даними та файл `.jane/stack-jane-doc-storage.json` зі згенерованими паролями:

```powershell
just down -v --project jane-doc-storage
```
