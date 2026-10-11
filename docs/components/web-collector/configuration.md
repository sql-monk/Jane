# Web Collector: налаштування

Префікс — `JANE_WEB_COLLECTOR_`; вкладені settings і limits розділяються `__`. [Settings](../../../services/web-collector/src/jane_web_collector/settings.py) є фактичним джерелом default та validators.

## Параметри модуля

| Поле | Default | Призначення |
|---|---|---|
| `service_name`, `port` | `web-collector`, `8101` | Ідентифікація та HTTP |
| `state_dir` | `.jane/web-collector` | SQLite state.db |
| `transit_dir` | `null` | Великі матеріали file blobs |
| `rules_dir`, `registry_url`, `registry_token_env` | `null` | Локальні/віддалені пакети правил; token env — назва змінної |
| `secret_env_prefix` | `JANE_SECRET_` | Дозволені env references |
| `secret_files_dir` | `/run/secrets` | Корінь file references |
| `connection_origin_allowlist` | `[]` | Точні HTTP(S) origins для credentials; пусто — заборона |
| `egress_deny_link_local` | `true` | Заборона link-local після DNS та redirects |
| `egress_deny_private` | `false` | Доступ до private/loopback джерел дозволений типово |
| `render_enabled` | `true` | Дозвіл JS rendering |
| `render_wait_until` | `networkidle` | Також domcontentloaded/load |
| `render_block_resource_types` | `["image","media","font"]` | Ресурси, що блокуються браузером |
| `render_browser_executable` | `null` | Власний Chromium executable |
| `render_deny_private` | `true` | Скрипти сторінки не мають довільного доступу до private hosts |
| `contracts_dir`, `discovery_path` | `null` | Автопошук contract/discovery у checkout |
| `user_agent` | `JaneBot/0.1 (+https://github.com/jane)` | HTTP User-Agent; rules.fetch може перевизначити |
| `lease_seconds` | `30` | Timeout owner lease, мінімум 2 с |
| `heartbeat_interval_ms` | `5000` | Поновлення ownership, мінімум 50 ms |
| `state_busy_timeout_ms` | `10000` | Очікування SQLite lock, мінімум 1 ms |
| `idempotency_lease_ms` | `900000` | Claim убитого процесу, мінімум 1000 ms |

## Спільні параметри

Host типово `127.0.0.1`, log level `INFO`, format `json`, auth mode `none`, metrics enabled/public `true`, health check timeout `2000` ms. Повний перелік процесних та auth fields із типами/defaults — [Jane Kit](../jane-kit/configuration.md).

## Успадкування

Defaults → platform limits file → environment → rules.limits → request.limits. Hard caps можуть лише звужувати значення. Web додатково застосовує strategy limits до URL відповідної стратегії.

Змінні `LIMITS__` використовують назви моделей; файл `limits_file` має форму PlatformLimits (`profile`, `defaults`, `hard_caps`). Contract paths невикористаних груп ignored; невідома назва чи null є помилкою.

## Життєвий цикл конфігурації

Налаштування процесу читаються на старті. Правила та request limits застосовуються до конкретного запуску. Керовані connections змінюються API з ETag/If-Match; секрети задаються references, а не значеннями в API. Перезапуск застосовує нове environment.

Lease constraint: `heartbeat_interval_ms + state_busy_timeout_ms < lease_seconds * 1000`. Типово `5000 + 10000 < 30000`; порушення зупиняє побудову Settings.


## Ліміти

Усі `ServiceLimits` та їхні поля з bounds — [generated settings](reference/types/generated/jane_web_collector.settings.md). Основні групи:

| Група | Defaults |
|---|---|
| concurrency | 4 fetches загалом; 2 на host |
| rate | 1 request/s/host; delay 500 ms; respect_crawl_delay=true |
| crawl | depth 5; pages 5000; bytes 2147483648; material 10485760; redirects 5; links/page 2000; seeds/frontier 100000; revisit 86400 с |
| timeouts | connect 10000 ms; request 30000 ms |
| retries | attempts 3; initial 1000 ms; max 60000 ms; multiplier 2; jitter=true |
| queue | 500 unacked materials |
| transfer | inline 262144 bytes; transit TTL 604800 с |
| jobs/idempotency/page | [Спільні defaults](../jane-kit/configuration.md#успадковані-ліміти) |
| collector | wait 30000 ms; robots TTL 3600 с і max 512000 bytes; retry-after cap 300 с; backpressure poll 1000 ms; long poll 100 ms; GC 3600 с |
| shared hosts | enabled=true; poll 100 ms; TTL 120 с; prune interval 60 с |
| render | timeout 30000 ms; extra wait 0; pages 2; transfer 52428800 bytes; launch/close 30000 ms |

Для shared-host TTL додатково перевіряється `TTL * 2/3 > state_busy_timeout_ms/1000`. Backoff maximum не може бути нижчим за initial.

```json
{
  "profile": "small-web",
  "defaults": {"concurrency": {"max_parallel_fetches": 2}},
  "hard_caps": {"crawl": {"max_pages_per_run": 100}}
}
```

Збережіть цей JSON як файл та передайте його шлях у `JANE_WEB_COLLECTOR_LIMITS_FILE`. У PowerShell:

```powershell
$env:JANE_WEB_COLLECTOR_LIMITS__CONCURRENCY__MAX_PARALLEL_FETCHES = "2"
```

У Bash на Linux:

```bash
export JANE_WEB_COLLECTOR_LIMITS__CONCURRENCY__MAX_PARALLEL_FETCHES=2
```
