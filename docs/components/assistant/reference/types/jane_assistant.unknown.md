# Модуль `jane_assistant.unknown`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/unknown.py](../../../../../services/assistant/src/jane_assistant/unknown.py). Не редагуйте вручну.

Analysis of an unknown material (ТЗ §8, criterion 11).

The orchestrator forwards a material without a matching handler only when the effective flag «Передавати в LLM невідомі сторінки» (``forward_unknown_to_llm``) is on. The assistant checks the flag again and refuses (403 ``access_denied_by_policy``) *before* any LLM call when it is off.

## Класи

### Клас `FlagOff`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_assistant.unknown` |
| Успадкування | `JaneError` |
| Код | [unknown.py:31](../../../../../services/assistant/src/jane_assistant/unknown.py#L31) |

```python
class FlagOff(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'access_denied_by_policy'` |  |

## Функції

### Функція `run_unknown`

```python
async def run_unknown(
    *,
    nb: Neighbours,
    req: dict[str, Any],
    settings: Settings,
    limits: ServiceLimits,
    job_id: str,
) -> dict[str, Any]: ...
```

Код: [unknown.py:35](../../../../../services/assistant/src/jane_assistant/unknown.py#L35).
