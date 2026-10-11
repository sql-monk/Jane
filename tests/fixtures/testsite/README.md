# Тестовий сайт Jane

`jane-testsite` — детермінований вебсайт-магазин для тестів Web Collector, стратегій пошуку й наскрізних сценаріїв. Увесь вміст будується з моделі [site.py](src/jane_testsite/site.py), і з тієї самої моделі обчислюються очікувані набори URL [expected_urls.json](expected_urls.json), тож очікування не можуть розійтися з тим, що віддає сервер. Лише стандартна бібліотека Python 3.12.

## Зміст

- [Запуск](#запуск)
- [Вміст сайту](#вміст-сайту)
- [Очікувані набори URL](#очікувані-набори-url)
- [Особлива поведінка](#особлива-поведінка)
- [Керування для e2e](#керування-для-e2e)
- [Тести й оновлення очікувань](#тести-й-оновлення-очікувань)

## Запуск

Локально, з кореня репозиторію (типово `http://127.0.0.1:8080`):

```powershell
just testsite --port 18841
```

```text
$ uv run --all-packages python -m jane_testsite --host 127.0.0.1 --port 18841 --verbose
Jane testsite on http://127.0.0.1:18841/
```

Параметри `python -m jane_testsite` (або скрипта `jane-testsite`): `--host` (типово `127.0.0.1`), `--port` (типово `8080`), `--verbose` — журнал кожного запиту (рецепт `just testsite` вмикає його завжди), `--write-expected <файл>` — записати очікувані набори й вийти.

У dev-стеку сайт — сервіс `testsite` (`just up testsite`; образ із [Dockerfile](Dockerfile), health-check — `GET /robots.txt`). У pytest — у фоновому потоці на випадковому порту:

```python
from jane_testsite import expected, serve_in_thread

with serve_in_thread() as base_url:
    ...  # crawl base_url and compare with expected().sets["recursive"]
```

## Вміст сайту

| Шлях | Вміст |
|---|---|
| `/` | Головна: каталог, новини, пошук, популярний запит `phone`, петля, календар-пастка, приватні, зовнішні й не-HTTP посилання |
| `/about` | Невідомі сторінки, старе посилання з редиректом, бита сторінка, варіант зі слешем |
| `/catalog/`, `/catalog/<категорія>/?page=<n>` | Категорії `phones`, `laptops`, `accessories`, по 3 товари на сторінці, `rel="next"`/`rel="prev"` |
| `/product/<slug>` | Товар: назва, ціна в UAH, наявність (`InStock`, `OutOfStock`, `PreOrder`), JSON-LD `Product` з `Offer`, мікродані |
| `/news/`, `/news/page/<n>/`, `/news/2026/<slug>` | Новини по 3 на сторінці і статті; дві статті мають дату редагування |
| `/pages/<slug>` | Невідомі сторінки: подія, вакансія, FAQ |
| `/sitemap.xml` → `/sitemaps/products.xml`, `/sitemaps/news.xml.gz`, `/sitemaps/pages.xml` | Sitemap Index із gzip-картою новин |
| `/feeds/news.rss`, `/feeds/news.atom` | RSS і Atom |
| `/api/v1/products?page=<n>`, `/api/v1/products/<slug>` | JSON API по 5 товарів: `{"items", "page", "pages", "next"}` |
| `/search?q=<термін>&page=<n>` | Пошук по 3 результати на сторінці |
| `/archive/<n>` | Шаблон URL: сторінки `1`–`5`, далі `404` |
| `/files/price-list.pdf` | Не-HTML файл |
| `/robots.txt` | `Disallow: /private/`, окремий `Disallow: /` для `BadBot`, посилання на Sitemap |

Дані: 19 товарів (16 у категоріях), 9 статей (8 у переліку новин), 3 невідомі сторінки. Кожна HTML-сторінка має `<meta name="jane:page-type">` з типом (`product`, `category`, `news`, `news-list`, `unknown`…).

## Очікувані набори URL

`expected_urls.json` містить `sets` — шляхи відносно кореня, відсортовані, — і довідкові поля (`entry`, `robots`, `sitemaps`, `feeds`, `api`, `search`, `url_template`, `trap_prefix`, `redirects`, `external_links`, `non_http_links`, `tracking_params`, `page_types`).

| Набір | Шляхів | Що це |
|---|---|---|
| `recursive` | 47 | Усе, що досяжне рекурсивним обходом від `/` у межах сайту з урахуванням `robots.txt` |
| `sitemap` | 32 | Шляхи з усіх карт Sitemap |
| `feeds` | 9 | Статті з RSS/Atom |
| `categories` | 23 | Сторінки категорій із пагінацією та їхні товари |
| `api` | 17 | Товари з JSON API |
| `search:phone` | 12 | Сторінки пошуку `phone` і знайдені товари |
| `search:cable` | 2 | Пошук `cable` і знайдений товар |
| `template:/archive/{n}` | 5 | `/archive/1`–`/archive/5` |
| `only:sitemap`, `only:api`, `only:search`, `only:feeds`, `only:template` | 1, 1, 1, 1, 5 | Знаходить лише одна стратегія — перевірка, що комбінація стратегій дає більше, ніж кожна окремо |
| `robots_disallowed` | 2 | `/private/admin`, `/private/reports` — обхід не має їх завантажувати |
| `broken` | 1 | `/missing-page` — посилання на `404` |

## Особлива поведінка

| Поведінка | Деталі |
|---|---|
| Редиректи `301` | `/old/catalog` → `/catalog/`, `/loop/b/` → `/loop/b`, `/about/` → `/about` |
| Петля | `/loop/a` → `/loop/b` → `/loop/c` → `/loop/a`, посилання на себе й варіант зі слешем |
| Параметри відстеження й фрагмент | `/loop/a?utm_source=home&utm_medium=link`, `/loop/a#top` — нормалізація має звести їх до `/loop/a` |
| Пастка | `/calendar/2026-09` посилається на сусідні місяці без кінця (`trap_prefix`: `/calendar/`) |
| Зовнішні й не-HTTP посилання | `external.example.org`, `cdn.external.example.net`; `mailto:`, `tel:`, `javascript:` — поза областю обходу |
| Умовний GET | Відповідь `200` має `ETag`; запит з `If-None-Match` тим самим значенням — `304` |
| Проксі | `X-Forwarded-Prefix` додається до всіх посилань; `X-Forwarded-Host` і `X-Forwarded-Proto` — до абсолютних URL у картах, стрічках і API |
| Рендеринг JavaScript | `/js/price` заповнює ціну й JSON-LD `Offer` скриптом із `/js/price.json` (у HTML-коді ціни немає); `/js/probe` додатково звертається до `169.254.169.254` — перевірка політики вихідних запитів. Поза всіма наборами |
| Prompt injection | `/pages/faq-injection` містить у тексті інструкцію для LLM — лише за прямою адресою, поза наборами |

## Керування для e2e

Сценарії перевірки цін змінюють товар у процесі сайту без зміни URL:

```bash
curl -s -X PUT http://127.0.0.1:18840/_e2e/products/phone-alpha -H 'Content-Type: application/json' -d '{"price": "279.00"}'
```

```json
{"slug": "phone-alpha", "name": "Phone Alpha", "category": "phones", "price": "279.00", "availability": "InStock"}
```

Дозволені поля — `price` (рядок `279.00`), `availability` (`InStock`, `OutOfStock`, `PreOrder`), `name`; інше — `422`, невідомий товар — `404`. `GET /_e2e/products/<slug>` повертає поточний стан. Зміна живе до перезапуску процесу.

## Тести й оновлення очікувань

```powershell
just test testsite
```

```text
============================= 15 passed in 5.55s ==============================
```

Тест `test_expected_json_is_up_to_date` падає, якщо модель змінено без оновлення файла. Оновлення:

```powershell
uv run python -m jane_testsite --write-expected tests/fixtures/testsite/expected_urls.json
```

Приклади й вивід на цій сторінці перевірено 2026-10-11 на Windows 11, ревізія `48389a3`: локальний запуск на порту `18841` і контейнер dev-стеку на порту `18840`.
