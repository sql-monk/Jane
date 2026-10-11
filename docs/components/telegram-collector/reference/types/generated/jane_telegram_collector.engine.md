# jane_telegram_collector.engine

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.engine.Engine](#jane_telegram_collectorengineengine)
- [jane_telegram_collector.engine.Engine.__init__](#jane_telegram_collectorengineengine__init__)
- [jane_telegram_collector.engine.Engine.settings](#jane_telegram_collectorengineenginesettings)
- [jane_telegram_collector.engine.Engine.idempotency](#jane_telegram_collectorengineengineidempotency)
- [jane_telegram_collector.engine.Engine.base](#jane_telegram_collectorengineenginebase)
- [jane_telegram_collector.engine.Engine.limits](#jane_telegram_collectorengineenginelimits)
- [jane_telegram_collector.engine.Engine.state](#jane_telegram_collectorengineenginestate)
- [jane_telegram_collector.engine.Engine.factory](#jane_telegram_collectorengineenginefactory)
- [jane_telegram_collector.engine.Engine.schemas](#jane_telegram_collectorengineengineschemas)
- [jane_telegram_collector.engine.Engine.runner](#jane_telegram_collectorengineenginerunner)
- [jane_telegram_collector.engine.Engine.platform](#jane_telegram_collectorengineengineplatform)
- [jane_telegram_collector.engine.Engine.transit](#jane_telegram_collectorengineenginetransit)
- [jane_telegram_collector.engine.Engine.policy](#jane_telegram_collectorengineenginepolicy)
- [jane_telegram_collector.engine.Engine.rules_loader](#jane_telegram_collectorengineenginerules_loader)
- [jane_telegram_collector.engine.Engine.deps](#jane_telegram_collectorengineenginedeps)
- [jane_telegram_collector.engine.Engine.local](#jane_telegram_collectorengineenginelocal)
- [jane_telegram_collector.engine.Engine.shutting_down](#jane_telegram_collectorengineengineshutting_down)
- [jane_telegram_collector.engine.Engine.resolve](#jane_telegram_collectorengineengineresolve)
- [jane_telegram_collector.engine.Engine.start](#jane_telegram_collectorengineenginestart)
- [jane_telegram_collector.engine.Engine.stop](#jane_telegram_collectorengineenginestop)
- [jane_telegram_collector.engine.Engine.resume_pending](#jane_telegram_collectorengineengineresume_pending)
- [jane_telegram_collector.engine.Engine.gc](#jane_telegram_collectorengineenginegc)
- [jane_telegram_collector.engine.Engine.account](#jane_telegram_collectorengineengineaccount)
- [jane_telegram_collector.engine.Engine.start_collection](#jane_telegram_collectorengineenginestart_collection)
- [jane_telegram_collector.engine.Engine.collection_view](#jane_telegram_collectorengineenginecollection_view)
- [jane_telegram_collector.engine.Engine.acked](#jane_telegram_collectorengineengineacked)
- [jane_telegram_collector.engine.Engine.fetch_one](#jane_telegram_collectorengineenginefetch_one)
- [jane_telegram_collector.engine.Engine.capabilities](#jane_telegram_collectorengineenginecapabilities)

## jane_telegram_collector.engine.Engine

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:55](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L55).

```python
class Engine:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.engine.md#jane_telegram_collectorengineengine__init__) | Конструктор | ні |
| [settings](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginesettings) | Поле екземпляра | ні |
| [idempotency](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineidempotency) | Поле екземпляра | ні |
| [base](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginebase) | Поле екземпляра | ні |
| [limits](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginelimits) | Поле екземпляра | ні |
| [state](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginestate) | Поле екземпляра | ні |
| [factory](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginefactory) | Поле екземпляра | ні |
| [schemas](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineschemas) | Поле екземпляра | ні |
| [runner](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginerunner) | Поле екземпляра | ні |
| [platform](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineplatform) | Поле екземпляра | ні |
| [transit](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginetransit) | Поле екземпляра | ні |
| [policy](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginepolicy) | Поле екземпляра | ні |
| [rules_loader](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginerules_loader) | Поле екземпляра | ні |
| [deps](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginedeps) | Поле екземпляра | ні |
| [local](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginelocal) | Поле екземпляра | ні |
| [shutting_down](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineshutting_down) | Поле екземпляра | ні |
| [resolve](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineresolve) | Метод | ні |
| [start](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginestart) | Метод | ні |
| [stop](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginestop) | Метод | ні |
| [resume_pending](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineresume_pending) | Метод | ні |
| [gc](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginegc) | Метод | ні |
| [account](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineaccount) | Метод | ні |
| [start_collection](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginestart_collection) | Метод | ні |
| [collection_view](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginecollection_view) | Метод | ні |
| [acked](jane_telegram_collector.engine.md#jane_telegram_collectorengineengineacked) | Метод | ні |
| [fetch_one](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginefetch_one) | Метод | ні |
| [capabilities](jane_telegram_collector.engine.md#jane_telegram_collectorengineenginecapabilities) | Метод | ні |

## jane_telegram_collector.engine.Engine.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:56](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L56).

```python
def __init__(self, settings: Settings, base_limits: ResolvedLimits[ServiceLimits], state: StateStore, factory: ClientFactory, schemas: ContractSchemas, runner: JobRunner, *, idempotency: SqliteIdempotencyStore | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `base_limits` | `ResolvedLimits[ServiceLimits]` | `—` | positional-or-keyword |
| `state` | `StateStore` | `—` | positional-or-keyword |
| `factory` | `ClientFactory` | `—` | positional-or-keyword |
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |
| `runner` | `JobRunner` | `—` | positional-or-keyword |
| `idempotency` | `SqliteIdempotencyStore \| None` | `None` | keyword-only |

Результат: `None`.

## jane_telegram_collector.engine.Engine.settings

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:67](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L67).

```python
self.settings = settings
```

## jane_telegram_collector.engine.Engine.idempotency

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:68](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L68).

```python
self.idempotency = idempotency
```

## jane_telegram_collector.engine.Engine.base

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:69](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L69).

```python
self.base = base_limits
```

## jane_telegram_collector.engine.Engine.limits

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:70](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L70).

```python
self.limits = base_limits.limits
```

## jane_telegram_collector.engine.Engine.state

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:71](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L71).

```python
self.state = state
```

## jane_telegram_collector.engine.Engine.factory

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:72](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L72).

```python
self.factory = factory
```

## jane_telegram_collector.engine.Engine.schemas

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:73](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L73).

```python
self.schemas = schemas
```

## jane_telegram_collector.engine.Engine.runner

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:74](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L74).

```python
self.runner = runner
```

## jane_telegram_collector.engine.Engine.platform

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:75](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L75).

```python
self.platform = platform_layers(settings)
```

## jane_telegram_collector.engine.Engine.transit

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:76](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L76).

```python
self.transit = TransitStore(settings.transit_dir) if settings.transit_dir else None
```

## jane_telegram_collector.engine.Engine.policy

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:77](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L77).

```python
self.policy = settings.connection_policy()
```

## jane_telegram_collector.engine.Engine.rules_loader

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:78](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L78).

```python
self.rules_loader = RulesLoader(rules_dir=settings.rules_dir, registry_url=settings.registry_url, registry_token_env=settings.registry_token_env, timeout_s=self.limits.timeouts.request_timeout_ms / 1000)
```

## jane_telegram_collector.engine.Engine.deps

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:84](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L84).

```python
self.deps = RunDeps(state=state, factory=factory, resolve=self.resolve, transit=self.transit, instance_id=settings.instance_id, lease_seconds=settings.lease_seconds, heartbeat_seconds=settings.heartbeat_interval_ms / 1000, version=__version__)
```

## jane_telegram_collector.engine.Engine.local

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:94](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L94).

```python
self.local: set[str] = set()
```

## jane_telegram_collector.engine.Engine.shutting_down

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L95).

```python
self.shutting_down = False
```

## jane_telegram_collector.engine.Engine.resolve

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:99](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L99).

```python
def resolve(self, source: Mapping[str, Any] | None=None, request: Mapping[str, Any] | None=None) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `request` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `ResolvedLimits[ServiceLimits]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.engine.Engine.start

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:113](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L113).

```python
async def start(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.engine.Engine.stop

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:117](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L117).

```python
async def stop(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.engine.Engine.resume_pending

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:138](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L138).

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

## jane_telegram_collector.engine.Engine.gc

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:169](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L169).

```python
def gc(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.engine.Engine.account

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:216](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L216).

```python
def account(self, rules: Mapping[str, Any], pointer: str) -> ResolvedAccount:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rules` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `pointer` | `str` | `—` | positional-or-keyword |

Результат: `ResolvedAccount`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The ``telegram_account`` connection named by the rules (or the configured default), secrets resolved.
```

## jane_telegram_collector.engine.Engine.start_collection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:241](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L241).

```python
async def start_collection(self, payload: dict[str, Any]) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `payload` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `Job`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.engine.Engine.collection_view

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:325](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L325).

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

## jane_telegram_collector.engine.Engine.acked

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:363](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L363).

```python
def acked(self, cid: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.engine.Engine.fetch_one

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:369](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L369).

```python
async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `payload` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.engine.Engine.capabilities

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/engine.py:463](../../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L463).

```python
def capabilities(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.
