# jane_web_collector.discovery.registry

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.discovery.registry.ENTRY_POINT_GROUP](#jane_web_collectordiscoveryregistryentry_point_group)
- [jane_web_collector.discovery.registry.DISCOVERY_MODULE](#jane_web_collectordiscoveryregistrydiscovery_module)
- [jane_web_collector.discovery.registry.RESERVED_TYPES](#jane_web_collectordiscoveryregistryreserved_types)
- [jane_web_collector.discovery.registry.default_discovery_path](#jane_web_collectordiscoveryregistrydefault_discovery_path)
- [jane_web_collector.discovery.registry.load_discovery_package](#jane_web_collectordiscoveryregistryload_discovery_package)
- [jane_web_collector.discovery.registry.Registry](#jane_web_collectordiscoveryregistryregistry)
- [jane_web_collector.discovery.registry.Registry.__init__](#jane_web_collectordiscoveryregistryregistry__init__)
- [jane_web_collector.discovery.registry.Registry.origins](#jane_web_collectordiscoveryregistryregistryorigins)
- [jane_web_collector.discovery.registry.Registry.load_errors](#jane_web_collectordiscoveryregistryregistryload_errors)
- [jane_web_collector.discovery.registry.Registry.register](#jane_web_collectordiscoveryregistryregistryregister)
- [jane_web_collector.discovery.registry.Registry.get](#jane_web_collectordiscoveryregistryregistryget)
- [jane_web_collector.discovery.registry.Registry.types](#jane_web_collectordiscoveryregistryregistrytypes)
- [jane_web_collector.discovery.registry.Registry.supported](#jane_web_collectordiscoveryregistryregistrysupported)
- [jane_web_collector.discovery.registry.Registry.default](#jane_web_collectordiscoveryregistryregistrydefault)

## jane_web_collector.discovery.registry.ENTRY_POINT_GROUP

**Константа.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:41](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L41).

```python
ENTRY_POINT_GROUP = 'jane.web_collector.strategies'
```

## jane_web_collector.discovery.registry.DISCOVERY_MODULE

**Константа.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:42](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L42).

```python
DISCOVERY_MODULE = 'jane_web_collector_discovery'
```

## jane_web_collector.discovery.registry.RESERVED_TYPES

**Константа.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:43](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L43).

```python
RESERVED_TYPES = frozenset({'llm_explore'})
```

### Опис із вихідного коду

```text
Valid in CollectorRules but not executed by the collector in v1 (ADR-0010).
```

## jane_web_collector.discovery.registry.default_discovery_path

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:47](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L47).

```python
def default_discovery_path() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
``services/web-collector/strategies/discovery`` next to ``src/`` (editable/dev checkout).
```

## jane_web_collector.discovery.registry.load_discovery_package

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:52](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L52).

```python
def load_discovery_package(path: Path) -> ModuleType | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `Path` | `—` | positional-or-keyword |

Результат: `ModuleType | None`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Import the WP-03 package at ``path`` (a directory with ``__init__.py``) as ``jane_web_collector_discovery``.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/conftest.py:103](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L103).

```python
module = load_discovery_package(PACKAGE_DIR)
```

## jane_web_collector.discovery.registry.Registry

**Клас.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:76](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L76).

```python
class Registry:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistry__init__) | Конструктор | ні |
| [origins](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistryorigins) | Поле екземпляра | ні |
| [load_errors](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistryload_errors) | Поле екземпляра | ні |
| [register](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistryregister) | Метод | ні |
| [get](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistryget) | Метод | ні |
| [types](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistrytypes) | Метод | ні |
| [supported](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistrysupported) | Метод | ні |
| [default](jane_web_collector.discovery.registry.md#jane_web_collectordiscoveryregistryregistrydefault) | Метод | ні |

### Опис із вихідного коду

```text
``StrategyRegistry`` owned by WP-02.
```

## jane_web_collector.discovery.registry.Registry.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:79](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L79).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.discovery.registry.Registry.origins

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:81](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L81).

```python
self.origins: dict[str, str] = {}
```

## jane_web_collector.discovery.registry.Registry.load_errors

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:82](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L82).

```python
self.load_errors: list[str] = []
```

## jane_web_collector.discovery.registry.Registry.register

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:84](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L84).

```python
def register(self, strategy: type[DiscoveryStrategy], origin: str='code') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `strategy` | `type[DiscoveryStrategy]` | `—` | positional-or-keyword |
| `origin` | `str` | `'code'` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `TypeError`, `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.discovery.registry.Registry.get

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:100](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L100).

```python
def get(self, type_name: str) -> type[DiscoveryStrategy]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `type_name` | `str` | `—` | positional-or-keyword |

Результат: `type[DiscoveryStrategy]`.

## jane_web_collector.discovery.registry.Registry.types

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:103](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L103).

```python
def types(self) -> Sequence[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Sequence[str]`.

## jane_web_collector.discovery.registry.Registry.supported

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:106](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L106).

```python
def supported(self, type_name: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `type_name` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.discovery.registry.Registry.default

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/registry.py:118](../../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L118).

```python
def default(cls, discovery_path: Path | None=None, *, use_entry_points: bool=True) -> Registry:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `discovery_path` | `Path \| None` | `None` | positional-or-keyword |
| `use_entry_points` | `bool` | `True` | keyword-only |

Результат: `Registry`.
