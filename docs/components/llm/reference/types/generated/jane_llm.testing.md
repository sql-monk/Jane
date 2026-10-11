# jane_llm.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.testing.differences](#jane_llmtestingdifferences)
- [jane_llm.testing.run_tests](#jane_llmtestingrun_tests)

## jane_llm.testing.differences

**Функція.** Код: [services/llm/src/jane_llm/testing.py:29](../../../../../../services/llm/src/jane_llm/testing.py#L29).

```python
def differences(expected: Any, actual: Any, mode: str, pointer: str='') -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `expected` | `Any` | `—` | positional-or-keyword |
| `actual` | `Any` | `—` | positional-or-keyword |
| `mode` | `str` | `—` | positional-or-keyword |
| `pointer` | `str` | `''` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Опис із вихідного коду

```text
``exact`` — equal; ``subset`` — every expected value present (extra fields allowed).
```

## jane_llm.testing.run_tests

**Функція.** Код: [services/llm/src/jane_llm/testing.py:81](../../../../../../services/llm/src/jane_llm/testing.py#L81).

```python
async def run_tests(handler: LlmHandler, request: dict[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `handler` | `LlmHandler` | `—` | positional-or-keyword |
| `request` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.
