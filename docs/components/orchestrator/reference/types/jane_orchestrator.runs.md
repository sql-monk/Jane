# Модуль `jane_orchestrator.runs`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/runs.py](../../../../../services/orchestrator/src/jane_orchestrator/runs.py). Не редагуйте вручну.

Runs: creation (with a snapshot of the task, source and effective limits), state, cancellation, items, the material trace and the ``Job`` view (run_id = job_id, ``kind: run``).

## Класи

### Клас `Runs`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.runs` |
| Код | [runs.py:55](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L55) |

```python
class Runs: ...
```

#### Конструктор `Runs.__init__`

```python
def __init__(self, core: Core) -> None: ...
```

Код: [runs.py:56](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L56).

#### Метод `Runs.create`

```python
def create(
    self,
    conn: Any,
    task_row: Mapping[str, Any],
    source_doc: Mapping[str, Any],
    *,
    trigger: str,
    test_mode: bool = False,
    reason: str | None = None,
    input_override: Mapping[str, Any] | None = None,
    request_limits: Mapping[str, Any] | None = None,
    requested_by: str | None = None,
    idempotency_key: str | None = None,
    from_stage: str | None = None,
    enforce_overlap: bool = True,
) -> dict[str, Any] | None: ...
```

Insert a queued run. Returns the run row, or ``None`` when a scheduled run is skipped (``overlap: skip`` with an active run). A manual start in that case is ``409 conflict``.

Винятки в коді методу: `ValidationFailed`, `Conflict`, `LimitExceeded`.

Код: [runs.py:60](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L60).

#### Метод `Runs.get_row`

```python
def get_row(self, conn: Any, run_id: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [runs.py:162](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L162).

#### Метод `Runs.run_view`

```python
def run_view(
    self,
    conn: Any,
    row: Mapping[str, Any],
    *,
    include_summary: bool = True,
) -> dict[str, Any]: ...
```

Код: [runs.py:191](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L191).

#### Метод `Runs.output_summary`

```python
@staticmethod
def output_summary(conn: Any, run: Mapping[str, Any]) -> dict[str, Any]: ...
```

Unique entity identities recorded by this run; never query a storage database.

Legacy traces were capped, so their identities are a lower bound and labelled as such.

Код: [runs.py:241](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L241).

#### Метод `Runs.job_view`

```python
def job_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]: ...
```

Код: [runs.py:318](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L318).

#### Метод `Runs.list_runs`

```python
def list_runs(
    self,
    conn: Any,
    *,
    task_id: str | None,
    status: str | None,
    since: datetime | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [runs.py:364](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L364).

#### Метод `Runs.item_view`

```python
@staticmethod
def item_view(r: Mapping[str, Any]) -> dict[str, Any]: ...
```

Код: [runs.py:398](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L398).

#### Метод `Runs.list_items`

```python
def list_items(
    self,
    conn: Any,
    run_id: str,
    *,
    stage_id: str | None,
    status: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [runs.py:418](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L418).

#### Метод `Runs.trace`

```python
def trace(self, conn: Any, material_id: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [runs.py:447](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L447).

#### Метод `Runs.request_cancel`

```python
def request_cancel(
    self,
    run_id: str,
    actor: str,
    reason: str | None,
) -> tuple[dict[str, Any], bool]: ...
```

Returns ``(job, accepted)``; ``accepted=False`` when the run was already terminal (200).

Винятки в коді методу: `NotFound`.

Код: [runs.py:501](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L501).

#### Метод `Runs.fail_run`

```python
def fail_run(self, conn: Any, run_id: str, problem: Mapping[str, Any]) -> bool: ...
```

Mark a run failed (``on_failure: fail_run``, collector failure, run timeout). Caller holds a tx.

Returns ``True`` only for the caller that actually changed the state (several workers or reapers may race for the same run): only that caller counts the metric and cancels the collection.

Код: [runs.py:530](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L530).

#### Метод `Runs.maybe_finish`

```python
def maybe_finish(self, run_id: str) -> str | None: ...
```

Close the run when the feed is exhausted and no item is active. Returns the new status.

Код: [runs.py:552](../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L552).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ACTIVE_ITEM` | — | `('queued', 'retrying', 'leased', 'running')` |  |
| `TERMINAL_RUN` | — | `('succeeded', 'failed', 'cancelled')` |  |
