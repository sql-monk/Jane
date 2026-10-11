# Контракти Jane

Публічні API, документи та Python Protocol-и задають межі автономних модулів. Повні схеми залишаються в цьому каталозі; пояснення й приклади зібрані в [довідниках](../docs/reference/README.md).

| Джерело | Зміст |
|---|---|
| [openapi/](openapi/) | HTTP API сервісів, запити, відповіді та статуси |
| [schemas/](schemas/) | JSON Schema документів, матеріалів, результатів і пакетів |
| [python/](python/) | Спільні Protocol-и для Python-реалізацій |
| [examples/](examples/) | Валідні й негативні контрактні приклади |
| [Помилки](docs/errors.md) | Машинні коди, HTTP-статуси й повторні спроби |
| [Власність даних](docs/data-ownership.md) | Хто керує станом і як передає дані |
| [Стратегії обходу](docs/discovery-strategy.md) | Розширення Web Collector |
| [Адаптер сховища](docs/storage-adapter.md) | Підключення Storage й операції адаптера |
| [Пакети обробників](docs/handler-packages.md) | Маніфест, перевірка, публікація й версії |

## Хто що реалізує й споживає

| API або Protocol | Реалізації | Основні споживачі |
|---|---|---|
| collector.v1 | Web Collector, Telegram Collector | Orchestrator, Admin, сторонній клієнт |
| handler.v1 | Handler Runtime, Storage, LLM | Orchestrator, Admin, сторонній клієнт |
| storage.v1 | Storage | Orchestrator, Admin, сторонній клієнт |
| registry.v1 | Registry | Handler Runtime, Storage, LLM, Web Collector, Telegram Collector, Orchestrator, Assistant, Admin |
| orchestrator.v1 | Orchestrator | Admin, Assistant, сторонній клієнт |
| llm.v1 | LLM | Assistant, Orchestrator, Admin |
| assistant.v1 | Assistant | Admin, сторонній клієнт |
| DiscoveryStrategy, DiscoveryContext | Web Collector та пакети стратегій | Web Collector |
| StorageAdapter | Адаптери Storage | Storage Engine |

HTTP-реалізації визначаються конфігурацією адрес. Детальні залежності й межі заміни — у [каталозі модулів](../docs/components/README.md), [автономності](../docs/architecture/autonomy.md) та [виконанні](../docs/architecture/execution.md).

Зміни контрактів: [настанови розробника](../docs/development/README.md), [jane-contracts](../.agents/skills/jane-contracts/SKILL.md).
