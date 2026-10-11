# Web Collector: будова

Компоненти коду, алгоритм обробки URL, стани збору, власні дані й гарантії Web Collector. Код — `services/web-collector/src/jane_web_collector/` і `services/web-collector/strategies/discovery/` (ревізія `48389a3`).

## Зміст

- [Компоненти](#компоненти)
- [Стратегії пошуку](#стратегії-пошуку)
- [Обробка одного URL](#обробка-одного-url)
- [Межі, нормалізація й дедуплікація](#межі-нормалізація-й-дедуплікація)
- [robots.txt](#robotstxt)
- [Ліміти хоста між екземплярами](#ліміти-хоста-між-екземплярами)
- [Рендеринг](#рендеринг)
- [Стани збору](#стани-збору)
- [Буфер, підтвердження й backpressure](#буфер-підтвердження-й-backpressure)
- [Власні дані](#власні-дані)
- [Гарантії](#гарантії)

## Компоненти

![Компоненти Web Collector і його залежності](../../diagrams/web-collector/components.light.png#gh-light-mode-only)
![Компоненти Web Collector і його залежності](../../diagrams/web-collector/components.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/web-collector/components.light.png), [темне](../../diagrams/web-collector/components.dark.png); джерело — [components.drawio](../../diagrams/web-collector/components.drawio).

| Модуль | Відповідальність |
|---|---|
| `app.py` | HTTP API `collector.v1`; `/v1/health`, `/v1/info`, `/metrics`, `/v1/jobs/*` — із `jane-kit` |
| `engine.py` | `Engine`: старт і відновлення зборів, разове отримання, прибирання (GC), можливості |
| `crawler.py` | `CrawlRun`: черга, допуск кандидатів, обробка URL, `StrategyContext` — реалізація `DiscoveryContext` для стратегій |
| `discovery/` | реєстр стратегій, вбудовані `seed_list` і `recursive`, витягування посилань з HTML |
| `strategies/discovery/` | `sitemap`, `feed`, `listing`, `url_template`, `api_feed` (окремий пакет, імпортується як `jane_web_collector_discovery`) |
| `fetcher.py` | HTTP-запити: повтори, переадресації з перевіркою кожного кроку, розмір, умовні запити, облікові дані |
| `host_limits.py`, `shared_hosts.py` | ліміти хоста в процесі та між екземплярами через `state.db` |
| `robots.py` | розбір `robots.txt` (RFC 9309) і кеш на хост |
| `egress.py` | політика вихідних адрес: перевірка всіх адрес після DNS для кожного з'єднання |
| `render.py` | рендеринг у headless Chromium через Playwright, проксі з тією самою політикою адрес |
| `urls.py` | нормалізація URL, межі (`scope`), шаблони glob і regex, `material_id` |
| `materials.py` | побудова Material, доставка inline або транзитним blob |
| `state.py`, `stores.py` | власний стан SQLite; job і `Idempotency-Key` на спільних сховищах `jane-kit` |
| `rules.py`, `connections.py` | перевірка й завантаження правил, керовані підключення `kind=http` |

## Стратегії пошуку

Стратегія лише пропонує URL; усі запити йдуть через ядро (`ctx.fetch`) з тими самими межами, `robots.txt` і лімітами. Ядро викликає `on_fetched` **усіх** стратегій для кожної отриманої відповіді, тому стратегії комбінуються.

| `type` | Звідки URL | Особливості |
|---|---|---|
| `seed_list` | `urls` правил або `urls` запиту | глибина 0, на інші сторінки не реагує |
| `recursive` | посилання з кожної HTML-сторінки 2xx, хто б її не знайшов | `seeds`, `follow`, `link_sources` (`a_href`, `link_rel`, `canonical`, `pagination_rel`) |
| `sitemap` | Sitemap, Sitemap Index, `.gz`, текстові sitemap | без `urls` — з `robots.txt`, потім `/sitemap.xml`; `lastmod_since`, `use_lastmod_for_revisit` |
| `feed` | RSS 2.0, RSS 1.0, Atom | `autodiscover` шукає `link rel=alternate` на початкових сторінках |
| `listing` | сторінки категорій, пагінації, пошуку | `item_links`, `next_page` (типово `rel=next`), `page_param`, `search`; сторінки списку видаються як матеріали й перечитуються в кожному зборі |
| `url_template` | шаблон RFC 6570 рівня 1 з діапазонами чи переліками | `stop_after_consecutive_misses` — зупинка після N поспіль 404/410 |
| `api_feed` | сторінки JSON API | JSONPath `items_path`, `url_path`, `lastmod_path`; пагінація `next_url`, `cursor`, `page`; `method: POST`; `emit_items_as_materials` |
| `llm_explore` | — | зарезервовано, не виконується (`supported: false`) |

Порядок у черзі — пріоритет: перший збіг `priorities` правил + `priority` стратегії + `priority` кандидата; за рівного пріоритету — порядок появи. Глибина: початкові URL мають 0, кандидат з `on_fetched` — глибину сторінки + 1; межа — `crawl.max_depth` з урахуванням `strategies[].limits`. Як написати власну стратегію — [strategies/discovery/README.md](../../../services/web-collector/strategies/discovery/README.md).

## Обробка одного URL

![Обробка одного URL: перевірки, повтори, помилки й транзакція](../../diagrams/web-collector/url-pipeline.light.png#gh-light-mode-only)
![Обробка одного URL: перевірки, повтори, помилки й транзакція](../../diagrams/web-collector/url-pipeline.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/web-collector/url-pipeline.light.png), [темне](../../diagrams/web-collector/url-pipeline.dark.png); джерело — [url-pipeline.drawio](../../diagrams/web-collector/url-pipeline.drawio).

1. **Допуск.** Кожен кандидат нормалізується, перевіряється на `scope` (домени, схеми, `path_prefixes`, `include`, `exclude`), глибину й розмір черги; дубль за первинним ключем `(collection_id, url)` відкидається.
2. **Вибір.** До `concurrency.max_parallel_fetches` URL одночасно, але не більше залишку `crawl.max_pages_per_run`.
3. **robots.txt** або явна `owner_policy`.
4. **revisit** — лише в `incremental` для URL з історією `state_key`; пропущений URL стає `unchanged`, а його збережені посилання йдуть у `recursive`.
5. **Backpressure** для матеріалів: чекати, доки в буфері менше `queue.max_unacked_materials`.
6. **Запит.** Слот і черга хоста; переадресації вручну, кожен крок перевіряється `scope` і `robots.txt`, переадресація на вже відомий URL зупиняється без повторного запиту. Повтори для 429, 500, 502, 503, 504 і збоїв мережі з експоненційною паузою та `Retry-After`; `Retry-After` довший за `collector.max_retry_after_seconds` — одразу `rate_limited`.
7. **Відповідь.** `304` — `not_modified`; 404/410 — `not_found`; інші ≥ 400 — `source_unavailable`; 2xx — дедуплікація за кінцевим і `rel=canonical` URL, потім Material.
8. **Стратегії.** `on_fetched` усіх стратегій (крім тієї, що запитала через `ctx.fetch`), до `crawl.max_links_per_page` кандидатів.
9. **Транзакція.** Нові URL черги, статус URL, матеріал у буфері, історія URL, знімки стратегій і лічильники — одна транзакція SQLite, захищена орендою (fence).

Збір завершується, коли в черзі немає `pending` та `inflight`. Вичерпаний бюджет (`crawl.max_pages_per_run`, `crawl.max_bytes_per_run`) теж завершує збір як `succeeded`: решта URL відкидається, у результаті job — `stopped_by` і лічильник `dropped_by_budget`.

## Межі, нормалізація й дедуплікація

- **Нормалізація** (`normalization`): прибрати фрагмент, хост у нижньому регістрі, сортування параметрів, видалення параметрів за іменем або glob (`utm_*`), `trailing_slash`.
- **Шаблони URL** (`UrlPattern`): `glob` порівнюється з канонічним URL без схеми (`*` — у межах сегмента, `**` — будь-що), `regex` — з усім URL.
- **Дедуплікація в зборі**: один рядок черги на канонічний URL; кінцевий URL переадресації та `rel=canonical` (`dedup.use_link_rel_canonical`) теж займають рядок, тож та сама сторінка під іншою адресою дає `duplicates`, а не другий матеріал.
- **`material_id`** — `web:` + хеш канонічного URL; однаковий для всіх спостережень сторінки.
- **`dedup.key: canonical_url_and_content`** — у повторних зборах URL видається знову лише за зміни SHA-256 вмісту.

## robots.txt

Групи за `User-agent` — переважає найточніший збіг токена (перше слово User-Agent або `robots.user_agent_token`), інакше `*`; найдовше правило перемагає, за рівності — `Allow`. Відповідь `robots.txt` 2xx — розбір; 4xx — усе дозволено; 5xx і збої мережі — усе заборонено до спливання кешу (`collector.robots_cache_ttl_seconds`). `Crawl-delay` збільшує інтервал хоста, якщо `rate.respect_crawl_delay`.

## Ліміти хоста між екземплярами

Кожен збір і кожне разове отримання відкривають сесію в спільному для процесу `HostLimiter`. Для хоста діє найсуворіше значення активних сесій: найбільший інтервал і найменша паралельність. Слот тримається лише під час запиту; `Retry-After` відкладає всіх користувачів хоста.

Екземпляри з одним `STATE_DIR` узгоджують ті самі ліміти через таблиці `host_users`, `host_slots`, `host_waiters`, `host_schedule` у `state.db`: запит займає слот платформи й чергу хоста в порядку прибуття. Записи живого екземпляра поновлюються кожні `collector.shared_host_ttl_seconds / 3`; записи зупиненого перестають діяти через TTL. Зайнятий файл стану не валить запит — він чекає й пробує знову, а ліміти процесу діють і далі. Екземпляри з різними `STATE_DIR` не координуються.

## Рендеринг

З `fetch.render_js: true` сторінку спершу завантажує `Fetcher` з усіма перевірками; браузер отримує вже завантажене тіло (`route.fulfill`) і не робить повторного запиту. Подальші навігації верхнього рівня (скриптова переадресація, meta refresh) не виконуються. Інші запити браузера (скрипти, XHR, стилі) йдуть через локальний проксі з тією самою політикою адрес; типи з `RENDER_BLOCK_RESOURCE_TYPES` не завантажуються. Матеріал — серіалізований DOM у UTF-8 з діагностикою `rendered`, `render_incomplete` або `render_budget_exceeded`. Облікові дані підключення браузеру не передаються, умовні запити для таких сторінок не надсилаються.

Перевірено на тестовому сайті: `/js/price` без `render_js` не містить маркера, який додає скрипт, з `render_js` — містить; діагностика `rendered in headless Chromium (fetch.render_js): wait 'networkidle', 719 ms, ...`.

## Стани збору

![Стани збору, скасування, перехід до іншого екземпляра й прострочення](../../diagrams/web-collector/collection-states.light.png#gh-light-mode-only)
![Стани збору, скасування, перехід до іншого екземпляра й прострочення](../../diagrams/web-collector/collection-states.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/web-collector/collection-states.light.png), [темне](../../diagrams/web-collector/collection-states.dark.png); джерело — [collection-states.drawio](../../diagrams/web-collector/collection-states.drawio).

- Збір і його job мають той самий ідентифікатор. Статус «завершено» визначає запис збору; job додає лише `queued`, `running`, `cancelling`.
- **Оренда (lease).** Збір виконує екземпляр, що тримає оренду; він поновлює її кожні `HEARTBEAT_INTERVAL_MS` і заодно перевіряє скасування, зроблене через інший екземпляр. Цикл відновлення кожні `LEASE_SECONDS / 3` підбирає незавершені збори без власника — після kill чи зупинки процесу — і продовжує з останньої транзакції; URL у стані `inflight` повертаються в чергу.
- **Fence.** Кожна транзакція перевіряє, що оренда ще належить цьому екземпляру; запуск, який утратив оренду, нічого не записує.
- **Плавна зупинка** процесу звільняє оренду без зміни статусу — збір лишається відновлюваним.
- **Прострочення.** Через `transfer.job_retention_seconds` після завершення черга, буфер і помилки видаляються, запис лишається, а `GET` повертає `410`.

## Буфер, підтвердження й backpressure

Кожен матеріал отримує в буфері послідовний номер; курсор `c_<номер>` — це цей номер. Запит `/materials` з `after` видаляє з буфера все до курсора включно й оновлює `acked_seq`; курсор, більший за останній виданий номер, відхиляється `422`. Поки непідтверджених матеріалів `queue.max_unacked_materials` або більше, збір чекає (`paused_by_backpressure: true`) і перевіряє буфер кожні `collector.backpressure_poll_ms` — підтвердження може прийти через інший екземпляр.

## Власні дані

Файл `STATE_DIR/state.db` (SQLite, режим WAL) належить лише Web Collector; інші сервіси його не читають ([карта власності даних](../../../contracts/docs/data-ownership.md)).

![ER-схема власного стану Web Collector у SQLite](../../diagrams/web-collector/state-er.light.png#gh-light-mode-only)
![ER-схема власного стану Web Collector у SQLite](../../diagrams/web-collector/state-er.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/web-collector/state-er.light.png), [темне](../../diagrams/web-collector/state-er.dark.png); джерело — [state-er.drawio](../../diagrams/web-collector/state-er.drawio).

| Таблиця | Ключ | Зміст | Час життя |
|---|---|---|---|
| `collections` | `collection_id` | запит, правила, статус, лічильники, оренда, `acked_seq` | запис — назавжди (після прострочення — лише позначка) |
| `frontier` | `collection_id`, `url` | черга й дедуплікація збору | до прострочення збору |
| `strategy_state` | `collection_id`, `strategy_id` | знімки стратегій для відновлення | до прострочення |
| `materials` | `collection_id`, `seq` | буфер виданих непідтверджених матеріалів | до підтвердження |
| `errors` | `collection_id`, `seq` | помилки URL | до прострочення |
| `url_state` | `state_key`, `url` | історія URL: час, статус, ETag, Last-Modified, SHA-256, посилання | до `DELETE /v1/states/{key}` |
| `state_cursors` | `state_key`, `strategy_id` | курсори стратегій для `GET /v1/states` | до `DELETE /v1/states/{key}` |
| `connections` | `connection_id` | керовані підключення (лише посилання на секрети) | до видалення |
| `jobs`, `idempotency` | `job_id`, `key` | job і ключі ідемпотентності (`jane-kit`) | `job_retention_seconds`, `idempotency_ttl_seconds` |
| `counters` | `name` | лічильники послідовностей | постійно |
| `host_*` | `host`, екземпляр або токен | спільний розклад хостів | TTL `collector.shared_host_ttl_seconds` |

Схема створюється під час відкриття файла (`CREATE TABLE IF NOT EXISTS`); номера версії формату немає.

## Гарантії

- **Не більше одного матеріалу на канонічний URL у зборі**; повторне завантаження в новому зборі — нове спостереження з новим `observation_id`.
- **Узгоджене відновлення.** Після kill збір продовжується з останньої транзакції; уже виданий матеріал не видається вдруге, бо матеріал, рядок черги й історія URL записуються разом.
- **Доставка «хоча б один раз» до підтвердження.** Матеріал лишається в буфері, доки отримувач не підтвердить курсор; повторне читання без `after` повертає ті самі матеріали.
- **Ідемпотентний старт.** `POST /v1/collections` з тим самим `Idempotency-Key` і тілом повертає той самий job; заявку зупиненого екземпляра можна перехопити після `IDEMPOTENCY_LEASE_MS`.
- **Ввічливість до сайту.** Ліміти хоста спільні для всіх зборів, разових отримань і екземплярів одного `STATE_DIR`.
- **Без SSRF через колектор.** Політика вихідних адрес діє для кожного з'єднання, включно з переадресаціями й запитами браузера.
