# jane_kit.jobs

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.jobs.JobStatus](#jane_kitjobsjobstatus)
- [jane_kit.jobs.JobStatus.QUEUED](#jane_kitjobsjobstatusqueued)
- [jane_kit.jobs.JobStatus.RUNNING](#jane_kitjobsjobstatusrunning)
- [jane_kit.jobs.JobStatus.CANCELLING](#jane_kitjobsjobstatuscancelling)
- [jane_kit.jobs.JobStatus.SUCCEEDED](#jane_kitjobsjobstatussucceeded)
- [jane_kit.jobs.JobStatus.FAILED](#jane_kitjobsjobstatusfailed)
- [jane_kit.jobs.JobStatus.CANCELLED](#jane_kitjobsjobstatuscancelled)
- [jane_kit.jobs.TERMINAL_STATUSES](#jane_kitjobsterminal_statuses)
- [jane_kit.jobs.JobProgress](#jane_kitjobsjobprogress)
- [jane_kit.jobs.JobProgress.completed](#jane_kitjobsjobprogresscompleted)
- [jane_kit.jobs.JobProgress.total](#jane_kitjobsjobprogresstotal)
- [jane_kit.jobs.JobProgress.unit](#jane_kitjobsjobprogressunit)
- [jane_kit.jobs.JobProgress.message](#jane_kitjobsjobprogressmessage)
- [jane_kit.jobs.JobProgress.counters](#jane_kitjobsjobprogresscounters)
- [jane_kit.jobs.JobProgress.updated_at](#jane_kitjobsjobprogressupdated_at)
- [jane_kit.jobs.JobCancellation](#jane_kitjobsjobcancellation)
- [jane_kit.jobs.JobCancellation.requested_at](#jane_kitjobsjobcancellationrequested_at)
- [jane_kit.jobs.JobCancellation.requested_by](#jane_kitjobsjobcancellationrequested_by)
- [jane_kit.jobs.JobCancellation.reason](#jane_kitjobsjobcancellationreason)
- [jane_kit.jobs.JobCancelRequest](#jane_kitjobsjobcancelrequest)
- [jane_kit.jobs.JobCancelRequest.model_config](#jane_kitjobsjobcancelrequestmodel_config)
- [jane_kit.jobs.JobCancelRequest.reason](#jane_kitjobsjobcancelrequestreason)
- [jane_kit.jobs.Job](#jane_kitjobsjob)
- [jane_kit.jobs.Job.job_id](#jane_kitjobsjobjob_id)
- [jane_kit.jobs.Job.kind](#jane_kitjobsjobkind)
- [jane_kit.jobs.Job.status](#jane_kitjobsjobstatus)
- [jane_kit.jobs.Job.created_at](#jane_kitjobsjobcreated_at)
- [jane_kit.jobs.Job.updated_at](#jane_kitjobsjobupdated_at)
- [jane_kit.jobs.Job.started_at](#jane_kitjobsjobstarted_at)
- [jane_kit.jobs.Job.finished_at](#jane_kitjobsjobfinished_at)
- [jane_kit.jobs.Job.progress](#jane_kitjobsjobprogress)
- [jane_kit.jobs.Job.result](#jane_kitjobsjobresult)
- [jane_kit.jobs.Job.result_ref](#jane_kitjobsjobresult_ref)
- [jane_kit.jobs.Job.error](#jane_kitjobsjoberror)
- [jane_kit.jobs.Job.cancellation](#jane_kitjobsjobcancellation)
- [jane_kit.jobs.Job.idempotency_key](#jane_kitjobsjobidempotency_key)
- [jane_kit.jobs.Job.links](#jane_kitjobsjoblinks)
- [jane_kit.jobs.Job.labels](#jane_kitjobsjoblabels)
- [jane_kit.jobs.Job.wire](#jane_kitjobsjobwire)
- [jane_kit.jobs.JobLimits](#jane_kitjobsjoblimits)
- [jane_kit.jobs.JobLimits.max_concurrent_jobs](#jane_kitjobsjoblimitsmax_concurrent_jobs)
- [jane_kit.jobs.JobLimits.max_queued_jobs](#jane_kitjobsjoblimitsmax_queued_jobs)
- [jane_kit.jobs.JobLimits.job_timeout_ms](#jane_kitjobsjoblimitsjob_timeout_ms)
- [jane_kit.jobs.JobLimits.job_retention_seconds](#jane_kitjobsjoblimitsjob_retention_seconds)
- [jane_kit.jobs.JobLimits.queue_full_retry_after_seconds](#jane_kitjobsjoblimitsqueue_full_retry_after_seconds)
- [jane_kit.jobs.JobCancelledError](#jane_kitjobsjobcancellederror)
- [jane_kit.jobs.JobStore](#jane_kitjobsjobstore)
- [jane_kit.jobs.JobStore.create](#jane_kitjobsjobstorecreate)
- [jane_kit.jobs.JobStore.get](#jane_kitjobsjobstoreget)
- [jane_kit.jobs.JobStore.save](#jane_kitjobsjobstoresave)
- [jane_kit.jobs.decide_save](#jane_kitjobsdecide_save)
- [jane_kit.jobs.orphaned](#jane_kitjobsorphaned)
- [jane_kit.jobs.resumed](#jane_kitjobsresumed)
- [jane_kit.jobs.JobPosition](#jane_kitjobsjobposition)
- [jane_kit.jobs.InMemoryJobStore](#jane_kitjobsinmemoryjobstore)
- [jane_kit.jobs.InMemoryJobStore.__init__](#jane_kitjobsinmemoryjobstore__init__)
- [jane_kit.jobs.InMemoryJobStore.limits](#jane_kitjobsinmemoryjobstorelimits)
- [jane_kit.jobs.InMemoryJobStore.create](#jane_kitjobsinmemoryjobstorecreate)
- [jane_kit.jobs.InMemoryJobStore.get](#jane_kitjobsinmemoryjobstoreget)
- [jane_kit.jobs.InMemoryJobStore.save](#jane_kitjobsinmemoryjobstoresave)
- [jane_kit.jobs.InMemoryJobStore.page](#jane_kitjobsinmemoryjobstorepage)
- [jane_kit.jobs.JobContext](#jane_kitjobsjobcontext)
- [jane_kit.jobs.JobContext.__init__](#jane_kitjobsjobcontext__init__)
- [jane_kit.jobs.JobContext.job_id](#jane_kitjobsjobcontextjob_id)
- [jane_kit.jobs.JobContext.progress](#jane_kitjobsjobcontextprogress)
- [jane_kit.jobs.JobContext.cancelled](#jane_kitjobsjobcontextcancelled)
- [jane_kit.jobs.JobContext.check_cancelled](#jane_kitjobsjobcontextcheck_cancelled)
- [jane_kit.jobs.JobRunner](#jane_kitjobsjobrunner)
- [jane_kit.jobs.JobRunner.__init__](#jane_kitjobsjobrunner__init__)
- [jane_kit.jobs.JobRunner.limits](#jane_kitjobsjobrunnerlimits)
- [jane_kit.jobs.JobRunner.store](#jane_kitjobsjobrunnerstore)
- [jane_kit.jobs.JobRunner.jobs_path](#jane_kitjobsjobrunnerjobs_path)
- [jane_kit.jobs.JobRunner.active](#jane_kitjobsjobrunneractive)
- [jane_kit.jobs.JobRunner.location](#jane_kitjobsjobrunnerlocation)
- [jane_kit.jobs.JobRunner.submit](#jane_kitjobsjobrunnersubmit)
- [jane_kit.jobs.JobRunner.get](#jane_kitjobsjobrunnerget)
- [jane_kit.jobs.JobRunner.cancel](#jane_kitjobsjobrunnercancel)
- [jane_kit.jobs.JobRunner.wait](#jane_kitjobsjobrunnerwait)
- [jane_kit.jobs.JobRunner.shutdown](#jane_kitjobsjobrunnershutdown)
- [jane_kit.jobs.accepted](#jane_kitjobsaccepted)
- [jane_kit.jobs.jobs_router](#jane_kitjobsjobs_router)

## jane_kit.jobs.JobStatus

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:64](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L64).

```python
class JobStatus(StrEnum):
```

Базові типи / інтерфейси: `StrEnum`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [QUEUED](jane_kit.jobs.md#jane_kitjobsjobstatusqueued) | Поле | ні |
| [RUNNING](jane_kit.jobs.md#jane_kitjobsjobstatusrunning) | Поле | ні |
| [CANCELLING](jane_kit.jobs.md#jane_kitjobsjobstatuscancelling) | Поле | ні |
| [SUCCEEDED](jane_kit.jobs.md#jane_kitjobsjobstatussucceeded) | Поле | ні |
| [FAILED](jane_kit.jobs.md#jane_kitjobsjobstatusfailed) | Поле | ні |
| [CANCELLED](jane_kit.jobs.md#jane_kitjobsjobstatuscancelled) | Поле | ні |

## jane_kit.jobs.JobStatus.QUEUED

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:65](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L65).

```python
QUEUED = 'queued'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:25](../../../../../../libs/jane-kit/tests/test_jobs.py#L25).

```python
assert job.status == JobStatus.QUEUED
```

## jane_kit.jobs.JobStatus.RUNNING

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:66](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L66).

```python
RUNNING = 'running'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:158](../../../../../../libs/jane-kit/tests/test_jobs.py#L158).

```python
job = Job(job_id="job_a", kind="demo", status=JobStatus.RUNNING)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:193](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L193).

```python
assert legacy is not None and legacy.status == JobStatus.RUNNING
```

## jane_kit.jobs.JobStatus.CANCELLING

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:67](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L67).

```python
CANCELLING = 'cancelling'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:80](../../../../../../libs/jane-kit/tests/test_jobs.py#L80).

```python
assert q.status == JobStatus.CANCELLING and q.cancellation and q.cancellation.reason == "wrong scope"
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:170](../../../../../../libs/jane-kit/tests/test_jobs.py#L170).

```python
assert current is not None and current.status == JobStatus.CANCELLING and current.progress is not None
```

## jane_kit.jobs.JobStatus.SUCCEEDED

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:68](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L68).

```python
SUCCEEDED = 'succeeded'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:29](../../../../../../libs/jane-kit/tests/test_jobs.py#L29).

```python
assert done.status == JobStatus.SUCCEEDED
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:171](../../../../../../libs/jane-kit/tests/test_jobs.py#L171).

```python
await store.save(job.model_copy(update={"status": JobStatus.SUCCEEDED, "result": {"x": 1}}))
```

## jane_kit.jobs.JobStatus.FAILED

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:69](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L69).

```python
FAILED = 'failed'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:118](../../../../../../libs/jane-kit/tests/test_jobs.py#L118).

```python
assert (await runner.cancel(j1.job_id)).status == JobStatus.FAILED
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:115](../../../../../../libs/jane-kit/tests/test_jobs.py#L115).

```python
assert r1.status == JobStatus.FAILED and r1.error and r1.error.code == "schema_mismatch"
```

## jane_kit.jobs.JobStatus.CANCELLED

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:70](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L70).

```python
CANCELLED = 'cancelled'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:82](../../../../../../libs/jane-kit/tests/test_jobs.py#L82).

```python
assert (await runner.wait(running.job_id)).status == JobStatus.CANCELLED
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:83](../../../../../../libs/jane-kit/tests/test_jobs.py#L83).

```python
assert (await runner.wait(queued.job_id)).status == JobStatus.CANCELLED
```

## jane_kit.jobs.TERMINAL_STATUSES

**Константа.** Код: [libs/jane-kit/src/jane_kit/jobs.py:73](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L73).

```python
TERMINAL_STATUSES = frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED})
```

## jane_kit.jobs.JobProgress

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:84](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L84).

```python
class JobProgress(_Model):
```

Базові типи / інтерфейси: `_Model`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [completed](jane_kit.jobs.md#jane_kitjobsjobprogresscompleted) | Поле | ні |
| [total](jane_kit.jobs.md#jane_kitjobsjobprogresstotal) | Поле | ні |
| [unit](jane_kit.jobs.md#jane_kitjobsjobprogressunit) | Поле | ні |
| [message](jane_kit.jobs.md#jane_kitjobsjobprogressmessage) | Поле | ні |
| [counters](jane_kit.jobs.md#jane_kitjobsjobprogresscounters) | Поле | ні |
| [updated_at](jane_kit.jobs.md#jane_kitjobsjobprogressupdated_at) | Поле | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:168](../../../../../../libs/jane-kit/tests/test_jobs.py#L168).

```python
await store.save(job.model_copy(update={"progress": JobProgress(completed=2)}))
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:260](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L260).

```python
await a.save(third.model_copy(update={"progress": JobProgress(completed=1)}))
```

## jane_kit.jobs.JobProgress.completed

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:85](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L85).

```python
completed: int | None = Field(default=None, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "0"
}
```

## jane_kit.jobs.JobProgress.total

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:86](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L86).

```python
total: int | None = Field(default=None, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "0"
}
```

## jane_kit.jobs.JobProgress.unit

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:87](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L87).

```python
unit: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobProgress.message

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:88](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L88).

```python
message: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobProgress.counters

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:89](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L89).

```python
counters: dict[str, int] | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobProgress.updated_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:90](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L90).

```python
updated_at: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobCancellation

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:93](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L93).

```python
class JobCancellation(_Model):
```

Базові типи / інтерфейси: `_Model`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [requested_at](jane_kit.jobs.md#jane_kitjobsjobcancellationrequested_at) | Поле | ні |
| [requested_by](jane_kit.jobs.md#jane_kitjobsjobcancellationrequested_by) | Поле | ні |
| [reason](jane_kit.jobs.md#jane_kitjobsjobcancellationreason) | Поле | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:160](../../../../../../libs/jane-kit/tests/test_jobs.py#L160).

```python
await store.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:252](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L252).

```python
await b.save(
        third.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=third.created_at),
            }
        )
    )
```

## jane_kit.jobs.JobCancellation.requested_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:94](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L94).

```python
requested_at: datetime
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobCancellation.requested_by

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:95](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L95).

```python
requested_by: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobCancellation.reason

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:96](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L96).

```python
reason: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobCancelRequest

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:99](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L99).

```python
class JobCancelRequest(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.jobs.md#jane_kitjobsjobcancelrequestmodel_config) | Поле | ні |
| [reason](jane_kit.jobs.md#jane_kitjobsjobcancelrequestreason) | Поле | ні |

## jane_kit.jobs.JobCancelRequest.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:100](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L100).

```python
model_config = ConfigDict(extra='forbid')
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.JobCancelRequest.reason

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:102](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L102).

```python
reason: str | None = Field(default=None, max_length=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "1000"
}
```

## jane_kit.jobs.Job

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:105](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L105).

```python
class Job(_Model):
```

Базові типи / інтерфейси: `_Model`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [job_id](jane_kit.jobs.md#jane_kitjobsjobjob_id) | Поле | ні |
| [kind](jane_kit.jobs.md#jane_kitjobsjobkind) | Поле | ні |
| [status](jane_kit.jobs.md#jane_kitjobsjobstatus) | Поле | ні |
| [created_at](jane_kit.jobs.md#jane_kitjobsjobcreated_at) | Поле | ні |
| [updated_at](jane_kit.jobs.md#jane_kitjobsjobupdated_at) | Поле | ні |
| [started_at](jane_kit.jobs.md#jane_kitjobsjobstarted_at) | Поле | ні |
| [finished_at](jane_kit.jobs.md#jane_kitjobsjobfinished_at) | Поле | ні |
| [progress](jane_kit.jobs.md#jane_kitjobsjobprogress) | Поле | ні |
| [result](jane_kit.jobs.md#jane_kitjobsjobresult) | Поле | ні |
| [result_ref](jane_kit.jobs.md#jane_kitjobsjobresult_ref) | Поле | ні |
| [error](jane_kit.jobs.md#jane_kitjobsjoberror) | Поле | ні |
| [cancellation](jane_kit.jobs.md#jane_kitjobsjobcancellation) | Поле | ні |
| [idempotency_key](jane_kit.jobs.md#jane_kitjobsjobidempotency_key) | Поле | ні |
| [links](jane_kit.jobs.md#jane_kitjobsjoblinks) | Поле | ні |
| [labels](jane_kit.jobs.md#jane_kitjobsjoblabels) | Поле | ні |
| [wire](jane_kit.jobs.md#jane_kitjobsjobwire) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:158](../../../../../../libs/jane-kit/tests/test_jobs.py#L158).

```python
job = Job(job_id="job_a", kind="demo", status=JobStatus.RUNNING)
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:185](../../../../../../libs/jane-kit/tests/test_jobs.py#L185).

```python
jobs = [Job(job_id=f"job_{n}", kind="demo", labels={"s": "1" if n % 2 else "2"}) for n in range(4)]
```

## jane_kit.jobs.Job.job_id

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:106](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L106).

```python
job_id: str
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:26](../../../../../../libs/jane-kit/tests/test_jobs.py#L26).

```python
assert job.job_id.startswith("job_")
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:27](../../../../../../libs/jane-kit/tests/test_jobs.py#L27).

```python
assert job.links == {"self": f"/v1/jobs/{job.job_id}", "cancel": f"/v1/jobs/{job.job_id}/cancel"}
```

## jane_kit.jobs.Job.kind

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:107](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L107).

```python
kind: str = Field(pattern='^[a-z][a-z0-9_]{1,63}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "'^[a-z][a-z0-9_]{1,63}$'"
}
```

## jane_kit.jobs.Job.status

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:108](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L108).

```python
status: JobStatus = JobStatus.QUEUED
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:25](../../../../../../libs/jane-kit/tests/test_jobs.py#L25).

```python
assert job.status == JobStatus.QUEUED
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:306](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L306).

```python
assert done.status == JobStatus.SUCCEEDED and done.result == {"n": 1}
```

## jane_kit.jobs.Job.created_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:109](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L109).

```python
created_at: datetime = Field(default_factory=_now)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "_now"
}
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:160](../../../../../../libs/jane-kit/tests/test_jobs.py#L160).

```python
await store.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:164](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L164).

```python
done = done.model_copy(update={"finished_at": done.created_at + timedelta(seconds=1)})
```

## jane_kit.jobs.Job.updated_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:110](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L110).

```python
updated_at: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.Job.started_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:111](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L111).

```python
started_at: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.Job.finished_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:112](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L112).

```python
finished_at: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.Job.progress

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:113](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L113).

```python
progress: JobProgress | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.Job.result

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:114](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L114).

```python
result: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:306](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L306).

```python
assert done.status == JobStatus.SUCCEEDED and done.result == {"n": 1}
```

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:74](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L74).

```python
job.result = {"n": 1}
```

## jane_kit.jobs.Job.result_ref

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:115](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L115).

```python
result_ref: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``ContentRef`` of a large result (passed by reference, not inline).
```

## jane_kit.jobs.Job.error

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:117](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L117).

```python
error: Problem | None = None
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:70](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L70).

```python
job.error = NotFound("x").to_problem()
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:345](../../../../../../services/handler-runtime/tests/test_state.py#L345).

```python
assert job.error is not None and job.error.retryable is True
```

## jane_kit.jobs.Job.cancellation

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:118](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L118).

```python
cancellation: JobCancellation | None = None
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:72](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L72).

```python
job.cancellation = JobCancellation(requested_at=now, reason="r")
```

## jane_kit.jobs.Job.idempotency_key

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:119](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L119).

```python
idempotency_key: str | None = Field(default=None, max_length=255)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "255"
}
```

## jane_kit.jobs.Job.links

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:120](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L120).

```python
links: dict[str, str] | None = None
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:27](../../../../../../libs/jane-kit/tests/test_jobs.py#L27).

```python
assert job.links == {"self": f"/v1/jobs/{job.job_id}", "cancel": f"/v1/jobs/{job.job_id}/cancel"}
```

## jane_kit.jobs.Job.labels

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:121](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L121).

```python
labels: dict[str, str] | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.jobs.Job.wire

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:123](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L123).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
JSON body as in the contract (``None`` fields omitted).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:75](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L75).

```python
COMMON.validate_component("Job", job.wire())
```

## jane_kit.jobs.JobLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:128](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L128).

```python
class JobLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_concurrent_jobs](jane_kit.jobs.md#jane_kitjobsjoblimitsmax_concurrent_jobs) | Поле | ні |
| [max_queued_jobs](jane_kit.jobs.md#jane_kitjobsjoblimitsmax_queued_jobs) | Поле | ні |
| [job_timeout_ms](jane_kit.jobs.md#jane_kitjobsjoblimitsjob_timeout_ms) | Поле | ні |
| [job_retention_seconds](jane_kit.jobs.md#jane_kitjobsjoblimitsjob_retention_seconds) | Поле | ні |
| [queue_full_retry_after_seconds](jane_kit.jobs.md#jane_kitjobsjoblimitsqueue_full_retry_after_seconds) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:225](../../../../../../libs/jane-kit/tests/test_config.py#L225).

```python
jobs: JobLimits = JobLimits()
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:36](../../../../../../libs/jane-kit/tests/test_jobs.py#L36).

```python
runner = JobRunner(limits=JobLimits(max_concurrent_jobs=2))
```

## jane_kit.jobs.JobLimits.max_concurrent_jobs

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:129](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L129).

```python
max_concurrent_jobs: int = Field(default=4, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Jobs executing at the same time in one instance; the rest wait in ``queued``.
```

## jane_kit.jobs.JobLimits.max_queued_jobs

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:131](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L131).

```python
max_queued_jobs: int = Field(default=1000, ge=0)
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
Beyond this, submit fails with 503 ``service_unavailable`` (backpressure, retryable).
```

## jane_kit.jobs.JobLimits.job_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:133](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L133).

```python
job_timeout_ms: int = Field(default=3600000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3600000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Wall-clock limit per job; exceeded -> ``failed`` with code ``timeout``.
```

## jane_kit.jobs.JobLimits.job_retention_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:135](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L135).

```python
job_retention_seconds: int = contract_field('transfer.job_retention_seconds', 86400, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.job_retention_seconds'",
  "ge": "60"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.job_retention_seconds``: finished jobs are kept at least this long.
```

## jane_kit.jobs.JobLimits.queue_full_retry_after_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/jobs.py:137](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L137).

```python
queue_full_retry_after_seconds: int = Field(default=1, ge=0)
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
``Retry-After`` sent with 503 when the job queue is full.
```

## jane_kit.jobs.JobCancelledError

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:141](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L141).

```python
class JobCancelledError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Опис із вихідного коду

```text
Raised inside a job by :meth:`JobContext.check_cancelled`.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_service_ops.py:342](../../../../../../services/registry/tests/test_service_ops.py#L342).

```python
JobCancelledError("job")
```

## jane_kit.jobs.JobStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:145](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L145).

```python
class JobStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [create](jane_kit.jobs.md#jane_kitjobsjobstorecreate) | Метод | ні |
| [get](jane_kit.jobs.md#jane_kitjobsjobstoreget) | Метод | ні |
| [save](jane_kit.jobs.md#jane_kitjobsjobstoresave) | Метод | ні |

## jane_kit.jobs.JobStore.create

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:146](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L146).

```python
async def create(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.jobs.JobStore.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:147](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L147).

```python
async def get(self, job_id: str) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job | None`.

## jane_kit.jobs.JobStore.save

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:148](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L148).

```python
async def save(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.jobs.decide_save

**Функція.** Код: [libs/jane-kit/src/jane_kit/jobs.py:151](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L151).

```python
def decide_save(current: Job | None, new: Job, *, mine: bool, live: bool) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `current` | `Job \| None` | `—` | positional-or-keyword |
| `new` | `Job` | `—` | positional-or-keyword |
| `mine` | `bool` | `—` | keyword-only |
| `live` | `bool` | `—` | keyword-only |

Результат: `Job | None`.

### Опис із вихідного коду

```text
The document a save of ``new`` writes over ``current`` (``None``: write nothing).

``mine`` - the saving instance owns the job; ``live`` - the owner's lease has not expired.
```

## jane_kit.jobs.orphaned

**Функція.** Код: [libs/jane-kit/src/jane_kit/jobs.py:189](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L189).

```python
def orphaned(job: Job, owner: str | None) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `job` | `Job` | `—` | positional-or-keyword |
| `owner` | `str \| None` | `—` | positional-or-keyword |

Результат: `Job`.

### Опис із вихідного коду

```text
Terminal state of a job whose owner stopped renewing its lease (killed, hung or partitioned).
```

## jane_kit.jobs.resumed

**Функція.** Код: [libs/jane-kit/src/jane_kit/jobs.py:210](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L210).

```python
def resumed(existing: Job, new: Job) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `existing` | `Job` | `—` | positional-or-keyword |
| `new` | `Job` | `—` | positional-or-keyword |

Результат: `Job`.

### Опис із вихідного коду

```text
``new`` (a resubmission of the same ``job_id``) keeping what the existing job already recorded.
```

## jane_kit.jobs.JobPosition

**Змінна.** Код: [libs/jane-kit/src/jane_kit/jobs.py:226](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L226).

```python
JobPosition = tuple[datetime, str]
```

### Опис із вихідного коду

```text
Cursor position in a job listing: ``(created_at, job_id)``, newest first.
```

## jane_kit.jobs.InMemoryJobStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:230](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L230).

```python
class InMemoryJobStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.jobs.md#jane_kitjobsinmemoryjobstore__init__) | Конструктор | ні |
| [limits](jane_kit.jobs.md#jane_kitjobsinmemoryjobstorelimits) | Поле екземпляра | ні |
| [create](jane_kit.jobs.md#jane_kitjobsinmemoryjobstorecreate) | Метод | ні |
| [get](jane_kit.jobs.md#jane_kitjobsinmemoryjobstoreget) | Метод | ні |
| [save](jane_kit.jobs.md#jane_kitjobsinmemoryjobstoresave) | Метод | ні |
| [page](jane_kit.jobs.md#jane_kitjobsinmemoryjobstorepage) | Метод | ні |

### Опис із вихідного коду

```text
Single-instance store; drops finished jobs older than ``job_retention_seconds``.

Writes follow :func:`decide_save` (this process owns every job and its lease never expires): a terminal job
never changes, a committed cancellation is kept.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:157](../../../../../../libs/jane-kit/tests/test_jobs.py#L157).

```python
store = InMemoryJobStore()
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:184](../../../../../../libs/jane-kit/tests/test_jobs.py#L184).

```python
store = InMemoryJobStore()
```

## jane_kit.jobs.InMemoryJobStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/jobs.py:237](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L237).

```python
def __init__(self, limits: JobLimits | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `JobLimits \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:157](../../../../../../libs/jane-kit/tests/test_jobs.py#L157).

```python
store = InMemoryJobStore()
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:184](../../../../../../libs/jane-kit/tests/test_jobs.py#L184).

```python
store = InMemoryJobStore()
```

## jane_kit.jobs.InMemoryJobStore.limits

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/jobs.py:238](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L238).

```python
self.limits = limits or JobLimits()
```

## jane_kit.jobs.InMemoryJobStore.create

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:250](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L250).

```python
async def create(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:159](../../../../../../libs/jane-kit/tests/test_jobs.py#L159).

```python
await store.create(job)
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:187](../../../../../../libs/jane-kit/tests/test_jobs.py#L187).

```python
await store.create(job)
```

## jane_kit.jobs.InMemoryJobStore.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:257](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L257).

```python
async def get(self, job_id: str) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job | None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:169](../../../../../../libs/jane-kit/tests/test_jobs.py#L169).

```python
current = await store.get("job_a")
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:172](../../../../../../libs/jane-kit/tests/test_jobs.py#L172).

```python
done = await store.get("job_a")
```

## jane_kit.jobs.InMemoryJobStore.save

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:261](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L261).

```python
async def save(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:160](../../../../../../libs/jane-kit/tests/test_jobs.py#L160).

```python
await store.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:168](../../../../../../libs/jane-kit/tests/test_jobs.py#L168).

```python
await store.save(job.model_copy(update={"progress": JobProgress(completed=2)}))
```

## jane_kit.jobs.InMemoryJobStore.page

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:266](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L266).

```python
async def page(self, kind: str, *, labels: Mapping[str, str], statuses: Iterable[str] | None, after: JobPosition | None, limit: int) -> list[Job]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `labels` | `Mapping[str, str]` | `—` | keyword-only |
| `statuses` | `Iterable[str] \| None` | `—` | keyword-only |
| `after` | `JobPosition \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `list[Job]`.

### Опис із вихідного коду

```text
Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly
after ``after`` (the same listing as :meth:`jane_kit.stores.PgJobStore.page`).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:189](../../../../../../libs/jane-kit/tests/test_jobs.py#L189).

```python
page = await store.page("demo", labels={}, statuses=None, after=None, limit=2)
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:191](../../../../../../libs/jane-kit/tests/test_jobs.py#L191).

```python
rest = await store.page(
        "demo", labels={}, statuses=None, after=(page[-1].created_at, page[-1].job_id), limit=5
    )
```

## jane_kit.jobs.JobContext

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:291](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L291).

```python
class JobContext:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.jobs.md#jane_kitjobsjobcontext__init__) | Конструктор | ні |
| [job_id](jane_kit.jobs.md#jane_kitjobsjobcontextjob_id) | Поле екземпляра | ні |
| [progress](jane_kit.jobs.md#jane_kitjobsjobcontextprogress) | Метод | ні |
| [cancelled](jane_kit.jobs.md#jane_kitjobsjobcontextcancelled) | Метод | ні |
| [check_cancelled](jane_kit.jobs.md#jane_kitjobsjobcontextcheck_cancelled) | Метод | ні |

### Опис із вихідного коду

```text
Handle given to a running job for progress reporting and cooperative cancellation.
```

## jane_kit.jobs.JobContext.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/jobs.py:294](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L294).

```python
def __init__(self, runner: JobRunner, job_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `runner` | `JobRunner` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.jobs.JobContext.job_id

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/jobs.py:296](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L296).

```python
self.job_id = job_id
```

## jane_kit.jobs.JobContext.progress

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:298](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L298).

```python
async def progress(self, completed: int | None=None, total: int | None=None, *, unit: str | None=None, message: str | None=None, counters: Mapping[str, int] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `completed` | `int \| None` | `None` | positional-or-keyword |
| `total` | `int \| None` | `None` | positional-or-keyword |
| `unit` | `str \| None` | `None` | keyword-only |
| `message` | `str \| None` | `None` | keyword-only |
| `counters` | `Mapping[str, int] \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:21](../../../../../../libs/jane-kit/tests/test_jobs.py#L21).

```python
await ctx.progress(5, 10, unit="pages", counters={"fetched": 5})
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:289](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L289).

```python
await ctx.progress(1, 2)
```

## jane_kit.jobs.JobContext.cancelled

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:325](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L325).

```python
async def cancelled(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:93](../../../../../../libs/jane-kit/tests/test_jobs.py#L93).

```python
seen.append(await ctx.cancelled())
```

## jane_kit.jobs.JobContext.check_cancelled

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:329](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L329).

```python
async def check_cancelled(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `JobCancelledError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:94](../../../../../../libs/jane-kit/tests/test_jobs.py#L94).

```python
await ctx.check_cancelled()
```

## jane_kit.jobs.JobRunner

**Клас.** Код: [libs/jane-kit/src/jane_kit/jobs.py:337](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L337).

```python
class JobRunner:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.jobs.md#jane_kitjobsjobrunner__init__) | Конструктор | ні |
| [limits](jane_kit.jobs.md#jane_kitjobsjobrunnerlimits) | Поле екземпляра | ні |
| [store](jane_kit.jobs.md#jane_kitjobsjobrunnerstore) | Поле екземпляра | ні |
| [jobs_path](jane_kit.jobs.md#jane_kitjobsjobrunnerjobs_path) | Поле екземпляра | ні |
| [active](jane_kit.jobs.md#jane_kitjobsjobrunneractive) | Властивість | ні |
| [location](jane_kit.jobs.md#jane_kitjobsjobrunnerlocation) | Метод | ні |
| [submit](jane_kit.jobs.md#jane_kitjobsjobrunnersubmit) | Метод | ні |
| [get](jane_kit.jobs.md#jane_kitjobsjobrunnerget) | Метод | ні |
| [cancel](jane_kit.jobs.md#jane_kitjobsjobrunnercancel) | Метод | ні |
| [wait](jane_kit.jobs.md#jane_kitjobsjobrunnerwait) | Метод | ні |
| [shutdown](jane_kit.jobs.md#jane_kitjobsjobrunnershutdown) | Метод | ні |

### Опис із вихідного коду

```text
Runs job coroutines in the current event loop with limits from config.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:515](../../../../../../libs/jane-kit/tests/test_auth.py#L515).

```python
app.include_router(jobs_router(JobRunner()))
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:18](../../../../../../libs/jane-kit/tests/test_jobs.py#L18).

```python
runner = JobRunner()
```

## jane_kit.jobs.JobRunner.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/jobs.py:340](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L340).

```python
def __init__(self, store: JobStore | None=None, limits: JobLimits | None=None, jobs_path: str='/v1/jobs') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `store` | `JobStore \| None` | `None` | positional-or-keyword |
| `limits` | `JobLimits \| None` | `None` | positional-or-keyword |
| `jobs_path` | `str` | `'/v1/jobs'` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:515](../../../../../../libs/jane-kit/tests/test_auth.py#L515).

```python
app.include_router(jobs_router(JobRunner()))
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:18](../../../../../../libs/jane-kit/tests/test_jobs.py#L18).

```python
runner = JobRunner()
```

## jane_kit.jobs.JobRunner.limits

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/jobs.py:343](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L343).

```python
self.limits = limits or JobLimits()
```

## jane_kit.jobs.JobRunner.store

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/jobs.py:344](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L344).

```python
self.store: JobStore = store or InMemoryJobStore(self.limits)
```

## jane_kit.jobs.JobRunner.jobs_path

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/jobs.py:345](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L345).

```python
self.jobs_path = jobs_path.rstrip('/')
```

## jane_kit.jobs.JobRunner.active

**Властивість.** Код: [libs/jane-kit/src/jane_kit/jobs.py:350](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L350).

```python
def active(self) -> int:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

Доступ: читання — так; запис — ні.

## jane_kit.jobs.JobRunner.location

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:353](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L353).

```python
def location(self, job_id: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_kit.jobs.JobRunner.submit

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:356](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L356).

```python
async def submit(self, kind: str, fn: JobFn, *, job_id: str | None=None, idempotency_key: str | None=None, labels: Mapping[str, str] | None=None) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `fn` | `JobFn` | `—` | positional-or-keyword |
| `job_id` | `str \| None` | `None` | keyword-only |
| `idempotency_key` | `str \| None` | `None` | keyword-only |
| `labels` | `Mapping[str, str] \| None` | `None` | keyword-only |

Результат: `Job`.

Явні `raise` у тілі: `ServiceUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:24](../../../../../../libs/jane-kit/tests/test_jobs.py#L24).

```python
job = await runner.submit("collection", work, idempotency_key="k1")
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:59](../../../../../../libs/jane-kit/tests/test_jobs.py#L59).

```python
await runner.submit("demo", work)
```

## jane_kit.jobs.JobRunner.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:424](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L424).

```python
async def get(self, job_id: str) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:120](../../../../../../libs/jane-kit/tests/test_jobs.py#L120).

```python
await runner.get("nope")
```

## jane_kit.jobs.JobRunner.cancel

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:430](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L430).

```python
async def cancel(self, job_id: str, reason: str | None=None, requested_by: str | None=None) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |
| `reason` | `str \| None` | `None` | positional-or-keyword |
| `requested_by` | `str \| None` | `None` | positional-or-keyword |

Результат: `Job`.

### Опис із вихідного коду

```text
Request cancellation. Terminal jobs are returned unchanged (HTTP 200 in the contract).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:79](../../../../../../libs/jane-kit/tests/test_jobs.py#L79).

```python
q = await runner.cancel(queued.job_id, reason="wrong scope")
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:81](../../../../../../libs/jane-kit/tests/test_jobs.py#L81).

```python
await runner.cancel(running.job_id)
```

## jane_kit.jobs.JobRunner.wait

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:442](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L442).

```python
async def wait(self, job_id: str) -> Job:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:28](../../../../../../libs/jane-kit/tests/test_jobs.py#L28).

```python
done = await runner.wait(job.job_id)
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:97](../../../../../../libs/jane-kit/tests/test_jobs.py#L97).

```python
await runner.wait(job.job_id)
```

## jane_kit.jobs.JobRunner.shutdown

**Метод.** Код: [libs/jane-kit/src/jane_kit/jobs.py:448](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L448).

```python
async def shutdown(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:65](../../../../../../libs/jane-kit/tests/test_jobs.py#L65).

```python
await runner.shutdown()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:317](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L317).

```python
await runner.shutdown()
```

## jane_kit.jobs.accepted

**Функція.** Код: [libs/jane-kit/src/jane_kit/jobs.py:454](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L454).

```python
def accepted(job: Job, location: str | None=None, headers: Mapping[str, str] | None=None) -> JSONResponse:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `job` | `Job` | `—` | positional-or-keyword |
| `location` | `str \| None` | `None` | positional-or-keyword |
| `headers` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |

Результат: `JSONResponse`.

### Опис із вихідного коду

```text
``202 Accepted`` with the Job body and ``Location`` of the job resource.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:133](../../../../../../libs/jane-kit/tests/test_jobs.py#L133).

```python
return accepted(await runner.submit("work", work))
```

## jane_kit.jobs.jobs_router

**Функція.** Код: [libs/jane-kit/src/jane_kit/jobs.py:460](../../../../../../libs/jane-kit/src/jane_kit/jobs.py#L460).

```python
def jobs_router(runner: JobRunner) -> APIRouter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `runner` | `JobRunner` | `—` | positional-or-keyword |

Результат: `APIRouter`.

### Опис із вихідного коду

```text
``GET {jobs_path}/{job_id}`` and ``POST {jobs_path}/{job_id}/cancel`` (common.yaml Job, JobCancel).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:515](../../../../../../libs/jane-kit/tests/test_auth.py#L515).

```python
app.include_router(jobs_router(JobRunner()))
```

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:126](../../../../../../libs/jane-kit/tests/test_jobs.py#L126).

```python
app.include_router(jobs_router(runner))
```
