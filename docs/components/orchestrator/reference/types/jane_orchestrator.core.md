# Модуль `jane_orchestrator.core`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/core.py](../../../../../services/orchestrator/src/jane_orchestrator/core.py). Не редагуйте вручну.

Shared state of one orchestrator process: DB, contract schemas, executors, limits, metrics.

## Класи

### Клас `Core`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.core` |
| Код | [core.py:55](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L55) |

```python
class Core: ...
```

#### Конструктор `Core.__init__`

```python
def __init__(
    self,
    settings: Settings,
    limits: ServiceLimits,
    metrics: Metrics | None = None,
) -> None: ...
```

Код: [core.py:56](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L56).

#### Метод `Core.open`

```python
def open(self) -> None: ...
```

Код: [core.py:73](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L73).

#### Метод `Core.close`

```python
def close(self) -> None: ...
```

Код: [core.py:78](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L78).

#### Метод `Core.seed_platform_limits`

```python
def seed_platform_limits(self) -> None: ...
```

First start: platform document from ``LIMITS_FILE`` (PlatformLimits) or the documented defaults.

Винятки в коді методу: `ValidationFailed`.

Код: [core.py:83](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L83).

#### Метод `Core.platform_limits`

```python
def platform_limits(self, conn: Any) -> tuple[dict[str, Any], int]: ...
```

Код: [core.py:108](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L108).

#### Метод `Core.effective`

```python
def effective(
    self,
    platform: dict[str, Any],
    source: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    stage: dict[str, Any] | None = None,
    request: dict[str, Any] | None = None,
) -> Effective: ...
```

Код: [core.py:112](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L112).

#### Метод `Core.audit`

```python
@staticmethod
def audit(
    conn: Any,
    actor: str,
    action: str,
    subject_type: str,
    subject_id: str,
    details: dict[str, Any] | None,
) -> None: ...
```

Код: [core.py:139](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L139).

### Клас `EngineMetrics`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_orchestrator.core` |
| Код | [core.py:24](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L24) |

```python
@dataclass
class EngineMetrics: ...
```

Prometheus metrics of the queue engine (attached to the app registry when metrics are enabled).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `metrics` | `Metrics \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `EngineMetrics.inc`

```python
def inc(self, name: str, amount: float = 1, **labels: str) -> None: ...
```

Код: [core.py:48](../../../../../services/orchestrator/src/jane_orchestrator/core.py#L48).
