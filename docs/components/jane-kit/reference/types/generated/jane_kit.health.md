# jane_kit.health

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.health.CheckResult](#jane_kithealthcheckresult)
- [jane_kit.health.CheckResult.status](#jane_kithealthcheckresultstatus)
- [jane_kit.health.CheckResult.message](#jane_kithealthcheckresultmessage)
- [jane_kit.health.HealthReport](#jane_kithealthhealthreport)
- [jane_kit.health.HealthReport.status](#jane_kithealthhealthreportstatus)
- [jane_kit.health.HealthReport.checks](#jane_kithealthhealthreportchecks)
- [jane_kit.health.ServiceInfo](#jane_kithealthserviceinfo)
- [jane_kit.health.ServiceInfo.service](#jane_kithealthserviceinfoservice)
- [jane_kit.health.ServiceInfo.version](#jane_kithealthserviceinfoversion)
- [jane_kit.health.ServiceInfo.api_versions](#jane_kithealthserviceinfoapi_versions)
- [jane_kit.health.ServiceInfo.capabilities](#jane_kithealthserviceinfocapabilities)
- [jane_kit.health.ServiceInfo.auth_mode](#jane_kithealthserviceinfoauth_mode)
- [jane_kit.health.ServiceInfo.limits](#jane_kithealthserviceinfolimits)
- [jane_kit.health.HealthRegistry](#jane_kithealthhealthregistry)
- [jane_kit.health.HealthRegistry.__init__](#jane_kithealthhealthregistry__init__)
- [jane_kit.health.HealthRegistry.check_timeout_s](#jane_kithealthhealthregistrycheck_timeout_s)
- [jane_kit.health.HealthRegistry.add](#jane_kithealthhealthregistryadd)
- [jane_kit.health.HealthRegistry.report](#jane_kithealthhealthregistryreport)
- [jane_kit.health.install_health](#jane_kithealthinstall_health)

## jane_kit.health.CheckResult

**Клас.** Код: [libs/jane-kit/src/jane_kit/health.py:26](../../../../../../libs/jane-kit/src/jane_kit/health.py#L26).

```python
class CheckResult(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status](jane_kit.health.md#jane_kithealthcheckresultstatus) | Поле | ні |
| [message](jane_kit.health.md#jane_kithealthcheckresultmessage) | Поле | ні |

## jane_kit.health.CheckResult.status

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:27](../../../../../../libs/jane-kit/src/jane_kit/health.py#L27).

```python
status: Status
```

Доступ: читання — так; запис — так.

## jane_kit.health.CheckResult.message

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:28](../../../../../../libs/jane-kit/src/jane_kit/health.py#L28).

```python
message: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.health.HealthReport

**Клас.** Код: [libs/jane-kit/src/jane_kit/health.py:31](../../../../../../libs/jane-kit/src/jane_kit/health.py#L31).

```python
class HealthReport(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status](jane_kit.health.md#jane_kithealthhealthreportstatus) | Поле | ні |
| [checks](jane_kit.health.md#jane_kithealthhealthreportchecks) | Поле | ні |

## jane_kit.health.HealthReport.status

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:32](../../../../../../libs/jane-kit/src/jane_kit/health.py#L32).

```python
status: Status
```

Доступ: читання — так; запис — так.

## jane_kit.health.HealthReport.checks

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:33](../../../../../../libs/jane-kit/src/jane_kit/health.py#L33).

```python
checks: dict[str, CheckResult] = {}
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo

**Клас.** Код: [libs/jane-kit/src/jane_kit/health.py:36](../../../../../../libs/jane-kit/src/jane_kit/health.py#L36).

```python
class ServiceInfo(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [service](jane_kit.health.md#jane_kithealthserviceinfoservice) | Поле | ні |
| [version](jane_kit.health.md#jane_kithealthserviceinfoversion) | Поле | ні |
| [api_versions](jane_kit.health.md#jane_kithealthserviceinfoapi_versions) | Поле | ні |
| [capabilities](jane_kit.health.md#jane_kithealthserviceinfocapabilities) | Поле | ні |
| [auth_mode](jane_kit.health.md#jane_kithealthserviceinfoauth_mode) | Поле | ні |
| [limits](jane_kit.health.md#jane_kithealthserviceinfolimits) | Поле | ні |

## jane_kit.health.ServiceInfo.service

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:37](../../../../../../libs/jane-kit/src/jane_kit/health.py#L37).

```python
service: str
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo.version

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:38](../../../../../../libs/jane-kit/src/jane_kit/health.py#L38).

```python
version: str
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo.api_versions

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:39](../../../../../../libs/jane-kit/src/jane_kit/health.py#L39).

```python
api_versions: list[str]
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo.capabilities

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:40](../../../../../../libs/jane-kit/src/jane_kit/health.py#L40).

```python
capabilities: dict[str, Any] = {}
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo.auth_mode

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:41](../../../../../../libs/jane-kit/src/jane_kit/health.py#L41).

```python
auth_mode: Literal['none', 'api_key', 'jwt'] | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.health.ServiceInfo.limits

**Поле.** Код: [libs/jane-kit/src/jane_kit/health.py:42](../../../../../../libs/jane-kit/src/jane_kit/health.py#L42).

```python
limits: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``PlatformLimits``: the service's configured defaults and hard caps (contract fields only).
```

## jane_kit.health.HealthRegistry

**Клас.** Код: [libs/jane-kit/src/jane_kit/health.py:46](../../../../../../libs/jane-kit/src/jane_kit/health.py#L46).

```python
class HealthRegistry:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.health.md#jane_kithealthhealthregistry__init__) | Конструктор | ні |
| [check_timeout_s](jane_kit.health.md#jane_kithealthhealthregistrycheck_timeout_s) | Поле екземпляра | ні |
| [add](jane_kit.health.md#jane_kithealthhealthregistryadd) | Метод | ні |
| [report](jane_kit.health.md#jane_kithealthhealthregistryreport) | Метод | ні |

### Опис із вихідного коду

```text
Named health checks. ``critical=False`` checks can only make the service ``degraded``.
```

## jane_kit.health.HealthRegistry.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/health.py:49](../../../../../../libs/jane-kit/src/jane_kit/health.py#L49).

```python
def __init__(self, check_timeout_s: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `check_timeout_s` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.health.HealthRegistry.check_timeout_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/health.py:50](../../../../../../libs/jane-kit/src/jane_kit/health.py#L50).

```python
self.check_timeout_s = check_timeout_s
```

## jane_kit.health.HealthRegistry.add

**Метод.** Код: [libs/jane-kit/src/jane_kit/health.py:53](../../../../../../libs/jane-kit/src/jane_kit/health.py#L53).

```python
def add(self, name: str, check: CheckFn, *, critical: bool=True) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `check` | `CheckFn` | `—` | positional-or-keyword |
| `critical` | `bool` | `True` | keyword-only |

Результат: `None`.

## jane_kit.health.HealthRegistry.report

**Метод.** Код: [libs/jane-kit/src/jane_kit/health.py:74](../../../../../../libs/jane-kit/src/jane_kit/health.py#L74).

```python
async def report(self) -> HealthReport:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `HealthReport`.

## jane_kit.health.install_health

**Функція.** Код: [libs/jane-kit/src/jane_kit/health.py:82](../../../../../../libs/jane-kit/src/jane_kit/health.py#L82).

```python
def install_health(app: FastAPI, registry: HealthRegistry, info: Callable[[], ServiceInfo], prefix: str='/v1') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |
| `registry` | `HealthRegistry` | `—` | positional-or-keyword |
| `info` | `Callable[[], ServiceInfo]` | `—` | positional-or-keyword |
| `prefix` | `str` | `'/v1'` | positional-or-keyword |

Результат: `None`.
