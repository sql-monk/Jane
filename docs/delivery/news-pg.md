# Новини в PostgreSQL: реляційна схема, перенесення, перемикання запису

Доручення людини 2026-10-19: новини й усе, що їх стосується, перенести з MongoDB у PostgreSQL як нормальні реляційні дані. Для цього треба підготувати базу, написати скрипти перенесення й переробити збереження новин з Mongo на PostgreSQL.

Цей документ — спільний дизайн для виконавців. Відступати від нього можна лише з поясненням у розділі «Хід виконання».

## 1. Обсяг

| Тип | Хто пише | Ключ (`scope` / `natural`) | Mongo (`results-mongo`) | Старий `results-pg` (`public`, до 12.10) |
|---|---|---|---|---|
| `article` | `news.articles` (examples/sites, 8 сайтів) | `source_id` / `url` | 1 834 (+ історія 1 875) | 1 035 (історія 1 075) |
| `post` | `telegram.web-posts` (8 `tg-*`), `channels.telegram-posts` | `source_id` / `channel`+`message_id` | 605 (історія 7 152) | 433 (історія 8 951) |
| `news_article` | `news.article-normalize` (examples/news, 12 завдань) | `source_id` / `url` | 263 (історія 421) | 328 (історія 564) |
| `news_event` | `news.article-normalize` | `news-events` / `event_id` | 8 (історія 10) | 16 (історія 32) |

Поза обсягом:
- RAW лишається в `raw-files`;
- товари, оголошення й авто лишаються в Mongo;
- демо-тип `event` (`examples.telegram-event-extractor`) теж лишається в Mongo;
- нерозгорнутий комплект `news.analysis` (`news_item`, `news_mention`) не переносимо;
- вихідні дані в Mongo і `public.jane_*` **не видаляються**.

## 2. Архітектура

- **Де лежать дані.** База та сама — `jane_storage_results`, нова схема `news`. Підключення `results-news`: `kind: postgresql`, ті самі `host`/`port`/`database`/`secret_refs`, що й у `results-pg`, плюс `params.schema = "news"` і новий параметр підключення `params.layout = "news"`. Інфраструктуру (provision, compose) не змінюємо: адаптер сам робить `CREATE SCHEMA IF NOT EXISTS`.
- **Точка розширення — адаптер `postgresql`** (`services/storage/adapters/postgres`). Kind, пакет `jane.storage-postgresql@1.0.0` і його дайджест, ядро Storage і контракти не змінюються.
- **Стан рушія.** Загальні таблиці `news.jane_entities`, `news.jane_entity_history`, `news.jane_deliveries` і `news.jane_objects` лишаються джерелом істини для протоколу адаптера. На них тримаються злиття за полями (`field_orders`, `cleared_fields`), CAS за версією, ідемпотентність доставок, а також `/v1/entities`, пошук, каталог і статистика.
- **Реляційна проєкція.** Якщо `layout = "news"`, то в **тій самій транзакції** `commit_entity` після успішного CAS знімок сутності типу `article`, `post`, `news_article` або `news_event` розкладається в нормалізовані таблиці (розділ 3). Проєкція завжди узгоджена зі станом. Сутності інших типів, наприклад `product` із набору сумісності C-01…C-16, пишуться лише в загальні таблиці.
- **Чому стан не перебудовується з колонок.** Перетворення значень у типи PostgreSQL втрачає оригінальний рядок, наприклад `+03:00` у часі. Злиття бачило б такі значення як зміни. Тому `fields` у jsonb лишається внутрішнім станом рушія, а реляційні таблиці — це модель для SQL-споживачів.
- **Еволюція схеми.** Нумеровані міграції розкладки, таблиця `news.jane_layout_migrations(layout, version, applied_at)`. Застосовуються в `ensure_schema` під тим самим advisory-lock.
- **Перебудова.** Функція `rebuild` очищає проєкцію і заново розкладає всі знімки чотирьох типів із `jane_entities` (наприклад, після нової міграції розкладки). Її доступно з CLI модуля.

## 3. Реляційна схема `news`

Усі часові колонки — `timestamptz`, упевненості (`*_confidence`) — `double precision`. Кожна таблиця сутностей має `canonical_key text UNIQUE NOT NULL` (зв'язок зі станом рушія й `run_output_identities` Orchestrator), `version int`, `updated_at timestamptz` і `extra jsonb NOT NULL DEFAULT '{}'`.

**Довідники**

| Таблиця | Колонки |
|---|---|
| `source` | `source_id text PK` (`= key.scope`), `kind` (`web` / `telegram`), `name`, `site`, `channel`, `first_seen_at`, `last_seen_at` |
| `tag` | `tag_id bigint identity PK`, `name text UNIQUE` |
| `topic` | `topic_id`, `name UNIQUE` |
| `named_entity` | `named_entity_id`, `canonical_name`, `entity_kind` (`person` / `organization` / `country` / `place` / `product` / `group` / `other`), `UNIQUE(canonical_name, entity_kind)` |

**Сутності та їхні дочірні таблиці**

| Таблиця | Колонки |
|---|---|
| `article` | `article_id PK`, `canonical_key`, `source_id FK→source`, `url`, `site`, `title`, `lead`, `body` (поле `text`), `author`, `section`, `language`, `image`, `published_at`, `modified_at`, `UNIQUE(source_id, url)` |
| `article_tag` | `article_id FK ON DELETE CASCADE`, `position`, `tag_id FK`, `PK(article_id, position)` |
| `post` | `post_id PK`, `canonical_key`, `source_id FK`, `channel`, `message_id bigint`, `url`, `title`, `body`, `views bigint`, `forwarded_from`, `has_media bool`, `edited bool`, `published_at`, `UNIQUE(source_id, channel, message_id)` |
| `post_link` | `post_id FK CASCADE`, `position`, `url`, `PK(post_id, position)` |
| `news_event` | `news_event_id PK`, `canonical_key`, `scope`, `event_id`, `summary`, `identity_kind`, `grouping_method`, `identity_confidence`, `event_date date`, `event_time time`, `primary_actor`, `action`, `object`, `location`, `country`, `UNIQUE(scope, event_id)` |
| `news_article` | `news_article_id PK`, `canonical_key`, `source_id FK` (`source_name`/`source_kind` — у `source`), `url`, `material_id`, `content_sha256`, `headline`, `headline_ukrainian`, `summary`, `source_language`, `analysis_language`, `reporting_kind`, `region`, `transport`, `published_at`, `fetched_at`, `edited_at`, `evidence_validation`, `event_id text` (логічне посилання на `news_event.event_id`, **без FK**: порядок надходження довільний, зв'язок може бути очищений), `grouping_status`, `grouping_method`, `grouping_reason`, `sentiment_label`, `sentiment_confidence`, `sentiment_explanation`, `UNIQUE(source_id, url)` |
| `news_article_event` | 1:1 з `news_article`, «що стаття каже про подію»: `news_article_id PK FK CASCADE`, `summary`, `identity_confidence`, `identity_specificity`, `identity_kind`, `event_date`, `event_time`, `primary_actor`, `action`, `object`, `location`, `country`, `date_resolution_method`, `date_resolution_quote`, `date_resolution_reference_published_at` |
| `news_article_topic` | `news_article_id FK CASCADE`, `position`, `topic_id FK`, `PK(news_article_id, position)` |
| `news_article_location` | `news_article_id FK CASCADE`, `position`, `name`, `PK(...)` |
| `news_article_mention` | `mention_id PK`, `news_article_id FK CASCADE`, `position`, `named_entity_id FK`, `name` (як у тексті), `role`, `attitude`, `attitude_confidence`, `factual_impact`, `UNIQUE(news_article_id, position)` |
| `evidence` | `evidence_id PK`, `news_article_id FK CASCADE`, `subject` (`event` / `event_time` / `sentiment` / `mention`), `mention_id FK NULL CASCADE`, `position`, `quote`, `reason`, `attribution` |

**Подання**
- `news_article_with_event`: `news_article LEFT JOIN news_event USING (event_id)`;
- `article_analysis`: `article JOIN news_article ON url` — аналіз LLM поруч зі статтею сайту.

**Правила проєкції**
1. Батьківський рядок оновлюється upsert-ом за `canonical_key`. Дочірні рядки щоразу видаляються й вставляються заново. Довідники заповнюються upsert-ом за назвою.
2. Поля, яких немає у знімку (зокрема з `cleared_fields`), дають `NULL`.
3. Невідомі поля верхнього рівня, а також значення, що не перетворюються в тип колонки (наприклад, нерозбірний час), потрапляють у `extra`. Ключ — шлях поля, наприклад `published_at` чи `event.canonical.foo`. Колонка тоді `NULL`. Значення ніколи не губляться.
4. `source` оновлюється з кожної сутності:
   - `article` → `kind=web`, `site`;
   - `post` → `kind=telegram`, `channel`;
   - `news_article` → `source_kind`, `source_name`.

   `news_event.scope` на `source` не посилається.

## 4. Перенесення даних

Скрипт `scripts/migrate_news_to_pg.py`. Джерела:
- Mongo `jane_results.<type>.history`;
- старий `jane_storage_results.public.jane_entity_history` (чотири типи).

Як він працює:
- **Відтворення через рушій.** Події історії групуються за `(entity_type, canonical_key)` і впорядковуються за `received_at` (далі джерело, версія). Кожна подія проганяється через `StorageEngine.store_entity` над `PostgresAdapter` підключення `results-news`. Годинник рушія повертає оригінальний `received_at` події, `delivery_key` береться оригінальний.
- **Що це дає:**
  - злиття, версії, історія й доставки виходять такі самі, як дав би живий запис;
  - проєкція будується автоматично;
  - повторний запуск ідемпотентний (`duplicate`), тож другий прогін дотягує хвіст подій, що з'явилися після першого.
- **Режими:**
  - `--dry-run` — лише підрахунок;
  - `--verify` — звірка стану з джерелом і проєкції зі станом, звіт за типами й джерелами.

  Ліміти (розмір пачки, паралельність) задаються параметрами з безпечними типовими значеннями.

## 5. Перемикання запису

- Підключення `results-news` додається в `infra/config/storage-connections.json`, `examples/documents/connections.json` і `tests/e2e/config/storage-connections.json`.
- Етапи збереження сутностей цих типів переходять на `jane.storage-postgresql` + `results-news`:
  - `examples/sites/sites/news-*.json` (етап `store-articles`) і `tg-*.json` (`store-posts`);
  - `examples/news/setup_news.py` (`store-news`);
  - `examples/channels/setup_channels.py` (`store-posts`).
- RAW і далі пишеться в `raw-files`.
- Рішення фіксує ADR-0012, який уточнює ADR-0011.

## 6. Розгортання на `jane-demo`

Порядок:
1. Резервна копія (`pg_dump` бази `jane_storage_results`). Mongo не змінюється.
2. Новий образ `storage`.
3. Підключення `results-news` в Orchestrator.
4. Пауза розкладів новинних завдань.
5. Перенесення.
6. Перемикання завдань.
7. Відновлення розкладів.
8. Другий прогін перенесення (хвіст).
9. Звірка (`--verify`).
10. Запис у «Хід виконання».

## 7. Хід виконання

Роботу 2026-10-19 вели три субагенти паралельно за цим дизайном, без перетину шляхів. Потім було незалежне рев'ю: вердикт «прийнято із зауваженнями», блокерів не знайдено, чотири зауваження виправлено. Окремо проведено інтеграційний прогін на фінальному коді.

### A — розкладка `news` в адаптері `postgresql`

**Що зроблено**
- Новий пакет `jane_storage_postgres/news_layout/`: `ddl.py` (міграція 1), `mapping.py` (чистий мапінг знімка в рядки), `__init__.py` (`ensure_layout`, `write_projection`, `rebuild`), `__main__.py` (CLI `python -m jane_storage_postgres.news_layout rebuild --schema news …`, пароль — лише через `--password-env`).
- В адаптері (`__init__.py`): параметр підключення `layout`, міграції в `ensure_schema`, проєкція в `commit_entity` після CAS та історії в тій самій транзакції, `rebuild_layout()`.

**Відступи від дизайну та уточнення**
- Таблиці проєкції без префікса — одна розкладка на схему.
- Довідники заповнюються `INSERT … ON CONFLICT DO NOTHING` у відсортованому порядку, потім читається id. Так популярні теги не серіалізують коміти.
- `named_entity.entity_kind` може бути NULL, унікальність `UNIQUE NULLS NOT DISTINCT` (потрібен PostgreSQL 15+, стек на 18).
- CHECK на переліки свідомо немає.
- Шляхи в `extra` мають вигляд `event.canonical.foo`, `tags[2]`, `entities[0].evidence[1].page`.
- Подання `news_article_with_event` дає колонки події з префіксом `event_`.
- Атрибути `source` визначаються за `updated_at` знімка, а не за порядком комітів, тож `rebuild` дає ту саму проєкцію, що й живий запис. Відмінності `rebuild` описано в `docs/components/storage/adapters.md`: нові сурогатні id, довідники без посилань зникають, атрибут, який мала лише попередня версія сутності.
- Якщо в підключенні задано `layout`, етап не може перевизначити `schema` чи `table_prefix` (неповторювана `AdapterError` в `open`).
- Дайджест `jane.storage-postgresql@1.0.0` не змінився: `sha256:4765e62faa6e82fa25a863dff2ef133905bf8e9b5e0b8f0f9e6285d2a451ac3b`.

**Перевірки**
- `just integration --project news-a services/storage/adapters/postgres`: `47 passed, 25 deselected`. Набір C-01…C-16 пройшов і з `layout=news`.
- Після виправлень за рев'ю: `test_news_layout.py` + `TestPostgresCompatNewsLayout` — `29 passed`; юніт-тести адаптера — `33 passed, 47 deselected`.
- `just test storage`: `241 passed`.
- ruff і mypy чисті.

### B — скрипт `scripts/migrate_news_to_pg.py`

**Як працює**
- Джерела читаються через протокол адаптерів (`list_entities`/`list_history`).
- Події ключа впорядковуються за `received_at`, потім джерелом (legacy раніше mongo), потім позицією.
- Кожна подія йде через `StorageEngine.store_entity` з фіксованим годинником `received_at` і оригінальним `delivery_key`. Паралельність лише між ключами.
- Скрипт пише від ролі `jane_storage_results` і перевіряє власника схеми `news` до і після запису.
- Опції: `--dry-run`, `--verify` (стан проти джерел; проєкція проти стану за парами `(canonical_key, version)`), `--types`, `--source`, `--batch-size`, `--concurrency`, `--max-failures`, `--examples`.

**Відступи від дизайну та уточнення**
- Очікувана версія ключа з обох джерел дорівнює кількості *різних* `delivery_key`.
- Події, яких немає в джерелах (живий запис після перемикання), мають статус `changed_after` і помилкою не вважаються.

**Перевірки**
- Юніт-тести: `12 passed, 1 deselected`.
- `just integration --project news-b2 scripts/tests/test_migrate_news_to_pg.py -s`: `1 passed`.
  - Перший прогін: `written 30, stale 3, duplicate 1`; другий: `duplicate 34`.
  - `--verify` OK, проєкція 3/3, 3/3, 3/3, 4/4.
  - Підроблена версія рядка дає `MISMATCH` і код 1.
- `--dry-run` на jane-demo (лише читання):

| Тип | legacy-pg сутн. / подій | mongo сутн. / подій | ключів | в обох |
|---|---|---|---|---|
| `article` | 1035 / 1075 | 1840 / 1883 | 2865 | 10 |
| `post` | 433 / 8951 | 607 / 7569 | 1032 | 8 |
| `news_article` | 328 / 564 | 271 / 435 | 591 | 8 |
| `news_event` | 16 / 32 | 8 / 10 | 24 | 0 |

  Спільних `delivery_key` між джерелами — 0. Швидкість з хоста — близько 30 подій/с при `--concurrency 16` (затримка Docker Desktop), тобто ≈ 10–15 хв на jane-demo.

### C — перемикання запису й документація

**Конфігурація**
- `results-news` додано в `infra/config/storage-connections.json`, `examples/documents/connections.json` і `tests/e2e/config/storage-connections.json`.
- 33 новинні завдання пишуть у `jane.storage-postgresql` + `results-news`:
  - 8 `news-*` (`store-articles`);
  - 8 `tg-*` (`store-posts`);
  - 12 `examples/news` (`store-news`);
  - 5 `examples/channels` (`store-posts`).
- Читання в `setup_news verify`, `validate_live`, `setup_channels` і `export_sites` іде з `results-news`.
- Товари, оголошення, авто й демо `event` лишились у `results-mongo`.

**Тести**
- `examples/tests/test_examples.py` перевіряє розміщення за типами з маніфестів, мутаційно перевірено.
- `examples/tests`: `176 passed, 1 failed`. Упав нестабільний `test_classifieds.py::test_polling_transport_failures_end_at_overall_timeout`, окремо він проходить; цієї зміни він не стосується.

**Документи**
- ADR-0012; позначки в ADR-0011.
- `data-ownership`, `deployment`, `entity-types`, `backup-restore`, `infra/README`, README прикладів, примітка в `mongo-entities.md`.

**Не зроблено:** діаграми `docs/diagrams/platform/dev-stack.drawio` і `operations/data-ownership.drawio` ще кажуть «сутності → mongodb».

### Незалежне рев'ю

Вердикт — «прийнято із зауваженнями». Виправлено:
1. Інтеграційний тест скрипта приймав відсутню розкладку. Тепер перевірка безумовна, і є юніт-тест, що `run()` відкриває ціль з `layout=news`.
2. `--verify` звіряв проєкцію лише кількістю рядків. Тепер звіряє пари `(canonical_key, version)`.
3. Атрибути `source` після `rebuild` могли відрізнятися від живого запису. Тепер їх визначає `updated_at`.
4. Етап міг перевизначити простір імен підключення з розкладкою. Тепер `AdapterError`.
