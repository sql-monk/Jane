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
| Код | [app.py:164](../../../../../services/storage/src/jane_storage/app.py#L164) |

```python
class InvocationResults: ...
```

Recent HandlerResults of this instance (``GET /v1/invocations/{id}``).

#### Конструктор `InvocationResults.__init__`

```python
def __init__(self, max_entries: int) -> None: ...
```

Код: [app.py:167](../../../../../services/storage/src/jane_storage/app.py#L167).

#### Метод `InvocationResults.put`

```python
def put(self, result: dict[str, Any]) -> None: ...
```

Код: [app.py:171](../../../../../services/storage/src/jane_storage/app.py#L171).

#### Метод `InvocationResults.get`

```python
def get(self, invocation_id: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [app.py:176](../../../../../services/storage/src/jane_storage/app.py#L176).

## Функції

### Функція `entity_state`

```python
def entity_state(snap: EntitySnapshot) -> dict[str, Any]: ...
```

Код: [app.py:148](../../../../../services/storage/src/jane_storage/app.py#L148).

### Функція `history_entry`

```python
def history_entry(event: HistoryEvent) -> dict[str, Any]: ...
```

Код: [app.py:154](../../../../../services/storage/src/jane_storage/app.py#L154).

### Функція `build_app`

```python
def build_app(
    settings: Settings | None = None,
    *,
    registry_transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI: ...
```

The storage service. ``registry_transport`` Р В Р вЂ Р В РІР‚С™Р Р†Р вЂљРЎСљ HTTP transport to the registry (tests).

Винятки в коді функції: `JaneError`, `ValidationFailed`, `NotFound`, `IdempotencyKeyReused`, `IdempotencyInProgress`, `Timeout`.

Код: [app.py:220](../../../../../services/storage/src/jane_storage/app.py#L220).

### Функція `manifest_test_cases`

```python
def manifest_test_cases(
    pkg: StoragePackage,
    body: Mapping[str, Any],
) -> list[tuple[str, dict[str, Any], str]]: ...
```

Invocations (``test_mode``) for the package's manifest tests and extra cases of a test run.

Код: [app.py:1050](../../../../../services/storage/src/jane_storage/app.py#L1050).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `REQUEST_LIMIT_PATHS` | — | `{'timeouts.sync_response_max_ms', 'timeouts.request_timeout_ms'}` | Parts of ``HandlerInvocation.limits`` this executor applies (min with its own hard caps). The stage's ``retries`` is the caller's policy (the orchestrator re-sends with the same key) and is ignored here: the core's own ``CONFLICT`` retries come from ``limits.conflict_retries`` of the service configuration. |
