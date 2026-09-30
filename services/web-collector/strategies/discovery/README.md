# Стратегії пошуку Web Collector (WP-03)

Пакет стратегій пошуку матеріалів для ядра Web Collector (WP-02): `sitemap`, `feed`, `listing`, `url_template`,
`api_feed`. Інтерфейс — [`jane_contracts.discovery`](../../../../contracts/python/src/jane_contracts/discovery.py) і
[`contracts/docs/discovery-strategy.md`](../../../../contracts/docs/discovery-strategy.md); параметри — розділ
`$defs/*Strategy` у [`collector-rules.schema.json`](../../../../contracts/schemas/collector-rules.schema.json).
`llm_explore` колектор не виконує (ADR-0010).

## Підключення

Ядро імпортує цей каталог як пакет `jane_web_collector_discovery` і реєструє список `STRATEGIES` з
[`__init__.py`](__init__.py). Інший каталог — `JANE_WEB_COLLECTOR_DISCOVERY_PATH`; Docker-образ колектора копіює
каталог у `/app/strategies/discovery`. Окремого запуску немає: пакет працює лише всередині колектора.
Нових залежностей немає — лише `lxml` (уже є в колекторі) і стандартна бібліотека.

## Загальні правила

- **Мережа — лише через `ctx.fetch` ядра**: scope, `exclude`, `robots.txt`, ліміти на хост, переадресації,
  розміри, тайм-аути й бюджети діють однаково для всіх стратегій. Відмова ядра (`FetchRejected`) — нормальна
  ситуація: URL пропускається; вичерпаний бюджет (`limit_exceeded`, `rate_limited`) зупиняє стратегію.
- **Навігаційні документи** (sitemap, стрічки, сторінки API, `robots.txt`) мають `kind=navigation`, не видаються
  як Material і читаються щоразу повністю (`conditional=False`) — також в `incremental`-зборах. Матеріали, які
  вони перелічують, проходять звичайні правила ядра (dedup, `revisit`).
- **Сторінки списків** (`listing`: категорії, пагінація, пошук) пропонуються як `material` — це HTML-сторінки
  сайту, і очікувані набори testsite (`categories`, `search:*`) їх містять. Як `navigation` вони в комбінації з
  `recursive` прибрали б ці самі сторінки з матеріалів (ядро тримає один `kind` на URL).
- **Глибина**: документ, прочитаний напряму, має рівень 0; його записи — глибину 1; кожен крок пагінації чи
  вкладеного sitemap index — ще +1. Ядро відкидає кандидатів, глибших за `crawl.max_depth` **стратегії**
  (`strategies[].limits`), тож глибина пагінації задається саме ним.
- **Стан і відновлення**: `seeds()` виконується до основного обходу; якщо колектор убили посеред нього, ядро
  викликає `seeds()` знову — навігаційні документи перечитуються, а черга ядра відкидає дублікати (стан, що
  «обіцяє» ще не зафіксовані URL, не зберігається). `listing` зберігає відомі сторінки списків у `snapshot()`,
  і ядро фіксує його в тій самій транзакції, що й кандидатів, тому ланцюжок пагінації не губиться.
  `snapshot()` решти стратегій містить лише діагностичні лічильники (`GET /v1/states/{state_key}` → `cursors`).

## Стратегії

| `type` | Параметри (зі схеми) | Поведінка |
|---|---|---|
| `sitemap` | `urls`, `use_robots_txt` (true), `lastmod_since`, `use_lastmod_for_revisit` (true) | `<urlset>`, `<sitemapindex>` (вкладені індекси), gzip (за сигнатурою, напр. `.gz` як `application/gzip`), текстові sitemap (URL на рядок), RSS/Atom як sitemap. Без `urls`: рядки `Sitemap:` у `/robots.txt` кожного origin правил (origin — з явних URL стратегій правил, інакше `scope.allowed_domains` з першою дозволеною схемою), а якщо їх немає (або `use_robots_txt=false`) — `/sitemap.xml`. `lastmod_since` пропускає записи зі старішим `lastmod` (записи без нього лишаються); `use_lastmod_for_revisit` передає `lastmod` ядру в кандидаті |
| `feed` | `urls`, `autodiscover` (true) | RSS 2.0, RSS 1.0 (RDF), Atom; посилання запису: RSS `link` → `guid isPermaLink` → `rdf:about`, Atom `link rel=alternate` з урахуванням `xml:base`; `lastmod` — `atom:updated`/`dc:date`/`pubDate` або `updated`/`published`. `autodiscover`: `<link rel="alternate" type="application/rss+xml\|atom+xml\|rdf+xml">` на HTML-сторінці з `urls` і на всіх HTML-сторінках глибини 0, отриманих іншими стратегіями (seed-сторінки) |
| `listing` | `start_urls`, `item_links`, `next_page`, `page_param` (`name`, `start`=1, `step`=1, `stop_when_empty`=true), `search` (`url_template` з `{query}`, `queries`) | Стартові сторінки = `start_urls` + сторінки пошуку для кожного запиту. З кожної сторінки списку (отриманої будь-якою стратегією): посилання `item_links` (без нього — усі `a[href]`, крім пагінації й самої сторінки) і наступна сторінка — через `page_param`, якщо задано, інакше `next_page` (типово `rel=next`). Ланцюжок зупиняється на не-2xx, на порожній сторінці (`stop_when_empty`), на повторі елементів попередньої сторінки й на глибині |
| `url_template` | `template` (RFC 6570, рівень 1), `variables` (`range` або `values`), `stop_after_consecutive_misses` | Змінні комбінуються в порядку появи в шаблоні (остання змінюється найшвидше), значення кодуються за RFC 6570. Без `stop_after_consecutive_misses` — усі URL одразу в чергу ядра (паралельно). З ним — послідовно через `ctx.fetch` (як матеріали): найглибша змінна зупиняється після N поспіль 404/410 і починається наступне значення зовнішніх змінних; інші помилки й відмови промахами не вважаються |
| `api_feed` | `url`, `items_path`, `url_path`, `lastmod_path`, `pagination` (`none`, `next_url` + `next_url_path`, `cursor` + `cursor_path` + `cursor_param`, `page` + `page_param`) | Сторінки API (GET) — навігаційні документи; `url_path` кожного елемента — кандидат у матеріали (відносні URL — від адреси сторінки). Пагінація зупиняється без наступної сторінки, на повторі URL чи курсора, на сторінці без нових елементів, на не-2xx або не-JSON і на глибині. `method: POST` і `emit_items_as_materials: true` ядро v1 виконати не може — збір завершується `failed` з поясненням (див. «Відомі обмеження») |

JSONPath (`api_feed`) — підмножина без залежностей: `$`/`@`, `.name`, `['name']`, `[n]` (зокрема від'ємні),
`[*]`, `.*`, `..name`, `..*`; шлях без `$` — від кореня (`items` = `$.items`). Фільтри, зрізи й об'єднання —
помилка конфігурації (збір не стартує).

## Ліміти

Жодних власних чисел: усе — з ефективних лімітів стратегії (`ctx.limits`: платформа → `rules.limits` → запит →
`strategies[].limits`). Типові значення встановлює ядро колектора (README колектора, розділ «Ліміти»).
Відсутній або нечисловий ефективний ліміт — помилка інтеграції з ядром; пакет не підставляє власне число.

| Ліміт | Типово | Що обмежує в стратегіях |
|---|---|---|
| `crawl.max_depth` | 5 | глибину пагінації `listing`/`api_feed` (сторінка N = N-1 кроків; наступна сторінка пропонується, лише поки її елементи вміщаються в ліміт) і вкладеність sitemap index; для довгих списків задайте `limits.crawl.max_depth` у стратегії |
| `crawl.max_links_per_page` | 2000 | записів з одного документа: sitemap, стрічки, сторінки API (зайве відкидається з попередженням і лічильником `entries_over_limit` / `items_over_limit`); кандидатів з однієї сторінки списку обмежує ядро |
| `crawl.max_material_bytes` | 10 MiB | розмір документа (ядро обрізає тіло) і **розпакованого** gzip (`.gz` sitemap/стрічки): вивід понад ліміт обрізається, а не розгортається в пам'яті |
| `crawl.max_seed_urls` | 100000 | кількість URL, згенерованих `url_template` |
| `crawl.max_pages_per_run`, `max_bytes_per_run`, `max_frontier_size` | 5000 / 2 GiB / 100000 | бюджети ядра; вичерпаний бюджет зупиняє стратегію |
| `timeouts.*`, `rate.*`, `concurrency.*`, `retries.*` | див. колектор | застосовує ядро до кожного `ctx.fetch` (з рівнем стратегії) |

## Безпека розбору

- **gzip**: розпакування потоком з обмеженням виводу `crawl.max_material_bytes` (gzip-бомба 200 MiB → 1 MiB за
  частки секунди, тест); пошкоджений чи обрізаний потік дає те, що встигли розпакувати.
- **XML** (`lxml` без нових залежностей; `defusedxml` у колекторі немає): сутності не розгортаються
  (`resolve_entities=False`), мережа й DTD вимкнені (`no_network`, `load_dtd=False`), `huge_tree=False`;
  документ, що **оголошує сутності DTD**, відхиляється повністю (захист від «billion laughs» і XXE); режим
  `recover` зберігає повні записи з документа, обрізаного за розміром.
- **JSON**: тіло вже обмежене ядром; обрізана сторінка API не розбирається; надто глибока вкладеність
  (`RecursionError`) — сторінка вважається невалідною. JSONPath обходить дерево без рекурсії.
- Вміст сайтів — дані: стратегії лише витягають URL і дати.

## Комбінації

Ядро викликає `on_fetched()` усіх стратегій для кожного отриманого ресурсу, тому:
- `recursive` переходить за посиланнями зі сторінок, знайдених будь-якою стратегією (також без власних `seeds`);
- `listing` обробляє свої сторінки списків, навіть якщо їх отримала рекурсія;
- `feed` з `autodiscover` знаходить стрічки на seed-сторінках `seed_list`.

Якщо URL пропонують дві стратегії, матеріал видається один раз; у `discovery.strategy` — та, чий кандидат ядро
прийняло першим (наприклад, товари зі сторінки списку в комбінації з `recursive` можуть бути позначені
`recursive`: це ті самі посилання).

## Приклад

```json
{
  "collector": "web",
  "scope": {"allowed_domains": ["shop.example.test"]},
  "strategies": [
    {"type": "sitemap", "use_robots_txt": true},
    {"type": "listing", "start_urls": ["https://shop.example.test/catalog/phones/"],
     "item_links": {"value": "main li a"}, "limits": {"crawl": {"max_depth": 30}}},
    {"type": "api_feed", "url": "https://shop.example.test/api/v1/products", "items_path": "$.items",
     "url_path": "$.url", "pagination": {"type": "next_url", "next_url_path": "$.next"}},
    {"type": "url_template", "template": "https://shop.example.test/archive/{n}",
     "variables": {"n": {"range": {"start": 1, "end": 500}}}, "stop_after_consecutive_misses": 3},
    {"type": "seed_list", "urls": ["https://shop.example.test/"]},
    {"type": "feed"},
    {"type": "recursive"}
  ]
}
```

## Тести

```
just test web-collector                                        # увесь колектор разом зі стратегіями
uv run --all-packages pytest services/web-collector/strategies # лише WP-03, ~1 хв
```

Усе — проти справжнього testsite (`jane_testsite`, WP-01) і справжнього ядра колектора (WP-02), нічого не
мокається. [`tests/test_testsite.py`](tests/test_testsite.py) — кожна стратегія окремо, з рекурсією, усі разом
і без рекурсії: матеріали дорівнюють очікуваним наборам `expected_urls.json` (кожен URL один раз);
[`tests/test_policy_and_limits.py`](tests/test_policy_and_limits.py) — robots, scope, бюджет, ліміти з рівня
стратегії, `incremental`; [`tests/test_resume.py`](tests/test_resume.py) — kill процесу колектора посеред
`seeds()` і посеред обходу; [`tests/test_units.py`](tests/test_units.py) — формати, gzip-бомба, XXE, JSONPath,
шаблони, пагінація API, реєстрація в реєстрі ядра.

Перевірка типів пакета (`just types` перевіряє лише `src/` і `tests/` сервісів):
`uv run --all-packages mypy services/web-collector/strategies/discovery`.

## Відомі обмеження

- `api_feed`: `method: POST` (тіло запиту) і `emit_items_as_materials` потребують розширення `DiscoveryContext`
  (запит до WP-00/WP-02) — зараз збір завершується `failed` з поясненням, `POST /v1/rules/validations` про це не
  знає (перевіряє лише тип стратегії).
- `use_lastmod_for_revisit`: `lastmod` передається ядру в кандидаті, але ядро v1 не використовує його для
  рішення про повторне відвідування (запит до WP-02).
- `listing` в `incremental`-зборі: відомі сторінки списків ядро пропускає (`revisit.mode=never`) або отримує
  304 (`if_changed`) і не викликає `on_fetched`, тож нові елементи списку знаходить лише `recursive` (він
  отримує збережені посилання). Повний збір (`mode=full`) не має цього обмеження.
- Якщо сторінку списку інша стратегія отримала ще **до** того, як `listing` дізнався про неї (посилання
  `rel=next` з попередньої сторінки), ланцюжок на ній обривається: ядро не повертає вже отриманий ресурс.
  У комбінації з `recursive` посилання все одно обходяться.
- HTML-сторінка в `feed.urls` (для autodiscovery) отримується як `navigation` і не видається матеріалом;
  якщо та сама сторінка потрібна як матеріал, краще `seed_list` + `feed` без `urls`.
- `robots.txt` для пошуку sitemap читається двічі за процес (кеш robots ядра + документ стратегії).
- Паралельність: навігаційні документи в `seeds()` читаються послідовно (для одного хоста це не повільніше —
  частоту обмежує ядро), а основний обхід починається після `seeds()` усіх стратегій.
