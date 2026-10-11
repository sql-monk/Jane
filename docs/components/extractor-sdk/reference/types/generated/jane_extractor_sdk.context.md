# jane_extractor_sdk.context

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.context.DiagnosticsLog](#jane_extractor_sdkcontextdiagnosticslog)
- [jane_extractor_sdk.context.DiagnosticsLog.__init__](#jane_extractor_sdkcontextdiagnosticslog__init__)
- [jane_extractor_sdk.context.DiagnosticsLog.messages](#jane_extractor_sdkcontextdiagnosticslogmessages)
- [jane_extractor_sdk.context.DiagnosticsLog.add](#jane_extractor_sdkcontextdiagnosticslogadd)
- [jane_extractor_sdk.context.DiagnosticsLog.debug](#jane_extractor_sdkcontextdiagnosticslogdebug)
- [jane_extractor_sdk.context.DiagnosticsLog.info](#jane_extractor_sdkcontextdiagnosticsloginfo)
- [jane_extractor_sdk.context.DiagnosticsLog.warning](#jane_extractor_sdkcontextdiagnosticslogwarning)
- [jane_extractor_sdk.context.DiagnosticsLog.error](#jane_extractor_sdkcontextdiagnosticslogerror)
- [jane_extractor_sdk.context.Context](#jane_extractor_sdkcontextcontext)
- [jane_extractor_sdk.context.Context.__init__](#jane_extractor_sdkcontextcontext__init__)
- [jane_extractor_sdk.context.Context.material](#jane_extractor_sdkcontextcontextmaterial)
- [jane_extractor_sdk.context.Context.params](#jane_extractor_sdkcontextcontextparams)
- [jane_extractor_sdk.context.Context.test_mode](#jane_extractor_sdkcontextcontexttest_mode)
- [jane_extractor_sdk.context.Context.log](#jane_extractor_sdkcontextcontextlog)
- [jane_extractor_sdk.context.Context.bytes](#jane_extractor_sdkcontextcontextbytes)
- [jane_extractor_sdk.context.Context.charset](#jane_extractor_sdkcontextcontextcharset)
- [jane_extractor_sdk.context.Context.text](#jane_extractor_sdkcontextcontexttext)

## jane_extractor_sdk.context.DiagnosticsLog

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:15](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L15).

```python
class DiagnosticsLog:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslog__init__) | Конструктор | ні |
| [messages](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslogmessages) | Поле екземпляра | ні |
| [add](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslogadd) | Метод | ні |
| [debug](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslogdebug) | Метод | ні |
| [info](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticsloginfo) | Метод | ні |
| [warning](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslogwarning) | Метод | ні |
| [error](jane_extractor_sdk.context.md#jane_extractor_sdkcontextdiagnosticslogerror) | Метод | ні |

### Опис із вихідного коду

```text
``ctx.log``: messages that end up in ``HandlerResult.diagnostics.messages``.

Use it instead of ``print``: stdout/stderr of the sandbox go only to the (truncated) execution log.
```

## jane_extractor_sdk.context.DiagnosticsLog.__init__

**Конструктор.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:21](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L21).

```python
def __init__(self, material_id: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material_id` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_extractor_sdk.context.DiagnosticsLog.messages

**Поле екземпляра.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:22](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L22).

```python
self.messages: list[Diagnostic] = []
```

## jane_extractor_sdk.context.DiagnosticsLog.add

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:25](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L25).

```python
def add(self, level: DiagnosticLevel, message: str, *, code: str | None=None, selector: str | None=None, pointer: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `level` | `DiagnosticLevel` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `code` | `str \| None` | `None` | keyword-only |
| `selector` | `str \| None` | `None` | keyword-only |
| `pointer` | `str \| None` | `None` | keyword-only |

Результат: `None`.

## jane_extractor_sdk.context.DiagnosticsLog.debug

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:45](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L45).

```python
def debug(self, message: str, **kw: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `None`.

## jane_extractor_sdk.context.DiagnosticsLog.info

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:48](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L48).

```python
def info(self, message: str, **kw: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `None`.

## jane_extractor_sdk.context.DiagnosticsLog.warning

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:51](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L51).

```python
def warning(self, message: str, **kw: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `None`.

## jane_extractor_sdk.context.DiagnosticsLog.error

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:54](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L54).

```python
def error(self, message: str, **kw: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `None`.

## jane_extractor_sdk.context.Context

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:65](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L65).

```python
class Context:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontext__init__) | Конструктор | ні |
| [material](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontextmaterial) | Поле екземпляра | ні |
| [params](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontextparams) | Поле екземпляра | ні |
| [test_mode](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontexttest_mode) | Поле екземпляра | ні |
| [log](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontextlog) | Поле екземпляра | ні |
| [bytes](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontextbytes) | Метод | ні |
| [charset](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontextcharset) | Метод | ні |
| [text](jane_extractor_sdk.context.md#jane_extractor_sdkcontextcontexttext) | Метод | ні |

### Опис із вихідного коду

```text
What the extractor may use besides ``material`` and ``params``.

* :meth:`bytes` / :meth:`text` - content of the material (inline or blob: the runtime has already fetched
  and checked it; the extractor never downloads anything, there is no network in the sandbox);
* :attr:`log` - diagnostics; :attr:`test_mode` - run without writing to working data (informative);
* :attr:`params` - the same parameters the callable receives.
```

## jane_extractor_sdk.context.Context.__init__

**Конструктор.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:74](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L74).

```python
def __init__(self, material: Mapping[str, Any], params: Mapping[str, Any] | None=None, *, content_loader: Callable[[], bytes] | None=None, test_mode: bool=False) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `content_loader` | `Callable[[], bytes] \| None` | `None` | keyword-only |
| `test_mode` | `bool` | `False` | keyword-only |

Результат: `None`.

## jane_extractor_sdk.context.Context.material

**Поле екземпляра.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:82](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L82).

```python
self.material = material
```

## jane_extractor_sdk.context.Context.params

**Поле екземпляра.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:83](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L83).

```python
self.params: Mapping[str, Any] = params or {}
```

## jane_extractor_sdk.context.Context.test_mode

**Поле екземпляра.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:84](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L84).

```python
self.test_mode = test_mode
```

## jane_extractor_sdk.context.Context.log

**Поле екземпляра.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:86](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L86).

```python
self.log = DiagnosticsLog(material_id if isinstance(material_id, str) else None)
```

## jane_extractor_sdk.context.Context.bytes

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:90](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L90).

```python
def bytes(self) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Raw bytes of the material content.
```

## jane_extractor_sdk.context.Context.charset

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:102](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L102).

```python
def charset(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Charset from the content, then the format, then ``utf-8`` (unknown names fall back to utf-8).
```

## jane_extractor_sdk.context.Context.text

**Метод.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/context.py:115](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/context.py#L115).

```python
def text(self, errors: str='replace') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `errors` | `str` | `'replace'` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Content decoded as text (inline ``utf-8`` content is already text).
```
