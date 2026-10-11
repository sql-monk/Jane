# Web Collector: публічні типи

## Індекс

- [`jane_web_collector.app`](generated/jane_web_collector.app.md)
- [`jane_web_collector.settings`](generated/jane_web_collector.settings.md)
- [`jane_web_collector.engine`](generated/jane_web_collector.engine.md)
- [`jane_web_collector.crawler`](generated/jane_web_collector.crawler.md)
- [`jane_web_collector.fetcher`](generated/jane_web_collector.fetcher.md)
- [`jane_web_collector.state`](generated/jane_web_collector.state.md)
- [`jane_web_collector.stores`](generated/jane_web_collector.stores.md)
- [`jane_web_collector.rules`](generated/jane_web_collector.rules.md)
- [`jane_web_collector.materials`](generated/jane_web_collector.materials.md)
- [`jane_web_collector.connections`](generated/jane_web_collector.connections.md)
- [`jane_web_collector.urls`](generated/jane_web_collector.urls.md)
- [`jane_web_collector.robots`](generated/jane_web_collector.robots.md)
- [`jane_web_collector.host_limits`](generated/jane_web_collector.host_limits.md)
- [`jane_web_collector.shared_hosts`](generated/jane_web_collector.shared_hosts.md)
- [`jane_web_collector.render`](generated/jane_web_collector.render.md)
- [`jane_web_collector.egress`](generated/jane_web_collector.egress.md)
- [`jane_web_collector.testing`](generated/jane_web_collector.testing.md)
- [`jane_web_collector.discovery.builtin`](generated/jane_web_collector.discovery.builtin.md)
- [`jane_web_collector.discovery.links`](generated/jane_web_collector.discovery.links.md)
- [`jane_web_collector.discovery.registry`](generated/jane_web_collector.discovery.registry.md)

## Умови використання

| Тип | Поведінка |
|---|---|
| `Settings` | Перевіряє lease та connection policy; ValidationError при помилці |
| `Engine` | fetch/start_collection/resume; валідує source_kind=web |
| `StateStore` | SQLite transactions; writes зі Fence захищають ownership |
| `Fetcher` | HttpResult або FetchError; timeout/retry bounded |
| `HostLimiter` | Загальний для instances із shared state |
| `Renderer` | Опційний Chromium; без browser немає plain fallback |
| `SeedListStrategy`, `RecursiveStrategy` | seeds/on_fetched і snapshot/restore |
| `TransitStore` | FileTransitStore для великих матеріалів |


Згенеровані декларації містять bases, сигнатури, типи аргументів і публічні члени. Instance attributes конфігурації й стану mutable; read-only properties не мають setter. Сховища відкриваються/закриваються власником застосунку; прямі виклики внутрішнього Engine потребують усіх dependencies.

## Приклади

[Фабрика Settings/build_app](../../quickstart.md), [HTTP-клієнт](../../integration.md), [defaults та bounds](../../configuration.md).
