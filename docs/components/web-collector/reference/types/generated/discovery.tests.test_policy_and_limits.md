# discovery.tests.test_policy_and_limits

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.test_policy_and_limits.test_robots_txt_applies_to_strategy_urls](#discoveryteststest_policy_and_limitstest_robots_txt_applies_to_strategy_urls)
- [discovery.tests.test_policy_and_limits.test_urls_outside_the_scope_are_never_requested](#discoveryteststest_policy_and_limitstest_urls_outside_the_scope_are_never_requested)
- [discovery.tests.test_policy_and_limits.test_sitemap_entries_per_document_come_from_limits](#discoveryteststest_policy_and_limitstest_sitemap_entries_per_document_come_from_limits)
- [discovery.tests.test_policy_and_limits.test_listing_pagination_depth_comes_from_strategy_limits](#discoveryteststest_policy_and_limitstest_listing_pagination_depth_comes_from_strategy_limits)
- [discovery.tests.test_policy_and_limits.test_api_pagination_depth_comes_from_strategy_limits](#discoveryteststest_policy_and_limitstest_api_pagination_depth_comes_from_strategy_limits)
- [discovery.tests.test_policy_and_limits.test_url_template_size_comes_from_max_seed_urls](#discoveryteststest_policy_and_limitstest_url_template_size_comes_from_max_seed_urls)
- [discovery.tests.test_policy_and_limits.test_page_budget_stops_the_strategies](#discoveryteststest_policy_and_limitstest_page_budget_stops_the_strategies)
- [discovery.tests.test_policy_and_limits.test_incremental_run_rereads_navigation_documents_only](#discoveryteststest_policy_and_limitstest_incremental_run_rereads_navigation_documents_only)
- [discovery.tests.test_policy_and_limits.test_schema_valid_api_feed_options_are_supported](#discoveryteststest_policy_and_limitstest_schema_valid_api_feed_options_are_supported)

## discovery.tests.test_policy_and_limits.test_robots_txt_applies_to_strategy_urls

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:18](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L18).

```python
def test_robots_txt_applies_to_strategy_urls(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Disallowed URLs are refused by the core both as candidates and through ``ctx.fetch``.
```

## discovery.tests.test_policy_and_limits.test_urls_outside_the_scope_are_never_requested

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:48](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L48).

```python
def test_urls_outside_the_scope_are_never_requested(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_sitemap_entries_per_document_come_from_limits

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:71](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L71).

```python
def test_sitemap_entries_per_document_come_from_limits(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_listing_pagination_depth_comes_from_strategy_limits

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:89](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L89).

```python
def test_listing_pagination_depth_comes_from_strategy_limits(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_api_pagination_depth_comes_from_strategy_limits

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:101](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L101).

```python
def test_api_pagination_depth_comes_from_strategy_limits(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_url_template_size_comes_from_max_seed_urls

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:109](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L109).

```python
def test_url_template_size_comes_from_max_seed_urls(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_page_budget_stops_the_strategies

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:122](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L122).

```python
def test_page_budget_stops_the_strategies(client: TestClient, site: Site) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_incremental_run_rereads_navigation_documents_only

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:130](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L130).

```python
def test_incremental_run_rereads_navigation_documents_only(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_policy_and_limits.test_schema_valid_api_feed_options_are_supported

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:172](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L172).

```python
def test_schema_valid_api_feed_options_are_supported(client: TestClient, site: Site, options: dict[str, Any], pointers: list[str]) -> None:
```

Декоратори: `pytest.mark.parametrize(('options', 'pointers'), [({'method': 'POST', 'body': {'q': 'phones'}}, ['/strategies/0/method']), ({'emit_items_as_materials': True}, ['/strategies/0/emit_items_as_materials']), ({'method': 'POST', 'body': {}, 'emit_items_as_materials': True}, ['/strategies/0/method', '/strategies/0/emit_items_as_materials'])], ids=['post', 'json-materials', 'both'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `site` | `Site` | `—` | positional-or-keyword |
| `options` | `dict[str, Any]` | `—` | positional-or-keyword |
| `pointers` | `list[str]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Since WP-16 (R22) the core executes POST and JSON items (``test_post_m3.py``): no early 422 any more.
```
