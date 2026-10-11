# jane_orchestrator.limits

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.limits.flatten](#jane_orchestratorlimitsflatten)
- [jane_orchestrator.limits.unflatten](#jane_orchestratorlimitsunflatten)
- [jane_orchestrator.limits.LimitsLayer](#jane_orchestratorlimitslimitslayer)
- [jane_orchestrator.limits.LimitsLayer.__init__](#jane_orchestratorlimitslimitslayer__init__)
- [jane_orchestrator.limits.LimitsLayer.level](#jane_orchestratorlimitslimitslayerlevel)
- [jane_orchestrator.limits.LimitsLayer.values](#jane_orchestratorlimitslimitslayervalues)
- [jane_orchestrator.limits.Effective](#jane_orchestratorlimitseffective)
- [jane_orchestrator.limits.Effective.__init__](#jane_orchestratorlimitseffective__init__)
- [jane_orchestrator.limits.Effective.limits](#jane_orchestratorlimitseffectivelimits)
- [jane_orchestrator.limits.Effective.provenance](#jane_orchestratorlimitseffectiveprovenance)
- [jane_orchestrator.limits.Effective.flat](#jane_orchestratorlimitseffectiveflat)
- [jane_orchestrator.limits.Effective.doc](#jane_orchestratorlimitseffectivedoc)
- [jane_orchestrator.limits.Effective.get](#jane_orchestratorlimitseffectiveget)
- [jane_orchestrator.limits.merge_limits](#jane_orchestratorlimitsmerge_limits)

## jane_orchestrator.limits.flatten

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:20](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L20).

```python
def flatten(data: Mapping[str, Any], prefix: str='') -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.limits.unflatten

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:31](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L31).

```python
def unflatten(flat: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `flat` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.limits.LimitsLayer

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:56](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L56).

```python
class LimitsLayer:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [level](jane_orchestrator.limits.md#jane_orchestratorlimitslimitslayerlevel) | Поле | ні |
| [values](jane_orchestrator.limits.md#jane_orchestratorlimitslimitslayervalues) | Поле | ні |
| [__init__](jane_orchestrator.limits.md#jane_orchestratorlimitslimitslayer__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:244](../../../../../../services/orchestrator/tests/test_logic.py#L244).

```python
eff = merge_limits(
        fallback,
        [
            LimitsLayer(
                "platform", {"rate": {"requests_per_second_per_host": 1}, "sandbox": {"memory_mb": 256}}
            ),
            LimitsLayer("source", {"rate": {"requests_per_second_per_host": 2}}),
            LimitsLayer(
                "task",
                {
                    "crawl": {"max_depth": 5},
                    "llm": {"budget": {"amount": 1, "currency": "USD", "period": "day"}},
                },
            ),
            LimitsLayer("stage", {"sandbox": {"memory_mb": 4096}, "crawl": {"max_depth": 3}}),
        ],
        {"sandbox": {"memory_mb": 2048}},
    )
```

## jane_orchestrator.limits.LimitsLayer.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:56](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L56).

```python
def __init__(self, level: str, values: Mapping[str, Any]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `level` | `str` | `—` | positional-or-keyword |
| `values` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:244](../../../../../../services/orchestrator/tests/test_logic.py#L244).

```python
eff = merge_limits(
        fallback,
        [
            LimitsLayer(
                "platform", {"rate": {"requests_per_second_per_host": 1}, "sandbox": {"memory_mb": 256}}
            ),
            LimitsLayer("source", {"rate": {"requests_per_second_per_host": 2}}),
            LimitsLayer(
                "task",
                {
                    "crawl": {"max_depth": 5},
                    "llm": {"budget": {"amount": 1, "currency": "USD", "period": "day"}},
                },
            ),
            LimitsLayer("stage", {"sandbox": {"memory_mb": 4096}, "crawl": {"max_depth": 3}}),
        ],
        {"sandbox": {"memory_mb": 2048}},
    )
```

## jane_orchestrator.limits.LimitsLayer.level

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:57](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L57).

```python
level: str
```

Доступ: читання — так; запис — ні.

## jane_orchestrator.limits.LimitsLayer.values

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:58](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L58).

```python
values: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_orchestrator.limits.Effective

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:62](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L62).

```python
class Effective:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [limits](jane_orchestrator.limits.md#jane_orchestratorlimitseffectivelimits) | Поле | ні |
| [provenance](jane_orchestrator.limits.md#jane_orchestratorlimitseffectiveprovenance) | Поле | ні |
| [flat](jane_orchestrator.limits.md#jane_orchestratorlimitseffectiveflat) | Поле | ні |
| [doc](jane_orchestrator.limits.md#jane_orchestratorlimitseffectivedoc) | Метод | ні |
| [get](jane_orchestrator.limits.md#jane_orchestratorlimitseffectiveget) | Метод | ні |
| [__init__](jane_orchestrator.limits.md#jane_orchestratorlimitseffective__init__) | Конструктор dataclass | ні |

## jane_orchestrator.limits.Effective.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:62](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L62).

```python
def __init__(self, limits: dict[str, Any], provenance: dict[str, str], flat: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `limits` | `dict[str, Any]` | `—` | positional-or-keyword |
| `provenance` | `dict[str, str]` | `—` | positional-or-keyword |
| `flat` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.limits.Effective.limits

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:63](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L63).

```python
limits: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_orchestrator.limits.Effective.provenance

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:64](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L64).

```python
provenance: dict[str, str]
```

Доступ: читання — так; запис — так.

## jane_orchestrator.limits.Effective.flat

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:65](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L65).

```python
flat: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_orchestrator.limits.Effective.doc

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:67](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L67).

```python
def doc(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``EffectiveLimits`` document.
```

## jane_orchestrator.limits.Effective.get

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:71](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L71).

```python
def get(self, path: str, default: Any=None) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `default` | `Any` | `None` | positional-or-keyword |

Результат: `Any`.

## jane_orchestrator.limits.merge_limits

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/limits.py:79](../../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L79).

```python
def merge_limits(fallback: Mapping[str, Any], layers: Sequence[LimitsLayer], hard_caps: Mapping[str, Any] | None=None) -> Effective:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `fallback` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `layers` | `Sequence[LimitsLayer]` | `—` | positional-or-keyword |
| `hard_caps` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `Effective`.

### Опис із вихідного коду

```text
Merge ``fallback`` (code defaults, level platform) and ``layers`` (least specific first).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:244](../../../../../../services/orchestrator/tests/test_logic.py#L244).

```python
eff = merge_limits(
        fallback,
        [
            LimitsLayer(
                "platform", {"rate": {"requests_per_second_per_host": 1}, "sandbox": {"memory_mb": 256}}
            ),
            LimitsLayer("source", {"rate": {"requests_per_second_per_host": 2}}),
            LimitsLayer(
                "task",
                {
                    "crawl": {"max_depth": 5},
                    "llm": {"budget": {"amount": 1, "currency": "USD", "period": "day"}},
                },
            ),
            LimitsLayer("stage", {"sandbox": {"memory_mb": 4096}, "crawl": {"max_depth": 3}}),
        ],
        {"sandbox": {"memory_mb": 2048}},
    )
```
