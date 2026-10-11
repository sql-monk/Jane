# Модуль `jane_assistant.onboarding`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/onboarding.py](../../../../../services/assistant/src/jane_assistant/onboarding.py). Не редагуйте вручну.

Onboarding of a new source (ТЗ §8, §13.1 п.2, plan.md WP-11 «Підключення»).

States (``assistant.v1`` ``OnboardingSession.status``)::

    resolving -> needs_disambiguation --(candidate-selection)--> sampling
    resolving -> sampling -> analyzing -> proposals_ready --(acceptance)--> applying -> completed
                          \-> insufficient_sample
    any running state -> failed | cancelled

* resolving: a URL/@channel is taken as is; a name goes to the search provider; a clear winner is selected automatically, otherwise the user chooses.
* sampling: adaptive (see :mod:`jane_assistant.sampling`).
* analyzing: material types, entities and fields; for every entity type existing extractors are searched in the registry and tested on the samples (bind / fork+adapt / create), new code is generated and tested; then several collection plans with coverage, cost and risks.
* acceptance: publishes rules and packages (``draft``), records test reports and returns source and task drafts. With ``activate: true`` (or ``auto_activation`` in the request, which accepts the recommended plan) and all tests passing, versions are approved and the source and task are created in the orchestrator.

## Зміст

- [Клас `InMemorySessionStore`](#клас-inmemorysessionstore)
- [Клас `OnboardingService`](#клас-onboardingservice)
- [Клас `Session`](#клас-session)
- [Клас `SessionStore`](#клас-sessionstore)

## Класи

### Клас `InMemorySessionStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.onboarding` |
| Код | [onboarding.py:265](../../../../../services/assistant/src/jane_assistant/onboarding.py#L265) |

```python
class InMemorySessionStore: ...
```

Single standalone instance and tests only (lost on restart). Several instances use :class:`jane_assistant.state.PostgresState` (``JANE_ASSISTANT_STATE_DSN``). Stores serialized documents, so it behaves like the shared store (copies, versions).

#### Конструктор `InMemorySessionStore.__init__`

```python
def __init__(self) -> None: ...
```

Код: [onboarding.py:270](../../../../../services/assistant/src/jane_assistant/onboarding.py#L270).

#### Метод `InMemorySessionStore.get`

```python
async def get(self, session_id: str) -> Session | None: ...
```

Код: [onboarding.py:273](../../../../../services/assistant/src/jane_assistant/onboarding.py#L273).

#### Метод `InMemorySessionStore.save`

```python
async def save(self, session: Session) -> None: ...
```

Код: [onboarding.py:277](../../../../../services/assistant/src/jane_assistant/onboarding.py#L277).

#### Метод `InMemorySessionStore.save_if`

```python
async def save_if(self, session: Session, expected: int) -> bool: ...
```

Код: [onboarding.py:282](../../../../../services/assistant/src/jane_assistant/onboarding.py#L282).

#### Метод `InMemorySessionStore.page`

```python
async def page(
    self,
    *,
    statuses: frozenset[str] | None,
    after: Position | None,
    limit: int,
) -> list[Session]: ...
```

Код: [onboarding.py:288](../../../../../services/assistant/src/jane_assistant/onboarding.py#L288).

### Клас `OnboardingService`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.onboarding` |
| Код | [onboarding.py:310](../../../../../services/assistant/src/jane_assistant/onboarding.py#L310) |

```python
class OnboardingService: ...
```

#### Конструктор `OnboardingService.__init__`

```python
def __init__(
    self,
    *,
    settings: Settings,
    neighbours: Neighbours,
    search: SearchProvider,
    runner: JobRunner,
    store: SessionStore,
    validator: SchemaValidator,
) -> None: ...
```

Код: [onboarding.py:311](../../../../../services/assistant/src/jane_assistant/onboarding.py#L311).

#### Метод `OnboardingService.start`

```python
async def start(
    self,
    request: dict[str, Any],
    idempotency_key: str | None,
) -> tuple[dict[str, Any], str]: ...
```

Код: [onboarding.py:329](../../../../../services/assistant/src/jane_assistant/onboarding.py#L329).

#### Метод `OnboardingService.get`

```python
async def get(self, session_id: str) -> Session: ...
```

Винятки в коді методу: `NotFound`.

Код: [onboarding.py:340](../../../../../services/assistant/src/jane_assistant/onboarding.py#L340).

#### Метод `OnboardingService.page`

```python
async def page(
    self,
    statuses: frozenset[str] | None,
    after: Position | None,
    limit: int,
) -> tuple[list[Session], Position | None]: ...
```

One page of ``listOnboardingSessions`` (newest first) and the position after it (``None`` = last page).

Running sessions are settled first, as ``GET`` does for one session (a job that ended without its handler updating the session: cancelled before it started, failed because its instance stopped), so the stored status the page is filtered by is the status ``GET`` reports - a session of a dead job is listed under ``failed``, not ``sampling``.

Код: [onboarding.py:346](../../../../../services/assistant/src/jane_assistant/onboarding.py#L346).

#### Метод `OnboardingService.select`

```python
async def select(self, session_id: str, candidate_id: str) -> Session: ...
```

Винятки в коді методу: `Conflict`, `NotFound`.

Код: [onboarding.py:370](../../../../../services/assistant/src/jane_assistant/onboarding.py#L370).

#### Метод `OnboardingService.accept`

```python
async def accept(
    self,
    session_id: str,
    proposal_id: str,
    activate: bool,
    source_id: str | None,
    idempotency_key: str | None,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `Conflict`, `NotFound`.

Код: [onboarding.py:391](../../../../../services/assistant/src/jane_assistant/onboarding.py#L391).

### Клас `Session`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.onboarding` |
| Код | [onboarding.py:96](../../../../../services/assistant/src/jane_assistant/onboarding.py#L96) |

```python
@dataclass
class Session: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `session_id` | `str` | — | читання й запис |  |
| `query` | `str` | — | читання й запис |  |
| `request` | `dict[str, Any]` | — | читання й запис |  |
| `status` | `str` | `'resolving'` | читання й запис |  |
| `created_at` | `str` | `field(default_factory=_now)` | читання й запис |  |
| `candidates` | `list[Candidate]` | `field(default_factory=list)` | читання й запис |  |
| `selected_candidate_id` | `str \| None` | `None` | читання й запис |  |
| `sample` | `SampleResult \| None` | `None` | читання й запис |  |
| `analysis` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `proposals` | `list[dict[str, Any]]` | `field(default_factory=list)` | читання й запис |  |
| `plans` | `dict[str, ExtractorPlan]` | `field(default_factory=dict)` | читання й запис |  |
| `spent` | `float` | `0.0` | читання й запис |  |
| `currency` | `str` | `'USD'` | читання й запис |  |
| `job_id` | `str \| None` | `None` | читання й запис |  |
| `error` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `acceptance` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `version` | `int` | `0` | читання й запис | Optimistic concurrency version of the stored session (set by the store). |
| `position` | `Position` | — | читання (властивість) | Sort key of the list (newest first): ``created_at`` as UTC time, then ``session_id``. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Session.to_doc`

```python
def to_doc(self) -> dict[str, Any]: ...
```

JSON document of the whole session (shared state of all instances).

Код: [onboarding.py:116](../../../../../services/assistant/src/jane_assistant/onboarding.py#L116).

#### Метод `Session.from_doc`

```python
@classmethod
def from_doc(cls, doc: dict[str, Any], version: int = 0) -> Session: ...
```

Код: [onboarding.py:138](../../../../../services/assistant/src/jane_assistant/onboarding.py#L138).

#### Метод `Session.candidate`

```python
def candidate(self) -> Candidate | None: ...
```

Код: [onboarding.py:168](../../../../../services/assistant/src/jane_assistant/onboarding.py#L168).

#### Метод `Session.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [onboarding.py:174](../../../../../services/assistant/src/jane_assistant/onboarding.py#L174).

#### Метод `Session.summary`

```python
def summary(self) -> dict[str, Any]: ...
```

``OnboardingSessionSummary`` (``listOnboardingSessions``).

Код: [onboarding.py:199](../../../../../services/assistant/src/jane_assistant/onboarding.py#L199).

### Клас `SessionStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_assistant.onboarding` |
| Успадкування | `Protocol` |
| Код | [onboarding.py:250](../../../../../services/assistant/src/jane_assistant/onboarding.py#L250) |

```python
class SessionStore(Protocol): ...
```

Sessions shared by instances. ``save`` always writes (the job that owns a running session); ``save_if`` writes only if the stored version is still ``expected`` (API state transitions).

#### Метод `SessionStore.get`

```python
async def get(self, session_id: str) -> Session | None: ...
```

Код: [onboarding.py:254](../../../../../services/assistant/src/jane_assistant/onboarding.py#L254).

#### Метод `SessionStore.save`

```python
async def save(self, session: Session) -> None: ...
```

Код: [onboarding.py:255](../../../../../services/assistant/src/jane_assistant/onboarding.py#L255).

#### Метод `SessionStore.save_if`

```python
async def save_if(self, session: Session, expected: int) -> bool: ...
```

Код: [onboarding.py:256](../../../../../services/assistant/src/jane_assistant/onboarding.py#L256).

#### Метод `SessionStore.page`

```python
async def page(
    self,
    *,
    statuses: frozenset[str] | None,
    after: Position | None,
    limit: int,
) -> list[Session]: ...
```

Newest first by :attr:`Session.position`, strictly after the ``after`` position (the cursor), filtered by the **stored** status.

Код: [onboarding.py:257](../../../../../services/assistant/src/jane_assistant/onboarding.py#L257).
