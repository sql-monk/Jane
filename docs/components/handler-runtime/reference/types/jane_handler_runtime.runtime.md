# Модуль `jane_handler_runtime.runtime`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/runtime.py](../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py). Не редагуйте вручну.

Wiring shared by the HTTP service and the CLI.

## Класи

### Клас `Runtime`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_handler_runtime.runtime` |
| Код | [runtime.py:22](../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L22) |

```python
@dataclass
class Runtime: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `settings` | `Settings` | — | читання й запис |  |
| `limits` | `ResolvedLimits[ServiceLimits]` | — | читання й запис |  |
| `backend` | `SandboxBackend` | — | читання й запис |  |
| `store` | `PackageStore` | — | читання й запис |  |
| `executor` | `Executor` | — | читання й запис |  |
| `schemas` | `ContractSchemas` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Runtime.close`

```python
def close(self) -> None: ...
```

Код: [runtime.py:30](../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L30).

## Функції

### Функція `build_backend`

```python
def build_backend(settings: Settings, limits: ServiceLimits) -> SandboxBackend: ...
```

Код: [runtime.py:34](../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L34).

### Функція `build_runtime`

```python
def build_runtime(
    settings: Settings,
    *,
    backend: SandboxBackend | None = None,
    registry_transport: httpx.AsyncBaseTransport | None = None,
    download_transport: httpx.AsyncBaseTransport | None = None,
) -> Runtime: ...
```

Код: [runtime.py:47](../../../../../services/handler-runtime/src/jane_handler_runtime/runtime.py#L47).
