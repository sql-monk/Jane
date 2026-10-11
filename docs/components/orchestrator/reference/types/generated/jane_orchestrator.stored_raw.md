# jane_orchestrator.stored_raw

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.stored_raw.stored_raw_id](#jane_orchestratorstored_rawstored_raw_id)

## jane_orchestrator.stored_raw.stored_raw_id

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/stored_raw.py:8](../../../../../../services/orchestrator/src/jane_orchestrator/stored_raw.py#L8).

```python
def stored_raw_id(conn: Any, source_id: str, observation_id: str | None, *, run_id: str | None=None, invocation_id: str | None=None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `conn` | `Any` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |
| `observation_id` | `str \| None` | `—` | positional-or-keyword |
| `run_id` | `str \| None` | `None` | keyword-only |
| `invocation_id` | `str \| None` | `None` | keyword-only |

Результат: `str | None`.

### Опис із вихідного коду

```text
Return a known RAW id for this observation and run, never a different observation of its URL.

A problem sample identifies its run through the invocation. Missing provenance or several distinct
RAW copies is not resolved by choosing an arbitrary object: the optional API field stays absent.
```
