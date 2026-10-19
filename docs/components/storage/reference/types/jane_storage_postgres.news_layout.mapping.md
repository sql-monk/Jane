# Модуль `jane_storage_postgres.news_layout.mapping`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py). Не редагуйте вручну.

Pure mapping of an entity snapshot to the rows of the ``news`` layout (no database).

Rules (``docs/delivery/news-pg.md``, section 3):

* a field missing from the snapshot (also a cleared one) gives ``NULL``;
* an unknown field — at the top level or inside a known object — and a value that does not fit the column type (a number in a text column, an unparsable time, …) go to ``extra`` under the field path (``published_at``, ``event.canonical.foo``, ``tags[2]``, ``entities[0].evidence[1].foo``); the column is then ``NULL``. JSON ``null`` is ``NULL`` without an ``extra`` entry. Values are never dropped;
* lists keep the original index as ``position``: an item that gives no row (wrong type, ``null``) goes to ``extra`` and leaves a gap instead of shifting the following items.

## Зміст

- [Клас `EntityRows`](#клас-entityrows)
- [Клас `EvidenceRow`](#клас-evidencerow)
- [Клас `MentionRow`](#клас-mentionrow)
- [Клас `SourceRow`](#клас-sourcerow)
- [Функція `map_snapshot`](#функція-map_snapshot)
- [Функція `parse_date`](#функція-parse_date)
- [Функція `parse_time`](#функція-parse_time)
- [Функція `parse_timestamp`](#функція-parse_timestamp)

## Класи

### Клас `EntityRows`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage_postgres.news_layout.mapping` |
| Код | [mapping.py:117](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L117) |

```python
@dataclass(frozen=True)
class EntityRows: ...
```

Everything one snapshot gives to the projection.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entity_type` | `str` | — | читання |  |
| `table` | `str` | — | читання |  |
| `id_column` | `str` | — | читання |  |
| `columns` | `dict[str, Any]` | — | читання | Parent row without the surrogate id: ``canonical_key``, data columns, ``version``, ``updated_at``, ``extra``. |
| `source` | `SourceRow \| None` | `None` | читання |  |
| `tags` | `list[tuple[int, str]]` | `field(default_factory=list)` | читання |  |
| `links` | `list[tuple[int, str]]` | `field(default_factory=list)` | читання |  |
| `topics` | `list[tuple[int, str]]` | `field(default_factory=list)` | читання |  |
| `locations` | `list[tuple[int, str]]` | `field(default_factory=list)` | читання |  |
| `event` | `dict[str, Any] \| None` | `None` | читання | ``news_article_event`` row without ``news_article_id``; ``None`` when the snapshot has no ``event``. |
| `mentions` | `list[MentionRow]` | `field(default_factory=list)` | читання |  |
| `evidence` | `list[EvidenceRow]` | `field(default_factory=list)` | читання |  |
| `extra` | `dict[str, Any]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `EvidenceRow`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage_postgres.news_layout.mapping` |
| Код | [mapping.py:105](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L105) |

```python
@dataclass(frozen=True)
class EvidenceRow: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `subject` | `str` | — | читання | ``event``, ``event_time``, ``sentiment`` or ``mention``. |
| `position` | `int` | — | читання |  |
| `quote` | `str \| None` | — | читання |  |
| `reason` | `str \| None` | — | читання |  |
| `attribution` | `str \| None` | — | читання |  |
| `mention_position` | `int \| None` | `None` | читання | Position of the mention in ``entities`` (``subject == "mention"``). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `MentionRow`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage_postgres.news_layout.mapping` |
| Код | [mapping.py:93](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L93) |

```python
@dataclass(frozen=True)
class MentionRow: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `position` | `int` | — | читання |  |
| `canonical_name` | `str \| None` | — | читання |  |
| `entity_kind` | `str \| None` | — | читання |  |
| `name` | `str \| None` | — | читання |  |
| `role` | `str \| None` | — | читання |  |
| `attitude` | `str \| None` | — | читання |  |
| `attitude_confidence` | `float \| None` | — | читання |  |
| `factual_impact` | `str \| None` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `SourceRow`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage_postgres.news_layout.mapping` |
| Код | [mapping.py:81](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L81) |

```python
@dataclass(frozen=True)
class SourceRow: ...
```

Upsert of ``source``: ``None`` never overwrites a stored value; ``seen_at`` widens first/last seen.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `source_id` | `str` | — | читання |  |
| `kind` | `str \| None` | — | читання |  |
| `name` | `str \| None` | — | читання |  |
| `site` | `str \| None` | — | читання |  |
| `channel` | `str \| None` | — | читання |  |
| `seen_at` | `datetime` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `map_snapshot`

```python
def map_snapshot(snapshot: EntitySnapshot) -> EntityRows | None: ...
```

Rows of the projection for ``snapshot``; ``None`` for a type the layout does not project.

Код: [mapping.py:595](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L595).

### Функція `parse_date`

```python
def parse_date(value: str) -> date | None: ...
```

Код: [mapping.py:66](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L66).

### Функція `parse_time`

```python
def parse_time(value: str) -> time | None: ...
```

``HH:MM`` or ``HH:MM:SS``.

Код: [mapping.py:75](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L75).

### Функція `parse_timestamp`

```python
def parse_timestamp(value: str) -> datetime | None: ...
```

Strict RFC 3339 date-time with an offset → aware ``datetime`` (UTC); ``None`` when it does not fit.

More than six fractional digits fit only when the extra digits are zeros (``timestamptz`` keeps microseconds).

Код: [mapping.py:48](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/mapping.py#L48).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `PROJECTED_TYPES` | `frozenset[str]` | `frozenset({'article', 'post', 'news_article', 'news_event'})` |  |
