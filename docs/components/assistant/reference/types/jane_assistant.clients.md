# Модуль `jane_assistant.clients`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/clients.py](../../../../../services/assistant/src/jane_assistant/clients.py). Не редагуйте вручну.

Clients of neighbour services, strictly by their contracts (``contracts/openapi/*.v1.yaml``).

Only the operations the assistant needs are wrapped. Every POST with a side effect carries an ``Idempotency-Key`` derived from the assistant job, so a retry never duplicates the effect. Long operations (``202`` + Job) are awaited with :meth:`ServiceClient.wait_for_job`.

## Класи

### Клас `Neighbours`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.clients` |
| Код | [clients.py:343](../../../../../services/assistant/src/jane_assistant/clients.py#L343) |

```python
@dataclass
class Neighbours: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `llm` | `LlmClient` | — | читання й запис |  |
| `registry` | `RegistryClient` | — | читання й запис |  |
| `collectors` | `dict[str, CollectorClient]` | — | читання й запис |  |
| `handler` | `HandlerClient` | — | читання й запис |  |
| `orchestrator` | `OrchestratorClient` | — | читання й запис |  |
| `storage` | `StorageClient` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Neighbours.collector`

```python
def collector(self, source_kind: str) -> CollectorClient: ...
```

Код: [clients.py:352](../../../../../services/assistant/src/jane_assistant/clients.py#L352).

#### Метод `Neighbours.from_settings`

```python
@classmethod
def from_settings(
    cls,
    settings: Settings,
    limits: ClientLimits,
    transports: Mapping[str, httpx.AsyncBaseTransport] | None = None,
    *,
    llm_limits: ClientLimits | None = None,
) -> Neighbours: ...
```

Clients for configured URLs. ``transports`` (tests) maps a neighbour name to an ASGI transport; the URL then only provides the base. ``llm_limits`` - the LLM gateway client's own limits (a model call is far longer than a call of another neighbour, ``limits.llm_call``); default ``limits``.

Код: [clients.py:359](../../../../../services/assistant/src/jane_assistant/clients.py#L359).

#### Метод `Neighbours.aclose`

```python
async def aclose(self) -> None: ...
```

Код: [clients.py:407](../../../../../services/assistant/src/jane_assistant/clients.py#L407).

## Функції

### Функція `idem_key`

```python
def idem_key(*parts: str) -> str: ...
```

Deterministic ``Idempotency-Key`` (1-255 printable ASCII) from job-scoped parts.

Код: [clients.py:39](../../../../../services/assistant/src/jane_assistant/clients.py#L39).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `RemoteError` | `jane_kit.clients` |
