# discovery.tests.test_testsite

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.test_testsite.test_sitemap_index_with_gzip_alone](#discoveryteststest_testsitetest_sitemap_index_with_gzip_alone)
- [discovery.tests.test_testsite.test_sitemap_found_through_robots_txt](#discoveryteststest_testsitetest_sitemap_found_through_robots_txt)
- [discovery.tests.test_testsite.test_sitemap_lastmod_since_skips_older_entries](#discoveryteststest_testsitetest_sitemap_lastmod_since_skips_older_entries)
- [discovery.tests.test_testsite.test_feed_alone](#discoveryteststest_testsitetest_feed_alone)
- [discovery.tests.test_testsite.test_feed_autodiscovery_from_an_html_url](#discoveryteststest_testsitetest_feed_autodiscovery_from_an_html_url)
- [discovery.tests.test_testsite.test_feed_autodiscovery_on_seed_pages](#discoveryteststest_testsitetest_feed_autodiscovery_on_seed_pages)
- [discovery.tests.test_testsite.test_listing_categories_with_rel_next](#discoveryteststest_testsitetest_listing_categories_with_rel_next)
- [discovery.tests.test_testsite.test_listing_categories_with_page_param](#discoveryteststest_testsitetest_listing_categories_with_page_param)
- [discovery.tests.test_testsite.test_listing_search_pages](#discoveryteststest_testsitetest_listing_search_pages)
- [discovery.tests.test_testsite.test_url_template_stops_after_consecutive_misses](#discoveryteststest_testsitetest_url_template_stops_after_consecutive_misses)
- [discovery.tests.test_testsite.test_url_template_values_without_miss_detection](#discoveryteststest_testsitetest_url_template_values_without_miss_detection)
- [discovery.tests.test_testsite.test_api_feed_alone](#discoveryteststest_testsitetest_api_feed_alone)
- [discovery.tests.test_testsite.test_each_strategy_combined_with_recursion](#discoveryteststest_testsitetest_each_strategy_combined_with_recursion)
- [discovery.tests.test_testsite.test_all_strategies_together](#discoveryteststest_testsitetest_all_strategies_together)
- [discovery.tests.test_testsite.test_recursion_without_seeds_follows_sitemap_pages](#discoveryteststest_testsitetest_recursion_without_seeds_follows_sitemap_pages)
- [discovery.tests.test_testsite.test_all_strategies_without_recursion](#discoveryteststest_testsitetest_all_strategies_without_recursion)

## discovery.tests.test_testsite.test_sitemap_index_with_gzip_alone

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:35](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L35).

```python
def test_sitemap_index_with_gzip_alone(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_sitemap_found_through_robots_txt

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:49](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L49).

```python
def test_sitemap_found_through_robots_txt(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
No ``urls``: the ``Sitemap:`` line of robots.txt of the origin of the rules (here the seed list).
```

## discovery.tests.test_testsite.test_sitemap_lastmod_since_skips_older_entries

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:63](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L63).

```python
def test_sitemap_lastmod_since_skips_older_entries(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_feed_alone

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:89](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L89).

```python
def test_feed_alone(client: TestClient, site: Site, expected_sets: dict[str, set[str]], path: str) -> None:
```

Декоратори: `pytest.mark.parametrize('path', ['/feeds/news.rss', '/feeds/news.atom'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_feed_autodiscovery_from_an_html_url

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:97](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L97).

```python
def test_feed_autodiscovery_from_an_html_url(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
An HTML page in ``urls``: its ``<link rel=alternate>`` feeds are read; the page itself is navigation.
```

## discovery.tests.test_testsite.test_feed_autodiscovery_on_seed_pages

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:106](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L106).

```python
def test_feed_autodiscovery_on_seed_pages(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
No ``urls``: feeds announced on the seed pages of other strategies (depth 0).
```

## discovery.tests.test_testsite.test_listing_categories_with_rel_next

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:119](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L119).

```python
def test_listing_categories_with_rel_next(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_listing_categories_with_page_param

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:127](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L127).

```python
def test_listing_categories_with_page_param(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_listing_search_pages

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:144](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L144).

```python
def test_listing_search_pages(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_url_template_stops_after_consecutive_misses

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:149](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L149).

```python
def test_url_template_stops_after_consecutive_misses(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_url_template_values_without_miss_detection

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:158](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L158).

```python
def test_url_template_values_without_miss_detection(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_api_feed_alone

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:178](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L178).

```python
def test_api_feed_alone(client: TestClient, site: Site, expected_sets: dict[str, set[str]], pagination: dict[str, Any]) -> None:
```

Декоратори: `pytest.mark.parametrize('pagination', [{'type': 'next_url', 'next_url_path': '$.next'}, {'type': 'page', 'page_param': 'page'}], ids=['next_url', 'page'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `pagination` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_each_strategy_combined_with_recursion

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:201](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L201).

```python
def test_each_strategy_combined_with_recursion(client: TestClient, site: Site, expected_sets: dict[str, set[str]], make: Any, sets: tuple[str, ...]) -> None:
```

Декоратори: `pytest.mark.parametrize(('make', 'sets'), [(sitemap, ('sitemap',)), (rss, ('feeds',)), (categories, ('categories',)), (search, ('search:phone', 'search:cable')), (archive, ('template:/archive/{n}',)), (api, ('api',))], ids=['sitemap', 'feed', 'categories', 'search', 'url_template', 'api_feed'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `make` | `Any` | `—` | positional-or-keyword |
| `sets` | `tuple[str, ...]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_all_strategies_together

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:213](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L213).

```python
def test_all_strategies_together(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_testsite.test_recursion_without_seeds_follows_sitemap_pages

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:239](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L239).

```python
def test_recursion_without_seeds_follows_sitemap_pages(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
``recursive`` without ``seeds`` starts from the pages another strategy found (here: the sitemap).
```

## discovery.tests.test_testsite.test_all_strategies_without_recursion

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_testsite.py:247](../../../../../../services/web-collector/strategies/discovery/tests/test_testsite.py#L247).

```python
def test_all_strategies_without_recursion(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.
