# jane_llm.prompt

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.prompt.DELIM_OPEN](#jane_llmpromptdelim_open)
- [jane_llm.prompt.DELIM_CLOSE](#jane_llmpromptdelim_close)
- [jane_llm.prompt.new_nonce](#jane_llmpromptnew_nonce)
- [jane_llm.prompt.NonceFactory](#jane_llmpromptnoncefactory)
- [jane_llm.prompt.DataBlock](#jane_llmpromptdatablock)
- [jane_llm.prompt.DataBlock.__init__](#jane_llmpromptdatablock__init__)
- [jane_llm.prompt.DataBlock.name](#jane_llmpromptdatablockname)
- [jane_llm.prompt.DataBlock.media_type](#jane_llmpromptdatablockmedia_type)
- [jane_llm.prompt.DataBlock.text](#jane_llmpromptdatablocktext)
- [jane_llm.prompt.Prompt](#jane_llmpromptprompt)
- [jane_llm.prompt.Prompt.__init__](#jane_llmpromptprompt__init__)
- [jane_llm.prompt.Prompt.system](#jane_llmpromptpromptsystem)
- [jane_llm.prompt.Prompt.user](#jane_llmpromptpromptuser)
- [jane_llm.prompt.Prompt.nonce](#jane_llmpromptpromptnonce)
- [jane_llm.prompt.neutralise](#jane_llmpromptneutralise)
- [jane_llm.prompt.preamble](#jane_llmpromptpreamble)
- [jane_llm.prompt.build_prompt](#jane_llmpromptbuild_prompt)
- [jane_llm.prompt.retry_hint](#jane_llmpromptretry_hint)

## jane_llm.prompt.DELIM_OPEN

**Константа.** Код: [services/llm/src/jane_llm/prompt.py:19](../../../../../../services/llm/src/jane_llm/prompt.py#L19).

```python
DELIM_OPEN = '<<<JANE-DATA'
```

## jane_llm.prompt.DELIM_CLOSE

**Константа.** Код: [services/llm/src/jane_llm/prompt.py:20](../../../../../../services/llm/src/jane_llm/prompt.py#L20).

```python
DELIM_CLOSE = '<<<JANE-END'
```

## jane_llm.prompt.new_nonce

**Функція.** Код: [services/llm/src/jane_llm/prompt.py:24](../../../../../../services/llm/src/jane_llm/prompt.py#L24).

```python
def new_nonce() -> str:
```

Результат: `str`.

## jane_llm.prompt.NonceFactory

**Змінна.** Код: [services/llm/src/jane_llm/prompt.py:28](../../../../../../services/llm/src/jane_llm/prompt.py#L28).

```python
NonceFactory = Callable[[], str]
```

## jane_llm.prompt.DataBlock

**Клас.** Код: [services/llm/src/jane_llm/prompt.py:32](../../../../../../services/llm/src/jane_llm/prompt.py#L32).

```python
class DataBlock:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_llm.prompt.md#jane_llmpromptdatablockname) | Поле | ні |
| [media_type](jane_llm.prompt.md#jane_llmpromptdatablockmedia_type) | Поле | ні |
| [text](jane_llm.prompt.md#jane_llmpromptdatablocktext) | Поле | ні |
| [__init__](jane_llm.prompt.md#jane_llmpromptdatablock__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:56](../../../../../../services/llm/tests/test_fake_provider.py#L56).

```python
prompt = build_prompt("Classify.", [DataBlock("page", None, data)], structured=False)
```

Контекст і передумови: [services/llm/tests/test_injection.py:132](../../../../../../services/llm/tests/test_injection.py#L132).

```python
prompt = build_prompt(
        "Classify the page type.",
        [DataBlock("page", "text/html", BENIGN)],
        structured=True,
        nonce_factory=lambda: "f" * 32,
    )
```

## jane_llm.prompt.DataBlock.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/prompt.py:32](../../../../../../services/llm/src/jane_llm/prompt.py#L32).

```python
def __init__(self, name: str, media_type: str | None, text: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `media_type` | `str \| None` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:56](../../../../../../services/llm/tests/test_fake_provider.py#L56).

```python
prompt = build_prompt("Classify.", [DataBlock("page", None, data)], structured=False)
```

Контекст і передумови: [services/llm/tests/test_injection.py:132](../../../../../../services/llm/tests/test_injection.py#L132).

```python
prompt = build_prompt(
        "Classify the page type.",
        [DataBlock("page", "text/html", BENIGN)],
        structured=True,
        nonce_factory=lambda: "f" * 32,
    )
```

## jane_llm.prompt.DataBlock.name

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:33](../../../../../../services/llm/src/jane_llm/prompt.py#L33).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.DataBlock.media_type

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:34](../../../../../../services/llm/src/jane_llm/prompt.py#L34).

```python
media_type: str | None
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.DataBlock.text

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:35](../../../../../../services/llm/src/jane_llm/prompt.py#L35).

```python
text: str
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.Prompt

**Клас.** Код: [services/llm/src/jane_llm/prompt.py:39](../../../../../../services/llm/src/jane_llm/prompt.py#L39).

```python
class Prompt:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [system](jane_llm.prompt.md#jane_llmpromptpromptsystem) | Поле | ні |
| [user](jane_llm.prompt.md#jane_llmpromptpromptuser) | Поле | ні |
| [nonce](jane_llm.prompt.md#jane_llmpromptpromptnonce) | Поле | ні |
| [__init__](jane_llm.prompt.md#jane_llmpromptprompt__init__) | Конструктор dataclass | ні |

## jane_llm.prompt.Prompt.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/prompt.py:39](../../../../../../services/llm/src/jane_llm/prompt.py#L39).

```python
def __init__(self, system: str, user: str, nonce: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `system` | `str` | `—` | positional-or-keyword |
| `user` | `str` | `—` | positional-or-keyword |
| `nonce` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.prompt.Prompt.system

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:40](../../../../../../services/llm/src/jane_llm/prompt.py#L40).

```python
system: str
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.Prompt.user

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:41](../../../../../../services/llm/src/jane_llm/prompt.py#L41).

```python
user: str
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.Prompt.nonce

**Поле.** Код: [services/llm/src/jane_llm/prompt.py:42](../../../../../../services/llm/src/jane_llm/prompt.py#L42).

```python
nonce: str
```

Доступ: читання — так; запис — ні.

## jane_llm.prompt.neutralise

**Функція.** Код: [services/llm/src/jane_llm/prompt.py:45](../../../../../../services/llm/src/jane_llm/prompt.py#L45).

```python
def neutralise(text: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Make ``text`` unable to open or close a data block.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:36](../../../../../../services/llm/tests/test_units.py#L36).

```python
assert "<<<" not in neutralise(evil)
```

Контекст і передумови: [services/llm/tests/test_units.py:38](../../../../../../services/llm/tests/test_units.py#L38).

```python
assert data == [neutralise(evil)]
```

## jane_llm.prompt.preamble

**Функція.** Код: [services/llm/src/jane_llm/prompt.py:54](../../../../../../services/llm/src/jane_llm/prompt.py#L54).

```python
def preamble(nonce: str, structured: bool) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `nonce` | `str` | `—` | positional-or-keyword |
| `structured` | `bool` | `—` | positional-or-keyword |

Результат: `str`.

## jane_llm.prompt.build_prompt

**Функція.** Код: [services/llm/src/jane_llm/prompt.py:70](../../../../../../services/llm/src/jane_llm/prompt.py#L70).

```python
def build_prompt(instructions: str, data: Sequence[DataBlock], *, structured: bool, nonce_factory: NonceFactory=new_nonce) -> Prompt:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `instructions` | `str` | `—` | positional-or-keyword |
| `data` | `Sequence[DataBlock]` | `—` | positional-or-keyword |
| `structured` | `bool` | `—` | keyword-only |
| `nonce_factory` | `NonceFactory` | `new_nonce` | keyword-only |

Результат: `Prompt`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:56](../../../../../../services/llm/tests/test_fake_provider.py#L56).

```python
prompt = build_prompt("Classify.", [DataBlock("page", None, data)], structured=False)
```

Контекст і передумови: [services/llm/tests/test_injection.py:132](../../../../../../services/llm/tests/test_injection.py#L132).

```python
prompt = build_prompt(
        "Classify the page type.",
        [DataBlock("page", "text/html", BENIGN)],
        structured=True,
        nonce_factory=lambda: "f" * 32,
    )
```

## jane_llm.prompt.retry_hint

**Функція.** Код: [services/llm/src/jane_llm/prompt.py:90](../../../../../../services/llm/src/jane_llm/prompt.py#L90).

```python
def retry_hint(errors: Sequence[tuple[str, str]]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `errors` | `Sequence[tuple[str, str]]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Trusted feedback for a schema retry: locations **in the schema** and violated keywords only.

Never pass instance paths or values here: they come from the model output and may carry data.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_injection.py:248](../../../../../../services/llm/tests/test_injection.py#L248).

```python
leaky_system = prompt.system + retry_hint([("/" + EVIL_KEY, "type")])
```
