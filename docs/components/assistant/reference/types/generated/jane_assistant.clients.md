# jane_assistant.clients

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.clients.RemoteError](#jane_assistantclientsremoteerror)
- [jane_assistant.clients.idem_key](#jane_assistantclientsidem_key)
- [jane_assistant.clients.Neighbours](#jane_assistantclientsneighbours)
- [jane_assistant.clients.Neighbours.__init__](#jane_assistantclientsneighbours__init__)
- [jane_assistant.clients.Neighbours.llm](#jane_assistantclientsneighboursllm)
- [jane_assistant.clients.Neighbours.registry](#jane_assistantclientsneighboursregistry)
- [jane_assistant.clients.Neighbours.collectors](#jane_assistantclientsneighbourscollectors)
- [jane_assistant.clients.Neighbours.handler](#jane_assistantclientsneighbourshandler)
- [jane_assistant.clients.Neighbours.orchestrator](#jane_assistantclientsneighboursorchestrator)
- [jane_assistant.clients.Neighbours.storage](#jane_assistantclientsneighboursstorage)
- [jane_assistant.clients.Neighbours.collector](#jane_assistantclientsneighbourscollector)
- [jane_assistant.clients.Neighbours.from_settings](#jane_assistantclientsneighboursfrom_settings)
- [jane_assistant.clients.Neighbours.aclose](#jane_assistantclientsneighboursaclose)

## jane_assistant.clients.RemoteError

**Повторний експорт.** Код: [services/assistant/src/jane_assistant/clients.py:24](../../../../../../services/assistant/src/jane_assistant/clients.py#L24).

```python
from jane_kit.clients import RemoteError as RemoteError
```

Повторний експорт: [jane_kit.clients.RemoteError](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsremoteerror).

## jane_assistant.clients.idem_key

**Функція.** Код: [services/assistant/src/jane_assistant/clients.py:39](../../../../../../services/assistant/src/jane_assistant/clients.py#L39).

```python
def idem_key(*parts: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `parts` | `str` | `—` | var-positional |

Результат: `str`.

### Опис із вихідного коду

```text
Deterministic ``Idempotency-Key`` (1-255 printable ASCII) from job-scoped parts.
```

## jane_assistant.clients.Neighbours

**Клас.** Код: [services/assistant/src/jane_assistant/clients.py:343](../../../../../../services/assistant/src/jane_assistant/clients.py#L343).

```python
class Neighbours:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [llm](jane_assistant.clients.md#jane_assistantclientsneighboursllm) | Поле | ні |
| [registry](jane_assistant.clients.md#jane_assistantclientsneighboursregistry) | Поле | ні |
| [collectors](jane_assistant.clients.md#jane_assistantclientsneighbourscollectors) | Поле | ні |
| [handler](jane_assistant.clients.md#jane_assistantclientsneighbourshandler) | Поле | ні |
| [orchestrator](jane_assistant.clients.md#jane_assistantclientsneighboursorchestrator) | Поле | ні |
| [storage](jane_assistant.clients.md#jane_assistantclientsneighboursstorage) | Поле | ні |
| [collector](jane_assistant.clients.md#jane_assistantclientsneighbourscollector) | Метод | ні |
| [from_settings](jane_assistant.clients.md#jane_assistantclientsneighboursfrom_settings) | Метод | ні |
| [aclose](jane_assistant.clients.md#jane_assistantclientsneighboursaclose) | Метод | ні |
| [__init__](jane_assistant.clients.md#jane_assistantclientsneighbours__init__) | Конструктор dataclass | ні |

## jane_assistant.clients.Neighbours.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/clients.py:343](../../../../../../services/assistant/src/jane_assistant/clients.py#L343).

```python
def __init__(self, llm: LlmClient, registry: RegistryClient, collectors: dict[str, CollectorClient], handler: HandlerClient, orchestrator: OrchestratorClient, storage: StorageClient) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `llm` | `LlmClient` | `—` | positional-or-keyword |
| `registry` | `RegistryClient` | `—` | positional-or-keyword |
| `collectors` | `dict[str, CollectorClient]` | `—` | positional-or-keyword |
| `handler` | `HandlerClient` | `—` | positional-or-keyword |
| `orchestrator` | `OrchestratorClient` | `—` | positional-or-keyword |
| `storage` | `StorageClient` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.clients.Neighbours.llm

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:344](../../../../../../services/assistant/src/jane_assistant/clients.py#L344).

```python
llm: LlmClient
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.registry

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:345](../../../../../../services/assistant/src/jane_assistant/clients.py#L345).

```python
registry: RegistryClient
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.collectors

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:346](../../../../../../services/assistant/src/jane_assistant/clients.py#L346).

```python
collectors: dict[str, CollectorClient]
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.handler

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:347](../../../../../../services/assistant/src/jane_assistant/clients.py#L347).

```python
handler: HandlerClient
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.orchestrator

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:348](../../../../../../services/assistant/src/jane_assistant/clients.py#L348).

```python
orchestrator: OrchestratorClient
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.storage

**Поле.** Код: [services/assistant/src/jane_assistant/clients.py:349](../../../../../../services/assistant/src/jane_assistant/clients.py#L349).

```python
storage: StorageClient
```

Доступ: читання — так; запис — так.

## jane_assistant.clients.Neighbours.collector

**Метод.** Код: [services/assistant/src/jane_assistant/clients.py:352](../../../../../../services/assistant/src/jane_assistant/clients.py#L352).

```python
def collector(self, source_kind: str) -> CollectorClient:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_kind` | `str` | `—` | positional-or-keyword |

Результат: `CollectorClient`.

## jane_assistant.clients.Neighbours.from_settings

**Метод.** Код: [services/assistant/src/jane_assistant/clients.py:359](../../../../../../services/assistant/src/jane_assistant/clients.py#L359).

```python
def from_settings(cls, settings: Settings, limits: ClientLimits, transports: Mapping[str, httpx.AsyncBaseTransport] | None=None, *, llm_limits: ClientLimits | None=None) -> Neighbours:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ClientLimits` | `—` | positional-or-keyword |
| `transports` | `Mapping[str, httpx.AsyncBaseTransport] \| None` | `None` | positional-or-keyword |
| `llm_limits` | `ClientLimits \| None` | `None` | keyword-only |

Результат: `Neighbours`.

### Опис із вихідного коду

```text
Clients for configured URLs. ``transports`` (tests) maps a neighbour name to an ASGI
transport; the URL then only provides the base. ``llm_limits`` - the LLM gateway client's own limits
(a model call is far longer than a call of another neighbour, ``limits.llm_call``); default ``limits``.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_auth.py:53](../../../../../../services/assistant/tests/test_auth.py#L53).

```python
nb = Neighbours.from_settings(s, ClientLimits())
```

Контекст і передумови: [services/assistant/tests/test_auth.py:61](../../../../../../services/assistant/tests/test_auth.py#L61).

```python
Neighbours.from_settings(
            s.with_overrides(llm_token_ref="env:JANE_TEST_ASSISTANT_UNSET"), ClientLimits()
        )
```

## jane_assistant.clients.Neighbours.aclose

**Метод.** Код: [services/assistant/src/jane_assistant/clients.py:407](../../../../../../services/assistant/src/jane_assistant/clients.py#L407).

```python
async def aclose(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.
