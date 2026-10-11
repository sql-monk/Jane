# Модуль `jane_extractor_sdk.context`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/context.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py). Не редагуйте вручну.

Execution context passed to the extractor callable as ``ctx``.

## Класи

### Клас `Context`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_extractor_sdk.context` |
| Код | [context.py:65](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L65) |

```python
class Context: ...
```

What the extractor may use besides ``material`` and ``params``.

* :meth:`bytes` / :meth:`text` - content of the material (inline or blob: the runtime has already fetched and checked it; the extractor never downloads anything, there is no network in the sandbox);
* :attr:`log` - diagnostics; :attr:`test_mode` - run without writing to working data (informative);
* :attr:`params` - the same parameters the callable receives.

#### Конструктор `Context.__init__`

```python
def __init__(
    self,
    material: Mapping[str, Any],
    params: Mapping[str, Any] | None = None,
    *,
    content_loader: Callable[[], bytes] | None = None,
    test_mode: bool = False,
) -> None: ...
```

Код: [context.py:74](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L74).

#### Метод `Context.bytes`

```python
def bytes(self) -> bytes: ...
```

Raw bytes of the material content.

Винятки в коді методу: `RuntimeError`.

Код: [context.py:90](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L90).

#### Метод `Context.charset`

```python
def charset(self) -> str: ...
```

Charset from the content, then the format, then ``utf-8`` (unknown names fall back to utf-8).

Код: [context.py:102](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L102).

#### Метод `Context.text`

```python
def text(self, errors: str = 'replace') -> str: ...
```

Content decoded as text (inline ``utf-8`` content is already text).

Код: [context.py:115](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L115).

### Клас `DiagnosticsLog`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_extractor_sdk.context` |
| Код | [context.py:15](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L15) |

```python
class DiagnosticsLog: ...
```

``ctx.log``: messages that end up in ``HandlerResult.diagnostics.messages``.

Use it instead of ``print``: stdout/stderr of the sandbox go only to the (truncated) execution log.

#### Конструктор `DiagnosticsLog.__init__`

```python
def __init__(self, material_id: str | None = None) -> None: ...
```

Код: [context.py:21](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L21).

#### Метод `DiagnosticsLog.add`

```python
def add(
    self,
    level: DiagnosticLevel,
    message: str,
    *,
    code: str | None = None,
    selector: str | None = None,
    pointer: str | None = None,
) -> None: ...
```

Код: [context.py:25](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L25).

#### Метод `DiagnosticsLog.debug`

```python
def debug(self, message: str, **kw: Any) -> None: ...
```

Код: [context.py:45](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L45).

#### Метод `DiagnosticsLog.info`

```python
def info(self, message: str, **kw: Any) -> None: ...
```

Код: [context.py:48](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L48).

#### Метод `DiagnosticsLog.warning`

```python
def warning(self, message: str, **kw: Any) -> None: ...
```

Код: [context.py:51](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L51).

#### Метод `DiagnosticsLog.error`

```python
def error(self, message: str, **kw: Any) -> None: ...
```

Код: [context.py:54](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L54).
