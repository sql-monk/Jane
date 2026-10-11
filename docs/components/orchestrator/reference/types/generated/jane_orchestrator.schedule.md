# jane_orchestrator.schedule

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.schedule.CronError](#jane_orchestratorschedulecronerror)
- [jane_orchestrator.schedule.parse_cron](#jane_orchestratorscheduleparse_cron)
- [jane_orchestrator.schedule.next_fire](#jane_orchestratorschedulenext_fire)

## jane_orchestrator.schedule.CronError

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/schedule.py:15](../../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L15).

```python
class CronError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

## jane_orchestrator.schedule.parse_cron

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/schedule.py:68](../../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L68).

```python
def parse_cron(expr: str) -> tuple[set[int], set[int], set[int], set[int], set[int], bool, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `expr` | `str` | `—` | positional-or-keyword |

Результат: `tuple[set[int], set[int], set[int], set[int], set[int], bool, bool]`.

Явні `raise` у тілі: `CronError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:302](../../../../../../services/orchestrator/tests/test_logic.py#L302).

```python
parse_cron("61 * * * *")
```

## jane_orchestrator.schedule.next_fire

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/schedule.py:104](../../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L104).

```python
def next_fire(schedule: Mapping[str, Any] | None, after: datetime, last_fired: datetime | None) -> datetime | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schedule` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `after` | `datetime` | `—` | positional-or-keyword |
| `last_fired` | `datetime \| None` | `—` | positional-or-keyword |

Результат: `datetime | None`.

### Опис із вихідного коду

```text
Next run strictly after ``after`` (UTC), or ``None`` (manual, disabled, finished).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:295](../../../../../../services/orchestrator/tests/test_logic.py#L295).

```python
nxt = next_fire({"type": "cron", "cron": "0 2 * * 0", "timezone": "Europe/Kyiv"}, T0, None)
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:297](../../../../../../services/orchestrator/tests/test_logic.py#L297).

```python
assert next_fire({"type": "cron", "cron": "*/15 * * * *"}, T0, None) == T0 + timedelta(minutes=15)
```
