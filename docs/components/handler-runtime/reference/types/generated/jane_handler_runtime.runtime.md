# jane_handler_runtime.runtime

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.runtime.Runtime](#jane_handler_runtimeruntimeruntime)
- [jane_handler_runtime.runtime.Runtime.__init__](#jane_handler_runtimeruntimeruntime__init__)
- [jane_handler_runtime.runtime.Runtime.settings](#jane_handler_runtimeruntimeruntimesettings)
- [jane_handler_runtime.runtime.Runtime.limits](#jane_handler_runtimeruntimeruntimelimits)
- [jane_handler_runtime.runtime.Runtime.backend](#jane_handler_runtimeruntimeruntimebackend)
- [jane_handler_runtime.runtime.Runtime.store](#jane_handler_runtimeruntimeruntimestore)
- [jane_handler_runtime.runtime.Runtime.executor](#jane_handler_runtimeruntimeruntimeexecutor)
- [jane_handler_runtime.runtime.Runtime.schemas](#jane_handler_runtimeruntimeruntimeschemas)
- [jane_handler_runtime.runtime.Runtime.close](#jane_handler_runtimeruntimeruntimeclose)
- [jane_handler_runtime.runtime.build_backend](#jane_handler_runtimeruntimebuild_backend)
- [jane_handler_runtime.runtime.build_runtime](#jane_handler_runtimeruntimebuild_runtime)

## jane_handler_runtime.runtime.Runtime

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:22](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L22).

```python
class Runtime:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [settings](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimesettings) | Поле | ні |
| [limits](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimelimits) | Поле | ні |
| [backend](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimebackend) | Поле | ні |
| [store](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimestore) | Поле | ні |
| [executor](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimeexecutor) | Поле | ні |
| [schemas](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimeschemas) | Поле | ні |
| [close](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntimeclose) | Метод | ні |
| [__init__](jane_handler_runtime.runtime.md#jane_handler_runtimeruntimeruntime__init__) | Конструктор dataclass | ні |

## jane_handler_runtime.runtime.Runtime.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:22](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L22).

```python
def __init__(self, settings: Settings, limits: ResolvedLimits[ServiceLimits], backend: SandboxBackend, store: PackageStore, executor: Executor, schemas: ContractSchemas) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ResolvedLimits[ServiceLimits]` | `—` | positional-or-keyword |
| `backend` | `SandboxBackend` | `—` | positional-or-keyword |
| `store` | `PackageStore` | `—` | positional-or-keyword |
| `executor` | `Executor` | `—` | positional-or-keyword |
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.runtime.Runtime.settings

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:23](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L23).

```python
settings: Settings
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.limits

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:24](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L24).

```python
limits: ResolvedLimits[ServiceLimits]
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.backend

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:25](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L25).

```python
backend: SandboxBackend
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.store

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:26](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L26).

```python
store: PackageStore
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.executor

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:27](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L27).

```python
executor: Executor
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.schemas

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:28](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L28).

```python
schemas: ContractSchemas
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.runtime.Runtime.close

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:30](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L30).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.runtime.build_backend

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:34](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L34).

```python
def build_backend(settings: Settings, limits: ServiceLimits) -> SandboxBackend:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `SandboxBackend`.

## jane_handler_runtime.runtime.build_runtime

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/runtime.py:47](../../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L47).

```python
def build_runtime(settings: Settings, *, backend: SandboxBackend | None=None, registry_transport: httpx.AsyncBaseTransport | None=None, download_transport: httpx.AsyncBaseTransport | None=None) -> Runtime:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `backend` | `SandboxBackend \| None` | `None` | keyword-only |
| `registry_transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |
| `download_transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |

Результат: `Runtime`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:290](../../../../../../services/handler-runtime/tests/test_app.py#L290).

```python
runtime = build_runtime(settings, registry_transport=httpx.ASGITransport(app=fake))
```

Контекст і передумови: [services/handler-runtime/tests/test_app.py:386](../../../../../../services/handler-runtime/tests/test_app.py#L386).

```python
runtime = build_runtime(settings, registry_transport=httpx.ASGITransport(app=fake))
```
