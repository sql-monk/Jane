# jane_web_collector.urls

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.urls.Normalizer](#jane_web_collectorurlsnormalizer)
- [jane_web_collector.urls.Normalizer.__init__](#jane_web_collectorurlsnormalizer__init__)
- [jane_web_collector.urls.Normalizer.remove_fragment](#jane_web_collectorurlsnormalizerremove_fragment)
- [jane_web_collector.urls.Normalizer.lowercase_host](#jane_web_collectorurlsnormalizerlowercase_host)
- [jane_web_collector.urls.Normalizer.sort_query](#jane_web_collectorurlsnormalizersort_query)
- [jane_web_collector.urls.Normalizer.strip_query_params](#jane_web_collectorurlsnormalizerstrip_query_params)
- [jane_web_collector.urls.Normalizer.trailing_slash](#jane_web_collectorurlsnormalizertrailing_slash)
- [jane_web_collector.urls.Normalizer.from_rules](#jane_web_collectorurlsnormalizerfrom_rules)
- [jane_web_collector.urls.Normalizer.normalize](#jane_web_collectorurlsnormalizernormalize)
- [jane_web_collector.urls.material_id](#jane_web_collectorurlsmaterial_id)
- [jane_web_collector.urls.UrlPattern](#jane_web_collectorurlsurlpattern)
- [jane_web_collector.urls.UrlPattern.__init__](#jane_web_collectorurlsurlpattern__init__)
- [jane_web_collector.urls.UrlPattern.type](#jane_web_collectorurlsurlpatterntype)
- [jane_web_collector.urls.UrlPattern.value](#jane_web_collectorurlsurlpatternvalue)
- [jane_web_collector.urls.UrlPattern.regex](#jane_web_collectorurlsurlpatternregex)
- [jane_web_collector.urls.UrlPattern.from_rule](#jane_web_collectorurlsurlpatternfrom_rule)
- [jane_web_collector.urls.UrlPattern.matches](#jane_web_collectorurlsurlpatternmatches)
- [jane_web_collector.urls.compile_patterns](#jane_web_collectorurlscompile_patterns)
- [jane_web_collector.urls.patterns_match](#jane_web_collectorurlspatterns_match)
- [jane_web_collector.urls.Scope](#jane_web_collectorurlsscope)
- [jane_web_collector.urls.Scope.__init__](#jane_web_collectorurlsscope__init__)
- [jane_web_collector.urls.Scope.allowed_domains](#jane_web_collectorurlsscopeallowed_domains)
- [jane_web_collector.urls.Scope.include_subdomains](#jane_web_collectorurlsscopeinclude_subdomains)
- [jane_web_collector.urls.Scope.allowed_schemes](#jane_web_collectorurlsscopeallowed_schemes)
- [jane_web_collector.urls.Scope.path_prefixes](#jane_web_collectorurlsscopepath_prefixes)
- [jane_web_collector.urls.Scope.include](#jane_web_collectorurlsscopeinclude)
- [jane_web_collector.urls.Scope.exclude](#jane_web_collectorurlsscopeexclude)
- [jane_web_collector.urls.Scope.from_rules](#jane_web_collectorurlsscopefrom_rules)
- [jane_web_collector.urls.Scope.domain_allowed](#jane_web_collectorurlsscopedomain_allowed)
- [jane_web_collector.urls.Scope.check](#jane_web_collectorurlsscopecheck)

## jane_web_collector.urls.Normalizer

**Клас.** Код: [services/web-collector/src/jane_web_collector/urls.py:54](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L54).

```python
class Normalizer:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [remove_fragment](jane_web_collector.urls.md#jane_web_collectorurlsnormalizerremove_fragment) | Поле | ні |
| [lowercase_host](jane_web_collector.urls.md#jane_web_collectorurlsnormalizerlowercase_host) | Поле | ні |
| [sort_query](jane_web_collector.urls.md#jane_web_collectorurlsnormalizersort_query) | Поле | ні |
| [strip_query_params](jane_web_collector.urls.md#jane_web_collectorurlsnormalizerstrip_query_params) | Поле | ні |
| [trailing_slash](jane_web_collector.urls.md#jane_web_collectorurlsnormalizertrailing_slash) | Поле | ні |
| [from_rules](jane_web_collector.urls.md#jane_web_collectorurlsnormalizerfrom_rules) | Метод | ні |
| [normalize](jane_web_collector.urls.md#jane_web_collectorurlsnormalizernormalize) | Метод | ні |
| [__init__](jane_web_collector.urls.md#jane_web_collectorurlsnormalizer__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Applies CollectorRules ``normalization`` (defaults as in the schema).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:25](../../../../../../services/web-collector/tests/test_units.py#L25).

```python
n = Normalizer(strip_query_params=("utm_*", "sessionid"))
```

Контекст і передумови: [services/web-collector/tests/test_units.py:62](../../../../../../services/web-collector/tests/test_units.py#L62).

```python
norm = Normalizer()
```

## jane_web_collector.urls.Normalizer.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/urls.py:54](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L54).

```python
def __init__(self, remove_fragment: bool = True, lowercase_host: bool = True, sort_query: bool = True, strip_query_params: tuple[str, ...] = (), trailing_slash: str = 'keep') -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `remove_fragment` | `bool` | `True` | positional-or-keyword |
| `lowercase_host` | `bool` | `True` | positional-or-keyword |
| `sort_query` | `bool` | `True` | positional-or-keyword |
| `strip_query_params` | `tuple[str, ...]` | `()` | positional-or-keyword |
| `trailing_slash` | `str` | `'keep'` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:25](../../../../../../services/web-collector/tests/test_units.py#L25).

```python
n = Normalizer(strip_query_params=("utm_*", "sessionid"))
```

Контекст і передумови: [services/web-collector/tests/test_units.py:62](../../../../../../services/web-collector/tests/test_units.py#L62).

```python
norm = Normalizer()
```

## jane_web_collector.urls.Normalizer.remove_fragment

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:57](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L57).

```python
remove_fragment: bool = True
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Normalizer.lowercase_host

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:58](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L58).

```python
lowercase_host: bool = True
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Normalizer.sort_query

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:59](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L59).

```python
sort_query: bool = True
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Normalizer.strip_query_params

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:60](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L60).

```python
strip_query_params: tuple[str, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Normalizer.trailing_slash

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:61](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L61).

```python
trailing_slash: str = 'keep'
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Normalizer.from_rules

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:64](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L64).

```python
def from_rules(cls, rules: Mapping[str, Any] | None) -> Normalizer:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `rules` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `Normalizer`.

## jane_web_collector.urls.Normalizer.normalize

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:74](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L74).

```python
def normalize(self, url: str, base: str | None=None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `base` | `str \| None` | `None` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Absolute canonical URL, or ``None`` for non-HTTP(S) or malformed URLs.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:26](../../../../../../services/web-collector/tests/test_units.py#L26).

```python
assert (
        n.normalize("HTTP://Example.TEST:80/a/./b/../c?b=2&a=1&utm_source=x#frag")
        == "http://example.test/a/c?a=1&b=2"
    )
```

Контекст і передумови: [services/web-collector/tests/test_units.py:30](../../../../../../services/web-collector/tests/test_units.py#L30).

```python
assert n.normalize("https://example.test:443") == "https://example.test/"
```

## jane_web_collector.urls.material_id

**Функція.** Код: [services/web-collector/src/jane_web_collector/urls.py:119](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L119).

```python
def material_id(canonical_url: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `canonical_url` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``web:`` + sha256(canonical URL)[:32] (material.schema.json).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:38](../../../../../../services/web-collector/tests/test_units.py#L38).

```python
assert material_id("https://e.test/") == material_id("https://e.test/")
```

Контекст і передумови: [services/web-collector/tests/test_units.py:39](../../../../../../services/web-collector/tests/test_units.py#L39).

```python
assert material_id("https://e.test/").startswith("web:") and len(material_id("https://e.test/")) == 36
```

## jane_web_collector.urls.UrlPattern

**Клас.** Код: [services/web-collector/src/jane_web_collector/urls.py:144](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L144).

```python
class UrlPattern:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type](jane_web_collector.urls.md#jane_web_collectorurlsurlpatterntype) | Поле | ні |
| [value](jane_web_collector.urls.md#jane_web_collectorurlsurlpatternvalue) | Поле | ні |
| [regex](jane_web_collector.urls.md#jane_web_collectorurlsurlpatternregex) | Поле | ні |
| [from_rule](jane_web_collector.urls.md#jane_web_collectorurlsurlpatternfrom_rule) | Метод | ні |
| [matches](jane_web_collector.urls.md#jane_web_collectorurlsurlpatternmatches) | Метод | ні |
| [__init__](jane_web_collector.urls.md#jane_web_collectorurlsurlpattern__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
``glob`` is matched against the canonical URL without scheme (``host[:port]/path?query``);
``regex`` is searched in the whole canonical URL.
```

## jane_web_collector.urls.UrlPattern.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/urls.py:144](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L144).

```python
def __init__(self, type: str, value: str, regex: re.Pattern[str] = field(compare=False, repr=False)) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `type` | `str` | `—` | positional-or-keyword |
| `value` | `str` | `—` | positional-or-keyword |
| `regex` | `re.Pattern[str]` | `field(compare=False, repr=False)` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.urls.UrlPattern.type

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:148](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L148).

```python
type: str
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.UrlPattern.value

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:149](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L149).

```python
value: str
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.UrlPattern.regex

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:150](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L150).

```python
regex: re.Pattern[str] = field(compare=False, repr=False)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "compare": "False",
  "repr": "False"
}
```

## jane_web_collector.urls.UrlPattern.from_rule

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:153](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L153).

```python
def from_rule(cls, rule: Mapping[str, Any]) -> UrlPattern:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `rule` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `UrlPattern`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:43](../../../../../../services/web-collector/tests/test_units.py#L43).

```python
glob = UrlPattern.from_rule({"value": "shop.test/product/*"})
```

Контекст і передумови: [services/web-collector/tests/test_units.py:46](../../../../../../services/web-collector/tests/test_units.py#L46).

```python
assert UrlPattern.from_rule({"value": "shop.test/**"}).matches("https://shop.test/a/b?c=1")
```

## jane_web_collector.urls.UrlPattern.matches

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:159](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L159).

```python
def matches(self, canonical_url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `canonical_url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.urls.compile_patterns

**Функція.** Код: [services/web-collector/src/jane_web_collector/urls.py:166](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L166).

```python
def compile_patterns(rules: Sequence[Mapping[str, Any]] | None) -> tuple[UrlPattern, ...]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `rules` | `Sequence[Mapping[str, Any]] \| None` | `—` | positional-or-keyword |

Результат: `tuple[UrlPattern, ...]`.

## jane_web_collector.urls.patterns_match

**Функція.** Код: [services/web-collector/src/jane_web_collector/urls.py:170](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L170).

```python
def patterns_match(patterns: Sequence[UrlPattern], url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `patterns` | `Sequence[UrlPattern]` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.urls.Scope

**Клас.** Код: [services/web-collector/src/jane_web_collector/urls.py:175](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L175).

```python
class Scope:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [allowed_domains](jane_web_collector.urls.md#jane_web_collectorurlsscopeallowed_domains) | Поле | ні |
| [include_subdomains](jane_web_collector.urls.md#jane_web_collectorurlsscopeinclude_subdomains) | Поле | ні |
| [allowed_schemes](jane_web_collector.urls.md#jane_web_collectorurlsscopeallowed_schemes) | Поле | ні |
| [path_prefixes](jane_web_collector.urls.md#jane_web_collectorurlsscopepath_prefixes) | Поле | ні |
| [include](jane_web_collector.urls.md#jane_web_collectorurlsscopeinclude) | Поле | ні |
| [exclude](jane_web_collector.urls.md#jane_web_collectorurlsscopeexclude) | Поле | ні |
| [from_rules](jane_web_collector.urls.md#jane_web_collectorurlsscopefrom_rules) | Метод | ні |
| [domain_allowed](jane_web_collector.urls.md#jane_web_collectorurlsscopedomain_allowed) | Метод | ні |
| [check](jane_web_collector.urls.md#jane_web_collectorurlsscopecheck) | Метод | ні |
| [__init__](jane_web_collector.urls.md#jane_web_collectorurlsscope__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
CollectorRules ``scope``: domains, schemes, path prefixes, include and exclude (exclude wins).
```

## jane_web_collector.urls.Scope.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/urls.py:175](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L175).

```python
def __init__(self, allowed_domains: tuple[str, ...], include_subdomains: bool = False, allowed_schemes: tuple[str, ...] = ('https', 'http'), path_prefixes: tuple[str, ...] = (), include: tuple[UrlPattern, ...] = (), exclude: tuple[UrlPattern, ...] = ()) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `allowed_domains` | `tuple[str, ...]` | `—` | positional-or-keyword |
| `include_subdomains` | `bool` | `False` | positional-or-keyword |
| `allowed_schemes` | `tuple[str, ...]` | `('https', 'http')` | positional-or-keyword |
| `path_prefixes` | `tuple[str, ...]` | `()` | positional-or-keyword |
| `include` | `tuple[UrlPattern, ...]` | `()` | positional-or-keyword |
| `exclude` | `tuple[UrlPattern, ...]` | `()` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.urls.Scope.allowed_domains

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:178](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L178).

```python
allowed_domains: tuple[str, ...]
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.include_subdomains

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:179](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L179).

```python
include_subdomains: bool = False
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.allowed_schemes

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:180](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L180).

```python
allowed_schemes: tuple[str, ...] = ('https', 'http')
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.path_prefixes

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:181](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L181).

```python
path_prefixes: tuple[str, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.include

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:182](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L182).

```python
include: tuple[UrlPattern, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.exclude

**Поле.** Код: [services/web-collector/src/jane_web_collector/urls.py:183](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L183).

```python
exclude: tuple[UrlPattern, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_web_collector.urls.Scope.from_rules

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:186](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L186).

```python
def from_rules(cls, rules: Mapping[str, Any] | None) -> Scope | None:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `rules` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `Scope | None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:50](../../../../../../services/web-collector/tests/test_units.py#L50).

```python
paged = Scope.from_rules(
        {
            "scope": {
                "allowed_domains": ["rozetka.com.ua"],
                "include": [
                    {"value": "rozetka.com.ua/ua/notebooks/c80004/"},
                    {"value": "rozetka.com.ua/ua/notebooks/c80004/page=?/"},
                ],
            }
        }
    )
```

Контекст і передумови: [services/web-collector/tests/test_units.py:69](../../../../../../services/web-collector/tests/test_units.py#L69).

```python
scope = Scope.from_rules(
        {
            "scope": {
                "allowed_domains": ["shop.test"],
                "include_subdomains": True,
                "path_prefixes": ["/catalog", "/product"],
                "exclude": [{"value": "**/private/**"}],
                "allowed_schemes": ["https"],
            }
        }
    )
```

## jane_web_collector.urls.Scope.domain_allowed

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:199](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L199).

```python
def domain_allowed(self, host: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.urls.Scope.check

**Метод.** Код: [services/web-collector/src/jane_web_collector/urls.py:206](../../../../../../services/web-collector/src/jane_web_collector/urls.py#L206).

```python
def check(self, canonical_url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `canonical_url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
``None`` if in scope, else a short reason (for diagnostics).
```
