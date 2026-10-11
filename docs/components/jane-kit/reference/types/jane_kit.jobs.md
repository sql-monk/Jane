# Модуль `jane_kit.jobs`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/jobs.py](../../../../../libs/jane-kit/src/jane_kit/jobs.py). Не редагуйте вручну.

Long-running operations per WP-00 ``schemas/common/job.schema.json`` and ``common.yaml`` pathItems.

* ``202 Accepted`` + ``Job`` body + ``Location: /v1/jobs/{job_id}`` (:func:`accepted`);
* ``GET /v1/jobs/{job_id}``; ``POST /v1/jobs/{job_id}/cancel`` -> 202 (``cancelling``) or 200 if the job is already terminal (:func:`jobs_router`);
* statuses ``queued -> running -> succeeded|failed``; ``queued|running -> cancelling -> cancelled``.

:class:`InMemoryJobStore` is for a single instance and tests. For several instances use the shared stores of :mod:`jane_kit.stores` (PostgreSQL / SQLite, with leases and fencing) on the service's own database; :class:`JobRunner` works with any store. Every store follows the same write rules (:func:`decide_save`):

* a terminal job (``succeeded|failed|cancelled``) never changes again;
* any instance may request cancellation (``cancelling``) of a live job; every other write comes only from the instance that owns the job and only while its lease is live (fencing: a run that lost the lease cannot overwrite the job);
* a cancellation committed first is kept: progress of the run keeps ``cancelling``, a later success or failure of a stale snapshot ends the job ``cancelled``;
* a job whose owner stopped renewing its lease ends ``failed`` (``service_unavailable``, retryable) - or ``cancelled`` if cancellation had already been requested (:func:`orphaned`).

## Зміст

- [Клас `InMemoryJobStore`](#клас-inmemoryjobstore)
- [Клас `Job`](#клас-job)
- [Клас `JobCancelRequest`](#клас-jobcancelrequest)
- [Клас `JobCancellation`](#клас-jobcancellation)
- [Клас `JobCancelledError`](#клас-jobcancellederror)
- [Клас `JobContext`](#клас-jobcontext)
- [Клас `JobLimits`](#клас-joblimits)
- [Клас `JobProgress`](#клас-jobprogress)
- [Клас `JobRunner`](#клас-jobrunner)
- [Клас `JobStatus`](#клас-jobstatus)
- [Клас `JobStore`](#клас-jobstore)
- [Функція `accepted`](#функція-accepted)
- [Функція `decide_save`](#функція-decide_save)
- [Функція `jobs_router`](#функція-jobs_router)
- [Функція `orphaned`](#функція-orphaned)
- [Функція `resumed`](#функція-resumed)

## Класи

### Клас `InMemoryJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Код | [jobs.py:230](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L230) |

```python
class InMemoryJobStore: ...
```

Single-instance store; drops finished jobs older than ``job_retention_seconds``.

Writes follow :func:`decide_save` (this process owns every job and its lease never expires): a terminal job never changes, a committed cancellation is kept.

#### Конструктор `InMemoryJobStore.__init__`

```python
def __init__(self, limits: JobLimits | None = None) -> None: ...
```

Код: [jobs.py:237](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L237).

#### Метод `InMemoryJobStore.create`

```python
async def create(self, job: Job) -> None: ...
```

Код: [jobs.py:250](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L250).

#### Метод `InMemoryJobStore.get`

```python
async def get(self, job_id: str) -> Job | None: ...
```

Код: [jobs.py:257](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L257).

#### Метод `InMemoryJobStore.save`

```python
async def save(self, job: Job) -> None: ...
```

Код: [jobs.py:261](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L261).

#### Метод `InMemoryJobStore.page`

```python
async def page(
    self,
    kind: str,
    *,
    labels: Mapping[str, str],
    statuses: Iterable[str] | None,
    after: JobPosition | None,
    limit: int,
) -> list[Job]: ...
```

Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly after ``after`` (the same listing as :meth:`jane_kit.stores.PgJobStore.page`).

Код: [jobs.py:266](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L266).

### Клас `Job`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Успадкування | `_Model` |
| Код | [jobs.py:105](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L105) |

```python
class Job(_Model): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `job_id` | `str` | — | читання й запис |  |
| `kind` | `str` | `Field(pattern='^[a-z][a-z0-9_]{1,63}$')` | читання й запис |  |
| `status` | `JobStatus` | `JobStatus.QUEUED` | читання й запис |  |
| `created_at` | `datetime` | `Field(default_factory=_now)` | читання й запис |  |
| `updated_at` | `datetime \| None` | `None` | читання й запис |  |
| `started_at` | `datetime \| None` | `None` | читання й запис |  |
| `finished_at` | `datetime \| None` | `None` | читання й запис |  |
| `progress` | `JobProgress \| None` | `None` | читання й запис |  |
| `result` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `result_ref` | `dict[str, Any] \| None` | `None` | читання й запис | ``ContentRef`` of a large result (passed by reference, not inline). |
| `error` | `Problem \| None` | `None` | читання й запис |  |
| `cancellation` | `JobCancellation \| None` | `None` | читання й запис |  |
| `idempotency_key` | `str \| None` | `Field(default=None, max_length=255)` | читання й запис |  |
| `links` | `dict[str, str] \| None` | `None` | читання й запис |  |
| `labels` | `dict[str, str] \| None` | `None` | читання й запис |  |

#### Метод `Job.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

JSON body as in the contract (``None`` fields omitted).

Код: [jobs.py:123](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L123).

### Клас `JobCancelRequest`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.jobs` |
| Успадкування | `BaseModel` |
| Код | [jobs.py:99](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L99) |

```python
class JobCancelRequest(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `reason` | `str \| None` | `Field(default=None, max_length=1000)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='forbid')` |  |

### Клас `JobCancellation`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Успадкування | `_Model` |
| Код | [jobs.py:93](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L93) |

```python
class JobCancellation(_Model): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `requested_at` | `datetime` | — | читання й запис |  |
| `requested_by` | `str \| None` | `None` | читання й запис |  |
| `reason` | `str \| None` | `None` | читання й запис |  |

### Клас `JobCancelledError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.jobs` |
| Успадкування | `Exception` |
| Код | [jobs.py:141](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L141) |

```python
class JobCancelledError(Exception): ...
```

Raised inside a job by :meth:`JobContext.check_cancelled`.

### Клас `JobContext`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Код | [jobs.py:291](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L291) |

```python
class JobContext: ...
```

Handle given to a running job for progress reporting and cooperative cancellation.

#### Конструктор `JobContext.__init__`

```python
def __init__(self, runner: JobRunner, job_id: str) -> None: ...
```

Код: [jobs.py:294](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L294).

#### Метод `JobContext.progress`

```python
async def progress(
    self,
    completed: int | None = None,
    total: int | None = None,
    *,
    unit: str | None = None,
    message: str | None = None,
    counters: Mapping[str, int] | None = None,
) -> None: ...
```

Код: [jobs.py:298](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L298).

#### Метод `JobContext.cancelled`

```python
async def cancelled(self) -> bool: ...
```

Код: [jobs.py:325](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L325).

#### Метод `JobContext.check_cancelled`

```python
async def check_cancelled(self) -> None: ...
```

Винятки в коді методу: `JobCancelledError`.

Код: [jobs.py:329](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L329).

### Клас `JobLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Успадкування | `Limits` |
| Код | [jobs.py:128](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L128) |

```python
class JobLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_concurrent_jobs` | `int` | `Field(default=4, ge=1)` | читання й запис | Jobs executing at the same time in one instance; the rest wait in ``queued``. |
| `max_queued_jobs` | `int` | `Field(default=1000, ge=0)` | читання й запис | Beyond this, submit fails with 503 ``service_unavailable`` (backpressure, retryable). |
| `job_timeout_ms` | `int` | `Field(default=3600000, ge=1)` | читання й запис | Wall-clock limit per job; exceeded -> ``failed`` with code ``timeout``. |
| `job_retention_seconds` | `int` | `contract_field('transfer.job_retention_seconds', 86400, ge=60)` | читання й запис | Contract ``limits.transfer.job_retention_seconds``: finished jobs are kept at least this long. |
| `queue_full_retry_after_seconds` | `int` | `Field(default=1, ge=0)` | читання й запис | ``Retry-After`` sent with 503 when the job queue is full. |

### Клас `JobProgress`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Успадкування | `_Model` |
| Код | [jobs.py:84](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L84) |

```python
class JobProgress(_Model): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `completed` | `int \| None` | `Field(default=None, ge=0)` | читання й запис |  |
| `total` | `int \| None` | `Field(default=None, ge=0)` | читання й запис |  |
| `unit` | `str \| None` | `None` | читання й запис |  |
| `message` | `str \| None` | `None` | читання й запис |  |
| `counters` | `dict[str, int] \| None` | `None` | читання й запис |  |
| `updated_at` | `datetime \| None` | `None` | читання й запис |  |

### Клас `JobRunner`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.jobs` |
| Код | [jobs.py:337](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L337) |

```python
class JobRunner: ...
```

Runs job coroutines in the current event loop with limits from config.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `active` | `int` | — | читання (властивість) |  |

#### Конструктор `JobRunner.__init__`

```python
def __init__(
    self,
    store: JobStore | None = None,
    limits: JobLimits | None = None,
    jobs_path: str = '/v1/jobs',
) -> None: ...
```

Код: [jobs.py:340](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L340).

#### Метод `JobRunner.location`

```python
def location(self, job_id: str) -> str: ...
```

Код: [jobs.py:353](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L353).

#### Метод `JobRunner.submit`

```python
async def submit(
    self,
    kind: str,
    fn: JobFn,
    *,
    job_id: str | None = None,
    idempotency_key: str | None = None,
    labels: Mapping[str, str] | None = None,
) -> Job: ...
```

Винятки в коді методу: `ServiceUnavailable`.

Код: [jobs.py:356](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L356).

#### Метод `JobRunner.get`

```python
async def get(self, job_id: str) -> Job: ...
```

Винятки в коді методу: `NotFound`.

Код: [jobs.py:424](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L424).

#### Метод `JobRunner.cancel`

```python
async def cancel(
    self,
    job_id: str,
    reason: str | None = None,
    requested_by: str | None = None,
) -> Job: ...
```

Request cancellation. Terminal jobs are returned unchanged (HTTP 200 in the contract).

Код: [jobs.py:430](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L430).

#### Метод `JobRunner.wait`

```python
async def wait(self, job_id: str) -> Job: ...
```

Код: [jobs.py:442](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L442).

#### Метод `JobRunner.shutdown`

```python
async def shutdown(self) -> None: ...
```

Код: [jobs.py:448](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L448).

### Клас `JobStatus`

| Властивість | Значення |
|---|---|
| Вид | перелік |
| Модуль | `jane_kit.jobs` |
| Успадкування | `StrEnum` |
| Код | [jobs.py:64](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L64) |

```python
class JobStatus(StrEnum): ...
```

**Значення переліку**

| Назва | Значення | Опис |
|---|---|---|
| `QUEUED` | `'queued'` |  |
| `RUNNING` | `'running'` |  |
| `CANCELLING` | `'cancelling'` |  |
| `SUCCEEDED` | `'succeeded'` |  |
| `FAILED` | `'failed'` |  |
| `CANCELLED` | `'cancelled'` |  |

### Клас `JobStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_kit.jobs` |
| Успадкування | `Protocol` |
| Код | [jobs.py:145](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L145) |

```python
class JobStore(Protocol): ...
```

#### Метод `JobStore.create`

```python
async def create(self, job: Job) -> None: ...
```

Код: [jobs.py:146](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L146).

#### Метод `JobStore.get`

```python
async def get(self, job_id: str) -> Job | None: ...
```

Код: [jobs.py:147](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L147).

#### Метод `JobStore.save`

```python
async def save(self, job: Job) -> None: ...
```

Код: [jobs.py:148](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L148).

## Функції

### Функція `accepted`

```python
def accepted(
    job: Job,
    location: str | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse: ...
```

``202 Accepted`` with the Job body and ``Location`` of the job resource.

Код: [jobs.py:454](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L454).

### Функція `decide_save`

```python
def decide_save(current: Job | None, new: Job, *, mine: bool, live: bool) -> Job | None: ...
```

The document a save of ``new`` writes over ``current`` (``None``: write nothing).

``mine`` - the saving instance owns the job; ``live`` - the owner's lease has not expired.

Код: [jobs.py:151](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L151).

### Функція `jobs_router`

```python
def jobs_router(runner: JobRunner) -> APIRouter: ...
```

``GET {jobs_path}/{job_id}`` and ``POST {jobs_path}/{job_id}/cancel`` (common.yaml Job, JobCancel).

Код: [jobs.py:460](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L460).

### Функція `orphaned`

```python
def orphaned(job: Job, owner: str | None) -> Job: ...
```

Terminal state of a job whose owner stopped renewing its lease (killed, hung or partitioned).

Код: [jobs.py:189](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L189).

### Функція `resumed`

```python
def resumed(existing: Job, new: Job) -> Job: ...
```

``new`` (a resubmission of the same ``job_id``) keeping what the existing job already recorded.

Код: [jobs.py:210](../../../../../libs/jane-kit/src/jane_kit/jobs.py#L210).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `TERMINAL_STATUSES` | — | `frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED})` |  |
| `JobPosition` | — | `tuple[datetime, str]` | Cursor position in a job listing: ``(created_at, job_id)``, newest first. |
