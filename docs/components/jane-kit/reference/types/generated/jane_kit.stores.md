# jane_kit.stores

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.stores.ClaimLimits](#jane_kitstoresclaimlimits)
- [jane_kit.stores.ClaimLimits.in_progress_lease_ms](#jane_kitstoresclaimlimitsin_progress_lease_ms)
- [jane_kit.stores.ClaimLimits.heartbeat_interval_ms](#jane_kitstoresclaimlimitsheartbeat_interval_ms)
- [jane_kit.stores.LeaseLimits](#jane_kitstoresleaselimits)
- [jane_kit.stores.LeaseLimits.job_lease_ms](#jane_kitstoresleaselimitsjob_lease_ms)
- [jane_kit.stores.heartbeat_loop](#jane_kitstoresheartbeat_loop)

## jane_kit.stores.ClaimLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:32](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L32).

```python
class ClaimLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [in_progress_lease_ms](jane_kit.stores.md#jane_kitstoresclaimlimitsin_progress_lease_ms) | Поле | ні |
| [heartbeat_interval_ms](jane_kit.stores.md#jane_kitstoresclaimlimitsheartbeat_interval_ms) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Leases of ``Idempotency-Key`` claims (a service without shared jobs, e.g. the orchestrator).
```

## jane_kit.stores.ClaimLimits.in_progress_lease_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:35](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L35).

```python
in_progress_lease_ms: int = Field(default=900000, ge=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900000",
  "ge": "1000"
}
```

### Опис із вихідного коду

```text
An ``Idempotency-Key`` claim not renewed for this long (its instance stopped) can be claimed again.
```

## jane_kit.stores.ClaimLimits.heartbeat_interval_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:37](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L37).

```python
heartbeat_interval_ms: int = Field(default=15000, ge=100)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "15000",
  "ge": "100"
}
```

### Опис із вихідного коду

```text
How often an instance renews its leases (keep well below them).
```

## jane_kit.stores.LeaseLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:41](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L41).

```python
class LeaseLimits(ClaimLimits):
```

Базові типи / інтерфейси: `ClaimLimits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [job_lease_ms](jane_kit.stores.md#jane_kitstoresleaselimitsjob_lease_ms) | Поле | ні |
| [in_progress_lease_ms](jane_kit.stores.md#jane_kitstoresclaimlimitsin_progress_lease_ms) | Поле | так |
| [heartbeat_interval_ms](jane_kit.stores.md#jane_kitstoresclaimlimitsheartbeat_interval_ms) | Поле | так |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Leases of the shared stores (one group per service, e.g. ``limits.state``): claims and jobs.
```

## jane_kit.stores.LeaseLimits.job_lease_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:44](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L44).

```python
job_lease_ms: int = Field(default=60000, ge=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "1000"
}
```

### Опис із вихідного коду

```text
A job whose instance did not renew its lease for this long ends ``failed`` (retryable).
```

## jane_kit.stores.heartbeat_loop

**Функція.** Код: [libs/jane-kit/src/jane_kit/stores/__init__.py:48](../../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L48).

```python
async def heartbeat_loop(beats: Iterable[Callable[[], Awaitable[Any]]], interval_s: float, *, name: str='store') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `beats` | `Iterable[Callable[[], Awaitable[Any]]]` | `—` | positional-or-keyword |
| `interval_s` | `float` | `—` | positional-or-keyword |
| `name` | `str` | `'store'` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Call every ``beat`` (``store.heartbeat``, ``store.gc``...) each ``interval_s`` until cancelled; a failed
beat is logged and retried at the next tick (the lease covers a few missed beats).
```
