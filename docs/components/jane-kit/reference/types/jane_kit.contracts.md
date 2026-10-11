# Модуль `jane_kit.contracts`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/contracts.py](../../../../../libs/jane-kit/src/jane_kit/contracts.py). Не редагуйте вручну.

Contract helpers over the OpenAPI 3.1 documents in ``contracts/openapi/`` (WP-00).

* :class:`OpenAPISpec` - load a spec (YAML/JSON) with cross-file ``$ref`` (``common.yaml``, ``../schemas/*.schema.json``, ``../examples/*``), list operations (including ``$ref``'d path items), validate requests/responses (schemas are JSON Schema 2020-12).
* :class:`ContractClient` - wraps an httpx client (e.g. FastAPI ``TestClient``) and validates every response of the real service against the spec. Basis of ``@pytest.mark.contract`` tests.
* :func:`build_mock_app` - an ASGI mock of a neighbour service generated from its spec: first example of the first 2xx response; ``Prefer: code=404`` / ``Prefer: example=<name>`` select another (same convention as ``contracts/tools/mock.py`` and Prism); invalid request bodies get 422.
* :func:`find_specs` - service specs under ``contracts/openapi`` (documents with ``paths``).

## Зміст

- [Клас `ContractClient`](#клас-contractclient)
- [Клас `ContractViolation`](#клас-contractviolation)
- [Клас `Loc`](#клас-loc)
- [Клас `OpenAPISpec`](#клас-openapispec)
- [Клас `Operation`](#клас-operation)
- [Функція `build_mock_app`](#функція-build_mock_app)
- [Функція `contracts_dir`](#функція-contracts_dir)
- [Функція `example_from_schema`](#функція-example_from_schema)
- [Функція `find_specs`](#функція-find_specs)

## Класи

### Клас `ContractClient`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.contracts` |
| Код | [contracts.py:323](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L323) |

```python
class ContractClient: ...
```

Validates every response of a real service against its contract.

``ContractClient(spec, TestClient(app)).get("/v1/jobs/1")`` returns the httpx response or raises :class:`ContractViolation`.

#### Конструктор `ContractClient.__init__`

```python
def __init__(self, spec: OpenAPISpec, client: httpx.Client) -> None: ...
```

Код: [contracts.py:330](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L330).

#### Метод `ContractClient.request`

```python
def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response: ...
```

Код: [contracts.py:335](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L335).

#### Метод `ContractClient.get`

```python
def get(self, url: str, **kw: Any) -> httpx.Response: ...
```

Код: [contracts.py:351](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L351).

#### Метод `ContractClient.post`

```python
def post(self, url: str, **kw: Any) -> httpx.Response: ...
```

Код: [contracts.py:354](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L354).

#### Метод `ContractClient.put`

```python
def put(self, url: str, **kw: Any) -> httpx.Response: ...
```

Код: [contracts.py:357](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L357).

#### Метод `ContractClient.patch`

```python
def patch(self, url: str, **kw: Any) -> httpx.Response: ...
```

Код: [contracts.py:360](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L360).

#### Метод `ContractClient.delete`

```python
def delete(self, url: str, **kw: Any) -> httpx.Response: ...
```

Код: [contracts.py:363](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L363).

#### Метод `ContractClient.uncovered`

```python
def uncovered(self) -> list[str]: ...
```

Operations never called through this client (coverage hint for contract tests).

Код: [contracts.py:366](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L366).

### Клас `ContractViolation`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.contracts` |
| Успадкування | `AssertionError` |
| Код | [contracts.py:57](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L57) |

```python
class ContractViolation(AssertionError): ...
```

The request or response does not match the contract.

### Клас `Loc`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.contracts` |
| Код | [contracts.py:84](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L84) |

```python
@dataclass(frozen=True)
class Loc: ...
```

A node of a contract document together with where it lives (for correct relative ``$ref``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `uri` | `str` | — | читання |  |
| `pointer` | `str` | — | читання |  |
| `node` | `Any` | `field(compare=False, repr=False)` | читання |  |
| `ref` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Loc.child`

```python
def child(self, *tokens: str | int) -> Loc: ...
```

Код: [contracts.py:95](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L95).

### Клас `OpenAPISpec`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.contracts` |
| Код | [contracts.py:127](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L127) |

```python
class OpenAPISpec: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `operations` | `list[Operation]` | — | читання (властивість) |  |

#### Конструктор `OpenAPISpec.__init__`

```python
def __init__(self, document: Mapping[str, Any], base_uri: str) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [contracts.py:128](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L128).

#### Метод `OpenAPISpec.load`

```python
@classmethod
def load(cls, path: str | Path) -> OpenAPISpec: ...
```

Код: [contracts.py:138](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L138).

#### Метод `OpenAPISpec.root`

```python
def root(self) -> Loc: ...
```

Код: [contracts.py:148](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L148).

#### Метод `OpenAPISpec.lookup`

```python
def lookup(self, uri: str) -> Loc: ...
```

Код: [contracts.py:151](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L151).

#### Метод `OpenAPISpec.follow`

```python
def follow(self, loc: Loc) -> Loc: ...
```

Follow ``$ref`` chains of non-schema objects (path items, responses, examples...).

Винятки в коді методу: `ValueError`.

Код: [contracts.py:156](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L156).

#### Метод `OpenAPISpec.resolve`

```python
def resolve(self, node: Any) -> Any: ...
```

Follow ``$ref`` for a node that lives in the root document.

Код: [contracts.py:164](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L164).

#### Метод `OpenAPISpec.operation`

```python
def operation(self, method: str, path: str) -> Operation: ...
```

Find the operation for a concrete path (``/v1/jobs/abc``) or a template.

Винятки в коді методу: `ContractViolation`.

Код: [contracts.py:201](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L201).

#### Метод `OpenAPISpec.by_id`

```python
def by_id(self, operation_id: str) -> Operation: ...
```

Винятки в коді методу: `KeyError`.

Код: [contracts.py:214](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L214).

#### Метод `OpenAPISpec.validate_at`

```python
def validate_at(self, schema_uri: str, instance: Any, what: str = 'instance') -> None: ...
```

Validate ``instance`` against the schema at ``schema_uri`` (``<doc>#<pointer>``).

Винятки в коді методу: `ContractViolation`.

Код: [contracts.py:221](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L221).

#### Метод `OpenAPISpec.validate_component`

```python
def validate_component(self, name: str, instance: Any) -> None: ...
```

Validate against ``#/components/schemas/<name>`` of this document.

Код: [contracts.py:232](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L232).

#### Метод `OpenAPISpec.response`

```python
def response(self, op: Operation, status: int) -> Loc: ...
```

Винятки в коді методу: `ContractViolation`.

Код: [contracts.py:236](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L236).

#### Метод `OpenAPISpec.validate_response`

```python
def validate_response(
    self,
    method: str,
    path: str,
    status: int,
    body: Any,
    content_type: str | None = 'application/json',
) -> Operation: ...
```

Винятки в коді методу: `ContractViolation`.

Код: [contracts.py:245](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L245).

#### Метод `OpenAPISpec.validate_request`

```python
def validate_request(
    self,
    method: str,
    path: str,
    body: Any,
    content_type: str = 'application/json',
) -> Operation: ...
```

Винятки в коді методу: `ContractViolation`.

Код: [contracts.py:264](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L264).

### Клас `Operation`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.contracts` |
| Код | [contracts.py:104](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L104) |

```python
@dataclass(frozen=True)
class Operation: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `method` | `str` | — | читання |  |
| `path` | `str` | — | читання |  |
| `operation_id` | `str \| None` | — | читання |  |
| `loc` | `Loc` | — | читання |  |
| `parameters` | `tuple[Mapping[str, Any], ...]` | `()` | читання |  |
| `spec` | `Mapping[str, Any]` | — | читання (властивість) |  |
| `regex` | `re.Pattern[str]` | — | читання (властивість) |  |
| `literal_weight` | `int` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `build_mock_app`

```python
def build_mock_app(spec: OpenAPISpec) -> Starlette: ...
```

ASGI mock of a service from its contract (see module docstring).

Код: [contracts.py:455](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L455).

### Функція `contracts_dir`

```python
def contracts_dir(start: Path | None = None) -> Path | None: ...
```

``contracts/`` of this checkout: env ``JANE_CONTRACTS_DIR``, else ``<checkout root>/contracts``.

The search stops at the checkout root (nearest ancestor with ``.git``), so a git worktree nested inside another checkout never picks up that checkout's contracts.

Код: [contracts.py:290](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L290).

### Функція `example_from_schema`

```python
def example_from_schema(
    spec: OpenAPISpec,
    schema: Loc | Mapping[str, Any],
    depth: int = 0,
) -> Any: ...
```

Deterministic minimal instance of a schema (examples > default > const > enum > type).

Код: [contracts.py:382](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L382).

### Функція `find_specs`

```python
def find_specs(contracts_dir: str | Path) -> Iterator[Path]: ...
```

OpenAPI documents that describe a service (have ``paths``), e.g. ``contracts/openapi/*.v1.yaml``.

Код: [contracts.py:307](../../../../../libs/jane-kit/src/jane_kit/contracts.py#L307).
