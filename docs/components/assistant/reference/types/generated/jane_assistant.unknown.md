# jane_assistant.unknown

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.unknown.FlagOff](#jane_assistantunknownflagoff)
- [jane_assistant.unknown.FlagOff.code](#jane_assistantunknownflagoffcode)
- [jane_assistant.unknown.run_unknown](#jane_assistantunknownrun_unknown)

## jane_assistant.unknown.FlagOff

**Клас.** Код: [services/assistant/src/jane_assistant/unknown.py:31](../../../../../../services/assistant/src/jane_assistant/unknown.py#L31).

```python
class FlagOff(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_assistant.unknown.md#jane_assistantunknownflagoffcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_assistant.unknown.FlagOff.code

**Поле.** Код: [services/assistant/src/jane_assistant/unknown.py:32](../../../../../../services/assistant/src/jane_assistant/unknown.py#L32).

```python
code = 'access_denied_by_policy'
```

Доступ: читання — так; запис — так.

## jane_assistant.unknown.run_unknown

**Функція.** Код: [services/assistant/src/jane_assistant/unknown.py:35](../../../../../../services/assistant/src/jane_assistant/unknown.py#L35).

```python
async def run_unknown(*, nb: Neighbours, req: dict[str, Any], settings: Settings, limits: ServiceLimits, job_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `nb` | `Neighbours` | `—` | keyword-only |
| `req` | `dict[str, Any]` | `—` | keyword-only |
| `settings` | `Settings` | `—` | keyword-only |
| `limits` | `ServiceLimits` | `—` | keyword-only |
| `job_id` | `str` | `—` | keyword-only |

Результат: `dict[str, Any]`.
