# jane_orchestrator.routing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.routing.NewItem](#jane_orchestratorroutingnewitem)
- [jane_orchestrator.routing.NewItem.__init__](#jane_orchestratorroutingnewitem__init__)
- [jane_orchestrator.routing.NewItem.stage_id](#jane_orchestratorroutingnewitemstage_id)
- [jane_orchestrator.routing.NewItem.item_key](#jane_orchestratorroutingnewitemitem_key)
- [jane_orchestrator.routing.NewItem.inputs](#jane_orchestratorroutingnewiteminputs)
- [jane_orchestrator.routing.NewItem.material](#jane_orchestratorroutingnewitemmaterial)
- [jane_orchestrator.routing.NewItem.upstream_item_id](#jane_orchestratorroutingnewitemupstream_item_id)
- [jane_orchestrator.routing.UnknownDecision](#jane_orchestratorroutingunknowndecision)
- [jane_orchestrator.routing.UnknownDecision.__init__](#jane_orchestratorroutingunknowndecision__init__)
- [jane_orchestrator.routing.UnknownDecision.unknown](#jane_orchestratorroutingunknowndecisionunknown)
- [jane_orchestrator.routing.UnknownDecision.forwarded](#jane_orchestratorroutingunknowndecisionforwarded)
- [jane_orchestrator.routing.UnknownDecision.reason](#jane_orchestratorroutingunknowndecisionreason)
- [jane_orchestrator.routing.collect_stage_id](#jane_orchestratorroutingcollect_stage_id)
- [jane_orchestrator.routing.material_of](#jane_orchestratorroutingmaterial_of)
- [jane_orchestrator.routing.route_material](#jane_orchestratorroutingroute_material)
- [jane_orchestrator.routing.result_context](#jane_orchestratorroutingresult_context)
- [jane_orchestrator.routing.route_result](#jane_orchestratorroutingroute_result)

## jane_orchestrator.routing.NewItem

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:34](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L34).

```python
class NewItem:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [stage_id](jane_orchestrator.routing.md#jane_orchestratorroutingnewitemstage_id) | Поле | ні |
| [item_key](jane_orchestrator.routing.md#jane_orchestratorroutingnewitemitem_key) | Поле | ні |
| [inputs](jane_orchestrator.routing.md#jane_orchestratorroutingnewiteminputs) | Поле | ні |
| [material](jane_orchestrator.routing.md#jane_orchestratorroutingnewitemmaterial) | Поле | ні |
| [upstream_item_id](jane_orchestrator.routing.md#jane_orchestratorroutingnewitemupstream_item_id) | Поле | ні |
| [__init__](jane_orchestrator.routing.md#jane_orchestratorroutingnewitem__init__) | Конструктор dataclass | ні |

## jane_orchestrator.routing.NewItem.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:34](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L34).

```python
def __init__(self, stage_id: str, item_key: str, inputs: list[dict[str, Any]], material: dict[str, Any] | None = None, upstream_item_id: str | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stage_id` | `str` | `—` | positional-or-keyword |
| `item_key` | `str` | `—` | positional-or-keyword |
| `inputs` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `material` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `upstream_item_id` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.routing.NewItem.stage_id

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:35](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L35).

```python
stage_id: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.NewItem.item_key

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:36](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L36).

```python
item_key: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.NewItem.inputs

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:37](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L37).

```python
inputs: list[dict[str, Any]]
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.NewItem.material

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:38](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L38).

```python
material: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.NewItem.upstream_item_id

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:39](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L39).

```python
upstream_item_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.UnknownDecision

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:43](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L43).

```python
class UnknownDecision:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [unknown](jane_orchestrator.routing.md#jane_orchestratorroutingunknowndecisionunknown) | Поле | ні |
| [forwarded](jane_orchestrator.routing.md#jane_orchestratorroutingunknowndecisionforwarded) | Поле | ні |
| [reason](jane_orchestrator.routing.md#jane_orchestratorroutingunknowndecisionreason) | Поле | ні |
| [__init__](jane_orchestrator.routing.md#jane_orchestratorroutingunknowndecision__init__) | Конструктор dataclass | ні |

## jane_orchestrator.routing.UnknownDecision.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:43](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L43).

```python
def __init__(self, unknown: bool, forwarded: bool, reason: str = '') -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `unknown` | `bool` | `—` | positional-or-keyword |
| `forwarded` | `bool` | `—` | positional-or-keyword |
| `reason` | `str` | `''` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.routing.UnknownDecision.unknown

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:44](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L44).

```python
unknown: bool
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.UnknownDecision.forwarded

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:45](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L45).

```python
forwarded: bool
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.UnknownDecision.reason

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:46](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L46).

```python
reason: str = ''
```

Доступ: читання — так; запис — так.

## jane_orchestrator.routing.collect_stage_id

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:55](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L55).

```python
def collect_stage_id(config: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_orchestrator.routing.material_of

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:59](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L59).

```python
def material_of(inputs: Sequence[Mapping[str, Any]] | None) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `inputs` | `Sequence[Mapping[str, Any]] \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Опис із вихідного коду

```text
The material an item is about (MaterialInput, or the material attached to EntitiesInput).
```

## jane_orchestrator.routing.route_material

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:67](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L67).

```python
def route_material(config: Mapping[str, Any], source_id: str, material: dict[str, Any], forward_unknown: bool, from_stage: str | None=None) -> MaterialRouting:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `forward_unknown` | `bool` | `—` | positional-or-keyword |
| `from_stage` | `str \| None` | `None` | positional-or-keyword |

Результат: `MaterialRouting`.

### Опис із вихідного коду

```text
Items for a material emitted by the collect stage (or injected at ``from_stage`` on reprocessing).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:152](../../../../../../services/orchestrator/tests/test_logic.py#L152).

```python
r = route_material(task, "shop-example", prod, forward_unknown=False)
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:156](../../../../../../services/orchestrator/tests/test_logic.py#L156).

```python
r = route_material(task, "shop-example", gift, forward_unknown=False)
```

## jane_orchestrator.routing.result_context

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:128](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L128).

```python
def result_context(result: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `result` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.routing.route_result

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/routing.py:147](../../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L147).

```python
def route_result(config: Mapping[str, Any], source_id: str, stage_id: str, upstream_item_id: str, inputs: Sequence[Mapping[str, Any]] | None, result: Mapping[str, Any]) -> list[NewItem]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |
| `stage_id` | `str` | `—` | positional-or-keyword |
| `upstream_item_id` | `str` | `—` | positional-or-keyword |
| `inputs` | `Sequence[Mapping[str, Any]] \| None` | `—` | positional-or-keyword |
| `result` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `list[NewItem]`.

### Опис із вихідного коду

```text
Items created by a completed handler item with ``result`` (HandlerResult).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:201](../../../../../../services/orchestrator/tests/test_logic.py#L201).

```python
items = route_result(task, "shop-example", "extract-products", "itm_1", inputs, ok)
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:215](../../../../../../services/orchestrator/tests/test_logic.py#L215).

```python
items = route_result(task, "shop-example", "extract-products", "itm_2", inputs, bad)
```
