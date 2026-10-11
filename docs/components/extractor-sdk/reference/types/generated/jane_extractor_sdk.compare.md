# jane_extractor_sdk.compare

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.compare.IGNORED_ENTITY_KEYS](#jane_extractor_sdkcompareignored_entity_keys)
- [jane_extractor_sdk.compare.strip_runtime_metadata](#jane_extractor_sdkcomparestrip_runtime_metadata)
- [jane_extractor_sdk.compare.compare_output](#jane_extractor_sdkcomparecompare_output)

## jane_extractor_sdk.compare.IGNORED_ENTITY_KEYS

**Константа.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/compare.py:14](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py#L14).

```python
IGNORED_ENTITY_KEYS = frozenset({'observation', 'provenance', 'schema'})
```

## jane_extractor_sdk.compare.strip_runtime_metadata

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/compare.py:22](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py#L22).

```python
def strip_runtime_metadata(output: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `output` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_extractor_sdk.compare.compare_output

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/compare.py:101](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py#L101).

```python
def compare_output(expected: Mapping[str, Any], actual: Mapping[str, Any] | None, mode: Literal['exact', 'subset']='exact') -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `expected` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actual` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `mode` | `Literal['exact', 'subset']` | `'exact'` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Опис із вихідного коду

```text
Differences between the expected and the actual ``HandlerOutput`` (empty list = equal).
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:113](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L113).

```python
diffs = compare_output(expected, actual, "exact")
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:115](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L115).

```python
assert compare_output({"entities": [{"fields": {"ok": True}}]}, {"entities": [{"fields": {"ok": 1}}]})
```
