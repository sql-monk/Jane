# discovery.tests.test_units

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.test_units.PACKAGE_DIR](#discoveryteststest_unitspackage_dir)
- [discovery.tests.test_units.MiB](#discoveryteststest_unitsmib)
- [discovery.tests.test_units.SM](#discoveryteststest_unitssm)
- [discovery.tests.test_units.test_package_registers_every_wp03_strategy](#discoveryteststest_unitstest_package_registers_every_wp03_strategy)
- [discovery.tests.test_units.test_contract_examples_are_supported](#discoveryteststest_unitstest_contract_examples_are_supported)
- [discovery.tests.test_units.test_gzip_is_decoded_and_multi_member_files_are_joined](#discoveryteststest_unitstest_gzip_is_decoded_and_multi_member_files_are_joined)
- [discovery.tests.test_units.test_gzip_bomb_is_cut_at_the_limit](#discoveryteststest_unitstest_gzip_bomb_is_cut_at_the_limit)
- [discovery.tests.test_units.test_cut_or_corrupt_gzip_yields_what_was_decoded](#discoveryteststest_unitstest_cut_or_corrupt_gzip_yields_what_was_decoded)
- [discovery.tests.test_units.BILLION_LAUGHS](#discoveryteststest_unitsbillion_laughs)
- [discovery.tests.test_units.XXE](#discoveryteststest_unitsxxe)
- [discovery.tests.test_units.test_documents_with_dtd_entities_are_refused](#discoveryteststest_unitstest_documents_with_dtd_entities_are_refused)
- [discovery.tests.test_units.test_non_xml_and_broken_xml](#discoveryteststest_unitstest_non_xml_and_broken_xml)
- [discovery.tests.test_units.test_sitemap_formats](#discoveryteststest_unitstest_sitemap_formats)
- [discovery.tests.test_units.test_robots_sitemap_lines](#discoveryteststest_unitstest_robots_sitemap_lines)
- [discovery.tests.test_units.test_feed_formats](#discoveryteststest_unitstest_feed_formats)
- [discovery.tests.test_units.test_autodiscovery_xpath_matches_only_feed_links](#discoveryteststest_unitstest_autodiscovery_xpath_matches_only_feed_links)
- [discovery.tests.test_units.test_parse_datetime](#discoveryteststest_unitstest_parse_datetime)
- [discovery.tests.test_units.test_jsonpath_subset](#discoveryteststest_unitstest_jsonpath_subset)
- [discovery.tests.test_units.test_url_template_expansion](#discoveryteststest_unitstest_url_template_expansion)
- [discovery.tests.test_units.test_api_pagination_rules](#discoveryteststest_unitstest_api_pagination_rules)
- [discovery.tests.test_units.test_api_feed_configs](#discoveryteststest_unitstest_api_feed_configs)
- [discovery.tests.test_units.test_rule_origins](#discoveryteststest_unitstest_rule_origins)
- [discovery.tests.test_units.test_limits_require_effective_value_from_context](#discoveryteststest_unitstest_limits_require_effective_value_from_context)
- [discovery.tests.test_units.test_zlib_stream_without_gzip_header_is_not_touched](#discoveryteststest_unitstest_zlib_stream_without_gzip_header_is_not_touched)
- [discovery.tests.test_units.test_package_dir_is_the_production_path](#discoveryteststest_unitstest_package_dir_is_the_production_path)

## discovery.tests.test_units.PACKAGE_DIR

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:22](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L22).

```python
PACKAGE_DIR = Path(__file__).resolve().parents[1]
```

## discovery.tests.test_units.MiB

**Змінна.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:23](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L23).

```python
MiB = 1024 * 1024
```

## discovery.tests.test_units.SM

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:24](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L24).

```python
SM = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
```

## discovery.tests.test_units.test_package_registers_every_wp03_strategy

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:28](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L28).

```python
def test_package_registers_every_wp03_strategy(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_contract_examples_are_supported

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:58](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L58).

```python
def test_contract_examples_are_supported(client: TestClient, name: str) -> None:
```

Декоратори: `pytest.mark.parametrize('name', ['web-shop.json', 'web-news-feeds-templates-api.json'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `TestClient` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
The collector-rules examples of the contract validate and are executable with this package
(``llm_explore`` is dropped: ADR-0010 keeps it unsupported by design).
```

## discovery.tests.test_units.test_gzip_is_decoded_and_multi_member_files_are_joined

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:71](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L71).

```python
def test_gzip_is_decoded_and_multi_member_files_are_joined(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_gzip_bomb_is_cut_at_the_limit

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:80](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L80).

```python
def test_gzip_bomb_is_cut_at_the_limit(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_cut_or_corrupt_gzip_yields_what_was_decoded

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:90](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L90).

```python
def test_cut_or_corrupt_gzip_yields_what_was_decoded(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.BILLION_LAUGHS

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:102](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L102).

```python
BILLION_LAUGHS = b'<?xml version="1.0"?>\n<!DOCTYPE lolz [\n <!ENTITY lol "lol">\n <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">\n <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">\n <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">\n <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">\n <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">\n <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">\n <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">\n <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">\n]>\n<urlset><url><loc>https://x.test/&lol9;</loc></url></urlset>'
```

## discovery.tests.test_units.XXE

**Константа.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:116](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L116).

```python
XXE = b'<?xml version="1.0"?>\n<!DOCTYPE urlset [<!ENTITY secret SYSTEM "file:///etc/passwd">]>\n<urlset><url><loc>https://x.test/&secret;</loc></url></urlset>'
```

## discovery.tests.test_units.test_documents_with_dtd_entities_are_refused

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:124](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L124).

```python
def test_documents_with_dtd_entities_are_refused(discovery: ModuleType, body: bytes) -> None:
```

Декоратори: `pytest.mark.parametrize('body', [BILLION_LAUGHS, XXE, gzip.compress(XXE, mtime=0)], ids=['laughs', 'xxe', 'xxe-gz'])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_non_xml_and_broken_xml

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:132](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L132).

```python
def test_non_xml_and_broken_xml(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_sitemap_formats

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:143](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L143).

```python
def test_sitemap_formats(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_robots_sitemap_lines

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:177](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L177).

```python
def test_robots_sitemap_lines(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_feed_formats

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:186](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L186).

```python
def test_feed_formats(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_autodiscovery_xpath_matches_only_feed_links

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:213](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L213).

```python
def test_autodiscovery_xpath_matches_only_feed_links(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_parse_datetime

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:244](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L244).

```python
def test_parse_datetime(discovery: ModuleType, value: Any, expected: datetime | None) -> None:
```

Декоратори: `pytest.mark.parametrize(('value', 'expected'), [('2026', datetime(2026, 1, 1, tzinfo=UTC)), ('2026-09', datetime(2026, 9, 1, tzinfo=UTC)), ('2026-09-05', datetime(2026, 9, 5, tzinfo=UTC)), ('2026-09-05T10:30+02:00', datetime(2026, 9, 5, 8, 30, tzinfo=UTC)), ('2026-09-05T10:30:00Z', datetime(2026, 9, 5, 10, 30, tzinfo=UTC)), ('Sat, 05 Sep 2026 10:30:00 +0000', datetime(2026, 9, 5, 10, 30, tzinfo=UTC)), (1788604200, datetime(2026, 9, 5, 10, 30, tzinfo=UTC)), ('yesterday', None), ('', None), (None, None), (True, None)])`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |
| `value` | `Any` | `—` | positional-or-keyword |
| `expected` | `datetime \| None` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_jsonpath_subset

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:249](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L249).

```python
def test_jsonpath_subset(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_url_template_expansion

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:273](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L273).

```python
def test_url_template_expansion(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_api_pagination_rules

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:305](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L305).

```python
def test_api_pagination_rules(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_api_feed_configs

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:332](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L332).

```python
def test_api_feed_configs(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
POST with a body and JSON items as materials are executed since WP-16 (R22, ``DiscoveryContext`` 1.1);
a method the schema does not know and an incomplete pagination are still configuration errors.
```

## discovery.tests.test_units.test_rule_origins

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:350](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L350).

```python
def test_rule_origins(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_limits_require_effective_value_from_context

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:373](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L373).

```python
def test_limits_require_effective_value_from_context(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_zlib_stream_without_gzip_header_is_not_touched

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:383](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L383).

```python
def test_zlib_stream_without_gzip_header_is_not_touched(discovery: ModuleType) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `discovery` | `ModuleType` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.tests.test_units.test_package_dir_is_the_production_path

**Функція.** Код: [services/web-collector/strategies/discovery/tests/test_units.py:388](../../../../../../services/web-collector/strategies/discovery/tests/test_units.py#L388).

```python
def test_package_dir_is_the_production_path() -> None:
```

Результат: `None`.
