# Telegram Collector: публічні типи

## Індекс

- [`jane_telegram_collector.app`](generated/jane_telegram_collector.app.md)
- [`jane_telegram_collector.settings`](generated/jane_telegram_collector.settings.md)
- [`jane_telegram_collector.engine`](generated/jane_telegram_collector.engine.md)
- [`jane_telegram_collector.collector`](generated/jane_telegram_collector.collector.md)
- [`jane_telegram_collector.state`](generated/jane_telegram_collector.state.md)
- [`jane_telegram_collector.stores`](generated/jane_telegram_collector.stores.md)
- [`jane_telegram_collector.connections`](generated/jane_telegram_collector.connections.md)
- [`jane_telegram_collector.client`](generated/jane_telegram_collector.client.md)
- [`jane_telegram_collector.recorded`](generated/jane_telegram_collector.recorded.md)
- [`jane_telegram_collector.telethon_client`](generated/jane_telegram_collector.telethon_client.md)
- [`jane_telegram_collector.rules`](generated/jane_telegram_collector.rules.md)
- [`jane_telegram_collector.materials`](generated/jane_telegram_collector.materials.md)
- [`jane_telegram_collector.testing`](generated/jane_telegram_collector.testing.md)

## Умови використання

| Тип | Умови |
|---|---|
| `Settings` | Lease validator, own client backend та секретна policy |
| `Engine` | Валідує source_kind=telegram, правила та account |
| `TelegramRun` | History/changes, dedup, media і bounded retries |
| `StateStore` | Власний SQLite, lease/fence, cursors та seen revisions |
| `TelegramClient`, `ClientFactory` | Protocol для стороннього backend |
| `RecordedClient`, `Recording` | JSON replay; Recording.post/edit зберігає events |
| `FloodWait` | Seconds до наступної спроби |
| `AccountUnauthorized`, `ChannelUnavailable`, `ClientUnavailable` | Окремі категорії відмови |


Згенеровані декларації містять bases, сигнатури, типи аргументів і публічні члени. Instance attributes конфігурації й стану mutable; read-only properties не мають setter. Сховища відкриваються/закриваються власником застосунку; прямі виклики внутрішнього Engine потребують усіх dependencies.

## Приклади

[Фабрика Settings/build_app](../../quickstart.md), [HTTP-клієнт](../../integration.md), [defaults та bounds](../../configuration.md).
