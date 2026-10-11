# Модуль `jane_llm.prompt`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/prompt.py](../../../../../services/llm/src/jane_llm/prompt.py). Не редагуйте вручну.

Prompt assembly with a strict split between trusted instructions and untrusted data (TZ §11).

* Trusted text (the platform preamble and ``instructions`` of the caller or the package) goes only to the provider's **system** channel.
* Untrusted data (page content, messages, code under analysis, template renderings) goes only to the **user** channel, each part wrapped in delimiters carrying a fresh random nonce (128 bits) that is announced in the system channel. Data cannot guess the nonce of the current request.
* Any ``<<<`` in data is neutralised, so data cannot forge a delimiter even if it knew the nonce.
* Data parts never influence the system channel; the output schema is passed out of band.

## Зміст

- [Клас `DataBlock`](#клас-datablock)
- [Клас `Prompt`](#клас-prompt)
- [Функція `new_nonce`](#функція-new_nonce)
- [Функція `neutralise`](#функція-neutralise)
- [Функція `preamble`](#функція-preamble)
- [Функція `build_prompt`](#функція-build_prompt)
- [Функція `retry_hint`](#функція-retry_hint)

## Класи

### Клас `DataBlock`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.prompt` |
| Код | [prompt.py:32](../../../../../services/llm/src/jane_llm/prompt.py#L32) |

```python
@dataclass(frozen=True)
class DataBlock: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання |  |
| `media_type` | `str \| None` | — | читання |  |
| `text` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `Prompt`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.prompt` |
| Код | [prompt.py:39](../../../../../services/llm/src/jane_llm/prompt.py#L39) |

```python
@dataclass(frozen=True)
class Prompt: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `system` | `str` | — | читання |  |
| `user` | `str` | — | читання |  |
| `nonce` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `new_nonce`

```python
def new_nonce() -> str: ...
```

Код: [prompt.py:24](../../../../../services/llm/src/jane_llm/prompt.py#L24).

### Функція `neutralise`

```python
def neutralise(text: str) -> str: ...
```

Make ``text`` unable to open or close a data block.

Код: [prompt.py:45](../../../../../services/llm/src/jane_llm/prompt.py#L45).

### Функція `preamble`

```python
def preamble(nonce: str, structured: bool) -> str: ...
```

Код: [prompt.py:54](../../../../../services/llm/src/jane_llm/prompt.py#L54).

### Функція `build_prompt`

```python
def build_prompt(
    instructions: str,
    data: Sequence[DataBlock],
    *,
    structured: bool,
    nonce_factory: NonceFactory = new_nonce,
) -> Prompt: ...
```

Код: [prompt.py:70](../../../../../services/llm/src/jane_llm/prompt.py#L70).

### Функція `retry_hint`

```python
def retry_hint(errors: Sequence[tuple[str, str]]) -> str: ...
```

Trusted feedback for a schema retry: locations **in the schema** and violated keywords only.

Never pass instance paths or values here: they come from the model output and may carry data.

Код: [prompt.py:90](../../../../../services/llm/src/jane_llm/prompt.py#L90).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DELIM_OPEN` | — | `'&lt;&lt;&lt;JANE-DATA'` |  |
| `DELIM_CLOSE` | — | `'&lt;&lt;&lt;JANE-END'` |  |
| `NonceFactory` | — | `Callable[[], str]` |  |
