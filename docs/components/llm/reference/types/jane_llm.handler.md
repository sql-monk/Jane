# Модуль `jane_llm.handler`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/handler.py](../../../../../services/llm/src/jane_llm/handler.py). Не редагуйте вручну.

LLM handler (``handler.v1``): executes ``kind: llm`` packages through the gateway.

For every input one structured completion is made: trusted text = the package's ``instructions`` file; untrusted data = the input (material content and metadata, rendered ``input_template``, entities or data) — never mixed into the instructions. The model output is validated against the package's ``output_schema`` (retries per ``gateway.max_schema_retries``), then mapped to ``HandlerResult``:

* ``output.data`` — the model output (a list ``{"results": [...]}`` for several inputs);
* ``output.entities`` — for each ``output.entities[]`` of the manifest with ``entity_type`` T, the items of the top-level array ``T + "s"`` (or ``T``) of the output become ``EntityRecord`` s; key fields are taken from the item, key fields named ``message``/``material``/``material_id`` fall back to the material id; observation comes from the material;
* status: ``success`` (entities, or non-empty data when the package declares no entities), ``empty``, ``failed`` with ``schema_mismatch`` / ``budget_exhausted`` / ``invalid_params``.

## Класи

### Клас `HandlerFailure`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.handler` |
| Успадкування | `Exception` |
| Код | [handler.py:65](../../../../../services/llm/src/jane_llm/handler.py#L65) |

```python
class HandlerFailure(Exception): ...
```

#### Конструктор `HandlerFailure.__init__`

```python
def __init__(
    self,
    kind: str,
    message: str,
    *,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
): ...
```

Код: [handler.py:66](../../../../../services/llm/src/jane_llm/handler.py#L66).

### Клас `LlmHandler`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.handler` |
| Код | [handler.py:73](../../../../../services/llm/src/jane_llm/handler.py#L73) |

```python
class LlmHandler: ...
```

#### Конструктор `LlmHandler.__init__`

```python
def __init__(
    self,
    gateway: Gateway,
    loader: PackageLoader,
    content: ContentReader | None = None,
) -> None: ...
```

Код: [handler.py:74](../../../../../services/llm/src/jane_llm/handler.py#L74).

#### Метод `LlmHandler.invoke`

```python
async def invoke(
    self,
    inv: dict[str, Any],
    *,
    invocation_id: str | None = None,
    force_test_mode: bool = False,
) -> dict[str, Any]: ...
```

Run one invocation; returns ``HandlerResult`` (never raises for handler failures).

Код: [handler.py:202](../../../../../services/llm/src/jane_llm/handler.py#L202).

## Функції

### Функція `render_template`

```python
def render_template(template: str, context: dict[str, Any]) -> str: ...
```

``{{path.to.value}}`` placeholders; values are JSON for non-strings, empty for missing.

Код: [handler.py:53](../../../../../services/llm/src/jane_llm/handler.py#L53).
