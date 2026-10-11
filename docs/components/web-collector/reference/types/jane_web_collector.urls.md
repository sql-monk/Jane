# Модуль `jane_web_collector.urls`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/urls.py](../../../../../services/web-collector/src/jane_web_collector/urls.py). Не редагуйте вручну.

URL normalization, URL patterns and scope checks (CollectorRules ``normalization``, ``UrlPattern``, ``scope``).

## Зміст

- [Клас `Normalizer`](#клас-normalizer)
- [Клас `Scope`](#клас-scope)
- [Клас `UrlPattern`](#клас-urlpattern)
- [Функція `compile_patterns`](#функція-compile_patterns)
- [Функція `material_id`](#функція-material_id)
- [Функція `patterns_match`](#функція-patterns_match)

## Класи

### Клас `Normalizer`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.urls` |
| Код | [urls.py:54](../../../../../services/web-collector/src/jane_web_collector/urls.py#L54) |

```python
@dataclass(frozen=True)
class Normalizer: ...
```

Applies CollectorRules ``normalization`` (defaults as in the schema).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `remove_fragment` | `bool` | `True` | читання |  |
| `lowercase_host` | `bool` | `True` | читання |  |
| `sort_query` | `bool` | `True` | читання |  |
| `strip_query_params` | `tuple[str, ...]` | `()` | читання |  |
| `trailing_slash` | `str` | `'keep'` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Normalizer.from_rules`

```python
@classmethod
def from_rules(cls, rules: Mapping[str, Any] | None) -> Normalizer: ...
```

Код: [urls.py:64](../../../../../services/web-collector/src/jane_web_collector/urls.py#L64).

#### Метод `Normalizer.normalize`

```python
def normalize(self, url: str, base: str | None = None) -> str | None: ...
```

Absolute canonical URL, or ``None`` for non-HTTP(S) or malformed URLs.

Код: [urls.py:74](../../../../../services/web-collector/src/jane_web_collector/urls.py#L74).

### Клас `Scope`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.urls` |
| Код | [urls.py:175](../../../../../services/web-collector/src/jane_web_collector/urls.py#L175) |

```python
@dataclass(frozen=True)
class Scope: ...
```

CollectorRules ``scope``: domains, schemes, path prefixes, include and exclude (exclude wins).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `allowed_domains` | `tuple[str, ...]` | — | читання |  |
| `include_subdomains` | `bool` | `False` | читання |  |
| `allowed_schemes` | `tuple[str, ...]` | `('https', 'http')` | читання |  |
| `path_prefixes` | `tuple[str, ...]` | `()` | читання |  |
| `include` | `tuple[UrlPattern, ...]` | `()` | читання |  |
| `exclude` | `tuple[UrlPattern, ...]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Scope.from_rules`

```python
@classmethod
def from_rules(cls, rules: Mapping[str, Any] | None) -> Scope | None: ...
```

Код: [urls.py:186](../../../../../services/web-collector/src/jane_web_collector/urls.py#L186).

#### Метод `Scope.domain_allowed`

```python
def domain_allowed(self, host: str) -> bool: ...
```

Код: [urls.py:199](../../../../../services/web-collector/src/jane_web_collector/urls.py#L199).

#### Метод `Scope.check`

```python
def check(self, canonical_url: str) -> str | None: ...
```

``None`` if in scope, else a short reason (for diagnostics).

Код: [urls.py:206](../../../../../services/web-collector/src/jane_web_collector/urls.py#L206).

### Клас `UrlPattern`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.urls` |
| Код | [urls.py:144](../../../../../services/web-collector/src/jane_web_collector/urls.py#L144) |

```python
@dataclass(frozen=True)
class UrlPattern: ...
```

``glob`` is matched against the canonical URL without scheme (``host[:port]/path?query``); ``regex`` is searched in the whole canonical URL.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `type` | `str` | — | читання |  |
| `value` | `str` | — | читання |  |
| `regex` | `re.Pattern[str]` | `field(compare=False, repr=False)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `UrlPattern.from_rule`

```python
@classmethod
def from_rule(cls, rule: Mapping[str, Any]) -> UrlPattern: ...
```

Код: [urls.py:153](../../../../../services/web-collector/src/jane_web_collector/urls.py#L153).

#### Метод `UrlPattern.matches`

```python
def matches(self, canonical_url: str) -> bool: ...
```

Код: [urls.py:159](../../../../../services/web-collector/src/jane_web_collector/urls.py#L159).

## Функції

### Функція `compile_patterns`

```python
def compile_patterns(rules: Sequence[Mapping[str, Any]] | None) -> tuple[UrlPattern, ...]: ...
```

Код: [urls.py:166](../../../../../services/web-collector/src/jane_web_collector/urls.py#L166).

### Функція `material_id`

```python
def material_id(canonical_url: str) -> str: ...
```

``web:`` + sha256(canonical URL)[:32] (material.schema.json).

Код: [urls.py:119](../../../../../services/web-collector/src/jane_web_collector/urls.py#L119).

### Функція `patterns_match`

```python
def patterns_match(patterns: Sequence[UrlPattern], url: str) -> bool: ...
```

Код: [urls.py:170](../../../../../services/web-collector/src/jane_web_collector/urls.py#L170).
