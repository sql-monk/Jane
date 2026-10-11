# Web Collector: швидкий старт

Запуск Web Collector разом із детермінованим тестовим сайтом без Docker, Orchestrator і Registry: разове отримання сторінки, збір двома стратегіями, читання й підтвердження матеріалів, повторний збір.

Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7 і Git Bash), ревізія `48389a3`; на Linux не перевірялися. Порти 18110 (тестовий сайт) і 18101 (колектор) взято для прикладу — підставте вільні.

## Зміст

- [Передумови](#передумови)
- [Запуск](#запуск)
- [Отримати одну сторінку](#отримати-одну-сторінку)
- [Зібрати новини двома стратегіями](#зібрати-новини-двома-стратегіями)
- [Прочитати й підтвердити матеріали](#прочитати-й-підтвердити-матеріали)
- [Повторний збір](#повторний-збір)
- [Помилки збору](#помилки-збору)
- [Прибирання](#прибирання)

## Передумови

- uv і Python 3.12+ — встановлення в [DEVELOPMENT.md](../../../DEVELOPMENT.md).
- Команди виконуються з кореня репозиторію; залежності встановлено командою `uv sync --all-packages`.
- Для `fetch.render_js` потрібен ще Chromium: `uv run playwright install chromium` (див. [dependencies.md](dependencies.md#рендеринг-javascript)). Для кроків нижче він не потрібен.

## Запуск

1. У першому терміналі запустіть тестовий сайт:

   ```powershell
   uv run python -m jane_testsite --port 18110
   ```

   ```text
   Jane testsite on http://127.0.0.1:18110/
   ```

2. У другому терміналі задайте порт і запустіть колектор.

   PowerShell:

   ```powershell
   $env:JANE_WEB_COLLECTOR_PORT = "18101"
   uv run --package jane-web-collector python -m jane_web_collector
   ```

   Bash:

   ```bash
   JANE_WEB_COLLECTOR_PORT=18101 uv run --package jane-web-collector python -m jane_web_collector
   ```

   Журнал пишеться рядками JSON. Очікувані рядки (уривок, поля скорочено):

   ```text
   {"level": "warning", "logger": "jane.auth", "msg": "auth_mode=none: every caller has every scope - for local tests only", ...}
   {"level": "info", "logger": "jane_web_collector.app", "msg": "configured limits", ...}
   {"level": "info", "logger": "uvicorn.error", "msg": "Uvicorn running on http://127.0.0.1:18101 (Press CTRL+C to quit)", ...}
   ```

   `auth_mode=none` — сервіс приймає запити без ключа; так можна лише локально. Стан пишеться в `.jane/web-collector/state.db` відносно поточного каталогу.

3. У третьому терміналі перевірте стан і можливості:

   ```powershell
   curl.exe -s http://127.0.0.1:18101/v1/health
   curl.exe -s http://127.0.0.1:18101/v1/info
   ```

   На Linux — те саме з `curl` замість `curl.exe`. Відповідь health:

   ```json
   {"status":"ok","checks":{"state_store":{"status":"ok"}}}
   ```

   У `/v1/info` поле `capabilities` (уривок) показує зареєстровані стратегії та підтримку рендерингу:

   ```json
   {
     "source_kinds": ["web"],
     "strategies": ["api_feed", "feed", "listing", "recursive", "seed_list", "sitemap", "url_template"],
     "unsupported_strategies": ["llm_explore"],
     "content_delivery": ["auto", "inline"],
     "rules_sources": ["inline"],
     "connection_kinds": ["http"],
     "robots_policies": ["respect", "owner_policy"],
     "render_js": true
   }
   ```

   `content_delivery` без `blob` — транзитне сховище не налаштовано (`JANE_WEB_COLLECTOR_TRANSIT_DIR`); `rules_sources` лише `inline` — немає `RULES_DIR` і Registry.

## Отримати одну сторінку

1. Збережіть тіло запиту у файл `fetch.json`. Правила inline задають межі обходу й нормалізацію URL (схема — [collector-rules.schema.json](../../../contracts/schemas/collector-rules.schema.json)); `strategies` для разового отримання не використовуються, але обов'язкові за схемою:

   ```json
   {
     "source_kind": "web",
     "source_id": "testsite",
     "url": "http://127.0.0.1:18110/product/laptop-four?utm_source=doc",
     "rules": {
       "collector": "web",
       "scope": {"allowed_domains": ["127.0.0.1"]},
       "strategies": [{"type": "seed_list", "urls": ["http://127.0.0.1:18110/"]}],
       "normalization": {"strip_query_params": ["utm_*"]}
     }
   }
   ```

2. Надішліть запит.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18101/v1/fetches -ContentType application/json -InFile fetch.json).Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18101/v1/fetches -H 'Content-Type: application/json' --data @fetch.json
   ```

   Відповідь — матеріал за [material.schema.json](../../../contracts/schemas/material.schema.json). Уривок, відформатовано, `content.data` скорочено:

   ```json
   {
     "material_id": "web:364b50889135364b4358260b3e7621ae",
     "observation_id": "obs_01a12a661ed50000745c0fd1",
     "source": {"kind": "web", "source_id": "testsite"},
     "locator": {
       "url": "http://127.0.0.1:18110/product/laptop-four",
       "final_url": "http://127.0.0.1:18110/product/laptop-four",
       "canonical_url": "http://127.0.0.1:18110/product/laptop-four"
     },
     "fetched_at": "2026-10-11T09:58:18Z",
     "format": {"media_type": "text/html", "content_kind": "page", "charset": "utf-8"},
     "revision": {
       "content_sha256": "fbff2501c24e5e29e62bfffae13666cb953c0976e7bc03eba046fa3cd01364eb",
       "source_revision": "\"fbff2501c24e5e29\""
     },
     "content": {
       "kind": "inline",
       "media_type": "text/html",
       "data": "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Laptop Four |...",
       "size_bytes": 1093
     },
     "http": {"status": 200, "headers": {"content-type": "text/html; charset=utf-8", "etag": "\"fbff2501c24e5e29\""}},
     "collector": {"name": "web-collector", "version": "0.1.0"},
     "metadata": {"title": "Laptop Four | Jane Test Shop"}
   }
   ```

   Параметр `utm_source` прибрано нормалізацією. Кожен виклик — нове спостереження: `material_id` той самий, `observation_id` і `fetched_at` нові.

3. Перевірте відмову за `robots.txt` (тестовий сайт забороняє `/private/`):

   PowerShell 7:

   ```powershell
   curl.exe -s -X POST http://127.0.0.1:18101/v1/fetches -H "Content-Type: application/json" -d '{"source_kind": "web", "url": "http://127.0.0.1:18110/private/admin"}'
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18101/v1/fetches -H 'Content-Type: application/json' -d '{"source_kind": "web", "url": "http://127.0.0.1:18110/private/admin"}'
   ```

   Відповідь `403` у форматі `application/problem+json`:

   ```json
   {"type":"urn:jane:problem:access_denied_by_policy","title":"Access denied by policy","status":403,"detail":"disallowed by robots.txt for user-agent JaneBot","instance":"/v1/fetches","code":"access_denied_by_policy","retryable":false,"trace_id":"a416d3aeabe4abbf5a258377515185ab"}
   ```

   Сторінка, якої немає (`/missing-page`), дає `404` з кодом `not_found` і `details.http_status: 404`.

## Зібрати новини двома стратегіями

Стрічка RSS (`feed`) дає новини, зокрема ту, на яку немає посилань на сайті; рекурсивний обхід (`recursive`) від `/news/` додає сторінки списків. Результати зливаються в одну чергу без дублів.

1. Збережіть тіло запиту у файл `collection.json`:

   ```json
   {
     "source_kind": "web",
     "source_id": "testsite",
     "state_key": "testsite-news",
     "mode": "full",
     "rules": {
       "collector": "web",
       "scope": {
         "allowed_domains": ["127.0.0.1"],
         "path_prefixes": ["/news/", "/feeds/"]
       },
       "strategies": [
         {"type": "feed", "strategy_id": "news-feed", "urls": ["http://127.0.0.1:18110/feeds/news.rss"]},
         {"type": "recursive", "strategy_id": "news-pages", "seeds": ["http://127.0.0.1:18110/news/"],
          "limits": {"crawl": {"max_depth": 2}}}
       ],
       "revisit": {"mode": "if_changed"}
     },
     "limits": {"rate": {"requests_per_second_per_host": 20, "min_delay_ms_per_host": 0}}
   }
   ```

   `path_prefixes` має містити й `/feeds/`: навігаційні документи (стрічка) проходять ті самі межі, що й сторінки. Ліміт частоти піднято лише для тестового сайту; типово — 1 запит на секунду на хост.

2. Запустіть збір. Заголовок `Idempotency-Key` обов'язковий: повтор із тим самим ключем і тілом повертає той самий job.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18101/v1/collections -ContentType application/json -Headers @{"Idempotency-Key" = "doc-news-2"} -InFile collection.json).Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18101/v1/collections -H 'Content-Type: application/json' -H 'Idempotency-Key: doc-news-2' --data @collection.json
   ```

   Відповідь `202 Accepted` із заголовком `Location: /v1/jobs/<job_id>`:

   ```json
   {"job_id":"job_b5ca4926490c435eac915268a1ac5d6a","kind":"collection","status":"queued","created_at":"2026-10-11T09:59:03.445764Z","links":{"self":"/v1/jobs/job_b5ca4926490c435eac915268a1ac5d6a","cancel":"/v1/jobs/job_b5ca4926490c435eac915268a1ac5d6a/cancel"}}
   ```

   `job_id` одночасно є `collection_id`.

3. Перевірте стан збору (підставте свій ідентифікатор):

   ```powershell
   curl.exe -s http://127.0.0.1:18101/v1/collections/job_b5ca4926490c435eac915268a1ac5d6a
   ```

   Уривок відповіді (без `effective_limits`), відформатовано:

   ```json
   {
     "collection_id": "job_b5ca4926490c435eac915268a1ac5d6a",
     "status": "succeeded",
     "paused_by_backpressure": false,
     "source_kind": "web",
     "mode": "full",
     "state_key": "testsite-news",
     "created_at": "2026-10-11T09:59:03Z",
     "stats": {
       "discovered": 12,
       "fetched": 14,
       "emitted": 12,
       "acknowledged": 0,
       "unacked": 12,
       "duplicates": 40,
       "skipped_out_of_scope": 36,
       "skipped_robots": 0,
       "not_modified": 0,
       "errors": 0,
       "frontier_size": 0,
       "bytes_fetched": 15318,
       "by_strategy": {"news-feed": 9, "news-pages": 3}
     },
     "source_id": "testsite",
     "finished_at": "2026-10-11T09:59:04Z"
   }
   ```

   `fetched` (14) більше за `emitted` (12): стрічка RSS і `/news/` як сторінка-початок пошуку — навігаційні документи, вони не видаються матеріалами. `by_strategy` рахує URL за `strategy_id`, яка першою їх знайшла. `effective_limits` у повній відповіді — ліміти після успадкування ([configuration.md](configuration.md#успадкування-лімітів)).

## Прочитати й підтвердити матеріали

Матеріали читаються сторінками. Параметр `after` — курсор останнього обробленого матеріалу; запит з `after` **підтверджує** все до нього включно, і ці матеріали видаляються з буфера колектора.

1. Перша сторінка з трьох матеріалів:

   ```powershell
   curl.exe -s "http://127.0.0.1:18101/v1/collections/job_b5ca4926490c435eac915268a1ac5d6a/materials?limit=3"
   ```

   У відповіді `items`, `next_cursor: "c_0000000000000003"`, `end_of_stream: false`, `collection_status: "succeeded"`. Перший матеріал знайшла стрічка: `discovery.strategy: "feed"`, `discovery.parent_url: "http://127.0.0.1:18110/feeds/news.rss"`.

2. Наступна сторінка — з курсором попередньої. Це підтверджує перші три матеріали:

   ```powershell
   curl.exe -s "http://127.0.0.1:18101/v1/collections/job_b5ca4926490c435eac915268a1ac5d6a/materials?after=c_0000000000000003&limit=2"
   ```

   Уривок першого елемента, відформатовано, `content` скорочено:

   ```json
   {
     "material_id": "web:5c3af7eb0419f822131757a6e9aecc6f",
     "locator": {"canonical_url": "http://127.0.0.1:18110/news/2026/warranty-update"},
     "published_at": "2026-09-07T09:00:00Z",
     "edited_at": "2026-09-07T09:00:00Z",
     "discovery": {"depth": 1, "parent_url": "http://127.0.0.1:18110/feeds/news.rss", "priority": 0, "strategy": "feed"},
     "collector": {"collection_id": "job_b5ca4926490c435eac915268a1ac5d6a", "name": "web-collector", "version": "0.1.0"},
     "metadata": {"title": "Warranty terms updated | Jane Test Shop"}
   }
   ```

   Після цього запиту `GET /v1/collections/{id}` показує `acknowledged: 3`, `unacked: 9`.

3. Дочитайте решту (`after=c_0000000000000005&limit=50` повертає 7 матеріалів і `end_of_stream: true`) і підтвердіть останню сторінку ще одним запитом з її курсором:

   ```powershell
   curl.exe -s "http://127.0.0.1:18101/v1/collections/job_b5ca4926490c435eac915268a1ac5d6a/materials?after=c_0000000000000012"
   ```

   ```json
   {"items":[],"next_cursor":"c_0000000000000012","end_of_stream":true,"collection_status":"succeeded"}
   ```

Параметр `wait_ms` (до `collector.max_wait_ms`, типово 30 000) вмикає довге опитування: відповідь чекає нових матеріалів, поки збір триває.

## Повторний збір

1. Подивіться збережений стан ключа `testsite-news`:

   ```powershell
   curl.exe -s http://127.0.0.1:18101/v1/states/testsite-news
   ```

   ```json
   {"state_key":"testsite-news","collector":"web","updated_at":"2026-10-11T09:59:04Z","known_urls":14,"frontier_size":0,"cursors":{"news-feed":{"stats":{"entries":18,"feeds_discovered":1,"feeds_read":2}}}}
   ```

2. Запустіть той самий збір у режимі `incremental`: у `collection.json` замініть `"mode": "full"` на `"mode": "incremental"` і надішліть його з новим ключем, наприклад `Idempotency-Key: doc-news-3`. Статистика завершеного збору:

   ```json
   {"discovered": 12, "fetched": 13, "emitted": 0, "acknowledged": 0, "unacked": 0, "duplicates": 31, "skipped_out_of_scope": 36, "skipped_robots": 0, "not_modified": 12, "errors": 0, "frontier_size": 0, "bytes_fetched": 2323, "by_strategy": {"news-feed": 9, "news-pages": 3}}
   ```

   Усі 12 сторінок не змінилися: `revisit.mode: if_changed` надіслав умовні запити (ETag), сайт відповів `304`, нових матеріалів немає (`emitted: 0`). Стрічку RSS прочитано повністю, як і в кожному зборі.

3. Повтор `POST /v1/collections` з ключем `doc-news-3`, але іншим тілом дає `422 idempotency_key_reused`.

## Помилки збору

Помилки окремих URL не зупиняють збір. Запит із явними URL (`urls` у запиті замінюють стратегії правил):

```json
{
  "source_kind": "web",
  "urls": ["http://127.0.0.1:18110/missing-page", "http://127.0.0.1:18110/private/admin", "http://127.0.0.1:18110/about"],
  "rules": {"collector": "web", "scope": {"allowed_domains": ["127.0.0.1"]}, "strategies": [{"type": "seed_list", "urls": ["http://127.0.0.1:18110/"]}]}
}
```

Збір завершується `succeeded` з одним матеріалом (`/about`), а `GET /v1/collections/{id}/errors` повертає:

```json
{
  "items": [
    {"at": "2026-10-11T10:00:41Z", "code": "access_denied_by_policy", "message": "disallowed by robots.txt", "url": "http://127.0.0.1:18110/private/admin"},
    {"at": "2026-10-11T10:00:42Z", "attempts": 1, "code": "not_found", "http_status": 404, "message": "HTTP 404", "url": "http://127.0.0.1:18110/missing-page"}
  ],
  "next_cursor": null
}
```

Скасування: `POST /v1/jobs/{job_id}/cancel` переводить job у `cancelling`, далі збір стає `cancelled`; уже видані матеріали лишаються доступними до підтвердження.

## Прибирання

1. Зупиніть колектор і тестовий сайт: `Ctrl+C` у їхніх терміналах.
2. Видаліть стан. Команда видаляє **весь** власний стан колектора в цьому каталозі: збори, буфери матеріалів, історію URL усіх `state_key`, підключення:

   ```powershell
   uv run python -c "import shutil; shutil.rmtree('.jane/web-collector', ignore_errors=True)"
   ```

3. Видаліть створені файли запитів `fetch.json` і `collection.json`.
