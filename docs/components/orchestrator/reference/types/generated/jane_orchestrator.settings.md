# jane_orchestrator.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.settings.ENV_PREFIX](#jane_orchestratorsettingsenv_prefix)
- [jane_orchestrator.settings.log](#jane_orchestratorsettingslog)
- [jane_orchestrator.settings.ExecutorConfig](#jane_orchestratorsettingsexecutorconfig)
- [jane_orchestrator.settings.ExecutorConfig.model_config](#jane_orchestratorsettingsexecutorconfigmodel_config)
- [jane_orchestrator.settings.ExecutorConfig.executor](#jane_orchestratorsettingsexecutorconfigexecutor)
- [jane_orchestrator.settings.ExecutorConfig.role](#jane_orchestratorsettingsexecutorconfigrole)
- [jane_orchestrator.settings.ExecutorConfig.base_url](#jane_orchestratorsettingsexecutorconfigbase_url)
- [jane_orchestrator.settings.ExecutorConfig.capabilities](#jane_orchestratorsettingsexecutorconfigcapabilities)
- [jane_orchestrator.settings.ExecutorConfig.sync_connections](#jane_orchestratorsettingsexecutorconfigsync_connections)
- [jane_orchestrator.settings.ExecutorConfig.token_ref](#jane_orchestratorsettingsexecutorconfigtoken_ref)
- [jane_orchestrator.settings.ExecutorConfig.token](#jane_orchestratorsettingsexecutorconfigtoken)
- [jane_orchestrator.settings.ExecutorConfig.syncs_connections](#jane_orchestratorsettingsexecutorconfigsyncs_connections)
- [jane_orchestrator.settings.Queue](#jane_orchestratorsettingsqueue)
- [jane_orchestrator.settings.Queue.max_queue_depth](#jane_orchestratorsettingsqueuemax_queue_depth)
- [jane_orchestrator.settings.Queue.max_inflight_materials](#jane_orchestratorsettingsqueuemax_inflight_materials)
- [jane_orchestrator.settings.Concurrency](#jane_orchestratorsettingsconcurrency)
- [jane_orchestrator.settings.Concurrency.max_parallel_runs_per_task](#jane_orchestratorsettingsconcurrencymax_parallel_runs_per_task)
- [jane_orchestrator.settings.Concurrency.max_parallel_stage_items](#jane_orchestratorsettingsconcurrencymax_parallel_stage_items)
- [jane_orchestrator.settings.Timeouts](#jane_orchestratorsettingstimeouts)
- [jane_orchestrator.settings.Timeouts.connect_timeout_ms](#jane_orchestratorsettingstimeoutsconnect_timeout_ms)
- [jane_orchestrator.settings.Timeouts.request_timeout_ms](#jane_orchestratorsettingstimeoutsrequest_timeout_ms)
- [jane_orchestrator.settings.Timeouts.invocation_timeout_ms](#jane_orchestratorsettingstimeoutsinvocation_timeout_ms)
- [jane_orchestrator.settings.Timeouts.run_timeout_ms](#jane_orchestratorsettingstimeoutsrun_timeout_ms)
- [jane_orchestrator.settings.Transfer](#jane_orchestratorsettingstransfer)
- [jane_orchestrator.settings.Transfer.idempotency_ttl_seconds](#jane_orchestratorsettingstransferidempotency_ttl_seconds)
- [jane_orchestrator.settings.ContractDefaults](#jane_orchestratorsettingscontractdefaults)
- [jane_orchestrator.settings.ContractDefaults.queue](#jane_orchestratorsettingscontractdefaultsqueue)
- [jane_orchestrator.settings.ContractDefaults.concurrency](#jane_orchestratorsettingscontractdefaultsconcurrency)
- [jane_orchestrator.settings.ContractDefaults.timeouts](#jane_orchestratorsettingscontractdefaultstimeouts)
- [jane_orchestrator.settings.ContractDefaults.transfer](#jane_orchestratorsettingscontractdefaultstransfer)
- [jane_orchestrator.settings.ContractDefaults.retries](#jane_orchestratorsettingscontractdefaultsretries)
- [jane_orchestrator.settings.EngineLimits](#jane_orchestratorsettingsenginelimits)
- [jane_orchestrator.settings.EngineLimits.workers](#jane_orchestratorsettingsenginelimitsworkers)
- [jane_orchestrator.settings.EngineLimits.lease_ms](#jane_orchestratorsettingsenginelimitslease_ms)
- [jane_orchestrator.settings.EngineLimits.heartbeat_ms](#jane_orchestratorsettingsenginelimitsheartbeat_ms)
- [jane_orchestrator.settings.EngineLimits.poll_interval_ms](#jane_orchestratorsettingsenginelimitspoll_interval_ms)
- [jane_orchestrator.settings.EngineLimits.feed_page_size](#jane_orchestratorsettingsenginelimitsfeed_page_size)
- [jane_orchestrator.settings.EngineLimits.feed_wait_ms](#jane_orchestratorsettingsenginelimitsfeed_wait_ms)
- [jane_orchestrator.settings.EngineLimits.backpressure_recheck_ms](#jane_orchestratorsettingsenginelimitsbackpressure_recheck_ms)
- [jane_orchestrator.settings.EngineLimits.scheduler_interval_ms](#jane_orchestratorsettingsenginelimitsscheduler_interval_ms)
- [jane_orchestrator.settings.EngineLimits.sync_retry_ms](#jane_orchestratorsettingsenginelimitssync_retry_ms)
- [jane_orchestrator.settings.EngineLimits.sync_max_attempts](#jane_orchestratorsettingsenginelimitssync_max_attempts)
- [jane_orchestrator.settings.EngineLimits.executor_health_timeout_ms](#jane_orchestratorsettingsenginelimitsexecutor_health_timeout_ms)
- [jane_orchestrator.settings.EngineLimits.executor_keepalive_expiry_ms](#jane_orchestratorsettingsenginelimitsexecutor_keepalive_expiry_ms)
- [jane_orchestrator.settings.EngineLimits.executor_stale_connection_retries](#jane_orchestratorsettingsenginelimitsexecutor_stale_connection_retries)
- [jane_orchestrator.settings.EngineLimits.job_poll_interval_ms](#jane_orchestratorsettingsenginelimitsjob_poll_interval_ms)
- [jane_orchestrator.settings.EngineLimits.idempotency_in_progress_poll_ms](#jane_orchestratorsettingsenginelimitsidempotency_in_progress_poll_ms)
- [jane_orchestrator.settings.EngineLimits.idempotency_in_progress_max_wait_ms](#jane_orchestratorsettingsenginelimitsidempotency_in_progress_max_wait_ms)
- [jane_orchestrator.settings.EngineLimits.idempotency_in_progress_retry_ms](#jane_orchestratorsettingsenginelimitsidempotency_in_progress_retry_ms)
- [jane_orchestrator.settings.EngineLimits.problem_samples](#jane_orchestratorsettingsenginelimitsproblem_samples)
- [jane_orchestrator.settings.EngineLimits.trace_outputs_max](#jane_orchestratorsettingsenginelimitstrace_outputs_max)
- [jane_orchestrator.settings.EngineLimits.attempt_history_max](#jane_orchestratorsettingsenginelimitsattempt_history_max)
- [jane_orchestrator.settings.EngineLimits.stored_selection_max_ids](#jane_orchestratorsettingsenginelimitsstored_selection_max_ids)
- [jane_orchestrator.settings.EngineLimits.stored_material_ids_per_request](#jane_orchestratorsettingsenginelimitsstored_material_ids_per_request)
- [jane_orchestrator.settings.EngineLimits.db_pool_max](#jane_orchestratorsettingsenginelimitsdb_pool_max)
- [jane_orchestrator.settings.EngineLimits.max_lease_reclaims](#jane_orchestratorsettingsenginelimitsmax_lease_reclaims)
- [jane_orchestrator.settings.EngineLimits.schedule_batch](#jane_orchestratorsettingsenginelimitsschedule_batch)
- [jane_orchestrator.settings.EngineLimits.reap_batch](#jane_orchestratorsettingsenginelimitsreap_batch)
- [jane_orchestrator.settings.ServiceLimits](#jane_orchestratorsettingsservicelimits)
- [jane_orchestrator.settings.ServiceLimits.contract](#jane_orchestratorsettingsservicelimitscontract)
- [jane_orchestrator.settings.ServiceLimits.engine](#jane_orchestratorsettingsservicelimitsengine)
- [jane_orchestrator.settings.ServiceLimits.idempotency](#jane_orchestratorsettingsservicelimitsidempotency)
- [jane_orchestrator.settings.ServiceLimits.claims](#jane_orchestratorsettingsservicelimitsclaims)
- [jane_orchestrator.settings.ServiceLimits.pages](#jane_orchestratorsettingsservicelimitspages)
- [jane_orchestrator.settings.Settings](#jane_orchestratorsettingssettings)
- [jane_orchestrator.settings.Settings.model_config](#jane_orchestratorsettingssettingsmodel_config)
- [jane_orchestrator.settings.Settings.service_name](#jane_orchestratorsettingssettingsservice_name)
- [jane_orchestrator.settings.Settings.port](#jane_orchestratorsettingssettingsport)
- [jane_orchestrator.settings.Settings.database_url](#jane_orchestratorsettingssettingsdatabase_url)
- [jane_orchestrator.settings.Settings.executors](#jane_orchestratorsettingssettingsexecutors)
- [jane_orchestrator.settings.Settings.executors_file](#jane_orchestratorsettingssettingsexecutors_file)
- [jane_orchestrator.settings.Settings.contracts_dir](#jane_orchestratorsettingssettingscontracts_dir)
- [jane_orchestrator.settings.Settings.service_token_ref](#jane_orchestratorsettingssettingsservice_token_ref)
- [jane_orchestrator.settings.Settings.scheduler_enabled](#jane_orchestratorsettingssettingsscheduler_enabled)
- [jane_orchestrator.settings.Settings.run_workers](#jane_orchestratorsettingssettingsrun_workers)
- [jane_orchestrator.settings.Settings.executor_configs](#jane_orchestratorsettingssettingsexecutor_configs)
- [jane_orchestrator.settings.Settings.all_executors](#jane_orchestratorsettingssettingsall_executors)
- [jane_orchestrator.settings.resolve_service_limits](#jane_orchestratorsettingsresolve_service_limits)

## jane_orchestrator.settings.ENV_PREFIX

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:31](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L31).

```python
ENV_PREFIX = 'JANE_ORCHESTRATOR_'
```

## jane_orchestrator.settings.log

**Змінна.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:32](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L32).

```python
log = logging.getLogger(__name__)
```

## jane_orchestrator.settings.ExecutorConfig

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:35](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L35).

```python
class ExecutorConfig(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigmodel_config) | Поле | ні |
| [executor](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigexecutor) | Поле | ні |
| [role](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigrole) | Поле | ні |
| [base_url](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigbase_url) | Поле | ні |
| [capabilities](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigcapabilities) | Поле | ні |
| [sync_connections](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigsync_connections) | Поле | ні |
| [token_ref](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigtoken_ref) | Поле | ні |
| [token](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigtoken) | Поле | ні |
| [syncs_connections](jane_orchestrator.settings.md#jane_orchestratorsettingsexecutorconfigsyncs_connections) | Властивість | ні |

### Опис із вихідного коду

```text
A service the orchestrator calls (``orchestrator.v1`` ``Executor``).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_executors.py:94](../../../../../../services/orchestrator/tests/test_executors.py#L94).

```python
cfg = ExecutorConfig(executor="handler", role="handler", base_url=ex.url)
```

## jane_orchestrator.settings.ExecutorConfig.model_config

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:38](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L38).

```python
model_config = ConfigDict(extra='forbid')
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ExecutorConfig.executor

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:40](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L40).

```python
executor: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ExecutorConfig.role

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:41](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L41).

```python
role: Literal['collector', 'handler', 'storage_read', 'registry', 'llm', 'assistant']
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ExecutorConfig.base_url

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L42).

```python
base_url: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ExecutorConfig.capabilities

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:43](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L43).

```python
capabilities: dict[str, Any] = Field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
``collector: web`` for collectors; ``handler_kinds: [...]`` and ``packages: ["jane.storage-*"]``
    (globs of package ids routed to this executor) for handlers; ``default: true`` marks the fallback
    handler executor.
```

## jane_orchestrator.settings.ExecutorConfig.sync_connections

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:47](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L47).

```python
sync_connections: bool | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Push the connections registry to this executor (``PUT /v1/connections/{id}``). Default: true for
    collectors, handlers and llm.
```

## jane_orchestrator.settings.ExecutorConfig.token_ref

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:50](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L50).

```python
token_ref: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Secret reference (``env:VAR`` / ``file:/path``, ADR-0006) of the bearer token for this executor;
    without it the orchestrator's own ``service_token_ref`` is used (ADR-0005 §5).
```

## jane_orchestrator.settings.ExecutorConfig.token

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:53](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L53).

```python
token: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Bearer token in plain text - deprecated (logged as a warning at start), use ``token_ref``. After
    :meth:`Settings.all_executors` it holds the resolved token (``SecretStr``: never in reprs, logs or the API).
```

## jane_orchestrator.settings.ExecutorConfig.syncs_connections

**Властивість.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:64](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L64).

```python
def syncs_connections(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``sync_connections`` if set; otherwise collectors, handlers and llm, except an executor whose
``capabilities.connections`` is ``false`` (handler.v1: ``/v1/connections*`` are optional for it).
```

## jane_orchestrator.settings.Queue

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:74](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L74).

```python
class Queue(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_queue_depth](jane_orchestrator.settings.md#jane_orchestratorsettingsqueuemax_queue_depth) | Поле | ні |
| [max_inflight_materials](jane_orchestrator.settings.md#jane_orchestratorsettingsqueuemax_inflight_materials) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_orchestrator.settings.Queue.max_queue_depth

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:75](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L75).

```python
max_queue_depth: int = contract_field('queue.max_queue_depth', 10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'queue.max_queue_depth'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Queue.max_inflight_materials

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:76](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L76).

```python
max_inflight_materials: int = contract_field('queue.max_inflight_materials', 100, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'queue.max_inflight_materials'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Concurrency

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:79](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L79).

```python
class Concurrency(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_parallel_runs_per_task](jane_orchestrator.settings.md#jane_orchestratorsettingsconcurrencymax_parallel_runs_per_task) | Поле | ні |
| [max_parallel_stage_items](jane_orchestrator.settings.md#jane_orchestratorsettingsconcurrencymax_parallel_stage_items) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_orchestrator.settings.Concurrency.max_parallel_runs_per_task

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:80](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L80).

```python
max_parallel_runs_per_task: int = contract_field('concurrency.max_parallel_runs_per_task', 1, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'concurrency.max_parallel_runs_per_task'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Concurrency.max_parallel_stage_items

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:81](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L81).

```python
max_parallel_stage_items: int = contract_field('concurrency.max_parallel_stage_items', 4, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'concurrency.max_parallel_stage_items'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Timeouts

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:84](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L84).

```python
class Timeouts(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_orchestrator.settings.md#jane_orchestratorsettingstimeoutsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_orchestrator.settings.md#jane_orchestratorsettingstimeoutsrequest_timeout_ms) | Поле | ні |
| [invocation_timeout_ms](jane_orchestrator.settings.md#jane_orchestratorsettingstimeoutsinvocation_timeout_ms) | Поле | ні |
| [run_timeout_ms](jane_orchestrator.settings.md#jane_orchestratorsettingstimeoutsrun_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_orchestrator.settings.Timeouts.connect_timeout_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:85](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L85).

```python
connect_timeout_ms: int = contract_field('timeouts.connect_timeout_ms', 5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.connect_timeout_ms'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Timeouts.request_timeout_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:86](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L86).

```python
request_timeout_ms: int = contract_field('timeouts.request_timeout_ms', 30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.request_timeout_ms'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Timeouts.invocation_timeout_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:87](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L87).

```python
invocation_timeout_ms: int = contract_field('timeouts.invocation_timeout_ms', 60000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.invocation_timeout_ms'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Timeouts.run_timeout_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:88](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L88).

```python
run_timeout_ms: int = contract_field('timeouts.run_timeout_ms', 21600000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.run_timeout_ms'",
  "ge": "1"
}
```

## jane_orchestrator.settings.Transfer

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:91](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L91).

```python
class Transfer(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [idempotency_ttl_seconds](jane_orchestrator.settings.md#jane_orchestratorsettingstransferidempotency_ttl_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_orchestrator.settings.Transfer.idempotency_ttl_seconds

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:92](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L92).

```python
idempotency_ttl_seconds: int = contract_field('transfer.idempotency_ttl_seconds', 86400, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.idempotency_ttl_seconds'",
  "ge": "60"
}
```

## jane_orchestrator.settings.ContractDefaults

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:95](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L95).

```python
class ContractDefaults(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [queue](jane_orchestrator.settings.md#jane_orchestratorsettingscontractdefaultsqueue) | Поле | ні |
| [concurrency](jane_orchestrator.settings.md#jane_orchestratorsettingscontractdefaultsconcurrency) | Поле | ні |
| [timeouts](jane_orchestrator.settings.md#jane_orchestratorsettingscontractdefaultstimeouts) | Поле | ні |
| [transfer](jane_orchestrator.settings.md#jane_orchestratorsettingscontractdefaultstransfer) | Поле | ні |
| [retries](jane_orchestrator.settings.md#jane_orchestratorsettingscontractdefaultsretries) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Fallback values of contract limits the orchestrator consumes (level ``platform``).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:243](../../../../../../services/orchestrator/tests/test_logic.py#L243).

```python
fallback = ContractDefaults().model_dump(mode="json")
```

## jane_orchestrator.settings.ContractDefaults.queue

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:98](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L98).

```python
queue: Queue = Queue()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ContractDefaults.concurrency

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:99](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L99).

```python
concurrency: Concurrency = Concurrency()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ContractDefaults.timeouts

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:100](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L100).

```python
timeouts: Timeouts = Timeouts()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ContractDefaults.transfer

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:101](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L101).

```python
transfer: Transfer = Transfer()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ContractDefaults.retries

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:102](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L102).

```python
retries: RetryPolicy = contract_field('retries', RetryPolicy(max_attempts=3, initial_backoff_ms=1000, max_backoff_ms=60000))
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'retries'"
}
```

## jane_orchestrator.settings.EngineLimits

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:108](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L108).

```python
class EngineLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [workers](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsworkers) | Поле | ні |
| [lease_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitslease_ms) | Поле | ні |
| [heartbeat_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsheartbeat_ms) | Поле | ні |
| [poll_interval_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitspoll_interval_ms) | Поле | ні |
| [feed_page_size](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsfeed_page_size) | Поле | ні |
| [feed_wait_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsfeed_wait_ms) | Поле | ні |
| [backpressure_recheck_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsbackpressure_recheck_ms) | Поле | ні |
| [scheduler_interval_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsscheduler_interval_ms) | Поле | ні |
| [sync_retry_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitssync_retry_ms) | Поле | ні |
| [sync_max_attempts](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitssync_max_attempts) | Поле | ні |
| [executor_health_timeout_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsexecutor_health_timeout_ms) | Поле | ні |
| [executor_keepalive_expiry_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsexecutor_keepalive_expiry_ms) | Поле | ні |
| [executor_stale_connection_retries](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsexecutor_stale_connection_retries) | Поле | ні |
| [job_poll_interval_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsjob_poll_interval_ms) | Поле | ні |
| [idempotency_in_progress_poll_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsidempotency_in_progress_poll_ms) | Поле | ні |
| [idempotency_in_progress_max_wait_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsidempotency_in_progress_max_wait_ms) | Поле | ні |
| [idempotency_in_progress_retry_ms](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsidempotency_in_progress_retry_ms) | Поле | ні |
| [problem_samples](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsproblem_samples) | Поле | ні |
| [trace_outputs_max](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitstrace_outputs_max) | Поле | ні |
| [attempt_history_max](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsattempt_history_max) | Поле | ні |
| [stored_selection_max_ids](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsstored_selection_max_ids) | Поле | ні |
| [stored_material_ids_per_request](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsstored_material_ids_per_request) | Поле | ні |
| [db_pool_max](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsdb_pool_max) | Поле | ні |
| [max_lease_reclaims](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsmax_lease_reclaims) | Поле | ні |
| [schedule_batch](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsschedule_batch) | Поле | ні |
| [reap_batch](jane_orchestrator.settings.md#jane_orchestratorsettingsenginelimitsreap_batch) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Internal knobs of the queue engine (not part of ``limits.schema.json``).
```

## jane_orchestrator.settings.EngineLimits.workers

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:111](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L111).

```python
workers: int = Field(default=2, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Worker threads per process (0 — API only).
```

## jane_orchestrator.settings.EngineLimits.lease_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:113](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L113).

```python
lease_ms: int = Field(default=30000, ge=100)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "100"
}
```

### Опис із вихідного коду

```text
Lease of a claimed item / collection feed; extended by heartbeats while a call runs.
```

## jane_orchestrator.settings.EngineLimits.heartbeat_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:115](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L115).

```python
heartbeat_ms: int = Field(default=10000, ge=50)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "50"
}
```

## jane_orchestrator.settings.EngineLimits.poll_interval_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:116](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L116).

```python
poll_interval_ms: int = Field(default=500, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
Idle sleep of a worker when there is nothing to claim.
```

## jane_orchestrator.settings.EngineLimits.feed_page_size

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:118](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L118).

```python
feed_page_size: int = Field(default=100, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Materials requested from a collector per page (bounded further by queue limits).
```

## jane_orchestrator.settings.EngineLimits.feed_wait_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:120](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L120).

```python
feed_wait_ms: int = Field(default=1000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Long-poll ``wait_ms`` for collector material pages.
```

## jane_orchestrator.settings.EngineLimits.backpressure_recheck_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:122](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L122).

```python
backpressure_recheck_ms: int = Field(default=500, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "10"
}
```

## jane_orchestrator.settings.EngineLimits.scheduler_interval_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:123](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L123).

```python
scheduler_interval_ms: int = Field(default=1000, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "10"
}
```

## jane_orchestrator.settings.EngineLimits.sync_retry_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:124](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L124).

```python
sync_retry_ms: int = Field(default=5000, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
Delay before retrying a failed connection sync.
```

## jane_orchestrator.settings.EngineLimits.sync_max_attempts

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:126](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L126).

```python
sync_max_attempts: int = Field(default=5, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "1"
}
```

## jane_orchestrator.settings.EngineLimits.executor_health_timeout_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:127](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L127).

```python
executor_health_timeout_ms: int = Field(default=2000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000",
  "ge": "1"
}
```

## jane_orchestrator.settings.EngineLimits.executor_keepalive_expiry_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:128](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L128).

```python
executor_keepalive_expiry_ms: int = Field(default=4000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Idle time after which a pooled connection to an executor is dropped. Keep it below the executors'
    server keep-alive (uvicorn ``timeout_keep_alive``, 5 s for every Jane service): with equal values a
    request sent at the moment the server closes the idle connection fails with ``RemoteProtocolError``.
```

## jane_orchestrator.settings.EngineLimits.executor_stale_connection_retries

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:132](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L132).

```python
executor_stale_connection_retries: int = Field(default=1, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Immediate re-sends, on a new connection, of a request that is safe to repeat (GET/HEAD/OPTIONS/PUT/
    DELETE or with ``Idempotency-Key``) after the executor dropped the connection without a response. They do
    not spend ``retries.max_attempts`` of an item; 0 hands such an error to the item retry policy.
```

## jane_orchestrator.settings.EngineLimits.job_poll_interval_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:136](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L136).

```python
job_poll_interval_ms: int = Field(default=500, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
Polling interval for an executor's 202 job (async handler invocation).
```

## jane_orchestrator.settings.EngineLimits.idempotency_in_progress_poll_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:138](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L138).

```python
idempotency_in_progress_poll_ms: int = Field(default=500, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
Delay between replays while an executor is still processing the same delivery key.
```

## jane_orchestrator.settings.EngineLimits.idempotency_in_progress_max_wait_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:140](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L140).

```python
idempotency_in_progress_max_wait_ms: int = Field(default=120000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "120000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Maximum time one worker waits for an already running invocation before parking the item.
```

## jane_orchestrator.settings.EngineLimits.idempotency_in_progress_retry_ms

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:142](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L142).

```python
idempotency_in_progress_retry_ms: int = Field(default=5000, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
Delay before another worker checks a parked delivery key; run_timeout_ms bounds the run.
```

## jane_orchestrator.settings.EngineLimits.problem_samples

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:144](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L144).

```python
problem_samples: int = Field(default=10, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Samples kept per problem group.
```

## jane_orchestrator.settings.EngineLimits.trace_outputs_max

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:146](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L146).

```python
trace_outputs_max: int = Field(default=100, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Output references (entity keys, stored object ids) recorded per item for the material trace.
```

## jane_orchestrator.settings.EngineLimits.attempt_history_max

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:148](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L148).

```python
attempt_history_max: int = Field(default=20, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Diagnostic events (claims, scheduled retries, outcome) kept per item for ``attempt_history`` in run items
    and the material trace; the first events are kept (0 — none).
```

## jane_orchestrator.settings.EngineLimits.stored_selection_max_ids

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:151](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L151).

```python
stored_selection_max_ids: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Most ``stored_materials.object_ids`` / ``observation_ids`` values of one run (more — 422 limit_exceeded).
```

## jane_orchestrator.settings.EngineLimits.stored_material_ids_per_request

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:153](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L153).

```python
stored_material_ids_per_request: int = Field(default=100, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Up to this many ``stored_materials.material_ids`` are passed to ``storage.v1 GET /v1/objects`` as the
    ``material_ids`` filter (keep it within storage's ``objects.max_filter_material_ids``); with more, or 0, the
    source's objects are listed and filtered here, as before WP-17.
```

## jane_orchestrator.settings.EngineLimits.db_pool_max

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:157](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L157).

```python
db_pool_max: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

## jane_orchestrator.settings.EngineLimits.max_lease_reclaims

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:158](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L158).

```python
max_lease_reclaims: int = Field(default=5, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Take-overs of an expired lease before an item is failed as poisonous (a worker keeps dying on it).
    Take-overs are not retry attempts (``retries.max_attempts``): the handler may have done its effect.
```

## jane_orchestrator.settings.EngineLimits.schedule_batch

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:161](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L161).

```python
schedule_batch: int = Field(default=20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Due tasks turned into runs per scheduler pass.
```

## jane_orchestrator.settings.EngineLimits.reap_batch

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:163](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L163).

```python
reap_batch: int = Field(default=50, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Runs checked per housekeeping pass (finish cancelled/drained runs, run timeouts).
```

## jane_orchestrator.settings.ServiceLimits

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:167](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L167).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [contract](jane_orchestrator.settings.md#jane_orchestratorsettingsservicelimitscontract) | Поле | ні |
| [engine](jane_orchestrator.settings.md#jane_orchestratorsettingsservicelimitsengine) | Поле | ні |
| [idempotency](jane_orchestrator.settings.md#jane_orchestratorsettingsservicelimitsidempotency) | Поле | ні |
| [claims](jane_orchestrator.settings.md#jane_orchestratorsettingsservicelimitsclaims) | Поле | ні |
| [pages](jane_orchestrator.settings.md#jane_orchestratorsettingsservicelimitspages) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_executors.py:99](../../../../../../services/orchestrator/tests/test_executors.py#L99).

```python
limits = ServiceLimits()
```

## jane_orchestrator.settings.ServiceLimits.contract

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:168](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L168).

```python
contract: ContractDefaults = ContractDefaults()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ServiceLimits.engine

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:169](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L169).

```python
engine: EngineLimits = EngineLimits()
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_executors.py:102](../../../../../../services/orchestrator/tests/test_executors.py#L102).

```python
assert limits.engine.executor_keepalive_expiry_ms == 4_000
```

Контекст і передумови: [services/orchestrator/tests/test_executors.py:104](../../../../../../services/orchestrator/tests/test_executors.py#L104).

```python
assert limits.engine.executor_stale_connection_retries == 1
```

## jane_orchestrator.settings.ServiceLimits.idempotency

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:170](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L170).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.ServiceLimits.claims

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:171](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L171).

```python
claims: ClaimLimits = ClaimLimits()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``Idempotency-Key`` claims of the shared store (R17): lease of a stopped instance's claim, renewal interval.
```

## jane_orchestrator.settings.ServiceLimits.pages

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:173](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L173).

```python
pages: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.Settings

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:176](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L176).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsservice_name) | Поле | ні |
| [port](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsport) | Поле | ні |
| [database_url](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsdatabase_url) | Поле | ні |
| [executors](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsexecutors) | Поле | ні |
| [executors_file](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsexecutors_file) | Поле | ні |
| [contracts_dir](jane_orchestrator.settings.md#jane_orchestratorsettingssettingscontracts_dir) | Поле | ні |
| [service_token_ref](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsservice_token_ref) | Поле | ні |
| [scheduler_enabled](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsscheduler_enabled) | Поле | ні |
| [run_workers](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsrun_workers) | Поле | ні |
| [executor_configs](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsexecutor_configs) | Метод | ні |
| [all_executors](jane_orchestrator.settings.md#jane_orchestratorsettingssettingsall_executors) | Метод | ні |
| [instance_id](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsinstance_id) | Поле | так |
| [host](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshost) | Поле | так |
| [log_level](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_level) | Поле | так |
| [log_format](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_format) | Поле | так |
| [metrics_enabled](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsmetrics_enabled) | Поле | так |
| [health_check_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshealth_check_timeout_ms) | Поле | так |
| [limits_file](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslimits_file) | Поле | так |
| [platform_layers](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsplatform_layers) | Метод | так |
| [with_overrides](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingswith_overrides) | Метод | так |
| [auth_mode](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_mode) | Поле | так |
| [auth_none_allow_remote](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_none_allow_remote) | Поле | так |
| [api_keys](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys) | Поле | так |
| [api_keys_file](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys_file) | Поле | так |
| [jwt_jwks_url](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_url) | Поле | так |
| [jwt_issuer](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_issuer) | Поле | так |
| [jwt_audience](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_audience) | Поле | так |
| [jwt_algorithms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_algorithms) | Поле | так |
| [jwt_scope_claim](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_scope_claim) | Поле | так |
| [jwt_leeway_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_leeway_seconds) | Поле | так |
| [jwt_jwks_cache_ttl_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds) | Поле | так |
| [jwt_jwks_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_timeout_ms) | Поле | так |
| [jwt_jwks_refresh_cooldown_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds) | Поле | так |
| [jwt_jwks_max_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_max_bytes) | Поле | так |
| [auth_max_token_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_max_token_bytes) | Поле | так |
| [metrics_public](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsmetrics_public) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/conftest.py:78](../../../../../../services/orchestrator/tests/conftest.py#L78).

```python
settings = Settings(
            database_url=db_dsn,
            executors=[ExecutorConfig.model_validate(e) for e in neighbours.executors()],
            contracts_dir=CONTRACTS,
            log_format="console",
            log_level="WARNING",
            **overrides,
        )
```

Контекст і передумови: [services/orchestrator/tests/test_auth.py:26](../../../../../../services/orchestrator/tests/test_auth.py#L26).

```python
settings = Settings(
        service_token_ref="env:JANE_TEST_ORCH_TOKEN",
        executors=[
            ExecutorConfig.model_validate(executor("runtime")),
            ExecutorConfig.model_validate(executor("storage", token_ref=f"file:{secret}")),
            ExecutorConfig.model_validate(executor("legacy", token="plain-token")),
        ],
    )
```

## jane_orchestrator.settings.Settings.model_config

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:177](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L177).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.Settings.service_name

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:179](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L179).

```python
service_name: str = 'orchestrator'
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.Settings.port

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:180](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L180).

```python
port: int = 8109
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.Settings.database_url

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:181](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L181).

```python
database_url: str = 'postgresql://jane@127.0.0.1:5432/jane_orchestrator'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
DSN of the orchestrator's own database (it never touches other services' databases).
```

## jane_orchestrator.settings.Settings.executors

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:183](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L183).

```python
executors: list[ExecutorConfig] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_orchestrator.settings.Settings.executors_file

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:184](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L184).

```python
executors_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
JSON file with a list of executors (alternative to ``JANE_ORCHESTRATOR_EXECUTORS``).
```

## jane_orchestrator.settings.Settings.contracts_dir

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:186](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L186).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``contracts/`` for request validation (default: env ``JANE_CONTRACTS_DIR`` or the checkout).
```

## jane_orchestrator.settings.Settings.service_token_ref

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:190](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L190).

```python
service_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Secret reference (``env:VAR`` / ``file:/path``) of the orchestrator's own service token: the bearer
    token for every executor without its own ``token_ref`` (ADR-0005 §5).
```

## jane_orchestrator.settings.Settings.scheduler_enabled

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:193](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L193).

```python
scheduler_enabled: bool = True
```

Доступ: читання — так; запис — так.

## jane_orchestrator.settings.Settings.run_workers

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:194](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L194).

```python
run_workers: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Start worker threads inside the API process (``python -m jane_orchestrator worker`` runs them alone).
```

## jane_orchestrator.settings.Settings.executor_configs

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:197](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L197).

```python
def executor_configs(self) -> list[ExecutorConfig]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[ExecutorConfig]`.

### Опис із вихідного коду

```text
Executors as configured (tokens not resolved).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_auth.py:40](../../../../../../services/orchestrator/tests/test_auth.py#L40).

```python
assert all(e.token is None for e in settings.executor_configs() if e.executor != "legacy")
```

## jane_orchestrator.settings.Settings.all_executors

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:205](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L205).

```python
def all_executors(self) -> list[ExecutorConfig]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[ExecutorConfig]`.

### Опис із вихідного коду

```text
Executors with ``token`` = the bearer token to send: ``token_ref``, else the deprecated plain
``token``, else ``service_token_ref``. An unresolvable reference raises (the service must not start).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_auth.py:35](../../../../../../services/orchestrator/tests/test_auth.py#L35).

```python
resolved = settings.all_executors()
```

Контекст і передумови: [services/orchestrator/tests/test_auth.py:41](../../../../../../services/orchestrator/tests/test_auth.py#L41).

```python
clients = Executors(settings.all_executors(), connect_timeout_ms=1000, request_timeout_ms=1000)
```

## jane_orchestrator.settings.resolve_service_limits

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/settings.py:227](../../../../../../services/orchestrator/src/jane_orchestrator/settings.py#L227).

```python
def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `extra` | `LimitLayer` | `—` | var-positional |

Результат: `ResolvedLimits[ServiceLimits]`.

### Опис із вихідного коду

```text
Defaults <- ``JANE_ORCHESTRATOR_LIMITS__*`` env <- ``extra``.

The platform limits *file* (``JANE_ORCHESTRATOR_LIMITS_FILE``, ``PlatformLimits``) seeds the platform
document in the DB instead (see :mod:`jane_orchestrator.limits`), because it has the contract shape.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_executors.py:110](../../../../../../services/orchestrator/tests/test_executors.py#L110).

```python
engine = resolve_service_limits(Settings()).limits.engine
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:276](../../../../../../services/orchestrator/tests/test_logic.py#L276).

```python
resolved = resolve_service_limits(Settings())
```
