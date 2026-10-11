# discovery.tests.conftest

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.tests.conftest.PACKAGE_DIR](#discoverytestsconftestpackage_dir)
- [discovery.tests.conftest.START_S](#discoverytestsconfteststart_s)
- [discovery.tests.conftest.site](#discoverytestsconftestsite)
- [discovery.tests.conftest.expected_sets](#discoverytestsconftestexpected_sets)
- [discovery.tests.conftest.discovery](#discoverytestsconftestdiscovery)
- [discovery.tests.conftest.client](#discoverytestsconftestclient)
- [discovery.tests.conftest.service_factory](#discoverytestsconftestservice_factory)

## discovery.tests.conftest.PACKAGE_DIR

**Константа.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:36](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L36).

```python
PACKAGE_DIR = Path(__file__).resolve().parents[1]
```

### Опис із вихідного коду

```text
``services/web-collector/strategies/discovery`` — the package under test.
```

## discovery.tests.conftest.START_S

**Константа.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:38](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L38).

```python
START_S = float(os.environ.get('JANE_DISCOVERY_TEST_START_S', '120'))
```

### Опис із вихідного коду

```text
How long a collector process may take to answer ``/v1/health`` (``ServiceProcess.start`` waits 30 s, which
a loaded machine exceeded for the Telegram collector's processes in a full ``just check``).
```

## discovery.tests.conftest.site

**Функція.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:72](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L72).

```python
def site() -> Iterator[HoldingSite]:
```

Декоратори: `pytest.fixture`.

Результат: `Iterator[HoldingSite]`.

## discovery.tests.conftest.expected_sets

**Функція.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:89](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L89).

```python
def expected_sets() -> dict[str, set[str]]:
```

Декоратори: `pytest.fixture(scope='session')`.

Результат: `dict[str, set[str]]`.

## discovery.tests.conftest.discovery

**Функція.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:109](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L109).

```python
def discovery() -> ModuleType:
```

Декоратори: `pytest.fixture`.

Результат: `ModuleType`.

### Опис із вихідного коду

```text
The package as the core imports it (``jane_web_collector_discovery``).
```

## discovery.tests.conftest.client

**Функція.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:115](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L115).

```python
def client(tmp_path: Path) -> Iterator[TestClient]:
```

Декоратори: `pytest.fixture`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tmp_path` | `Path` | `—` | positional-or-keyword |

Результат: `Iterator[TestClient]`.

## discovery.tests.conftest.service_factory

**Функція.** Код: [services/web-collector/strategies/discovery/tests/conftest.py:122](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L122).

```python
def service_factory(tmp_path: Path) -> Iterator[ServiceFactory]:
```

Декоратори: `pytest.fixture`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tmp_path` | `Path` | `—` | positional-or-keyword |

Результат: `Iterator[ServiceFactory]`.

### Опис із вихідного коду

```text
The collector as a separate OS process with this package (``JANE_WEB_COLLECTOR_DISCOVERY_PATH``).
```
