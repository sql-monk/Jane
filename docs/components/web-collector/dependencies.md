# Web Collector: залежності

Що потрібно Web Collector для роботи, які залежності опційні та як сервіс поводиться, коли залежність недоступна. Версії — з `services/web-collector/pyproject.toml` і `uv.lock` ревізії `48389a3`.

## Зміст

- [Обов'язкові](#обовязкові)
- [Опційні](#опційні)
- [Рендеринг JavaScript](#рендеринг-javascript)
- [Поведінка за недоступності](#поведінка-за-недоступності)

## Обов'язкові

| Залежність | Версія | Призначення |
|---|---|---|
| Python | ≥ 3.12 (образ `python:3.12-slim`) | середовище виконання |
| `jane-kit` | workspace | конфігурація й ліміти, помилки, job, Idempotency-Key, автентифікація, метрики, правила |
| `jane-contracts` | workspace | протокол стратегій `jane_contracts.discovery` |
| `httpx` | ≥ 0.27 (у lock — 0.28.1) | HTTP-клієнт |
| `lxml`, `cssselect` | ≥ 5.3, ≥ 1.2 (у lock — 6.1.3, 1.5.0) | розбір HTML і XML, селектори посилань |
| JSON Schema контрактів | каталог `contracts/` | перевірка запитів і правил; шукається в `JANE_WEB_COLLECTOR_CONTRACTS_DIR`, `JANE_CONTRACTS_DIR` або в checkout |
| Каталог стану | `JANE_WEB_COLLECTOR_STATE_DIR` | файл SQLite `state.db` (WAL), доступний на запис |
| Доступ до сайтів | HTTP/HTTPS | вихідні з'єднання з урахуванням [політики вихідних адрес](configuration.md#безпека-й-підключення) |

Пакет стратегій `services/web-collector/strategies/discovery/` (стратегії `sitemap`, `feed`, `listing`, `url_template`, `api_feed`) завантажується з `JANE_WEB_COLLECTOR_DISCOVERY_PATH`, типово — з checkout; у Docker-образі він скопійований у `/app/strategies/discovery`.

## Опційні

| Залежність | Коли потрібна | Як підключити |
|---|---|---|
| Registry (`registry.v1`) | правила за `rules_ref` з репозиторію | `JANE_WEB_COLLECTOR_REGISTRY_URL`, токен — через `JANE_WEB_COLLECTOR_REGISTRY_TOKEN_ENV` |
| Локальні пакети правил | `rules_ref` без Registry | `JANE_WEB_COLLECTOR_RULES_DIR` з каталогами `<package_id>/<version>/` |
| Транзитне сховище | великі матеріали, `content_delivery: blob` | `JANE_WEB_COLLECTOR_TRANSIT_DIR` (локальний або спільний каталог; посилання `file://`) |
| Playwright і Chromium | `fetch.render_js: true` | extra `render`, див. нижче |
| Пакети стратегій через entry points | стратегії поза репозиторієм | група `jane.web_collector.strategies`, див. [strategies/discovery/README.md](../../../services/web-collector/strategies/discovery/README.md) |
| Секрети підключень | сайти з автентифікацією | змінні з префіксом `JANE_SECRET_` або файли в `/run/secrets` |

Orchestrator, Storage, Handler Runtime і PostgreSQL колектору не потрібні.

## Рендеринг JavaScript

Рендеринг використовує Playwright (`playwright>=1.49`, у lock — 1.63.0) і headless Chromium.

- Локально: Playwright входить до dev-групи workspace, тому після `uv sync --all-packages` достатньо встановити браузер:

  ```powershell
  uv run playwright install chromium
  ```

- Окреме встановлення сервісу: `uv sync --package jane-web-collector --extra render`, потім та сама команда встановлення браузера.
- Docker: образ зі збіркою `--build-arg EXTRAS="--extra render"` містить Chromium і системні бібліотеки (приблизно на 1 ГБ більший):

  ```powershell
  docker build -f services/web-collector/Dockerfile --build-arg EXTRAS="--extra render" -t jane-web-collector .
  ```

  Збірку образу з рендерингом у цій ревізії не перевіряли.

Чи доступний рендеринг, показує `capabilities.render_js` у `GET /v1/info`.

## Поведінка за недоступності

| Що недоступно | Поведінка |
|---|---|
| Сайт (мережа, 5xx, 429) | повтори за `retries.*`; потім помилка URL `source_unavailable` або `rate_limited` у `/errors`, збір триває |
| `robots.txt` відповідає 5xx або не відповідає | усі URL хоста заборонені до спливання `collector.robots_cache_ttl_seconds` (RFC 9309); 4xx — усе дозволено |
| Сайт просить чекати довше за `collector.max_retry_after_seconds` | URL завершується `rate_limited`; стратегії припиняють запити в цьому зборі |
| Registry не відповідає | запит із `rules_ref` — `502 upstream_unavailable` (повторюваний); inline-правила працюють |
| Пакет правил не знайдено (ні в `RULES_DIR`, ні в Registry) | `422 validation_failed`; невідповідність дайджесту — `digest_mismatch` |
| Транзитне сховище не налаштоване | `content_delivery: blob` — `422 validation_failed`; у режимі `auto` матеріал понад `transfer.inline_max_bytes` — помилка URL `limit_exceeded` |
| Chromium або Playwright | URL з `render_js` завершуються `not_implemented` (у `POST /v1/fetches` — `501`), без тихого звичайного завантаження |
| Файл стану заблоковано іншим процесом довше за `STATE_BUSY_TIMEOUT_MS` | `503 service_unavailable` із `Retry-After`; запит можна повторити |
| Каталог стану недоступний на запис | сервіс не стартує |
| Пакет стратегій не імпортується | сервіс стартує з вбудованими `seed_list` і `recursive`; причина — у `capabilities.strategy_load_errors` і журналі |
