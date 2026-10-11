# jane_web_collector.robots

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.robots.RobotsRules](#jane_web_collectorrobotsrobotsrules)
- [jane_web_collector.robots.RobotsRules.__init__](#jane_web_collectorrobotsrobotsrules__init__)
- [jane_web_collector.robots.RobotsRules.rules](#jane_web_collectorrobotsrobotsrulesrules)
- [jane_web_collector.robots.RobotsRules.crawl_delay](#jane_web_collectorrobotsrobotsrulescrawl_delay)
- [jane_web_collector.robots.RobotsRules.sitemaps](#jane_web_collectorrobotsrobotsrulessitemaps)
- [jane_web_collector.robots.RobotsRules.allow_all](#jane_web_collectorrobotsrobotsrulesallow_all)
- [jane_web_collector.robots.RobotsRules.disallow_all](#jane_web_collectorrobotsrobotsrulesdisallow_all)
- [jane_web_collector.robots.RobotsRules.allowed](#jane_web_collectorrobotsrobotsrulesallowed)
- [jane_web_collector.robots.parse_robots](#jane_web_collectorrobotsparse_robots)
- [jane_web_collector.robots.RobotsCache](#jane_web_collectorrobotsrobotscache)
- [jane_web_collector.robots.RobotsCache.__init__](#jane_web_collectorrobotsrobotscache__init__)
- [jane_web_collector.robots.RobotsCache.token](#jane_web_collectorrobotsrobotscachetoken)
- [jane_web_collector.robots.RobotsCache.ttl](#jane_web_collectorrobotsrobotscachettl)
- [jane_web_collector.robots.RobotsCache.origin](#jane_web_collectorrobotsrobotscacheorigin)
- [jane_web_collector.robots.RobotsCache.rules_for](#jane_web_collectorrobotsrobotscacherules_for)
- [jane_web_collector.robots.RobotsCache.allowed](#jane_web_collectorrobotsrobotscacheallowed)

## jane_web_collector.robots.RobotsRules

**Клас.** Код: [services/web-collector/src/jane_web_collector/robots.py:43](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L43).

```python
class RobotsRules:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [rules](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulesrules) | Поле | ні |
| [crawl_delay](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulescrawl_delay) | Поле | ні |
| [sitemaps](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulessitemaps) | Поле | ні |
| [allow_all](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulesallow_all) | Поле | ні |
| [disallow_all](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulesdisallow_all) | Поле | ні |
| [allowed](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrulesallowed) | Метод | ні |
| [__init__](jane_web_collector.robots.md#jane_web_collectorrobotsrobotsrules__init__) | Конструктор dataclass | ні |

## jane_web_collector.robots.RobotsRules.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/robots.py:43](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L43).

```python
def __init__(self, rules: list[_Rule] = <factory list>, crawl_delay: float | None = None, sitemaps: list[str] = <factory list>, allow_all: bool = False, disallow_all: bool = False) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `rules` | `list[_Rule]` | `factory: list` | positional-or-keyword |
| `crawl_delay` | `float \| None` | `None` | positional-or-keyword |
| `sitemaps` | `list[str]` | `factory: list` | positional-or-keyword |
| `allow_all` | `bool` | `False` | positional-or-keyword |
| `disallow_all` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.robots.RobotsRules.rules

**Поле.** Код: [services/web-collector/src/jane_web_collector/robots.py:44](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L44).

```python
rules: list[_Rule] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_web_collector.robots.RobotsRules.crawl_delay

**Поле.** Код: [services/web-collector/src/jane_web_collector/robots.py:45](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L45).

```python
crawl_delay: float | None = None
```

Доступ: читання — так; запис — так.

## jane_web_collector.robots.RobotsRules.sitemaps

**Поле.** Код: [services/web-collector/src/jane_web_collector/robots.py:46](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L46).

```python
sitemaps: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_web_collector.robots.RobotsRules.allow_all

**Поле.** Код: [services/web-collector/src/jane_web_collector/robots.py:47](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L47).

```python
allow_all: bool = False
```

Доступ: читання — так; запис — так.

## jane_web_collector.robots.RobotsRules.disallow_all

**Поле.** Код: [services/web-collector/src/jane_web_collector/robots.py:48](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L48).

```python
disallow_all: bool = False
```

Доступ: читання — так; запис — так.

## jane_web_collector.robots.RobotsRules.allowed

**Метод.** Код: [services/web-collector/src/jane_web_collector/robots.py:50](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L50).

```python
def allowed(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.robots.parse_robots

**Функція.** Код: [services/web-collector/src/jane_web_collector/robots.py:68](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L68).

```python
def parse_robots(text: str, token: str) -> RobotsRules:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `token` | `str` | `—` | positional-or-keyword |

Результат: `RobotsRules`.

### Опис із вихідного коду

```text
Rules for the crawler with product ``token`` (e.g. ``JaneBot``).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:103](../../../../../../services/web-collector/tests/test_units.py#L103).

```python
jane = parse_robots(text, "JaneBot")
```

Контекст і передумови: [services/web-collector/tests/test_units.py:108](../../../../../../services/web-collector/tests/test_units.py#L108).

```python
anyone = parse_robots(text, "Somebody")
```

## jane_web_collector.robots.RobotsCache

**Клас.** Код: [services/web-collector/src/jane_web_collector/robots.py:126](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L126).

```python
class RobotsCache:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscache__init__) | Конструктор | ні |
| [token](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscachetoken) | Поле екземпляра | ні |
| [ttl](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscachettl) | Поле екземпляра | ні |
| [origin](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscacheorigin) | Метод | ні |
| [rules_for](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscacherules_for) | Метод | ні |
| [allowed](jane_web_collector.robots.md#jane_web_collectorrobotsrobotscacheallowed) | Метод | ні |

### Опис із вихідного коду

```text
Per-origin robots rules with TTL. ``fetch`` is provided by the fetcher (same client and limits).
```

## jane_web_collector.robots.RobotsCache.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/robots.py:129](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L129).

```python
def __init__(self, fetch: FetchRobots, token: str, ttl_seconds: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `fetch` | `FetchRobots` | `—` | positional-or-keyword |
| `token` | `str` | `—` | positional-or-keyword |
| `ttl_seconds` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.robots.RobotsCache.token

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/robots.py:131](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L131).

```python
self.token = token
```

## jane_web_collector.robots.RobotsCache.ttl

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/robots.py:132](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L132).

```python
self.ttl = ttl_seconds
```

## jane_web_collector.robots.RobotsCache.origin

**Метод.** Код: [services/web-collector/src/jane_web_collector/robots.py:137](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L137).

```python
def origin(url: str) -> str:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_web_collector.robots.RobotsCache.rules_for

**Метод.** Код: [services/web-collector/src/jane_web_collector/robots.py:141](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L141).

```python
async def rules_for(self, url: str) -> RobotsRules:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `RobotsRules`.

## jane_web_collector.robots.RobotsCache.allowed

**Метод.** Код: [services/web-collector/src/jane_web_collector/robots.py:166](../../../../../../services/web-collector/src/jane_web_collector/robots.py#L166).

```python
async def allowed(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.
