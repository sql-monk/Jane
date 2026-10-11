# Модуль `jane_assistant.guards`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/guards.py](../../../../../services/assistant/src/jane_assistant/guards.py). Не редагуйте вручну.

Guards against untrusted model output (ТЗ §11: source content is data, not instructions).

The model may be steered by a prompt injection inside a page. Whatever it answers is therefore checked before it can take effect:

* collector rules: only known discovery strategies, URLs and patterns inside the source's hosts (the selected candidate plus domains the *user* allowed in ``crawl_hints``), ``robots`` always ``respect``, no ``llm_explore`` (ADR-0010), no per-rule limits (limits come from configuration); then JSON Schema (``collector-rules.schema.json``) and the collector's own ``validateRules``;
* generated code: parses, defines the entry callable, imports only allowed modules, calls no dangerous builtins (the runtime sandbox of WP-06 is the real barrier; this is an early reject);
* manifests: ``package-manifest.schema.json`` before publishing.

## Зміст

- [Клас `CodeCheck`](#клас-codecheck)
- [Клас `RulesCheck`](#клас-rulescheck)
- [Клас `SchemaValidator`](#клас-schemavalidator)
- [Функція `check_code`](#функція-check_code)
- [Функція `sanitize_web_rules`](#функція-sanitize_web_rules)

## Класи

### Клас `CodeCheck`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.guards` |
| Код | [guards.py:200](../../../../../services/assistant/src/jane_assistant/guards.py#L200) |

```python
@dataclass
class CodeCheck: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `ok` | `bool` | — | читання й запис |  |
| `problems` | `list[str]` | `field(default_factory=list)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RulesCheck`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.guards` |
| Код | [guards.py:104](../../../../../services/assistant/src/jane_assistant/guards.py#L104) |

```python
@dataclass
class RulesCheck: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `rules` | `dict[str, Any] \| None` | — | читання й запис |  |
| `rejected` | `list[str]` | `field(default_factory=list)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `SchemaValidator`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.guards` |
| Код | [guards.py:232](../../../../../services/assistant/src/jane_assistant/guards.py#L232) |

```python
class SchemaValidator: ...
```

Validates documents against ``contracts/schemas/*.schema.json`` when they are available.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `available` | `bool` | — | читання (властивість) |  |

#### Конструктор `SchemaValidator.__init__`

```python
def __init__(self, schemas_dir: Path | None) -> None: ...
```

Код: [guards.py:235](../../../../../services/assistant/src/jane_assistant/guards.py#L235).

#### Метод `SchemaValidator.locate`

```python
@classmethod
def locate(cls, configured: Path | None) -> SchemaValidator: ...
```

Код: [guards.py:239](../../../../../services/assistant/src/jane_assistant/guards.py#L239).

#### Метод `SchemaValidator.errors`

```python
def errors(self, schema_file: str, instance: Any) -> list[str]: ...
```

Код: [guards.py:254](../../../../../services/assistant/src/jane_assistant/guards.py#L254).

## Функції

### Функція `check_code`

```python
def check_code(source: str, callable_name: str, allowed_modules: Iterable[str]) -> CodeCheck: ...
```

Код: [guards.py:205](../../../../../services/assistant/src/jane_assistant/guards.py#L205).

### Функція `sanitize_web_rules`

```python
def sanitize_web_rules(
    proposal: dict[str, Any],
    allowed_domains: list[str],
    hints: dict[str, Any] | None = None,
) -> RulesCheck: ...
```

Build ``WebRules`` from a model proposal keeping only what stays inside ``allowed_domains``.

Код: [guards.py:109](../../../../../services/assistant/src/jane_assistant/guards.py#L109).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ALLOWED_STRATEGIES` | `dict[str, set[str]]` | `{'seed_list': {'urls', 'section', 'priority', 'strategy_id'}, 'recursive': {'see` |  |
