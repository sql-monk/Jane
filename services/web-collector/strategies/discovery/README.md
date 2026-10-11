# Стратегії пошуку Web Collector

Пакет стратегій `sitemap`, `feed`, `listing`, `url_template` і `api_feed` та інструкція, як підключити нову стратегію пошуку матеріалів. Ядро колектора імпортує цей каталог як пакет `jane_web_collector_discovery` і реєструє список `STRATEGIES`. Огляд усіх стратегій — [internals.md](../../../../docs/components/web-collector/internals.md#стратегії-пошуку).

## Зміст

- [Контракт стратегії](#контракт-стратегії)
- [Правила для стратегії](#правила-для-стратегії)
- [Способи підключення](#способи-підключення)
- [Схема правил](#схема-правил)
- [Приклад: стратегія text_list](#приклад-стратегія-text_list)
- [Тести](#тести)

## Контракт стратегії

Протокол — `jane_contracts.discovery` ([discovery.py](../../../../contracts/python/src/jane_contracts/discovery.py)); пояснення поділу відповідальності з ядром — [discovery-strategy.md](../../../../contracts/docs/discovery-strategy.md).

```python
class DiscoveryStrategy(Protocol):
    type_name: ClassVar[str]  # дорівнює полю "type" стратегії в правилах

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None: ...
    def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]: ...
    def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]: ...
    def snapshot(self) -> Mapping[str, Any]: ...
    def restore(self, state: Mapping[str, Any]) -> None: ...
```

| Член | Коли викликає ядро |
|---|---|
| `__init__(config, strategy_id)` | на старті збору; `config` — перевірений об'єкт стратегії з правил, `strategy_id` — її `strategy_id` або `<type>-<індекс>` |
| `seeds(ctx)` | один раз на збір; може читати навігаційні документи через `ctx.fetch` |
| `on_fetched(resource, ctx)` | для кожної відповіді з тілом (будь-який статус), отриманої будь-якою стратегією, крім тієї, що сама запитала її через `ctx.fetch` |
| `snapshot()` | після кожної порції, у тій самій транзакції, що й черга; має повертати JSON-серіалізовний стан |
| `restore(state)` | після перезапуску, перед `seeds`; стратегія, чиї `seeds` вже завершилися, їх більше не отримує |

Необов'язковий хук `refresh_on_revisit(url) -> bool` (`RefreshingStrategy`) змушує ядро читати сторінку повністю в кожному зборі — так робить `listing`.

## Правила для стратегії

- Жодних власних HTTP-запитів — лише `ctx.fetch`; тоді межі, `robots.txt`, ліміти хоста, бюджети й політика адрес діють однаково.
- `kind="navigation"` — документ лише для пошуку (не видається як матеріал); `kind="material"` — кандидат у матеріали.
- `FetchRejected` — нормальна ситуація: `out_of_scope` чи `access_denied_by_policy` — пропустити URL; `limit_exceeded` чи `rate_limited` — припинити запити в цьому зборі.
- Числа — лише з `ctx.limits` (ефективні ліміти з урахуванням `strategies[].limits`) або з конфігурації стратегії.
- Нормалізацію, межі, дедуплікацію, глибину й пріоритети виконує ядро; стратегія лише пропонує `DiscoveredUrl`.

## Способи підключення

Реєстр (`src/jane_web_collector/discovery/registry.py`) збирає стратегії на старті в такому порядку; пізніше джерело не може перевизначити наявний `type_name`:

| Джерело | Як додати стратегію |
|---|---|
| вбудовані | `seed_list`, `recursive` у ядрі |
| цей каталог | модуль у `strategies/discovery/` і клас у списку `STRATEGIES` з `__init__.py` |
| інший каталог | `JANE_WEB_COLLECTOR_DISCOVERY_PATH=<каталог з __init__.py і STRATEGIES>` — **замінює** цей каталог, тому скопіюйте в нього й наявні стратегії |
| встановлений пакет | entry point групи `jane.web_collector.strategies` (клас або список класів) |

Приклад entry point у `pyproject.toml` пакета, встановленого поруч із сервісом:

```toml
[project.entry-points."jane.web_collector.strategies"]
text_list = "my_strategies.text_list:TextListStrategy"
```

Клас без `type_name` або без методів протоколу, дубль типу чи зарезервований `llm_explore` не реєструються; сервіс усе одно стартує, а причина з'являється в `capabilities.strategy_load_errors` відповіді `GET /v1/info` і в журналі (`strategy not registered`). Підключені стратегії видно в `capabilities.strategies`.

## Схема правил

Правила перевіряються за [collector-rules.schema.json](../../../../contracts/schemas/collector-rules.schema.json), де `$defs/Strategy` — закритий перелік типів. Тому нова стратегія потребує **зміни контракту**: визначення `$defs/<Назва>Strategy` (з `allOf` на `StrategyCommon` і `"type": {"const": "<type_name>"}`) і посилання в `oneOf` стратегій. Зміни контрактів виконуються за процесом `contracts/` (скіл `jane-contracts`, перевірка зворотної сумісності).

Без зміни схеми правила з новим типом не проходять перевірку навіть за зареєстрованого класу:

```json
{"valid":false,"supported":false,"errors":[{"pointer":"/strategies/0","code":"one_of","message":"{'type': 'text_list', 'urls': ['http://127.0.0.1:18111/urls.txt']} is not valid under any of the given schemas"}],"warnings":[]}
```

Для локальної перевірки до зміни контракту можна вказати копію каталогу контрактів зі зміненою схемою: `JANE_WEB_COLLECTOR_CONTRACTS_DIR=<копія contracts>`.

## Приклад: стратегія text_list

Стратегія читає текстові документи зі списком URL (по одному в рядку, `#` — коментар) і пропонує ці URL як матеріали.

```python
"""``text_list`` strategy: material URLs listed one per line in plain-text documents."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any, ClassVar

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource, FetchRejected


class TextListStrategy:
    type_name: ClassVar[str] = "text_list"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.strategy_id = strategy_id
        self.urls: list[str] = list(config["urls"])
        self.done: list[str] = []

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for list_url in self.urls:
            if list_url in self.done or ctx.is_cancelled():
                continue
            try:
                resource = await ctx.fetch(list_url, kind="navigation", conditional=False)
            except FetchRejected as exc:
                if exc.code in {"limit_exceeded", "rate_limited"}:
                    return  # the run budget is exhausted: stop asking
                continue  # out of scope or denied by robots.txt: skip this list
            if resource is not None and 200 <= resource.status < 300:
                for line in resource.body.decode("utf-8", errors="replace").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        yield DiscoveredUrl(
                            url=ctx.normalize(line, resource.final_url),
                            strategy_id=self.strategy_id,
                            kind="material",
                            depth=resource.depth + 1,
                            parent_url=resource.final_url,
                        )
            self.done.append(list_url)

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        return
        yield

    def snapshot(self) -> Mapping[str, Any]:
        return {"done": list(self.done)}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.done = list(state.get("done") or [])
```

Визначення для схеми правил (додається в `$defs` і в `oneOf` стратегій):

```json
{
  "TextListStrategy": {
    "description": "URLs one per line in plain-text documents.",
    "allOf": [{"$ref": "#/$defs/StrategyCommon"}],
    "type": "object",
    "unevaluatedProperties": false,
    "required": ["type", "urls"],
    "properties": {
      "type": {"const": "text_list"},
      "urls": {"type": "array", "minItems": 1, "items": {"type": "string", "format": "uri"}}
    }
  }
}
```

Перевірка (виконано 2026-10-11 на Windows 11, ревізія `48389a3`): копію цього каталогу з модулем `text_list.py` і класом у `STRATEGIES` та копію `contracts/` зі зміненою схемою підключено через `JANE_WEB_COLLECTOR_DISCOVERY_PATH` і `JANE_WEB_COLLECTOR_CONTRACTS_DIR`; список `urls.txt` із трьома сторінками товарів тестового сайту віддавав `python -m http.server` на порту 18111. `GET /v1/info` показав `text_list` у `capabilities.strategies`, а збір із правилами

```json
{
  "source_kind": "web",
  "rules": {
    "collector": "web",
    "scope": {"allowed_domains": ["127.0.0.1"]},
    "strategies": [{"type": "text_list", "strategy_id": "lists", "urls": ["http://127.0.0.1:18111/urls.txt"]}]
  },
  "limits": {"rate": {"requests_per_second_per_host": 20, "min_delay_ms_per_host": 0}}
}
```

завершився так (статистика збору):

```json
{"discovered": 3, "fetched": 4, "emitted": 3, "acknowledged": 0, "unacked": 3, "duplicates": 0, "skipped_out_of_scope": 0, "skipped_robots": 0, "not_modified": 0, "errors": 0, "frontier_size": 0, "bytes_fetched": 3381, "by_strategy": {"lists": 3}}
```

`fetched: 4` — три сторінки й сам список; список як навігаційний документ матеріалом не став.

## Тести

Тести пакета — у `tests/`: справжній тестовий сайт і справжнє ядро колектора з цим пакетом, підключеним так само, як у роботі (`conftest.py`, помічники `collect`, `assert_exactly` у `helpers.py`). Нова стратегія має покривати:

- очікуваний набір URL окремо й у комбінації з `recursive` — без дублів;
- відмови `ctx.fetch` (межі, `robots.txt`, бюджет);
- відновлення після перезапуску через `snapshot`/`restore` (зразок — `test_resume.py`).

Запуск разом із тестами сервісу:

```powershell
just test web-collector
```

Набори очікуваних URL тестового сайту — `tests/fixtures/testsite/expected_urls.json`.
