# Модуль `jane_web_collector.robots`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/robots.py](../../../../../services/web-collector/src/jane_web_collector/robots.py). Не редагуйте вручну.

robots.txt (RFC 9309): parsing, matching and the per-host cache.

* Groups by ``User-agent``; the group whose product token matches the crawler's token (case-insensitive prefix match of the most specific token) wins, else ``*``; several groups with the same token merge.
* ``Allow``/``Disallow`` with ``*`` and ``$``; the longest matching rule wins, ``Allow`` on a tie.
* ``Crawl-delay`` (non-standard) and ``Sitemap`` lines are kept.
* Fetch outcome: 2xx -> parse; 4xx -> everything allowed; 5xx / network error -> everything disallowed (the RFC's "unreachable" case), retried after the cache TTL.

## Класи

### Клас `RobotsCache`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.robots` |
| Код | [robots.py:126](../../../../../services/web-collector/src/jane_web_collector/robots.py#L126) |

```python
class RobotsCache: ...
```

Per-origin robots rules with TTL. ``fetch`` is provided by the fetcher (same client and limits).

#### Конструктор `RobotsCache.__init__`

```python
def __init__(self, fetch: FetchRobots, token: str, ttl_seconds: float) -> None: ...
```

Код: [robots.py:129](../../../../../services/web-collector/src/jane_web_collector/robots.py#L129).

#### Метод `RobotsCache.origin`

```python
@staticmethod
def origin(url: str) -> str: ...
```

Код: [robots.py:137](../../../../../services/web-collector/src/jane_web_collector/robots.py#L137).

#### Метод `RobotsCache.rules_for`

```python
async def rules_for(self, url: str) -> RobotsRules: ...
```

Код: [robots.py:141](../../../../../services/web-collector/src/jane_web_collector/robots.py#L141).

#### Метод `RobotsCache.allowed`

```python
async def allowed(self, url: str) -> bool: ...
```

Код: [robots.py:166](../../../../../services/web-collector/src/jane_web_collector/robots.py#L166).

### Клас `RobotsRules`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.robots` |
| Код | [robots.py:43](../../../../../services/web-collector/src/jane_web_collector/robots.py#L43) |

```python
@dataclass
class RobotsRules: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `rules` | `list[_Rule]` | `field(default_factory=list)` | читання й запис |  |
| `crawl_delay` | `float \| None` | `None` | читання й запис |  |
| `sitemaps` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `allow_all` | `bool` | `False` | читання й запис |  |
| `disallow_all` | `bool` | `False` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `RobotsRules.allowed`

```python
def allowed(self, url: str) -> bool: ...
```

Код: [robots.py:50](../../../../../services/web-collector/src/jane_web_collector/robots.py#L50).

## Функції

### Функція `parse_robots`

```python
def parse_robots(text: str, token: str) -> RobotsRules: ...
```

Rules for the crawler with product ``token`` (e.g. ``JaneBot``).

Код: [robots.py:68](../../../../../services/web-collector/src/jane_web_collector/robots.py#L68).
