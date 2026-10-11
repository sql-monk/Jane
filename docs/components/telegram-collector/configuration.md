# Telegram Collector: налаштування

Префікс — `JANE_TELEGRAM_COLLECTOR_`; nested delimiter — `__`.

## Параметри модуля

| Поле | Default | Призначення |
|---|---|---|
| `service_name`, `port` | `telegram-collector`, `8102` | Ідентифікація й HTTP |
| `state_dir` | `.jane/telegram-collector` | Власний state.db |
| `client_backend` | `recorded` | recorded, telethon або module:factory |
| `recordings_dir` | `null` | JSON recordings, обов’язковий для replay |
| `default_account_connection_id` | `null` | Account без ID у rules |
| `transit_dir` | `null` | Великі content/media |
| `rules_dir`, `registry_url`, `registry_token_env` | `null` | Джерело rules_ref, назва env token |
| `contracts_dir` | `null` | Автопошук contract root |
| `secret_env_prefix` | `JANE_SECRET_` | Дозволені env secret refs |
| `secret_files_dir` | `/run/secrets` | Корінь file refs |
| `telegram_host_allowlist` | `[]` | Дозволені host-like params; пусто — none |
| `lease_seconds` | `30` | Ownership timeout, мінімум 2 с |
| `heartbeat_interval_ms` | `5000` | Поновлення, мінімум 50 ms |
| `state_busy_timeout_ms` | `10000` | Очікування SQLite lock |
| `idempotency_lease_ms` | `900000` | Claim stale instance, мінімум 1000 ms |

## Спільні параметри

Host типово `127.0.0.1`, log level `INFO`, format `json`, auth mode `none`, metrics enabled/public `true`, health check timeout `2000` ms. Повний перелік процесних та auth fields із типами/defaults — [Jane Kit](../jane-kit/configuration.md).

## Успадкування

Defaults → platform limits file → environment → rules.limits → request.limits. Hard caps можуть лише звужувати значення.

Змінні `LIMITS__` використовують назви моделей; файл `limits_file` має форму PlatformLimits (`profile`, `defaults`, `hard_caps`). Contract paths невикористаних груп ignored; невідома назва чи null є помилкою.

## Життєвий цикл конфігурації

Налаштування процесу читаються на старті. Правила та request limits застосовуються до конкретного запуску. Керовані connections змінюються API з ETag/If-Match; секрети задаються references, а не значеннями в API. Перезапуск застосовує нове environment.

Lease constraint: `heartbeat_interval_ms + state_busy_timeout_ms < lease_seconds * 1000`. Типово `5000 + 10000 < 30000`; порушення зупиняє побудову Settings.


## Ліміти

| Група | Defaults |
|---|---|
| rate | min_delay_ms_per_host=200 |
| timeouts | connect=15000 ms; request=30000 ms |
| retries | attempts=3; initial=1000 ms; max=60000 ms; multiplier=2; jitter=true |
| queue | max_unacked_materials=500 |
| transfer | inline_max_bytes=262144; transit_ttl_seconds=604800 |
| telegram | messages/run=10000; media=20971520 bytes; flood-wait cap=300 с |
| jobs/idempotency/page | [Спільні defaults](../jane-kit/configuration.md#успадковані-ліміти) |
| collector | history_page_size=100; changes_page_size=100; max_wait_ms=30000; long_poll_interval_ms=100; backpressure_poll_ms=1000; gc_interval_seconds=3600 |

Всі типи та validators — [generated settings](reference/types/generated/jane_telegram_collector.settings.md). History page має бути сумісною з Telegram limit; backoff max не менший initial.

## Account connection

`kind=telegram_account` використовує params і secret_refs. Для Telethon потрібні api_id, api_hash та вже авторизована session; точне розташування params/secrets описане [resolve_account](../../../services/telegram-collector/src/jane_telegram_collector/connections.py) і [Telethon factory](../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py).

```json
{
  "connection_id": "tg-main",
  "kind": "telegram_account",
  "params": {"api_id": 12345},
  "secret_refs": {
    "api_hash": "env:JANE_SECRET_TG_API_HASH",
    "session": "env:JANE_SECRET_TG_SESSION"
  }
}
```

12345 — приклад форми api_id; замініть на власний. Не вставляйте api_hash чи session value у JSON. Для локального recorded backend без required_secrets account не потрібен.
