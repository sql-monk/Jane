# jane_registry.store

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.store.INACTIVE_FOR_LATEST](#jane_registrystoreinactive_for_latest)
- [jane_registry.store.now](#jane_registrystorenow)
- [jane_registry.store.iso](#jane_registrystoreiso)
- [jane_registry.store.AlreadyExists](#jane_registrystorealreadyexists)
- [jane_registry.store.VersionExists](#jane_registrystoreversionexists)
- [jane_registry.store.RevisionMismatch](#jane_registrystorerevisionmismatch)
- [jane_registry.store.StatusMismatch](#jane_registrystorestatusmismatch)
- [jane_registry.store.StatusMismatch.__init__](#jane_registrystorestatusmismatch__init__)
- [jane_registry.store.StatusMismatch.actual](#jane_registrystorestatusmismatchactual)
- [jane_registry.store.PackageRecord](#jane_registrystorepackagerecord)
- [jane_registry.store.PackageRecord.__init__](#jane_registrystorepackagerecord__init__)
- [jane_registry.store.PackageRecord.package_id](#jane_registrystorepackagerecordpackage_id)
- [jane_registry.store.PackageRecord.kind](#jane_registrystorepackagerecordkind)
- [jane_registry.store.PackageRecord.title](#jane_registrystorepackagerecordtitle)
- [jane_registry.store.PackageRecord.auto_changes_allowed](#jane_registrystorepackagerecordauto_changes_allowed)
- [jane_registry.store.PackageRecord.created_at](#jane_registrystorepackagerecordcreated_at)
- [jane_registry.store.PackageRecord.updated_at](#jane_registrystorepackagerecordupdated_at)
- [jane_registry.store.PackageRecord.description](#jane_registrystorepackagerecorddescription)
- [jane_registry.store.PackageRecord.deprecated](#jane_registrystorepackagerecorddeprecated)
- [jane_registry.store.PackageRecord.fork_of](#jane_registrystorepackagerecordfork_of)
- [jane_registry.store.PackageRecord.owner](#jane_registrystorepackagerecordowner)
- [jane_registry.store.PackageRecord.labels](#jane_registrystorepackagerecordlabels)
- [jane_registry.store.PackageRecord.revision](#jane_registrystorepackagerecordrevision)
- [jane_registry.store.PackageRecord.latest_version](#jane_registrystorepackagerecordlatest_version)
- [jane_registry.store.PackageRecord.tags](#jane_registrystorepackagerecordtags)
- [jane_registry.store.PackageRecord.entity_types](#jane_registrystorepackagerecordentity_types)
- [jane_registry.store.PackageRecord.media_types](#jane_registrystorepackagerecordmedia_types)
- [jane_registry.store.PackageRecord.domains](#jane_registrystorepackagerecorddomains)
- [jane_registry.store.VersionRecord](#jane_registrystoreversionrecord)
- [jane_registry.store.VersionRecord.__init__](#jane_registrystoreversionrecord__init__)
- [jane_registry.store.VersionRecord.package_id](#jane_registrystoreversionrecordpackage_id)
- [jane_registry.store.VersionRecord.version](#jane_registrystoreversionrecordversion)
- [jane_registry.store.VersionRecord.digest](#jane_registrystoreversionrecorddigest)
- [jane_registry.store.VersionRecord.status](#jane_registrystoreversionrecordstatus)
- [jane_registry.store.VersionRecord.test_status](#jane_registrystoreversionrecordtest_status)
- [jane_registry.store.VersionRecord.manifest](#jane_registrystoreversionrecordmanifest)
- [jane_registry.store.VersionRecord.files](#jane_registrystoreversionrecordfiles)
- [jane_registry.store.VersionRecord.size_bytes](#jane_registrystoreversionrecordsize_bytes)
- [jane_registry.store.VersionRecord.created_at](#jane_registrystoreversionrecordcreated_at)
- [jane_registry.store.VersionRecord.created_by](#jane_registrystoreversionrecordcreated_by)
- [jane_registry.store.VersionRecord.published_by](#jane_registrystoreversionrecordpublished_by)
- [jane_registry.store.VersionRecord.ported_parent_version](#jane_registrystoreversionrecordported_parent_version)
- [jane_registry.store.VersionRecord.seq](#jane_registrystoreversionrecordseq)
- [jane_registry.store.VersionRecord.status_history](#jane_registrystoreversionrecordstatus_history)
- [jane_registry.store.VersionRecord.test_reports](#jane_registrystoreversionrecordtest_reports)
- [jane_registry.store.VersionRecord.search_fields](#jane_registrystoreversionrecordsearch_fields)
- [jane_registry.store.PackageFilter](#jane_registrystorepackagefilter)
- [jane_registry.store.PackageFilter.__init__](#jane_registrystorepackagefilter__init__)
- [jane_registry.store.PackageFilter.kind](#jane_registrystorepackagefilterkind)
- [jane_registry.store.PackageFilter.q](#jane_registrystorepackagefilterq)
- [jane_registry.store.PackageFilter.tag](#jane_registrystorepackagefiltertag)
- [jane_registry.store.PackageFilter.entity_type](#jane_registrystorepackagefilterentity_type)
- [jane_registry.store.PackageFilter.media_type](#jane_registrystorepackagefiltermedia_type)
- [jane_registry.store.PackageFilter.domain](#jane_registrystorepackagefilterdomain)
- [jane_registry.store.PackageFilter.fork_of](#jane_registrystorepackagefilterfork_of)
- [jane_registry.store.pick_latest](#jane_registrystorepick_latest)
- [jane_registry.store.MetadataStore](#jane_registrystoremetadatastore)
- [jane_registry.store.MetadataStore.name](#jane_registrystoremetadatastorename)
- [jane_registry.store.MetadataStore.open](#jane_registrystoremetadatastoreopen)
- [jane_registry.store.MetadataStore.close](#jane_registrystoremetadatastoreclose)
- [jane_registry.store.MetadataStore.check](#jane_registrystoremetadatastorecheck)
- [jane_registry.store.MetadataStore.create_package](#jane_registrystoremetadatastorecreate_package)
- [jane_registry.store.MetadataStore.get_package](#jane_registrystoremetadatastoreget_package)
- [jane_registry.store.MetadataStore.update_package](#jane_registrystoremetadatastoreupdate_package)
- [jane_registry.store.MetadataStore.list_packages](#jane_registrystoremetadatastorelist_packages)
- [jane_registry.store.MetadataStore.count_forks](#jane_registrystoremetadatastorecount_forks)
- [jane_registry.store.MetadataStore.delete_package_if_empty](#jane_registrystoremetadatastoredelete_package_if_empty)
- [jane_registry.store.MetadataStore.insert_version](#jane_registrystoremetadatastoreinsert_version)
- [jane_registry.store.MetadataStore.get_version](#jane_registrystoremetadatastoreget_version)
- [jane_registry.store.MetadataStore.list_versions](#jane_registrystoremetadatastorelist_versions)
- [jane_registry.store.MetadataStore.version_numbers](#jane_registrystoremetadatastoreversion_numbers)
- [jane_registry.store.MetadataStore.count_versions](#jane_registrystoremetadatastorecount_versions)
- [jane_registry.store.MetadataStore.set_status](#jane_registrystoremetadatastoreset_status)
- [jane_registry.store.MetadataStore.add_test_report](#jane_registrystoremetadatastoreadd_test_report)
- [jane_registry.store.LimitReached](#jane_registrystorelimitreached)
- [jane_registry.store.LimitReached.__init__](#jane_registrystorelimitreached__init__)
- [jane_registry.store.LimitReached.count](#jane_registrystorelimitreachedcount)
- [jane_registry.store.MemoryStore](#jane_registrystorememorystore)
- [jane_registry.store.MemoryStore.name](#jane_registrystorememorystorename)
- [jane_registry.store.MemoryStore.__init__](#jane_registrystorememorystore__init__)
- [jane_registry.store.MemoryStore.open](#jane_registrystorememorystoreopen)
- [jane_registry.store.MemoryStore.close](#jane_registrystorememorystoreclose)
- [jane_registry.store.MemoryStore.check](#jane_registrystorememorystorecheck)
- [jane_registry.store.MemoryStore.create_package](#jane_registrystorememorystorecreate_package)
- [jane_registry.store.MemoryStore.get_package](#jane_registrystorememorystoreget_package)
- [jane_registry.store.MemoryStore.update_package](#jane_registrystorememorystoreupdate_package)
- [jane_registry.store.MemoryStore.list_packages](#jane_registrystorememorystorelist_packages)
- [jane_registry.store.MemoryStore.count_forks](#jane_registrystorememorystorecount_forks)
- [jane_registry.store.MemoryStore.delete_package_if_empty](#jane_registrystorememorystoredelete_package_if_empty)
- [jane_registry.store.MemoryStore.insert_version](#jane_registrystorememorystoreinsert_version)
- [jane_registry.store.MemoryStore.get_version](#jane_registrystorememorystoreget_version)
- [jane_registry.store.MemoryStore.list_versions](#jane_registrystorememorystorelist_versions)
- [jane_registry.store.MemoryStore.version_numbers](#jane_registrystorememorystoreversion_numbers)
- [jane_registry.store.MemoryStore.count_versions](#jane_registrystorememorystorecount_versions)
- [jane_registry.store.MemoryStore.set_status](#jane_registrystorememorystoreset_status)
- [jane_registry.store.MemoryStore.add_test_report](#jane_registrystorememorystoreadd_test_report)

## jane_registry.store.INACTIVE_FOR_LATEST

**Константа.** Код: [services/registry/src/jane_registry/store.py:36](../../../../../../services/registry/src/jane_registry/store.py#L36).

```python
INACTIVE_FOR_LATEST = frozenset({'rejected', 'yanked'})
```

## jane_registry.store.now

**Функція.** Код: [services/registry/src/jane_registry/store.py:39](../../../../../../services/registry/src/jane_registry/store.py#L39).

```python
def now() -> datetime:
```

Результат: `datetime`.

## jane_registry.store.iso

**Функція.** Код: [services/registry/src/jane_registry/store.py:44](../../../../../../services/registry/src/jane_registry/store.py#L44).

```python
def iso(t: datetime) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `t` | `datetime` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
RFC 3339 UTC with ``Z`` and milliseconds, as the contracts require.
```

## jane_registry.store.AlreadyExists

**Клас.** Код: [services/registry/src/jane_registry/store.py:49](../../../../../../services/registry/src/jane_registry/store.py#L49).

```python
class AlreadyExists(Exception):
```

Базові типи / інтерфейси: `Exception`.

## jane_registry.store.VersionExists

**Клас.** Код: [services/registry/src/jane_registry/store.py:53](../../../../../../services/registry/src/jane_registry/store.py#L53).

```python
class VersionExists(Exception):
```

Базові типи / інтерфейси: `Exception`.

## jane_registry.store.RevisionMismatch

**Клас.** Код: [services/registry/src/jane_registry/store.py:57](../../../../../../services/registry/src/jane_registry/store.py#L57).

```python
class RevisionMismatch(Exception):
```

Базові типи / інтерфейси: `Exception`.

## jane_registry.store.StatusMismatch

**Клас.** Код: [services/registry/src/jane_registry/store.py:61](../../../../../../services/registry/src/jane_registry/store.py#L61).

```python
class StatusMismatch(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.store.md#jane_registrystorestatusmismatch__init__) | Конструктор | ні |
| [actual](jane_registry.store.md#jane_registrystorestatusmismatchactual) | Поле екземпляра | ні |

## jane_registry.store.StatusMismatch.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/store.py:62](../../../../../../services/registry/src/jane_registry/store.py#L62).

```python
def __init__(self, actual: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `actual` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.StatusMismatch.actual

**Поле екземпляра.** Код: [services/registry/src/jane_registry/store.py:64](../../../../../../services/registry/src/jane_registry/store.py#L64).

```python
self.actual = actual
```

## jane_registry.store.PackageRecord

**Клас.** Код: [services/registry/src/jane_registry/store.py:68](../../../../../../services/registry/src/jane_registry/store.py#L68).

```python
class PackageRecord:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](jane_registry.store.md#jane_registrystorepackagerecordpackage_id) | Поле | ні |
| [kind](jane_registry.store.md#jane_registrystorepackagerecordkind) | Поле | ні |
| [title](jane_registry.store.md#jane_registrystorepackagerecordtitle) | Поле | ні |
| [auto_changes_allowed](jane_registry.store.md#jane_registrystorepackagerecordauto_changes_allowed) | Поле | ні |
| [created_at](jane_registry.store.md#jane_registrystorepackagerecordcreated_at) | Поле | ні |
| [updated_at](jane_registry.store.md#jane_registrystorepackagerecordupdated_at) | Поле | ні |
| [description](jane_registry.store.md#jane_registrystorepackagerecorddescription) | Поле | ні |
| [deprecated](jane_registry.store.md#jane_registrystorepackagerecorddeprecated) | Поле | ні |
| [fork_of](jane_registry.store.md#jane_registrystorepackagerecordfork_of) | Поле | ні |
| [owner](jane_registry.store.md#jane_registrystorepackagerecordowner) | Поле | ні |
| [labels](jane_registry.store.md#jane_registrystorepackagerecordlabels) | Поле | ні |
| [revision](jane_registry.store.md#jane_registrystorepackagerecordrevision) | Поле | ні |
| [latest_version](jane_registry.store.md#jane_registrystorepackagerecordlatest_version) | Поле | ні |
| [tags](jane_registry.store.md#jane_registrystorepackagerecordtags) | Поле | ні |
| [entity_types](jane_registry.store.md#jane_registrystorepackagerecordentity_types) | Поле | ні |
| [media_types](jane_registry.store.md#jane_registrystorepackagerecordmedia_types) | Поле | ні |
| [domains](jane_registry.store.md#jane_registrystorepackagerecorddomains) | Поле | ні |
| [__init__](jane_registry.store.md#jane_registrystorepackagerecord__init__) | Конструктор dataclass | ні |

## jane_registry.store.PackageRecord.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/store.py:68](../../../../../../services/registry/src/jane_registry/store.py#L68).

```python
def __init__(self, package_id: str, kind: str, title: str, auto_changes_allowed: bool, created_at: datetime, updated_at: datetime, description: str | None = None, deprecated: bool = False, fork_of: dict[str, str] | None = None, owner: str | None = None, labels: dict[str, str] = <factory dict>, revision: int = 1, latest_version: str | None = None, tags: list[str] = <factory list>, entity_types: list[str] = <factory list>, media_types: list[str] = <factory list>, domains: list[str] = <factory list>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `title` | `str` | `—` | positional-or-keyword |
| `auto_changes_allowed` | `bool` | `—` | positional-or-keyword |
| `created_at` | `datetime` | `—` | positional-or-keyword |
| `updated_at` | `datetime` | `—` | positional-or-keyword |
| `description` | `str \| None` | `None` | positional-or-keyword |
| `deprecated` | `bool` | `False` | positional-or-keyword |
| `fork_of` | `dict[str, str] \| None` | `None` | positional-or-keyword |
| `owner` | `str \| None` | `None` | positional-or-keyword |
| `labels` | `dict[str, str]` | `factory: dict` | positional-or-keyword |
| `revision` | `int` | `1` | positional-or-keyword |
| `latest_version` | `str \| None` | `None` | positional-or-keyword |
| `tags` | `list[str]` | `factory: list` | positional-or-keyword |
| `entity_types` | `list[str]` | `factory: list` | positional-or-keyword |
| `media_types` | `list[str]` | `factory: list` | positional-or-keyword |
| `domains` | `list[str]` | `factory: list` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.PackageRecord.package_id

**Поле.** Код: [services/registry/src/jane_registry/store.py:69](../../../../../../services/registry/src/jane_registry/store.py#L69).

```python
package_id: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.kind

**Поле.** Код: [services/registry/src/jane_registry/store.py:70](../../../../../../services/registry/src/jane_registry/store.py#L70).

```python
kind: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.title

**Поле.** Код: [services/registry/src/jane_registry/store.py:71](../../../../../../services/registry/src/jane_registry/store.py#L71).

```python
title: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.auto_changes_allowed

**Поле.** Код: [services/registry/src/jane_registry/store.py:72](../../../../../../services/registry/src/jane_registry/store.py#L72).

```python
auto_changes_allowed: bool
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.created_at

**Поле.** Код: [services/registry/src/jane_registry/store.py:73](../../../../../../services/registry/src/jane_registry/store.py#L73).

```python
created_at: datetime
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.updated_at

**Поле.** Код: [services/registry/src/jane_registry/store.py:74](../../../../../../services/registry/src/jane_registry/store.py#L74).

```python
updated_at: datetime
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.description

**Поле.** Код: [services/registry/src/jane_registry/store.py:75](../../../../../../services/registry/src/jane_registry/store.py#L75).

```python
description: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.deprecated

**Поле.** Код: [services/registry/src/jane_registry/store.py:76](../../../../../../services/registry/src/jane_registry/store.py#L76).

```python
deprecated: bool = False
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.fork_of

**Поле.** Код: [services/registry/src/jane_registry/store.py:77](../../../../../../services/registry/src/jane_registry/store.py#L77).

```python
fork_of: dict[str, str] | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.owner

**Поле.** Код: [services/registry/src/jane_registry/store.py:78](../../../../../../services/registry/src/jane_registry/store.py#L78).

```python
owner: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.labels

**Поле.** Код: [services/registry/src/jane_registry/store.py:79](../../../../../../services/registry/src/jane_registry/store.py#L79).

```python
labels: dict[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_registry.store.PackageRecord.revision

**Поле.** Код: [services/registry/src/jane_registry/store.py:80](../../../../../../services/registry/src/jane_registry/store.py#L80).

```python
revision: int = 1
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.latest_version

**Поле.** Код: [services/registry/src/jane_registry/store.py:81](../../../../../../services/registry/src/jane_registry/store.py#L81).

```python
latest_version: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.PackageRecord.tags

**Поле.** Код: [services/registry/src/jane_registry/store.py:82](../../../../../../services/registry/src/jane_registry/store.py#L82).

```python
tags: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.PackageRecord.entity_types

**Поле.** Код: [services/registry/src/jane_registry/store.py:83](../../../../../../services/registry/src/jane_registry/store.py#L83).

```python
entity_types: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.PackageRecord.media_types

**Поле.** Код: [services/registry/src/jane_registry/store.py:84](../../../../../../services/registry/src/jane_registry/store.py#L84).

```python
media_types: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.PackageRecord.domains

**Поле.** Код: [services/registry/src/jane_registry/store.py:85](../../../../../../services/registry/src/jane_registry/store.py#L85).

```python
domains: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.VersionRecord

**Клас.** Код: [services/registry/src/jane_registry/store.py:89](../../../../../../services/registry/src/jane_registry/store.py#L89).

```python
class VersionRecord:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](jane_registry.store.md#jane_registrystoreversionrecordpackage_id) | Поле | ні |
| [version](jane_registry.store.md#jane_registrystoreversionrecordversion) | Поле | ні |
| [digest](jane_registry.store.md#jane_registrystoreversionrecorddigest) | Поле | ні |
| [status](jane_registry.store.md#jane_registrystoreversionrecordstatus) | Поле | ні |
| [test_status](jane_registry.store.md#jane_registrystoreversionrecordtest_status) | Поле | ні |
| [manifest](jane_registry.store.md#jane_registrystoreversionrecordmanifest) | Поле | ні |
| [files](jane_registry.store.md#jane_registrystoreversionrecordfiles) | Поле | ні |
| [size_bytes](jane_registry.store.md#jane_registrystoreversionrecordsize_bytes) | Поле | ні |
| [created_at](jane_registry.store.md#jane_registrystoreversionrecordcreated_at) | Поле | ні |
| [created_by](jane_registry.store.md#jane_registrystoreversionrecordcreated_by) | Поле | ні |
| [published_by](jane_registry.store.md#jane_registrystoreversionrecordpublished_by) | Поле | ні |
| [ported_parent_version](jane_registry.store.md#jane_registrystoreversionrecordported_parent_version) | Поле | ні |
| [seq](jane_registry.store.md#jane_registrystoreversionrecordseq) | Поле | ні |
| [status_history](jane_registry.store.md#jane_registrystoreversionrecordstatus_history) | Поле | ні |
| [test_reports](jane_registry.store.md#jane_registrystoreversionrecordtest_reports) | Поле | ні |
| [search_fields](jane_registry.store.md#jane_registrystoreversionrecordsearch_fields) | Властивість | ні |
| [__init__](jane_registry.store.md#jane_registrystoreversionrecord__init__) | Конструктор dataclass | ні |

## jane_registry.store.VersionRecord.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/store.py:89](../../../../../../services/registry/src/jane_registry/store.py#L89).

```python
def __init__(self, package_id: str, version: str, digest: str, status: str, test_status: str, manifest: dict[str, Any], files: list[dict[str, Any]], size_bytes: int, created_at: datetime, created_by: str, published_by: str | None = None, ported_parent_version: str | None = None, seq: int = 0, status_history: list[dict[str, Any]] = <factory list>, test_reports: list[dict[str, Any]] = <factory list>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `test_status` | `str` | `—` | positional-or-keyword |
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `size_bytes` | `int` | `—` | positional-or-keyword |
| `created_at` | `datetime` | `—` | positional-or-keyword |
| `created_by` | `str` | `—` | positional-or-keyword |
| `published_by` | `str \| None` | `None` | positional-or-keyword |
| `ported_parent_version` | `str \| None` | `None` | positional-or-keyword |
| `seq` | `int` | `0` | positional-or-keyword |
| `status_history` | `list[dict[str, Any]]` | `factory: list` | positional-or-keyword |
| `test_reports` | `list[dict[str, Any]]` | `factory: list` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.VersionRecord.package_id

**Поле.** Код: [services/registry/src/jane_registry/store.py:90](../../../../../../services/registry/src/jane_registry/store.py#L90).

```python
package_id: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.version

**Поле.** Код: [services/registry/src/jane_registry/store.py:91](../../../../../../services/registry/src/jane_registry/store.py#L91).

```python
version: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.digest

**Поле.** Код: [services/registry/src/jane_registry/store.py:92](../../../../../../services/registry/src/jane_registry/store.py#L92).

```python
digest: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.status

**Поле.** Код: [services/registry/src/jane_registry/store.py:93](../../../../../../services/registry/src/jane_registry/store.py#L93).

```python
status: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.test_status

**Поле.** Код: [services/registry/src/jane_registry/store.py:94](../../../../../../services/registry/src/jane_registry/store.py#L94).

```python
test_status: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.manifest

**Поле.** Код: [services/registry/src/jane_registry/store.py:95](../../../../../../services/registry/src/jane_registry/store.py#L95).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.files

**Поле.** Код: [services/registry/src/jane_registry/store.py:96](../../../../../../services/registry/src/jane_registry/store.py#L96).

```python
files: list[dict[str, Any]]
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.size_bytes

**Поле.** Код: [services/registry/src/jane_registry/store.py:97](../../../../../../services/registry/src/jane_registry/store.py#L97).

```python
size_bytes: int
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.created_at

**Поле.** Код: [services/registry/src/jane_registry/store.py:98](../../../../../../services/registry/src/jane_registry/store.py#L98).

```python
created_at: datetime
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.created_by

**Поле.** Код: [services/registry/src/jane_registry/store.py:99](../../../../../../services/registry/src/jane_registry/store.py#L99).

```python
created_by: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.published_by

**Поле.** Код: [services/registry/src/jane_registry/store.py:100](../../../../../../services/registry/src/jane_registry/store.py#L100).

```python
published_by: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.ported_parent_version

**Поле.** Код: [services/registry/src/jane_registry/store.py:101](../../../../../../services/registry/src/jane_registry/store.py#L101).

```python
ported_parent_version: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.seq

**Поле.** Код: [services/registry/src/jane_registry/store.py:102](../../../../../../services/registry/src/jane_registry/store.py#L102).

```python
seq: int = 0
```

Доступ: читання — так; запис — так.

## jane_registry.store.VersionRecord.status_history

**Поле.** Код: [services/registry/src/jane_registry/store.py:103](../../../../../../services/registry/src/jane_registry/store.py#L103).

```python
status_history: list[dict[str, Any]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.VersionRecord.test_reports

**Поле.** Код: [services/registry/src/jane_registry/store.py:104](../../../../../../services/registry/src/jane_registry/store.py#L104).

```python
test_reports: list[dict[str, Any]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.store.VersionRecord.search_fields

**Властивість.** Код: [services/registry/src/jane_registry/store.py:108](../../../../../../services/registry/src/jane_registry/store.py#L108).

```python
def search_fields(self) -> dict[str, list[str]]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, list[str]]`.

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter

**Клас.** Код: [services/registry/src/jane_registry/store.py:121](../../../../../../services/registry/src/jane_registry/store.py#L121).

```python
class PackageFilter:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_registry.store.md#jane_registrystorepackagefilterkind) | Поле | ні |
| [q](jane_registry.store.md#jane_registrystorepackagefilterq) | Поле | ні |
| [tag](jane_registry.store.md#jane_registrystorepackagefiltertag) | Поле | ні |
| [entity_type](jane_registry.store.md#jane_registrystorepackagefilterentity_type) | Поле | ні |
| [media_type](jane_registry.store.md#jane_registrystorepackagefiltermedia_type) | Поле | ні |
| [domain](jane_registry.store.md#jane_registrystorepackagefilterdomain) | Поле | ні |
| [fork_of](jane_registry.store.md#jane_registrystorepackagefilterfork_of) | Поле | ні |
| [__init__](jane_registry.store.md#jane_registrystorepackagefilter__init__) | Конструктор dataclass | ні |

## jane_registry.store.PackageFilter.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/store.py:121](../../../../../../services/registry/src/jane_registry/store.py#L121).

```python
def __init__(self, kind: str | None = None, q: str | None = None, tag: str | None = None, entity_type: str | None = None, media_type: str | None = None, domain: str | None = None, fork_of: str | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str \| None` | `None` | positional-or-keyword |
| `q` | `str \| None` | `None` | positional-or-keyword |
| `tag` | `str \| None` | `None` | positional-or-keyword |
| `entity_type` | `str \| None` | `None` | positional-or-keyword |
| `media_type` | `str \| None` | `None` | positional-or-keyword |
| `domain` | `str \| None` | `None` | positional-or-keyword |
| `fork_of` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.PackageFilter.kind

**Поле.** Код: [services/registry/src/jane_registry/store.py:122](../../../../../../services/registry/src/jane_registry/store.py#L122).

```python
kind: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.q

**Поле.** Код: [services/registry/src/jane_registry/store.py:123](../../../../../../services/registry/src/jane_registry/store.py#L123).

```python
q: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.tag

**Поле.** Код: [services/registry/src/jane_registry/store.py:124](../../../../../../services/registry/src/jane_registry/store.py#L124).

```python
tag: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.entity_type

**Поле.** Код: [services/registry/src/jane_registry/store.py:125](../../../../../../services/registry/src/jane_registry/store.py#L125).

```python
entity_type: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.media_type

**Поле.** Код: [services/registry/src/jane_registry/store.py:126](../../../../../../services/registry/src/jane_registry/store.py#L126).

```python
media_type: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.domain

**Поле.** Код: [services/registry/src/jane_registry/store.py:127](../../../../../../services/registry/src/jane_registry/store.py#L127).

```python
domain: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.PackageFilter.fork_of

**Поле.** Код: [services/registry/src/jane_registry/store.py:128](../../../../../../services/registry/src/jane_registry/store.py#L128).

```python
fork_of: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.store.pick_latest

**Функція.** Код: [services/registry/src/jane_registry/store.py:131](../../../../../../services/registry/src/jane_registry/store.py#L131).

```python
def pick_latest(versions: Sequence[tuple[str, str]]) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `versions` | `Sequence[tuple[str, str]]` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Highest SemVer among versions whose status is not rejected/yanked.
```

## jane_registry.store.MetadataStore

**Клас.** Код: [services/registry/src/jane_registry/store.py:170](../../../../../../services/registry/src/jane_registry/store.py#L170).

```python
class MetadataStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.store.md#jane_registrystoremetadatastorename) | Поле | ні |
| [open](jane_registry.store.md#jane_registrystoremetadatastoreopen) | Метод | ні |
| [close](jane_registry.store.md#jane_registrystoremetadatastoreclose) | Метод | ні |
| [check](jane_registry.store.md#jane_registrystoremetadatastorecheck) | Метод | ні |
| [create_package](jane_registry.store.md#jane_registrystoremetadatastorecreate_package) | Метод | ні |
| [get_package](jane_registry.store.md#jane_registrystoremetadatastoreget_package) | Метод | ні |
| [update_package](jane_registry.store.md#jane_registrystoremetadatastoreupdate_package) | Метод | ні |
| [list_packages](jane_registry.store.md#jane_registrystoremetadatastorelist_packages) | Метод | ні |
| [count_forks](jane_registry.store.md#jane_registrystoremetadatastorecount_forks) | Метод | ні |
| [delete_package_if_empty](jane_registry.store.md#jane_registrystoremetadatastoredelete_package_if_empty) | Метод | ні |
| [insert_version](jane_registry.store.md#jane_registrystoremetadatastoreinsert_version) | Метод | ні |
| [get_version](jane_registry.store.md#jane_registrystoremetadatastoreget_version) | Метод | ні |
| [list_versions](jane_registry.store.md#jane_registrystoremetadatastorelist_versions) | Метод | ні |
| [version_numbers](jane_registry.store.md#jane_registrystoremetadatastoreversion_numbers) | Метод | ні |
| [count_versions](jane_registry.store.md#jane_registrystoremetadatastorecount_versions) | Метод | ні |
| [set_status](jane_registry.store.md#jane_registrystoremetadatastoreset_status) | Метод | ні |
| [add_test_report](jane_registry.store.md#jane_registrystoremetadatastoreadd_test_report) | Метод | ні |

## jane_registry.store.MetadataStore.name

**Поле.** Код: [services/registry/src/jane_registry/store.py:171](../../../../../../services/registry/src/jane_registry/store.py#L171).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_registry.store.MetadataStore.open

**Метод.** Код: [services/registry/src/jane_registry/store.py:173](../../../../../../services/registry/src/jane_registry/store.py#L173).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MetadataStore.close

**Метод.** Код: [services/registry/src/jane_registry/store.py:174](../../../../../../services/registry/src/jane_registry/store.py#L174).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MetadataStore.check

**Метод.** Код: [services/registry/src/jane_registry/store.py:175](../../../../../../services/registry/src/jane_registry/store.py#L175).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.store.MetadataStore.create_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:177](../../../../../../services/registry/src/jane_registry/store.py#L177).

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pkg` | `PackageRecord` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

## jane_registry.store.MetadataStore.get_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:178](../../../../../../services/registry/src/jane_registry/store.py#L178).

```python
async def get_package(self, package_id: str) -> PackageRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `PackageRecord | None`.

## jane_registry.store.MetadataStore.update_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:179](../../../../../../services/registry/src/jane_registry/store.py#L179).

```python
async def update_package(self, package_id: str, changes: dict[str, Any], expected_revision: int | None) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `changes` | `dict[str, Any]` | `—` | positional-or-keyword |
| `expected_revision` | `int \| None` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

## jane_registry.store.MetadataStore.list_packages

**Метод.** Код: [services/registry/src/jane_registry/store.py:182](../../../../../../services/registry/src/jane_registry/store.py#L182).

```python
async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `flt` | `PackageFilter` | `—` | positional-or-keyword |
| `after` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[PackageRecord]`.

## jane_registry.store.MetadataStore.count_forks

**Метод.** Код: [services/registry/src/jane_registry/store.py:185](../../../../../../services/registry/src/jane_registry/store.py#L185).

```python
async def count_forks(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.store.MetadataStore.delete_package_if_empty

**Метод.** Код: [services/registry/src/jane_registry/store.py:186](../../../../../../services/registry/src/jane_registry/store.py#L186).

```python
async def delete_package_if_empty(self, package_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MetadataStore.insert_version

**Метод.** Код: [services/registry/src/jane_registry/store.py:188](../../../../../../services/registry/src/jane_registry/store.py#L188).

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `version` | `VersionRecord` | `—` | positional-or-keyword |
| `max_versions` | `int` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.store.MetadataStore.get_version

**Метод.** Код: [services/registry/src/jane_registry/store.py:189](../../../../../../services/registry/src/jane_registry/store.py#L189).

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord | None`.

## jane_registry.store.MetadataStore.list_versions

**Метод.** Код: [services/registry/src/jane_registry/store.py:190](../../../../../../services/registry/src/jane_registry/store.py#L190).

```python
async def list_versions(self, package_id: str, status: str | None, before_seq: int | None, limit: int) -> list[VersionRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `status` | `str \| None` | `—` | positional-or-keyword |
| `before_seq` | `int \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[VersionRecord]`.

## jane_registry.store.MetadataStore.version_numbers

**Метод.** Код: [services/registry/src/jane_registry/store.py:193](../../../../../../services/registry/src/jane_registry/store.py#L193).

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `list[tuple[str, str]]`.

## jane_registry.store.MetadataStore.count_versions

**Метод.** Код: [services/registry/src/jane_registry/store.py:194](../../../../../../services/registry/src/jane_registry/store.py#L194).

```python
async def count_versions(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.store.MetadataStore.set_status

**Метод.** Код: [services/registry/src/jane_registry/store.py:195](../../../../../../services/registry/src/jane_registry/store.py#L195).

```python
async def set_status(self, package_id: str, version: str, expected: str, entry: dict[str, Any]) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `expected` | `str` | `—` | positional-or-keyword |
| `entry` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.store.MetadataStore.add_test_report

**Метод.** Код: [services/registry/src/jane_registry/store.py:198](../../../../../../services/registry/src/jane_registry/store.py#L198).

```python
async def add_test_report(self, package_id: str, version: str, record: dict[str, Any], test_status: str) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `record` | `dict[str, Any]` | `—` | positional-or-keyword |
| `test_status` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.store.LimitReached

**Клас.** Код: [services/registry/src/jane_registry/store.py:203](../../../../../../services/registry/src/jane_registry/store.py#L203).

```python
class LimitReached(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.store.md#jane_registrystorelimitreached__init__) | Конструктор | ні |
| [count](jane_registry.store.md#jane_registrystorelimitreachedcount) | Поле екземпляра | ні |

## jane_registry.store.LimitReached.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/store.py:204](../../../../../../services/registry/src/jane_registry/store.py#L204).

```python
def __init__(self, count: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `count` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.LimitReached.count

**Поле екземпляра.** Код: [services/registry/src/jane_registry/store.py:206](../../../../../../services/registry/src/jane_registry/store.py#L206).

```python
self.count = count
```

## jane_registry.store.MemoryStore

**Клас.** Код: [services/registry/src/jane_registry/store.py:209](../../../../../../services/registry/src/jane_registry/store.py#L209).

```python
class MemoryStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.store.md#jane_registrystorememorystorename) | Поле | ні |
| [__init__](jane_registry.store.md#jane_registrystorememorystore__init__) | Конструктор | ні |
| [open](jane_registry.store.md#jane_registrystorememorystoreopen) | Метод | ні |
| [close](jane_registry.store.md#jane_registrystorememorystoreclose) | Метод | ні |
| [check](jane_registry.store.md#jane_registrystorememorystorecheck) | Метод | ні |
| [create_package](jane_registry.store.md#jane_registrystorememorystorecreate_package) | Метод | ні |
| [get_package](jane_registry.store.md#jane_registrystorememorystoreget_package) | Метод | ні |
| [update_package](jane_registry.store.md#jane_registrystorememorystoreupdate_package) | Метод | ні |
| [list_packages](jane_registry.store.md#jane_registrystorememorystorelist_packages) | Метод | ні |
| [count_forks](jane_registry.store.md#jane_registrystorememorystorecount_forks) | Метод | ні |
| [delete_package_if_empty](jane_registry.store.md#jane_registrystorememorystoredelete_package_if_empty) | Метод | ні |
| [insert_version](jane_registry.store.md#jane_registrystorememorystoreinsert_version) | Метод | ні |
| [get_version](jane_registry.store.md#jane_registrystorememorystoreget_version) | Метод | ні |
| [list_versions](jane_registry.store.md#jane_registrystorememorystorelist_versions) | Метод | ні |
| [version_numbers](jane_registry.store.md#jane_registrystorememorystoreversion_numbers) | Метод | ні |
| [count_versions](jane_registry.store.md#jane_registrystorememorystorecount_versions) | Метод | ні |
| [set_status](jane_registry.store.md#jane_registrystorememorystoreset_status) | Метод | ні |
| [add_test_report](jane_registry.store.md#jane_registrystorememorystoreadd_test_report) | Метод | ні |

## jane_registry.store.MemoryStore.name

**Поле.** Код: [services/registry/src/jane_registry/store.py:210](../../../../../../services/registry/src/jane_registry/store.py#L210).

```python
name = 'memory'
```

Доступ: читання — так; запис — так.

## jane_registry.store.MemoryStore.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/store.py:212](../../../../../../services/registry/src/jane_registry/store.py#L212).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MemoryStore.open

**Метод.** Код: [services/registry/src/jane_registry/store.py:218](../../../../../../services/registry/src/jane_registry/store.py#L218).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MemoryStore.close

**Метод.** Код: [services/registry/src/jane_registry/store.py:221](../../../../../../services/registry/src/jane_registry/store.py#L221).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MemoryStore.check

**Метод.** Код: [services/registry/src/jane_registry/store.py:224](../../../../../../services/registry/src/jane_registry/store.py#L224).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.store.MemoryStore.create_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:238](../../../../../../services/registry/src/jane_registry/store.py#L238).

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pkg` | `PackageRecord` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

Явні `raise` у тілі: `AlreadyExists`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.store.MemoryStore.get_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:245](../../../../../../services/registry/src/jane_registry/store.py#L245).

```python
async def get_package(self, package_id: str) -> PackageRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `PackageRecord | None`.

## jane_registry.store.MemoryStore.update_package

**Метод.** Код: [services/registry/src/jane_registry/store.py:249](../../../../../../services/registry/src/jane_registry/store.py#L249).

```python
async def update_package(self, package_id: str, changes: dict[str, Any], expected_revision: int | None) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `changes` | `dict[str, Any]` | `—` | positional-or-keyword |
| `expected_revision` | `int \| None` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

Явні `raise` у тілі: `RevisionMismatch`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.store.MemoryStore.list_packages

**Метод.** Код: [services/registry/src/jane_registry/store.py:260](../../../../../../services/registry/src/jane_registry/store.py#L260).

```python
async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `flt` | `PackageFilter` | `—` | positional-or-keyword |
| `after` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[PackageRecord]`.

## jane_registry.store.MemoryStore.count_forks

**Метод.** Код: [services/registry/src/jane_registry/store.py:268](../../../../../../services/registry/src/jane_registry/store.py#L268).

```python
async def count_forks(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.store.MemoryStore.delete_package_if_empty

**Метод.** Код: [services/registry/src/jane_registry/store.py:271](../../../../../../services/registry/src/jane_registry/store.py#L271).

```python
async def delete_package_if_empty(self, package_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.store.MemoryStore.insert_version

**Метод.** Код: [services/registry/src/jane_registry/store.py:276](../../../../../../services/registry/src/jane_registry/store.py#L276).

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `version` | `VersionRecord` | `—` | positional-or-keyword |
| `max_versions` | `int` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `LimitReached`, `VersionExists`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.store.MemoryStore.get_version

**Метод.** Код: [services/registry/src/jane_registry/store.py:293](../../../../../../services/registry/src/jane_registry/store.py#L293).

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord | None`.

## jane_registry.store.MemoryStore.list_versions

**Метод.** Код: [services/registry/src/jane_registry/store.py:297](../../../../../../services/registry/src/jane_registry/store.py#L297).

```python
async def list_versions(self, package_id: str, status: str | None, before_seq: int | None, limit: int) -> list[VersionRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `status` | `str \| None` | `—` | positional-or-keyword |
| `before_seq` | `int \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[VersionRecord]`.

## jane_registry.store.MemoryStore.version_numbers

**Метод.** Код: [services/registry/src/jane_registry/store.py:313](../../../../../../services/registry/src/jane_registry/store.py#L313).

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `list[tuple[str, str]]`.

## jane_registry.store.MemoryStore.count_versions

**Метод.** Код: [services/registry/src/jane_registry/store.py:316](../../../../../../services/registry/src/jane_registry/store.py#L316).

```python
async def count_versions(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.store.MemoryStore.set_status

**Метод.** Код: [services/registry/src/jane_registry/store.py:319](../../../../../../services/registry/src/jane_registry/store.py#L319).

```python
async def set_status(self, package_id: str, version: str, expected: str, entry: dict[str, Any]) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `expected` | `str` | `—` | positional-or-keyword |
| `entry` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `StatusMismatch`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.store.MemoryStore.add_test_report

**Метод.** Код: [services/registry/src/jane_registry/store.py:334](../../../../../../services/registry/src/jane_registry/store.py#L334).

```python
async def add_test_report(self, package_id: str, version: str, record: dict[str, Any], test_status: str) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `record` | `dict[str, Any]` | `—` | positional-or-keyword |
| `test_status` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord`.
