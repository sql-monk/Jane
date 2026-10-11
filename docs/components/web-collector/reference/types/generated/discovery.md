# discovery

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.ApiFeedStrategy](#discoveryapifeedstrategy)
- [discovery.FeedStrategy](#discoveryfeedstrategy)
- [discovery.ListingStrategy](#discoverylistingstrategy)
- [discovery.SitemapStrategy](#discoverysitemapstrategy)
- [discovery.UrlTemplateStrategy](#discoveryurltemplatestrategy)
- [discovery.STRATEGIES](#discoverystrategies)

## discovery.ApiFeedStrategy

**Повторний експорт.** Код: [services/web-collector/strategies/discovery/__init__.py:12](../../../../../../services/web-collector/strategies/discovery/__init__.py#L12).

```python
from discovery.api_feed import ApiFeedStrategy as ApiFeedStrategy
```

Повторний експорт: [discovery.api_feed.ApiFeedStrategy](discovery.api_feed.md#discoveryapi_feedapifeedstrategy).

## discovery.FeedStrategy

**Повторний експорт.** Код: [services/web-collector/strategies/discovery/__init__.py:13](../../../../../../services/web-collector/strategies/discovery/__init__.py#L13).

```python
from discovery.feed import FeedStrategy as FeedStrategy
```

Повторний експорт: [discovery.feed.FeedStrategy](discovery.feed.md#discoveryfeedfeedstrategy).

## discovery.ListingStrategy

**Повторний експорт.** Код: [services/web-collector/strategies/discovery/__init__.py:14](../../../../../../services/web-collector/strategies/discovery/__init__.py#L14).

```python
from discovery.listing import ListingStrategy as ListingStrategy
```

Повторний експорт: [discovery.listing.ListingStrategy](discovery.listing.md#discoverylistinglistingstrategy).

## discovery.SitemapStrategy

**Повторний експорт.** Код: [services/web-collector/strategies/discovery/__init__.py:15](../../../../../../services/web-collector/strategies/discovery/__init__.py#L15).

```python
from discovery.sitemap import SitemapStrategy as SitemapStrategy
```

Повторний експорт: [discovery.sitemap.SitemapStrategy](discovery.sitemap.md#discoverysitemapsitemapstrategy).

## discovery.UrlTemplateStrategy

**Повторний експорт.** Код: [services/web-collector/strategies/discovery/__init__.py:16](../../../../../../services/web-collector/strategies/discovery/__init__.py#L16).

```python
from discovery.url_template import UrlTemplateStrategy as UrlTemplateStrategy
```

Повторний експорт: [discovery.url_template.UrlTemplateStrategy](discovery.url_template.md#discoveryurl_templateurltemplatestrategy).

## discovery.STRATEGIES

**Константа.** Код: [services/web-collector/strategies/discovery/__init__.py:27](../../../../../../services/web-collector/strategies/discovery/__init__.py#L27).

```python
STRATEGIES: list[type[DiscoveryStrategy]] = [SitemapStrategy, FeedStrategy, ListingStrategy, UrlTemplateStrategy, ApiFeedStrategy]
```
