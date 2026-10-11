# Модуль `jane_assistant.packages`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/packages.py](../../../../../services/assistant/src/jane_assistant/packages.py). Не редагуйте вручну.

Package drafts built by the assistant (``jane-handler-package`` skill, ``package-manifest.schema.json``).

The manifest is always assembled by the assistant, never taken from the model: the model only supplies code, the entity schema and expected outputs. Tests are package files (``tests/<case>/material.json`` + ``expected.json``) so the package stays usable without the registry; problem samples become tests with ``origin: problem_sample``.

## Зміст

- [Клас `PackageDraft`](#клас-packagedraft)
- [Функція `bump`](#функція-bump)
- [Функція `case_name`](#функція-case_name)
- [Функція `collector_rules_draft`](#функція-collector_rules_draft)
- [Функція `extractor_draft`](#функція-extractor_draft)
- [Функція `slug`](#функція-slug)

## Класи

### Клас `PackageDraft`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.packages` |
| Код | [packages.py:123](../../../../../services/assistant/src/jane_assistant/packages.py#L123) |

```python
@dataclass
class PackageDraft: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `manifest` | `dict[str, Any]` | — | читання й запис |  |
| `files` | `dict[str, bytes]` | `field(default_factory=dict)` | читання й запис |  |
| `ref` | `dict[str, str]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `PackageDraft.copy`

```python
def copy(self) -> PackageDraft: ...
```

Код: [packages.py:131](../../../../../services/assistant/src/jane_assistant/packages.py#L131).

#### Метод `PackageDraft.add_test`

```python
def add_test(
    self,
    name: str,
    material: dict[str, Any],
    expected_status: str,
    entities: list[dict[str, Any]] | None,
    origin: str,
) -> str: ...
```

Код: [packages.py:134](../../../../../services/assistant/src/jane_assistant/packages.py#L134).

#### Метод `PackageDraft.publish_body`

```python
def publish_body(self) -> dict[str, Any]: ...
```

``registry.v1`` ``PublishRequest``: manifest + files (jane-package.json comes from manifest).

Код: [packages.py:165](../../../../../services/assistant/src/jane_assistant/packages.py#L165).

#### Метод `PackageDraft.proposal`

```python
def proposal(
    self,
    base: PackageDraft,
    based_on: dict[str, str],
    *,
    schema_change: str,
    change_summary: str,
    max_bytes: int,
) -> dict[str, Any]: ...
```

``assistant.v1`` ``ImprovementProposal``: this unpublished version as changes against ``base``.

The whole proposal - as compact UTF-8 JSON - stays within ``max_bytes`` whenever its required part (``based_on``, ``version``, ``manifest``...) fits. In that budget come, in this order: changed code and schema files (``src/``, ``schemas/``, in the form of ``PublishRequest.files``), the unified ``diff`` of the changed text files under ``src/`` and ``schemas/`` (cut with a marker if needed), then test fixtures and other files. A file that does not fit is named in ``omitted_files`` (room for these names is reserved).

Код: [packages.py:170](../../../../../services/assistant/src/jane_assistant/packages.py#L170).

#### Метод `PackageDraft.archive`

```python
def archive(self) -> bytes: ...
```

Deterministic, deflated zip (sorted paths, fixed timestamps) with ``jane-package.json``.

It only carries an unpublished draft to handler-runtime test runs (inline, up to ``transfer.inline_max_bytes``); the registry stores and digests its own canonical (stored) zip of the published files. Each entry is deflated explicitly: a ``ZipInfo`` entry would otherwise be stored, and test fixtures of real pages (a reduced shop page is ~130 KB) did not fit the inline limit.

Код: [packages.py:234](../../../../../services/assistant/src/jane_assistant/packages.py#L234).

#### Метод `PackageDraft.content_ref`

```python
def content_ref(self) -> dict[str, Any]: ...
```

Код: [packages.py:252](../../../../../services/assistant/src/jane_assistant/packages.py#L252).

#### Метод `PackageDraft.from_files`

```python
@classmethod
def from_files(cls, files: dict[str, bytes]) -> PackageDraft: ...
```

Код: [packages.py:256](../../../../../services/assistant/src/jane_assistant/packages.py#L256).

#### Метод `PackageDraft.text`

```python
def text(self, path: str) -> str: ...
```

Код: [packages.py:260](../../../../../services/assistant/src/jane_assistant/packages.py#L260).

## Функції

### Функція `bump`

```python
def bump(version: str, part: str) -> str: ...
```

Код: [packages.py:51](../../../../../services/assistant/src/jane_assistant/packages.py#L51).

### Функція `case_name`

```python
def case_name(text: str) -> str: ...
```

Код: [packages.py:47](../../../../../services/assistant/src/jane_assistant/packages.py#L47).

### Функція `collector_rules_draft`

```python
def collector_rules_draft(
    *,
    package_id: str,
    version: str,
    title: str,
    rules: dict[str, Any],
    job_id: str,
    model: dict[str, str],
) -> PackageDraft: ...
```

Код: [packages.py:332](../../../../../services/assistant/src/jane_assistant/packages.py#L332).

### Функція `extractor_draft`

```python
def extractor_draft(
    *,
    package_id: str,
    version: str,
    title: str,
    entity_type: str,
    key_fields: list[str],
    entity_schema: dict[str, Any],
    module_code: str,
    domains: list[str],
    source_kind: str,
    media_types: list[str],
    job_id: str,
    model: dict[str, str],
    reason: str,
    based_on: dict[str, str] | None = None,
    change_summary: str | None = None,
) -> PackageDraft: ...
```

Код: [packages.py:264](../../../../../services/assistant/src/jane_assistant/packages.py#L264).

### Функція `slug`

```python
def slug(text: str, max_len: int = 100) -> str: ...
```

Код: [packages.py:42](../../../../../services/assistant/src/jane_assistant/packages.py#L42).
