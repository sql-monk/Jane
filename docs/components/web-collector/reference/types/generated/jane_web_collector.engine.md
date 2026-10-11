# jane_web_collector.engine

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.engine.Engine](#jane_web_collectorengineengine)
- [jane_web_collector.engine.Engine.__init__](#jane_web_collectorengineengine__init__)
- [jane_web_collector.engine.Engine.settings](#jane_web_collectorengineenginesettings)
- [jane_web_collector.engine.Engine.idempotency](#jane_web_collectorengineengineidempotency)
- [jane_web_collector.engine.Engine.connection_policy](#jane_web_collectorengineengineconnection_policy)
- [jane_web_collector.engine.Engine.base](#jane_web_collectorengineenginebase)
- [jane_web_collector.engine.Engine.limits](#jane_web_collectorengineenginelimits)
- [jane_web_collector.engine.Engine.state](#jane_web_collectorengineenginestate)
- [jane_web_collector.engine.Engine.registry](#jane_web_collectorengineengineregistry)
- [jane_web_collector.engine.Engine.schemas](#jane_web_collectorengineengineschemas)
- [jane_web_collector.engine.Engine.runner](#jane_web_collectorengineenginerunner)
- [jane_web_collector.engine.Engine.platform](#jane_web_collectorengineengineplatform)
- [jane_web_collector.engine.Engine.transit](#jane_web_collectorengineenginetransit)
- [jane_web_collector.engine.Engine.rules_loader](#jane_web_collectorengineenginerules_loader)
- [jane_web_collector.engine.Engine.client](#jane_web_collectorengineengineclient)
- [jane_web_collector.engine.Engine.renderer](#jane_web_collectorengineenginerenderer)
- [jane_web_collector.engine.Engine.host_limiter](#jane_web_collectorengineenginehost_limiter)
- [jane_web_collector.engine.Engine.deps](#jane_web_collectorengineenginedeps)
- [jane_web_collector.engine.Engine.local](#jane_web_collectorengineenginelocal)
- [jane_web_collector.engine.Engine.shutting_down](#jane_web_collectorengineengineshutting_down)
- [jane_web_collector.engine.Engine.resolve](#jane_web_collectorengineengineresolve)
- [jane_web_collector.engine.Engine.start](#jane_web_collectorengineenginestart)
- [jane_web_collector.engine.Engine.stop](#jane_web_collectorengineenginestop)
- [jane_web_collector.engine.Engine.resume_pending](#jane_web_collectorengineengineresume_pending)
- [jane_web_collector.engine.Engine.gc](#jane_web_collectorengineenginegc)
- [jane_web_collector.engine.Engine.start_collection](#jane_web_collectorengineenginestart_collection)
- [jane_web_collector.engine.Engine.collection_view](#jane_web_collectorengineenginecollection_view)
- [jane_web_collector.engine.Engine.acked](#jane_web_collectorengineengineacked)
- [jane_web_collector.engine.Engine.fetch_one](#jane_web_collectorengineenginefetch_one)
- [jane_web_collector.engine.Engine.capabilities](#jane_web_collectorengineenginecapabilities)

## jane_web_collector.engine.Engine

**Клас.** Код: [services/web-collector/src/jane_web_collector/engine.py:45](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L45).

```python
class Engine:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.engine.md#jane_web_collectorengineengine__init__) | Конструктор | ні |
| [settings](jane_web_collector.engine.md#jane_web_collectorengineenginesettings) | Поле екземпляра | ні |
| [idempotency](jane_web_collector.engine.md#jane_web_collectorengineengineidempotency) | Поле екземпляра | ні |
| [connection_policy](jane_web_collector.engine.md#jane_web_collectorengineengineconnection_policy) | Поле екземпляра | ні |
| [base](jane_web_collector.engine.md#jane_web_collectorengineenginebase) | Поле екземпляра | ні |
| [limits](jane_web_collector.engine.md#jane_web_collectorengineenginelimits) | Поле екземпляра | ні |
| [state](jane_web_collector.engine.md#jane_web_collectorengineenginestate) | Поле екземпляра | ні |
| [registry](jane_web_collector.engine.md#jane_web_collectorengineengineregistry) | Поле екземпляра | ні |
| [schemas](jane_web_collector.engine.md#jane_web_collectorengineengineschemas) | Поле екземпляра | ні |
| [runner](jane_web_collector.engine.md#jane_web_collectorengineenginerunner) | Поле екземпляра | ні |
| [platform](jane_web_collector.engine.md#jane_web_collectorengineengineplatform) | Поле екземпляра | ні |
| [transit](jane_web_collector.engine.md#jane_web_collectorengineenginetransit) | Поле екземпляра | ні |
| [rules_loader](jane_web_collector.engine.md#jane_web_collectorengineenginerules_loader) | Поле екземпляра | ні |
| [client](jane_web_collector.engine.md#jane_web_collectorengineengineclient) | Поле екземпляра | ні |
| [renderer](jane_web_collector.engine.md#jane_web_collectorengineenginerenderer) | Поле екземпляра | ні |
| [host_limiter](jane_web_collector.engine.md#jane_web_collectorengineenginehost_limiter) | Поле екземпляра | ні |
| [deps](jane_web_collector.engine.md#jane_web_collectorengineenginedeps) | Поле екземпляра | ні |
| [local](jane_web_collector.engine.md#jane_web_collectorengineenginelocal) | Поле екземпляра | ні |
| [shutting_down](jane_web_collector.engine.md#jane_web_collectorengineengineshutting_down) | Поле екземпляра | ні |
| [resolve](jane_web_collector.engine.md#jane_web_collectorengineengineresolve) | Метод | ні |
| [start](jane_web_collector.engine.md#jane_web_collectorengineenginestart) | Метод | ні |
| [stop](jane_web_collector.engine.md#jane_web_collectorengineenginestop) | Метод | ні |
| [resume_pending](jane_web_collector.engine.md#jane_web_collectorengineengineresume_pending) | Метод | ні |
| [gc](jane_web_collector.engine.md#jane_web_collectorengineenginegc) | Метод | ні |
| [start_collection](jane_web_collector.engine.md#jane_web_collectorengineenginestart_collection) | Метод | ні |
| [collection_view](jane_web_collector.engine.md#jane_web_collectorengineenginecollection_view) | Метод | ні |
| [acked](jane_web_collector.engine.md#jane_web_collectorengineengineacked) | Метод | ні |
| [fetch_one](jane_web_collector.engine.md#jane_web_collectorengineenginefetch_one) | Метод | ні |
| [capabilities](jane_web_collector.engine.md#jane_web_collectorengineenginecapabilities) | Метод | ні |

## jane_web_collector.engine.Engine.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/engine.py:46](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L46).

```python
def __init__(self, settings: Settings, base_limits: ResolvedLimits[ServiceLimits], state: StateStore, registry: Registry, schemas: ContractSchemas, runner: JobRunner, *, idempotency: SqliteIdempotencyStore | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `base_limits` | `ResolvedLimits[ServiceLimits]` | `—` | positional-or-keyword |
| `state` | `StateStore` | `—` | positional-or-keyword |
| `registry` | `Registry` | `—` | positional-or-keyword |
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |
| `runner` | `JobRunner` | `—` | positional-or-keyword |
| `idempotency` | `SqliteIdempotencyStore \| None` | `None` | keyword-only |

Результат: `None`.

## jane_web_collector.engine.Engine.settings

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:57](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L57).

```python
self.settings = settings
```

## jane_web_collector.engine.Engine.idempotency

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:58](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L58).

```python
self.idempotency = idempotency
```

## jane_web_collector.engine.Engine.connection_policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:59](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L59).

```python
self.connection_policy = settings.connection_policy()
```

## jane_web_collector.engine.Engine.base

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:60](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L60).

```python
self.base = base_limits
```

## jane_web_collector.engine.Engine.limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:61](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L61).

```python
self.limits = base_limits.limits
```

## jane_web_collector.engine.Engine.state

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:62](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L62).

```python
self.state = state
```

## jane_web_collector.engine.Engine.registry

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:63](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L63).

```python
self.registry = registry
```

## jane_web_collector.engine.Engine.schemas

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:64](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L64).

```python
self.schemas = schemas
```

## jane_web_collector.engine.Engine.runner

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:65](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L65).

```python
self.runner = runner
```

## jane_web_collector.engine.Engine.platform

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:66](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L66).

```python
self.platform = platform_layers(settings)
```

## jane_web_collector.engine.Engine.transit

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:67](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L67).

```python
self.transit = TransitStore(settings.transit_dir) if settings.transit_dir else None
```

## jane_web_collector.engine.Engine.rules_loader

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:68](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L68).

```python
self.rules_loader = RulesLoader(rules_dir=settings.rules_dir, registry_url=settings.registry_url, registry_token_env=settings.registry_token_env, timeout_s=self.limits.timeouts.request_timeout_ms / 1000)
```

## jane_web_collector.engine.Engine.client

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:79](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L79).

```python
self.client = build_client(self.limits, egress)
```

## jane_web_collector.engine.Engine.renderer

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:82](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L82).

```python
self.renderer = Renderer(RenderOptions(enabled=settings.render_enabled, wait_until=settings.render_wait_until, block_resource_types=tuple(settings.render_block_resource_types), executable=settings.render_browser_executable, deny_private=settings.render_deny_private), egress, max_pages=self.limits.collector.render_max_pages, launch_timeout_ms=self.limits.collector.render_launch_timeout_ms, close_timeout_ms=self.limits.collector.render_close_timeout_ms)
```

## jane_web_collector.engine.Engine.host_limiter

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:109](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L109).

```python
self.host_limiter = HostLimiter(self.limits, shared)
```

## jane_web_collector.engine.Engine.deps

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:110](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L110).

```python
self.deps = RunDeps(state=state, registry=registry, client=self.client, resolve=self.resolve, transit=self.transit, instance_id=settings.instance_id, lease_seconds=settings.lease_seconds, heartbeat_seconds=settings.heartbeat_interval_ms / 1000, user_agent=settings.user_agent, version=__version__, host_limiter=self.host_limiter, connection_policy=self.connection_policy, renderer=self.renderer)
```

## jane_web_collector.engine.Engine.local

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:125](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L125).

```python
self.local: set[str] = set()
```

## jane_web_collector.engine.Engine.shutting_down

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/engine.py:126](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L126).

```python
self.shutting_down = False
```

## jane_web_collector.engine.Engine.resolve

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:130](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L130).

```python
def resolve(self, source: Mapping[str, Any] | None=None, request: Mapping[str, Any] | None=None, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `request` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `extra` | `LimitLayer` | `—` | var-positional |

Результат: `ResolvedLimits[ServiceLimits]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.engine.Engine.start

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:148](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L148).

```python
async def start(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.engine.Engine.stop

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:152](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L152).

```python
async def stop(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.engine.Engine.resume_pending

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:176](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L176).

```python
async def resume_pending(self) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Take over non-terminal collections whose lease expired (after a crash/kill) and continue them.
```

## jane_web_collector.engine.Engine.gc

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:208](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L208).

```python
def gc(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.engine.Engine.start_collection

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:262](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L262).

```python
async def start_collection(self, payload: dict[str, Any]) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `payload` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `Job`.

Явні `raise` у тілі: `JaneError`, `LimitExceeded`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.engine.Engine.collection_view

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:347](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L347).

```python
def collection_view(self, cid: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.engine.Engine.acked

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:390](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L390).

```python
def acked(self, cid: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.engine.Engine.fetch_one

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:396](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L396).

```python
async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `payload` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `JaneError`, `LimitExceeded`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.engine.Engine.capabilities

**Метод.** Код: [services/web-collector/src/jane_web_collector/engine.py:532](../../../../../../services/web-collector/src/jane_web_collector/engine.py#L532).

```python
def capabilities(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.
