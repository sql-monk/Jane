# Модуль `jane_kit.health`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/health.py](../../../../../libs/jane-kit/src/jane_kit/health.py). Не редагуйте вручну.

``GET /v1/health`` and ``GET /v1/info`` per WP-00 ``common.yaml`` (pathItems Health, Info).

Health: ``{"status": "ok"|"degraded"|"down", "checks": {name: {"status", "message"}}}``; HTTP 200 for ok/degraded, 503 for down. A check returns ``True``/``False``, a status string, or raises; each check is time-boxed by ``check_timeout_s`` (from config).

## Зміст

- [Клас `CheckResult`](#клас-checkresult)
- [Клас `HealthRegistry`](#клас-healthregistry)
- [Клас `HealthReport`](#клас-healthreport)
- [Клас `ServiceInfo`](#клас-serviceinfo)
- [Функція `install_health`](#функція-install_health)

## Класи

### Клас `CheckResult`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.health` |
| Успадкування | `BaseModel` |
| Код | [health.py:26](../../../../../libs/jane-kit/src/jane_kit/health.py#L26) |

```python
class CheckResult(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `status` | `Status` | — | читання й запис |  |
| `message` | `str \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `HealthRegistry`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.health` |
| Код | [health.py:46](../../../../../libs/jane-kit/src/jane_kit/health.py#L46) |

```python
class HealthRegistry: ...
```

Named health checks. ``critical=False`` checks can only make the service ``degraded``.

#### Конструктор `HealthRegistry.__init__`

```python
def __init__(self, check_timeout_s: float) -> None: ...
```

Код: [health.py:49](../../../../../libs/jane-kit/src/jane_kit/health.py#L49).

#### Метод `HealthRegistry.add`

```python
def add(self, name: str, check: CheckFn, *, critical: bool = True) -> None: ...
```

Код: [health.py:53](../../../../../libs/jane-kit/src/jane_kit/health.py#L53).

#### Метод `HealthRegistry.report`

```python
async def report(self) -> HealthReport: ...
```

Код: [health.py:74](../../../../../libs/jane-kit/src/jane_kit/health.py#L74).

### Клас `HealthReport`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.health` |
| Успадкування | `BaseModel` |
| Код | [health.py:31](../../../../../libs/jane-kit/src/jane_kit/health.py#L31) |

```python
class HealthReport(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `status` | `Status` | — | читання й запис |  |
| `checks` | `dict[str, CheckResult]` | `{}` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ServiceInfo`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.health` |
| Успадкування | `BaseModel` |
| Код | [health.py:36](../../../../../libs/jane-kit/src/jane_kit/health.py#L36) |

```python
class ServiceInfo(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service` | `str` | — | читання й запис |  |
| `version` | `str` | — | читання й запис |  |
| `api_versions` | `list[str]` | — | читання й запис |  |
| `capabilities` | `dict[str, Any]` | `{}` | читання й запис |  |
| `auth_mode` | `Literal['none', 'api_key', 'jwt'] \| None` | `None` | читання й запис |  |
| `limits` | `dict[str, Any] \| None` | `None` | читання й запис | ``PlatformLimits``: the service's configured defaults and hard caps (contract fields only). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `install_health`

```python
def install_health(
    app: FastAPI,
    registry: HealthRegistry,
    info: Callable[[], ServiceInfo],
    prefix: str = '/v1',
) -> None: ...
```

Код: [health.py:82](../../../../../libs/jane-kit/src/jane_kit/health.py#L82).
