# jane_assistant.onboarding

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.onboarding.Session](#jane_assistantonboardingsession)
- [jane_assistant.onboarding.Session.__init__](#jane_assistantonboardingsession__init__)
- [jane_assistant.onboarding.Session.session_id](#jane_assistantonboardingsessionsession_id)
- [jane_assistant.onboarding.Session.query](#jane_assistantonboardingsessionquery)
- [jane_assistant.onboarding.Session.request](#jane_assistantonboardingsessionrequest)
- [jane_assistant.onboarding.Session.status](#jane_assistantonboardingsessionstatus)
- [jane_assistant.onboarding.Session.created_at](#jane_assistantonboardingsessioncreated_at)
- [jane_assistant.onboarding.Session.candidates](#jane_assistantonboardingsessioncandidates)
- [jane_assistant.onboarding.Session.selected_candidate_id](#jane_assistantonboardingsessionselected_candidate_id)
- [jane_assistant.onboarding.Session.sample](#jane_assistantonboardingsessionsample)
- [jane_assistant.onboarding.Session.analysis](#jane_assistantonboardingsessionanalysis)
- [jane_assistant.onboarding.Session.proposals](#jane_assistantonboardingsessionproposals)
- [jane_assistant.onboarding.Session.plans](#jane_assistantonboardingsessionplans)
- [jane_assistant.onboarding.Session.spent](#jane_assistantonboardingsessionspent)
- [jane_assistant.onboarding.Session.currency](#jane_assistantonboardingsessioncurrency)
- [jane_assistant.onboarding.Session.job_id](#jane_assistantonboardingsessionjob_id)
- [jane_assistant.onboarding.Session.error](#jane_assistantonboardingsessionerror)
- [jane_assistant.onboarding.Session.acceptance](#jane_assistantonboardingsessionacceptance)
- [jane_assistant.onboarding.Session.version](#jane_assistantonboardingsessionversion)
- [jane_assistant.onboarding.Session.to_doc](#jane_assistantonboardingsessionto_doc)
- [jane_assistant.onboarding.Session.from_doc](#jane_assistantonboardingsessionfrom_doc)
- [jane_assistant.onboarding.Session.candidate](#jane_assistantonboardingsessioncandidate)
- [jane_assistant.onboarding.Session.wire](#jane_assistantonboardingsessionwire)
- [jane_assistant.onboarding.Session.summary](#jane_assistantonboardingsessionsummary)
- [jane_assistant.onboarding.Session.position](#jane_assistantonboardingsessionposition)
- [jane_assistant.onboarding.SessionStore](#jane_assistantonboardingsessionstore)
- [jane_assistant.onboarding.SessionStore.get](#jane_assistantonboardingsessionstoreget)
- [jane_assistant.onboarding.SessionStore.save](#jane_assistantonboardingsessionstoresave)
- [jane_assistant.onboarding.SessionStore.save_if](#jane_assistantonboardingsessionstoresave_if)
- [jane_assistant.onboarding.SessionStore.page](#jane_assistantonboardingsessionstorepage)
- [jane_assistant.onboarding.InMemorySessionStore](#jane_assistantonboardinginmemorysessionstore)
- [jane_assistant.onboarding.InMemorySessionStore.__init__](#jane_assistantonboardinginmemorysessionstore__init__)
- [jane_assistant.onboarding.InMemorySessionStore.get](#jane_assistantonboardinginmemorysessionstoreget)
- [jane_assistant.onboarding.InMemorySessionStore.save](#jane_assistantonboardinginmemorysessionstoresave)
- [jane_assistant.onboarding.InMemorySessionStore.save_if](#jane_assistantonboardinginmemorysessionstoresave_if)
- [jane_assistant.onboarding.InMemorySessionStore.page](#jane_assistantonboardinginmemorysessionstorepage)
- [jane_assistant.onboarding.OnboardingService](#jane_assistantonboardingonboardingservice)
- [jane_assistant.onboarding.OnboardingService.__init__](#jane_assistantonboardingonboardingservice__init__)
- [jane_assistant.onboarding.OnboardingService.settings](#jane_assistantonboardingonboardingservicesettings)
- [jane_assistant.onboarding.OnboardingService.nb](#jane_assistantonboardingonboardingservicenb)
- [jane_assistant.onboarding.OnboardingService.search](#jane_assistantonboardingonboardingservicesearch)
- [jane_assistant.onboarding.OnboardingService.runner](#jane_assistantonboardingonboardingservicerunner)
- [jane_assistant.onboarding.OnboardingService.store](#jane_assistantonboardingonboardingservicestore)
- [jane_assistant.onboarding.OnboardingService.validator](#jane_assistantonboardingonboardingservicevalidator)
- [jane_assistant.onboarding.OnboardingService.start](#jane_assistantonboardingonboardingservicestart)
- [jane_assistant.onboarding.OnboardingService.get](#jane_assistantonboardingonboardingserviceget)
- [jane_assistant.onboarding.OnboardingService.page](#jane_assistantonboardingonboardingservicepage)
- [jane_assistant.onboarding.OnboardingService.select](#jane_assistantonboardingonboardingserviceselect)
- [jane_assistant.onboarding.OnboardingService.accept](#jane_assistantonboardingonboardingserviceaccept)

## jane_assistant.onboarding.Session

**Клас.** Код: [services/assistant/src/jane_assistant/onboarding.py:96](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L96).

```python
class Session:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [session_id](jane_assistant.onboarding.md#jane_assistantonboardingsessionsession_id) | Поле | ні |
| [query](jane_assistant.onboarding.md#jane_assistantonboardingsessionquery) | Поле | ні |
| [request](jane_assistant.onboarding.md#jane_assistantonboardingsessionrequest) | Поле | ні |
| [status](jane_assistant.onboarding.md#jane_assistantonboardingsessionstatus) | Поле | ні |
| [created_at](jane_assistant.onboarding.md#jane_assistantonboardingsessioncreated_at) | Поле | ні |
| [candidates](jane_assistant.onboarding.md#jane_assistantonboardingsessioncandidates) | Поле | ні |
| [selected_candidate_id](jane_assistant.onboarding.md#jane_assistantonboardingsessionselected_candidate_id) | Поле | ні |
| [sample](jane_assistant.onboarding.md#jane_assistantonboardingsessionsample) | Поле | ні |
| [analysis](jane_assistant.onboarding.md#jane_assistantonboardingsessionanalysis) | Поле | ні |
| [proposals](jane_assistant.onboarding.md#jane_assistantonboardingsessionproposals) | Поле | ні |
| [plans](jane_assistant.onboarding.md#jane_assistantonboardingsessionplans) | Поле | ні |
| [spent](jane_assistant.onboarding.md#jane_assistantonboardingsessionspent) | Поле | ні |
| [currency](jane_assistant.onboarding.md#jane_assistantonboardingsessioncurrency) | Поле | ні |
| [job_id](jane_assistant.onboarding.md#jane_assistantonboardingsessionjob_id) | Поле | ні |
| [error](jane_assistant.onboarding.md#jane_assistantonboardingsessionerror) | Поле | ні |
| [acceptance](jane_assistant.onboarding.md#jane_assistantonboardingsessionacceptance) | Поле | ні |
| [version](jane_assistant.onboarding.md#jane_assistantonboardingsessionversion) | Поле | ні |
| [to_doc](jane_assistant.onboarding.md#jane_assistantonboardingsessionto_doc) | Метод | ні |
| [from_doc](jane_assistant.onboarding.md#jane_assistantonboardingsessionfrom_doc) | Метод | ні |
| [candidate](jane_assistant.onboarding.md#jane_assistantonboardingsessioncandidate) | Метод | ні |
| [wire](jane_assistant.onboarding.md#jane_assistantonboardingsessionwire) | Метод | ні |
| [summary](jane_assistant.onboarding.md#jane_assistantonboardingsessionsummary) | Метод | ні |
| [position](jane_assistant.onboarding.md#jane_assistantonboardingsessionposition) | Властивість | ні |
| [__init__](jane_assistant.onboarding.md#jane_assistantonboardingsession__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:200](../../../../../../services/assistant/tests/test_lists.py#L200).

```python
session = Session(
        session_id="onb_dead1", query="https://shop.example.test/", request={}, status="sampling"
    )
```

Контекст і передумови: [services/assistant/tests/test_state.py:414](../../../../../../services/assistant/tests/test_state.py#L414).

```python
session = Session(
                session_id="onb_dead2", query="https://shop.example.test/", request={}, status="sampling"
            )
```

## jane_assistant.onboarding.Session.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/onboarding.py:96](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L96).

```python
def __init__(self, session_id: str, query: str, request: dict[str, Any], status: str = 'resolving', created_at: str = <factory _now>, candidates: list[Candidate] = <factory list>, selected_candidate_id: str | None = None, sample: SampleResult | None = None, analysis: dict[str, Any] | None = None, proposals: list[dict[str, Any]] = <factory list>, plans: dict[str, ExtractorPlan] = <factory dict>, spent: float = 0.0, currency: str = 'USD', job_id: str | None = None, error: dict[str, Any] | None = None, acceptance: dict[str, Any] | None = None, version: int = 0) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `session_id` | `str` | `—` | positional-or-keyword |
| `query` | `str` | `—` | positional-or-keyword |
| `request` | `dict[str, Any]` | `—` | positional-or-keyword |
| `status` | `str` | `'resolving'` | positional-or-keyword |
| `created_at` | `str` | `factory: _now` | positional-or-keyword |
| `candidates` | `list[Candidate]` | `factory: list` | positional-or-keyword |
| `selected_candidate_id` | `str \| None` | `None` | positional-or-keyword |
| `sample` | `SampleResult \| None` | `None` | positional-or-keyword |
| `analysis` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `proposals` | `list[dict[str, Any]]` | `factory: list` | positional-or-keyword |
| `plans` | `dict[str, ExtractorPlan]` | `factory: dict` | positional-or-keyword |
| `spent` | `float` | `0.0` | positional-or-keyword |
| `currency` | `str` | `'USD'` | positional-or-keyword |
| `job_id` | `str \| None` | `None` | positional-or-keyword |
| `error` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `acceptance` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `version` | `int` | `0` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:200](../../../../../../services/assistant/tests/test_lists.py#L200).

```python
session = Session(
        session_id="onb_dead1", query="https://shop.example.test/", request={}, status="sampling"
    )
```

Контекст і передумови: [services/assistant/tests/test_state.py:414](../../../../../../services/assistant/tests/test_state.py#L414).

```python
session = Session(
                session_id="onb_dead2", query="https://shop.example.test/", request={}, status="sampling"
            )
```

## jane_assistant.onboarding.Session.session_id

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:97](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L97).

```python
session_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.query

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:98](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L98).

```python
query: str
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.request

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:99](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L99).

```python
request: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.status

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:100](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L100).

```python
status: str = 'resolving'
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:323](../../../../../../services/assistant/tests/test_units.py#L323).

```python
s.status = "sampling"
```

## jane_assistant.onboarding.Session.created_at

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:101](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L101).

```python
created_at: str = field(default_factory=_now)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "_now"
}
```

## jane_assistant.onboarding.Session.candidates

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:102](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L102).

```python
candidates: list[Candidate] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.onboarding.Session.selected_candidate_id

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:103](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L103).

```python
selected_candidate_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.sample

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:104](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L104).

```python
sample: SampleResult | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.analysis

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:105](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L105).

```python
analysis: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.proposals

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:106](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L106).

```python
proposals: list[dict[str, Any]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.onboarding.Session.plans

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:107](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L107).

```python
plans: dict[str, ExtractorPlan] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.onboarding.Session.spent

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:108](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L108).

```python
spent: float = 0.0
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.currency

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:109](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L109).

```python
currency: str = 'USD'
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.job_id

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:110](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L110).

```python
job_id: str | None = None
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:203](../../../../../../services/assistant/tests/test_lists.py#L203).

```python
session.job_id = job.job_id
```

Контекст і передумови: [services/assistant/tests/test_state.py:417](../../../../../../services/assistant/tests/test_state.py#L417).

```python
session.job_id = "job_dead2"
```

## jane_assistant.onboarding.Session.error

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:111](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L111).

```python
error: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.acceptance

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:112](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L112).

```python
acceptance: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.onboarding.Session.version

**Поле.** Код: [services/assistant/src/jane_assistant/onboarding.py:113](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L113).

```python
version: int = 0
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Optimistic concurrency version of the stored session (set by the store).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:320](../../../../../../services/assistant/tests/test_units.py#L320).

```python
assert asyncio.run(store.save_if(s, 0)) and s.version == 1
```

Контекст і передумови: [services/assistant/tests/test_units.py:324](../../../../../../services/assistant/tests/test_units.py#L324).

```python
assert asyncio.run(store.save_if(s, 1)) and s.version == 2
```

## jane_assistant.onboarding.Session.to_doc

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:116](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L116).

```python
def to_doc(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
JSON document of the whole session (shared state of all instances).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:315](../../../../../../services/assistant/tests/test_units.py#L315).

```python
assert back.to_doc() == s.to_doc() and back.version == 3
```

Контекст і передумови: [services/assistant/tests/test_units.py:314](../../../../../../services/assistant/tests/test_units.py#L314).

```python
back = Session.from_doc(json.loads(json.dumps(s.to_doc())), 3)
```

## jane_assistant.onboarding.Session.from_doc

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:138](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L138).

```python
def from_doc(cls, doc: dict[str, Any], version: int=0) -> Session:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |
| `version` | `int` | `0` | positional-or-keyword |

Результат: `Session`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:314](../../../../../../services/assistant/tests/test_units.py#L314).

```python
back = Session.from_doc(json.loads(json.dumps(s.to_doc())), 3)
```

## jane_assistant.onboarding.Session.candidate

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:168](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L168).

```python
def candidate(self) -> Candidate | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Candidate | None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:317](../../../../../../services/assistant/tests/test_units.py#L317).

```python
assert back.candidate() == s.candidate()
```

## jane_assistant.onboarding.Session.wire

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:174](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L174).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.onboarding.Session.summary

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:199](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L199).

```python
def summary(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``OnboardingSessionSummary`` (``listOnboardingSessions``).
```

## jane_assistant.onboarding.Session.position

**Властивість.** Код: [services/assistant/src/jane_assistant/onboarding.py:210](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L210).

```python
def position(self) -> Position:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Position`.

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Sort key of the list (newest first): ``created_at`` as UTC time, then ``session_id``.
```

## jane_assistant.onboarding.SessionStore

**Клас.** Код: [services/assistant/src/jane_assistant/onboarding.py:250](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L250).

```python
class SessionStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [get](jane_assistant.onboarding.md#jane_assistantonboardingsessionstoreget) | Метод | ні |
| [save](jane_assistant.onboarding.md#jane_assistantonboardingsessionstoresave) | Метод | ні |
| [save_if](jane_assistant.onboarding.md#jane_assistantonboardingsessionstoresave_if) | Метод | ні |
| [page](jane_assistant.onboarding.md#jane_assistantonboardingsessionstorepage) | Метод | ні |

### Опис із вихідного коду

```text
Sessions shared by instances. ``save`` always writes (the job that owns a running session);
``save_if`` writes only if the stored version is still ``expected`` (API state transitions).
```

## jane_assistant.onboarding.SessionStore.get

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:254](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L254).

```python
async def get(self, session_id: str) -> Session | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session_id` | `str` | `—` | positional-or-keyword |

Результат: `Session | None`.

## jane_assistant.onboarding.SessionStore.save

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:255](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L255).

```python
async def save(self, session: Session) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session` | `Session` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.onboarding.SessionStore.save_if

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:256](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L256).

```python
async def save_if(self, session: Session, expected: int) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session` | `Session` | `—` | positional-or-keyword |
| `expected` | `int` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_assistant.onboarding.SessionStore.page

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:257](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L257).

```python
async def page(self, *, statuses: frozenset[str] | None, after: Position | None, limit: int) -> list[Session]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `statuses` | `frozenset[str] \| None` | `—` | keyword-only |
| `after` | `Position \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `list[Session]`.

### Опис із вихідного коду

```text
Newest first by :attr:`Session.position`, strictly after the ``after`` position (the cursor),
filtered by the **stored** status.
```

## jane_assistant.onboarding.InMemorySessionStore

**Клас.** Код: [services/assistant/src/jane_assistant/onboarding.py:265](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L265).

```python
class InMemorySessionStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.onboarding.md#jane_assistantonboardinginmemorysessionstore__init__) | Конструктор | ні |
| [get](jane_assistant.onboarding.md#jane_assistantonboardinginmemorysessionstoreget) | Метод | ні |
| [save](jane_assistant.onboarding.md#jane_assistantonboardinginmemorysessionstoresave) | Метод | ні |
| [save_if](jane_assistant.onboarding.md#jane_assistantonboardinginmemorysessionstoresave_if) | Метод | ні |
| [page](jane_assistant.onboarding.md#jane_assistantonboardinginmemorysessionstorepage) | Метод | ні |

### Опис із вихідного коду

```text
Single standalone instance and tests only (lost on restart). Several instances use
:class:`jane_assistant.state.PostgresState` (``JANE_ASSISTANT_STATE_DSN``). Stores serialized
documents, so it behaves like the shared store (copies, versions).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:319](../../../../../../services/assistant/tests/test_units.py#L319).

```python
store = InMemorySessionStore()
```

## jane_assistant.onboarding.InMemorySessionStore.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/onboarding.py:270](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L270).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:319](../../../../../../services/assistant/tests/test_units.py#L319).

```python
store = InMemorySessionStore()
```

## jane_assistant.onboarding.InMemorySessionStore.get

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:273](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L273).

```python
async def get(self, session_id: str) -> Session | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session_id` | `str` | `—` | positional-or-keyword |

Результат: `Session | None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:321](../../../../../../services/assistant/tests/test_units.py#L321).

```python
stale = asyncio.run(store.get("onb_1"))
```

Контекст і передумови: [services/assistant/tests/test_units.py:327](../../../../../../services/assistant/tests/test_units.py#L327).

```python
current = asyncio.run(store.get("onb_1"))
```

## jane_assistant.onboarding.InMemorySessionStore.save

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:277](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L277).

```python
async def save(self, session: Session) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session` | `Session` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.onboarding.InMemorySessionStore.save_if

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:282](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L282).

```python
async def save_if(self, session: Session, expected: int) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session` | `Session` | `—` | positional-or-keyword |
| `expected` | `int` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:320](../../../../../../services/assistant/tests/test_units.py#L320).

```python
assert asyncio.run(store.save_if(s, 0)) and s.version == 1
```

Контекст і передумови: [services/assistant/tests/test_units.py:324](../../../../../../services/assistant/tests/test_units.py#L324).

```python
assert asyncio.run(store.save_if(s, 1)) and s.version == 2
```

## jane_assistant.onboarding.InMemorySessionStore.page

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:288](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L288).

```python
async def page(self, *, statuses: frozenset[str] | None, after: Position | None, limit: int) -> list[Session]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `statuses` | `frozenset[str] \| None` | `—` | keyword-only |
| `after` | `Position \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `list[Session]`.

## jane_assistant.onboarding.OnboardingService

**Клас.** Код: [services/assistant/src/jane_assistant/onboarding.py:310](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L310).

```python
class OnboardingService:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservice__init__) | Конструктор | ні |
| [settings](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicesettings) | Поле екземпляра | ні |
| [nb](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicenb) | Поле екземпляра | ні |
| [search](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicesearch) | Поле екземпляра | ні |
| [runner](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicerunner) | Поле екземпляра | ні |
| [store](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicestore) | Поле екземпляра | ні |
| [validator](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicevalidator) | Поле екземпляра | ні |
| [start](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicestart) | Метод | ні |
| [get](jane_assistant.onboarding.md#jane_assistantonboardingonboardingserviceget) | Метод | ні |
| [page](jane_assistant.onboarding.md#jane_assistantonboardingonboardingservicepage) | Метод | ні |
| [select](jane_assistant.onboarding.md#jane_assistantonboardingonboardingserviceselect) | Метод | ні |
| [accept](jane_assistant.onboarding.md#jane_assistantonboardingonboardingserviceaccept) | Метод | ні |

## jane_assistant.onboarding.OnboardingService.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/onboarding.py:311](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L311).

```python
def __init__(self, *, settings: Settings, neighbours: Neighbours, search: SearchProvider, runner: JobRunner, store: SessionStore, validator: SchemaValidator) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | keyword-only |
| `neighbours` | `Neighbours` | `—` | keyword-only |
| `search` | `SearchProvider` | `—` | keyword-only |
| `runner` | `JobRunner` | `—` | keyword-only |
| `store` | `SessionStore` | `—` | keyword-only |
| `validator` | `SchemaValidator` | `—` | keyword-only |

Результат: `None`.

## jane_assistant.onboarding.OnboardingService.settings

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:321](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L321).

```python
self.settings = settings
```

## jane_assistant.onboarding.OnboardingService.nb

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:322](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L322).

```python
self.nb = neighbours
```

## jane_assistant.onboarding.OnboardingService.search

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:323](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L323).

```python
self.search = search
```

## jane_assistant.onboarding.OnboardingService.runner

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:324](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L324).

```python
self.runner = runner
```

## jane_assistant.onboarding.OnboardingService.store

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:325](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L325).

```python
self.store = store
```

## jane_assistant.onboarding.OnboardingService.validator

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/onboarding.py:326](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L326).

```python
self.validator = validator
```

## jane_assistant.onboarding.OnboardingService.start

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:329](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L329).

```python
async def start(self, request: dict[str, Any], idempotency_key: str | None) -> tuple[dict[str, Any], str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `request` | `dict[str, Any]` | `—` | positional-or-keyword |
| `idempotency_key` | `str \| None` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], str]`.

## jane_assistant.onboarding.OnboardingService.get

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:340](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L340).

```python
async def get(self, session_id: str) -> Session:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session_id` | `str` | `—` | positional-or-keyword |

Результат: `Session`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_assistant.onboarding.OnboardingService.page

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:346](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L346).

```python
async def page(self, statuses: frozenset[str] | None, after: Position | None, limit: int) -> tuple[list[Session], Position | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `statuses` | `frozenset[str] \| None` | `—` | positional-or-keyword |
| `after` | `Position \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[Session], Position | None]`.

### Опис із вихідного коду

```text
One page of ``listOnboardingSessions`` (newest first) and the position after it (``None`` = last page).

Running sessions are settled first, as ``GET`` does for one session (a job that ended without its handler
updating the session: cancelled before it started, failed because its instance stopped), so the stored
status the page is filtered by is the status ``GET`` reports - a session of a dead job is listed under
``failed``, not ``sampling``.
```

## jane_assistant.onboarding.OnboardingService.select

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:370](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L370).

```python
async def select(self, session_id: str, candidate_id: str) -> Session:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session_id` | `str` | `—` | positional-or-keyword |
| `candidate_id` | `str` | `—` | positional-or-keyword |

Результат: `Session`.

Явні `raise` у тілі: `Conflict`, `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_assistant.onboarding.OnboardingService.accept

**Метод.** Код: [services/assistant/src/jane_assistant/onboarding.py:391](../../../../../../services/assistant/src/jane_assistant/onboarding.py#L391).

```python
async def accept(self, session_id: str, proposal_id: str, activate: bool, source_id: str | None, idempotency_key: str | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `session_id` | `str` | `—` | positional-or-keyword |
| `proposal_id` | `str` | `—` | positional-or-keyword |
| `activate` | `bool` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `idempotency_key` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `Conflict`, `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.
