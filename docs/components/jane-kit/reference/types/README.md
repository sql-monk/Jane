# Jane Kit: публічні типи

## Індекс

- [`jane_kit.service`](generated/jane_kit.service.md)
- [`jane_kit.config`](generated/jane_kit.config.md)
- [`jane_kit.auth`](generated/jane_kit.auth.md)
- [`jane_kit.auth_scopes`](generated/jane_kit.auth_scopes.md)
- [`jane_kit.secrets`](generated/jane_kit.secrets.md)
- [`jane_kit.jobs`](generated/jane_kit.jobs.md)
- [`jane_kit.idempotency`](generated/jane_kit.idempotency.md)
- [`jane_kit.clients`](generated/jane_kit.clients.md)
- [`jane_kit.content`](generated/jane_kit.content.md)
- [`jane_kit.health`](generated/jane_kit.health.md)
- [`jane_kit.metrics`](generated/jane_kit.metrics.md)
- [`jane_kit.logs`](generated/jane_kit.logs.md)
- [`jane_kit.tracing`](generated/jane_kit.tracing.md)
- [`jane_kit.pagination`](generated/jane_kit.pagination.md)
- [`jane_kit.errors`](generated/jane_kit.errors.md)
- [`jane_kit.contracts`](generated/jane_kit.contracts.md)
- [`jane_kit.schemas`](generated/jane_kit.schemas.md)
- [`jane_kit.rules`](generated/jane_kit.rules.md)
- [`jane_kit.codegen`](generated/jane_kit.codegen.md)
- [`jane_kit.devstack`](generated/jane_kit.devstack.md)
- [`jane_kit.stores.sqlite`](generated/jane_kit.stores.sqlite.md)
- [`jane_kit.stores.postgres`](generated/jane_kit.stores.postgres.md)

Згенеровані сторінки містять декларації, всі виявлені публічні члени, bases, типи параметрів і посилання на код.

## Гарантії та помилки

| Тип або функція | Умови використання |
|---|---|
| `JaneSettings` | Mutable settings; `with_overrides` повертає копію без автоматичного перезапуску |
| `Limits` | Frozen Pydantic model; кожне поле повинно мати default |
| `resolve_limits` | Повертає `ResolvedLimits`; `LimitError` для недопустимих шарів |
| `Principal` | Frozen dataclass; `require` повертає None або піднімає Forbidden |
| `Authenticator` | Неповна конфігурація → AuthConfigError; невдалий token → Unauthenticated |
| `JobRunner` | Виконує callback кооперативно; durable store не означає автоматичне відновлення коду callback |
| `ContentWriter` | Inline або transit reference за розміром; blob потребує доступного store |
| [`ServiceClient`](service-client.md) | Повтори обмежені RetryPolicy; RemoteError і транспортні помилки мають різні умови |

Властивості без setter доступні лише для читання; mutable поля та колекції змінюйте лише в рамках власного процесу. Атрибути `app.state` — об’єкти, створені фабрикою, а не стабільний бізнес-контракт.

## Приклади

[Сервіс](../../quickstart.md), [власні ліміти](../../configuration.md#успадковані-ліміти), [ContentRef та codegen](../../integration.md).
