# Модуль `jane_registry.app`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/app.py](../../../../../services/registry/src/jane_registry/app.py). Не редагуйте вручну.

HTTP API of the registry: ``contracts/openapi/registry.v1.yaml``.

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit.

## Зміст

- [Клас `PackageCreate`](#клас-packagecreate)
- [Клас `PackagePatch`](#клас-packagepatch)
- [Клас `FileContent`](#клас-filecontent)
- [Клас `PublishRequest`](#клас-publishrequest)
- [Клас `StatusChange`](#клас-statuschange)
- [Клас `TestResultsRecord`](#клас-testresultsrecord)
- [Клас `ForkRequest`](#клас-forkrequest)
- [Клас `UpstreamPortRequest`](#клас-upstreamportrequest)
- [Клас `Components`](#клас-components)
- [Функція `build_components`](#функція-build_components)
- [Функція `build_app`](#функція-build_app)

## Класи

### Клас `PackageCreate`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:60](../../../../../services/registry/src/jane_registry/app.py#L60) |

```python
class PackageCreate(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `str` | `Field(pattern=SLUG)` | читання й запис |  |
| `kind` | `KINDS` | — | читання й запис |  |
| `title` | `str` | — | читання й запис |  |
| `description` | `str \| None` | `None` | читання й запис |  |
| `auto_changes_allowed` | `bool` | `True` | читання й запис |  |
| `labels` | `LABELS \| None` | `Field(default=None, max_length=64)` | читання й запис |  |

### Клас `PackagePatch`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:69](../../../../../services/registry/src/jane_registry/app.py#L69) |

```python
class PackagePatch(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `title` | `str \| None` | `None` | читання й запис |  |
| `description` | `str \| None` | `None` | читання й запис |  |
| `auto_changes_allowed` | `bool \| None` | `None` | читання й запис |  |
| `deprecated` | `bool \| None` | `None` | читання й запис |  |
| `labels` | `LABELS \| None` | `Field(default=None, max_length=64)` | читання й запис |  |

### Клас `FileContent`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:77](../../../../../services/registry/src/jane_registry/app.py#L77) |

```python
class FileContent(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `encoding` | `Literal['utf-8', 'base64']` | — | читання й запис |  |
| `data` | `str` | — | читання й запис |  |

### Клас `PublishRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:82](../../../../../services/registry/src/jane_registry/app.py#L82) |

```python
class PublishRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `manifest` | `dict[str, Any]` | — | читання й запис |  |
| `files` | `dict[str, FileContent]` | — | читання й запис |  |

### Клас `StatusChange`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:87](../../../../../services/registry/src/jane_registry/app.py#L87) |

```python
class StatusChange(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `status` | `Literal['approved', 'rejected', 'deprecated', 'yanked']` | — | читання й запис |  |
| `reason` | `str \| None` | `Field(default=None, max_length=2000)` | читання й запис |  |

### Клас `TestResultsRecord`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_registry.app` |
| Успадкування | `BaseModel` |
| Код | [app.py:92](../../../../../services/registry/src/jane_registry/app.py#L92) |

```python
class TestResultsRecord(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `runner` | `str \| None` | `None` | читання й запис |  |
| `context` | `str \| None` | `None` | читання й запис |  |
| `report` | `dict[str, Any]` | — | читання й запис |  |
| `recorded_at` | `str \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='allow')` |  |

### Клас `ForkRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:100](../../../../../services/registry/src/jane_registry/app.py#L100) |

```python
class ForkRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `new_package_id` | `str` | `Field(pattern=SLUG)` | читання й запис |  |
| `from_version` | `str` | `Field(pattern=SEMVER)` | читання й запис |  |
| `initial_version` | `str \| None` | `Field(default=None, pattern=SEMVER)` | читання й запис |  |
| `title` | `str \| None` | `None` | читання й запис |  |
| `auto_changes_allowed` | `bool` | `False` | читання й запис |  |

### Клас `UpstreamPortRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.app` |
| Успадкування | `_Strict` |
| Код | [app.py:108](../../../../../services/registry/src/jane_registry/app.py#L108) |

```python
class UpstreamPortRequest(_Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `parent_version` | `str` | `Field(pattern=SEMVER)` | читання й запис |  |
| `base_version` | `str \| None` | `Field(default=None, pattern=SEMVER)` | читання й запис |  |
| `new_version` | `str` | `Field(pattern=SEMVER)` | читання й запис |  |

### Клас `Components`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_registry.app` |
| Код | [app.py:140](../../../../../services/registry/src/jane_registry/app.py#L140) |

```python
@dataclass
class Components: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `store` | `MetadataStore` | — | читання й запис |  |
| `blobs` | `BlobStore` | — | читання й запис |  |
| `idempotency` | `IdempotencyStore` | — | читання й запис |  |
| `jobs` | `JobStore` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `build_components`

```python
def build_components(settings: Settings, limits: ServiceLimits) -> Components: ...
```

Винятки в коді функції: `ValueError`.

Код: [app.py:147](../../../../../services/registry/src/jane_registry/app.py#L147).

### Функція `build_app`

```python
def build_app(
    settings: Settings | None = None,
    components: Components | None = None,
) -> FastAPI: ...
```

Винятки в коді функції: `ValidationFailed`, `NotFound`, `Forbidden`, `JaneError`.

Код: [app.py:191](../../../../../services/registry/src/jane_registry/app.py#L191).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `SLUG` | — | `'^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'` |  |
| `SEMVER` | — | `'^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[` |  |
| `KINDS` | — | `Literal['extractor', 'storage', 'llm', 'transform', 'collector-rules']` |  |
| `STATUSES` | — | `Literal['draft', 'approved', 'rejected', 'deprecated', 'yanked']` |  |
| `LABELS` | — | `dict[Annotated[str, Field(pattern='^[a-z0-9][a-z0-9._/-]{0,62}$')], Annotated[st` |  |
