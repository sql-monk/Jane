# discovery.tests.test_post_m3

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.test_post_m3.SCHEMAS](#discoveryteststest_post_m3schemas)
- [discovery.tests.test_post_m3.material_validator](#discoveryteststest_post_m3material_validator)
- [discovery.tests.test_post_m3.test_api_feed_emits_json_items_as_materials](#discoveryteststest_post_m3test_api_feed_emits_json_items_as_materials)
- [discovery.tests.test_post_m3.test_api_feed_items_combine_with_recursion_once_per_url](#discoveryteststest_post_m3test_api_feed_items_combine_with_recursion_once_per_url)
- [discovery.tests.test_post_m3.test_api_feed_items_in_incremental_runs_follow_revisit](#discoveryteststest_post_m3test_api_feed_items_in_incremental_runs_follow_revisit)
- [discovery.tests.test_post_m3.REDIRECTS](#discoveryteststest_post_m3redirects)
- [discovery.tests.test_post_m3.PostingSite](#discoveryteststest_post_m3postingsite)
- [discovery.tests.test_post_m3.PostingSite.posts](#discoveryteststest_post_m3postingsiteposts)
- [discovery.tests.test_post_m3.post_site](#discoveryteststest_post_m3post_site)
- [discovery.tests.test_post_m3.test_api_feed_post_queries_every_page_with_the_json_body](#discoveryteststest_post_m3test_api_feed_post_queries_every_page_with_the_json_body)
- [discovery.tests.test_post_m3.test_api_feed_post_follows_redirects_by_their_method_rules](#discoveryteststest_post_m3test_api_feed_post_follows_redirects_by_their_method_rules)
- [discovery.tests.test_post_m3.OWNER_POLICY](#discoveryteststest_post_m3owner_policy)
- [discovery.tests.test_post_m3.test_api_feed_post_obeys_robots_scope_and_egress](#discoveryteststest_post_m3test_api_feed_post_obeys_robots_scope_and_egress)
- [discovery.tests.test_post_m3.ChangingSite](#discoveryteststest_post_m3changingsite)
- [discovery.tests.test_post_m3.ChangingSite.__init__](#discoveryteststest_post_m3changingsite__init__)
- [discovery.tests.test_post_m3.ChangingSite.base](#discoveryteststest_post_m3changingsitebase)
- [discovery.tests.test_post_m3.ChangingSite.items](#discoveryteststest_post_m3changingsiteitems)
- [discovery.tests.test_post_m3.ChangingSite.lastmod](#discoveryteststest_post_m3changingsitelastmod)
- [discovery.tests.test_post_m3.ChangingSite.log](#discoveryteststest_post_m3changingsitelog)
- [discovery.tests.test_post_m3.ChangingSite.lock](#discoveryteststest_post_m3changingsitelock)
- [discovery.tests.test_post_m3.ChangingSite.host](#discoveryteststest_post_m3changingsitehost)
- [discovery.tests.test_post_m3.ChangingSite.url](#discoveryteststest_post_m3changingsiteurl)
- [discovery.tests.test_post_m3.ChangingSite.fetched](#discoveryteststest_post_m3changingsitefetched)
- [discovery.tests.test_post_m3.ChangingSite.conditional](#discoveryteststest_post_m3changingsiteconditional)
- [discovery.tests.test_post_m3.ChangingSite.clear](#discoveryteststest_post_m3changingsiteclear)
- [discovery.tests.test_post_m3.ChangingSite.page](#discoveryteststest_post_m3changingsitepage)
- [discovery.tests.test_post_m3.changing](#discoveryteststest_post_m3changing)
- [discovery.tests.test_post_m3.test_listing_pages_are_reread_and_find_new_items](#discoveryteststest_post_m3test_listing_pages_are_reread_and_find_new_items)
- [discovery.tests.test_post_m3.test_lastmod_newer_than_the_last_fetch_forces_a_revisit](#discoveryteststest_post_m3test_lastmod_newer_than_the_last_fetch_forces_a_revisit)

## discovery.tests.test_post_m3.SCHEMAS

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:34](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L34).

```python
SCHEMAS = REPO_ROOT / 'contracts' / 'schemas'
```

## discovery.tests.test_post_m3.material_validator

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:38](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L38).

```python
def material_validator() -> Draft202012Validator:
```

Декоратори: `pytest.fixture(scope='module')`.

Результат: `Draft202012Validator`.

## discovery.tests.test_post_m3.test_api_feed_emits_json_items_as_materials

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:59](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L59).

```python
def test_api_feed_emits_json_items_as_materials(client: TestClient, site: Site, expected_sets: dict[str, set[str]], material_validator: Draft202012Validator) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `material_validator` | `Draft202012Validator` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.test_api_feed_items_combine_with_recursion_once_per_url

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:85](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L85).

```python
def test_api_feed_items_combine_with_recursion_once_per_url(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.test_api_feed_items_in_incremental_runs_follow_revisit

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:100](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L100).

```python
def test_api_feed_items_in_incremental_runs_follow_revisit(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.REDIRECTS

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:120](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L120).

```python
REDIRECTS: dict[str, tuple[int, str]] = {'/old-api': (307, '/api/v1/products'), '/moved-api': (303, '/api/v1/products'), '/out-api': (307, 'http://elsewhere.example.org/api/v1/products'), '/meta-api': (307, 'http://169.254.169.254/latest/meta-data')}
```

### Опис із вихідного коду

```text
POST redirects of the test site: path -> (status, Location).
```

## discovery.tests.test_post_m3.PostingSite

**Клас.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:129](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L129).

```python
class PostingSite(Site):
```

Базові типи / інтерфейси: `Site`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [posts](discovery.tests.test_post_m3.md#discoveryteststest_post_m3postingsiteposts) | Поле | ні |
| [base](jane_web_collector.testing.md#jane_web_collectortestingsitebase) | Поле | так |
| [requests](jane_web_collector.testing.md#jane_web_collectortestingsiterequests) | Поле | так |
| [user_agents](jane_web_collector.testing.md#jane_web_collectortestingsiteuser_agents) | Поле | так |
| [lock](jane_web_collector.testing.md#jane_web_collectortestingsitelock) | Поле | так |
| [host](jane_web_collector.testing.md#jane_web_collectortestingsitehost) | Властивість | так |
| [url](jane_web_collector.testing.md#jane_web_collectortestingsiteurl) | Метод | так |
| [canonical](jane_web_collector.testing.md#jane_web_collectortestingsitecanonical) | Метод | так |
| [reset](jane_web_collector.testing.md#jane_web_collectortestingsitereset) | Метод | так |

### Опис із вихідного коду

```text
``Site`` that also logs POST requests: ``(path, content-type, body)``.
```

## discovery.tests.test_post_m3.PostingSite.posts

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:132](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L132).

```python
posts: list[tuple[str, str, bytes]]
```

Доступ: читання — так; запис — так.

## discovery.tests.test_post_m3.post_site

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:136](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L136).

```python
def post_site() -> Iterator[PostingSite]:
```

Декоратори: `pytest.fixture`.

Результат: `Iterator[PostingSite]`.

## discovery.tests.test_post_m3.test_api_feed_post_queries_every_page_with_the_json_body

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:182](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L182).

```python
def test_api_feed_post_queries_every_page_with_the_json_body(client: TestClient, post_site: PostingSite, expected_sets: dict[str, set[str]], pagination: str) -> None:
```

Декоратори: `pytest.mark.parametrize('pagination', ['next_url', 'page'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `post_site` | `PostingSite` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `pagination` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.test_api_feed_post_follows_redirects_by_their_method_rules

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:200](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L200).

```python
def test_api_feed_post_follows_redirects_by_their_method_rules(client: TestClient, post_site: PostingSite, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `post_site` | `PostingSite` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.OWNER_POLICY

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:231](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L231).

```python
OWNER_POLICY = {'mode': 'owner_policy', 'owner_policy': {'confirmed_owner': True, 'justification': 'the test owns this site and its API'}}
```

## discovery.tests.test_post_m3.test_api_feed_post_obeys_robots_scope_and_egress

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:247](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L247).

```python
def test_api_feed_post_obeys_robots_scope_and_egress(client: TestClient, post_site: PostingSite, path: str, code: str, extra: dict[str, Any]) -> None:
```

Декоратори: `pytest.mark.parametrize(('path', 'code', 'extra'), [('/private/api', 'access_denied_by_policy', {}), ('/out-api', 'out_of_scope', {}), ('/meta-api', 'access_denied_by_policy', {'robots': OWNER_POLICY, 'extra_domain': '169.254.169.254'})], ids=['robots', 'redirect-out-of-scope', 'redirect-egress'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `post_site` | `PostingSite` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `code` | `str` | `—` | positional-or-keyword |
| `extra` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Review 1 of WP-16: a POST of an API page goes through the same policy as any fetch of the core -
robots.txt, the scope of every redirect hop and the outbound address policy - and is refused, not sent.
```

## discovery.tests.test_post_m3.ChangingSite

**Клас.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:276](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L276).

```python
class ChangingSite:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [base](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitebase) | Поле | ні |
| [items](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsiteitems) | Поле | ні |
| [lastmod](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitelastmod) | Поле | ні |
| [log](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitelog) | Поле | ні |
| [lock](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitelock) | Поле | ні |
| [host](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitehost) | Властивість | ні |
| [url](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsiteurl) | Метод | ні |
| [fetched](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitefetched) | Метод | ні |
| [conditional](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsiteconditional) | Метод | ні |
| [clear](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsiteclear) | Метод | ні |
| [page](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsitepage) | Метод | ні |
| [__init__](discovery.tests.test_post_m3.md#discoveryteststest_post_m3changingsite__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A site the test changes between runs: a paginated list (two items per page, ``rel=next``), item pages, a
sitemap with ``lastmod``. Every page has an ``ETag`` and answers 304 to a matching ``If-None-Match``.
```

## discovery.tests.test_post_m3.ChangingSite.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:276](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L276).

```python
def __init__(self, base: str = '', items: list[int] = <factory lambda: [1, 2, 3]>, lastmod: dict[str, datetime] = <factory dict>, log: list[tuple[str, str | None]] = <factory list>, lock: threading.Lock = <factory threading.Lock>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `str` | `''` | positional-or-keyword |
| `items` | `list[int]` | `factory: lambda: [1, 2, 3]` | positional-or-keyword |
| `lastmod` | `dict[str, datetime]` | `factory: dict` | positional-or-keyword |
| `log` | `list[tuple[str, str \| None]]` | `factory: list` | positional-or-keyword |
| `lock` | `threading.Lock` | `factory: threading.Lock` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.ChangingSite.base

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:280](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L280).

```python
base: str = ''
```

Доступ: читання — так; запис — так.

## discovery.tests.test_post_m3.ChangingSite.items

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:281](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L281).

```python
items: list[int] = field(default_factory=lambda: [1, 2, 3])
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: [1, 2, 3]"
}
```

## discovery.tests.test_post_m3.ChangingSite.lastmod

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:282](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L282).

```python
lastmod: dict[str, datetime] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## discovery.tests.test_post_m3.ChangingSite.log

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:283](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L283).

```python
log: list[tuple[str, str | None]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
(path, If-None-Match) of every request.
```

## discovery.tests.test_post_m3.ChangingSite.lock

**Поле.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:285](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L285).

```python
lock: threading.Lock = field(default_factory=threading.Lock)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "threading.Lock"
}
```

## discovery.tests.test_post_m3.ChangingSite.host

**Властивість.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:288](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L288).

```python
def host(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## discovery.tests.test_post_m3.ChangingSite.url

**Метод.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:291](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L291).

```python
def url(self, path: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## discovery.tests.test_post_m3.ChangingSite.fetched

**Метод.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:294](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L294).

```python
def fetched(self, path: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## discovery.tests.test_post_m3.ChangingSite.conditional

**Метод.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:298](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L298).

```python
def conditional(self, path: str) -> list[str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `list[str | None]`.

## discovery.tests.test_post_m3.ChangingSite.clear

**Метод.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:302](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L302).

```python
def clear(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_post_m3.ChangingSite.page

**Метод.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:306](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L306).

```python
def page(self, path: str, query: dict[str, list[str]]) -> tuple[int, str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `query` | `dict[str, list[str]]` | `—` | positional-or-keyword |

Результат: `tuple[int, str, str]`.

## discovery.tests.test_post_m3.changing

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:331](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L331).

```python
def changing() -> Iterator[ChangingSite]:
```

Декоратори: `pytest.fixture`.

Результат: `Iterator[ChangingSite]`.

## discovery.tests.test_post_m3.test_listing_pages_are_reread_and_find_new_items

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:404](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L404).

```python
def test_listing_pages_are_reread_and_find_new_items(client: TestClient, changing: ChangingSite, revisit: str) -> None:
```

Декоратори: `pytest.mark.parametrize('revisit', ['never', 'if_changed'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `changing` | `ChangingSite` | `—` | positional-or-keyword |
| `revisit` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
A new item on the second page of a known category: before R23 an incremental run skipped the first page
(``never``) or got 304 for it (``if_changed``), never learnt the next page and missed the item.
```

## discovery.tests.test_post_m3.test_lastmod_newer_than_the_last_fetch_forces_a_revisit

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_post_m3.py:432](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L432).

```python
def test_lastmod_newer_than_the_last_fetch_forces_a_revisit(client: TestClient, changing: ChangingSite) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `changing` | `ChangingSite` | `—` | positional-or-keyword |

Результат: `None`.
