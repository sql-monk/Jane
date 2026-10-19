# Модуль `jane_orchestrator.service`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/service.py](../../../../../services/orchestrator/src/jane_orchestrator/service.py). Не редагуйте вручну.

Management operations behind ``orchestrator.v1``: sources, tasks, runs, connections, limits, activations with audit, problem groups, unknown materials, executors.

## Класи

### Клас `Admin`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.service` |
| Код | [service.py:102](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L102) |

```python
class Admin: ...
```

#### Конструктор `Admin.__init__`

```python
def __init__(self, core: Core) -> None: ...
```

Код: [service.py:103](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L103).

#### Метод `Admin.create_source`

```python
def create_source(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:149](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L149).

#### Метод `Admin.get_source`

```python
def get_source(self, source_id: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:162](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L162).

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

Код: [service.py:169](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L169).

#### Метод `Admin.delete_source`

```python
def delete_source(self, source_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `NotFound`, `Conflict`.

Код: [service.py:195](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L195).

#### Метод `Admin.list_sources`

```python
def list_sources(
    self,
    kind: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:208](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L208).

#### Метод `Admin.validate_task`

```python
def validate_task(self, doc: Any) -> dict[str, Any]: ...
```

``TaskValidation``: schema + DAG + references (never raises for an invalid config).

Код: [service.py:231](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L231).

#### Метод `Admin.create_task`

```python
def create_task(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:287](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L287).

#### Метод `Admin.get_task_row`

```python
def get_task_row(self, conn: Any, task_id: str, lock: bool = False) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:301](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L301).

#### Метод `Admin.get_task`

```python
def get_task(self, task_id: str) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:312](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L312).

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

Код: [service.py:317](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L317).

#### Метод `Admin.delete_task`

```python
def delete_task(self, task_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:343](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L343).

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

Код: [service.py:375](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L375).

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

Код: [service.py:447](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L447).

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

Код: [service.py:470](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L470).

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

Код: [service.py:518](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L518).

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

Код: [service.py:549](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L549).

#### Метод `Admin.list_problem_groups`

```python
def list_problem_groups(
    self,
    source_id: str | None,
    status: str | None,
    cursor: str | None,
    limit: int,
    group_id: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:720](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L720).

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

Код: [service.py:750](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L750).

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

Код: [service.py:773](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L773).

#### Метод `Admin.list_connections`

```python
def list_connections(
    self,
    kind: str | None,
    cursor: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:865](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L865).

#### Метод `Admin.get_connection`

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], int]: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:884](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L884).

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

Код: [service.py:893](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L893).

#### Метод `Admin.delete_connection`

```python
def delete_connection(self, connection_id: str, actor: str) -> None: ...
```

Винятки в коді методу: `NotFound`, `Conflict`.

Код: [service.py:962](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L962).

#### Метод `Admin.get_platform_limits`

```python
def get_platform_limits(self) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:993](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L993).

#### Метод `Admin.put_platform_limits`

```python
def put_platform_limits(
    self,
    doc: Mapping[str, Any],
    if_match: str | None,
    actor: str,
) -> tuple[dict[str, Any], int]: ...
```

Код: [service.py:997](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L997).

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

Код: [service.py:1020](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L1020).

#### Метод `Admin.list_executors`

```python
def list_executors(self) -> list[dict[str, Any]]: ...
```

Код: [service.py:1055](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L1055).

#### Метод `Admin.list_audit`

```python
def list_audit(
    self,
    subject_type: str | None,
    subject_id: str | None,
    cursor: str | None,
    limit: int,
    since: datetime | None = None,
    until: datetime | None = None,
) -> tuple[list[dict[str, Any]], str | None]: ...
```

Код: [service.py:1069](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L1069).

### Клас `PreconditionFailed`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_orchestrator.service` |
| Успадкування | `JaneError` |
| Код | [service.py:75](../../../../../services/orchestrator/src/jane_orchestrator/service.py#L75) |

```python
class PreconditionFailed(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'precondition_failed'` |  |
