# Модуль `jane_orchestrator.schedule`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/schedule.py](../../../../../services/orchestrator/src/jane_orchestrator/schedule.py). Не редагуйте вручну.

Next fire time of a ``Schedule`` (manual | once | cron | interval), IANA time zones via zoneinfo.

## Класи

### Клас `CronError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_orchestrator.schedule` |
| Успадкування | `ValueError` |
| Код | [schedule.py:15](../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L15) |

```python
class CronError(ValueError): ...
```

## Функції

### Функція `next_fire`

```python
def next_fire(
    schedule: Mapping[str, Any] | None,
    after: datetime,
    last_fired: datetime | None,
) -> datetime | None: ...
```

Next run strictly after ``after`` (UTC), or ``None`` (manual, disabled, finished).

Код: [schedule.py:104](../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L104).

### Функція `parse_cron`

```python
def parse_cron(
    expr: str,
) -> tuple[set[int], set[int], set[int], set[int], set[int], bool, bool]: ...
```

Винятки в коді функції: `CronError`.

Код: [schedule.py:68](../../../../../services/orchestrator/src/jane_orchestrator/schedule.py#L68).
