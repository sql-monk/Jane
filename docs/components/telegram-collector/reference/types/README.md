# Типи й члени: Telegram Collector

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector](../../../../../services/telegram-collector/src/jane_telegram_collector). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_telegram_collector`](jane_telegram_collector.md) | 0 | 0 | Telegram Collector of the Jane platform. |
| [`jane_telegram_collector.__main__`](jane_telegram_collector.__main__.md) | 0 | 1 | Entry point: ``python -m jane_telegram_collector`` (host/port from ``JANE_TELEGRAM_COLLECTOR_HOST/PORT``). |
| [`jane_telegram_collector.app`](jane_telegram_collector.app.md) | 0 | 2 | HTTP API ``collector.v1`` of the Telegram Collector (``contracts/openapi/collector.v1.yaml``). |
| [`jane_telegram_collector.client`](jane_telegram_collector.client.md) | 12 | 1 | Telegram client abstraction: the collector talks to Telegram only through :class:`TelegramClient`. |
| [`jane_telegram_collector.collector`](jane_telegram_collector.collector.md) | 2 | 2 | Collection run: one :class:`TelegramRun` per collection (history, new messages, edits, cursors). |
| [`jane_telegram_collector.connections`](jane_telegram_collector.connections.md) | 1 | 5 | Managed connections (``/v1/connections``, ADR-0006): the Telegram account the collector works as. |
| [`jane_telegram_collector.engine`](jane_telegram_collector.engine.md) | 1 | 0 | Service core: collections (start, resume after restart or takeover, cancellation), one-shot fetch, housekeeping. |
| [`jane_telegram_collector.materials`](jane_telegram_collector.materials.md) | 2 | 6 | Material documents for Telegram messages (``material.schema.json``) and content delivery (ADR-0004). |
| [`jane_telegram_collector.recorded`](jane_telegram_collector.recorded.md) | 3 | 0 | Recorded Telegram backend: channels replayed from JSON recordings (tests, demos, offline replays). |
| [`jane_telegram_collector.rules`](jane_telegram_collector.rules.md) | 2 | 1 | Collector rules of the Telegram Collector: what this implementation supports, on top of the shared parts. |
| [`jane_telegram_collector.settings`](jane_telegram_collector.settings.md) | 9 | 4 | Settings and limits of the Telegram Collector. Every limit has a safe default documented in README.md. |
| [`jane_telegram_collector.state`](jane_telegram_collector.state.md) | 3 | 0 | Own state store of the Telegram Collector (SQLite, WAL): nobody else reads these tables (ADR-0009). |
| [`jane_telegram_collector.stores`](jane_telegram_collector.stores.md) | 2 | 0 | jane-kit's shared SQLite ``JobStore`` / ``IdempotencyStore`` on the collector's own state file (R17). |
| [`jane_telegram_collector.telethon_client`](jane_telegram_collector.telethon_client.md) | 1 | 0 | MTProto backend on Telethon (optional extra ``telethon``: ``uv sync --package jane-telegram-collector --extra telethon``). |
| [`jane_telegram_collector.testing`](jane_telegram_collector.testing.md) | 1 | 9 | Test helpers for the Telegram Collector API (this service's tests; usable by WP-13 too). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`AccountUnauthorized`](jane_telegram_collector.client.md#клас-accountunauthorized) | виняток | `jane_telegram_collector.client` |
| [`build_app`](jane_telegram_collector.app.md#функція-build_app) | функція | `jane_telegram_collector.app` |
| [`build_material`](jane_telegram_collector.materials.md#функція-build_material) | функція | `jane_telegram_collector.materials` |
| [`ChangeBatch`](jane_telegram_collector.client.md#клас-changebatch) | dataclass (незмінний) | `jane_telegram_collector.client` |
| [`channel_key`](jane_telegram_collector.collector.md#функція-channel_key) | функція | `jane_telegram_collector.collector` |
| [`ChannelInfo`](jane_telegram_collector.client.md#клас-channelinfo) | dataclass (незмінний) | `jane_telegram_collector.client` |
| [`ChannelUnavailable`](jane_telegram_collector.client.md#клас-channelunavailable) | виняток | `jane_telegram_collector.client` |
| [`check_params`](jane_telegram_collector.connections.md#функція-check_params) | функція | `jane_telegram_collector.connections` |
| [`ClientFactory`](jane_telegram_collector.client.md#клас-clientfactory) | протокол | `jane_telegram_collector.client` |
| [`ClientUnavailable`](jane_telegram_collector.client.md#клас-clientunavailable) | виняток | `jane_telegram_collector.client` |
| [`Collector`](jane_telegram_collector.settings.md#клас-collector) | клас | `jane_telegram_collector.settings` |
| [`connection_etag`](jane_telegram_collector.connections.md#функція-connection_etag) | функція | `jane_telegram_collector.connections` |
| [`ConnectionPolicy`](jane_telegram_collector.connections.md#клас-connectionpolicy) | dataclass (незмінний) | `jane_telegram_collector.connections` |
| [`contract_layer`](jane_telegram_collector.settings.md#функція-contract_layer) | функція | `jane_telegram_collector.settings` |
| [`ContractSchemas`](jane_telegram_collector.rules.md#клас-contractschemas) | клас | `jane_telegram_collector.rules` |
| [`Delivery`](jane_telegram_collector.materials.md#клас-delivery) | клас | `jane_telegram_collector.materials` |
| [`drain`](jane_telegram_collector.testing.md#функція-drain) | функція | `jane_telegram_collector.testing` |
| [`Engine`](jane_telegram_collector.engine.md#клас-engine) | клас | `jane_telegram_collector.engine` |
| [`errors`](jane_telegram_collector.testing.md#функція-errors) | функція | `jane_telegram_collector.testing` |
| [`FloodWait`](jane_telegram_collector.client.md#клас-floodwait) | виняток | `jane_telegram_collector.client` |
| [`free_port`](jane_telegram_collector.testing.md#функція-free_port) | функція | `jane_telegram_collector.testing` |
| [`LeaseLost`](jane_telegram_collector.state.md#клас-leaselost) | виняток | `jane_telegram_collector.state` |
| [`load_factory`](jane_telegram_collector.client.md#функція-load_factory) | функція | `jane_telegram_collector.client` |
| [`main`](jane_telegram_collector.__main__.md#функція-main) | функція | `jane_telegram_collector.__main__` |
| [`make_channel`](jane_telegram_collector.testing.md#функція-make_channel) | функція | `jane_telegram_collector.testing` |
| [`make_settings`](jane_telegram_collector.testing.md#функція-make_settings) | функція | `jane_telegram_collector.testing` |
| [`message_sequence`](jane_telegram_collector.materials.md#функція-message_sequence) | функція | `jane_telegram_collector.materials` |
| [`message_sha`](jane_telegram_collector.materials.md#функція-message_sha) | функція | `jane_telegram_collector.materials` |
| [`new_observation_id`](jane_telegram_collector.materials.md#функція-new_observation_id) | функція | `jane_telegram_collector.materials` |
| [`new_stats`](jane_telegram_collector.collector.md#функція-new_stats) | функція | `jane_telegram_collector.collector` |
| [`page`](jane_telegram_collector.testing.md#функція-page) | функція | `jane_telegram_collector.testing` |
| [`parse_host`](jane_telegram_collector.connections.md#функція-parse_host) | функція | `jane_telegram_collector.connections` |
| [`platform_layers`](jane_telegram_collector.settings.md#функція-platform_layers) | функція | `jane_telegram_collector.settings` |
| [`Queue`](jane_telegram_collector.settings.md#клас-queue) | клас | `jane_telegram_collector.settings` |
| [`Rate`](jane_telegram_collector.settings.md#клас-rate) | клас | `jane_telegram_collector.settings` |
| [`RecordedClient`](jane_telegram_collector.recorded.md#клас-recordedclient) | клас | `jane_telegram_collector.recorded` |
| [`RecordedClientFactory`](jane_telegram_collector.recorded.md#клас-recordedclientfactory) | клас | `jane_telegram_collector.recorded` |
| [`Recording`](jane_telegram_collector.recorded.md#клас-recording) | dataclass | `jane_telegram_collector.recorded` |
| [`resolve_account`](jane_telegram_collector.connections.md#функція-resolve_account) | функція | `jane_telegram_collector.connections` |
| [`resolve_service_limits`](jane_telegram_collector.settings.md#функція-resolve_service_limits) | функція | `jane_telegram_collector.settings` |
| [`resolved_map`](jane_telegram_collector.connections.md#функція-resolved_map) | функція | `jane_telegram_collector.connections` |
| [`ResolvedAccount`](jane_telegram_collector.client.md#клас-resolvedaccount) | dataclass (незмінний) | `jane_telegram_collector.client` |
| [`Retries`](jane_telegram_collector.settings.md#клас-retries) | клас | `jane_telegram_collector.settings` |
| [`revision_sequence`](jane_telegram_collector.materials.md#функція-revision_sequence) | функція | `jane_telegram_collector.materials` |
| [`rfc3339`](jane_telegram_collector.materials.md#функція-rfc3339) | функція | `jane_telegram_collector.materials` |
| [`RulesLoader`](jane_telegram_collector.rules.md#клас-rulesloader) | клас | `jane_telegram_collector.rules` |
| [`RunDeps`](jane_telegram_collector.collector.md#клас-rundeps) | dataclass | `jane_telegram_collector.collector` |
| [`ServiceLimits`](jane_telegram_collector.settings.md#клас-servicelimits) | клас | `jane_telegram_collector.settings` |
| [`ServiceProcess`](jane_telegram_collector.testing.md#клас-serviceprocess) | dataclass | `jane_telegram_collector.testing` |
| [`Settings`](jane_telegram_collector.settings.md#клас-settings) | модель Pydantic | `jane_telegram_collector.settings` |
| [`SqliteIdempotencyStore`](jane_telegram_collector.stores.md#клас-sqliteidempotencystore) | клас | `jane_telegram_collector.stores` |
| [`SqliteJobStore`](jane_telegram_collector.stores.md#клас-sqlitejobstore) | клас | `jane_telegram_collector.stores` |
| [`start`](jane_telegram_collector.testing.md#функція-start) | функція | `jane_telegram_collector.testing` |
| [`state_store_busy`](jane_telegram_collector.app.md#функція-state_store_busy) | функція | `jane_telegram_collector.app` |
| [`StateFileTooNew`](jane_telegram_collector.state.md#клас-statefiletoonew) | виняток | `jane_telegram_collector.state` |
| [`StateStore`](jane_telegram_collector.state.md#клас-statestore) | клас | `jane_telegram_collector.state` |
| [`Telegram`](jane_telegram_collector.settings.md#клас-telegram) | клас | `jane_telegram_collector.settings` |
| [`telegram_rules`](jane_telegram_collector.testing.md#функція-telegram_rules) | функція | `jane_telegram_collector.testing` |
| [`TelegramClient`](jane_telegram_collector.client.md#клас-telegramclient) | протокол | `jane_telegram_collector.client` |
| [`TelegramError`](jane_telegram_collector.client.md#клас-telegramerror) | виняток | `jane_telegram_collector.client` |
| [`TelegramRun`](jane_telegram_collector.collector.md#клас-telegramrun) | клас | `jane_telegram_collector.collector` |
| [`TelethonClientFactory`](jane_telegram_collector.telethon_client.md#клас-telethonclientfactory) | клас | `jane_telegram_collector.telethon_client` |
| [`TgMedia`](jane_telegram_collector.client.md#клас-tgmedia) | dataclass (незмінний) | `jane_telegram_collector.client` |
| [`TgMessage`](jane_telegram_collector.client.md#клас-tgmessage) | dataclass (незмінний) | `jane_telegram_collector.client` |
| [`Timeouts`](jane_telegram_collector.settings.md#клас-timeouts) | клас | `jane_telegram_collector.settings` |
| [`to_contract`](jane_telegram_collector.settings.md#функція-to_contract) | функція | `jane_telegram_collector.settings` |
| [`Transfer`](jane_telegram_collector.settings.md#клас-transfer) | клас | `jane_telegram_collector.settings` |
| [`TransitStore`](jane_telegram_collector.materials.md#клас-transitstore) | клас | `jane_telegram_collector.materials` |
| [`validate_rules`](jane_telegram_collector.rules.md#функція-validate_rules) | функція | `jane_telegram_collector.rules` |
| [`wait_done`](jane_telegram_collector.testing.md#функція-wait_done) | функція | `jane_telegram_collector.testing` |
