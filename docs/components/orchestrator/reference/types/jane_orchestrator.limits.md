# Модуль `jane_orchestrator.limits`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/limits.py](../../../../../services/orchestrator/src/jane_orchestrator/limits.py). Не редагуйте вручну.

Effective limits (``limits.schema.json``): platform → source → task → stage → request, with hard caps.

jane-kit's :func:`~jane_kit.config.resolve_limits` merges into a static model with a default for every field. The orchestrator merges *contract documents* whose fields are set by users at any level (crawl, sandbox, llm… — values it only forwards to executors), so it merges JSON documents here with the same rules: deep merge, lower level overrides, ``null`` is never a value, numeric leaves are capped by the platform ``hard_caps`` (provenance ``hard_cap``). Fields the orchestrator consumes itself fall back to :class:`~jane_orchestrator.settings.ContractDefaults` (provenance ``platform``).

## Зміст

- [Клас `Effective`](#клас-effective)
- [Клас `LimitsLayer`](#клас-limitslayer)
- [Функція `flatten`](#функція-flatten)
- [Функція `merge_limits`](#функція-merge_limits)
- [Функція `unflatten`](#функція-unflatten)

## Класи

### Клас `Effective`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_orchestrator.limits` |
| Код | [limits.py:62](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L62) |

```python
@dataclass
class Effective: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `limits` | `dict[str, Any]` | — | читання й запис |  |
| `provenance` | `dict[str, str]` | — | читання й запис |  |
| `flat` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Effective.doc`

```python
def doc(self) -> dict[str, Any]: ...
```

``EffectiveLimits`` document.

Код: [limits.py:67](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L67).

#### Метод `Effective.get`

```python
def get(self, path: str, default: Any = None) -> Any: ...
```

Код: [limits.py:71](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L71).

### Клас `LimitsLayer`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_orchestrator.limits` |
| Код | [limits.py:56](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L56) |

```python
@dataclass(frozen=True)
class LimitsLayer: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `level` | `str` | — | читання |  |
| `values` | `Mapping[str, Any]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `flatten`

```python
def flatten(data: Mapping[str, Any], prefix: str = '') -> dict[str, Any]: ...
```

Код: [limits.py:20](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L20).

### Функція `merge_limits`

```python
def merge_limits(
    fallback: Mapping[str, Any],
    layers: Sequence[LimitsLayer],
    hard_caps: Mapping[str, Any] | None = None,
) -> Effective: ...
```

Merge ``fallback`` (code defaults, level platform) and ``layers`` (least specific first).

Код: [limits.py:79](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L79).

### Функція `unflatten`

```python
def unflatten(flat: Mapping[str, Any]) -> dict[str, Any]: ...
```

Код: [limits.py:31](../../../../../services/orchestrator/src/jane_orchestrator/limits.py#L31).
