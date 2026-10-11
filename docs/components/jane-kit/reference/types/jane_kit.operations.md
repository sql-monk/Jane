# Модуль `jane_kit.operations`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/operations.py](../../../../../libs/jane-kit/src/jane_kit/operations.py). Не редагуйте вручну.

Per-module configuration and durable sampled telemetry; no neighbouring databases.

## Зміст

- [Клас `ConfigurationUpdate`](#клас-configurationupdate)
- [Клас `Operations`](#клас-operations)
- [Функція `operations_path`](#функція-operations_path)
- [Функція `read_overrides`](#функція-read_overrides)
- [Функція `flatten`](#функція-flatten)
- [Функція `unflatten`](#функція-unflatten)
- [Функція `install_operations`](#функція-install_operations)

## Класи

### Клас `ConfigurationUpdate`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.operations` |
| Успадкування | `BaseModel` |
| Код | [operations.py:83](../../../../../libs/jane-kit/src/jane_kit/operations.py#L83) |

```python
class ConfigurationUpdate(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `values` | `dict[str, bool \| int \| float \| str]` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='forbid', strict=True)` |  |

### Клас `Operations`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.operations` |
| Код | [operations.py:88](../../../../../libs/jane-kit/src/jane_kit/operations.py#L88) |

```python
class Operations: ...
```

#### Конструктор `Operations.__init__`

```python
def __init__(self, app: FastAPI, settings: Any, resolved: Any) -> None: ...
```

Код: [operations.py:89](../../../../../libs/jane-kit/src/jane_kit/operations.py#L89).

#### Метод `Operations.lifespan`

```python
@asynccontextmanager
async def lifespan(self) -> AsyncIterator[None]: ...
```

Код: [operations.py:95](../../../../../libs/jane-kit/src/jane_kit/operations.py#L95).

#### Метод `Operations.connect`

```python
@contextmanager
def connect(self) -> Iterator[sqlite3.Connection]: ...
```

Код: [operations.py:105](../../../../../libs/jane-kit/src/jane_kit/operations.py#L105).

#### Метод `Operations.initialize`

```python
def initialize(self) -> None: ...
```

Код: [operations.py:114](../../../../../libs/jane-kit/src/jane_kit/operations.py#L114).

#### Метод `Operations.fields`

```python
def fields(self) -> list[dict[str, Any]]: ...
```

Код: [operations.py:133](../../../../../libs/jane-kit/src/jane_kit/operations.py#L133).

#### Метод `Operations.configuration`

```python
def configuration(self) -> tuple[dict[str, Any], str]: ...
```

Код: [operations.py:190](../../../../../libs/jane-kit/src/jane_kit/operations.py#L190).

#### Метод `Operations.save`

```python
def save(
    self,
    values: dict[str, Any],
    expected: str | None,
    actor: str,
) -> tuple[dict[str, Any], str]: ...
```

Винятки в коді методу: `JaneError`, `ValidationFailed`.

Код: [operations.py:215](../../../../../libs/jane-kit/src/jane_kit/operations.py#L215).

#### Метод `Operations.definitions`

```python
def definitions(self) -> list[dict[str, str]]: ...
```

Код: [operations.py:269](../../../../../libs/jane-kit/src/jane_kit/operations.py#L269).

#### Метод `Operations.sample`

```python
def sample(self) -> None: ...
```

Код: [operations.py:282](../../../../../libs/jane-kit/src/jane_kit/operations.py#L282).

#### Метод `Operations.sample_loop`

```python
async def sample_loop(self) -> None: ...
```

Код: [operations.py:351](../../../../../libs/jane-kit/src/jane_kit/operations.py#L351).

#### Метод `Operations.telemetry`

```python
def telemetry(
    self,
    since: datetime | None,
    until: datetime | None,
    limit: int,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `BadRequest`.

Код: [operations.py:359](../../../../../libs/jane-kit/src/jane_kit/operations.py#L359).

## Функції

### Функція `operations_path`

```python
def operations_path(settings: Any) -> Path: ...
```

Код: [operations.py:44](../../../../../libs/jane-kit/src/jane_kit/operations.py#L44).

### Функція `read_overrides`

```python
def read_overrides(settings: Any) -> dict[str, Any]: ...
```

Код: [operations.py:52](../../../../../libs/jane-kit/src/jane_kit/operations.py#L52).

### Функція `flatten`

```python
def flatten(value: dict[str, Any], prefix: str = '') -> dict[str, Any]: ...
```

Код: [operations.py:61](../../../../../libs/jane-kit/src/jane_kit/operations.py#L61).

### Функція `unflatten`

```python
def unflatten(value: dict[str, Any]) -> dict[str, Any]: ...
```

Код: [operations.py:72](../../../../../libs/jane-kit/src/jane_kit/operations.py#L72).

### Функція `install_operations`

```python
def install_operations(app: FastAPI, settings: Any, resolved: Any) -> Operations: ...
```

Код: [operations.py:396](../../../../../libs/jane-kit/src/jane_kit/operations.py#L396).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `EDITABLE_SETTINGS` | — | `{'log_level', 'health_check_timeout_ms', 'render_enabled', 'render_wait_until',` |  |
