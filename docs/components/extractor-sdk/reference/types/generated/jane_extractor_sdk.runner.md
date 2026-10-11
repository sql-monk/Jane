# jane_extractor_sdk.runner

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.runner.PROTOCOL_VERSION](#jane_extractor_sdkrunnerprotocol_version)
- [jane_extractor_sdk.runner.execute](#jane_extractor_sdkrunnerexecute)
- [jane_extractor_sdk.runner.main](#jane_extractor_sdkrunnermain)

## jane_extractor_sdk.runner.PROTOCOL_VERSION

**Константа.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/runner.py:42](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py#L42).

```python
PROTOCOL_VERSION = 1
```

## jane_extractor_sdk.runner.execute

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/runner.py:120](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py#L120).

```python
def execute(request: Mapping[str, Any], workdir: Path, *, recorder: _Recorder | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `workdir` | `Path` | `—` | positional-or-keyword |
| `recorder` | `_Recorder \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `TypeError`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Run the entry callable for every input of ``request``; return the protocol response.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:244](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L244).

```python
out = execute(req, pkg)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:254](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L254).

```python
out = execute(request_for(pkg, {}), pkg)
```

## jane_extractor_sdk.runner.main

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/runner.py:178](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py#L178).

```python
def main(argv: list[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `list[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.
