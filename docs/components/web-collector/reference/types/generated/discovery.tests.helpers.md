# discovery.tests.helpers

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.helpers.ITEMS](#discoverytestshelpersitems)
- [discovery.tests.helpers.WAIT_S](#discoverytestshelperswait_s)
- [discovery.tests.helpers.HTTP_TIMEOUT_S](#discoverytestshelpershttp_timeout_s)
- [discovery.tests.helpers.DRAIN_S](#discoverytestshelpersdrain_s)
- [discovery.tests.helpers.DONE_S](#discoverytestshelpersdone_s)
- [discovery.tests.helpers.Hold](#discoverytestshelpershold)
- [discovery.tests.helpers.Hold.__init__](#discoverytestshelpershold__init__)
- [discovery.tests.helpers.Hold.path](#discoverytestshelpersholdpath)
- [discovery.tests.helpers.Hold.arrived](#discoverytestshelpersholdarrived)
- [discovery.tests.helpers.Hold.released](#discoverytestshelpersholdreleased)
- [discovery.tests.helpers.Hold.wait_arrived](#discoverytestshelpersholdwait_arrived)
- [discovery.tests.helpers.Hold.release](#discoverytestshelpersholdrelease)
- [discovery.tests.helpers.HoldingSite](#discoverytestshelpersholdingsite)
- [discovery.tests.helpers.HoldingSite.__init__](#discoverytestshelpersholdingsite__init__)
- [discovery.tests.helpers.HoldingSite.holds](#discoverytestshelpersholdingsiteholds)
- [discovery.tests.helpers.HoldingSite.hold](#discoverytestshelpersholdingsitehold)
- [discovery.tests.helpers.HoldingSite.take_hold](#discoverytestshelpersholdingsitetake_hold)
- [discovery.tests.helpers.HoldingSite.release_all](#discoverytestshelpersholdingsiterelease_all)
- [discovery.tests.helpers.sitemap](#discoverytestshelperssitemap)
- [discovery.tests.helpers.rss](#discoverytestshelpersrss)
- [discovery.tests.helpers.categories](#discoverytestshelperscategories)
- [discovery.tests.helpers.search](#discoverytestshelperssearch)
- [discovery.tests.helpers.archive](#discoverytestshelpersarchive)
- [discovery.tests.helpers.api](#discoverytestshelpersapi)
- [discovery.tests.helpers.seeds_and_recursion](#discoverytestshelpersseeds_and_recursion)
- [discovery.tests.helpers.collect](#discoverytestshelperscollect)
- [discovery.tests.helpers.assert_exactly](#discoverytestshelpersassert_exactly)
- [discovery.tests.helpers.by_strategy](#discoverytestshelpersby_strategy)
- [discovery.tests.helpers.union](#discoverytestshelpersunion)
- [discovery.tests.helpers.cursor_stats](#discoverytestshelperscursor_stats)

## discovery.tests.helpers.ITEMS

**Константа.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:16](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L16).

```python
ITEMS = {'value': 'main li a'}
```

### Опис із вихідного коду

```text
Item links of testsite category and search pages (the site navigation is outside ``<main>``).
```

## discovery.tests.helpers.WAIT_S

**Константа.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:19](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L19).

```python
WAIT_S = float(os.environ.get('JANE_DISCOVERY_TEST_WAIT_S', '30'))
```

### Опис із вихідного коду

```text
How long a test waits for an event of the collector (a held request arriving) before it fails.
```

## discovery.tests.helpers.HTTP_TIMEOUT_S

**Константа.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:21](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L21).

```python
HTTP_TIMEOUT_S = float(os.environ.get('JANE_DISCOVERY_TEST_HTTP_TIMEOUT_S', '60'))
```

### Опис із вихідного коду

```text
Timeout of one HTTP request to a collector process (the first ``POST /v1/collections`` took 8-16 s on a loaded
machine, beyond the former 10 s).
```

## discovery.tests.helpers.DRAIN_S

**Константа.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:24](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L24).

```python
DRAIN_S = float(os.environ.get('JANE_DISCOVERY_TEST_DRAIN_S', '300'))
```

### Опис із вихідного коду

```text
How long a test reads materials of a collection run by a collector process until ``end_of_stream``.
```

## discovery.tests.helpers.DONE_S

**Константа.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:26](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L26).

```python
DONE_S = float(os.environ.get('JANE_DISCOVERY_TEST_DONE_S', '120'))
```

### Опис із вихідного коду

```text
How long a test waits for such a collection to reach a final status after its stream ended.
```

## discovery.tests.helpers.Hold

**Клас.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:32](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L32).

```python
class Hold:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [path](discovery.tests.helpers.md#discoverytestshelpersholdpath) | Поле | ні |
| [arrived](discovery.tests.helpers.md#discoverytestshelpersholdarrived) | Поле | ні |
| [released](discovery.tests.helpers.md#discoverytestshelpersholdreleased) | Поле | ні |
| [wait_arrived](discovery.tests.helpers.md#discoverytestshelpersholdwait_arrived) | Метод | ні |
| [release](discovery.tests.helpers.md#discoverytestshelpersholdrelease) | Метод | ні |
| [__init__](discovery.tests.helpers.md#discoverytestshelpershold__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
From the first request of ``path`` on, every request to the site waits for :meth:`release` (afterwards
requests are answered at once). The collector stands still at a known point while the test acts (kills
it), instead of the test polling and racing with it.
```

## discovery.tests.helpers.Hold.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:32](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L32).

```python
def __init__(self, path: str, arrived: threading.Event = <factory threading.Event>, released: threading.Event = <factory threading.Event>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str` | `—` | positional-or-keyword |
| `arrived` | `threading.Event` | `factory: threading.Event` | positional-or-keyword |
| `released` | `threading.Event` | `factory: threading.Event` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.Hold.path

**Поле.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:37](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L37).

```python
path: str
```

Доступ: читання — так; запис — так.

## discovery.tests.helpers.Hold.arrived

**Поле.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:38](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L38).

```python
arrived: threading.Event = field(default_factory=threading.Event)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "threading.Event"
}
```

## discovery.tests.helpers.Hold.released

**Поле.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:39](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L39).

```python
released: threading.Event = field(default_factory=threading.Event)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "threading.Event"
}
```

## discovery.tests.helpers.Hold.wait_arrived

**Метод.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:41](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L41).

```python
def wait_arrived(self, timeout: float=WAIT_S) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `timeout` | `float` | `WAIT_S` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.Hold.release

**Метод.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:44](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L44).

```python
def release(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.HoldingSite

**Клас.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:49](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L49).

```python
class HoldingSite(Site):
```

Базові типи / інтерфейси: `Site`.

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [holds](discovery.tests.helpers.md#discoverytestshelpersholdingsiteholds) | Поле | ні |
| [hold](discovery.tests.helpers.md#discoverytestshelpersholdingsitehold) | Метод | ні |
| [take_hold](discovery.tests.helpers.md#discoverytestshelpersholdingsitetake_hold) | Метод | ні |
| [release_all](discovery.tests.helpers.md#discoverytestshelpersholdingsiterelease_all) | Метод | ні |
| [base](jane_web_collector.testing.md#jane_web_collectortestingsitebase) | Поле | так |
| [requests](jane_web_collector.testing.md#jane_web_collectortestingsiterequests) | Поле | так |
| [user_agents](jane_web_collector.testing.md#jane_web_collectortestingsiteuser_agents) | Поле | так |
| [lock](jane_web_collector.testing.md#jane_web_collectortestingsitelock) | Поле | так |
| [host](jane_web_collector.testing.md#jane_web_collectortestingsitehost) | Властивість | так |
| [url](jane_web_collector.testing.md#jane_web_collectortestingsiteurl) | Метод | так |
| [canonical](jane_web_collector.testing.md#jane_web_collectortestingsitecanonical) | Метод | так |
| [reset](jane_web_collector.testing.md#jane_web_collectortestingsitereset) | Метод | так |
| [__init__](discovery.tests.helpers.md#discoverytestshelpersholdingsite__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
:class:`Site` whose requests can be held (:meth:`hold`); the ``site`` fixture serves one.
```

## discovery.tests.helpers.HoldingSite.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:49](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L49).

```python
def __init__(self, base: str, requests: Counter[str] = <factory Counter>, user_agents: set[str] = <factory set>, lock: threading.Lock = <factory threading.Lock>, holds: dict[str, Hold] = <factory dict>) -> None:
```

Базові типи / інтерфейси: `Site`.

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `str` | `—` | positional-or-keyword |
| `requests` | `Counter[str]` | `factory: Counter` | positional-or-keyword |
| `user_agents` | `set[str]` | `factory: set` | positional-or-keyword |
| `lock` | `threading.Lock` | `factory: threading.Lock` | positional-or-keyword |
| `holds` | `dict[str, Hold]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.HoldingSite.holds

**Поле.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:52](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L52).

```python
holds: dict[str, Hold] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## discovery.tests.helpers.HoldingSite.hold

**Метод.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:54](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L54).

```python
def hold(self, path: str) -> Hold:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `Hold`.

## discovery.tests.helpers.HoldingSite.take_hold

**Метод.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:59](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L59).

```python
def take_hold(self, path: str) -> Hold | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `Hold | None`.

### Опис із вихідного коду

```text
The hold a request of ``path`` has to wait for, if any (called by the request handler).
```

## discovery.tests.helpers.HoldingSite.release_all

**Метод.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:71](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L71).

```python
def release_all(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.sitemap

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:78](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L78).

```python
def sitemap(site: Site, **extra: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `extra` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.rss

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:82](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L82).

```python
def rss(site: Site) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.categories

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:86](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L86).

```python
def categories(site: Site, **extra: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `extra` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.search

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:97](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L97).

```python
def search(site: Site) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.archive

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:107](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L107).

```python
def archive(site: Site, **extra: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `extra` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.api

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:118](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L118).

```python
def api(site: Site, **pagination: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `pagination` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

## discovery.tests.helpers.seeds_and_recursion

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:129](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L129).

```python
def seeds_and_recursion(site: Site) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## discovery.tests.helpers.collect

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:134](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L134).

```python
def collect(client: TestClient, site: Site, strategies: list[dict[str, Any]], limits: dict[str, Any] | None=None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `strategies` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `limits` | `dict[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], dict[str, Any]]`.

## discovery.tests.helpers.assert_exactly

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:147](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L147).

```python
def assert_exactly(site: Site, materials: list[dict[str, Any]], paths: set[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `materials` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `paths` | `set[str]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.helpers.by_strategy

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:157](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L157).

```python
def by_strategy(materials: list[dict[str, Any]]) -> Counter[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `materials` | `list[dict[str, Any]]` | `—` | positional-or-keyword |

Результат: `Counter[str]`.

## discovery.tests.helpers.union

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:161](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L161).

```python
def union(expected_sets: dict[str, set[str]], *names: str) -> set[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `names` | `str` | `—` | var-positional |

Результат: `set[str]`.

## discovery.tests.helpers.cursor_stats

**Функція.** Код: [services/web-collector/strategies/discovery/tests/helpers.py:168](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L168).

```python
def cursor_stats(client: TestClient, state_key: str, strategy_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Diagnostic counters a strategy keeps in its snapshot (``GET /v1/states/{state_key}`` -> ``cursors``).
```
