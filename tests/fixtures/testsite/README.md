# Тестовий сайт (testsite)

Детермінований сайт-фікстура для перевірок Web Collector (WP-02) і стратегій пошуку (WP-03), а також
«невідомих» сторінок (WP-09/WP-11). Лише стандартна бібліотека Python.

## Запуск

| Як | Команда | Адреса |
|---|---|---|
| Локально | `just testsite` (або `uv run python -m jane_testsite --port 8080`) | `http://127.0.0.1:8080/` |
| У тестах | `from jane_testsite import serve_in_thread` → `with serve_in_thread() as base: ...` | випадковий порт |
| У compose | сервіс `testsite` стеку `just up` | порт з `just env` (`testsite`), а також `http://<proxy>/testsite/` |

Як залежність сервісу: `jane-testsite = { workspace = true }` у `[tool.uv.sources]` і в dev-групі.

Абсолютні URL у sitemap, стрічках і API будуються з заголовка `Host`, тож сайт працює на будь-якому порту.
Через reverse proxy префікс `/testsite` передається заголовком `X-Forwarded-Prefix` і додається до всіх посилань.

## Очікувані URL

Машинозчитувано: [`expected_urls.json`](expected_urls.json) (генерується з моделі `site.py`; тест
перевіряє, що файл актуальний). Шляхи — відносно кореня сайту. Регенерація:

```
uv run python -m jane_testsite --write-expected tests/fixtures/testsite/expected_urls.json
```

| Набір (`sets.*`) | Що це | Як отримати |
|---|---|---|
| `recursive` | усе, що знаходить рекурсивний обхід від `/` у межах хоста з дотриманням `robots.txt`, нормалізацією (без `#фрагмента`, без `utm_*`), переходом за редиректами й виключенням `/calendar/` | обхід |
| `sitemap` | URL з `/sitemap.xml` (index) → `products.xml`, `news.xml.gz` (gzip-файл, `application/gzip`), `pages.xml` | sitemap |
| `feeds` | статті з `/feeds/news.rss` і `/feeds/news.atom` (однакові) | RSS/Atom |
| `categories` | `/catalog/<категорія>/` з пагінацією `?page=N` (`rel="next"`) і товари на них | категорії/пагінація |
| `search:cable`, `search:phone` | сторінки результатів `/search?q=<term>&page=N` і товари | пошук |
| `api` | товари з JSON API `/api/v1/products?page=N` (поле `next`), деталі `/api/v1/products/<slug>` | API/JSON |
| `template:/archive/{n}` | `/archive/1..5`; `/archive/6` → 404 (умова зупинки) | шаблон URL |
| `robots_disallowed` | `/private/*` — посилання є, але `robots.txt` забороняє; не можна завантажувати | — |
| `broken` | `/missing-page` → 404 | — |
| `only:sitemap`, `only:api`, `only:search`, `only:feeds`, `only:template` | URL, які знаходить **лише** відповідна стратегія (рекурсія їх не бачить) — для перевірки комбінацій | — |

Інше в `expected_urls.json`:

- `redirects`: `/old/catalog` → `/catalog/`, `/loop/b/` → `/loop/b`, `/about/` → `/about` (301).
- `trap_prefix`: `/calendar/` — нескінченний календар (кожен місяць посилається на наступний). Обхід без
  обмеження глибини або правила виключення ніколи не завершиться; очікуваний набір `recursive` рахується з
  виключенням `^/calendar/`.
- `external_links`: посилання на `external.example.org` і `cdn.external.example.net` — не завантажувати.
- `non_http_links`: `mailto:`, `tel:`, `javascript:` — ігнорувати.
- `tracking_params`: `utm_source`, `utm_medium` — `/loop/a?utm_source=...` і `/loop/a#top` дублюють `/loop/a`.
- `page_types`: тип кожної сторінки (`product`, `news`, `unknown`, `category`, `news-list`), також у
  `<meta name="jane:page-type">`. `unknown` — сторінки подій, вакансій, FAQ, для яких немає екстрактора.

Цикли: `/loop/a → /loop/b → /loop/c → /loop/a`, самопосилання, товари посилаються на «пов'язаний» товар
по колу, статті — на новішу/старішу.

Дані сторінок: товари містять JSON-LD `Product` з `offers.price`, мікродані й `.price`; статті — `<time>`,
`article:published_time`/`modified_time`, заголовок `Last-Modified`. Усі сторінки мають `ETag` і відповідають
`304` на `If-None-Match` (повторне відвідування).

## Керована зміна товару для e2e

`PUT /_e2e/products/{slug}` приймає JSON з одним або кількома полями `price` (рядок на кшталт
`"279.00"`), `availability` (`InStock`, `OutOfStock`, `PreOrder`) та `name`. `GET` за тим самим шляхом
повертає поточний товар. Зміна діє в пам'яті одного процесу testsite до його завершення: URL товару не
змінюється, а HTML, JSON-LD, JSON API та `ETag` відображають нове значення. Службовий шлях не входить
до посилань, sitemap чи `expected_urls.json` і призначений лише для ізольованого тестового сайту.
