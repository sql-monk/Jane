# Модуль `jane_storage.app`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/app.py](../../../../../services/storage/src/jane_storage/app.py). Не редагуйте вручну.

HTTP API of the storage service.

* ``handler.v1`` (write path): ``POST /v1/invocations``, ``GET /v1/invocations/{id}``, ``POST /v1/test-runs``, ``/v1/connections*``, ``/v1/jobs/*``;
* ``storage.v1`` (read path): ``/v1/entities``, ``/v1/entity-history``, ``/v1/objects*``;
* ``/v1/health``, ``/v1/info``, ``/metrics`` from jane-kit.

Idempotency: ``Idempotency-Key`` must equal ``delivery.delivery_key``. The durable deduplication is the delivery record kept by the adapter together with the data (works across instances and restarts); the in-memory key store only rejects a reused key with a different body (422) and a concurrent duplicate (409). A repeated delivery is executed again and returns the stored acks with ``duplicate: true`` (``Idempotency-Replayed: true`` if this instance saw the key).

## Зміст

- [Клас `InvocationResults`](#клас-invocationresults)
- [Функція `entity_state`](#функція-entity_state)
- [Функція `history_entry`](#функція-history_entry)
- [Функція `build_app`](#функція-build_app)
- [Функція `manifest_test_cases`](#функція-manifest_test_cases)

## Класи

### Клас `InvocationResults`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.app` |
| Код | [app.py:163](../../../../../services/storage/src/jane_storage/app.py#L163) |

```python
class InvocationResults: ...
```

Recent HandlerResults of this instance (``GET /v1/invocations/{id}``).

#### Конструктор `InvocationResults.__init__`

```python
def __init__(self, max_entries: int) -> None: ...
```

Код: [app.py:166](../../../../../services/storage/src/jane_storage/app.py#L166).

#### Метод `InvocationResults.put`

```python
def put(self, result: dict[str, Any]) -> None: ...
```

Код: [app.py:170](../../../../../services/storage/src/jane_storage/app.py#L170).

#### Метод `InvocationResults.get`

```python
def get(self, invocation_id: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [app.py:175](../../../../../services/storage/src/jane_storage/app.py#L175).

## Функції

### Функція `entity_state`

```python
def entity_state(snap: EntitySnapshot) -> dict[str, Any]: ...
```

Код: [app.py:147](../../../../../services/storage/src/jane_storage/app.py#L147).

### Функція `history_entry`

```python
def history_entry(event: HistoryEvent) -> dict[str, Any]: ...
```

Код: [app.py:153](../../../../../services/storage/src/jane_storage/app.py#L153).

### Функція `build_app`

```python
def build_app(
    settings: Settings | None = None,
    *,
    registry_transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI: ...
```

The storage service. ``registry_transport`` — HTTP transport to the registry (tests).

Винятки в коді функції: `JaneError`, `ValidationFailed`, `NotFound`, `IdempotencyKeyReused`, `IdempotencyInProgress`.

Код: [app.py:219](../../../../../services/storage/src/jane_storage/app.py#L219).

### Функція `manifest_test_cases`

```python
def manifest_test_cases(
    pkg: StoragePackage,
    body: Mapping[str, Any],
) -> list[tuple[str, dict[str, Any], str]]: ...
```

Invocations (``test_mode``) for the package's manifest tests and extra cases of a test run.

Код: [app.py:839](../../../../../services/storage/src/jane_storage/app.py#L839).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `REQUEST_LIMIT_PATHS` | — | `{'timeouts.sync_response_max_ms', 'timeouts.request_timeout_ms'}` | Parts of ``HandlerInvocation.limits`` this executor applies (min with its own hard caps). The stage's ``retries`` is the caller's policy (the orchestrator re-sends with the same key) and is ignored here: the core's own ``CONFLICT`` retries come from ``limits.conflict_retries`` of the service configuration. |
