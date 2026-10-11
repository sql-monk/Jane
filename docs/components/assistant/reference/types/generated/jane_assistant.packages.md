# jane_assistant.packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.packages.slug](#jane_assistantpackagesslug)
- [jane_assistant.packages.case_name](#jane_assistantpackagescase_name)
- [jane_assistant.packages.bump](#jane_assistantpackagesbump)
- [jane_assistant.packages.PackageDraft](#jane_assistantpackagespackagedraft)
- [jane_assistant.packages.PackageDraft.__init__](#jane_assistantpackagespackagedraft__init__)
- [jane_assistant.packages.PackageDraft.manifest](#jane_assistantpackagespackagedraftmanifest)
- [jane_assistant.packages.PackageDraft.files](#jane_assistantpackagespackagedraftfiles)
- [jane_assistant.packages.PackageDraft.ref](#jane_assistantpackagespackagedraftref)
- [jane_assistant.packages.PackageDraft.copy](#jane_assistantpackagespackagedraftcopy)
- [jane_assistant.packages.PackageDraft.add_test](#jane_assistantpackagespackagedraftadd_test)
- [jane_assistant.packages.PackageDraft.publish_body](#jane_assistantpackagespackagedraftpublish_body)
- [jane_assistant.packages.PackageDraft.proposal](#jane_assistantpackagespackagedraftproposal)
- [jane_assistant.packages.PackageDraft.archive](#jane_assistantpackagespackagedraftarchive)
- [jane_assistant.packages.PackageDraft.content_ref](#jane_assistantpackagespackagedraftcontent_ref)
- [jane_assistant.packages.PackageDraft.from_files](#jane_assistantpackagespackagedraftfrom_files)
- [jane_assistant.packages.PackageDraft.text](#jane_assistantpackagespackagedrafttext)
- [jane_assistant.packages.extractor_draft](#jane_assistantpackagesextractor_draft)
- [jane_assistant.packages.collector_rules_draft](#jane_assistantpackagescollector_rules_draft)

## jane_assistant.packages.slug

**Функція.** Код: [services/assistant/src/jane_assistant/packages.py:42](../../../../../../services/assistant/src/jane_assistant/packages.py#L42).

```python
def slug(text: str, max_len: int=100) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `max_len` | `int` | `100` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:149](../../../../../../services/assistant/tests/test_units.py#L149).

```python
assert slug("Shop.Example.TEST") == "shop.example.test" and slug("@@") == "source"
```

## jane_assistant.packages.case_name

**Функція.** Код: [services/assistant/src/jane_assistant/packages.py:47](../../../../../../services/assistant/src/jane_assistant/packages.py#L47).

```python
def case_name(text: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_assistant.packages.bump

**Функція.** Код: [services/assistant/src/jane_assistant/packages.py:51](../../../../../../services/assistant/src/jane_assistant/packages.py#L51).

```python
def bump(version: str, part: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `version` | `str` | `—` | positional-or-keyword |
| `part` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:144](../../../../../../services/assistant/tests/test_units.py#L144).

```python
assert (
        bump("1.2.3", "patch") == "1.2.4"
        and bump("1.2.3", "minor") == "1.3.0"
        and bump("1.2.3", "major") == "2.0.0"
    )
```

## jane_assistant.packages.PackageDraft

**Клас.** Код: [services/assistant/src/jane_assistant/packages.py:123](../../../../../../services/assistant/src/jane_assistant/packages.py#L123).

```python
class PackageDraft:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [manifest](jane_assistant.packages.md#jane_assistantpackagespackagedraftmanifest) | Поле | ні |
| [files](jane_assistant.packages.md#jane_assistantpackagespackagedraftfiles) | Поле | ні |
| [ref](jane_assistant.packages.md#jane_assistantpackagespackagedraftref) | Властивість | ні |
| [copy](jane_assistant.packages.md#jane_assistantpackagespackagedraftcopy) | Метод | ні |
| [add_test](jane_assistant.packages.md#jane_assistantpackagespackagedraftadd_test) | Метод | ні |
| [publish_body](jane_assistant.packages.md#jane_assistantpackagespackagedraftpublish_body) | Метод | ні |
| [proposal](jane_assistant.packages.md#jane_assistantpackagespackagedraftproposal) | Метод | ні |
| [archive](jane_assistant.packages.md#jane_assistantpackagespackagedraftarchive) | Метод | ні |
| [content_ref](jane_assistant.packages.md#jane_assistantpackagespackagedraftcontent_ref) | Метод | ні |
| [from_files](jane_assistant.packages.md#jane_assistantpackagespackagedraftfrom_files) | Метод | ні |
| [text](jane_assistant.packages.md#jane_assistantpackagespackagedrafttext) | Метод | ні |
| [__init__](jane_assistant.packages.md#jane_assistantpackagespackagedraft__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:116](../../../../../../services/assistant/tests/test_units.py#L116).

```python
d = PackageDraft({"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"x"})
```

Контекст і передумови: [services/assistant/tests/test_units.py:290](../../../../../../services/assistant/tests/test_units.py#L290).

```python
draft = PackageDraft(
        {"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"\x00code"}
    )
```

## jane_assistant.packages.PackageDraft.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/packages.py:123](../../../../../../services/assistant/src/jane_assistant/packages.py#L123).

```python
def __init__(self, manifest: dict[str, Any], files: dict[str, bytes] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:116](../../../../../../services/assistant/tests/test_units.py#L116).

```python
d = PackageDraft({"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"x"})
```

Контекст і передумови: [services/assistant/tests/test_units.py:290](../../../../../../services/assistant/tests/test_units.py#L290).

```python
draft = PackageDraft(
        {"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"\x00code"}
    )
```

## jane_assistant.packages.PackageDraft.manifest

**Поле.** Код: [services/assistant/src/jane_assistant/packages.py:124](../../../../../../services/assistant/src/jane_assistant/packages.py#L124).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:336](../../../../../../services/assistant/tests/test_units.py#L336).

```python
draft.manifest["version"] = "1.0.1"
```

## jane_assistant.packages.PackageDraft.files

**Поле.** Код: [services/assistant/src/jane_assistant/packages.py:125](../../../../../../services/assistant/src/jane_assistant/packages.py#L125).

```python
files: dict[str, bytes] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:338](../../../../../../services/assistant/tests/test_units.py#L338).

```python
draft.files["src/m/main.py"] = code.encode()
```

Контекст і передумови: [services/assistant/tests/test_units.py:339](../../../../../../services/assistant/tests/test_units.py#L339).

```python
draft.files["tests/case/material.json"] = json.dumps({"text": "ж" * 400}, ensure_ascii=False).encode()
```

## jane_assistant.packages.PackageDraft.ref

**Властивість.** Код: [services/assistant/src/jane_assistant/packages.py:128](../../../../../../services/assistant/src/jane_assistant/packages.py#L128).

```python
def ref(self) -> dict[str, str]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

Доступ: читання — так; запис — ні.

## jane_assistant.packages.PackageDraft.copy

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:131](../../../../../../services/assistant/src/jane_assistant/packages.py#L131).

```python
def copy(self) -> PackageDraft:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `PackageDraft`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:335](../../../../../../services/assistant/tests/test_units.py#L335).

```python
draft = base.copy()
```

Контекст і передумови: [services/assistant/tests/test_units.py:136](../../../../../../services/assistant/tests/test_units.py#L136).

```python
assert d.archive() == d.copy().archive()
```

## jane_assistant.packages.PackageDraft.add_test

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:134](../../../../../../services/assistant/src/jane_assistant/packages.py#L134).

```python
def add_test(self, name: str, material: dict[str, Any], expected_status: str, entities: list[dict[str, Any]] | None, origin: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `expected_status` | `str` | `—` | positional-or-keyword |
| `entities` | `list[dict[str, Any]] \| None` | `—` | positional-or-keyword |
| `origin` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:123](../../../../../../services/assistant/tests/test_units.py#L123).

```python
name = d.add_test(
        "my case!",
        mat,
        "success",
        [{"entity_type": "t", "fields": {"a": 1}, "observation": {}}],
        "problem_sample",
    )
```

Контекст і передумови: [services/assistant/tests/test_units.py:130](../../../../../../services/assistant/tests/test_units.py#L130).

```python
again = d.add_test("my case!", mat, "empty", None, "llm")
```

## jane_assistant.packages.PackageDraft.publish_body

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:165](../../../../../../services/assistant/src/jane_assistant/packages.py#L165).

```python
def publish_body(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``registry.v1`` ``PublishRequest``: manifest + files (jane-package.json comes from manifest).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:142](../../../../../../services/assistant/tests/test_units.py#L142).

```python
body = d.publish_body()
```

## jane_assistant.packages.PackageDraft.proposal

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:170](../../../../../../services/assistant/src/jane_assistant/packages.py#L170).

```python
def proposal(self, base: PackageDraft, based_on: dict[str, str], *, schema_change: str, change_summary: str, max_bytes: int) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `base` | `PackageDraft` | `—` | positional-or-keyword |
| `based_on` | `dict[str, str]` | `—` | positional-or-keyword |
| `schema_change` | `str` | `—` | keyword-only |
| `change_summary` | `str` | `—` | keyword-only |
| `max_bytes` | `int` | `—` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``assistant.v1`` ``ImprovementProposal``: this unpublished version as changes against ``base``.

The whole proposal - as compact UTF-8 JSON - stays within ``max_bytes`` whenever its required part
(``based_on``, ``version``, ``manifest``...) fits. In that budget come, in this order: changed code and schema
files (``src/``, ``schemas/``, in the form of ``PublishRequest.files``), the unified ``diff`` of the changed
text files under ``src/`` and ``schemas/`` (cut with a marker if needed), then test fixtures and other files.
A file that does not fit is named in ``omitted_files`` (room for these names is reserved).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:343](../../../../../../services/assistant/tests/test_units.py#L343).

```python
return draft.proposal(
            base, based_on, schema_change="none", change_summary="зміна", max_bytes=max_bytes
        )
```

## jane_assistant.packages.PackageDraft.archive

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:234](../../../../../../services/assistant/src/jane_assistant/packages.py#L234).

```python
def archive(self) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Deterministic, deflated zip (sorted paths, fixed timestamps) with ``jane-package.json``.

It only carries an unpublished draft to handler-runtime test runs (inline, up to
``transfer.inline_max_bytes``); the registry stores and digests its own canonical (stored) zip of the
published files. Each entry is deflated explicitly: a ``ZipInfo`` entry would otherwise be stored, and
test fixtures of real pages (a reduced shop page is ~130 KB) did not fit the inline limit.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:136](../../../../../../services/assistant/tests/test_units.py#L136).

```python
assert d.archive() == d.copy().archive()
```

Контекст і передумови: [services/assistant/tests/test_units.py:141](../../../../../../services/assistant/tests/test_units.py#L141).

```python
assert raw > 180_000 and len(d.archive()) < raw // 20
```

## jane_assistant.packages.PackageDraft.content_ref

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:252](../../../../../../services/assistant/src/jane_assistant/packages.py#L252).

```python
def content_ref(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.packages.PackageDraft.from_files

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:256](../../../../../../services/assistant/src/jane_assistant/packages.py#L256).

```python
def from_files(cls, files: dict[str, bytes]) -> PackageDraft:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |

Результат: `PackageDraft`.

## jane_assistant.packages.PackageDraft.text

**Метод.** Код: [services/assistant/src/jane_assistant/packages.py:260](../../../../../../services/assistant/src/jane_assistant/packages.py#L260).

```python
def text(self, path: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_assistant.packages.extractor_draft

**Функція.** Код: [services/assistant/src/jane_assistant/packages.py:264](../../../../../../services/assistant/src/jane_assistant/packages.py#L264).

```python
def extractor_draft(*, package_id: str, version: str, title: str, entity_type: str, key_fields: list[str], entity_schema: dict[str, Any], module_code: str, domains: list[str], source_kind: str, media_types: list[str], job_id: str, model: dict[str, str], reason: str, based_on: dict[str, str] | None=None, change_summary: str | None=None) -> PackageDraft:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | keyword-only |
| `version` | `str` | `—` | keyword-only |
| `title` | `str` | `—` | keyword-only |
| `entity_type` | `str` | `—` | keyword-only |
| `key_fields` | `list[str]` | `—` | keyword-only |
| `entity_schema` | `dict[str, Any]` | `—` | keyword-only |
| `module_code` | `str` | `—` | keyword-only |
| `domains` | `list[str]` | `—` | keyword-only |
| `source_kind` | `str` | `—` | keyword-only |
| `media_types` | `list[str]` | `—` | keyword-only |
| `job_id` | `str` | `—` | keyword-only |
| `model` | `dict[str, str]` | `—` | keyword-only |
| `reason` | `str` | `—` | keyword-only |
| `based_on` | `dict[str, str] \| None` | `None` | keyword-only |
| `change_summary` | `str \| None` | `None` | keyword-only |

Результат: `PackageDraft`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_improvement.py:30](../../../../../../services/assistant/tests/test_improvement.py#L30).

```python
draft = extractor_draft(
        package_id=PKG,
        version="1.2.0",
        title="Product cards",
        entity_type="product",
        key_fields=["sku"],
        entity_schema={"type": "object", "properties": {"sku": {"type": "string"}}},
        module_code=PRODUCT_CODE_V1,
        domains=["shop.example.test"],
        source_kind="web",
        media_types=["text/html"],
        job_id="seed",
        model={},
        reason="onboarding",
    )
```

Контекст і передумови: [services/assistant/tests/test_onboarding.py:41](../../../../../../services/assistant/tests/test_onboarding.py#L41).

```python
draft = extractor_draft(
        package_id=package_id,
        version="1.2.0",
        title="Generic product cards",
        entity_type="product",
        key_fields=["sku"],
        entity_schema={"type": "object", "properties": {"sku": {"type": "string"}}},
        module_code=code,
        domains=domains or [],
        source_kind="web",
        media_types=["text/html"],
        job_id="seed",
        model={},
        reason="onboarding",
    )
```

## jane_assistant.packages.collector_rules_draft

**Функція.** Код: [services/assistant/src/jane_assistant/packages.py:332](../../../../../../services/assistant/src/jane_assistant/packages.py#L332).

```python
def collector_rules_draft(*, package_id: str, version: str, title: str, rules: dict[str, Any], job_id: str, model: dict[str, str]) -> PackageDraft:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | keyword-only |
| `version` | `str` | `—` | keyword-only |
| `title` | `str` | `—` | keyword-only |
| `rules` | `dict[str, Any]` | `—` | keyword-only |
| `job_id` | `str` | `—` | keyword-only |
| `model` | `dict[str, str]` | `—` | keyword-only |

Результат: `PackageDraft`.
