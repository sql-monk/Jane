# Модуль `jane_kit.metrics`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/metrics.py](../../../../../libs/jane-kit/src/jane_kit/metrics.py). Не редагуйте вручну.

Prometheus metrics with a per-application registry (no global state between app instances).

## Класи

### Клас `Metrics`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.metrics` |
| Код | [metrics.py:21](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L21) |

```python
class Metrics: ...
```

Holds the registry and the standard HTTP metrics of one service instance.

#### Конструктор `Metrics.__init__`

```python
def __init__(self, service: str, namespace: str = 'jane') -> None: ...
```

Код: [metrics.py:24](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L24).

#### Метод `Metrics.counter`

```python
def counter(self, name: str, doc: str, labels: Sequence[str] = ()) -> Counter: ...
```

Код: [metrics.py:53](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L53).

#### Метод `Metrics.gauge`

```python
def gauge(self, name: str, doc: str, labels: Sequence[str] = ()) -> Gauge: ...
```

Код: [metrics.py:56](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L56).

#### Метод `Metrics.histogram`

```python
def histogram(self, name: str, doc: str, labels: Sequence[str] = ()) -> Histogram: ...
```

Код: [metrics.py:59](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L59).

#### Метод `Metrics.render`

```python
def render(self) -> bytes: ...
```

Код: [metrics.py:62](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L62).

## Функції

### Функція `install_metrics`

```python
def install_metrics(app: FastAPI, metrics: Metrics, path: str = '/metrics') -> None: ...
```

Expose ``path`` and record request count/latency labelled by route *template*.

Код: [metrics.py:72](../../../../../libs/jane-kit/src/jane_kit/metrics.py#L72).
