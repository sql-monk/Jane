# jane_assistant.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.app.log](#jane_assistantapplog)
- [jane_assistant.app.SLUG](#jane_assistantappslug)
- [jane_assistant.app.SEMVER](#jane_assistantappsemver)
- [jane_assistant.app.SessionStatus](#jane_assistantappsessionstatus)
- [jane_assistant.app.STATUS_QUERY](#jane_assistantappstatus_query)
- [jane_assistant.app.LIST_SCOPES](#jane_assistantapplist_scopes)
- [jane_assistant.app.OnboardingRequest](#jane_assistantapponboardingrequest)
- [jane_assistant.app.OnboardingRequest.query](#jane_assistantapponboardingrequestquery)
- [jane_assistant.app.OnboardingRequest.source_kind](#jane_assistantapponboardingrequestsource_kind)
- [jane_assistant.app.OnboardingRequest.expected_entity_types](#jane_assistantapponboardingrequestexpected_entity_types)
- [jane_assistant.app.OnboardingRequest.crawl_hints](#jane_assistantapponboardingrequestcrawl_hints)
- [jane_assistant.app.OnboardingRequest.limits](#jane_assistantapponboardingrequestlimits)
- [jane_assistant.app.OnboardingRequest.auto_activation](#jane_assistantapponboardingrequestauto_activation)
- [jane_assistant.app.CandidateSelection](#jane_assistantappcandidateselection)
- [jane_assistant.app.CandidateSelection.candidate_id](#jane_assistantappcandidateselectioncandidate_id)
- [jane_assistant.app.AcceptanceRequest](#jane_assistantappacceptancerequest)
- [jane_assistant.app.AcceptanceRequest.activate](#jane_assistantappacceptancerequestactivate)
- [jane_assistant.app.AcceptanceRequest.source_id](#jane_assistantappacceptancerequestsource_id)
- [jane_assistant.app.PackageRef](#jane_assistantapppackageref)
- [jane_assistant.app.PackageRef.package_id](#jane_assistantapppackagerefpackage_id)
- [jane_assistant.app.PackageRef.version](#jane_assistantapppackagerefversion)
- [jane_assistant.app.PackageRef.digest](#jane_assistantapppackagerefdigest)
- [jane_assistant.app.MaterialRef](#jane_assistantappmaterialref)
- [jane_assistant.app.MaterialRef.storage_connection_id](#jane_assistantappmaterialrefstorage_connection_id)
- [jane_assistant.app.MaterialRef.object_id](#jane_assistantappmaterialrefobject_id)
- [jane_assistant.app.ProblemSample](#jane_assistantappproblemsample)
- [jane_assistant.app.ProblemSample.material](#jane_assistantappproblemsamplematerial)
- [jane_assistant.app.ProblemSample.material_ref](#jane_assistantappproblemsamplematerial_ref)
- [jane_assistant.app.ProblemSample.result](#jane_assistantappproblemsampleresult)
- [jane_assistant.app.ProblemSample.diagnostics](#jane_assistantappproblemsamplediagnostics)
- [jane_assistant.app.BindingRef](#jane_assistantappbindingref)
- [jane_assistant.app.BindingRef.task_id](#jane_assistantappbindingreftask_id)
- [jane_assistant.app.BindingRef.stage_id](#jane_assistantappbindingrefstage_id)
- [jane_assistant.app.Policy](#jane_assistantapppolicy)
- [jane_assistant.app.Policy.approval](#jane_assistantapppolicyapproval)
- [jane_assistant.app.Policy.allow_fork](#jane_assistantapppolicyallow_fork)
- [jane_assistant.app.ImprovementRequest](#jane_assistantappimprovementrequest)
- [jane_assistant.app.ImprovementRequest.package](#jane_assistantappimprovementrequestpackage)
- [jane_assistant.app.ImprovementRequest.source_id](#jane_assistantappimprovementrequestsource_id)
- [jane_assistant.app.ImprovementRequest.problem_group_id](#jane_assistantappimprovementrequestproblem_group_id)
- [jane_assistant.app.ImprovementRequest.problem_samples](#jane_assistantappimprovementrequestproblem_samples)
- [jane_assistant.app.ImprovementRequest.successful_examples](#jane_assistantappimprovementrequestsuccessful_examples)
- [jane_assistant.app.ImprovementRequest.bindings](#jane_assistantappimprovementrequestbindings)
- [jane_assistant.app.ImprovementRequest.policy](#jane_assistantappimprovementrequestpolicy)
- [jane_assistant.app.ImprovementRequest.limits](#jane_assistantappimprovementrequestlimits)
- [jane_assistant.app.UnknownMaterialRequest](#jane_assistantappunknownmaterialrequest)
- [jane_assistant.app.UnknownMaterialRequest.source_id](#jane_assistantappunknownmaterialrequestsource_id)
- [jane_assistant.app.UnknownMaterialRequest.task_id](#jane_assistantappunknownmaterialrequesttask_id)
- [jane_assistant.app.UnknownMaterialRequest.forward_unknown_to_llm](#jane_assistantappunknownmaterialrequestforward_unknown_to_llm)
- [jane_assistant.app.UnknownMaterialRequest.material](#jane_assistantappunknownmaterialrequestmaterial)
- [jane_assistant.app.UnknownMaterialRequest.limits](#jane_assistantappunknownmaterialrequestlimits)
- [jane_assistant.app.Dependencies](#jane_assistantappdependencies)
- [jane_assistant.app.Dependencies.__init__](#jane_assistantappdependencies__init__)
- [jane_assistant.app.Dependencies.transports](#jane_assistantappdependenciestransports)
- [jane_assistant.app.Dependencies.search](#jane_assistantappdependenciessearch)
- [jane_assistant.app.Dependencies.state](#jane_assistantappdependenciesstate)
- [jane_assistant.app.build_state](#jane_assistantappbuild_state)
- [jane_assistant.app.build_search](#jane_assistantappbuild_search)
- [jane_assistant.app.build_app](#jane_assistantappbuild_app)

## jane_assistant.app.log

**Змінна.** Код: [services/assistant/src/jane_assistant/app.py:41](../../../../../../services/assistant/src/jane_assistant/app.py#L41).

```python
log = logging.getLogger(__name__)
```

## jane_assistant.app.SLUG

**Константа.** Код: [services/assistant/src/jane_assistant/app.py:43](../../../../../../services/assistant/src/jane_assistant/app.py#L43).

```python
SLUG = '^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'
```

## jane_assistant.app.SEMVER

**Константа.** Код: [services/assistant/src/jane_assistant/app.py:44](../../../../../../services/assistant/src/jane_assistant/app.py#L44).

```python
SEMVER = '^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$'
```

## jane_assistant.app.SessionStatus

**Змінна.** Код: [services/assistant/src/jane_assistant/app.py:47](../../../../../../services/assistant/src/jane_assistant/app.py#L47).

```python
SessionStatus = Literal['resolving', 'needs_disambiguation', 'sampling', 'analyzing', 'proposals_ready', 'insufficient_sample', 'applying', 'completed', 'failed', 'cancelled']
```

### Опис із вихідного коду

```text
``OnboardingStatus`` of the contract.
```

## jane_assistant.app.STATUS_QUERY

**Константа.** Код: [services/assistant/src/jane_assistant/app.py:61](../../../../../../services/assistant/src/jane_assistant/app.py#L61).

```python
STATUS_QUERY = Query(default=None)
```

### Опис із вихідного коду

```text
``?status=`` may repeat (a list); one module-level default (ruff B008).
```

## jane_assistant.app.LIST_SCOPES

**Константа.** Код: [services/assistant/src/jane_assistant/app.py:64](../../../../../../services/assistant/src/jane_assistant/app.py#L64).

```python
LIST_SCOPES = {'GET /v1/onboarding-sessions': 'assistant:use', 'GET /v1/improvement-runs': 'assistant:use'}
```

### Опис із вихідного коду

```text
Scopes of the list operations added by WP-15 (R24) until ``jane_kit.auth_scopes.ASSISTANT`` lists them; merging
is idempotent, so the table stays right after jane-kit adds them.
```

## jane_assistant.app.OnboardingRequest

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:76](../../../../../../services/assistant/src/jane_assistant/app.py#L76).

```python
class OnboardingRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [query](jane_assistant.app.md#jane_assistantapponboardingrequestquery) | Поле | ні |
| [source_kind](jane_assistant.app.md#jane_assistantapponboardingrequestsource_kind) | Поле | ні |
| [expected_entity_types](jane_assistant.app.md#jane_assistantapponboardingrequestexpected_entity_types) | Поле | ні |
| [crawl_hints](jane_assistant.app.md#jane_assistantapponboardingrequestcrawl_hints) | Поле | ні |
| [limits](jane_assistant.app.md#jane_assistantapponboardingrequestlimits) | Поле | ні |
| [auto_activation](jane_assistant.app.md#jane_assistantapponboardingrequestauto_activation) | Поле | ні |

## jane_assistant.app.OnboardingRequest.query

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:77](../../../../../../services/assistant/src/jane_assistant/app.py#L77).

```python
query: str = Field(min_length=1, max_length=2000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "max_length": "2000",
  "min_length": "1"
}
```

## jane_assistant.app.OnboardingRequest.source_kind

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:78](../../../../../../services/assistant/src/jane_assistant/app.py#L78).

```python
source_kind: str | None = Field(default=None, pattern='^[a-z][a-z0-9_-]{1,31}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "'^[a-z][a-z0-9_-]{1,31}$'"
}
```

## jane_assistant.app.OnboardingRequest.expected_entity_types

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:79](../../../../../../services/assistant/src/jane_assistant/app.py#L79).

```python
expected_entity_types: list[str] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.OnboardingRequest.crawl_hints

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:80](../../../../../../services/assistant/src/jane_assistant/app.py#L80).

```python
crawl_hints: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.OnboardingRequest.limits

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:81](../../../../../../services/assistant/src/jane_assistant/app.py#L81).

```python
limits: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.OnboardingRequest.auto_activation

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:82](../../../../../../services/assistant/src/jane_assistant/app.py#L82).

```python
auto_activation: bool = False
```

Доступ: читання — так; запис — так.

## jane_assistant.app.CandidateSelection

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:85](../../../../../../services/assistant/src/jane_assistant/app.py#L85).

```python
class CandidateSelection(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [candidate_id](jane_assistant.app.md#jane_assistantappcandidateselectioncandidate_id) | Поле | ні |

## jane_assistant.app.CandidateSelection.candidate_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:86](../../../../../../services/assistant/src/jane_assistant/app.py#L86).

```python
candidate_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.AcceptanceRequest

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:89](../../../../../../services/assistant/src/jane_assistant/app.py#L89).

```python
class AcceptanceRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [activate](jane_assistant.app.md#jane_assistantappacceptancerequestactivate) | Поле | ні |
| [source_id](jane_assistant.app.md#jane_assistantappacceptancerequestsource_id) | Поле | ні |

## jane_assistant.app.AcceptanceRequest.activate

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:90](../../../../../../services/assistant/src/jane_assistant/app.py#L90).

```python
activate: bool = False
```

Доступ: читання — так; запис — так.

## jane_assistant.app.AcceptanceRequest.source_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:91](../../../../../../services/assistant/src/jane_assistant/app.py#L91).

```python
source_id: str | None = Field(default=None, pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "SLUG"
}
```

## jane_assistant.app.PackageRef

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:94](../../../../../../services/assistant/src/jane_assistant/app.py#L94).

```python
class PackageRef(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](jane_assistant.app.md#jane_assistantapppackagerefpackage_id) | Поле | ні |
| [version](jane_assistant.app.md#jane_assistantapppackagerefversion) | Поле | ні |
| [digest](jane_assistant.app.md#jane_assistantapppackagerefdigest) | Поле | ні |

## jane_assistant.app.PackageRef.package_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:95](../../../../../../services/assistant/src/jane_assistant/app.py#L95).

```python
package_id: str = Field(pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SLUG"
}
```

## jane_assistant.app.PackageRef.version

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:96](../../../../../../services/assistant/src/jane_assistant/app.py#L96).

```python
version: str = Field(pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SEMVER"
}
```

## jane_assistant.app.PackageRef.digest

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:97](../../../../../../services/assistant/src/jane_assistant/app.py#L97).

```python
digest: str | None = Field(default=None, pattern='^sha256:[a-f0-9]{64}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "'^sha256:[a-f0-9]{64}$'"
}
```

## jane_assistant.app.MaterialRef

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:100](../../../../../../services/assistant/src/jane_assistant/app.py#L100).

```python
class MaterialRef(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [storage_connection_id](jane_assistant.app.md#jane_assistantappmaterialrefstorage_connection_id) | Поле | ні |
| [object_id](jane_assistant.app.md#jane_assistantappmaterialrefobject_id) | Поле | ні |

## jane_assistant.app.MaterialRef.storage_connection_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:101](../../../../../../services/assistant/src/jane_assistant/app.py#L101).

```python
storage_connection_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.MaterialRef.object_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:102](../../../../../../services/assistant/src/jane_assistant/app.py#L102).

```python
object_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ProblemSample

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:105](../../../../../../services/assistant/src/jane_assistant/app.py#L105).

```python
class ProblemSample(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [material](jane_assistant.app.md#jane_assistantappproblemsamplematerial) | Поле | ні |
| [material_ref](jane_assistant.app.md#jane_assistantappproblemsamplematerial_ref) | Поле | ні |
| [result](jane_assistant.app.md#jane_assistantappproblemsampleresult) | Поле | ні |
| [diagnostics](jane_assistant.app.md#jane_assistantappproblemsamplediagnostics) | Поле | ні |

## jane_assistant.app.ProblemSample.material

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:106](../../../../../../services/assistant/src/jane_assistant/app.py#L106).

```python
material: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ProblemSample.material_ref

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:107](../../../../../../services/assistant/src/jane_assistant/app.py#L107).

```python
material_ref: MaterialRef | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ProblemSample.result

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:108](../../../../../../services/assistant/src/jane_assistant/app.py#L108).

```python
result: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ProblemSample.diagnostics

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:109](../../../../../../services/assistant/src/jane_assistant/app.py#L109).

```python
diagnostics: list[dict[str, Any]] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.BindingRef

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:118](../../../../../../services/assistant/src/jane_assistant/app.py#L118).

```python
class BindingRef(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [task_id](jane_assistant.app.md#jane_assistantappbindingreftask_id) | Поле | ні |
| [stage_id](jane_assistant.app.md#jane_assistantappbindingrefstage_id) | Поле | ні |

## jane_assistant.app.BindingRef.task_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:119](../../../../../../services/assistant/src/jane_assistant/app.py#L119).

```python
task_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.BindingRef.stage_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:120](../../../../../../services/assistant/src/jane_assistant/app.py#L120).

```python
stage_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.Policy

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:123](../../../../../../services/assistant/src/jane_assistant/app.py#L123).

```python
class Policy(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [approval](jane_assistant.app.md#jane_assistantapppolicyapproval) | Поле | ні |
| [allow_fork](jane_assistant.app.md#jane_assistantapppolicyallow_fork) | Поле | ні |

## jane_assistant.app.Policy.approval

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:124](../../../../../../services/assistant/src/jane_assistant/app.py#L124).

```python
approval: Literal['manual', 'auto_after_checks'] = 'manual'
```

Доступ: читання — так; запис — так.

## jane_assistant.app.Policy.allow_fork

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:125](../../../../../../services/assistant/src/jane_assistant/app.py#L125).

```python
allow_fork: bool = True
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:128](../../../../../../services/assistant/src/jane_assistant/app.py#L128).

```python
class ImprovementRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package](jane_assistant.app.md#jane_assistantappimprovementrequestpackage) | Поле | ні |
| [source_id](jane_assistant.app.md#jane_assistantappimprovementrequestsource_id) | Поле | ні |
| [problem_group_id](jane_assistant.app.md#jane_assistantappimprovementrequestproblem_group_id) | Поле | ні |
| [problem_samples](jane_assistant.app.md#jane_assistantappimprovementrequestproblem_samples) | Поле | ні |
| [successful_examples](jane_assistant.app.md#jane_assistantappimprovementrequestsuccessful_examples) | Поле | ні |
| [bindings](jane_assistant.app.md#jane_assistantappimprovementrequestbindings) | Поле | ні |
| [policy](jane_assistant.app.md#jane_assistantappimprovementrequestpolicy) | Поле | ні |
| [limits](jane_assistant.app.md#jane_assistantappimprovementrequestlimits) | Поле | ні |

## jane_assistant.app.ImprovementRequest.package

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:129](../../../../../../services/assistant/src/jane_assistant/app.py#L129).

```python
package: PackageRef
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.source_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:130](../../../../../../services/assistant/src/jane_assistant/app.py#L130).

```python
source_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.problem_group_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:131](../../../../../../services/assistant/src/jane_assistant/app.py#L131).

```python
problem_group_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.problem_samples

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:132](../../../../../../services/assistant/src/jane_assistant/app.py#L132).

```python
problem_samples: list[ProblemSample] = Field(min_length=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "min_length": "1"
}
```

## jane_assistant.app.ImprovementRequest.successful_examples

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:133](../../../../../../services/assistant/src/jane_assistant/app.py#L133).

```python
successful_examples: list[ProblemSample] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.bindings

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:134](../../../../../../services/assistant/src/jane_assistant/app.py#L134).

```python
bindings: list[BindingRef] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.policy

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:135](../../../../../../services/assistant/src/jane_assistant/app.py#L135).

```python
policy: Policy | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.ImprovementRequest.limits

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:136](../../../../../../services/assistant/src/jane_assistant/app.py#L136).

```python
limits: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.UnknownMaterialRequest

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:139](../../../../../../services/assistant/src/jane_assistant/app.py#L139).

```python
class UnknownMaterialRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [source_id](jane_assistant.app.md#jane_assistantappunknownmaterialrequestsource_id) | Поле | ні |
| [task_id](jane_assistant.app.md#jane_assistantappunknownmaterialrequesttask_id) | Поле | ні |
| [forward_unknown_to_llm](jane_assistant.app.md#jane_assistantappunknownmaterialrequestforward_unknown_to_llm) | Поле | ні |
| [material](jane_assistant.app.md#jane_assistantappunknownmaterialrequestmaterial) | Поле | ні |
| [limits](jane_assistant.app.md#jane_assistantappunknownmaterialrequestlimits) | Поле | ні |

## jane_assistant.app.UnknownMaterialRequest.source_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:140](../../../../../../services/assistant/src/jane_assistant/app.py#L140).

```python
source_id: str
```

Доступ: читання — так; запис — так.

## jane_assistant.app.UnknownMaterialRequest.task_id

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:141](../../../../../../services/assistant/src/jane_assistant/app.py#L141).

```python
task_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.UnknownMaterialRequest.forward_unknown_to_llm

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:142](../../../../../../services/assistant/src/jane_assistant/app.py#L142).

```python
forward_unknown_to_llm: bool
```

Доступ: читання — так; запис — так.

## jane_assistant.app.UnknownMaterialRequest.material

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:143](../../../../../../services/assistant/src/jane_assistant/app.py#L143).

```python
material: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_assistant.app.UnknownMaterialRequest.limits

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:144](../../../../../../services/assistant/src/jane_assistant/app.py#L144).

```python
limits: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.Dependencies

**Клас.** Код: [services/assistant/src/jane_assistant/app.py:148](../../../../../../services/assistant/src/jane_assistant/app.py#L148).

```python
class Dependencies:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [transports](jane_assistant.app.md#jane_assistantappdependenciestransports) | Поле | ні |
| [search](jane_assistant.app.md#jane_assistantappdependenciessearch) | Поле | ні |
| [state](jane_assistant.app.md#jane_assistantappdependenciesstate) | Поле | ні |
| [__init__](jane_assistant.app.md#jane_assistantappdependencies__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Replaceable collaborators (tests pass ASGI transports of contract fakes and a fake search).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:92](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L92).

```python
deps = Dependencies(transports=self.extra["transports"], search=self.search)
```

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:137](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L137).

```python
app = build_app(settings, Dependencies(transports=transports, search=fake_search))
```

## jane_assistant.app.Dependencies.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/app.py:148](../../../../../../services/assistant/src/jane_assistant/app.py#L148).

```python
def __init__(self, transports: Mapping[str, httpx.AsyncBaseTransport] | None = None, search: SearchProvider | None = None, state: ServiceState | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `transports` | `Mapping[str, httpx.AsyncBaseTransport] \| None` | `None` | positional-or-keyword |
| `search` | `SearchProvider \| None` | `None` | positional-or-keyword |
| `state` | `ServiceState \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:92](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L92).

```python
deps = Dependencies(transports=self.extra["transports"], search=self.search)
```

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:137](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L137).

```python
app = build_app(settings, Dependencies(transports=transports, search=fake_search))
```

## jane_assistant.app.Dependencies.transports

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:151](../../../../../../services/assistant/src/jane_assistant/app.py#L151).

```python
transports: Mapping[str, httpx.AsyncBaseTransport] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.Dependencies.search

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:152](../../../../../../services/assistant/src/jane_assistant/app.py#L152).

```python
search: SearchProvider | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.Dependencies.state

**Поле.** Код: [services/assistant/src/jane_assistant/app.py:153](../../../../../../services/assistant/src/jane_assistant/app.py#L153).

```python
state: ServiceState | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.app.build_state

**Функція.** Код: [services/assistant/src/jane_assistant/app.py:156](../../../../../../services/assistant/src/jane_assistant/app.py#L156).

```python
def build_state(settings: Settings, limits: ServiceLimits) -> ServiceState:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `ServiceState`.

### Опис із вихідного коду

```text
PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance).
```

## jane_assistant.app.build_search

**Функція.** Код: [services/assistant/src/jane_assistant/app.py:165](../../../../../../services/assistant/src/jane_assistant/app.py#L165).

```python
def build_search(settings: Settings, limits: ServiceLimits) -> SearchProvider:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `SearchProvider`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_content_policy.py:214](../../../../../../services/assistant/tests/test_content_policy.py#L214).

```python
provider = build_search(s, resolve_service_limits(s).limits)
```

## jane_assistant.app.build_app

**Функція.** Код: [services/assistant/src/jane_assistant/app.py:195](../../../../../../services/assistant/src/jane_assistant/app.py#L195).

```python
def build_app(settings: Settings | None=None, deps: Dependencies | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |
| `deps` | `Dependencies \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:137](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L137).

```python
app = build_app(settings, Dependencies(transports=transports, search=fake_search))
```

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:93](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L93).

```python
return TestClient(build_app(settings, deps))
```
