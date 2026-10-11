# Модуль `jane_kit.schemas`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/schemas.py](../../../../../libs/jane-kit/src/jane_kit/schemas.py). Не редагуйте вручну.

Validation against the JSON Schemas of the contracts (``contracts/schemas``, WP-00) - R17.

Services never keep their own copies of contract documents: they validate with the contract files. One class for every service:

* :class:`ContractSchemas` - ``contracts/schemas/**.schema.json`` (cross-file ``$ref`` resolved from the files) and, optionally, one OpenAPI document of ``contracts/openapi`` (its components and request bodies); validators are cached; errors come sorted by instance path as :class:`~jane_kit.errors.FieldError` with RFC 6901 pointers (``prefix`` + path), or raised as ``422 validation_failed`` (:meth:`ContractSchemas.validate`);
* :meth:`ContractSchemas.locate` - where the contracts are: the service's setting, ``JANE_CONTRACTS_DIR``, the checkout, then the image fallbacks (``/app/contracts``); a missing directory stops the service at start (:class:`ContractsNotFound` names the setting).

``format_check=True`` also checks ``format`` (``date-time``, ``uri``... as far as the validators are installed); the validation of a service keeps the mode it had, so API behaviour does not change.

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.schemas` |
| Код | [schemas.py:53](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L53) |

```python
class ContractSchemas: ...
```

Validators over the contract schemas of ``root`` (``contracts/``); see the module docstring.

#### Конструктор `ContractSchemas.__init__`

```python
def __init__(
    self,
    root: Path,
    *,
    openapi: str | None = None,
    format_check: bool = False,
) -> None: ...
```

Код: [schemas.py:56](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L56).

#### Метод `ContractSchemas.locate`

```python
@classmethod
def locate(
    cls,
    configured: Path | None,
    *,
    setting: str,
    marker: str = 'schemas',
    openapi: str | None = None,
    format_check: bool = False,
    start: Path | None = None,
    fallbacks: Sequence[Path] = (Path('/app/contracts'),),
) -> Self: ...
```

The contracts of ``configured`` (a service setting), else of ``JANE_CONTRACTS_DIR`` / the checkout (searched from ``start``), else of ``fallbacks``; the directory must contain ``marker``.

Винятки в коді методу: `ContractsNotFound`.

Код: [schemas.py:67](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L67).

#### Метод `ContractSchemas.uri`

```python
def uri(self, ref: str) -> str: ...
```

Absolute URI of ``ref``: ``x.schema.json`` / ``common/y.schema.json#/$defs/Z`` (relative to ``contracts/schemas``) or an absolute ``file://``/``https://`` URI (returned as is).

Код: [schemas.py:87](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L87).

#### Метод `ContractSchemas.component`

```python
def component(self, name: str) -> str: ...
```

URI of ``#/components/schemas/<name>`` of the OpenAPI document.

Винятки в коді методу: `ValueError`.

Код: [schemas.py:95](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L95).

#### Метод `ContractSchemas.request_schema_uri`

```python
def request_schema_uri(self, method: str, path: str, media: str = 'application/json') -> str: ...
```

URI of the request body schema of an operation of the OpenAPI document.

Винятки в коді методу: `ValueError`.

Код: [schemas.py:101](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L101).

#### Метод `ContractSchemas.validator`

```python
def validator(self, ref: str) -> Draft202012Validator: ...
```

Код: [schemas.py:110](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L110).

#### Метод `ContractSchemas.iter_errors`

```python
def iter_errors(self, ref: str, instance: Any) -> list[ValidationError]: ...
```

Errors sorted by instance path.

Код: [schemas.py:118](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L118).

#### Метод `ContractSchemas.field_errors`

```python
def field_errors(
    self,
    ref: str,
    instance: Any,
    prefix: str = '',
    *,
    code: str | Callable[[ValidationError], str] = 'schema',
    limit: int | None = None,
    message_max: int | None = None,
    best: bool = False,
    explain: Explain | None = None,
) -> list[FieldError]: ...
```

:class:`FieldError` per error: ``pointer`` = ``prefix`` + RFC 6901 path (``/`` for the root when no prefix), ``code`` (or ``code(error)``), the message cut at ``message_max``; ``best`` - a failed ``oneOf``/``anyOf`` reports its best sub-error; at most ``limit`` errors.

Код: [schemas.py:122](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L122).

#### Метод `ContractSchemas.validate`

```python
def validate(
    self,
    ref: str,
    instance: Any,
    prefix: str = '',
    *,
    detail: str = '',
    **options: Any,
) -> None: ...
```

Raise ``422 validation_failed`` with :meth:`field_errors` if ``instance`` does not match ``ref``.

Винятки в коді методу: `ValidationFailed`.

Код: [schemas.py:159](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L159).

### Клас `ContractsNotFound`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.schemas` |
| Успадкування | `RuntimeError` |
| Код | [schemas.py:34](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L34) |

```python
class ContractsNotFound(RuntimeError): ...
```

The contracts directory is not available (misconfigured deployment).

## Функції

### Функція `json_pointer`

```python
def json_pointer(path: Iterable[Any], prefix: str = '') -> str: ...
```

RFC 6901 pointer of an instance path (``~`` -> ``~0``, ``/`` -> ``~1``).

Код: [schemas.py:38](../../../../../libs/jane-kit/src/jane_kit/schemas.py#L38).
