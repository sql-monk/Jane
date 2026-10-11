# Модуль `jane_orchestrator.service`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/service.py](../../../../../services/orchestrator/src/jane_orchestrator/service.py). Не редагуйте вручну.

Management operations behind ``orchestrator.v1``: sources, tasks, runs, connections, limits, activations with audit, problem groups, unknown materials, executors.

## Класи

### Клас `Admin`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.service` |
| Код | [service.py:63](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L63) |

```python
class Admin: ...
```

#### Конструктор `Admin.__init__`

```python
def __init__(self, core: Core) -> None: ...
```

Код: [service.py:64](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L64).

#### Метод `Admin.create_source`

```python
def create_source(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:110](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L110).

#### Метод `Admin.get_source`

```python
def get_source(self, source_id: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:123](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L123).

#### Метод `Admin.replace_source`

```python
def replace_source(
    self,
    source_id: str,
    doc: Mapping[str, Any],
    if_match: str | None,
    actor: str,
) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `ValidationFailed`, `NotFound`.

Код: [service.py:130](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L130).

#### Метод `Admin.delete_source`

```python
def delete_source(self, source_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `NotFound`, `Conflict`.

Код: [service.py:155](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L155).

#### Метод `Admin.list_sources`

```python
def list_sources(
    self,
    kind: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:168](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L168).

#### Метод `Admin.validate_task`

```python
def validate_task(self, doc: Any) -> dict[str, Any]: ...
```

``TaskValidation``: schema + DAG + references (never raises for an invalid config).

Код: [service.py:191](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L191).

#### Метод `Admin.create_task`

```python
def create_task(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:247](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L247).

#### Метод `Admin.get_task_row`

```python
def get_task_row(self, conn: Any, task_id: str, lock: bool = False) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:261](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L261).

#### Метод `Admin.get_task`

```python
def get_task(self, task_id: str) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:272](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L272).

#### Метод `Admin.replace_task`

```python
def replace_task(
    self,
    task_id: str,
    doc: Mapping[str, Any],
    if_match: str | None,
    actor: str,
) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [service.py:277](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L277).

#### Метод `Admin.delete_task`

```python
def delete_task(self, task_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:304](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L304).

#### Метод `Admin.list_tasks`

```python
def list_tasks(
    self,
    source_id: str | None,
    package_id: str | None,
    package_version: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [service.py:336](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L336).

#### Метод `Admin.start_run`

```python
def start_run(
    self,
    task_id: str,
    body: Mapping[str, Any],
    actor: str,
    idempotency_key: str | None,
) -> dict[str, Any]: ...
```

Код: [service.py:408](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L408).

#### Метод `Admin.start_reprocessing`

```python
def start_reprocessing(
    self,
    body: Mapping[str, Any],
    actor: str,
    idempotency_key: str | None,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`, `ServiceUnavailable`.

Код: [service.py:431](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L431).

#### Метод `Admin.list_activations`

```python
def list_activations(
    self,
    task_id: str,
    stage_id: str,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:479](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L479).

#### Метод `Admin.activate`

```python
def activate(
    self,
    task_id: str,
    stage_id: str,
    body: Mapping[str, Any],
    actor: str,
) -> dict[str, Any]: ...
```

Read → check in the registry (no DB lock held during network calls) → write if the task is unchanged.

Винятки в коді методу: `ValidationFailed`, `AccessDeniedByPolicy`, `Conflict`, `JaneError`, `NotFound`.

Код: [service.py:510](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L510).

#### Метод `Admin.list_problem_groups`

```python
def list_problem_groups(
    self,
    source_id: str | None,
    status: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:678](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L678).

#### Метод `Admin.update_problem_group`

```python
def update_problem_group(
    self,
    group_id: str,
    patch: Mapping[str, Any],
    actor: str,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:700](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L700).

#### Метод `Admin.list_unknown`

```python
def list_unknown(
    self,
    source_id: str | None,
    forwarded: bool | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:716](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L716).

#### Метод `Admin.list_connections`

```python
def list_connections(
    self,
    kind: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:792](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L792).

#### Метод `Admin.get_connection`

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:811](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L811).

#### Метод `Admin.put_connection`

```python
def put_connection(
    self,
    connection_id: str,
    doc: Mapping[str, Any],
    if_match: str | None,
    actor: str,
) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `ValidationFailed`, `JaneError`, `PreconditionFailed`.

Код: [service.py:820](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L820).

#### Метод `Admin.delete_connection`

```python
def delete_connection(self, connection_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `NotFound`, `Conflict`.

Код: [service.py:868](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L868).

#### Метод `Admin.get_platform_limits`

```python
def get_platform_limits(self) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:898](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L898).

#### Метод `Admin.put_platform_limits`

```python
def put_platform_limits(
    self,
    doc: Mapping[str, Any],
    if_match: str | None,
    actor: str,
) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:902](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L902).

#### Метод `Admin.effective_limits`

```python
def effective_limits(
    self,
    source_id: str | None,
    task_id: str | None,
    stage_id: str | None,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`, `NotFound`.

Код: [service.py:925](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L925).

#### Метод `Admin.list_executors`

```python
def list_executors(self) -> list[dict[str, Any]]: ...
```

Код: [service.py:960](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L960).

#### Метод `Admin.list_audit`

```python
def list_audit(
    self,
    subject_type: str | None,
    subject_id: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:974](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L974).

### Клас `PreconditionFailed`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_orchestrator.service` |
| Успадкування | `JaneError` |
| Код | [service.py:36](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L36) |

```python
class PreconditionFailed(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'precondition_failed'` |  |
