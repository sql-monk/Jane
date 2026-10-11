# Модуль `jane_orchestrator.engine`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/engine.py](../../../../../services/orchestrator/src/jane_orchestrator/engine.py). Не редагуйте вручну.

Queue engine: workers with leases over the orchestrator's PostgreSQL (``FOR UPDATE SKIP LOCKED``).

Four kinds of work, all claimed with a lease so several workers (threads, processes, instances) never do the same work twice and a killed worker's work is taken over once its lease expires:

* **feed** — a run's collection: start it in the collector (``Idempotency-Key`` = ``run:<id>:collect``), pull material pages with the cursor, create stage items and only then advance the cursor (the next pull acknowledges the page). A full queue (``limits.queue``) stops pulling: the collector's buffer fills up and it pauses crawling — backpressure. Reprocessing feeds stored RAW from ``storage.v1``.
* **item** — invoke a handler (``handler.v1``) with ``delivery_key`` as ``Idempotency-Key``; record the result, create downstream items and mark the item completed **in one transaction** (ADR-0008 §8). After a crash the lease expires and the item is retried with the same key: the executor returns its stored result (``duplicate: true``) instead of repeating the effect.
* **schedule** — due tasks create runs (row lock per task: exactly one run per tick).
* **sync** — push the connections registry to executors (``PUT/DELETE /v1/connections/{id}``).

## Класи

### Клас `Engine`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.engine` |
| Код | [engine.py:205](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L205) |

```python
class Engine: ...
```

The work-claiming operations; stateless apart from ``core`` (safe to share between threads).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `lease` | `timedelta` | — | читання (властивість) |  |

#### Конструктор `Engine.__init__`

```python
def __init__(self, core: Core) -> None: ...
```

Код: [engine.py:208](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L208).

#### Метод `Engine.claim_item`

```python
def claim_item(self, worker: str) -> dict[str, Any] | None: ...
```

Код: [engine.py:217](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L217).

#### Метод `Engine.process_item`

```python
def process_item(self, item: dict[str, Any], worker: str) -> str: ...
```

Invoke the handler for a claimed item and record the outcome. Returns the outcome label.

Код: [engine.py:236](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L236).

#### Метод `Engine.claim_feed`

```python
def claim_feed(self, worker: str) -> dict[str, Any] | None: ...
```

Код: [engine.py:708](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L708).

#### Метод `Engine.process_feed`

```python
def process_feed(self, run: dict[str, Any], worker: str) -> str: ...
```

Код: [engine.py:744](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L744).

#### Метод `Engine.schedule_due`

```python
def schedule_due(self) -> int: ...
```

Create runs for due tasks (row lock per task: one run per tick across all instances).

Код: [engine.py:1259](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1259).

#### Метод `Engine.reap`

```python
def reap(self) -> int: ...
```

Close runs nobody else will close: a cancelling or drained run whose last worker died (the item and feed paths never see it again), and runs over ``timeouts.run_timeout_ms`` in any phase.

Only runs that need action are selected, so busy runs never crowd out the ones to close (a batch of ``reap_batch`` always makes progress). Several reapers may pick the same run: state changes are conditional and only the reaper that changed the state counts it and calls the collector.

Код: [engine.py:1289](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1289).

#### Метод `Engine.sync_budgets`

```python
def sync_budgets(self, worker: str) -> int: ...
```

Push ``limits.llm.budget`` / ``max_requests_per_minute`` of sources and tasks to the LLM gateway (``llm.v1 PUT/DELETE /v1/budgets/{scope_type}/{scope_id}``), idempotently, with retries.

Код: [engine.py:1364](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1364).

#### Метод `Engine.sync_connections`

```python
def sync_connections(self, worker: str) -> int: ...
```

Код: [engine.py:1425](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1425).

### Клас `Worker`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.engine` |
| Код | [engine.py:1508](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1508) |

```python
class Worker: ...
```

A thread that repeatedly claims and processes work (feeds first, then items, schedules, syncs).

#### Конструктор `Worker.__init__`

```python
def __init__(self, engine: Engine, name: str, *, scheduler: bool = True) -> None: ...
```

Код: [engine.py:1511](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1511).

#### Метод `Worker.start`

```python
def start(self) -> None: ...
```

Код: [engine.py:1519](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1519).

#### Метод `Worker.stop`

```python
def stop(self, timeout: float | None = None) -> None: ...
```

Код: [engine.py:1522](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1522).

#### Метод `Worker.step`

```python
def step(self) -> bool: ...
```

One unit of work; ``False`` when there was nothing to do.

Код: [engine.py:1526](../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1526).
