# Модуль `jane_assistant.app`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/app.py](../../../../../services/assistant/src/jane_assistant/app.py). Не редагуйте вручну.

HTTP API of the source assistant (``contracts/openapi/assistant.v1.yaml``).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit. Every long operation is ``202`` + Job; POSTs with side effects honour ``Idempotency-Key``.

## Зміст

- [Клас `OnboardingRequest`](#клас-onboardingrequest)
- [Клас `CandidateSelection`](#клас-candidateselection)
- [Клас `AcceptanceRequest`](#клас-acceptancerequest)
- [Клас `PackageRef`](#клас-packageref)
- [Клас `MaterialRef`](#клас-materialref)
- [Клас `ProblemSample`](#клас-problemsample)
- [Клас `BindingRef`](#клас-bindingref)
- [Клас `Policy`](#клас-policy)
- [Клас `ImprovementRequest`](#клас-improvementrequest)
- [Клас `UnknownMaterialRequest`](#клас-unknownmaterialrequest)
- [Клас `Dependencies`](#клас-dependencies)
- [Функція `build_state`](#функція-build_state)
- [Функція `build_search`](#функція-build_search)
- [Функція `build_app`](#функція-build_app)

## Класи

### Клас `OnboardingRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:76](../../../../../services/assistant/src/jane_assistant/app.py#L76) |

```python
class OnboardingRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `query` | `str` | `Field(min_length=1, max_length=2000)` | читання й запис |  |
| `source_kind` | `str \| None` | `Field(default=None, pattern='^[a-z][a-z0-9_-]{1,31}$')` | читання й запис |  |
| `expected_entity_types` | `list[str] \| None` | `None` | читання й запис |  |
| `crawl_hints` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `limits` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `auto_activation` | `bool` | `False` | читання й запис |  |

### Клас `CandidateSelection`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:85](../../../../../services/assistant/src/jane_assistant/app.py#L85) |

```python
class CandidateSelection(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `candidate_id` | `str` | — | читання й запис |  |

### Клас `AcceptanceRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:89](../../../../../services/assistant/src/jane_assistant/app.py#L89) |

```python
class AcceptanceRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `activate` | `bool` | `False` | читання й запис |  |
| `source_id` | `str \| None` | `Field(default=None, pattern=SLUG)` | читання й запис |  |

### Клас `PackageRef`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:94](../../../../../services/assistant/src/jane_assistant/app.py#L94) |

```python
class PackageRef(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `str` | `Field(pattern=SLUG)` | читання й запис |  |
| `version` | `str` | `Field(pattern=SEMVER)` | читання й запис |  |
| `digest` | `str \| None` | `Field(default=None, pattern='^sha256:[a-f0-9]{64}$')` | читання й запис |  |

### Клас `MaterialRef`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:100](../../../../../services/assistant/src/jane_assistant/app.py#L100) |

```python
class MaterialRef(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `storage_connection_id` | `str` | — | читання й запис |  |
| `object_id` | `str` | — | читання й запис |  |

### Клас `ProblemSample`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:105](../../../../../services/assistant/src/jane_assistant/app.py#L105) |

```python
class ProblemSample(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `material` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `material_ref` | `MaterialRef \| None` | `None` | читання й запис |  |
| `result` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `diagnostics` | `list[dict[str, Any]] \| None` | `None` | читання й запис |  |

### Клас `BindingRef`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:118](../../../../../services/assistant/src/jane_assistant/app.py#L118) |

```python
class BindingRef(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `task_id` | `str` | — | читання й запис |  |
| `stage_id` | `str` | — | читання й запис |  |

### Клас `Policy`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:123](../../../../../services/assistant/src/jane_assistant/app.py#L123) |

```python
class Policy(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `approval` | `Literal['manual', 'auto_after_checks']` | `'manual'` | читання й запис |  |
| `allow_fork` | `bool` | `True` | читання й запис |  |

### Клас `ImprovementRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:128](../../../../../services/assistant/src/jane_assistant/app.py#L128) |

```python
class ImprovementRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package` | `PackageRef` | — | читання й запис |  |
| `source_id` | `str \| None` | `None` | читання й запис |  |
| `problem_group_id` | `str \| None` | `None` | читання й запис |  |
| `problem_samples` | `list[ProblemSample]` | `Field(min_length=1)` | читання й запис |  |
| `successful_examples` | `list[ProblemSample] \| None` | `None` | читання й запис |  |
| `bindings` | `list[BindingRef] \| None` | `None` | читання й запис |  |
| `policy` | `Policy \| None` | `None` | читання й запис |  |
| `limits` | `dict[str, Any] \| None` | `None` | читання й запис |  |

### Клас `UnknownMaterialRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.app` |
| Успадкування | `_Strict` |
| Код | [app.py:139](../../../../../services/assistant/src/jane_assistant/app.py#L139) |

```python
class UnknownMaterialRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `source_id` | `str` | — | читання й запис |  |
| `task_id` | `str \| None` | `None` | читання й запис |  |
| `forward_unknown_to_llm` | `bool` | — | читання й запис |  |
| `material` | `dict[str, Any]` | — | читання й запис |  |
| `limits` | `dict[str, Any] \| None` | `None` | читання й запис |  |

### Клас `Dependencies`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.app` |
| Код | [app.py:148](../../../../../services/assistant/src/jane_assistant/app.py#L148) |

```python
@dataclass
class Dependencies: ...
```

Replaceable collaborators (tests pass ASGI transports of contract fakes and a fake search).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `transports` | `Mapping[str, httpx.AsyncBaseTransport] \| None` | `None` | читання й запис |  |
| `search` | `SearchProvider \| None` | `None` | читання й запис |  |
| `state` | `ServiceState \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `build_state`

```python
def build_state(settings: Settings, limits: ServiceLimits) -> ServiceState: ...
```

PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance).

Код: [app.py:156](../../../../../services/assistant/src/jane_assistant/app.py#L156).

### Функція `build_search`

```python
def build_search(settings: Settings, limits: ServiceLimits) -> SearchProvider: ...
```

Винятки в коді функції: `ValueError`.

Код: [app.py:165](../../../../../services/assistant/src/jane_assistant/app.py#L165).

### Функція `build_app`

```python
def build_app(settings: Settings | None = None, deps: Dependencies | None = None) -> FastAPI: ...
```

Винятки в коді функції: `FlagOff`, `ValidationFailed`.

Код: [app.py:195](../../../../../services/assistant/src/jane_assistant/app.py#L195).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `SLUG` | — | `'^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'` |  |
| `SEMVER` | — | `'^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[` |  |
| `SessionStatus` | — | `Literal['resolving', 'needs_disambiguation', 'sampling', 'analyzing', 'proposals` | ``OnboardingStatus`` of the contract. |
| `STATUS_QUERY` | — | `Query(default=None)` | ``?status=`` may repeat (a list); one module-level default (ruff B008). |
| `LIST_SCOPES` | — | `{'GET /v1/onboarding-sessions': 'assistant:use', 'GET /v1/improvement-runs': 'as` | Scopes of the list operations added by WP-15 (R24) until ``jane_kit.auth_scopes.ASSISTANT`` lists them; merging is idempotent, so the table stays right after jane-kit adds them. |
