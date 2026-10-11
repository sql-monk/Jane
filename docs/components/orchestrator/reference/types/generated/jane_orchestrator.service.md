# jane_orchestrator.service

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.service.PreconditionFailed](#jane_orchestratorservicepreconditionfailed)
- [jane_orchestrator.service.PreconditionFailed.code](#jane_orchestratorservicepreconditionfailedcode)
- [jane_orchestrator.service.Admin](#jane_orchestratorserviceadmin)
- [jane_orchestrator.service.Admin.__init__](#jane_orchestratorserviceadmin__init__)
- [jane_orchestrator.service.Admin.core](#jane_orchestratorserviceadmincore)
- [jane_orchestrator.service.Admin.runs](#jane_orchestratorserviceadminruns)
- [jane_orchestrator.service.Admin.create_source](#jane_orchestratorserviceadmincreate_source)
- [jane_orchestrator.service.Admin.get_source](#jane_orchestratorserviceadminget_source)
- [jane_orchestrator.service.Admin.replace_source](#jane_orchestratorserviceadminreplace_source)
- [jane_orchestrator.service.Admin.delete_source](#jane_orchestratorserviceadmindelete_source)
- [jane_orchestrator.service.Admin.list_sources](#jane_orchestratorserviceadminlist_sources)
- [jane_orchestrator.service.Admin.validate_task](#jane_orchestratorserviceadminvalidate_task)
- [jane_orchestrator.service.Admin.create_task](#jane_orchestratorserviceadmincreate_task)
- [jane_orchestrator.service.Admin.get_task_row](#jane_orchestratorserviceadminget_task_row)
- [jane_orchestrator.service.Admin.get_task](#jane_orchestratorserviceadminget_task)
- [jane_orchestrator.service.Admin.replace_task](#jane_orchestratorserviceadminreplace_task)
- [jane_orchestrator.service.Admin.delete_task](#jane_orchestratorserviceadmindelete_task)
- [jane_orchestrator.service.Admin.list_tasks](#jane_orchestratorserviceadminlist_tasks)
- [jane_orchestrator.service.Admin.start_run](#jane_orchestratorserviceadminstart_run)
- [jane_orchestrator.service.Admin.start_reprocessing](#jane_orchestratorserviceadminstart_reprocessing)
- [jane_orchestrator.service.Admin.list_activations](#jane_orchestratorserviceadminlist_activations)
- [jane_orchestrator.service.Admin.activate](#jane_orchestratorserviceadminactivate)
- [jane_orchestrator.service.Admin.list_problem_groups](#jane_orchestratorserviceadminlist_problem_groups)
- [jane_orchestrator.service.Admin.update_problem_group](#jane_orchestratorserviceadminupdate_problem_group)
- [jane_orchestrator.service.Admin.list_unknown](#jane_orchestratorserviceadminlist_unknown)
- [jane_orchestrator.service.Admin.list_connections](#jane_orchestratorserviceadminlist_connections)
- [jane_orchestrator.service.Admin.get_connection](#jane_orchestratorserviceadminget_connection)
- [jane_orchestrator.service.Admin.put_connection](#jane_orchestratorserviceadminput_connection)
- [jane_orchestrator.service.Admin.delete_connection](#jane_orchestratorserviceadmindelete_connection)
- [jane_orchestrator.service.Admin.get_platform_limits](#jane_orchestratorserviceadminget_platform_limits)
- [jane_orchestrator.service.Admin.put_platform_limits](#jane_orchestratorserviceadminput_platform_limits)
- [jane_orchestrator.service.Admin.effective_limits](#jane_orchestratorserviceadmineffective_limits)
- [jane_orchestrator.service.Admin.list_executors](#jane_orchestratorserviceadminlist_executors)
- [jane_orchestrator.service.Admin.list_audit](#jane_orchestratorserviceadminlist_audit)

## jane_orchestrator.service.PreconditionFailed

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/service.py:36](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L36).

```python
class PreconditionFailed(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_orchestrator.service.md#jane_orchestratorservicepreconditionfailedcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_orchestrator.service.PreconditionFailed.code

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/service.py:37](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L37).

```python
code = 'precondition_failed'
```

Доступ: читання — так; запис — так.

## jane_orchestrator.service.Admin

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/service.py:63](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L63).

```python
class Admin:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.service.md#jane_orchestratorserviceadmin__init__) | Конструктор | ні |
| [core](jane_orchestrator.service.md#jane_orchestratorserviceadmincore) | Поле екземпляра | ні |
| [runs](jane_orchestrator.service.md#jane_orchestratorserviceadminruns) | Поле екземпляра | ні |
| [create_source](jane_orchestrator.service.md#jane_orchestratorserviceadmincreate_source) | Метод | ні |
| [get_source](jane_orchestrator.service.md#jane_orchestratorserviceadminget_source) | Метод | ні |
| [replace_source](jane_orchestrator.service.md#jane_orchestratorserviceadminreplace_source) | Метод | ні |
| [delete_source](jane_orchestrator.service.md#jane_orchestratorserviceadmindelete_source) | Метод | ні |
| [list_sources](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_sources) | Метод | ні |
| [validate_task](jane_orchestrator.service.md#jane_orchestratorserviceadminvalidate_task) | Метод | ні |
| [create_task](jane_orchestrator.service.md#jane_orchestratorserviceadmincreate_task) | Метод | ні |
| [get_task_row](jane_orchestrator.service.md#jane_orchestratorserviceadminget_task_row) | Метод | ні |
| [get_task](jane_orchestrator.service.md#jane_orchestratorserviceadminget_task) | Метод | ні |
| [replace_task](jane_orchestrator.service.md#jane_orchestratorserviceadminreplace_task) | Метод | ні |
| [delete_task](jane_orchestrator.service.md#jane_orchestratorserviceadmindelete_task) | Метод | ні |
| [list_tasks](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_tasks) | Метод | ні |
| [start_run](jane_orchestrator.service.md#jane_orchestratorserviceadminstart_run) | Метод | ні |
| [start_reprocessing](jane_orchestrator.service.md#jane_orchestratorserviceadminstart_reprocessing) | Метод | ні |
| [list_activations](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_activations) | Метод | ні |
| [activate](jane_orchestrator.service.md#jane_orchestratorserviceadminactivate) | Метод | ні |
| [list_problem_groups](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_problem_groups) | Метод | ні |
| [update_problem_group](jane_orchestrator.service.md#jane_orchestratorserviceadminupdate_problem_group) | Метод | ні |
| [list_unknown](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_unknown) | Метод | ні |
| [list_connections](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_connections) | Метод | ні |
| [get_connection](jane_orchestrator.service.md#jane_orchestratorserviceadminget_connection) | Метод | ні |
| [put_connection](jane_orchestrator.service.md#jane_orchestratorserviceadminput_connection) | Метод | ні |
| [delete_connection](jane_orchestrator.service.md#jane_orchestratorserviceadmindelete_connection) | Метод | ні |
| [get_platform_limits](jane_orchestrator.service.md#jane_orchestratorserviceadminget_platform_limits) | Метод | ні |
| [put_platform_limits](jane_orchestrator.service.md#jane_orchestratorserviceadminput_platform_limits) | Метод | ні |
| [effective_limits](jane_orchestrator.service.md#jane_orchestratorserviceadmineffective_limits) | Метод | ні |
| [list_executors](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_executors) | Метод | ні |
| [list_audit](jane_orchestrator.service.md#jane_orchestratorserviceadminlist_audit) | Метод | ні |

## jane_orchestrator.service.Admin.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/service.py:64](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L64).

```python
def __init__(self, core: Core) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `core` | `Core` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.service.Admin.core

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/service.py:65](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L65).

```python
self.core = core
```

## jane_orchestrator.service.Admin.runs

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/service.py:66](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L66).

```python
self.runs = Runs(core)
```

## jane_orchestrator.service.Admin.create_source

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:110](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L110).

```python
def create_source(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.get_source

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:123](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L123).

```python
def get_source(self, source_id: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.replace_source

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:130](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L130).

```python
def replace_source(self, source_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `if_match` | `str \| None` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.delete_source

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:155](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L155).

```python
def delete_source(self, source_id: str, actor: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Conflict`, `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.list_sources

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:168](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L168).

```python
def list_sources(self, kind: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.service.Admin.validate_task

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:191](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L191).

```python
def validate_task(self, doc: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Any` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``TaskValidation``: schema + DAG + references (never raises for an invalid config).
```

## jane_orchestrator.service.Admin.create_task

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:247](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L247).

```python
def create_task(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.get_task_row

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:261](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L261).

```python
def get_task_row(self, conn: Any, task_id: str, lock: bool=False) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `Any` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `lock` | `bool` | `False` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.get_task

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:272](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L272).

```python
def get_task(self, task_id: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

## jane_orchestrator.service.Admin.replace_task

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:277](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L277).

```python
def replace_task(self, task_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `if_match` | `str \| None` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.delete_task

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:304](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L304).

```python
def delete_task(self, task_id: str, actor: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.list_tasks

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:336](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L336).

```python
def list_tasks(self, source_id: str | None, package_id: str | None, package_version: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `package_id` | `str \| None` | `—` | positional-or-keyword |
| `package_version` | `str \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.start_run

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:408](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L408).

```python
def start_run(self, task_id: str, body: Mapping[str, Any], actor: str, idempotency_key: str | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |
| `idempotency_key` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.service.Admin.start_reprocessing

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:431](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L431).

```python
def start_reprocessing(self, body: Mapping[str, Any], actor: str, idempotency_key: str | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |
| `idempotency_key` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ServiceUnavailable`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.list_activations

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:479](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L479).

```python
def list_activations(self, task_id: str, stage_id: str, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `stage_id` | `str` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.activate

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:510](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L510).

```python
def activate(self, task_id: str, stage_id: str, body: Mapping[str, Any], actor: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `task_id` | `str` | `—` | positional-or-keyword |
| `stage_id` | `str` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `AccessDeniedByPolicy`, `Conflict`, `JaneError`, `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Read → check in the registry (no DB lock held during network calls) → write if the task is unchanged.
```

## jane_orchestrator.service.Admin.list_problem_groups

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:678](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L678).

```python
def list_problem_groups(self, source_id: str | None, status: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `status` | `str \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.service.Admin.update_problem_group

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:700](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L700).

```python
def update_problem_group(self, group_id: str, patch: Mapping[str, Any], actor: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `group_id` | `str` | `—` | positional-or-keyword |
| `patch` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.list_unknown

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:716](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L716).

```python
def list_unknown(self, source_id: str | None, forwarded: bool | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `forwarded` | `bool \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.service.Admin.list_connections

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:792](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L792).

```python
def list_connections(self, kind: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.

## jane_orchestrator.service.Admin.get_connection

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:811](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L811).

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.put_connection

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:820](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L820).

```python
def put_connection(self, connection_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `if_match` | `str \| None` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

Явні `raise` у тілі: `JaneError`, `PreconditionFailed`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.delete_connection

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:868](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L868).

```python
def delete_connection(self, connection_id: str, actor: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Conflict`, `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.get_platform_limits

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:898](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L898).

```python
def get_platform_limits(self) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

## jane_orchestrator.service.Admin.put_platform_limits

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:902](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L902).

```python
def put_platform_limits(self, doc: Mapping[str, Any], if_match: str | None, actor: str) -> tuple[dict[str, Any], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `if_match` | `str \| None` | `—` | positional-or-keyword |
| `actor` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], int]`.

## jane_orchestrator.service.Admin.effective_limits

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:925](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L925).

```python
def effective_limits(self, source_id: str | None, task_id: str | None, stage_id: str | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `task_id` | `str \| None` | `—` | positional-or-keyword |
| `stage_id` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.service.Admin.list_executors

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:960](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L960).

```python
def list_executors(self) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_orchestrator.service.Admin.list_audit

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/service.py:974](../../../../../../services/orchestrator/src/jane_orchestrator/service.py#L974).

```python
def list_audit(self, subject_type: str | None, subject_id: str | None, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `subject_type` | `str \| None` | `—` | positional-or-keyword |
| `subject_id` | `str \| None` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[dict[str, Any]], str | None]`.
