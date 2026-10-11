# jane_orchestrator.engine

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.engine.Engine](#jane_orchestratorengineengine)
- [jane_orchestrator.engine.Engine.__init__](#jane_orchestratorengineengine__init__)
- [jane_orchestrator.engine.Engine.core](#jane_orchestratorengineenginecore)
- [jane_orchestrator.engine.Engine.runs](#jane_orchestratorengineengineruns)
- [jane_orchestrator.engine.Engine.lease](#jane_orchestratorengineenginelease)
- [jane_orchestrator.engine.Engine.claim_item](#jane_orchestratorengineengineclaim_item)
- [jane_orchestrator.engine.Engine.process_item](#jane_orchestratorengineengineprocess_item)
- [jane_orchestrator.engine.Engine.claim_feed](#jane_orchestratorengineengineclaim_feed)
- [jane_orchestrator.engine.Engine.process_feed](#jane_orchestratorengineengineprocess_feed)
- [jane_orchestrator.engine.Engine.schedule_due](#jane_orchestratorengineengineschedule_due)
- [jane_orchestrator.engine.Engine.reap](#jane_orchestratorengineenginereap)
- [jane_orchestrator.engine.Engine.sync_budgets](#jane_orchestratorengineenginesync_budgets)
- [jane_orchestrator.engine.Engine.sync_connections](#jane_orchestratorengineenginesync_connections)
- [jane_orchestrator.engine.Worker](#jane_orchestratorengineworker)
- [jane_orchestrator.engine.Worker.__init__](#jane_orchestratorengineworker__init__)
- [jane_orchestrator.engine.Worker.engine](#jane_orchestratorengineworkerengine)
- [jane_orchestrator.engine.Worker.name](#jane_orchestratorengineworkername)
- [jane_orchestrator.engine.Worker.scheduler](#jane_orchestratorengineworkerscheduler)
- [jane_orchestrator.engine.Worker.start](#jane_orchestratorengineworkerstart)
- [jane_orchestrator.engine.Worker.stop](#jane_orchestratorengineworkerstop)
- [jane_orchestrator.engine.Worker.step](#jane_orchestratorengineworkerstep)

## jane_orchestrator.engine.Engine

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:205](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L205).

```python
class Engine:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.engine.md#jane_orchestratorengineengine__init__) | Конструктор | ні |
| [core](jane_orchestrator.engine.md#jane_orchestratorengineenginecore) | Поле екземпляра | ні |
| [runs](jane_orchestrator.engine.md#jane_orchestratorengineengineruns) | Поле екземпляра | ні |
| [lease](jane_orchestrator.engine.md#jane_orchestratorengineenginelease) | Властивість | ні |
| [claim_item](jane_orchestrator.engine.md#jane_orchestratorengineengineclaim_item) | Метод | ні |
| [process_item](jane_orchestrator.engine.md#jane_orchestratorengineengineprocess_item) | Метод | ні |
| [claim_feed](jane_orchestrator.engine.md#jane_orchestratorengineengineclaim_feed) | Метод | ні |
| [process_feed](jane_orchestrator.engine.md#jane_orchestratorengineengineprocess_feed) | Метод | ні |
| [schedule_due](jane_orchestrator.engine.md#jane_orchestratorengineengineschedule_due) | Метод | ні |
| [reap](jane_orchestrator.engine.md#jane_orchestratorengineenginereap) | Метод | ні |
| [sync_budgets](jane_orchestrator.engine.md#jane_orchestratorengineenginesync_budgets) | Метод | ні |
| [sync_connections](jane_orchestrator.engine.md#jane_orchestratorengineenginesync_connections) | Метод | ні |

### Опис із вихідного коду

```text
The work-claiming operations; stateless apart from ``core`` (safe to share between threads).
```

## jane_orchestrator.engine.Engine.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:208](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L208).

```python
def __init__(self, core: Core) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `core` | `Core` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.engine.Engine.core

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:209](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L209).

```python
self.core = core
```

## jane_orchestrator.engine.Engine.runs

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:210](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L210).

```python
self.runs = Runs(core)
```

## jane_orchestrator.engine.Engine.lease

**Властивість.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:213](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L213).

```python
def lease(self) -> timedelta:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `timedelta`.

Доступ: читання — так; запис — ні.

## jane_orchestrator.engine.Engine.claim_item

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:217](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L217).

```python
def claim_item(self, worker: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_orchestrator.engine.Engine.process_item

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:236](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L236).

```python
def process_item(self, item: dict[str, Any], worker: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `item` | `dict[str, Any]` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Invoke the handler for a claimed item and record the outcome. Returns the outcome label.
```

## jane_orchestrator.engine.Engine.claim_feed

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:708](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L708).

```python
def claim_feed(self, worker: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_orchestrator.engine.Engine.process_feed

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:744](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L744).

```python
def process_feed(self, run: dict[str, Any], worker: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `run` | `dict[str, Any]` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_orchestrator.engine.Engine.schedule_due

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1259](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1259).

```python
def schedule_due(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Create runs for due tasks (row lock per task: one run per tick across all instances).
```

## jane_orchestrator.engine.Engine.reap

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1289](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1289).

```python
def reap(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Close runs nobody else will close: a cancelling or drained run whose last worker died (the item
and feed paths never see it again), and runs over ``timeouts.run_timeout_ms`` in any phase.

Only runs that need action are selected, so busy runs never crowd out the ones to close (a batch of
``reap_batch`` always makes progress). Several reapers may pick the same run: state changes are
conditional and only the reaper that changed the state counts it and calls the collector.
```

## jane_orchestrator.engine.Engine.sync_budgets

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1364](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1364).

```python
def sync_budgets(self, worker: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Push ``limits.llm.budget`` / ``max_requests_per_minute`` of sources and tasks to the LLM gateway
(``llm.v1 PUT/DELETE /v1/budgets/{scope_type}/{scope_id}``), idempotently, with retries.
```

## jane_orchestrator.engine.Engine.sync_connections

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1425](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1425).

```python
def sync_connections(self, worker: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `worker` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_orchestrator.engine.Worker

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1508](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1508).

```python
class Worker:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.engine.md#jane_orchestratorengineworker__init__) | Конструктор | ні |
| [engine](jane_orchestrator.engine.md#jane_orchestratorengineworkerengine) | Поле екземпляра | ні |
| [name](jane_orchestrator.engine.md#jane_orchestratorengineworkername) | Поле екземпляра | ні |
| [scheduler](jane_orchestrator.engine.md#jane_orchestratorengineworkerscheduler) | Поле екземпляра | ні |
| [start](jane_orchestrator.engine.md#jane_orchestratorengineworkerstart) | Метод | ні |
| [stop](jane_orchestrator.engine.md#jane_orchestratorengineworkerstop) | Метод | ні |
| [step](jane_orchestrator.engine.md#jane_orchestratorengineworkerstep) | Метод | ні |

### Опис із вихідного коду

```text
A thread that repeatedly claims and processes work (feeds first, then items, schedules, syncs).
```

## jane_orchestrator.engine.Worker.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1511](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1511).

```python
def __init__(self, engine: Engine, name: str, *, scheduler: bool=True) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `engine` | `Engine` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `scheduler` | `bool` | `True` | keyword-only |

Результат: `None`.

## jane_orchestrator.engine.Worker.engine

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1512](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1512).

```python
self.engine = engine
```

## jane_orchestrator.engine.Worker.name

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1513](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1513).

```python
self.name = name
```

## jane_orchestrator.engine.Worker.scheduler

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1514](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1514).

```python
self.scheduler = scheduler
```

## jane_orchestrator.engine.Worker.start

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1519](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1519).

```python
def start(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.engine.Worker.stop

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1522](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1522).

```python
def stop(self, timeout: float | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `timeout` | `float \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.engine.Worker.step

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/engine.py:1526](../../../../../../services/orchestrator/src/jane_orchestrator/engine.py#L1526).

```python
def step(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
One unit of work; ``False`` when there was nothing to do.
```
