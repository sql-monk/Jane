# jane_extractor_sdk

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.Context](#jane_extractor_sdkcontext)
- [jane_extractor_sdk.DiagnosticsLog](#jane_extractor_sdkdiagnosticslog)
- [jane_extractor_sdk.empty](#jane_extractor_sdkempty)
- [jane_extractor_sdk.entity](#jane_extractor_sdkentity)
- [jane_extractor_sdk.success](#jane_extractor_sdksuccess)
- [jane_extractor_sdk.unrecognized](#jane_extractor_sdkunrecognized)
- [jane_extractor_sdk.Diagnostic](#jane_extractor_sdkdiagnostic)
- [jane_extractor_sdk.EntityOut](#jane_extractor_sdkentityout)
- [jane_extractor_sdk.ExtractResult](#jane_extractor_sdkextractresult)
- [jane_extractor_sdk.Material](#jane_extractor_sdkmaterial)
- [jane_extractor_sdk.Unrecognized](#jane_extractor_sdkunrecognized)
- [jane_extractor_sdk.__version__](#jane_extractor_sdk__version__)

## jane_extractor_sdk.Context

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:7](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L7).

```python
from jane_extractor_sdk.context import Context as Context
```

Повторний експорт: [jane_extractor_sdk.context.Context](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontext).

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:85](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L85).

```python
ctx = Context(m)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:90](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L90).

```python
loaded = Context({"content": {"kind": "blob"}}, content_loader=lambda: b"abc")
```

## jane_extractor_sdk.DiagnosticsLog

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:7](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L7).

```python
from jane_extractor_sdk.context import DiagnosticsLog as DiagnosticsLog
```

Повторний експорт: [jane_extractor_sdk.context.DiagnosticsLog](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslog).

## jane_extractor_sdk.empty

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:8](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L8).

```python
from jane_extractor_sdk.result import empty as empty
```

Повторний експорт: [jane_extractor_sdk.result.empty](jane_extractor_sdk.result.md#jane_extractor_sdkresultempty).

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:73](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L73).

```python
assert empty() == {"status": "empty", "entities": []}
```

## jane_extractor_sdk.entity

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:8](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L8).

```python
from jane_extractor_sdk.result import entity as entity
```

Повторний експорт: [jane_extractor_sdk.result.entity](jane_extractor_sdk.result.md#jane_extractor_sdkresultentity).

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:70](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L70).

```python
e = entity("product", {"sku": "A-1", "title": None, "price": 1}, cleared=["old", "old"])
```

## jane_extractor_sdk.success

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:8](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L8).

```python
from jane_extractor_sdk.result import success as success
```

Повторний експорт: [jane_extractor_sdk.result.success](jane_extractor_sdk.result.md#jane_extractor_sdkresultsuccess).

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:72](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L72).

```python
assert success([e])["status"] == "success"
```

## jane_extractor_sdk.unrecognized

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:8](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L8).

```python
from jane_extractor_sdk.result import unrecognized as unrecognized
```

Повторний експорт: [jane_extractor_sdk.result.unrecognized](jane_extractor_sdk.result.md#jane_extractor_sdkresultunrecognized).

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:74](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L74).

```python
partial = unrecognized("no price", signature="missing-selector:.price", entities=[e])
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:80](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L80).

```python
assert unrecognized("unknown layout")["unrecognized"]["partial"] is False
```

## jane_extractor_sdk.Diagnostic

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:9](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L9).

```python
from jane_extractor_sdk.types import Diagnostic as Diagnostic
```

Повторний експорт: [jane_extractor_sdk.types.Diagnostic](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnostic).

## jane_extractor_sdk.EntityOut

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:9](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L9).

```python
from jane_extractor_sdk.types import EntityOut as EntityOut
```

Повторний експорт: [jane_extractor_sdk.types.EntityOut](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityout).

## jane_extractor_sdk.ExtractResult

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:9](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L9).

```python
from jane_extractor_sdk.types import ExtractResult as ExtractResult
```

Повторний експорт: [jane_extractor_sdk.types.ExtractResult](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresult).

## jane_extractor_sdk.Material

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:9](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L9).

```python
from jane_extractor_sdk.types import Material as Material
```

Повторний експорт: [jane_extractor_sdk.types.Material](jane_extractor_sdk.types.md#jane_extractor_sdktypesmaterial).

## jane_extractor_sdk.Unrecognized

**Повторний експорт.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:9](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L9).

```python
from jane_extractor_sdk.types import Unrecognized as Unrecognized
```

Повторний експорт: [jane_extractor_sdk.types.Unrecognized](jane_extractor_sdk.types.md#jane_extractor_sdktypesunrecognized).

## jane_extractor_sdk.__version__

**Змінна.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/__init__.py:11](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py#L11).

```python
__version__ = '0.1.0'
```
