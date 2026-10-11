# Модуль `jane_orchestrator.settings`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/settings.py](../../../../../services/orchestrator/src/jane_orchestrator/settings.py). Не редагуйте вручну.

Settings and limits of the orchestrator. Every limit has a safe default documented in README.md.

Two kinds of limits:

* **Contract limits** (``limits.schema.json``): the platform document lives in the orchestrator DB (``GET/PUT /v1/limits/platform``) and is merged with source → task → stage → request levels for every run (``GET /v1/limits/effective``). :class:`ContractDefaults` gives the fallback for the fields the orchestrator itself consumes when the platform document does not set them; it also seeds the platform document on the first start when no limits file is configured.
* **Internal knobs** (:class:`EngineLimits`): lease duration, polling intervals, page sizes — they are not in the contract and come from env ``JANE_ORCHESTRATOR_LIMITS__ENGINE__*``.

## Зміст

- [Клас `ExecutorConfig`](#клас-executorconfig)
- [Клас `Queue`](#клас-queue)
- [Клас `Concurrency`](#клас-concurrency)
- [Клас `Timeouts`](#клас-timeouts)
- [Клас `Transfer`](#клас-transfer)
- [Клас `ContractDefaults`](#клас-contractdefaults)
- [Клас `EngineLimits`](#клас-enginelimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Клас `Settings`](#клас-settings)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `ExecutorConfig`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `BaseModel` |
| Код | [settings.py:35](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L35) |

```python
class ExecutorConfig(BaseModel): ...
```

A service the orchestrator calls (``orchestrator.v1`` ``Executor``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `executor` | `str` | — | читання й запис |  |
| `role` | `Literal['collector', 'handler', 'storage_read', 'registry', 'llm', 'assistant']` | — | читання й запис |  |
| `base_url` | `str` | — | читання й запис |  |
| `capabilities` | `dict[str, Any]` | `Field(default_factory=dict)` | читання й запис | ``collector: web`` for collectors; ``handler_kinds: [...]`` and ``packages: ["jane.storage-*"]`` (globs of package ids routed to this executor) for handlers; ``default: true`` marks the fallback handler executor. |
| `sync_connections` | `bool \| None` | `None` | читання й запис | Push the connections registry to this executor (``PUT /v1/connections/{id}``). Default: true for collectors, handlers and llm. |
| `token_ref` | `str \| None` | `None` | читання й запис | Secret reference (``env:VAR`` / ``file:/path``, ADR-0006) of the bearer token for this executor; without it the orchestrator's own ``service_token_ref`` is used (ADR-0005 §5). |
| `token` | `SecretStr \| None` | `None` | читання й запис | Bearer token in plain text - deprecated (logged as a warning at start), use ``token_ref``. After :meth:`Settings.all_executors` it holds the resolved token (``SecretStr``: never in reprs, logs or the API). |
| `syncs_connections` | `bool` | — | читання (властивість) | ``sync_connections`` if set; otherwise collectors, handlers and llm, except an executor whose ``capabilities.connections`` is ``false`` (handler.v1: ``/v1/connections*`` are optional for it). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='forbid')` |  |

### Клас `Queue`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:74](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L74) |

```python
class Queue(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_queue_depth` | `int` | `contract_field('queue.max_queue_depth', 10000, ge=1)` | читання й запис |  |
| `max_inflight_materials` | `int` | `contract_field('queue.max_inflight_materials', 100, ge=1)` | читання й запис |  |

### Клас `Concurrency`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:79](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L79) |

```python
class Concurrency(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_parallel_runs_per_task` | `int` | `contract_field('concurrency.max_parallel_runs_per_task', 1, ge=1)` | читання й запис |  |
| `max_parallel_stage_items` | `int` | `contract_field('concurrency.max_parallel_stage_items', 4, ge=1)` | читання й запис |  |

### Клас `Timeouts`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:84](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L84) |

```python
class Timeouts(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `contract_field('timeouts.connect_timeout_ms', 5000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `contract_field('timeouts.request_timeout_ms', 30000, ge=1)` | читання й запис |  |
| `invocation_timeout_ms` | `int` | `contract_field('timeouts.invocation_timeout_ms', 60000, ge=1)` | читання й запис |  |
| `run_timeout_ms` | `int` | `contract_field('timeouts.run_timeout_ms', 21600000, ge=1)` | читання й запис |  |

### Клас `Transfer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:91](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L91) |

```python
class Transfer(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `idempotency_ttl_seconds` | `int` | `contract_field('transfer.idempotency_ttl_seconds', 86400, ge=60)` | читання й запис |  |

### Клас `ContractDefaults`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:95](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L95) |

```python
class ContractDefaults(Limits): ...
```

Fallback values of contract limits the orchestrator consumes (level ``platform``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `queue` | `Queue` | `Queue()` | читання й запис |  |
| `concurrency` | `Concurrency` | `Concurrency()` | читання й запис |  |
| `timeouts` | `Timeouts` | `Timeouts()` | читання й запис |  |
| `transfer` | `Transfer` | `Transfer()` | читання й запис |  |
| `retries` | `RetryPolicy` | `contract_field('retries', RetryPolicy(max_attempts=3, initial_backoff_ms=1000, m` | читання й запис |  |

### Клас `EngineLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:108](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L108) |

```python
class EngineLimits(Limits): ...
```

Internal knobs of the queue engine (not part of ``limits.schema.json``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `workers` | `int` | `Field(default=2, ge=0)` | читання й запис | Worker threads per process (0 — API only). |
| `lease_ms` | `int` | `Field(default=30000, ge=100)` | читання й запис | Lease of a claimed item / collection feed; extended by heartbeats while a call runs. |
| `heartbeat_ms` | `int` | `Field(default=10000, ge=50)` | читання й запис |  |
| `poll_interval_ms` | `int` | `Field(default=500, ge=10)` | читання й запис | Idle sleep of a worker when there is nothing to claim. |
| `feed_page_size` | `int` | `Field(default=100, ge=1)` | читання й запис | Materials requested from a collector per page (bounded further by queue limits). |
| `feed_wait_ms` | `int` | `Field(default=1000, ge=0)` | читання й запис | Long-poll ``wait_ms`` for collector material pages. |
| `backpressure_recheck_ms` | `int` | `Field(default=500, ge=10)` | читання й запис |  |
| `scheduler_interval_ms` | `int` | `Field(default=1000, ge=10)` | читання й запис |  |
| `sync_retry_ms` | `int` | `Field(default=5000, ge=10)` | читання й запис | Delay before retrying a failed connection sync. |
| `sync_max_attempts` | `int` | `Field(default=5, ge=1)` | читання й запис |  |
| `executor_health_timeout_ms` | `int` | `Field(default=2000, ge=1)` | читання й запис |  |
| `executor_keepalive_expiry_ms` | `int` | `Field(default=4000, ge=0)` | читання й запис | Idle time after which a pooled connection to an executor is dropped. Keep it below the executors' server keep-alive (uvicorn ``timeout_keep_alive``, 5 s for every Jane service): with equal values a request sent at the moment the server closes the idle connection fails with ``RemoteProtocolError``. |
| `executor_stale_connection_retries` | `int` | `Field(default=1, ge=0)` | читання й запис | Immediate re-sends, on a new connection, of a request that is safe to repeat (GET/HEAD/OPTIONS/PUT/ DELETE or with ``Idempotency-Key``) after the executor dropped the connection without a response. They do not spend ``retries.max_attempts`` of an item; 0 hands such an error to the item retry policy. |
| `job_poll_interval_ms` | `int` | `Field(default=500, ge=10)` | читання й запис | Polling interval for an executor's 202 job (async handler invocation). |
| `idempotency_in_progress_poll_ms` | `int` | `Field(default=500, ge=10)` | читання й запис | Delay between replays while an executor is still processing the same delivery key. |
| `idempotency_in_progress_max_wait_ms` | `int` | `Field(default=120000, ge=1)` | читання й запис | Maximum time one worker waits for an already running invocation before parking the item. |
| `idempotency_in_progress_retry_ms` | `int` | `Field(default=5000, ge=10)` | читання й запис | Delay before another worker checks a parked delivery key; run_timeout_ms bounds the run. |
| `problem_samples` | `int` | `Field(default=10, ge=0)` | читання й запис | Samples kept per problem group. |
| `trace_outputs_max` | `int` | `Field(default=100, ge=0)` | читання й запис | Output references (entity keys, stored object ids) recorded per item for the material trace. |
| `attempt_history_max` | `int` | `Field(default=20, ge=0)` | читання й запис | Diagnostic events (claims, scheduled retries, outcome) kept per item for ``attempt_history`` in run items and the material trace; the first events are kept (0 — none). |
| `stored_selection_max_ids` | `int` | `Field(default=10000, ge=1)` | читання й запис | Most ``stored_materials.object_ids`` / ``observation_ids`` values of one run (more — 422 limit_exceeded). |
| `stored_material_ids_per_request` | `int` | `Field(default=100, ge=0)` | читання й запис | Up to this many ``stored_materials.material_ids`` are passed to ``storage.v1 GET /v1/objects`` as the ``material_ids`` filter (keep it within storage's ``objects.max_filter_material_ids``); with more, or 0, the source's objects are listed and filtered here, as before WP-17. |
| `db_pool_max` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `max_lease_reclaims` | `int` | `Field(default=5, ge=1)` | читання й запис | Take-overs of an expired lease before an item is failed as poisonous (a worker keeps dying on it). Take-overs are not retry attempts (``retries.max_attempts``): the handler may have done its effect. |
| `schedule_batch` | `int` | `Field(default=20, ge=1)` | читання й запис | Due tasks turned into runs per scheduler pass. |
| `reap_batch` | `int` | `Field(default=50, ge=1)` | читання й запис | Runs checked per housekeeping pass (finish cancelled/drained runs, run timeouts). |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:167](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L167) |

```python
class ServiceLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `contract` | `ContractDefaults` | `ContractDefaults()` | читання й запис |  |
| `engine` | `EngineLimits` | `EngineLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `claims` | `ClaimLimits` | `ClaimLimits()` | читання й запис | ``Idempotency-Key`` claims of the shared store (R17): lease of a stopped instance's claim, renewal interval. |
| `pages` | `PageLimits` | `PageLimits()` | читання й запис |  |

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_orchestrator.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:176](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L176) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'orchestrator'` | читання й запис |  |
| `port` | `int` | `8109` | читання й запис |  |
| `database_url` | `str` | `'postgresql://jane@127.0.0.1:5432/jane_orchestrator'` | читання й запис | DSN of the orchestrator's own database (it never touches other services' databases). |
| `executors` | `list[ExecutorConfig]` | `Field(default_factory=list)` | читання й запис |  |
| `executors_file` | `Path \| None` | `None` | читання й запис | JSON file with a list of executors (alternative to ``JANE_ORCHESTRATOR_EXECUTORS``). |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | ``contracts/`` for request validation (default: env ``JANE_CONTRACTS_DIR`` or the checkout). |
| `service_token_ref` | `str \| None` | `None` | читання й запис | Secret reference (``env:VAR`` / ``file:/path``) of the orchestrator's own service token: the bearer token for every executor without its own ``token_ref`` (ADR-0005 §5). |
| `scheduler_enabled` | `bool` | `True` | читання й запис |  |
| `run_workers` | `bool` | `True` | читання й запис | Start worker threads inside the API process (``python -m jane_orchestrator worker`` runs them alone). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

#### Метод `Settings.executor_configs`

```python
def executor_configs(self) -> list[ExecutorConfig]: ...
```

Executors as configured (tokens not resolved).

Код: [settings.py:197](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L197).

#### Метод `Settings.all_executors`

```python
def all_executors(self) -> list[ExecutorConfig]: ...
```

Executors with ``token`` = the bearer token to send: ``token_ref``, else the deprecated plain ``token``, else ``service_token_ref``. An unresolvable reference raises (the service must not start).

Код: [settings.py:205](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L205).

## Функції

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- ``JANE_ORCHESTRATOR_LIMITS__*`` env &lt;- ``extra``.

The platform limits *file* (``JANE_ORCHESTRATOR_LIMITS_FILE``, ``PlatformLimits``) seeds the platform document in the DB instead (see :mod:`jane_orchestrator.limits`), because it has the contract shape.

Код: [settings.py:227](../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L227).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_ORCHESTRATOR_'` |  |
| `log` | — | `logging.getLogger(__name__)` |  |
