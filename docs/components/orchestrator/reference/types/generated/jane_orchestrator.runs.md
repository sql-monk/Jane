# jane_orchestrator.runs

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.runs.TERMINAL_RUN](#jane_orchestratorrunsterminal_run)
- [jane_orchestrator.runs.ACTIVE_ITEM](#jane_orchestratorrunsactive_item)
- [jane_orchestrator.runs.Runs](#jane_orchestratorrunsruns)
- [jane_orchestrator.runs.Runs.__init__](#jane_orchestratorrunsruns__init__)
- [jane_orchestrator.runs.Runs.core](#jane_orchestratorrunsrunscore)
- [jane_orchestrator.runs.Runs.create](#jane_orchestratorrunsrunscreate)
- [jane_orchestrator.runs.Runs.get_row](#jane_orchestratorrunsrunsget_row)
- [jane_orchestrator.runs.Runs.run_view](#jane_orchestratorrunsrunsrun_view)
- [jane_orchestrator.runs.Runs.job_view](#jane_orchestratorrunsrunsjob_view)
- [jane_orchestrator.runs.Runs.list_runs](#jane_orchestratorrunsrunslist_runs)
- [jane_orchestrator.runs.Runs.item_view](#jane_orchestratorrunsrunsitem_view)
- [jane_orchestrator.runs.Runs.list_items](#jane_orchestratorrunsrunslist_items)
- [jane_orchestrator.runs.Runs.trace](#jane_orchestratorrunsrunstrace)
- [jane_orchestrator.runs.Runs.request_cancel](#jane_orchestratorrunsrunsrequest_cancel)
- [jane_orchestrator.runs.Runs.fail_run](#jane_orchestratorrunsrunsfail_run)
- [jane_orchestrator.runs.Runs.maybe_finish](#jane_orchestratorrunsrunsmaybe_finish)

## jane_orchestrator.runs.TERMINAL_RUN

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:24](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L24).

```python
TERMINAL_RUN = ('succeeded', 'failed', 'cancelled')
```

## jane_orchestrator.runs.ACTIVE_ITEM

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:26](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L26).

```python
ACTIVE_ITEM = ('queued', 'retrying', 'leased', 'running')
```

## jane_orchestrator.runs.Runs

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:41](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L41).

```python
class Runs:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.runs.md#jane_orchestratorrunsruns__init__) | Конструктор | ні |
| [core](jane_orchestrator.runs.md#jane_orchestratorrunsrunscore) | Поле екземпляра | ні |
| [create](jane_orchestrator.runs.md#jane_orchestratorrunsrunscreate) | Метод | ні |
| [get_row](jane_orchestrator.runs.md#jane_orchestratorrunsrunsget_row) | Метод | ні |
| [run_view](jane_orchestrator.runs.md#jane_orchestratorrunsrunsrun_view) | Метод | ні |
| [job_view](jane_orchestrator.runs.md#jane_orchestratorrunsrunsjob_view) | Метод | ні |
| [list_runs](jane_orchestrator.runs.md#jane_orchestratorrunsrunslist_runs) | Метод | ні |
| [item_view](jane_orchestrator.runs.md#jane_orchestratorrunsrunsitem_view) | Метод | ні |
| [list_items](jane_orchestrator.runs.md#jane_orchestratorrunsrunslist_items) | Метод | ні |
| [trace](jane_orchestrator.runs.md#jane_orchestratorrunsrunstrace) | Метод | ні |
| [request_cancel](jane_orchestrator.runs.md#jane_orchestratorrunsrunsrequest_cancel) | Метод | ні |
| [fail_run](jane_orchestrator.runs.md#jane_orchestratorrunsrunsfail_run) | Метод | ні |
| [maybe_finish](jane_orchestrator.runs.md#jane_orchestratorrunsrunsmaybe_finish) | Метод | ні |

## jane_orchestrator.runs.Runs.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L42).

```python
def __init__(self, core: Core) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `core` | `Core` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.runs.Runs.core

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:43](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L43).

```python
self.core = core
```

## jane_orchestrator.runs.Runs.create

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:46](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L46).

```python
def create(self, conn: Any, task_row: Mapping[str, Any], source_doc: Mapping[str, Any], *, trigger: str, test_mode: bool=False, reason: str | None=None, input_override: Mapping[str, Any] | None=None, request_limits: Mapping[str, Any] | None=None, requested_by: str | None=None, idempotency_key: str | None=None, from_stage: str | None=None, enforce_overlap: bool=True) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `task_row` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source_doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `trigger` | `str` | `—` | keyword-only |
| `test_mode` | `bool` | `False` | keyword-only |
| `reason` | `str \| None` | `None` | keyword-only |
| `input_override` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `request_limits` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `requested_by` | `str \| None` | `None` | keyword-only |
| `idempotency_key` | `str \| None` | `None` | keyword-only |
| `from_stage` | `str \| None` | `None` | keyword-only |
| `enforce_overlap` | `bool` | `True` | keyword-only |

Результат: `dict[str, Any] | None`.

Явні `raise` у тілі: `Conflict`, `LimitExceeded`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Insert a queued run. Returns the run row, or ``None`` when a scheduled run is skipped
(``overlap: skip`` with an active run). A manual start in that case is ``409 conflict``.
```

## jane_orchestrator.runs.Runs.get_row

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:148](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L148).

```python
def get_row(self, conn: Any, run_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `run_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.runs.Runs.run_view

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:169](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L169).

```python
def run_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `row` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.runs.Runs.job_view

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:213](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L213).

```python
def job_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `row` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.runs.Runs.list_runs

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:259](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L259).

```python
def list_runs(self, conn: Any, *, task_id: str | None, status: str | None, since: datetime | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `task_id` | `str \| None` | `—` | keyword-only |
| `status` | `str \| None` | `—` | keyword-only |
| `since` | `datetime \| None` | `—` | keyword-only |
| `cursor` | `str \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.runs.Runs.item_view

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:293](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L293).

```python
def item_view(r: Mapping[str, Any]) -> dict[str, Any]:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `r` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.runs.Runs.list_items

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:313](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L313).

```python
def list_items(self, conn: Any, run_id: str, *, stage_id: str | None, status: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `run_id` | `str` | `—` | positional-or-keyword |
| `stage_id` | `str \| None` | `—` | keyword-only |
| `status` | `str \| None` | `—` | keyword-only |
| `cursor` | `str \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.runs.Runs.trace

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:342](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L342).

```python
def trace(self, conn: Any, material_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `material_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.runs.Runs.request_cancel

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:396](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L396).

```python
def request_cancel(self, run_id: str, actor: str, reason: str | None) -> tuple[dict[str, Any], bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `run_id` | `str` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |
| `reason` | `str \| None` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], bool]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Returns ``(job, accepted)``; ``accepted=False`` when the run was already terminal (200).
```

## jane_orchestrator.runs.Runs.fail_run

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:425](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L425).

```python
def fail_run(self, conn: Any, run_id: str, problem: Mapping[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `run_id` | `str` | `—` | positional-or-keyword |
| `problem` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Mark a run failed (``on_failure: fail_run``, collector failure, run timeout). Caller holds a tx.

Returns ``True`` only for the caller that actually changed the state (several workers or reapers may
race for the same run): only that caller counts the metric and cancels the collection.
```

## jane_orchestrator.runs.Runs.maybe_finish

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/runs.py:447](../../../../../../services/orchestrator/src/jane_orchestrator/runs.py#L447).

```python
def maybe_finish(self, run_id: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `run_id` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Close the run when the feed is exhausted and no item is active. Returns the new status.
```
