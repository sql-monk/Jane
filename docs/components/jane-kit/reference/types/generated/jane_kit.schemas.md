# jane_kit.schemas

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.schemas.ContractsNotFound](#jane_kitschemascontractsnotfound)
- [jane_kit.schemas.json_pointer](#jane_kitschemasjson_pointer)
- [jane_kit.schemas.ContractSchemas](#jane_kitschemascontractschemas)
- [jane_kit.schemas.ContractSchemas.__init__](#jane_kitschemascontractschemas__init__)
- [jane_kit.schemas.ContractSchemas.root](#jane_kitschemascontractschemasroot)
- [jane_kit.schemas.ContractSchemas.schemas_dir](#jane_kitschemascontractschemasschemas_dir)
- [jane_kit.schemas.ContractSchemas.spec](#jane_kitschemascontractschemasspec)
- [jane_kit.schemas.ContractSchemas.registry](#jane_kitschemascontractschemasregistry)
- [jane_kit.schemas.ContractSchemas.format_checker](#jane_kitschemascontractschemasformat_checker)
- [jane_kit.schemas.ContractSchemas.locate](#jane_kitschemascontractschemaslocate)
- [jane_kit.schemas.ContractSchemas.uri](#jane_kitschemascontractschemasuri)
- [jane_kit.schemas.ContractSchemas.component](#jane_kitschemascontractschemascomponent)
- [jane_kit.schemas.ContractSchemas.request_schema_uri](#jane_kitschemascontractschemasrequest_schema_uri)
- [jane_kit.schemas.ContractSchemas.validator](#jane_kitschemascontractschemasvalidator)
- [jane_kit.schemas.ContractSchemas.iter_errors](#jane_kitschemascontractschemasiter_errors)
- [jane_kit.schemas.ContractSchemas.field_errors](#jane_kitschemascontractschemasfield_errors)
- [jane_kit.schemas.ContractSchemas.validate](#jane_kitschemascontractschemasvalidate)

## jane_kit.schemas.ContractsNotFound

**Клас.** Код: [libs/jane-kit/src/jane_kit/schemas.py:34](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L34).

```python
class ContractsNotFound(RuntimeError):
```

Базові типи / інтерфейси: `RuntimeError`.

### Опис із вихідного коду

```text
The contracts directory is not available (misconfigured deployment).
```

## jane_kit.schemas.json_pointer

**Функція.** Код: [libs/jane-kit/src/jane_kit/schemas.py:38](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L38).

```python
def json_pointer(path: Iterable[Any], prefix: str='') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `Iterable[Any]` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
RFC 6901 pointer of an instance path (``~`` -> ``~0``, ``/`` -> ``~1``).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:46](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L46).

```python
assert json_pointer(["a/b", "c~d", 0], "/p") == "/p/a~1b/c~0d/0"
```

## jane_kit.schemas.ContractSchemas

**Клас.** Код: [libs/jane-kit/src/jane_kit/schemas.py:53](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L53).

```python
class ContractSchemas:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.schemas.md#jane_kitschemascontractschemas__init__) | Конструктор | ні |
| [root](jane_kit.schemas.md#jane_kitschemascontractschemasroot) | Поле екземпляра | ні |
| [schemas_dir](jane_kit.schemas.md#jane_kitschemascontractschemasschemas_dir) | Поле екземпляра | ні |
| [spec](jane_kit.schemas.md#jane_kitschemascontractschemasspec) | Поле екземпляра | ні |
| [registry](jane_kit.schemas.md#jane_kitschemascontractschemasregistry) | Поле екземпляра | ні |
| [format_checker](jane_kit.schemas.md#jane_kitschemascontractschemasformat_checker) | Поле екземпляра | ні |
| [locate](jane_kit.schemas.md#jane_kitschemascontractschemaslocate) | Метод | ні |
| [uri](jane_kit.schemas.md#jane_kitschemascontractschemasuri) | Метод | ні |
| [component](jane_kit.schemas.md#jane_kitschemascontractschemascomponent) | Метод | ні |
| [request_schema_uri](jane_kit.schemas.md#jane_kitschemascontractschemasrequest_schema_uri) | Метод | ні |
| [validator](jane_kit.schemas.md#jane_kitschemascontractschemasvalidator) | Метод | ні |
| [iter_errors](jane_kit.schemas.md#jane_kitschemascontractschemasiter_errors) | Метод | ні |
| [field_errors](jane_kit.schemas.md#jane_kitschemascontractschemasfield_errors) | Метод | ні |
| [validate](jane_kit.schemas.md#jane_kitschemascontractschemasvalidate) | Метод | ні |

### Опис із вихідного коду

```text
Validators over the contract schemas of ``root`` (``contracts/``); see the module docstring.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:29](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L29).

```python
schemas = ContractSchemas(ROOT)
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:51](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L51).

```python
schemas = ContractSchemas(ROOT, openapi="orchestrator.v1.yaml")
```

## jane_kit.schemas.ContractSchemas.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/schemas.py:56](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L56).

```python
def __init__(self, root: Path, *, openapi: str | None=None, format_check: bool=False) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `openapi` | `str \| None` | `None` | keyword-only |
| `format_check` | `bool` | `False` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:29](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L29).

```python
schemas = ContractSchemas(ROOT)
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:51](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L51).

```python
schemas = ContractSchemas(ROOT, openapi="orchestrator.v1.yaml")
```

## jane_kit.schemas.ContractSchemas.root

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/schemas.py:57](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L57).

```python
self.root = Path(root)
```

## jane_kit.schemas.ContractSchemas.schemas_dir

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/schemas.py:58](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L58).

```python
self.schemas_dir = (self.root / 'schemas').resolve()
```

## jane_kit.schemas.ContractSchemas.spec

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/schemas.py:59](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L59).

```python
self.spec = OpenAPISpec.load(self.root / 'openapi' / openapi) if openapi else None
```

## jane_kit.schemas.ContractSchemas.registry

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/schemas.py:60](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L60).

```python
self.registry: Registry[Any] = self.spec.registry if self.spec is not None else Registry(retrieve=OpenAPISpec._retrieve)
```

## jane_kit.schemas.ContractSchemas.format_checker

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/schemas.py:63](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L63).

```python
self.format_checker = FormatChecker() if format_check else None
```

## jane_kit.schemas.ContractSchemas.locate

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:67](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L67).

```python
def locate(cls, configured: Path | None, *, setting: str, marker: str='schemas', openapi: str | None=None, format_check: bool=False, start: Path | None=None, fallbacks: Sequence[Path]=(Path('/app/contracts'),)) -> Self:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `configured` | `Path \| None` | `—` | positional-or-keyword |
| `setting` | `str` | `—` | keyword-only |
| `marker` | `str` | `'schemas'` | keyword-only |
| `openapi` | `str \| None` | `None` | keyword-only |
| `format_check` | `bool` | `False` | keyword-only |
| `start` | `Path \| None` | `None` | keyword-only |
| `fallbacks` | `Sequence[Path]` | `(Path('/app/contracts'),)` | keyword-only |

Результат: `Self`.

Явні `raise` у тілі: `ContractsNotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The contracts of ``configured`` (a service setting), else of ``JANE_CONTRACTS_DIR`` / the checkout
(searched from ``start``), else of ``fallbacks``; the directory must contain ``marker``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:61](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L61).

```python
found = ContractSchemas.locate(
        None, setting="S", marker="schemas/package-manifest.schema.json", start=Path(__file__).parent
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:59](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L59).

```python
ContractSchemas.locate(tmp_path, setting="JANE_X_CONTRACTS_DIR")
```

## jane_kit.schemas.ContractSchemas.uri

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:87](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L87).

```python
def uri(self, ref: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Absolute URI of ``ref``: ``x.schema.json`` / ``common/y.schema.json#/$defs/Z`` (relative to
``contracts/schemas``) or an absolute ``file://``/``https://`` URI (returned as is).
```

## jane_kit.schemas.ContractSchemas.component

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:95](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L95).

```python
def component(self, name: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |

Результат: `str`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
URI of ``#/components/schemas/<name>`` of the OpenAPI document.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:77](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L77).

```python
assert schemas.errors(schemas.component("CollectionRequest"), {}) != []
```

## jane_kit.schemas.ContractSchemas.request_schema_uri

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:101](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L101).

```python
def request_schema_uri(self, method: str, path: str, media: str='application/json') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `media` | `str` | `'application/json'` | positional-or-keyword |

Результат: `str`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
URI of the request body schema of an operation of the OpenAPI document.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:52](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L52).

```python
uri = schemas.request_schema_uri("PUT", "/v1/sources/shop")
```

## jane_kit.schemas.ContractSchemas.validator

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:110](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L110).

```python
def validator(self, ref: str) -> Draft202012Validator:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |

Результат: `Draft202012Validator`.

## jane_kit.schemas.ContractSchemas.iter_errors

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:118](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L118).

```python
def iter_errors(self, ref: str, instance: Any) -> list[ValidationError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |

Результат: `list[ValidationError]`.

### Опис із вихідного коду

```text
Errors sorted by instance path.
```

## jane_kit.schemas.ContractSchemas.field_errors

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:122](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L122).

```python
def field_errors(self, ref: str, instance: Any, prefix: str='', *, code: str | Callable[[ValidationError], str]='schema', limit: int | None=None, message_max: int | None=None, best: bool=False, explain: Explain | None=None) -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |
| `code` | `str \| Callable[[ValidationError], str]` | `'schema'` | keyword-only |
| `limit` | `int \| None` | `None` | keyword-only |
| `message_max` | `int \| None` | `None` | keyword-only |
| `best` | `bool` | `False` | keyword-only |
| `explain` | `Explain \| None` | `None` | keyword-only |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
:class:`FieldError` per error: ``pointer`` = ``prefix`` + RFC 6901 path (``/`` for the root when no
prefix), ``code`` (or ``code(error)``), the message cut at ``message_max``; ``best`` - a failed
``oneOf``/``anyOf`` reports its best sub-error; at most ``limit`` errors.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:38](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L38).

```python
errors = schemas.field_errors("material.schema.json", broken, "/inputs/0/material", best=True, limit=50)
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:44](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L44).

```python
report = schemas.field_errors("handler-result.schema.json#/$defs/TestReport", {}, limit=1)
```

## jane_kit.schemas.ContractSchemas.validate

**Метод.** Код: [libs/jane-kit/src/jane_kit/schemas.py:159](../../../../../../libs/jane-kit/src/jane_kit/schemas.py#L159).

```python
def validate(self, ref: str, instance: Any, prefix: str='', *, detail: str='', **options: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |
| `detail` | `str` | `''` | keyword-only |
| `options` | `Any` | `—` | var-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Raise ``422 validation_failed`` with :meth:`field_errors` if ``instance`` does not match ``ref``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:42](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L42).

```python
schemas.validate("material.schema.json", broken, detail="bad material")
```
