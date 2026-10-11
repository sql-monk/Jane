# jane_kit.contracts

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.contracts.ContractViolation](#jane_kitcontractscontractviolation)
- [jane_kit.contracts.Loc](#jane_kitcontractsloc)
- [jane_kit.contracts.Loc.__init__](#jane_kitcontractsloc__init__)
- [jane_kit.contracts.Loc.uri](#jane_kitcontractslocuri)
- [jane_kit.contracts.Loc.pointer](#jane_kitcontractslocpointer)
- [jane_kit.contracts.Loc.node](#jane_kitcontractslocnode)
- [jane_kit.contracts.Loc.ref](#jane_kitcontractslocref)
- [jane_kit.contracts.Loc.child](#jane_kitcontractslocchild)
- [jane_kit.contracts.Operation](#jane_kitcontractsoperation)
- [jane_kit.contracts.Operation.__init__](#jane_kitcontractsoperation__init__)
- [jane_kit.contracts.Operation.method](#jane_kitcontractsoperationmethod)
- [jane_kit.contracts.Operation.path](#jane_kitcontractsoperationpath)
- [jane_kit.contracts.Operation.operation_id](#jane_kitcontractsoperationoperation_id)
- [jane_kit.contracts.Operation.loc](#jane_kitcontractsoperationloc)
- [jane_kit.contracts.Operation.parameters](#jane_kitcontractsoperationparameters)
- [jane_kit.contracts.Operation.spec](#jane_kitcontractsoperationspec)
- [jane_kit.contracts.Operation.regex](#jane_kitcontractsoperationregex)
- [jane_kit.contracts.Operation.literal_weight](#jane_kitcontractsoperationliteral_weight)
- [jane_kit.contracts.OpenAPISpec](#jane_kitcontractsopenapispec)
- [jane_kit.contracts.OpenAPISpec.__init__](#jane_kitcontractsopenapispec__init__)
- [jane_kit.contracts.OpenAPISpec.document](#jane_kitcontractsopenapispecdocument)
- [jane_kit.contracts.OpenAPISpec.base_uri](#jane_kitcontractsopenapispecbase_uri)
- [jane_kit.contracts.OpenAPISpec.registry](#jane_kitcontractsopenapispecregistry)
- [jane_kit.contracts.OpenAPISpec.load](#jane_kitcontractsopenapispecload)
- [jane_kit.contracts.OpenAPISpec.root](#jane_kitcontractsopenapispecroot)
- [jane_kit.contracts.OpenAPISpec.lookup](#jane_kitcontractsopenapispeclookup)
- [jane_kit.contracts.OpenAPISpec.follow](#jane_kitcontractsopenapispecfollow)
- [jane_kit.contracts.OpenAPISpec.resolve](#jane_kitcontractsopenapispecresolve)
- [jane_kit.contracts.OpenAPISpec.operations](#jane_kitcontractsopenapispecoperations)
- [jane_kit.contracts.OpenAPISpec.operation](#jane_kitcontractsopenapispecoperation)
- [jane_kit.contracts.OpenAPISpec.by_id](#jane_kitcontractsopenapispecby_id)
- [jane_kit.contracts.OpenAPISpec.validate_at](#jane_kitcontractsopenapispecvalidate_at)
- [jane_kit.contracts.OpenAPISpec.validate_component](#jane_kitcontractsopenapispecvalidate_component)
- [jane_kit.contracts.OpenAPISpec.response](#jane_kitcontractsopenapispecresponse)
- [jane_kit.contracts.OpenAPISpec.validate_response](#jane_kitcontractsopenapispecvalidate_response)
- [jane_kit.contracts.OpenAPISpec.validate_request](#jane_kitcontractsopenapispecvalidate_request)
- [jane_kit.contracts.contracts_dir](#jane_kitcontractscontracts_dir)
- [jane_kit.contracts.find_specs](#jane_kitcontractsfind_specs)
- [jane_kit.contracts.ContractClient](#jane_kitcontractscontractclient)
- [jane_kit.contracts.ContractClient.__init__](#jane_kitcontractscontractclient__init__)
- [jane_kit.contracts.ContractClient.spec](#jane_kitcontractscontractclientspec)
- [jane_kit.contracts.ContractClient.client](#jane_kitcontractscontractclientclient)
- [jane_kit.contracts.ContractClient.seen](#jane_kitcontractscontractclientseen)
- [jane_kit.contracts.ContractClient.request](#jane_kitcontractscontractclientrequest)
- [jane_kit.contracts.ContractClient.get](#jane_kitcontractscontractclientget)
- [jane_kit.contracts.ContractClient.post](#jane_kitcontractscontractclientpost)
- [jane_kit.contracts.ContractClient.put](#jane_kitcontractscontractclientput)
- [jane_kit.contracts.ContractClient.patch](#jane_kitcontractscontractclientpatch)
- [jane_kit.contracts.ContractClient.delete](#jane_kitcontractscontractclientdelete)
- [jane_kit.contracts.ContractClient.uncovered](#jane_kitcontractscontractclientuncovered)
- [jane_kit.contracts.example_from_schema](#jane_kitcontractsexample_from_schema)
- [jane_kit.contracts.build_mock_app](#jane_kitcontractsbuild_mock_app)

## jane_kit.contracts.ContractViolation

**Клас.** Код: [libs/jane-kit/src/jane_kit/contracts.py:57](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L57).

```python
class ContractViolation(AssertionError):
```

Базові типи / інтерфейси: `AssertionError`.

### Опис із вихідного коду

```text
The request or response does not match the contract.
```

## jane_kit.contracts.Loc

**Клас.** Код: [libs/jane-kit/src/jane_kit/contracts.py:84](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L84).

```python
class Loc:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [uri](jane_kit.contracts.md#jane_kitcontractslocuri) | Поле | ні |
| [pointer](jane_kit.contracts.md#jane_kitcontractslocpointer) | Поле | ні |
| [node](jane_kit.contracts.md#jane_kitcontractslocnode) | Поле | ні |
| [ref](jane_kit.contracts.md#jane_kitcontractslocref) | Властивість | ні |
| [child](jane_kit.contracts.md#jane_kitcontractslocchild) | Метод | ні |
| [__init__](jane_kit.contracts.md#jane_kitcontractsloc__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A node of a contract document together with where it lives (for correct relative ``$ref``).
```

## jane_kit.contracts.Loc.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/contracts.py:84](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L84).

```python
def __init__(self, uri: str, pointer: str, node: Any = field(compare=False, repr=False)) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `uri` | `str` | `—` | positional-or-keyword |
| `pointer` | `str` | `—` | positional-or-keyword |
| `node` | `Any` | `field(compare=False, repr=False)` | positional-or-keyword |

Результат: `None`.

## jane_kit.contracts.Loc.uri

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:87](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L87).

```python
uri: str
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Loc.pointer

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:88](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L88).

```python
pointer: str
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Loc.node

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:89](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L89).

```python
node: Any = field(compare=False, repr=False)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "compare": "False",
  "repr": "False"
}
```

## jane_kit.contracts.Loc.ref

**Властивість.** Код: [libs/jane-kit/src/jane_kit/contracts.py:92](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L92).

```python
def ref(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Loc.child

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:95](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L95).

```python
def child(self, *tokens: str | int) -> Loc:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `tokens` | `str \| int` | `—` | var-positional |

Результат: `Loc`.

## jane_kit.contracts.Operation

**Клас.** Код: [libs/jane-kit/src/jane_kit/contracts.py:104](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L104).

```python
class Operation:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [method](jane_kit.contracts.md#jane_kitcontractsoperationmethod) | Поле | ні |
| [path](jane_kit.contracts.md#jane_kitcontractsoperationpath) | Поле | ні |
| [operation_id](jane_kit.contracts.md#jane_kitcontractsoperationoperation_id) | Поле | ні |
| [loc](jane_kit.contracts.md#jane_kitcontractsoperationloc) | Поле | ні |
| [parameters](jane_kit.contracts.md#jane_kitcontractsoperationparameters) | Поле | ні |
| [spec](jane_kit.contracts.md#jane_kitcontractsoperationspec) | Властивість | ні |
| [regex](jane_kit.contracts.md#jane_kitcontractsoperationregex) | Властивість | ні |
| [literal_weight](jane_kit.contracts.md#jane_kitcontractsoperationliteral_weight) | Властивість | ні |
| [__init__](jane_kit.contracts.md#jane_kitcontractsoperation__init__) | Конструктор dataclass | ні |

## jane_kit.contracts.Operation.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/contracts.py:104](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L104).

```python
def __init__(self, method: str, path: str, operation_id: str | None, loc: Loc, parameters: tuple[Mapping[str, Any], ...] = ()) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `operation_id` | `str \| None` | `—` | positional-or-keyword |
| `loc` | `Loc` | `—` | positional-or-keyword |
| `parameters` | `tuple[Mapping[str, Any], ...]` | `()` | positional-or-keyword |

Результат: `None`.

## jane_kit.contracts.Operation.method

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:105](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L105).

```python
method: str
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.path

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:106](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L106).

```python
path: str
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.operation_id

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:107](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L107).

```python
operation_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.loc

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:108](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L108).

```python
loc: Loc
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.parameters

**Поле.** Код: [libs/jane-kit/src/jane_kit/contracts.py:109](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L109).

```python
parameters: tuple[Mapping[str, Any], ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.spec

**Властивість.** Код: [libs/jane-kit/src/jane_kit/contracts.py:112](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L112).

```python
def spec(self) -> Mapping[str, Any]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

Доступ: читання — так; запис — ні.

## jane_kit.contracts.Operation.regex

**Властивість.** Код: [libs/jane-kit/src/jane_kit/contracts.py:117](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L117).

```python
def regex(self) -> re.Pattern[str]:
```

Декоратори: `cached_property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `re.Pattern[str]`.

Доступ: читання — так; запис — так.

## jane_kit.contracts.Operation.literal_weight

**Властивість.** Код: [libs/jane-kit/src/jane_kit/contracts.py:123](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L123).

```python
def literal_weight(self) -> int:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

Доступ: читання — так; запис — ні.

## jane_kit.contracts.OpenAPISpec

**Клас.** Код: [libs/jane-kit/src/jane_kit/contracts.py:127](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L127).

```python
class OpenAPISpec:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.contracts.md#jane_kitcontractsopenapispec__init__) | Конструктор | ні |
| [document](jane_kit.contracts.md#jane_kitcontractsopenapispecdocument) | Поле екземпляра | ні |
| [base_uri](jane_kit.contracts.md#jane_kitcontractsopenapispecbase_uri) | Поле екземпляра | ні |
| [registry](jane_kit.contracts.md#jane_kitcontractsopenapispecregistry) | Поле екземпляра | ні |
| [load](jane_kit.contracts.md#jane_kitcontractsopenapispecload) | Метод | ні |
| [root](jane_kit.contracts.md#jane_kitcontractsopenapispecroot) | Метод | ні |
| [lookup](jane_kit.contracts.md#jane_kitcontractsopenapispeclookup) | Метод | ні |
| [follow](jane_kit.contracts.md#jane_kitcontractsopenapispecfollow) | Метод | ні |
| [resolve](jane_kit.contracts.md#jane_kitcontractsopenapispecresolve) | Метод | ні |
| [operations](jane_kit.contracts.md#jane_kitcontractsopenapispecoperations) | Властивість | ні |
| [operation](jane_kit.contracts.md#jane_kitcontractsopenapispecoperation) | Метод | ні |
| [by_id](jane_kit.contracts.md#jane_kitcontractsopenapispecby_id) | Метод | ні |
| [validate_at](jane_kit.contracts.md#jane_kitcontractsopenapispecvalidate_at) | Метод | ні |
| [validate_component](jane_kit.contracts.md#jane_kitcontractsopenapispecvalidate_component) | Метод | ні |
| [response](jane_kit.contracts.md#jane_kitcontractsopenapispecresponse) | Метод | ні |
| [validate_response](jane_kit.contracts.md#jane_kitcontractsopenapispecvalidate_response) | Метод | ні |
| [validate_request](jane_kit.contracts.md#jane_kitcontractsopenapispecvalidate_request) | Метод | ні |

## jane_kit.contracts.OpenAPISpec.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/contracts.py:128](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L128).

```python
def __init__(self, document: Mapping[str, Any], base_uri: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `document` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `base_uri` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.contracts.OpenAPISpec.document

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:131](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L131).

```python
self.document = document
```

## jane_kit.contracts.OpenAPISpec.base_uri

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:132](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L132).

```python
self.base_uri = base_uri
```

## jane_kit.contracts.OpenAPISpec.registry

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:135](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L135).

```python
self.registry = registry.with_resource(base_uri, root)
```

## jane_kit.contracts.OpenAPISpec.load

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:138](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L138).

```python
def load(cls, path: str | Path) -> OpenAPISpec:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str \| Path` | `—` | positional-or-keyword |

Результат: `OpenAPISpec`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_codegen.py:30](../../../../../../libs/jane-kit/tests/test_codegen.py#L30).

```python
mock = build_mock_app(OpenAPISpec.load(DATA / "openapi.yaml"))
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:22](../../../../../../libs/jane-kit/tests/test_contracts.py#L22).

```python
return OpenAPISpec.load(DATA / "openapi.yaml")
```

## jane_kit.contracts.OpenAPISpec.root

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:148](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L148).

```python
def root(self) -> Loc:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Loc`.

## jane_kit.contracts.OpenAPISpec.lookup

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:151](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L151).

```python
def lookup(self, uri: str) -> Loc:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `uri` | `str` | `—` | positional-or-keyword |

Результат: `Loc`.

## jane_kit.contracts.OpenAPISpec.follow

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:156](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L156).

```python
def follow(self, loc: Loc) -> Loc:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `loc` | `Loc` | `—` | positional-or-keyword |

Результат: `Loc`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Follow ``$ref`` chains of non-schema objects (path items, responses, examples...).
```

## jane_kit.contracts.OpenAPISpec.resolve

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:164](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L164).

```python
def resolve(self, node: Any) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `node` | `Any` | `—` | positional-or-keyword |

Результат: `Any`.

### Опис із вихідного коду

```text
Follow ``$ref`` for a node that lives in the root document.
```

## jane_kit.contracts.OpenAPISpec.operations

**Властивість.** Код: [libs/jane-kit/src/jane_kit/contracts.py:169](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L169).

```python
def operations(self) -> list[Operation]:
```

Декоратори: `cached_property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[Operation]`.

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:26](../../../../../../libs/jane-kit/tests/test_contracts.py#L26).

```python
ids = {o.operation_id for o in spec.operations}
```

## jane_kit.contracts.OpenAPISpec.operation

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:201](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L201).

```python
def operation(self, method: str, path: str) -> Operation:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `Operation`.

Явні `raise` у тілі: `ContractViolation`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Find the operation for a concrete path (``/v1/jobs/abc``) or a template.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:31](../../../../../../libs/jane-kit/tests/test_contracts.py#L31).

```python
spec.operation("DELETE", "/v1/items/abc")
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:28](../../../../../../libs/jane-kit/tests/test_contracts.py#L28).

```python
assert spec.operation("GET", "/v1/items/abc").operation_id == "getItem"
```

## jane_kit.contracts.OpenAPISpec.by_id

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:214](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L214).

```python
def by_id(self, operation_id: str) -> Operation:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `operation_id` | `str` | `—` | positional-or-keyword |

Результат: `Operation`.

Явні `raise` у тілі: `KeyError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.contracts.OpenAPISpec.validate_at

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:221](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L221).

```python
def validate_at(self, schema_uri: str, instance: Any, what: str='instance') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `schema_uri` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `what` | `str` | `'instance'` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ContractViolation`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Validate ``instance`` against the schema at ``schema_uri`` (``<doc>#<pointer>``).
```

## jane_kit.contracts.OpenAPISpec.validate_component

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:232](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L232).

```python
def validate_component(self, name: str, instance: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Validate against ``#/components/schemas/<name>`` of this document.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_contract.py:222](../../../../../../services/registry/tests/test_contract.py#L222).

```python
spec.validate_component("PackageVersion", job["result"])
```

## jane_kit.contracts.OpenAPISpec.response

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:236](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L236).

```python
def response(self, op: Operation, status: int) -> Loc:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `op` | `Operation` | `—` | positional-or-keyword |
| `status` | `int` | `—` | positional-or-keyword |

Результат: `Loc`.

Явні `raise` у тілі: `ContractViolation`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.contracts.OpenAPISpec.validate_response

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:245](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L245).

```python
def validate_response(self, method: str, path: str, status: int, body: Any, content_type: str | None='application/json') -> Operation:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `status` | `int` | `—` | positional-or-keyword |
| `body` | `Any` | `—` | positional-or-keyword |
| `content_type` | `str \| None` | `'application/json'` | positional-or-keyword |

Результат: `Operation`.

Явні `raise` у тілі: `ContractViolation`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:35](../../../../../../libs/jane-kit/tests/test_contracts.py#L35).

```python
spec.validate_response("GET", "/v1/items/1", 200, {"id": "1", "name": "n", "tags": []})
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:41](../../../../../../libs/jane-kit/tests/test_contracts.py#L41).

```python
spec.validate_response(
        "GET",
        "/v1/items/1",
        404,
        {"type": "t", "title": "x", "status": 404, "code": "not_found"},
        "application/problem+json",
    )
```

## jane_kit.contracts.OpenAPISpec.validate_request

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:264](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L264).

```python
def validate_request(self, method: str, path: str, body: Any, content_type: str='application/json') -> Operation:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `body` | `Any` | `—` | positional-or-keyword |
| `content_type` | `str` | `'application/json'` | positional-or-keyword |

Результат: `Operation`.

Явні `raise` у тілі: `ContractViolation`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:59](../../../../../../libs/jane-kit/tests/test_contracts.py#L59).

```python
spec.validate_request("POST", "/v1/items", {"name": "a"})
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:61](../../../../../../libs/jane-kit/tests/test_contracts.py#L61).

```python
spec.validate_request("POST", "/v1/items", {"name": "a", "bogus": 1})
```

## jane_kit.contracts.contracts_dir

**Функція.** Код: [libs/jane-kit/src/jane_kit/contracts.py:290](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L290).

```python
def contracts_dir(start: Path | None=None) -> Path | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `start` | `Path \| None` | `None` | positional-or-keyword |

Результат: `Path | None`.

### Опис із вихідного коду

```text
``contracts/`` of this checkout: env ``JANE_CONTRACTS_DIR``, else ``<checkout root>/contracts``.

The search stops at the checkout root (nearest ancestor with ``.git``), so a git worktree nested
inside another checkout never picks up that checkout's contracts.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth_scopes.py:28](../../../../../../libs/jane-kit/tests/test_auth_scopes.py#L28).

```python
_FOUND = contracts_dir(Path(__file__).parent)
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:148](../../../../../../libs/jane-kit/tests/test_contracts.py#L148).

```python
root = contracts_dir(_Path(__file__).parent)
```

## jane_kit.contracts.find_specs

**Функція.** Код: [libs/jane-kit/src/jane_kit/contracts.py:307](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L307).

```python
def find_specs(contracts_dir: str | Path) -> Iterator[Path]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `contracts_dir` | `str \| Path` | `—` | positional-or-keyword |

Результат: `Iterator[Path]`.

### Опис із вихідного коду

```text
OpenAPI documents that describe a service (have ``paths``), e.g. ``contracts/openapi/*.v1.yaml``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:132](../../../../../../libs/jane-kit/tests/test_contracts.py#L132).

```python
assert list(find_specs(tmp_path / "missing")) == []
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:131](../../../../../../libs/jane-kit/tests/test_contracts.py#L131).

```python
assert [p.name for p in find_specs(tmp_path)] == ["collector.v1.yaml"]
```

## jane_kit.contracts.ContractClient

**Клас.** Код: [libs/jane-kit/src/jane_kit/contracts.py:323](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L323).

```python
class ContractClient:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.contracts.md#jane_kitcontractscontractclient__init__) | Конструктор | ні |
| [spec](jane_kit.contracts.md#jane_kitcontractscontractclientspec) | Поле екземпляра | ні |
| [client](jane_kit.contracts.md#jane_kitcontractscontractclientclient) | Поле екземпляра | ні |
| [seen](jane_kit.contracts.md#jane_kitcontractscontractclientseen) | Поле екземпляра | ні |
| [request](jane_kit.contracts.md#jane_kitcontractscontractclientrequest) | Метод | ні |
| [get](jane_kit.contracts.md#jane_kitcontractscontractclientget) | Метод | ні |
| [post](jane_kit.contracts.md#jane_kitcontractscontractclientpost) | Метод | ні |
| [put](jane_kit.contracts.md#jane_kitcontractscontractclientput) | Метод | ні |
| [patch](jane_kit.contracts.md#jane_kitcontractscontractclientpatch) | Метод | ні |
| [delete](jane_kit.contracts.md#jane_kitcontractscontractclientdelete) | Метод | ні |
| [uncovered](jane_kit.contracts.md#jane_kitcontractscontractclientuncovered) | Метод | ні |

### Опис із вихідного коду

```text
Validates every response of a real service against its contract.

``ContractClient(spec, TestClient(app)).get("/v1/jobs/1")`` returns the httpx response or raises
:class:`ContractViolation`.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:91](../../../../../../libs/jane-kit/tests/test_contracts.py#L91).

```python
c = ContractClient(spec, TestClient(real_app()))
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:100](../../../../../../libs/jane-kit/tests/test_contracts.py#L100).

```python
c = ContractClient(spec, TestClient(real_app(broken=True)))
```

## jane_kit.contracts.ContractClient.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/contracts.py:330](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L330).

```python
def __init__(self, spec: OpenAPISpec, client: httpx.Client) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `spec` | `OpenAPISpec` | `—` | positional-or-keyword |
| `client` | `httpx.Client` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:91](../../../../../../libs/jane-kit/tests/test_contracts.py#L91).

```python
c = ContractClient(spec, TestClient(real_app()))
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:100](../../../../../../libs/jane-kit/tests/test_contracts.py#L100).

```python
c = ContractClient(spec, TestClient(real_app(broken=True)))
```

## jane_kit.contracts.ContractClient.spec

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:331](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L331).

```python
self.spec = spec
```

## jane_kit.contracts.ContractClient.client

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:332](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L332).

```python
self.client = client
```

## jane_kit.contracts.ContractClient.seen

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/contracts.py:333](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L333).

```python
self.seen: set[tuple[str, str, int]] = set()
```

## jane_kit.contracts.ContractClient.request

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:335](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L335).

```python
def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kwargs` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_contract.py:41](../../../../../../services/telegram-collector/tests/test_contract.py#L41).

```python
bad = api.request("POST", "/v1/fetches", content=b"{", headers={"content-type": "application/json"})
```

Контекст і передумови: [services/web-collector/tests/test_contract.py:90](../../../../../../services/web-collector/tests/test_contract.py#L90).

```python
bad = api.request("POST", "/v1/fetches", content=b"{", headers={"content-type": "application/json"})
```

## jane_kit.contracts.ContractClient.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:351](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L351).

```python
def get(self, url: str, **kw: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:94](../../../../../../libs/jane-kit/tests/test_contracts.py#L94).

```python
c.get(f"/v1/items/{r.json()['id']}")
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:95](../../../../../../libs/jane-kit/tests/test_contracts.py#L95).

```python
c.get("/v1/items/unknown")
```

## jane_kit.contracts.ContractClient.post

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:354](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L354).

```python
def post(self, url: str, **kw: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:92](../../../../../../libs/jane-kit/tests/test_contracts.py#L92).

```python
r = c.post("/v1/items", json={"name": "x"}, headers={"Idempotency-Key": "1"})
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:102](../../../../../../libs/jane-kit/tests/test_contracts.py#L102).

```python
c.post("/v1/items", json={"name": "x"}, headers={"Idempotency-Key": "1"})
```

## jane_kit.contracts.ContractClient.put

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:357](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L357).

```python
def put(self, url: str, **kw: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_contract.py:78](../../../../../../services/handler-runtime/tests/test_contract.py#L78).

```python
put = api.put(
        "/v1/connections/results-pg",
        json={"connection_id": "results-pg", "kind": "postgresql", "params": {"host": "db"}},
        headers={"Idempotency-Key": "c-7"},
    )
```

Контекст і передумови: [services/llm/tests/test_contract.py:49](../../../../../../services/llm/tests/test_contract.py#L49).

```python
api.put("/v1/providers/fake", json=h.priced_fake)
```

## jane_kit.contracts.ContractClient.patch

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:360](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L360).

```python
def patch(self, url: str, **kw: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_contract.py:124](../../../../../../services/orchestrator/tests/test_contract.py#L124).

```python
assert (
        api.patch(
            f"/v1/problem-groups/{groups[0]['group_id']}", content=json.dumps(patch), headers=merge
        ).status_code
        == 200
    )
```

Контекст і передумови: [services/orchestrator/tests/test_contract.py:130](../../../../../../services/orchestrator/tests/test_contract.py#L130).

```python
assert (
        api.patch("/v1/problem-groups/pg_none", content=json.dumps(patch), headers=merge).status_code == 404
    )
```

## jane_kit.contracts.ContractClient.delete

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:363](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L363).

```python
def delete(self, url: str, **kw: Any) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `httpx.Response`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_contract.py:85](../../../../../../services/handler-runtime/tests/test_contract.py#L85).

```python
assert api.delete("/v1/connections/results-pg").status_code == 404
```

Контекст і передумови: [services/llm/tests/test_contract.py:67](../../../../../../services/llm/tests/test_contract.py#L67).

```python
assert api.delete("/v1/providers/spare").status_code == 409
```

## jane_kit.contracts.ContractClient.uncovered

**Метод.** Код: [libs/jane-kit/src/jane_kit/contracts.py:366](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L366).

```python
def uncovered(self) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Operations never called through this client (coverage hint for contract tests).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:96](../../../../../../libs/jane-kit/tests/test_contracts.py#L96).

```python
assert "GET /v1/items" in c.uncovered()
```

Контекст і передумови: [services/handler-runtime/tests/test_contract.py:87](../../../../../../services/handler-runtime/tests/test_contract.py#L87).

```python
assert api.uncovered() == []
```

## jane_kit.contracts.example_from_schema

**Функція.** Код: [libs/jane-kit/src/jane_kit/contracts.py:382](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L382).

```python
def example_from_schema(spec: OpenAPISpec, schema: Loc | Mapping[str, Any], depth: int=0) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec` | `OpenAPISpec` | `—` | positional-or-keyword |
| `schema` | `Loc \| Mapping[str, Any]` | `—` | positional-or-keyword |
| `depth` | `int` | `0` | positional-or-keyword |

Результат: `Any`.

### Опис із вихідного коду

```text
Deterministic minimal instance of a schema (examples > default > const > enum > type).
```

## jane_kit.contracts.build_mock_app

**Функція.** Код: [libs/jane-kit/src/jane_kit/contracts.py:455](../../../../../../libs/jane-kit/src/jane_kit/contracts.py#L455).

```python
def build_mock_app(spec: OpenAPISpec) -> Starlette:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec` | `OpenAPISpec` | `—` | positional-or-keyword |

Результат: `Starlette`.

### Опис із вихідного коду

```text
ASGI mock of a service from its contract (see module docstring).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_codegen.py:30](../../../../../../libs/jane-kit/tests/test_codegen.py#L30).

```python
mock = build_mock_app(OpenAPISpec.load(DATA / "openapi.yaml"))
```

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:106](../../../../../../libs/jane-kit/tests/test_contracts.py#L106).

```python
mock = TestClient(build_mock_app(spec))
```
