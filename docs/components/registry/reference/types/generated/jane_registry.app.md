# jane_registry.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.app.log](#jane_registryapplog)
- [jane_registry.app.SLUG](#jane_registryappslug)
- [jane_registry.app.SEMVER](#jane_registryappsemver)
- [jane_registry.app.KINDS](#jane_registryappkinds)
- [jane_registry.app.STATUSES](#jane_registryappstatuses)
- [jane_registry.app.LABELS](#jane_registryapplabels)
- [jane_registry.app.PackageCreate](#jane_registryapppackagecreate)
- [jane_registry.app.PackageCreate.package_id](#jane_registryapppackagecreatepackage_id)
- [jane_registry.app.PackageCreate.kind](#jane_registryapppackagecreatekind)
- [jane_registry.app.PackageCreate.title](#jane_registryapppackagecreatetitle)
- [jane_registry.app.PackageCreate.description](#jane_registryapppackagecreatedescription)
- [jane_registry.app.PackageCreate.auto_changes_allowed](#jane_registryapppackagecreateauto_changes_allowed)
- [jane_registry.app.PackageCreate.labels](#jane_registryapppackagecreatelabels)
- [jane_registry.app.PackagePatch](#jane_registryapppackagepatch)
- [jane_registry.app.PackagePatch.title](#jane_registryapppackagepatchtitle)
- [jane_registry.app.PackagePatch.description](#jane_registryapppackagepatchdescription)
- [jane_registry.app.PackagePatch.auto_changes_allowed](#jane_registryapppackagepatchauto_changes_allowed)
- [jane_registry.app.PackagePatch.deprecated](#jane_registryapppackagepatchdeprecated)
- [jane_registry.app.PackagePatch.labels](#jane_registryapppackagepatchlabels)
- [jane_registry.app.FileContent](#jane_registryappfilecontent)
- [jane_registry.app.FileContent.encoding](#jane_registryappfilecontentencoding)
- [jane_registry.app.FileContent.data](#jane_registryappfilecontentdata)
- [jane_registry.app.PublishRequest](#jane_registryapppublishrequest)
- [jane_registry.app.PublishRequest.manifest](#jane_registryapppublishrequestmanifest)
- [jane_registry.app.PublishRequest.files](#jane_registryapppublishrequestfiles)
- [jane_registry.app.StatusChange](#jane_registryappstatuschange)
- [jane_registry.app.StatusChange.status](#jane_registryappstatuschangestatus)
- [jane_registry.app.StatusChange.reason](#jane_registryappstatuschangereason)
- [jane_registry.app.TestResultsRecord](#jane_registryapptestresultsrecord)
- [jane_registry.app.TestResultsRecord.model_config](#jane_registryapptestresultsrecordmodel_config)
- [jane_registry.app.TestResultsRecord.runner](#jane_registryapptestresultsrecordrunner)
- [jane_registry.app.TestResultsRecord.context](#jane_registryapptestresultsrecordcontext)
- [jane_registry.app.TestResultsRecord.report](#jane_registryapptestresultsrecordreport)
- [jane_registry.app.TestResultsRecord.recorded_at](#jane_registryapptestresultsrecordrecorded_at)
- [jane_registry.app.ForkRequest](#jane_registryappforkrequest)
- [jane_registry.app.ForkRequest.new_package_id](#jane_registryappforkrequestnew_package_id)
- [jane_registry.app.ForkRequest.from_version](#jane_registryappforkrequestfrom_version)
- [jane_registry.app.ForkRequest.initial_version](#jane_registryappforkrequestinitial_version)
- [jane_registry.app.ForkRequest.title](#jane_registryappforkrequesttitle)
- [jane_registry.app.ForkRequest.auto_changes_allowed](#jane_registryappforkrequestauto_changes_allowed)
- [jane_registry.app.UpstreamPortRequest](#jane_registryappupstreamportrequest)
- [jane_registry.app.UpstreamPortRequest.parent_version](#jane_registryappupstreamportrequestparent_version)
- [jane_registry.app.UpstreamPortRequest.base_version](#jane_registryappupstreamportrequestbase_version)
- [jane_registry.app.UpstreamPortRequest.new_version](#jane_registryappupstreamportrequestnew_version)
- [jane_registry.app.Components](#jane_registryappcomponents)
- [jane_registry.app.Components.__init__](#jane_registryappcomponents__init__)
- [jane_registry.app.Components.store](#jane_registryappcomponentsstore)
- [jane_registry.app.Components.blobs](#jane_registryappcomponentsblobs)
- [jane_registry.app.Components.idempotency](#jane_registryappcomponentsidempotency)
- [jane_registry.app.Components.jobs](#jane_registryappcomponentsjobs)
- [jane_registry.app.build_components](#jane_registryappbuild_components)
- [jane_registry.app.build_app](#jane_registryappbuild_app)

## jane_registry.app.log

**Змінна.** Код: [services/registry/src/jane_registry/app.py:45](../../../../../../services/registry/src/jane_registry/app.py#L45).

```python
log = logging.getLogger(__name__)
```

## jane_registry.app.SLUG

**Константа.** Код: [services/registry/src/jane_registry/app.py:47](../../../../../../services/registry/src/jane_registry/app.py#L47).

```python
SLUG = '^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'
```

## jane_registry.app.SEMVER

**Константа.** Код: [services/registry/src/jane_registry/app.py:48](../../../../../../services/registry/src/jane_registry/app.py#L48).

```python
SEMVER = '^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$'
```

## jane_registry.app.KINDS

**Константа.** Код: [services/registry/src/jane_registry/app.py:49](../../../../../../services/registry/src/jane_registry/app.py#L49).

```python
KINDS = Literal['extractor', 'storage', 'llm', 'transform', 'collector-rules']
```

## jane_registry.app.STATUSES

**Константа.** Код: [services/registry/src/jane_registry/app.py:50](../../../../../../services/registry/src/jane_registry/app.py#L50).

```python
STATUSES = Literal['draft', 'approved', 'rejected', 'deprecated', 'yanked']
```

## jane_registry.app.LABELS

**Константа.** Код: [services/registry/src/jane_registry/app.py:51](../../../../../../services/registry/src/jane_registry/app.py#L51).

```python
LABELS = dict[Annotated[str, Field(pattern='^[a-z0-9][a-z0-9._/-]{0,62}$')], Annotated[str, Field(max_length=256)]]
```

## jane_registry.app.PackageCreate

**Клас.** Код: [services/registry/src/jane_registry/app.py:60](../../../../../../services/registry/src/jane_registry/app.py#L60).

```python
class PackageCreate(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](jane_registry.app.md#jane_registryapppackagecreatepackage_id) | Поле | ні |
| [kind](jane_registry.app.md#jane_registryapppackagecreatekind) | Поле | ні |
| [title](jane_registry.app.md#jane_registryapppackagecreatetitle) | Поле | ні |
| [description](jane_registry.app.md#jane_registryapppackagecreatedescription) | Поле | ні |
| [auto_changes_allowed](jane_registry.app.md#jane_registryapppackagecreateauto_changes_allowed) | Поле | ні |
| [labels](jane_registry.app.md#jane_registryapppackagecreatelabels) | Поле | ні |

## jane_registry.app.PackageCreate.package_id

**Поле.** Код: [services/registry/src/jane_registry/app.py:61](../../../../../../services/registry/src/jane_registry/app.py#L61).

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

## jane_registry.app.PackageCreate.kind

**Поле.** Код: [services/registry/src/jane_registry/app.py:62](../../../../../../services/registry/src/jane_registry/app.py#L62).

```python
kind: KINDS
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackageCreate.title

**Поле.** Код: [services/registry/src/jane_registry/app.py:63](../../../../../../services/registry/src/jane_registry/app.py#L63).

```python
title: str
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackageCreate.description

**Поле.** Код: [services/registry/src/jane_registry/app.py:64](../../../../../../services/registry/src/jane_registry/app.py#L64).

```python
description: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackageCreate.auto_changes_allowed

**Поле.** Код: [services/registry/src/jane_registry/app.py:65](../../../../../../services/registry/src/jane_registry/app.py#L65).

```python
auto_changes_allowed: bool = True
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackageCreate.labels

**Поле.** Код: [services/registry/src/jane_registry/app.py:66](../../../../../../services/registry/src/jane_registry/app.py#L66).

```python
labels: LABELS | None = Field(default=None, max_length=64)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "64"
}
```

## jane_registry.app.PackagePatch

**Клас.** Код: [services/registry/src/jane_registry/app.py:69](../../../../../../services/registry/src/jane_registry/app.py#L69).

```python
class PackagePatch(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [title](jane_registry.app.md#jane_registryapppackagepatchtitle) | Поле | ні |
| [description](jane_registry.app.md#jane_registryapppackagepatchdescription) | Поле | ні |
| [auto_changes_allowed](jane_registry.app.md#jane_registryapppackagepatchauto_changes_allowed) | Поле | ні |
| [deprecated](jane_registry.app.md#jane_registryapppackagepatchdeprecated) | Поле | ні |
| [labels](jane_registry.app.md#jane_registryapppackagepatchlabels) | Поле | ні |

## jane_registry.app.PackagePatch.title

**Поле.** Код: [services/registry/src/jane_registry/app.py:70](../../../../../../services/registry/src/jane_registry/app.py#L70).

```python
title: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackagePatch.description

**Поле.** Код: [services/registry/src/jane_registry/app.py:71](../../../../../../services/registry/src/jane_registry/app.py#L71).

```python
description: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackagePatch.auto_changes_allowed

**Поле.** Код: [services/registry/src/jane_registry/app.py:72](../../../../../../services/registry/src/jane_registry/app.py#L72).

```python
auto_changes_allowed: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackagePatch.deprecated

**Поле.** Код: [services/registry/src/jane_registry/app.py:73](../../../../../../services/registry/src/jane_registry/app.py#L73).

```python
deprecated: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.PackagePatch.labels

**Поле.** Код: [services/registry/src/jane_registry/app.py:74](../../../../../../services/registry/src/jane_registry/app.py#L74).

```python
labels: LABELS | None = Field(default=None, max_length=64)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "64"
}
```

## jane_registry.app.FileContent

**Клас.** Код: [services/registry/src/jane_registry/app.py:77](../../../../../../services/registry/src/jane_registry/app.py#L77).

```python
class FileContent(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [encoding](jane_registry.app.md#jane_registryappfilecontentencoding) | Поле | ні |
| [data](jane_registry.app.md#jane_registryappfilecontentdata) | Поле | ні |

## jane_registry.app.FileContent.encoding

**Поле.** Код: [services/registry/src/jane_registry/app.py:78](../../../../../../services/registry/src/jane_registry/app.py#L78).

```python
encoding: Literal['utf-8', 'base64']
```

Доступ: читання — так; запис — так.

## jane_registry.app.FileContent.data

**Поле.** Код: [services/registry/src/jane_registry/app.py:79](../../../../../../services/registry/src/jane_registry/app.py#L79).

```python
data: str
```

Доступ: читання — так; запис — так.

## jane_registry.app.PublishRequest

**Клас.** Код: [services/registry/src/jane_registry/app.py:82](../../../../../../services/registry/src/jane_registry/app.py#L82).

```python
class PublishRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [manifest](jane_registry.app.md#jane_registryapppublishrequestmanifest) | Поле | ні |
| [files](jane_registry.app.md#jane_registryapppublishrequestfiles) | Поле | ні |

## jane_registry.app.PublishRequest.manifest

**Поле.** Код: [services/registry/src/jane_registry/app.py:83](../../../../../../services/registry/src/jane_registry/app.py#L83).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_registry.app.PublishRequest.files

**Поле.** Код: [services/registry/src/jane_registry/app.py:84](../../../../../../services/registry/src/jane_registry/app.py#L84).

```python
files: dict[str, FileContent]
```

Доступ: читання — так; запис — так.

## jane_registry.app.StatusChange

**Клас.** Код: [services/registry/src/jane_registry/app.py:87](../../../../../../services/registry/src/jane_registry/app.py#L87).

```python
class StatusChange(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status](jane_registry.app.md#jane_registryappstatuschangestatus) | Поле | ні |
| [reason](jane_registry.app.md#jane_registryappstatuschangereason) | Поле | ні |

## jane_registry.app.StatusChange.status

**Поле.** Код: [services/registry/src/jane_registry/app.py:88](../../../../../../services/registry/src/jane_registry/app.py#L88).

```python
status: Literal['approved', 'rejected', 'deprecated', 'yanked']
```

Доступ: читання — так; запис — так.

## jane_registry.app.StatusChange.reason

**Поле.** Код: [services/registry/src/jane_registry/app.py:89](../../../../../../services/registry/src/jane_registry/app.py#L89).

```python
reason: str | None = Field(default=None, max_length=2000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "2000"
}
```

## jane_registry.app.TestResultsRecord

**Клас.** Код: [services/registry/src/jane_registry/app.py:92](../../../../../../services/registry/src/jane_registry/app.py#L92).

```python
class TestResultsRecord(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_registry.app.md#jane_registryapptestresultsrecordmodel_config) | Поле | ні |
| [runner](jane_registry.app.md#jane_registryapptestresultsrecordrunner) | Поле | ні |
| [context](jane_registry.app.md#jane_registryapptestresultsrecordcontext) | Поле | ні |
| [report](jane_registry.app.md#jane_registryapptestresultsrecordreport) | Поле | ні |
| [recorded_at](jane_registry.app.md#jane_registryapptestresultsrecordrecorded_at) | Поле | ні |

## jane_registry.app.TestResultsRecord.model_config

**Поле.** Код: [services/registry/src/jane_registry/app.py:93](../../../../../../services/registry/src/jane_registry/app.py#L93).

```python
model_config = ConfigDict(extra='allow')
```

Доступ: читання — так; запис — так.

## jane_registry.app.TestResultsRecord.runner

**Поле.** Код: [services/registry/src/jane_registry/app.py:94](../../../../../../services/registry/src/jane_registry/app.py#L94).

```python
runner: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.TestResultsRecord.context

**Поле.** Код: [services/registry/src/jane_registry/app.py:95](../../../../../../services/registry/src/jane_registry/app.py#L95).

```python
context: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.TestResultsRecord.report

**Поле.** Код: [services/registry/src/jane_registry/app.py:96](../../../../../../services/registry/src/jane_registry/app.py#L96).

```python
report: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_registry.app.TestResultsRecord.recorded_at

**Поле.** Код: [services/registry/src/jane_registry/app.py:97](../../../../../../services/registry/src/jane_registry/app.py#L97).

```python
recorded_at: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.ForkRequest

**Клас.** Код: [services/registry/src/jane_registry/app.py:100](../../../../../../services/registry/src/jane_registry/app.py#L100).

```python
class ForkRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [new_package_id](jane_registry.app.md#jane_registryappforkrequestnew_package_id) | Поле | ні |
| [from_version](jane_registry.app.md#jane_registryappforkrequestfrom_version) | Поле | ні |
| [initial_version](jane_registry.app.md#jane_registryappforkrequestinitial_version) | Поле | ні |
| [title](jane_registry.app.md#jane_registryappforkrequesttitle) | Поле | ні |
| [auto_changes_allowed](jane_registry.app.md#jane_registryappforkrequestauto_changes_allowed) | Поле | ні |

## jane_registry.app.ForkRequest.new_package_id

**Поле.** Код: [services/registry/src/jane_registry/app.py:101](../../../../../../services/registry/src/jane_registry/app.py#L101).

```python
new_package_id: str = Field(pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SLUG"
}
```

## jane_registry.app.ForkRequest.from_version

**Поле.** Код: [services/registry/src/jane_registry/app.py:102](../../../../../../services/registry/src/jane_registry/app.py#L102).

```python
from_version: str = Field(pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SEMVER"
}
```

## jane_registry.app.ForkRequest.initial_version

**Поле.** Код: [services/registry/src/jane_registry/app.py:103](../../../../../../services/registry/src/jane_registry/app.py#L103).

```python
initial_version: str | None = Field(default=None, pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "SEMVER"
}
```

## jane_registry.app.ForkRequest.title

**Поле.** Код: [services/registry/src/jane_registry/app.py:104](../../../../../../services/registry/src/jane_registry/app.py#L104).

```python
title: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.app.ForkRequest.auto_changes_allowed

**Поле.** Код: [services/registry/src/jane_registry/app.py:105](../../../../../../services/registry/src/jane_registry/app.py#L105).

```python
auto_changes_allowed: bool = False
```

Доступ: читання — так; запис — так.

## jane_registry.app.UpstreamPortRequest

**Клас.** Код: [services/registry/src/jane_registry/app.py:108](../../../../../../services/registry/src/jane_registry/app.py#L108).

```python
class UpstreamPortRequest(_Strict):
```

Базові типи / інтерфейси: `_Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [parent_version](jane_registry.app.md#jane_registryappupstreamportrequestparent_version) | Поле | ні |
| [base_version](jane_registry.app.md#jane_registryappupstreamportrequestbase_version) | Поле | ні |
| [new_version](jane_registry.app.md#jane_registryappupstreamportrequestnew_version) | Поле | ні |

## jane_registry.app.UpstreamPortRequest.parent_version

**Поле.** Код: [services/registry/src/jane_registry/app.py:109](../../../../../../services/registry/src/jane_registry/app.py#L109).

```python
parent_version: str = Field(pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SEMVER"
}
```

## jane_registry.app.UpstreamPortRequest.base_version

**Поле.** Код: [services/registry/src/jane_registry/app.py:110](../../../../../../services/registry/src/jane_registry/app.py#L110).

```python
base_version: str | None = Field(default=None, pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "SEMVER"
}
```

## jane_registry.app.UpstreamPortRequest.new_version

**Поле.** Код: [services/registry/src/jane_registry/app.py:111](../../../../../../services/registry/src/jane_registry/app.py#L111).

```python
new_version: str = Field(pattern=SEMVER)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SEMVER"
}
```

## jane_registry.app.Components

**Клас.** Код: [services/registry/src/jane_registry/app.py:140](../../../../../../services/registry/src/jane_registry/app.py#L140).

```python
class Components:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [store](jane_registry.app.md#jane_registryappcomponentsstore) | Поле | ні |
| [blobs](jane_registry.app.md#jane_registryappcomponentsblobs) | Поле | ні |
| [idempotency](jane_registry.app.md#jane_registryappcomponentsidempotency) | Поле | ні |
| [jobs](jane_registry.app.md#jane_registryappcomponentsjobs) | Поле | ні |
| [__init__](jane_registry.app.md#jane_registryappcomponents__init__) | Конструктор dataclass | ні |

## jane_registry.app.Components.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/app.py:140](../../../../../../services/registry/src/jane_registry/app.py#L140).

```python
def __init__(self, store: MetadataStore, blobs: BlobStore, idempotency: IdempotencyStore, jobs: JobStore) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `store` | `MetadataStore` | `—` | positional-or-keyword |
| `blobs` | `BlobStore` | `—` | positional-or-keyword |
| `idempotency` | `IdempotencyStore` | `—` | positional-or-keyword |
| `jobs` | `JobStore` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.app.Components.store

**Поле.** Код: [services/registry/src/jane_registry/app.py:141](../../../../../../services/registry/src/jane_registry/app.py#L141).

```python
store: MetadataStore
```

Доступ: читання — так; запис — так.

## jane_registry.app.Components.blobs

**Поле.** Код: [services/registry/src/jane_registry/app.py:142](../../../../../../services/registry/src/jane_registry/app.py#L142).

```python
blobs: BlobStore
```

Доступ: читання — так; запис — так.

## jane_registry.app.Components.idempotency

**Поле.** Код: [services/registry/src/jane_registry/app.py:143](../../../../../../services/registry/src/jane_registry/app.py#L143).

```python
idempotency: IdempotencyStore
```

Доступ: читання — так; запис — так.

## jane_registry.app.Components.jobs

**Поле.** Код: [services/registry/src/jane_registry/app.py:144](../../../../../../services/registry/src/jane_registry/app.py#L144).

```python
jobs: JobStore
```

Доступ: читання — так; запис — так.

## jane_registry.app.build_components

**Функція.** Код: [services/registry/src/jane_registry/app.py:147](../../../../../../services/registry/src/jane_registry/app.py#L147).

```python
def build_components(settings: Settings, limits: ServiceLimits) -> Components:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `Components`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.app.build_app

**Функція.** Код: [services/registry/src/jane_registry/app.py:191](../../../../../../services/registry/src/jane_registry/app.py#L191).

```python
def build_app(settings: Settings | None=None, components: Components | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |
| `components` | `Components \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/conftest.py:104](../../../../../../services/registry/tests/conftest.py#L104).

```python
return TestClient(build_app(self.settings(**extra)))
```

Контекст і передумови: [services/registry/tests/test_auth.py:51](../../../../../../services/registry/tests/test_auth.py#L51).

```python
build_app(settings(tmp_path, profile_file, bad))
```
