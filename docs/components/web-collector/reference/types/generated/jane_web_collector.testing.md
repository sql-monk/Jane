# jane_web_collector.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.testing.start_timeout_s](#jane_web_collectortestingstart_timeout_s)
- [jane_web_collector.testing.wait_timeout_s](#jane_web_collectortestingwait_timeout_s)
- [jane_web_collector.testing.START_TIMEOUT_S](#jane_web_collectortestingstart_timeout_s)
- [jane_web_collector.testing.FAST_LIMITS](#jane_web_collectortestingfast_limits)
- [jane_web_collector.testing.REPO_ROOT](#jane_web_collectortestingrepo_root)
- [jane_web_collector.testing.make_settings](#jane_web_collectortestingmake_settings)
- [jane_web_collector.testing.Site](#jane_web_collectortestingsite)
- [jane_web_collector.testing.Site.__init__](#jane_web_collectortestingsite__init__)
- [jane_web_collector.testing.Site.base](#jane_web_collectortestingsitebase)
- [jane_web_collector.testing.Site.requests](#jane_web_collectortestingsiterequests)
- [jane_web_collector.testing.Site.user_agents](#jane_web_collectortestingsiteuser_agents)
- [jane_web_collector.testing.Site.lock](#jane_web_collectortestingsitelock)
- [jane_web_collector.testing.Site.host](#jane_web_collectortestingsitehost)
- [jane_web_collector.testing.Site.url](#jane_web_collectortestingsiteurl)
- [jane_web_collector.testing.Site.canonical](#jane_web_collectortestingsitecanonical)
- [jane_web_collector.testing.Site.reset](#jane_web_collectortestingsitereset)
- [jane_web_collector.testing.web_rules](#jane_web_collectortestingweb_rules)
- [jane_web_collector.testing.start](#jane_web_collectortestingstart)
- [jane_web_collector.testing.wait_done](#jane_web_collectortestingwait_done)
- [jane_web_collector.testing.drain](#jane_web_collectortestingdrain)
- [jane_web_collector.testing.errors](#jane_web_collectortestingerrors)
- [jane_web_collector.testing.free_port](#jane_web_collectortestingfree_port)
- [jane_web_collector.testing.ServiceFactory](#jane_web_collectortestingservicefactory)
- [jane_web_collector.testing.ServiceProcess](#jane_web_collectortestingserviceprocess)
- [jane_web_collector.testing.ServiceProcess.__init__](#jane_web_collectortestingserviceprocess__init__)
- [jane_web_collector.testing.ServiceProcess.port](#jane_web_collectortestingserviceprocessport)
- [jane_web_collector.testing.ServiceProcess.state_dir](#jane_web_collectortestingserviceprocessstate_dir)
- [jane_web_collector.testing.ServiceProcess.env](#jane_web_collectortestingserviceprocessenv)
- [jane_web_collector.testing.ServiceProcess.proc](#jane_web_collectortestingserviceprocessproc)
- [jane_web_collector.testing.ServiceProcess.log_path](#jane_web_collectortestingserviceprocesslog_path)
- [jane_web_collector.testing.ServiceProcess.base](#jane_web_collectortestingserviceprocessbase)
- [jane_web_collector.testing.ServiceProcess.client](#jane_web_collectortestingserviceprocessclient)
- [jane_web_collector.testing.ServiceProcess.start](#jane_web_collectortestingserviceprocessstart)
- [jane_web_collector.testing.ServiceProcess.kill](#jane_web_collectortestingserviceprocesskill)
- [jane_web_collector.testing.ServiceProcess.stop](#jane_web_collectortestingserviceprocessstop)
- [jane_web_collector.testing.ServiceProcess.environment](#jane_web_collectortestingserviceprocessenvironment)

## jane_web_collector.testing.start_timeout_s

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:71](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L71).

```python
def start_timeout_s() -> float:
```

Результат: `float`.

### Опис із вихідного коду

```text
How long a service process may take to become healthy (``JANE_WEB_COLLECTOR_TEST_START_S``).
```

## jane_web_collector.testing.wait_timeout_s

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:76](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L76).

```python
def wait_timeout_s() -> float:
```

Результат: `float`.

### Опис із вихідного коду

```text
Upper bound for an awaited event in a test (``JANE_WEB_COLLECTOR_TEST_WAIT_S``).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_contract.py:54](../../../../../../services/web-collector/tests/test_contract.py#L54).

```python
deadline = time.monotonic() + wait_timeout_s()
```

Контекст і передумови: [services/web-collector/tests/test_contract.py:143](../../../../../../services/web-collector/tests/test_contract.py#L143).

```python
deadline = time.monotonic() + wait_timeout_s()
```

## jane_web_collector.testing.START_TIMEOUT_S

**Константа.** Код: [services/web-collector/src/jane_web_collector/testing.py:81](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L81).

```python
START_TIMEOUT_S = start_timeout_s()
```

### Опис із вихідного коду

```text
Default of :meth:`ServiceProcess.start`, read once at import (a plain ``float`` default keeps subclasses that
override ``start(timeout: float = ...)``, such as the WP-03 fixture, type-compatible).
```

## jane_web_collector.testing.FAST_LIMITS

**Константа.** Код: [services/web-collector/src/jane_web_collector/testing.py:86](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L86).

```python
FAST_LIMITS: dict[str, Any] = {'rate': {'requests_per_second_per_host': 500, 'min_delay_ms_per_host': 0}, 'concurrency': {'max_parallel_fetches': 4, 'max_parallel_fetches_per_host': 4}, 'retries': {'max_attempts': 1, 'initial_backoff_ms': 0, 'max_backoff_ms': 0}, 'crawl': {'max_depth': 20}}
```

### Опис із вихідного коду

```text
Politeness limits for a local test site: fast, but still through the per-host limiter.
```

## jane_web_collector.testing.REPO_ROOT

**Константа.** Код: [services/web-collector/src/jane_web_collector/testing.py:94](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L94).

```python
REPO_ROOT = Path(__file__).resolve().parents[4]
```

### Опис із вихідного коду

```text
Checkout root (``services/web-collector/src/jane_web_collector`` -> repository), for ``contracts/``.
```

## jane_web_collector.testing.make_settings

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:98](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L98).

```python
def make_settings(tmp: Path, **overrides: Any) -> Settings:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tmp` | `Path` | `—` | positional-or-keyword |
| `overrides` | `Any` | `—` | var-keyword |

Результат: `Settings`.

### Опис із вихідного коду

```text
Settings for an in-process test app: state in ``tmp``, no WP-03 package unless given.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/conftest.py:117](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L117).

```python
make_settings(tmp_path, discovery_path=PACKAGE_DIR)
```

Контекст і передумови: [services/web-collector/tests/conftest.py:92](../../../../../../services/web-collector/tests/conftest.py#L92).

```python
return make_settings(tmp_path)
```

## jane_web_collector.testing.Site

**Клас.** Код: [services/web-collector/src/jane_web_collector/testing.py:113](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L113).

```python
class Site:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [base](jane_web_collector.testing.md#jane_web_collectortestingsitebase) | Поле | ні |
| [requests](jane_web_collector.testing.md#jane_web_collectortestingsiterequests) | Поле | ні |
| [user_agents](jane_web_collector.testing.md#jane_web_collectortestingsiteuser_agents) | Поле | ні |
| [lock](jane_web_collector.testing.md#jane_web_collectortestingsitelock) | Поле | ні |
| [host](jane_web_collector.testing.md#jane_web_collectortestingsitehost) | Властивість | ні |
| [url](jane_web_collector.testing.md#jane_web_collectortestingsiteurl) | Метод | ні |
| [canonical](jane_web_collector.testing.md#jane_web_collectortestingsitecanonical) | Метод | ні |
| [reset](jane_web_collector.testing.md#jane_web_collectortestingsitereset) | Метод | ні |
| [__init__](jane_web_collector.testing.md#jane_web_collectortestingsite__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A running test site: base URL plus a log of requested paths and User-Agents.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:53](../../../../../../services/web-collector/tests/conftest.py#L53).

```python
holder = Site(base="")
```

## jane_web_collector.testing.Site.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/testing.py:113](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L113).

```python
def __init__(self, base: str, requests: Counter[str] = <factory Counter>, user_agents: set[str] = <factory set>, lock: threading.Lock = <factory threading.Lock>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `str` | `—` | positional-or-keyword |
| `requests` | `Counter[str]` | `factory: Counter` | positional-or-keyword |
| `user_agents` | `set[str]` | `factory: set` | positional-or-keyword |
| `lock` | `threading.Lock` | `factory: threading.Lock` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:53](../../../../../../services/web-collector/tests/conftest.py#L53).

```python
holder = Site(base="")
```

## jane_web_collector.testing.Site.base

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:116](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L116).

```python
base: str
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_post_m3.py:360](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L360).

```python
site.base = f"http://127.0.0.1:{server.server_address[1]}"
```

Контекст і передумови: [services/web-collector/tests/conftest.py:56](../../../../../../services/web-collector/tests/conftest.py#L56).

```python
holder.base = f"http://127.0.0.1:{server.server_address[1]}"
```

## jane_web_collector.testing.Site.requests

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:117](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L117).

```python
requests: Counter[str] = field(default_factory=Counter)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "Counter"
}
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:97](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L97).

```python
assert site.requests["/catalog/phones/?page=3"] == 0
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:105](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L105).

```python
assert site.requests["/api/v1/products?page=3"] == 0
```

## jane_web_collector.testing.Site.user_agents

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:118](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L118).

```python
user_agents: set[str] = field(default_factory=set)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "set"
}
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:38](../../../../../../services/web-collector/tests/conftest.py#L38).

```python
site.user_agents.add(self.headers.get("User-Agent", ""))
```

Контекст і передумови: [services/web-collector/tests/test_crawl_testsite.py:68](../../../../../../services/web-collector/tests/test_crawl_testsite.py#L68).

```python
assert "BadBot/1.0" in site.user_agents
```

## jane_web_collector.testing.Site.lock

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:119](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L119).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_post_m3.py:340](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L340).

```python
site.lock
```

Контекст і передумови: [services/web-collector/tests/conftest.py:36](../../../../../../services/web-collector/tests/conftest.py#L36).

```python
site.lock
```

## jane_web_collector.testing.Site.host

**Властивість.** Код: [services/web-collector/src/jane_web_collector/testing.py:122](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L122).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:154](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L154).

```python
assert urlsplit(m["locator"]["final_url"]).hostname == site.host
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_post_m3.py:374](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L374).

```python
return {
        "collector": "web",
        "scope": {"allowed_domains": [site.host]},
        "strategies": strategies,
        "revisit": {"mode": revisit},
        **extra,
    }
```

## jane_web_collector.testing.Site.url

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:125](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L125).

```python
def url(self, path: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:87](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L87).

```python
starts = [site.url(f"/catalog/{c}/") for c in ("phones", "laptops", "accessories")]
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:108](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L108).

```python
return {
        "type": "url_template",
        "strategy_id": "archive",
        "template": site.url("/archive/{n}"),
        "variables": {"n": {"range": {"start": 1, "end": 50}}},
        "stop_after_consecutive_misses": 2,
        **extra,
    }
```

## jane_web_collector.testing.Site.canonical

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:128](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L128).

```python
def canonical(self, paths: set[str] | list[str]) -> set[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `paths` | `set[str] \| list[str]` | `—` | positional-or-keyword |

Результат: `set[str]`.

### Опис із вихідного коду

```text
Root-relative paths -> canonical URLs (same normalization as the default test rules).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:151](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L151).

```python
got, want = set(canon), site.canonical(paths)
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_post_m3.py:92](../../../../../../services/web-collector/strategies/discovery/tests/test_post_m3.py#L92).

```python
assert set(canon) == site.canonical(expected_sets["recursive"] | expected_sets["api"])
```

## jane_web_collector.testing.Site.reset

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:133](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L133).

```python
def reset(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:137](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L137).

```python
site.reset()
```

Контекст і передумови: [services/web-collector/tests/test_crawl_testsite.py:192](../../../../../../services/web-collector/tests/test_crawl_testsite.py#L192).

```python
site.reset()
```

## jane_web_collector.testing.web_rules

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:138](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L138).

```python
def web_rules(site: Site, **overrides: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `site` | `Site` | `—` | positional-or-keyword |
| `overrides` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Home page + recursion inside the site host, without the /calendar/ trap, without utm_* params.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:137](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L137).

```python
rules = web_rules(site, strategies=strategies)
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:133](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L133).

```python
rules = web_rules(site, strategies=[sitemap(site), rss(site), api(site)])
```

## jane_web_collector.testing.start

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:150](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L150).

```python
def start(client: httpx.Client, body: dict[str, Any], key: str | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `body` | `dict[str, Any]` | `—` | positional-or-keyword |
| `key` | `str \| None` | `None` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:138](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L138).

```python
cid = start(
        client, {"source_kind": "web", "source_id": "wp03", "rules": rules, "limits": limits or FAST_LIMITS}
    )
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:138](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L138).

```python
cid = start(client, {**body, "mode": "incremental"})
```

## jane_web_collector.testing.wait_done

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:156](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L156).

```python
def wait_done(client: httpx.Client, cid: str, timeout: float | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |
| `timeout` | `float \| None` | `None` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:142](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L142).

```python
view = wait_done(client, cid)
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:140](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L140).

```python
assert wait_done(client, cid)["status"] == "succeeded"
```

## jane_web_collector.testing.drain

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:167](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L167).

```python
def drain(client: httpx.Client, cid: str, *, limit: int=50, timeout: float | None=None) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |
| `limit` | `int` | `50` | keyword-only |
| `timeout` | `float \| None` | `None` | keyword-only |

Результат: `list[dict[str, Any]]`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Pull every material (acknowledging each page with ``after``) until ``end_of_stream``.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/helpers.py:141](../../../../../../services/web-collector/strategies/discovery/tests/helpers.py#L141).

```python
materials = drain(client, cid)
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:135](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L135).

```python
first = drain(client, start(client, body))
```

## jane_web_collector.testing.errors

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:186](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L186).

```python
def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:39](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L39).

```python
denied = {
        urlsplit(e["url"]).path
        for e in errors(client, view["collection_id"])
        if e["code"] == "access_denied_by_policy"
    }
```

Контекст і передумови: [services/web-collector/strategies/discovery/tests/test_policy_and_limits.py:68](../../../../../../services/web-collector/strategies/discovery/tests/test_policy_and_limits.py#L68).

```python
assert [e for e in errors(client, view["collection_id"]) if e["code"] != "out_of_scope"] == []
```

## jane_web_collector.testing.free_port

**Функція.** Код: [services/web-collector/src/jane_web_collector/testing.py:198](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L198).

```python
def free_port() -> int:
```

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/conftest.py:128](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L128).

```python
port = free_port()
```

Контекст і передумови: [services/web-collector/tests/conftest.py:107](../../../../../../services/web-collector/tests/conftest.py#L107).

```python
port = free_port()
```

## jane_web_collector.testing.ServiceFactory

**Змінна.** Код: [services/web-collector/src/jane_web_collector/testing.py:204](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L204).

```python
ServiceFactory = Callable[..., 'ServiceProcess']
```

### Опис із вихідного коду

```text
Type of the ``service_factory`` fixture: ``factory(state_dir=None, **env) -> ServiceProcess``.
```

## jane_web_collector.testing.ServiceProcess

**Клас.** Код: [services/web-collector/src/jane_web_collector/testing.py:209](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L209).

```python
class ServiceProcess:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [port](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessport) | Поле | ні |
| [state_dir](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessstate_dir) | Поле | ні |
| [env](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessenv) | Поле | ні |
| [proc](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessproc) | Поле | ні |
| [log_path](jane_web_collector.testing.md#jane_web_collectortestingserviceprocesslog_path) | Поле | ні |
| [base](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessbase) | Властивість | ні |
| [client](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessclient) | Метод | ні |
| [start](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessstart) | Метод | ні |
| [kill](jane_web_collector.testing.md#jane_web_collectortestingserviceprocesskill) | Метод | ні |
| [stop](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessstop) | Метод | ні |
| [environment](jane_web_collector.testing.md#jane_web_collectortestingserviceprocessenvironment) | Метод | ні |
| [__init__](jane_web_collector.testing.md#jane_web_collectortestingserviceprocess__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
The collector as a separate OS process (what a third-party application talks to).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:118](../../../../../../services/web-collector/tests/conftest.py#L118).

```python
svc = ServiceProcess(port=port, state_dir=state_dir, env=env)
```

## jane_web_collector.testing.ServiceProcess.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/testing.py:209](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L209).

```python
def __init__(self, port: int, state_dir: Path, env: dict[str, str], proc: subprocess.Popen[bytes] | None = None, log_path: Path | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `port` | `int` | `—` | positional-or-keyword |
| `state_dir` | `Path` | `—` | positional-or-keyword |
| `env` | `dict[str, str]` | `—` | positional-or-keyword |
| `proc` | `subprocess.Popen[bytes] \| None` | `None` | positional-or-keyword |
| `log_path` | `Path \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:118](../../../../../../services/web-collector/tests/conftest.py#L118).

```python
svc = ServiceProcess(port=port, state_dir=state_dir, env=env)
```

## jane_web_collector.testing.ServiceProcess.port

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:212](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L212).

```python
port: int
```

Доступ: читання — так; запис — так.

## jane_web_collector.testing.ServiceProcess.state_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:213](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L213).

```python
state_dir: Path
```

Доступ: читання — так; запис — так.

## jane_web_collector.testing.ServiceProcess.env

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:214](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L214).

```python
env: dict[str, str]
```

Доступ: читання — так; запис — так.

## jane_web_collector.testing.ServiceProcess.proc

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:215](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L215).

```python
proc: subprocess.Popen[bytes] | None = None
```

Доступ: читання — так; запис — так.

## jane_web_collector.testing.ServiceProcess.log_path

**Поле.** Код: [services/web-collector/src/jane_web_collector/testing.py:216](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L216).

```python
log_path: Path | None = None
```

Доступ: читання — так; запис — так.

## jane_web_collector.testing.ServiceProcess.base

**Властивість.** Код: [services/web-collector/src/jane_web_collector/testing.py:219](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L219).

```python
def base(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_web_collector.testing.ServiceProcess.client

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:222](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L222).

```python
def client(self) -> httpx.Client:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `httpx.Client`.

### Опис із вихідного коду

```text
A client of this process for a test: request timeout :func:`wait_timeout_s`, and an idle pooled
connection is dropped after ``CLIENT_KEEPALIVE_EXPIRY_S``, long before the service closes it. A client that
keeps idle connections as long as the server (5 s in both httpx and uvicorn) may send a request on a
connection the server is closing at that moment and get ``httpx.ReadError`` (WinError 10054 under load).
```

## jane_web_collector.testing.ServiceProcess.start

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:233](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L233).

```python
def start(self, timeout: float=START_TIMEOUT_S) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `timeout` | `float` | `START_TIMEOUT_S` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Start the process and wait for ``/v1/health`` (``timeout`` defaults to ``START_TIMEOUT_S``).
```

## jane_web_collector.testing.ServiceProcess.kill

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:257](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L257).

```python
def kill(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Hard kill (SIGKILL on Linux, TerminateProcess on Windows): no graceful shutdown at all.

The whole process tree is killed: on Windows a venv's ``python.exe`` is a launcher whose child is
the real interpreter (psutil, a dev dependency, is used when available).
```

## jane_web_collector.testing.ServiceProcess.stop

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:276](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L276).

```python
def stop(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/conftest.py:124](../../../../../../services/web-collector/tests/conftest.py#L124).

```python
svc.stop()
```

## jane_web_collector.testing.ServiceProcess.environment

**Метод.** Код: [services/web-collector/src/jane_web_collector/testing.py:281](../../../../../../services/web-collector/src/jane_web_collector/testing.py#L281).

```python
def environment(port: int, state_dir: Path, **overrides: str) -> dict[str, str]:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `port` | `int` | `—` | positional-or-keyword |
| `state_dir` | `Path` | `—` | positional-or-keyword |
| `overrides` | `str` | `—` | var-keyword |

Результат: `dict[str, str]`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/conftest.py:129](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L129).

```python
env: dict[str, Any] = ServiceProcess.environment(
            port,
            state_dir,
            JANE_WEB_COLLECTOR_LEASE_SECONDS="3",
            JANE_WEB_COLLECTOR_HEARTBEAT_INTERVAL_MS="500",
            JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS="1000",
            JANE_WEB_COLLECTOR_DISCOVERY_PATH=str(PACKAGE_DIR),
            JANE_CONTRACTS_DIR=str(REPO_ROOT / "contracts"),
            **env_overrides,
        )
```

Контекст і передумови: [services/web-collector/tests/conftest.py:108](../../../../../../services/web-collector/tests/conftest.py#L108).

```python
env = ServiceProcess.environment(
            port,
            state_dir,
            JANE_WEB_COLLECTOR_LEASE_SECONDS="3",
            JANE_WEB_COLLECTOR_HEARTBEAT_INTERVAL_MS="500",
            JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS="1000",
            JANE_WEB_COLLECTOR_DISCOVERY_PATH=str(tmp_path / "no-discovery-package"),
            JANE_CONTRACTS_DIR=str(REPO_ROOT / "contracts"),
            **env_overrides,
        )
```
