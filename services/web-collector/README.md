# Web Collector

Отримує вебсторінки та інші вебматеріали за правилами колектора й віддає їх як `Material` (ТЗ §3, §5, §6).
Автономний: працює без оркестратора, екстрактора, сервісу збереження й репозиторію (ТЗ §4, критерій 1).
Контракт: [`contracts/openapi/collector.v1.yaml`](../../contracts/openapi/collector.v1.yaml), правила —
[`collector-rules.schema.json`](../../contracts/schemas/collector-rules.schema.json), інтерфейс стратегій —
[`jane_contracts.discovery`](../../contracts/python/src/jane_contracts/discovery.py) і
[`contracts/docs/discovery-strategy.md`](../../contracts/docs/discovery-strategy.md).

Ядро (WP-02): завантаження, нормалізація URL, межі доменів і шляхів, `include`/`exclude`, `robots.txt` і явна
політика власника (`owner_policy`), черга з дедуплікацією та пріоритетами, глибина, повторні відвідування
(`revisit`, умовні запити), ліміти на хост, власне сховище стану й відновлення після kill, реєстр стратегій,
стратегії `seed_list` (явний перелік / головна сторінка) і `recursive`. Решту стратегій додає WP-03.

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
uv run --package jane-web-collector python -m jane_web_collector
curl http://127.0.0.1:8101/v1/health
```

У Docker (контекст — корінь репозиторію; стан — у томі `/var/lib/jane-web-collector`):

```
docker build -f services/web-collector/Dockerfile -t jane-web-collector .
docker run --rm -p 8101:8101 -v jane-wc-state:/var/lib/jane-web-collector jane-web-collector
```

Правило конфігурації (перевіряється на старті, інакше сервіс не запускається):
`HEARTBEAT_INTERVAL_MS + STATE_BUSY_TIMEOUT_MS < LEASE_SECONDS × 1000` — живий власник завжди встигає продовжити
lease, навіть якщо один запис чекав на блокування весь busy timeout.

Кілька екземплярів: кожен процес має власний `JANE_WEB_COLLECTOR_PORT`. Екземпляри з **одним** каталогом стану на
одному вузлі ділять SQLite-файл: збір виконує той, хто тримає lease (`JANE_WEB_COLLECTOR_LEASE_SECONDS`), решта
віддає матеріали, стан і помилки з того самого сховища й підхоплює збір, якщо власник зник. Екземпляри з різними
каталогами — незалежні колектори. Спільного сховища для кількох вузлів (PostgreSQL) у v1 немає — див. «Відомі
обмеження» у звіті WP-02.

## Тести

```
just test web-collector                 # unit + contract + сценарії проти testsite, ~2 хв
just test web-collector -m contract     # лише контрактні
```

Усі сценарії йдуть проти справжнього testsite (`jane_testsite`, WP-01) через HTTP; колектор не мокається.
Тест відновлення (`tests/test_resume_after_kill.py`) і тест автономності (`tests/test_autonomy.py`) запускають
сервіс окремим процесом (`python -m jane_web_collector`) і вбивають його жорстко (SIGKILL / TerminateProcess).
Мок сусіда — лише registry.v1 (`tests/test_rules_sources.py`), відповіді перевіряються за його контрактом.

## Конфігурація

Змінні середовища з префіксом `JANE_WEB_COLLECTOR_`:

| Змінна | Типово | Опис |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8101` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `STATE_DIR` | `.jane/web-collector` (контейнер: `/var/lib/jane-web-collector`) | власне сховище стану (`state.db`, SQLite WAL) |
| `TRANSIT_DIR` | — | транзитне blob-сховище (`file://`) для великих матеріалів; без нього — лише inline |
| `RULES_DIR` | — | локальні пакети правил: `<package_id>/<version>/jane-package.json` + `rules.json` або архів `<package_id>-<version>.zip` |
| `REGISTRY_URL` | — | registry.v1 для `rules_ref` (після `RULES_DIR`) |
| `REGISTRY_TOKEN_ENV` | — | **ім'я** змінної середовища з bearer-токеном до registry (не значення) |
| `CONTRACTS_DIR` | `JANE_CONTRACTS_DIR` або `contracts/` checkout | JSON Schema контрактів для валідації запитів і правил |
| `DISCOVERY_PATH` | `services/web-collector/strategies/discovery` | пакет стратегій WP-03 |
| `USER_AGENT` | `JaneBot/0.1 (+https://github.com/jane)` | типовий User-Agent; перше слово — токен для `robots.txt` |
| `LEASE_SECONDS` | `30` | lease збору; після нього інший екземпляр підхоплює збір |
| `HEARTBEAT_INTERVAL_MS` | `5000` | як часто власник продовжує lease (окрема задача, працює й під час seeds і повільних запитів) і перевіряє скасування |
| `STATE_BUSY_TIMEOUT_MS` | `10000` | скільки запис чекає на блокування SQLite іншим процесом |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | журнали |
| `METRICS_ENABLED` | `true` | `/metrics` |
| `AUTH_MODE` | `none` | значення для `/v1/info` |
| `LIMITS_FILE` | — | `PlatformLimits` (`profile`, `defaults`, `hard_caps`; TOML/JSON/YAML); групи, яких колектор не використовує (`sandbox`, `llm`, `telegram`…), ігноруються |
| `LIMITS__<ГРУПА>__<ПАРАМЕТР>` / `LIMITS__HARD_CAPS__…` | — | перевизначення, напр. `JANE_WEB_COLLECTOR_LIMITS__CRAWL__MAX_DEPTH=3` |

## Ліміти

Рівні: типові значення сервісу → платформа (файл, потім змінні) → джерело (`rules.limits`) → запит
(`CollectionRequest.limits`, `FetchRequest.limits`) → стратегія (`strategies[].limits`, діє для URL цієї стратегії,
зокрема `crawl.max_depth`). `hard_caps` обмежують результат (`min`); `robots.txt` Crawl-delay і `Retry-After` лише
звужують. Ефективні ліміти збору — у `GET /v1/collections/{id}` → `effective_limits`; налаштовані —
у `GET /v1/info` → `limits`.

| Параметр | Типово | Опис |
|---|---|---|
| `concurrency.max_parallel_fetches` | 4 | одночасні завантаження одного збору |
| `concurrency.max_parallel_fetches_per_host` | 2 | одночасні запити до одного хоста |
| `rate.requests_per_second_per_host` | 1 | частота запитів до хоста |
| `rate.min_delay_ms_per_host` | 500 | мінімальний інтервал між запитами до хоста |
| `rate.respect_crawl_delay` | true | враховувати `Crawl-delay` |
| `crawl.max_depth` | 5 | глибина від seeds |
| `crawl.max_pages_per_run` | 5000 | запитів за збір |
| `crawl.max_bytes_per_run` | 2 GiB | байтів за збір |
| `crawl.max_material_bytes` | 10 MiB | більший вміст обрізається з діагностикою `truncated` |
| `crawl.max_redirects` | 5 | переадресацій на URL |
| `crawl.max_links_per_page` | 2000 | кандидатів зі сторінки (на стратегію) |
| `crawl.max_seed_urls` | 100000 | явних URL у запиті й `seed_list` |
| `crawl.max_frontier_size` | 100000 | URL у черзі |
| `crawl.revisit_interval_seconds` | 86400 | для `revisit.mode=interval` |
| `timeouts.connect_timeout_ms` / `request_timeout_ms` | 10000 / 30000 | тайм-аути HTTP |
| `retries.*` | 3 спроби, 1000–60000 мс, ×2, jitter | повтори на 429/5xx/мережі |
| `queue.max_unacked_materials` | 500 | буфер непідтверджених матеріалів; понад — пауза (backpressure) |
| `transfer.inline_max_bytes` | 262144 | більше — blob (або `limit_exceeded` без blob-сховища) |
| `transfer.transit_ttl_seconds` | 604800 | час життя транзитних файлів |
| `jobs.job_retention_seconds` (у контракті, файлі й запиті — `transfer.job_retention_seconds`) | 86400 | після цього збір видаляється (далі 410) |
| `idempotency.idempotency_ttl_seconds` (у контракті — `transfer.idempotency_ttl_seconds`) | 86400 | пам'ять `Idempotency-Key` |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` | 4 / 1000 | зборів одночасно / у черзі на екземпляр |
| `jobs.job_timeout_ms` | 3600000 | максимальна тривалість збору |
| `page.default_page_size` / `max_page_size` | 50 / 500 | сторінки `/materials`, `/errors`, `/connections` |
| `collector.max_wait_ms` | 30000 | стеля long-poll `wait_ms` |
| `collector.robots_cache_ttl_seconds` / `robots_max_bytes` | 3600 / 512000 | кеш і розмір `robots.txt` |
| `collector.max_retry_after_seconds` | 300 | довше очікування (Retry-After, Crawl-delay) → `rate_limited` |
| `collector.backpressure_poll_ms` | 1000 | як часто перевіряється буфер під час паузи backpressure |
| `collector.long_poll_interval_ms` | 100 | як часто `/materials?wait_ms=` шукає нові матеріали |
| `collector.gc_interval_seconds` | 3600 | прибирання прострочених зборів і транзитних файлів (не рідше `job_retention_seconds / 10`) |

## Поведінка

- **Межі**: кожен кандидат нормалізується (`normalization`) і перевіряється за `scope` (схеми, домени,
  піддомени, `path_prefixes`, `include`, `exclude` — виключення мають пріоритет); кожен крок переадресації
  перевіряється знову. `mailto:`, `tel:`, `javascript:` відкидаються.
- **robots.txt**: RFC 9309 (групи за токеном, `*`/`$`, найдовший збіг, 4xx → дозволено, 5xx/мережа → заборонено),
  кешується на збір. `robots.mode=owner_policy` (з `confirmed_owner` і обґрунтуванням у правилах) — явна політика
  для власного ресурсу: `robots.txt` не читається.
- **Дедуплікація й цикли**: ключ черги — канонічний URL; переадресація на вже відомий URL не завантажується вдруге;
  `<link rel=canonical>` (якщо `dedup.use_link_rel_canonical`) теж зводить дублікати. `dedup.key=canonical_url_and_content`
  видає матеріал лише за зміни вмісту відносно попереднього спостереження.
- **Пріоритет** = перший збіг `priorities` + `priority` стратегії + `priority` кандидата; `sections` → `discovery.section`.
- **Повторні відвідування** (історія URL у просторі `state_key`): `mode=full` — усе завантажується наново (нові
  спостереження); `mode=incremental` + `revisit.mode=never` — відомі успішні URL не завантажуються (їхні збережені
  посилання продовжують обхід), `interval` — лише старші за `revisit_interval_seconds`, `if_changed` — умовні
  запити (ETag / If-Modified-Since), 304 не видається. URL, що минулого разу впали (4xx/5xx), пробуються знову.
- **Тайм-аути** `timeouts.connect_timeout_ms` / `request_timeout_ms` застосовуються до кожного запиту з ефективних
  лімітів збору (з урахуванням `rules.limits`, `limits` запиту і `limits` стратегії), а не з платформних типових.
- **Видача**: `GET /v1/collections/{id}/materials?after=<cursor>` підтверджує все до курсора включно
  (курсор, якого сервіс не видавав, — 422);
  непідтверджене видається повторно з тим самим `observation_id`. Коли непідтверджених ≥ `max_unacked_materials`,
  обхід стає на паузу (`paused_by_backpressure: true`).
- **Відновлення**: кожна сторінка фіксується однією транзакцією (нові URL, статус, матеріал, історія, стан стратегій,
  статистика) і перевіряє, що цей прогін досі тримає lease (fencing): прогін, у якого lease перехопили (процес
«завис» довше за lease), не може записати нічого й зупиняється, а його Job не перезаписує Job нового власника.
Після kill новий процес (або інший екземпляр після lease) повертає незавершені URL у чергу й продовжує; перед
завершенням `inflight`, що лишились від чужого прогону, теж повертаються в чергу — `succeeded` неможливий, поки є
`pending`/`inflight`;
  повторно завантажуються лише URL, що були в польоті.
- **`llm_explore`**: валідна за схемою, але колектор її не виконує (ADR-0010): `supported: false`, збір — `validation_failed`.
- **Підключення** (`/v1/connections`, лише `kind=http`): `params.auth_scheme` = `bearer` (`secret_refs.token`),
  `basic` (`username`, `password`) або `header` (`params.header_name`, `secret_refs.value`); секрети — `env:`/`file:`
  у середовищі колектора, у `params` відхиляються (`secret_detected`). Облікові дані не йдуть на інший хост при переадресації.

## Підключення стратегій (WP-03)

Реєстр (`jane_web_collector.discovery.Registry`) збирає стратегії з трьох джерел; повторне `type_name` — помилка:

1. вбудовані: `seed_list`, `recursive`;
2. **пакет WP-03** — каталог `services/web-collector/strategies/discovery/` (інший — `JANE_WEB_COLLECTOR_DISCOVERY_PATH`).
   Ядро імпортує його як пакет `jane_web_collector_discovery` (відносні імпорти всередині працюють) і реєструє
   `STRATEGIES: list[type[DiscoveryStrategy]]` з `__init__.py`. Помилка імпорту не валить сервіс: вона видна в
   журналі й у `/v1/info` → `capabilities.strategy_load_errors`. Docker-образ копіює каталог у `/app/strategies`;
3. entry points групи `jane.web_collector.strategies` (клас або список класів) — для пакетів, встановлених поруч.

Що дає ядро стратегії (`StrategyContext`, реалізує `DiscoveryContext`):

- `ctx.fetch(url, kind=..., conditional=True)` — через ті самі scope, robots, ліміти, переадресації й бюджет.
  Повертає `FetchedResource` (зокрема з 4xx-статусом — корисно для `url_template`), `None` для 304, для URL, уже
  отриманого в цьому процесі, або для вже виданого матеріалу; `FetchRejected` — `out_of_scope`,
  `access_denied_by_policy`, `limit_exceeded`. Ресурс, отриманий через `ctx.fetch`, передається в `on_fetched`
  усіх **інших** стратегій. Навігаційні документи після рестарту можна отримати знову (стан — у `snapshot()`).
- `on_fetched` викликається для кожної HTTP-відповіді з черги (будь-який статус; `resource.strategy_id` — хто
  запропонував URL). Кандидати з `on_fetched` отримують `depth = resource.depth + 1`.
- `ctx.extract_links(resource, LinkSelector(...))` — css / xpath / rel через lxml (залежності `lxml`, `cssselect`
  уже є); `ctx.normalize`, `ctx.in_scope`, `ctx.section_for`, `ctx.limits` (ефективні, з `limits` стратегії),
  `ctx.is_cancelled()`.
- `snapshot()` зберігається після кожної сторінки разом із чергою; `restore()` — при відновленні. Непорожні
  знімки також видно в `GET /v1/states/{state_key}` → `cursors`.

Тести WP-03 можуть узяти пакет так само, як ядро: `load_discovery_package(path)` з
`jane_web_collector.discovery`, і допоміжні засоби `jane_web_collector.testing` (`web_rules`, `start`, `drain`,
`FAST_LIMITS`, `make_settings`). Приклад плагіна — `tests/test_registry.py`. Нові залежності для стратегій
додаються в `pyproject.toml` сервісу — це область WP-02 (запит через координатора).

## Приклад виклику зі стороннього застосунку

```python
import httpx

rules = {
    "collector": "web",
    "scope": {"allowed_domains": ["shop.example.test"], "exclude": [{"value": "*/calendar/**"}]},
    "strategies": [{"type": "seed_list", "urls": ["https://shop.example.test/"]}, {"type": "recursive"}],
    "normalization": {"strip_query_params": ["utm_*"]},
}
with httpx.Client(base_url="http://127.0.0.1:8101") as api:
    job = api.post(
        "/v1/collections",
        json={"source_kind": "web", "source_id": "shop", "rules": rules},
        headers={"Idempotency-Key": "shop-crawl-1"},
    ).json()
    after = None
    while True:
        page = api.get(
            f"/v1/collections/{job['job_id']}/materials",
            params={"wait_ms": 5000, **({"after": after} if after else {})},
        ).json()
        for material in page["items"]:
            print(material["locator"]["canonical_url"], material["content"]["kind"])
        after = page["next_cursor"] or after  # наступний запит підтверджує оброблене
        if page["end_of_stream"]:
            break
```

Одна сторінка синхронно: `POST /v1/fetches {"source_kind": "web", "url": "https://shop.example.test/about"}`.

## Спостережуваність

- `GET /v1/health` (перевірка `state_store`), `GET /v1/info` (стратегії, джерела правил, ліміти).
- `GET /metrics` — Prometheus (`jane_http_requests_total`, `jane_http_request_duration_seconds`).
- Журнали — JSON у stdout із `trace_id`, `job_id`; прогрес збору — `GET /v1/jobs/{id}` → `progress.counters`
  (зокрема `skipped_depth`, `dropped_frontier_full`, `dropped_by_budget`).
