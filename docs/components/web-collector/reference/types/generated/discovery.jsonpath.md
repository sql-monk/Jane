# discovery.jsonpath

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.jsonpath.JsonPath](#discoveryjsonpathjsonpath)
- [discovery.jsonpath.JsonPath.__init__](#discoveryjsonpathjsonpath__init__)
- [discovery.jsonpath.JsonPath.expr](#discoveryjsonpathjsonpathexpr)
- [discovery.jsonpath.JsonPath.steps](#discoveryjsonpathjsonpathsteps)
- [discovery.jsonpath.JsonPath.__repr__](#discoveryjsonpathjsonpath__repr__)
- [discovery.jsonpath.JsonPath.find](#discoveryjsonpathjsonpathfind)
- [discovery.jsonpath.JsonPath.first](#discoveryjsonpathjsonpathfirst)

## discovery.jsonpath.JsonPath

**Клас.** Код: [services/web-collector/strategies/discovery/jsonpath.py:106](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L106).

```python
class JsonPath:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](discovery.jsonpath.md#discoveryjsonpathjsonpath__init__) | Конструктор | ні |
| [expr](discovery.jsonpath.md#discoveryjsonpathjsonpathexpr) | Поле екземпляра | ні |
| [steps](discovery.jsonpath.md#discoveryjsonpathjsonpathsteps) | Поле екземпляра | ні |
| [__repr__](discovery.jsonpath.md#discoveryjsonpathjsonpath__repr__) | Метод | ні |
| [find](discovery.jsonpath.md#discoveryjsonpathjsonpathfind) | Метод | ні |
| [first](discovery.jsonpath.md#discoveryjsonpathjsonpathfirst) | Метод | ні |

### Опис із вихідного коду

```text
A compiled JSONPath expression (see the module docstring for the supported subset).
```

## discovery.jsonpath.JsonPath.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/jsonpath.py:111](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L111).

```python
def __init__(self, expr: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `expr` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.jsonpath.JsonPath.expr

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/jsonpath.py:112](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L112).

```python
self.expr = expr
```

## discovery.jsonpath.JsonPath.steps

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/jsonpath.py:113](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L113).

```python
self.steps: list[Step] = _parse(expr)
```

## discovery.jsonpath.JsonPath.__repr__

**Метод.** Код: [services/web-collector/strategies/discovery/jsonpath.py:115](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L115).

```python
def __repr__(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## discovery.jsonpath.JsonPath.find

**Метод.** Код: [services/web-collector/strategies/discovery/jsonpath.py:118](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L118).

```python
def find(self, data: Any) -> list[Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `data` | `Any` | `—` | positional-or-keyword |

Результат: `list[Any]`.

## discovery.jsonpath.JsonPath.first

**Метод.** Код: [services/web-collector/strategies/discovery/jsonpath.py:138](../../../../../../services/web-collector/strategies/discovery/jsonpath.py#L138).

```python
def first(self, data: Any) -> Any | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `data` | `Any` | `—` | positional-or-keyword |

Результат: `Any | None`.
