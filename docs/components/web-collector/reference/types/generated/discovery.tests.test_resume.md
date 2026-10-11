# discovery.tests.test_resume

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.test_resume.SLOW_LIMITS](#discoveryteststest_resumeslow_limits)
- [discovery.tests.test_resume.SEED_FETCHES](#discoveryteststest_resumeseed_fetches)
- [discovery.tests.test_resume.NAVIGATION_PREFIXES](#discoveryteststest_resumenavigation_prefixes)
- [discovery.tests.test_resume.TEMPLATE_MISSES](#discoveryteststest_resumetemplate_misses)
- [discovery.tests.test_resume.SEEDS_HOLD](#discoveryteststest_resumeseeds_hold)
- [discovery.tests.test_resume.CRAWL_HOLD](#discoveryteststest_resumecrawl_hold)
- [discovery.tests.test_resume.test_strategies_resume_after_kill](#discoveryteststest_resumetest_strategies_resume_after_kill)

## discovery.tests.test_resume.SLOW_LIMITS

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:27](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L27).

```python
SLOW_LIMITS: dict[str, Any] = {'rate': {'requests_per_second_per_host': 15, 'min_delay_ms_per_host': 0}, 'concurrency': {'max_parallel_fetches': 2, 'max_parallel_fetches_per_host': 2}, 'retries': {'max_attempts': 1, 'initial_backoff_ms': 0, 'max_backoff_ms': 0}, 'crawl': {'max_depth': 20}}
```

## discovery.tests.test_resume.SEED_FETCHES

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:34](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L34).

```python
SEED_FETCHES = 4 + 7 + 4
```

## discovery.tests.test_resume.NAVIGATION_PREFIXES

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:35](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L35).

```python
NAVIGATION_PREFIXES = ('/sitemap', '/api/', '/robots.txt')
```

## discovery.tests.test_resume.TEMPLATE_MISSES

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:36](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L36).

```python
TEMPLATE_MISSES = {'/archive/6', '/archive/7'}
```

## discovery.tests.test_resume.SEEDS_HOLD

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:37](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L37).

```python
SEEDS_HOLD = '/sitemaps/pages.xml'
```

### Опис із вихідного коду

```text
The last child sitemap (4th fetch of seeds()): held until the kill, so the sitemap strategy is unfinished.
```

## discovery.tests.test_resume.CRAWL_HOLD

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:39](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L39).

```python
CRAWL_HOLD = '/product/headphones-pro'
```

### Опис із вихідного коду

```text
The 15th URL of the crawl (from ``products.xml``, after the 15 seed fetches): seeds() is complete, the crawl
fetches sitemap products, listing chains have not started (the former kill point ``stats.fetched >= 30``).
```

## discovery.tests.test_resume.test_strategies_resume_after_kill

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_resume.py:45](../../../../../../services/web-collector/strategies/discovery/tests/test_resume.py#L45).

```python
def test_strategies_resume_after_kill(service_factory: ServiceFactory, site: HoldingSite, expected_sets: dict[str, set[str]], held: str) -> None:
```

Декоратори: `pytest.mark.parametrize('held', [SEEDS_HOLD, CRAWL_HOLD], ids=['during-seeds', 'during-crawl'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `service_factory` | `ServiceFactory` | `—` | positional-or-keyword |
| `site` | `HoldingSite` | `—` | positional-or-keyword |
| `expected_sets` | `dict[str, set[str]]` | `—` | positional-or-keyword |
| `held` | `str` | `—` | positional-or-keyword |

Результат: `None`.
