# discovery.url_template

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.url_template.template_variables](#discoveryurl_templatetemplate_variables)
- [discovery.url_template.expand](#discoveryurl_templateexpand)
- [discovery.url_template.variable_values](#discoveryurl_templatevariable_values)
- [discovery.url_template.UrlTemplateStrategy](#discoveryurl_templateurltemplatestrategy)
- [discovery.url_template.UrlTemplateStrategy.type_name](#discoveryurl_templateurltemplatestrategytype_name)
- [discovery.url_template.UrlTemplateStrategy.__init__](#discoveryurl_templateurltemplatestrategy__init__)
- [discovery.url_template.UrlTemplateStrategy.config](#discoveryurl_templateurltemplatestrategyconfig)
- [discovery.url_template.UrlTemplateStrategy.strategy_id](#discoveryurl_templateurltemplatestrategystrategy_id)
- [discovery.url_template.UrlTemplateStrategy.template](#discoveryurl_templateurltemplatestrategytemplate)
- [discovery.url_template.UrlTemplateStrategy.variables](#discoveryurl_templateurltemplatestrategyvariables)
- [discovery.url_template.UrlTemplateStrategy.names](#discoveryurl_templateurltemplatestrategynames)
- [discovery.url_template.UrlTemplateStrategy.stop_after](#discoveryurl_templateurltemplatestrategystop_after)
- [discovery.url_template.UrlTemplateStrategy.stats](#discoveryurl_templateurltemplatestrategystats)
- [discovery.url_template.UrlTemplateStrategy.combinations](#discoveryurl_templateurltemplatestrategycombinations)
- [discovery.url_template.UrlTemplateStrategy.seeds](#discoveryurl_templateurltemplatestrategyseeds)
- [discovery.url_template.UrlTemplateStrategy.on_fetched](#discoveryurl_templateurltemplatestrategyon_fetched)
- [discovery.url_template.UrlTemplateStrategy.snapshot](#discoveryurl_templateurltemplatestrategysnapshot)
- [discovery.url_template.UrlTemplateStrategy.restore](#discoveryurl_templateurltemplatestrategyrestore)

## discovery.url_template.template_variables

**Функція.** Код: [services/web-collector/strategies/discovery/url_template.py:33](../../../../../../services/web-collector/strategies/discovery/url_template.py#L33).

```python
def template_variables(template: str) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `template` | `str` | `—` | positional-or-keyword |

Результат: `list[str]`.

## discovery.url_template.expand

**Функція.** Код: [services/web-collector/strategies/discovery/url_template.py:37](../../../../../../services/web-collector/strategies/discovery/url_template.py#L37).

```python
def expand(template: str, values: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `template` | `str` | `—` | positional-or-keyword |
| `values` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
RFC 6570 level 1: ``{var}`` -> the value with every non-unreserved character percent-encoded.
```

## discovery.url_template.variable_values

**Функція.** Код: [services/web-collector/strategies/discovery/url_template.py:42](../../../../../../services/web-collector/strategies/discovery/url_template.py#L42).

```python
def variable_values(spec: Mapping[str, Any]) -> Iterator[Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `Iterator[Any]`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Lazy values of one variable (a huge range is never materialized).
```

## discovery.url_template.UrlTemplateStrategy

**Клас.** Код: [services/web-collector/strategies/discovery/url_template.py:57](../../../../../../services/web-collector/strategies/discovery/url_template.py#L57).

```python
class UrlTemplateStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](discovery.url_template.md#discoveryurl_templateurltemplatestrategytype_name) | Поле | ні |
| [__init__](discovery.url_template.md#discoveryurl_templateurltemplatestrategy__init__) | Конструктор | ні |
| [config](discovery.url_template.md#discoveryurl_templateurltemplatestrategyconfig) | Поле екземпляра | ні |
| [strategy_id](discovery.url_template.md#discoveryurl_templateurltemplatestrategystrategy_id) | Поле екземпляра | ні |
| [template](discovery.url_template.md#discoveryurl_templateurltemplatestrategytemplate) | Поле екземпляра | ні |
| [variables](discovery.url_template.md#discoveryurl_templateurltemplatestrategyvariables) | Поле екземпляра | ні |
| [names](discovery.url_template.md#discoveryurl_templateurltemplatestrategynames) | Поле екземпляра | ні |
| [stop_after](discovery.url_template.md#discoveryurl_templateurltemplatestrategystop_after) | Поле екземпляра | ні |
| [stats](discovery.url_template.md#discoveryurl_templateurltemplatestrategystats) | Поле екземпляра | ні |
| [combinations](discovery.url_template.md#discoveryurl_templateurltemplatestrategycombinations) | Метод | ні |
| [seeds](discovery.url_template.md#discoveryurl_templateurltemplatestrategyseeds) | Метод | ні |
| [on_fetched](discovery.url_template.md#discoveryurl_templateurltemplatestrategyon_fetched) | Метод | ні |
| [snapshot](discovery.url_template.md#discoveryurl_templateurltemplatestrategysnapshot) | Метод | ні |
| [restore](discovery.url_template.md#discoveryurl_templateurltemplatestrategyrestore) | Метод | ні |

## discovery.url_template.UrlTemplateStrategy.type_name

**Поле.** Код: [services/web-collector/strategies/discovery/url_template.py:58](../../../../../../services/web-collector/strategies/discovery/url_template.py#L58).

```python
type_name: ClassVar[str] = 'url_template'
```

Доступ: читання — так; запис — так.

## discovery.url_template.UrlTemplateStrategy.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/url_template.py:60](../../../../../../services/web-collector/strategies/discovery/url_template.py#L60).

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## discovery.url_template.UrlTemplateStrategy.config

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:61](../../../../../../services/web-collector/strategies/discovery/url_template.py#L61).

```python
self.config = config
```

## discovery.url_template.UrlTemplateStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:62](../../../../../../services/web-collector/strategies/discovery/url_template.py#L62).

```python
self.strategy_id = strategy_id
```

## discovery.url_template.UrlTemplateStrategy.template

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:63](../../../../../../services/web-collector/strategies/discovery/url_template.py#L63).

```python
self.template = str(config['template'])
```

## discovery.url_template.UrlTemplateStrategy.variables

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:64](../../../../../../services/web-collector/strategies/discovery/url_template.py#L64).

```python
self.variables: Mapping[str, Any] = config.get('variables') or {}
```

## discovery.url_template.UrlTemplateStrategy.names

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:65](../../../../../../services/web-collector/strategies/discovery/url_template.py#L65).

```python
self.names = template_variables(self.template)
```

## discovery.url_template.UrlTemplateStrategy.stop_after

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:70](../../../../../../services/web-collector/strategies/discovery/url_template.py#L70).

```python
self.stop_after: int | None = int(misses) if misses else None
```

## discovery.url_template.UrlTemplateStrategy.stats

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/url_template.py:71](../../../../../../services/web-collector/strategies/discovery/url_template.py#L71).

```python
self.stats: dict[str, int] = {}
```

## discovery.url_template.UrlTemplateStrategy.combinations

**Метод.** Код: [services/web-collector/strategies/discovery/url_template.py:73](../../../../../../services/web-collector/strategies/discovery/url_template.py#L73).

```python
def combinations(self, names: list[str] | None=None) -> Iterator[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `names` | `list[str] \| None` | `None` | positional-or-keyword |

Результат: `Iterator[dict[str, Any]]`.

### Опис із вихідного коду

```text
All assignments in template order, lazily (the last variable changes fastest).
```

## discovery.url_template.UrlTemplateStrategy.seeds

**Метод.** Код: [services/web-collector/strategies/discovery/url_template.py:84](../../../../../../services/web-collector/strategies/discovery/url_template.py#L84).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.url_template.UrlTemplateStrategy.on_fetched

**Метод.** Код: [services/web-collector/strategies/discovery/url_template.py:139](../../../../../../services/web-collector/strategies/discovery/url_template.py#L139).

```python
async def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.url_template.UrlTemplateStrategy.snapshot

**Метод.** Код: [services/web-collector/strategies/discovery/url_template.py:145](../../../../../../services/web-collector/strategies/discovery/url_template.py#L145).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## discovery.url_template.UrlTemplateStrategy.restore

**Метод.** Код: [services/web-collector/strategies/discovery/url_template.py:148](../../../../../../services/web-collector/strategies/discovery/url_template.py#L148).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
