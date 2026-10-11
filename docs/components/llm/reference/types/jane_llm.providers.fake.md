# Модуль `jane_llm.providers.fake`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/providers/fake.py](../../../../../services/llm/src/jane_llm/providers/fake.py). Не редагуйте вручну.

Deterministic fake provider ``fake`` for tests (this and other WPs).

It deliberately behaves like a **gullible, obedient model**, so that injection tests are meaningful:

1. It reads the system channel like a model would and learns the data-block nonce announced there (``<<<JANE-DATA <nonce> ...>>>``). Text between that exact opening and closing delimiter is *data*; everything else it receives (system text and the rest of the user text) is *instructions*. Without an announced nonce **everything is instructions** (a naive prompt).
2. **It obeys injections in the instruction channel**: a phrase like ``ignore previous instructions ... {"json": "object"}`` makes it reply with that JSON object (or, without JSON, with ``INJECTION-OBEYED: <rest of the line>``) regardless of the task.
3. Otherwise it answers deterministically: the first matching script from the connection params (``responses``: ``when_data_contains`` / ``when_data_matches`` → ``output`` / ``output_text`` / ``error``), else a minimal value that satisfies the output schema, else ``fake:<sha256 prefix>``.

So an injection placed inside data is harmless **only if** the gateway really keeps data inside unforgeable delimiters; the same text in the instruction channel, or any delimiter forgery that works, changes the answer. Token counts are ``ceil(chars / 4)``.

4. It can hold its answer, so that tests get a deterministic "call still in flight" window (R-04): the ``delay_ms`` of the first matching script that has one (a script with ``delay_ms`` and no answer only sets the delay; matching goes on to the next scripts for the answer), else the connection's ``params.delay_ms``. The delay is bounded by ``limits.fake.max_delay_ms`` (``0`` turns delays off) and logged (:data:`HOLD_LOG_MESSAGE` with ``connection_id`` and ``delay_ms``) before it starts.

## Зміст

- [Клас `FakeProvider`](#клас-fakeprovider)
- [Функція `split_channels`](#функція-split_channels)
- [Функція `find_directive`](#функція-find_directive)
- [Функція `minimal_instance`](#функція-minimal_instance)

## Класи

### Клас `FakeProvider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.providers.fake` |
| Код | [fake.py:121](../../../../../services/llm/src/jane_llm/providers/fake.py#L121) |

```python
class FakeProvider: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `kind` | `'fake'` |  |

#### Метод `FakeProvider.complete`

```python
async def complete(
    self,
    request: ProviderRequest,
    connection: ResolvedConnection | None,
    limits: ServiceLimits,
) -> ProviderResponse: ...
```

Код: [fake.py:124](../../../../../services/llm/src/jane_llm/providers/fake.py#L124).

## Функції

### Функція `split_channels`

```python
def split_channels(system: str, user: str) -> tuple[str, list[str]]: ...
```

Return ``(instruction_text, data_texts)`` as the fake model understands the prompt.

Код: [fake.py:56](../../../../../services/llm/src/jane_llm/providers/fake.py#L56).

### Функція `find_directive`

```python
def find_directive(instruction_text: str) -> str | None: ...
```

The reply an obedient model would give to an injection in its instruction channel.

Код: [fake.py:67](../../../../../services/llm/src/jane_llm/providers/fake.py#L67).

### Функція `minimal_instance`

```python
def minimal_instance(schema: Any, depth: int = 0) -> Any: ...
```

Deterministic minimal JSON value valid for common JSON Schema constructs.

Код: [fake.py:84](../../../../../services/llm/src/jane_llm/providers/fake.py#L84).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `FAKE_PROVIDER_ID` | — | `'fake'` |  |
| `FAKE_MODEL_ID` | — | `'fake-deterministic-1'` |  |
| `HOLD_LOG_MESSAGE` | — | `'fake provider holds its answer'` | Log message emitted (INFO, with ``connection_id`` and ``delay_ms``) when a call starts its delay. |
| `log` | — | `logging.getLogger(__name__)` |  |
