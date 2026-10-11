# jane_kit.rules

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.rules.STRATEGY_DEFS](#jane_kitrulesstrategy_defs)
- [jane_kit.rules.header_value_safe](#jane_kitrulesheader_value_safe)
- [jane_kit.rules.CollectorSchemas](#jane_kitrulescollectorschemas)
- [jane_kit.rules.CollectorSchemas.__init__](#jane_kitrulescollectorschemas__init__)
- [jane_kit.rules.CollectorSchemas.rules_uri](#jane_kitrulescollectorschemasrules_uri)
- [jane_kit.rules.CollectorSchemas.locate_collector](#jane_kitrulescollectorschemaslocate_collector)
- [jane_kit.rules.CollectorSchemas.errors](#jane_kitrulescollectorschemaserrors)
- [jane_kit.rules.CollectorSchemas.rules_errors](#jane_kitrulescollectorschemasrules_errors)
- [jane_kit.rules.RulesReport](#jane_kitrulesrulesreport)
- [jane_kit.rules.RulesReport.__init__](#jane_kitrulesrulesreport__init__)
- [jane_kit.rules.RulesReport.valid](#jane_kitrulesrulesreportvalid)
- [jane_kit.rules.RulesReport.supported](#jane_kitrulesrulesreportsupported)
- [jane_kit.rules.RulesReport.errors](#jane_kitrulesrulesreporterrors)
- [jane_kit.rules.RulesReport.warnings](#jane_kitrulesrulesreportwarnings)
- [jane_kit.rules.RulesReport.wire](#jane_kitrulesrulesreportwire)
- [jane_kit.rules.RulesLoader](#jane_kitrulesrulesloader)
- [jane_kit.rules.RulesLoader.__init__](#jane_kitrulesrulesloader__init__)
- [jane_kit.rules.RulesLoader.rules_dir](#jane_kitrulesrulesloaderrules_dir)
- [jane_kit.rules.RulesLoader.registry_url](#jane_kitrulesrulesloaderregistry_url)
- [jane_kit.rules.RulesLoader.registry_token_env](#jane_kitrulesrulesloaderregistry_token_env)
- [jane_kit.rules.RulesLoader.timeout_s](#jane_kitrulesrulesloadertimeout_s)
- [jane_kit.rules.RulesLoader.settings_prefix](#jane_kitrulesrulesloadersettings_prefix)
- [jane_kit.rules.RulesLoader.sources](#jane_kitrulesrulesloadersources)
- [jane_kit.rules.RulesLoader.load](#jane_kitrulesrulesloaderload)

## jane_kit.rules.STRATEGY_DEFS

**Константа.** Код: [libs/jane-kit/src/jane_kit/rules.py:46](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L46).

```python
STRATEGY_DEFS = {'seed_list': 'SeedListStrategy', 'recursive': 'RecursiveStrategy', 'sitemap': 'SitemapStrategy', 'feed': 'FeedStrategy', 'listing': 'ListingStrategy', 'url_template': 'UrlTemplateStrategy', 'api_feed': 'ApiFeedStrategy', 'llm_explore': 'LlmExploreStrategy'}
```

### Опис із вихідного коду

```text
``strategies[].type`` -> ``$defs`` branch of ``collector-rules.schema.json``.
```

## jane_kit.rules.header_value_safe

**Функція.** Код: [libs/jane-kit/src/jane_kit/rules.py:61](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L61).

```python
def header_value_safe(value: object) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `object` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
HTTP header values must be visible ASCII, with no control characters to reach error text.
```

## jane_kit.rules.CollectorSchemas

**Клас.** Код: [libs/jane-kit/src/jane_kit/rules.py:71](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L71).

```python
class CollectorSchemas(ContractSchemas):
```

Базові типи / інтерфейси: `ContractSchemas`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.rules.md#jane_kitrulescollectorschemas__init__) | Конструктор | ні |
| [rules_uri](jane_kit.rules.md#jane_kitrulescollectorschemasrules_uri) | Поле екземпляра | ні |
| [locate_collector](jane_kit.rules.md#jane_kitrulescollectorschemaslocate_collector) | Метод | ні |
| [errors](jane_kit.rules.md#jane_kitrulescollectorschemaserrors) | Метод | ні |
| [rules_errors](jane_kit.rules.md#jane_kitrulescollectorschemasrules_errors) | Метод | ні |
| [root](jane_kit.schemas.md#jane_kitschemascontractschemasroot) | Поле екземпляра | так |
| [schemas_dir](jane_kit.schemas.md#jane_kitschemascontractschemasschemas_dir) | Поле екземпляра | так |
| [spec](jane_kit.schemas.md#jane_kitschemascontractschemasspec) | Поле екземпляра | так |
| [registry](jane_kit.schemas.md#jane_kitschemascontractschemasregistry) | Поле екземпляра | так |
| [format_checker](jane_kit.schemas.md#jane_kitschemascontractschemasformat_checker) | Поле екземпляра | так |
| [locate](jane_kit.schemas.md#jane_kitschemascontractschemaslocate) | Метод | так |
| [uri](jane_kit.schemas.md#jane_kitschemascontractschemasuri) | Метод | так |
| [component](jane_kit.schemas.md#jane_kitschemascontractschemascomponent) | Метод | так |
| [request_schema_uri](jane_kit.schemas.md#jane_kitschemascontractschemasrequest_schema_uri) | Метод | так |
| [validator](jane_kit.schemas.md#jane_kitschemascontractschemasvalidator) | Метод | так |
| [iter_errors](jane_kit.schemas.md#jane_kitschemascontractschemasiter_errors) | Метод | так |
| [field_errors](jane_kit.schemas.md#jane_kitschemascontractschemasfield_errors) | Метод | так |
| [validate](jane_kit.schemas.md#jane_kitschemascontractschemasvalidate) | Метод | так |

### Опис із вихідного коду

```text
``collector.v1`` and ``collector-rules.schema.json`` validators (see the module docstring).
```

## jane_kit.rules.CollectorSchemas.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/rules.py:74](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L74).

```python
def __init__(self, root: Path, *, openapi: str | None='collector.v1.yaml', format_check: bool=False) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `openapi` | `str \| None` | `'collector.v1.yaml'` | keyword-only |
| `format_check` | `bool` | `False` | keyword-only |

Результат: `None`.

## jane_kit.rules.CollectorSchemas.rules_uri

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:78](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L78).

```python
self.rules_uri = self.uri('collector-rules.schema.json').rstrip('#')
```

## jane_kit.rules.CollectorSchemas.locate_collector

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:81](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L81).

```python
def locate_collector(cls, configured: Path | None, *, setting: str, start: Path | None=None) -> Self:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `configured` | `Path \| None` | `—` | positional-or-keyword |
| `setting` | `str` | `—` | keyword-only |
| `start` | `Path \| None` | `None` | keyword-only |

Результат: `Self`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:69](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L69).

```python
schemas = CollectorSchemas.locate_collector(None, setting="S", start=Path(__file__).parent)
```

## jane_kit.rules.CollectorSchemas.errors

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:84](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L84).

```python
def errors(self, uri: str, instance: Any, prefix: Sequence[Any]=()) -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `uri` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `Sequence[Any]` | `()` | positional-or-keyword |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
Field errors with the pointer ``prefix`` + instance path (empty for the root).
```

## jane_kit.rules.CollectorSchemas.rules_errors

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:107](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L107).

```python
def rules_errors(self, rules: Any, prefix: Sequence[Any]=()) -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rules` | `Any` | `—` | positional-or-keyword |
| `prefix` | `Sequence[Any]` | `()` | positional-or-keyword |

Результат: `list[FieldError]`.

## jane_kit.rules.RulesReport

**Клас.** Код: [libs/jane-kit/src/jane_kit/rules.py:112](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L112).

```python
class RulesReport:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [valid](jane_kit.rules.md#jane_kitrulesrulesreportvalid) | Поле | ні |
| [supported](jane_kit.rules.md#jane_kitrulesrulesreportsupported) | Поле | ні |
| [errors](jane_kit.rules.md#jane_kitrulesrulesreporterrors) | Поле | ні |
| [warnings](jane_kit.rules.md#jane_kitrulesrulesreportwarnings) | Поле | ні |
| [wire](jane_kit.rules.md#jane_kitrulesrulesreportwire) | Метод | ні |
| [__init__](jane_kit.rules.md#jane_kitrulesrulesreport__init__) | Конструктор dataclass | ні |

## jane_kit.rules.RulesReport.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/rules.py:112](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L112).

```python
def __init__(self, valid: bool, supported: bool, errors: list[FieldError], warnings: list[FieldError]) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `valid` | `bool` | `—` | positional-or-keyword |
| `supported` | `bool` | `—` | positional-or-keyword |
| `errors` | `list[FieldError]` | `—` | positional-or-keyword |
| `warnings` | `list[FieldError]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.rules.RulesReport.valid

**Поле.** Код: [libs/jane-kit/src/jane_kit/rules.py:113](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L113).

```python
valid: bool
```

Доступ: читання — так; запис — так.

## jane_kit.rules.RulesReport.supported

**Поле.** Код: [libs/jane-kit/src/jane_kit/rules.py:114](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L114).

```python
supported: bool
```

Доступ: читання — так; запис — так.

## jane_kit.rules.RulesReport.errors

**Поле.** Код: [libs/jane-kit/src/jane_kit/rules.py:115](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L115).

```python
errors: list[FieldError]
```

Доступ: читання — так; запис — так.

## jane_kit.rules.RulesReport.warnings

**Поле.** Код: [libs/jane-kit/src/jane_kit/rules.py:116](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L116).

```python
warnings: list[FieldError]
```

Доступ: читання — так; запис — так.

## jane_kit.rules.RulesReport.wire

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:118](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L118).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_kit.rules.RulesLoader

**Клас.** Код: [libs/jane-kit/src/jane_kit/rules.py:133](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L133).

```python
class RulesLoader:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.rules.md#jane_kitrulesrulesloader__init__) | Конструктор | ні |
| [rules_dir](jane_kit.rules.md#jane_kitrulesrulesloaderrules_dir) | Поле екземпляра | ні |
| [registry_url](jane_kit.rules.md#jane_kitrulesrulesloaderregistry_url) | Поле екземпляра | ні |
| [registry_token_env](jane_kit.rules.md#jane_kitrulesrulesloaderregistry_token_env) | Поле екземпляра | ні |
| [timeout_s](jane_kit.rules.md#jane_kitrulesrulesloadertimeout_s) | Поле екземпляра | ні |
| [settings_prefix](jane_kit.rules.md#jane_kitrulesrulesloadersettings_prefix) | Поле екземпляра | ні |
| [sources](jane_kit.rules.md#jane_kitrulesrulesloadersources) | Метод | ні |
| [load](jane_kit.rules.md#jane_kitrulesrulesloaderload) | Метод | ні |

### Опис із вихідного коду

```text
Rules of a ``rules_ref`` (see the module docstring); ``settings_prefix`` (``JANE_WEB_COLLECTOR_``) names
the settings in error messages.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:97](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L97).

```python
loader = RulesLoader(
        rules_dir=tmp_path / "rules",
        registry_url=None,
        registry_token_env=None,
        timeout_s=1,
        settings_prefix="JANE_T_",
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:113](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L113).

```python
zipped = RulesLoader(rules_dir=archive.parent, registry_url=None, registry_token_env=None, timeout_s=1)
```

## jane_kit.rules.RulesLoader.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/rules.py:137](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L137).

```python
def __init__(self, *, rules_dir: Path | None, registry_url: str | None, registry_token_env: str | None, timeout_s: float, settings_prefix: str='') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rules_dir` | `Path \| None` | `—` | keyword-only |
| `registry_url` | `str \| None` | `—` | keyword-only |
| `registry_token_env` | `str \| None` | `—` | keyword-only |
| `timeout_s` | `float` | `—` | keyword-only |
| `settings_prefix` | `str` | `''` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:97](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L97).

```python
loader = RulesLoader(
        rules_dir=tmp_path / "rules",
        registry_url=None,
        registry_token_env=None,
        timeout_s=1,
        settings_prefix="JANE_T_",
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:113](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L113).

```python
zipped = RulesLoader(rules_dir=archive.parent, registry_url=None, registry_token_env=None, timeout_s=1)
```

## jane_kit.rules.RulesLoader.rules_dir

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:146](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L146).

```python
self.rules_dir = rules_dir
```

## jane_kit.rules.RulesLoader.registry_url

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:147](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L147).

```python
self.registry_url = registry_url.rstrip('/') if registry_url else None
```

## jane_kit.rules.RulesLoader.registry_token_env

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:148](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L148).

```python
self.registry_token_env = registry_token_env
```

## jane_kit.rules.RulesLoader.timeout_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:149](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L149).

```python
self.timeout_s = timeout_s
```

## jane_kit.rules.RulesLoader.settings_prefix

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/rules.py:150](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L150).

```python
self.settings_prefix = settings_prefix
```

## jane_kit.rules.RulesLoader.sources

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:152](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L152).

```python
def sources(self) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:122](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L122).

```python
assert loader.sources() == ["inline", "local_dir"]
```

## jane_kit.rules.RulesLoader.load

**Метод.** Код: [libs/jane-kit/src/jane_kit/rules.py:160](../../../../../../libs/jane-kit/src/jane_kit/rules.py#L160).

```python
async def load(self, ref: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:105](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L105).

```python
assert await loader.load(ref) == rules
```

Контекст і передумови: [libs/jane-kit/tests/test_schemas_rules.py:107](../../../../../../libs/jane-kit/tests/test_schemas_rules.py#L107).

```python
await loader.load({**ref, "digest": "sha256:" + "0" * 64})
```
