# Модуль `jane_extractor_sdk.compare`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/compare.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py). Не редагуйте вручну.

Comparison of an expected test output with the actual one (``TestCase.compare``: ``exact`` | ``subset``).

Runtime-added metadata of entities (``observation``, ``provenance``, ``schema``) is ignored on both sides. Differences are reported as ``{"pointer", "expected", "actual"}`` (``TestCaseResult.differences``).

## Функції

### Функція `compare_output`

```python
def compare_output(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any] | None,
    mode: Literal['exact', 'subset'] = 'exact',
) -> list[dict[str, Any]]: ...
```

Differences between the expected and the actual ``HandlerOutput`` (empty list = equal).

Код: [compare.py:101](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py#L101).

### Функція `strip_runtime_metadata`

```python
def strip_runtime_metadata(output: Mapping[str, Any]) -> dict[str, Any]: ...
```

Код: [compare.py:22](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/compare.py#L22).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `IGNORED_ENTITY_KEYS` | — | `frozenset({'observation', 'provenance', 'schema'})` |  |
