# jane_orchestrator.core

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.core.EngineMetrics](#jane_orchestratorcoreenginemetrics)
- [jane_orchestrator.core.EngineMetrics.__init__](#jane_orchestratorcoreenginemetrics__init__)
- [jane_orchestrator.core.EngineMetrics.metrics](#jane_orchestratorcoreenginemetricsmetrics)
- [jane_orchestrator.core.EngineMetrics.inc](#jane_orchestratorcoreenginemetricsinc)
- [jane_orchestrator.core.Core](#jane_orchestratorcorecore)
- [jane_orchestrator.core.Core.__init__](#jane_orchestratorcorecore__init__)
- [jane_orchestrator.core.Core.settings](#jane_orchestratorcorecoresettings)
- [jane_orchestrator.core.Core.limits](#jane_orchestratorcorecorelimits)
- [jane_orchestrator.core.Core.engine](#jane_orchestratorcorecoreengine)
- [jane_orchestrator.core.Core.db](#jane_orchestratorcorecoredb)
- [jane_orchestrator.core.Core.schemas](#jane_orchestratorcorecoreschemas)
- [jane_orchestrator.core.Core.executors](#jane_orchestratorcorecoreexecutors)
- [jane_orchestrator.core.Core.metrics](#jane_orchestratorcorecoremetrics)
- [jane_orchestrator.core.Core.fallback](#jane_orchestratorcorecorefallback)
- [jane_orchestrator.core.Core.open](#jane_orchestratorcorecoreopen)
- [jane_orchestrator.core.Core.close](#jane_orchestratorcorecoreclose)
- [jane_orchestrator.core.Core.seed_platform_limits](#jane_orchestratorcorecoreseed_platform_limits)
- [jane_orchestrator.core.Core.platform_limits](#jane_orchestratorcorecoreplatform_limits)
- [jane_orchestrator.core.Core.effective](#jane_orchestratorcorecoreeffective)
- [jane_orchestrator.core.Core.audit](#jane_orchestratorcorecoreaudit)

## jane_orchestrator.core.EngineMetrics

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/core.py:24](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L24).

```python
class EngineMetrics:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [metrics](jane_orchestrator.core.md#jane_orchestratorcoreenginemetricsmetrics) | Поле | ні |
| [inc](jane_orchestrator.core.md#jane_orchestratorcoreenginemetricsinc) | Метод | ні |
| [__init__](jane_orchestrator.core.md#jane_orchestratorcoreenginemetrics__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Prometheus metrics of the queue engine (attached to the app registry when metrics are enabled).
```

## jane_orchestrator.core.EngineMetrics.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/core.py:24](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L24).

```python
def __init__(self, metrics: Metrics | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `metrics` | `Metrics \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.core.EngineMetrics.metrics

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/core.py:27](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L27).

```python
metrics: Metrics | None = None
```

Доступ: читання — так; запис — так.

## jane_orchestrator.core.EngineMetrics.inc

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:48](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L48).

```python
def inc(self, name: str, amount: float=1, **labels: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `amount` | `float` | `1` | positional-or-keyword |
| `labels` | `str` | `—` | var-keyword |

Результат: `None`.

## jane_orchestrator.core.Core

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/core.py:55](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L55).

```python
class Core:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.core.md#jane_orchestratorcorecore__init__) | Конструктор | ні |
| [settings](jane_orchestrator.core.md#jane_orchestratorcorecoresettings) | Поле екземпляра | ні |
| [limits](jane_orchestrator.core.md#jane_orchestratorcorecorelimits) | Поле екземпляра | ні |
| [engine](jane_orchestrator.core.md#jane_orchestratorcorecoreengine) | Поле екземпляра | ні |
| [db](jane_orchestrator.core.md#jane_orchestratorcorecoredb) | Поле екземпляра | ні |
| [schemas](jane_orchestrator.core.md#jane_orchestratorcorecoreschemas) | Поле екземпляра | ні |
| [executors](jane_orchestrator.core.md#jane_orchestratorcorecoreexecutors) | Поле екземпляра | ні |
| [metrics](jane_orchestrator.core.md#jane_orchestratorcorecoremetrics) | Поле екземпляра | ні |
| [fallback](jane_orchestrator.core.md#jane_orchestratorcorecorefallback) | Поле екземпляра | ні |
| [open](jane_orchestrator.core.md#jane_orchestratorcorecoreopen) | Метод | ні |
| [close](jane_orchestrator.core.md#jane_orchestratorcorecoreclose) | Метод | ні |
| [seed_platform_limits](jane_orchestrator.core.md#jane_orchestratorcorecoreseed_platform_limits) | Метод | ні |
| [platform_limits](jane_orchestrator.core.md#jane_orchestratorcorecoreplatform_limits) | Метод | ні |
| [effective](jane_orchestrator.core.md#jane_orchestratorcorecoreeffective) | Метод | ні |
| [audit](jane_orchestrator.core.md#jane_orchestratorcorecoreaudit) | Метод | ні |

## jane_orchestrator.core.Core.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/core.py:56](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L56).

```python
def __init__(self, settings: Settings, limits: ServiceLimits, metrics: Metrics | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `metrics` | `Metrics \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.core.Core.settings

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:57](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L57).

```python
self.settings = settings
```

## jane_orchestrator.core.Core.limits

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:58](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L58).

```python
self.limits = limits
```

## jane_orchestrator.core.Core.engine

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:59](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L59).

```python
self.engine = limits.engine
```

## jane_orchestrator.core.Core.db

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:60](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L60).

```python
self.db = Database(settings.database_url, max_size=limits.engine.db_pool_max)
```

## jane_orchestrator.core.Core.schemas

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:61](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L61).

```python
self.schemas = ContractSchemas(settings.contracts_dir)
```

## jane_orchestrator.core.Core.executors

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:63](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L63).

```python
self.executors = Executors(settings.all_executors(), connect_timeout_ms=c.timeouts.connect_timeout_ms, request_timeout_ms=c.timeouts.request_timeout_ms, keepalive_expiry_ms=limits.engine.executor_keepalive_expiry_ms, stale_connection_retries=limits.engine.executor_stale_connection_retries)
```

## jane_orchestrator.core.Core.metrics

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:70](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L70).

```python
self.metrics = EngineMetrics(metrics)
```

## jane_orchestrator.core.Core.fallback

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/core.py:71](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L71).

```python
self.fallback: dict[str, Any] = c.model_dump(mode='json')
```

## jane_orchestrator.core.Core.open

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:73](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L73).

```python
def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.core.Core.close

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:78](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L78).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.core.Core.seed_platform_limits

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:83](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L83).

```python
def seed_platform_limits(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
First start: platform document from ``LIMITS_FILE`` (PlatformLimits) or the documented defaults.
```

## jane_orchestrator.core.Core.platform_limits

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:108](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L108).

```python
def platform_limits(self, conn: Any) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

## jane_orchestrator.core.Core.effective

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:112](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L112).

```python
def effective(self, platform: dict[str, Any], source: dict[str, Any] | None=None, task: dict[str, Any] | None=None, stage: dict[str, Any] | None=None, request: dict[str, Any] | None=None) -> Effective:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `platform` | `dict[str, Any]` | `—` | positional-or-keyword |
| `source` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `task` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `stage` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `request` | `dict[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `Effective`.

## jane_orchestrator.core.Core.audit

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/core.py:139](../../../../../../services/orchestrator/src/jane_orchestrator/core.py#L139).

```python
def audit(conn: Any, actor: str, action: str, subject_type: str, subject_id: str, details: dict[str, Any] | None) -> None:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `conn` | `Any` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |
| `action` | `str` | `—` | positional-or-keyword |
| `subject_type` | `str` | `—` | positional-or-keyword |
| `subject_id` | `str` | `—` | positional-or-keyword |
| `details` | `dict[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `None`.
