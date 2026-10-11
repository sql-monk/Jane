# jane_assistant.state

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.state.ServiceState](#jane_assistantstateservicestate)
- [jane_assistant.state.ServiceState.name](#jane_assistantstateservicestatename)
- [jane_assistant.state.ServiceState.idempotency](#jane_assistantstateservicestateidempotency)
- [jane_assistant.state.ServiceState.jobs](#jane_assistantstateservicestatejobs)
- [jane_assistant.state.ServiceState.job_list](#jane_assistantstateservicestatejob_list)
- [jane_assistant.state.ServiceState.sessions](#jane_assistantstateservicestatesessions)
- [jane_assistant.state.ServiceState.open](#jane_assistantstateservicestateopen)
- [jane_assistant.state.ServiceState.close](#jane_assistantstateservicestateclose)
- [jane_assistant.state.ServiceState.ping](#jane_assistantstateservicestateping)
- [jane_assistant.state.ServiceState.heartbeat](#jane_assistantstateservicestateheartbeat)
- [jane_assistant.state.ServiceState.release_owned](#jane_assistantstateservicestaterelease_owned)
- [jane_assistant.state.InMemoryState](#jane_assistantstateinmemorystate)
- [jane_assistant.state.InMemoryState.name](#jane_assistantstateinmemorystatename)
- [jane_assistant.state.InMemoryState.__init__](#jane_assistantstateinmemorystate__init__)
- [jane_assistant.state.InMemoryState.idempotency](#jane_assistantstateinmemorystateidempotency)
- [jane_assistant.state.InMemoryState.jobs](#jane_assistantstateinmemorystatejobs)
- [jane_assistant.state.InMemoryState.job_list](#jane_assistantstateinmemorystatejob_list)
- [jane_assistant.state.InMemoryState.sessions](#jane_assistantstateinmemorystatesessions)
- [jane_assistant.state.InMemoryState.open](#jane_assistantstateinmemorystateopen)
- [jane_assistant.state.InMemoryState.close](#jane_assistantstateinmemorystateclose)
- [jane_assistant.state.InMemoryState.ping](#jane_assistantstateinmemorystateping)
- [jane_assistant.state.InMemoryState.heartbeat](#jane_assistantstateinmemorystateheartbeat)
- [jane_assistant.state.InMemoryState.release_owned](#jane_assistantstateinmemorystaterelease_owned)
- [jane_assistant.state.PostgresState](#jane_assistantstatepostgresstate)
- [jane_assistant.state.PostgresState.name](#jane_assistantstatepostgresstatename)
- [jane_assistant.state.PostgresState.__init__](#jane_assistantstatepostgresstate__init__)
- [jane_assistant.state.PostgresState.schema_name](#jane_assistantstatepostgresstateschema_name)
- [jane_assistant.state.PostgresState.schema](#jane_assistantstatepostgresstateschema)
- [jane_assistant.state.PostgresState.limits](#jane_assistantstatepostgresstatelimits)
- [jane_assistant.state.PostgresState.instance_id](#jane_assistantstatepostgresstateinstance_id)
- [jane_assistant.state.PostgresState.db](#jane_assistantstatepostgresstatedb)
- [jane_assistant.state.PostgresState.pool](#jane_assistantstatepostgresstatepool)
- [jane_assistant.state.PostgresState.idempotency](#jane_assistantstatepostgresstateidempotency)
- [jane_assistant.state.PostgresState.jobs](#jane_assistantstatepostgresstatejobs)
- [jane_assistant.state.PostgresState.job_list](#jane_assistantstatepostgresstatejob_list)
- [jane_assistant.state.PostgresState.sessions](#jane_assistantstatepostgresstatesessions)
- [jane_assistant.state.PostgresState.q](#jane_assistantstatepostgresstateq)
- [jane_assistant.state.PostgresState.run](#jane_assistantstatepostgresstaterun)
- [jane_assistant.state.PostgresState.rowcount](#jane_assistantstatepostgresstaterowcount)
- [jane_assistant.state.PostgresState.open](#jane_assistantstatepostgresstateopen)
- [jane_assistant.state.PostgresState.close](#jane_assistantstatepostgresstateclose)
- [jane_assistant.state.PostgresState.ping](#jane_assistantstatepostgresstateping)
- [jane_assistant.state.PostgresState.heartbeat](#jane_assistantstatepostgresstateheartbeat)
- [jane_assistant.state.PostgresState.release_owned](#jane_assistantstatepostgresstaterelease_owned)

## jane_assistant.state.ServiceState

**Клас.** Код: [services/assistant/src/jane_assistant/state.py:63](../../../../../../services/assistant/src/jane_assistant/state.py#L63).

```python
class ServiceState(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_assistant.state.md#jane_assistantstateservicestatename) | Поле | ні |
| [idempotency](jane_assistant.state.md#jane_assistantstateservicestateidempotency) | Поле | ні |
| [jobs](jane_assistant.state.md#jane_assistantstateservicestatejobs) | Поле | ні |
| [job_list](jane_assistant.state.md#jane_assistantstateservicestatejob_list) | Поле | ні |
| [sessions](jane_assistant.state.md#jane_assistantstateservicestatesessions) | Поле | ні |
| [open](jane_assistant.state.md#jane_assistantstateservicestateopen) | Метод | ні |
| [close](jane_assistant.state.md#jane_assistantstateservicestateclose) | Метод | ні |
| [ping](jane_assistant.state.md#jane_assistantstateservicestateping) | Метод | ні |
| [heartbeat](jane_assistant.state.md#jane_assistantstateservicestateheartbeat) | Метод | ні |
| [release_owned](jane_assistant.state.md#jane_assistantstateservicestaterelease_owned) | Метод | ні |

## jane_assistant.state.ServiceState.name

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:64](../../../../../../services/assistant/src/jane_assistant/state.py#L64).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_assistant.state.ServiceState.idempotency

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:65](../../../../../../services/assistant/src/jane_assistant/state.py#L65).

```python
idempotency: IdempotencyStore
```

Доступ: читання — так; запис — так.

## jane_assistant.state.ServiceState.jobs

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:66](../../../../../../services/assistant/src/jane_assistant/state.py#L66).

```python
jobs: JobStore
```

Доступ: читання — так; запис — так.

## jane_assistant.state.ServiceState.job_list

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:67](../../../../../../services/assistant/src/jane_assistant/state.py#L67).

```python
job_list: JobLister
```

Доступ: читання — так; запис — так.

## jane_assistant.state.ServiceState.sessions

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:68](../../../../../../services/assistant/src/jane_assistant/state.py#L68).

```python
sessions: SessionStore
```

Доступ: читання — так; запис — так.

## jane_assistant.state.ServiceState.open

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:70](../../../../../../services/assistant/src/jane_assistant/state.py#L70).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.ServiceState.close

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:71](../../../../../../services/assistant/src/jane_assistant/state.py#L71).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.ServiceState.ping

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:72](../../../../../../services/assistant/src/jane_assistant/state.py#L72).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_assistant.state.ServiceState.heartbeat

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:73](../../../../../../services/assistant/src/jane_assistant/state.py#L73).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.ServiceState.release_owned

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:74](../../../../../../services/assistant/src/jane_assistant/state.py#L74).

```python
async def release_owned(self, reason: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.InMemoryState

**Клас.** Код: [services/assistant/src/jane_assistant/state.py:77](../../../../../../services/assistant/src/jane_assistant/state.py#L77).

```python
class InMemoryState:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_assistant.state.md#jane_assistantstateinmemorystatename) | Поле | ні |
| [__init__](jane_assistant.state.md#jane_assistantstateinmemorystate__init__) | Конструктор | ні |
| [idempotency](jane_assistant.state.md#jane_assistantstateinmemorystateidempotency) | Поле екземпляра | ні |
| [jobs](jane_assistant.state.md#jane_assistantstateinmemorystatejobs) | Поле екземпляра | ні |
| [job_list](jane_assistant.state.md#jane_assistantstateinmemorystatejob_list) | Поле екземпляра | ні |
| [sessions](jane_assistant.state.md#jane_assistantstateinmemorystatesessions) | Поле екземпляра | ні |
| [open](jane_assistant.state.md#jane_assistantstateinmemorystateopen) | Метод | ні |
| [close](jane_assistant.state.md#jane_assistantstateinmemorystateclose) | Метод | ні |
| [ping](jane_assistant.state.md#jane_assistantstateinmemorystateping) | Метод | ні |
| [heartbeat](jane_assistant.state.md#jane_assistantstateinmemorystateheartbeat) | Метод | ні |
| [release_owned](jane_assistant.state.md#jane_assistantstateinmemorystaterelease_owned) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:219](../../../../../../services/assistant/tests/test_lists.py#L219).

```python
state = InMemoryState(ServiceLimits())
```

## jane_assistant.state.InMemoryState.name

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:78](../../../../../../services/assistant/src/jane_assistant/state.py#L78).

```python
name = 'memory'
```

Доступ: читання — так; запис — так.

## jane_assistant.state.InMemoryState.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/state.py:80](../../../../../../services/assistant/src/jane_assistant/state.py#L80).

```python
def __init__(self, limits: ServiceLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:219](../../../../../../services/assistant/tests/test_lists.py#L219).

```python
state = InMemoryState(ServiceLimits())
```

## jane_assistant.state.InMemoryState.idempotency

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:81](../../../../../../services/assistant/src/jane_assistant/state.py#L81).

```python
self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(limits.idempotency)
```

## jane_assistant.state.InMemoryState.jobs

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:83](../../../../../../services/assistant/src/jane_assistant/state.py#L83).

```python
self.jobs: JobStore = jobs
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:204](../../../../../../services/assistant/tests/test_lists.py#L204).

```python
asyncio.run(state.jobs.create(job))
```

Контекст і передумови: [services/assistant/tests/test_lists.py:223](../../../../../../services/assistant/tests/test_lists.py#L223).

```python
await state.jobs.create(Job(job_id="job_new1", kind="improvement"))
```

## jane_assistant.state.InMemoryState.job_list

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:84](../../../../../../services/assistant/src/jane_assistant/state.py#L84).

```python
self.job_list: JobLister = jobs
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:234](../../../../../../services/assistant/tests/test_lists.py#L234).

```python
return await state.job_list.page("improvement", labels={}, statuses=None, after=None, limit=10)
```

## jane_assistant.state.InMemoryState.sessions

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:85](../../../../../../services/assistant/src/jane_assistant/state.py#L85).

```python
self.sessions: SessionStore = InMemorySessionStore()
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:205](../../../../../../services/assistant/tests/test_lists.py#L205).

```python
asyncio.run(state.sessions.save(session))
```

## jane_assistant.state.InMemoryState.open

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:87](../../../../../../services/assistant/src/jane_assistant/state.py#L87).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.InMemoryState.close

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:90](../../../../../../services/assistant/src/jane_assistant/state.py#L90).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.InMemoryState.ping

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:93](../../../../../../services/assistant/src/jane_assistant/state.py#L93).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_assistant.state.InMemoryState.heartbeat

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:96](../../../../../../services/assistant/src/jane_assistant/state.py#L96).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.InMemoryState.release_owned

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:99](../../../../../../services/assistant/src/jane_assistant/state.py#L99).

```python
async def release_owned(self, reason: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.state.PostgresState

**Клас.** Код: [services/assistant/src/jane_assistant/state.py:114](../../../../../../services/assistant/src/jane_assistant/state.py#L114).

```python
class PostgresState:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_assistant.state.md#jane_assistantstatepostgresstatename) | Поле | ні |
| [__init__](jane_assistant.state.md#jane_assistantstatepostgresstate__init__) | Конструктор | ні |
| [schema_name](jane_assistant.state.md#jane_assistantstatepostgresstateschema_name) | Поле екземпляра | ні |
| [schema](jane_assistant.state.md#jane_assistantstatepostgresstateschema) | Поле екземпляра | ні |
| [limits](jane_assistant.state.md#jane_assistantstatepostgresstatelimits) | Поле екземпляра | ні |
| [instance_id](jane_assistant.state.md#jane_assistantstatepostgresstateinstance_id) | Поле екземпляра | ні |
| [db](jane_assistant.state.md#jane_assistantstatepostgresstatedb) | Поле екземпляра | ні |
| [pool](jane_assistant.state.md#jane_assistantstatepostgresstatepool) | Поле екземпляра | ні |
| [idempotency](jane_assistant.state.md#jane_assistantstatepostgresstateidempotency) | Поле екземпляра | ні |
| [jobs](jane_assistant.state.md#jane_assistantstatepostgresstatejobs) | Поле екземпляра | ні |
| [job_list](jane_assistant.state.md#jane_assistantstatepostgresstatejob_list) | Поле екземпляра | ні |
| [sessions](jane_assistant.state.md#jane_assistantstatepostgresstatesessions) | Поле екземпляра | ні |
| [q](jane_assistant.state.md#jane_assistantstatepostgresstateq) | Метод | ні |
| [run](jane_assistant.state.md#jane_assistantstatepostgresstaterun) | Метод | ні |
| [rowcount](jane_assistant.state.md#jane_assistantstatepostgresstaterowcount) | Метод | ні |
| [open](jane_assistant.state.md#jane_assistantstatepostgresstateopen) | Метод | ні |
| [close](jane_assistant.state.md#jane_assistantstatepostgresstateclose) | Метод | ні |
| [ping](jane_assistant.state.md#jane_assistantstatepostgresstateping) | Метод | ні |
| [heartbeat](jane_assistant.state.md#jane_assistantstatepostgresstateheartbeat) | Метод | ні |
| [release_owned](jane_assistant.state.md#jane_assistantstatepostgresstaterelease_owned) | Метод | ні |

### Опис із вихідного коду

```text
Jobs and ``Idempotency-Key`` records in jane-kit's shared stores (R17), onboarding sessions here.

The tables ``idempotency`` and ``jobs`` keep their layout; the kit migration adds the claim columns in place.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:410](../../../../../../services/assistant/tests/test_state.py#L410).

```python
dead = PostgresState(own[0], own[1], ServiceLimits(state=StateLimits(job_lease_ms=1)), "dead")
```

Контекст і передумови: [services/assistant/tests/test_state.py:304](../../../../../../services/assistant/tests/test_state.py#L304).

```python
dead, alive = (
            PostgresState(pg[0], schema, short, "dead"),
            PostgresState(pg[0], schema, ServiceLimits(), "alive"),
        )
```

## jane_assistant.state.PostgresState.name

**Поле.** Код: [services/assistant/src/jane_assistant/state.py:120](../../../../../../services/assistant/src/jane_assistant/state.py#L120).

```python
name = 'postgresql'
```

Доступ: читання — так; запис — так.

## jane_assistant.state.PostgresState.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/state.py:122](../../../../../../services/assistant/src/jane_assistant/state.py#L122).

```python
def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `schema` | `str` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:410](../../../../../../services/assistant/tests/test_state.py#L410).

```python
dead = PostgresState(own[0], own[1], ServiceLimits(state=StateLimits(job_lease_ms=1)), "dead")
```

Контекст і передумови: [services/assistant/tests/test_state.py:304](../../../../../../services/assistant/tests/test_state.py#L304).

```python
dead, alive = (
            PostgresState(pg[0], schema, short, "dead"),
            PostgresState(pg[0], schema, ServiceLimits(), "alive"),
        )
```

## jane_assistant.state.PostgresState.schema_name

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:123](../../../../../../services/assistant/src/jane_assistant/state.py#L123).

```python
self.schema_name = schema
```

## jane_assistant.state.PostgresState.schema

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:124](../../../../../../services/assistant/src/jane_assistant/state.py#L124).

```python
self.schema = sql.Identifier(schema)
```

## jane_assistant.state.PostgresState.limits

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:125](../../../../../../services/assistant/src/jane_assistant/state.py#L125).

```python
self.limits = limits
```

## jane_assistant.state.PostgresState.instance_id

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:126](../../../../../../services/assistant/src/jane_assistant/state.py#L126).

```python
self.instance_id = instance_id
```

## jane_assistant.state.PostgresState.db

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:128](../../../../../../services/assistant/src/jane_assistant/state.py#L128).

```python
self.db = PgDatabase(dsn, max_size=st.pool_max_size, connect_timeout_ms=st.connect_timeout_ms)
```

## jane_assistant.state.PostgresState.pool

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:129](../../../../../../services/assistant/src/jane_assistant/state.py#L129).

```python
self.pool = self.db.pool
```

## jane_assistant.state.PostgresState.idempotency

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:140](../../../../../../services/assistant/src/jane_assistant/state.py#L140).

```python
self.idempotency: IdempotencyStore = self._idem
```

## jane_assistant.state.PostgresState.jobs

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:141](../../../../../../services/assistant/src/jane_assistant/state.py#L141).

```python
self.jobs: JobStore = self._jobs
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:311](../../../../../../services/assistant/tests/test_state.py#L311).

```python
await dead.jobs.create(
                Job(job_id="job_stale1", kind="improvement", status="running", labels={"package_id": "p"})
            )
```

Контекст і передумови: [services/assistant/tests/test_state.py:413](../../../../../../services/assistant/tests/test_state.py#L413).

```python
await dead.jobs.create(Job(job_id="job_dead2", kind="onboarding", status=JobStatus.RUNNING))
```

## jane_assistant.state.PostgresState.job_list

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:142](../../../../../../services/assistant/src/jane_assistant/state.py#L142).

```python
self.job_list: JobLister = self._jobs
```

## jane_assistant.state.PostgresState.sessions

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/state.py:143](../../../../../../services/assistant/src/jane_assistant/state.py#L143).

```python
self.sessions: SessionStore = _PgSessions(self)
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:418](../../../../../../services/assistant/tests/test_state.py#L418).

```python
await dead.sessions.save(session)
```

## jane_assistant.state.PostgresState.q

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:145](../../../../../../services/assistant/src/jane_assistant/state.py#L145).

```python
def q(self, text: str) -> sql.Composed:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |

Результат: `sql.Composed`.

## jane_assistant.state.PostgresState.run

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:148](../../../../../../services/assistant/src/jane_assistant/state.py#L148).

```python
def run(self, text: str, params: tuple[Any, ...]=(), fetch: bool=False) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `params` | `tuple[Any, ...]` | `()` | positional-or-keyword |
| `fetch` | `bool` | `False` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_assistant.state.PostgresState.rowcount

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:153](../../../../../../services/assistant/src/jane_assistant/state.py#L153).

```python
def rowcount(self, text: str, params: tuple[Any, ...]) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `params` | `tuple[Any, ...]` | `—` | positional-or-keyword |

Результат: `int`.

## jane_assistant.state.PostgresState.open

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:166](../../../../../../services/assistant/src/jane_assistant/state.py#L166).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:308](../../../../../../services/assistant/tests/test_state.py#L308).

```python
await dead.open()
```

Контекст і передумови: [services/assistant/tests/test_state.py:411](../../../../../../services/assistant/tests/test_state.py#L411).

```python
await dead.open()
```

## jane_assistant.state.PostgresState.close

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:170](../../../../../../services/assistant/src/jane_assistant/state.py#L170).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:334](../../../../../../services/assistant/tests/test_state.py#L334).

```python
await dead.close()
```

Контекст і передумови: [services/assistant/tests/test_state.py:420](../../../../../../services/assistant/tests/test_state.py#L420).

```python
await dead.close()
```

## jane_assistant.state.PostgresState.ping

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:173](../../../../../../services/assistant/src/jane_assistant/state.py#L173).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_assistant.state.PostgresState.heartbeat

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:176](../../../../../../services/assistant/src/jane_assistant/state.py#L176).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Renew this process's job leases and idempotency claims; drop expired keys.
```

## jane_assistant.state.PostgresState.release_owned

**Метод.** Код: [services/assistant/src/jane_assistant/state.py:182](../../../../../../services/assistant/src/jane_assistant/state.py#L182).

```python
async def release_owned(self, reason: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
After the runner cancelled this instance's jobs: record why, close anything left open.
```
