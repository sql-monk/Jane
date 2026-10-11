# jane_kit.metrics

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.metrics.Metrics](#jane_kitmetricsmetrics)
- [jane_kit.metrics.Metrics.__init__](#jane_kitmetricsmetrics__init__)
- [jane_kit.metrics.Metrics.service](#jane_kitmetricsmetricsservice)
- [jane_kit.metrics.Metrics.namespace](#jane_kitmetricsmetricsnamespace)
- [jane_kit.metrics.Metrics.registry](#jane_kitmetricsmetricsregistry)
- [jane_kit.metrics.Metrics.http_requests](#jane_kitmetricsmetricshttp_requests)
- [jane_kit.metrics.Metrics.http_latency](#jane_kitmetricsmetricshttp_latency)
- [jane_kit.metrics.Metrics.http_in_flight](#jane_kitmetricsmetricshttp_in_flight)
- [jane_kit.metrics.Metrics.info](#jane_kitmetricsmetricsinfo)
- [jane_kit.metrics.Metrics.counter](#jane_kitmetricsmetricscounter)
- [jane_kit.metrics.Metrics.gauge](#jane_kitmetricsmetricsgauge)
- [jane_kit.metrics.Metrics.histogram](#jane_kitmetricsmetricshistogram)
- [jane_kit.metrics.Metrics.render](#jane_kitmetricsmetricsrender)
- [jane_kit.metrics.install_metrics](#jane_kitmetricsinstall_metrics)

## jane_kit.metrics.Metrics

**Клас.** Код: [libs/jane-kit/src/jane_kit/metrics.py:21](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L21).

```python
class Metrics:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.metrics.md#jane_kitmetricsmetrics__init__) | Конструктор | ні |
| [service](jane_kit.metrics.md#jane_kitmetricsmetricsservice) | Поле екземпляра | ні |
| [namespace](jane_kit.metrics.md#jane_kitmetricsmetricsnamespace) | Поле екземпляра | ні |
| [registry](jane_kit.metrics.md#jane_kitmetricsmetricsregistry) | Поле екземпляра | ні |
| [http_requests](jane_kit.metrics.md#jane_kitmetricsmetricshttp_requests) | Поле екземпляра | ні |
| [http_latency](jane_kit.metrics.md#jane_kitmetricsmetricshttp_latency) | Поле екземпляра | ні |
| [http_in_flight](jane_kit.metrics.md#jane_kitmetricsmetricshttp_in_flight) | Поле екземпляра | ні |
| [info](jane_kit.metrics.md#jane_kitmetricsmetricsinfo) | Поле екземпляра | ні |
| [counter](jane_kit.metrics.md#jane_kitmetricsmetricscounter) | Метод | ні |
| [gauge](jane_kit.metrics.md#jane_kitmetricsmetricsgauge) | Метод | ні |
| [histogram](jane_kit.metrics.md#jane_kitmetricsmetricshistogram) | Метод | ні |
| [render](jane_kit.metrics.md#jane_kitmetricsmetricsrender) | Метод | ні |

### Опис із вихідного коду

```text
Holds the registry and the standard HTTP metrics of one service instance.
```

## jane_kit.metrics.Metrics.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/metrics.py:24](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L24).

```python
def __init__(self, service: str, namespace: str='jane') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `service` | `str` | `—` | positional-or-keyword |
| `namespace` | `str` | `'jane'` | positional-or-keyword |

Результат: `None`.

## jane_kit.metrics.Metrics.service

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:25](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L25).

```python
self.service = service
```

## jane_kit.metrics.Metrics.namespace

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:26](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L26).

```python
self.namespace = namespace
```

## jane_kit.metrics.Metrics.registry

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:27](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L27).

```python
self.registry = CollectorRegistry(auto_describe=True)
```

## jane_kit.metrics.Metrics.http_requests

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:28](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L28).

```python
self.http_requests = Counter('http_requests_total', 'HTTP requests by route template and status', ['method', 'route', 'status'], namespace=namespace, registry=self.registry)
```

## jane_kit.metrics.Metrics.http_latency

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:35](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L35).

```python
self.http_latency = Histogram('http_request_duration_seconds', 'HTTP request latency by route template', ['method', 'route'], namespace=namespace, registry=self.registry)
```

## jane_kit.metrics.Metrics.http_in_flight

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:42](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L42).

```python
self.http_in_flight = Gauge('http_requests_in_flight', 'HTTP requests being processed', namespace=namespace, registry=self.registry)
```

## jane_kit.metrics.Metrics.info

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/metrics.py:48](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L48).

```python
self.info = Gauge('service_info', 'Static service info', ['service'], namespace=namespace, registry=self.registry)
```

## jane_kit.metrics.Metrics.counter

**Метод.** Код: [libs/jane-kit/src/jane_kit/metrics.py:53](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L53).

```python
def counter(self, name: str, doc: str, labels: Sequence[str]=()) -> Counter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `doc` | `str` | `—` | positional-or-keyword |
| `labels` | `Sequence[str]` | `()` | positional-or-keyword |

Результат: `Counter`.

## jane_kit.metrics.Metrics.gauge

**Метод.** Код: [libs/jane-kit/src/jane_kit/metrics.py:56](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L56).

```python
def gauge(self, name: str, doc: str, labels: Sequence[str]=()) -> Gauge:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `doc` | `str` | `—` | positional-or-keyword |
| `labels` | `Sequence[str]` | `()` | positional-or-keyword |

Результат: `Gauge`.

## jane_kit.metrics.Metrics.histogram

**Метод.** Код: [libs/jane-kit/src/jane_kit/metrics.py:59](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L59).

```python
def histogram(self, name: str, doc: str, labels: Sequence[str]=()) -> Histogram:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `doc` | `str` | `—` | positional-or-keyword |
| `labels` | `Sequence[str]` | `()` | positional-or-keyword |

Результат: `Histogram`.

## jane_kit.metrics.Metrics.render

**Метод.** Код: [libs/jane-kit/src/jane_kit/metrics.py:62](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L62).

```python
def render(self) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bytes`.

## jane_kit.metrics.install_metrics

**Функція.** Код: [libs/jane-kit/src/jane_kit/metrics.py:72](../../../../../../libs/jane-kit/src/jane_kit/metrics.py#L72).

```python
def install_metrics(app: FastAPI, metrics: Metrics, path: str='/metrics') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |
| `metrics` | `Metrics` | `—` | positional-or-keyword |
| `path` | `str` | `'/metrics'` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Expose ``path`` and record request count/latency labelled by route *template*.
```
