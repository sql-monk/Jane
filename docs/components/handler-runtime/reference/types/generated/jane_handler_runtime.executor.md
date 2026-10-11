# jane_handler_runtime.executor

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.executor.now_rfc3339](#jane_handler_runtimeexecutornow_rfc3339)
- [jane_handler_runtime.executor.new_invocation_id](#jane_handler_runtimeexecutornew_invocation_id)
- [jane_handler_runtime.executor.PreparedInvocation](#jane_handler_runtimeexecutorpreparedinvocation)
- [jane_handler_runtime.executor.PreparedInvocation.__init__](#jane_handler_runtimeexecutorpreparedinvocation__init__)
- [jane_handler_runtime.executor.PreparedInvocation.invocation_id](#jane_handler_runtimeexecutorpreparedinvocationinvocation_id)
- [jane_handler_runtime.executor.PreparedInvocation.package](#jane_handler_runtimeexecutorpreparedinvocationpackage)
- [jane_handler_runtime.executor.PreparedInvocation.params](#jane_handler_runtimeexecutorpreparedinvocationparams)
- [jane_handler_runtime.executor.PreparedInvocation.inputs](#jane_handler_runtimeexecutorpreparedinvocationinputs)
- [jane_handler_runtime.executor.PreparedInvocation.contents](#jane_handler_runtimeexecutorpreparedinvocationcontents)
- [jane_handler_runtime.executor.PreparedInvocation.limits](#jane_handler_runtimeexecutorpreparedinvocationlimits)
- [jane_handler_runtime.executor.PreparedInvocation.image](#jane_handler_runtimeexecutorpreparedinvocationimage)
- [jane_handler_runtime.executor.PreparedInvocation.test_mode](#jane_handler_runtimeexecutorpreparedinvocationtest_mode)
- [jane_handler_runtime.executor.PreparedInvocation.delivery_key](#jane_handler_runtimeexecutorpreparedinvocationdelivery_key)
- [jane_handler_runtime.executor.PreparedInvocation.context](#jane_handler_runtimeexecutorpreparedinvocationcontext)
- [jane_handler_runtime.executor.Executor](#jane_handler_runtimeexecutorexecutor)
- [jane_handler_runtime.executor.Executor.__init__](#jane_handler_runtimeexecutorexecutor__init__)
- [jane_handler_runtime.executor.Executor.settings](#jane_handler_runtimeexecutorexecutorsettings)
- [jane_handler_runtime.executor.Executor.store](#jane_handler_runtimeexecutorexecutorstore)
- [jane_handler_runtime.executor.Executor.fetcher](#jane_handler_runtimeexecutorexecutorfetcher)
- [jane_handler_runtime.executor.Executor.backend](#jane_handler_runtimeexecutorexecutorbackend)
- [jane_handler_runtime.executor.Executor.schemas](#jane_handler_runtimeexecutorexecutorschemas)
- [jane_handler_runtime.executor.Executor.check_package](#jane_handler_runtimeexecutorexecutorcheck_package)
- [jane_handler_runtime.executor.Executor.check_params](#jane_handler_runtimeexecutorexecutorcheck_params)
- [jane_handler_runtime.executor.Executor.check_input](#jane_handler_runtimeexecutorexecutorcheck_input)
- [jane_handler_runtime.executor.Executor.prepare](#jane_handler_runtimeexecutorexecutorprepare)
- [jane_handler_runtime.executor.Executor.bundle](#jane_handler_runtimeexecutorexecutorbundle)
- [jane_handler_runtime.executor.Executor.labels](#jane_handler_runtimeexecutorexecutorlabels)
- [jane_handler_runtime.executor.Executor.run](#jane_handler_runtimeexecutorexecutorrun)
- [jane_handler_runtime.executor.Executor.interpret](#jane_handler_runtimeexecutorexecutorinterpret)

## jane_handler_runtime.executor.now_rfc3339

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:46](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L46).

```python
def now_rfc3339() -> str:
```

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:44](../../../../../../services/handler-runtime/tests/test_classification.py#L44).

```python
interpreted = executor.interpret(prep, result, now_rfc3339())
```

## jane_handler_runtime.executor.new_invocation_id

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:50](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L50).

```python
def new_invocation_id() -> str:
```

Результат: `str`.

## jane_handler_runtime.executor.PreparedInvocation

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:55](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L55).

```python
class PreparedInvocation:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [invocation_id](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationinvocation_id) | Поле | ні |
| [package](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationpackage) | Поле | ні |
| [params](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationparams) | Поле | ні |
| [inputs](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationinputs) | Поле | ні |
| [contents](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationcontents) | Поле | ні |
| [limits](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationlimits) | Поле | ні |
| [image](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationimage) | Поле | ні |
| [test_mode](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationtest_mode) | Поле | ні |
| [delivery_key](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationdelivery_key) | Поле | ні |
| [context](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocationcontext) | Поле | ні |
| [__init__](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorpreparedinvocation__init__) | Конструктор dataclass | ні |

## jane_handler_runtime.executor.PreparedInvocation.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:55](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L55).

```python
def __init__(self, invocation_id: str, package: LoadedPackage, params: dict[str, Any], inputs: list[dict[str, Any]], contents: list[bytes | None], limits: ServiceLimits, image: str, test_mode: bool = False, delivery_key: str | None = None, context: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `invocation_id` | `str` | `—` | positional-or-keyword |
| `package` | `LoadedPackage` | `—` | positional-or-keyword |
| `params` | `dict[str, Any]` | `—` | positional-or-keyword |
| `inputs` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `contents` | `list[bytes \| None]` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `image` | `str` | `—` | positional-or-keyword |
| `test_mode` | `bool` | `False` | positional-or-keyword |
| `delivery_key` | `str \| None` | `None` | positional-or-keyword |
| `context` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.executor.PreparedInvocation.invocation_id

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:56](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L56).

```python
invocation_id: str
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.package

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:57](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L57).

```python
package: LoadedPackage
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.params

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:58](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L58).

```python
params: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.inputs

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:59](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L59).

```python
inputs: list[dict[str, Any]]
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.contents

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:60](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L60).

```python
contents: list[bytes | None]
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.limits

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:61](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L61).

```python
limits: ServiceLimits
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.image

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:62](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L62).

```python
image: str
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.test_mode

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:63](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L63).

```python
test_mode: bool = False
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.delivery_key

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:64](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L64).

```python
delivery_key: str | None = None
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.executor.PreparedInvocation.context

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:65](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L65).

```python
context: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_handler_runtime.executor.Executor

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:75](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L75).

```python
class Executor:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutor__init__) | Конструктор | ні |
| [settings](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorsettings) | Поле екземпляра | ні |
| [store](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorstore) | Поле екземпляра | ні |
| [fetcher](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorfetcher) | Поле екземпляра | ні |
| [backend](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorbackend) | Поле екземпляра | ні |
| [schemas](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorschemas) | Поле екземпляра | ні |
| [check_package](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorcheck_package) | Метод | ні |
| [check_params](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorcheck_params) | Метод | ні |
| [check_input](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorcheck_input) | Метод | ні |
| [prepare](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorprepare) | Метод | ні |
| [bundle](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorbundle) | Метод | ні |
| [labels](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorlabels) | Метод | ні |
| [run](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorrun) | Метод | ні |
| [interpret](jane_handler_runtime.executor.md#jane_handler_runtimeexecutorexecutorinterpret) | Метод | ні |

## jane_handler_runtime.executor.Executor.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:76](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L76).

```python
def __init__(self, settings: Settings, store: PackageStore, fetcher: ContentFetcher, backend: SandboxBackend, schemas: ContractSchemas) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `store` | `PackageStore` | `—` | positional-or-keyword |
| `fetcher` | `ContentFetcher` | `—` | positional-or-keyword |
| `backend` | `SandboxBackend` | `—` | positional-or-keyword |
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.executor.Executor.settings

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:84](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L84).

```python
self.settings = settings
```

## jane_handler_runtime.executor.Executor.store

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:85](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L85).

```python
self.store = store
```

## jane_handler_runtime.executor.Executor.fetcher

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:86](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L86).

```python
self.fetcher = fetcher
```

## jane_handler_runtime.executor.Executor.backend

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:87](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L87).

```python
self.backend = backend
```

## jane_handler_runtime.executor.Executor.schemas

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:88](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L88).

```python
self.schemas = schemas
```

## jane_handler_runtime.executor.Executor.check_package

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:94](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L94).

```python
def check_package(self, package: LoadedPackage) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package` | `LoadedPackage` | `—` | positional-or-keyword |

Результат: `str`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Kind, entry, access and dependencies; returns the sandbox image of the runtime profile.
```

## jane_handler_runtime.executor.Executor.check_params

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:141](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L141).

```python
def check_params(self, package: LoadedPackage, params: Mapping[str, Any] | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package` | `LoadedPackage` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_handler_runtime.executor.Executor.check_input

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:154](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L154).

```python
def check_input(self, package: LoadedPackage, index: int, item: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package` | `LoadedPackage` | `—` | positional-or-keyword |
| `index` | `int` | `—` | positional-or-keyword |
| `item` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_handler_runtime.executor.Executor.prepare

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:194](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L194).

```python
async def prepare(self, invocation: Mapping[str, Any], *, package: LoadedPackage | None=None, test_mode: bool | None=None) -> PreparedInvocation:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `package` | `LoadedPackage \| None` | `None` | keyword-only |
| `test_mode` | `bool \| None` | `None` | keyword-only |

Результат: `PreparedInvocation`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Validate everything that must be right before the sandbox starts.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:36](../../../../../../services/handler-runtime/tests/test_classification.py#L36).

```python
return executor, await executor.prepare(body)
```

## jane_handler_runtime.executor.Executor.bundle

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:236](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L236).

```python
def bundle(self, prep: PreparedInvocation) -> Bundle:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `prep` | `PreparedInvocation` | `—` | positional-or-keyword |

Результат: `Bundle`.

## jane_handler_runtime.executor.Executor.labels

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:258](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L258).

```python
def labels(self, prep: PreparedInvocation) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `prep` | `PreparedInvocation` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

## jane_handler_runtime.executor.Executor.run

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:264](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L264).

```python
async def run(self, prep: PreparedInvocation) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `prep` | `PreparedInvocation` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ServiceUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_handler_runtime.executor.Executor.interpret

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/executor.py:323](../../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L323).

```python
def interpret(self, prep: PreparedInvocation, outcome: SandboxOutcome, started_at: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `prep` | `PreparedInvocation` | `—` | positional-or-keyword |
| `outcome` | `SandboxOutcome` | `—` | positional-or-keyword |
| `started_at` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:44](../../../../../../services/handler-runtime/tests/test_classification.py#L44).

```python
interpreted = executor.interpret(prep, result, now_rfc3339())
```
