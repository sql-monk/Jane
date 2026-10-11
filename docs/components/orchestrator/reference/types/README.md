# Типи й члени: Orchestrator

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator](../../../../../services/orchestrator/src/jane_orchestrator). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_orchestrator`](jane_orchestrator.md) | 0 | 0 | Orchestrator of the Jane platform. |
| [`jane_orchestrator.__main__`](jane_orchestrator.__main__.md) | 0 | 2 | Entry point. |
| [`jane_orchestrator.app`](jane_orchestrator.app.md) | 0 | 1 | HTTP API of the orchestrator (``contracts/openapi/orchestrator.v1.yaml``). |
| [`jane_orchestrator.auth`](jane_orchestrator.auth.md) | 1 | 1 | Bearer authentication (ADR-0005) of the orchestrator, implemented by ``jane_kit.auth``. |
| [`jane_orchestrator.common`](jane_orchestrator.common.md) | 0 | 7 | Small helpers shared by the orchestrator modules: ids, time, hashing, JSON pointers. |
| [`jane_orchestrator.conditions`](jane_orchestrator.conditions.md) | 0 | 7 | Transition conditions (``TaskConfig`` ``Condition``), URL patterns and extractor bindings. |
| [`jane_orchestrator.contract`](jane_orchestrator.contract.md) | 1 | 0 | Request validation against ``contracts/openapi/orchestrator.v1.yaml`` (the source of truth). |
| [`jane_orchestrator.core`](jane_orchestrator.core.md) | 2 | 0 | Shared state of one orchestrator process: DB, contract schemas, executors, limits, metrics. |
| [`jane_orchestrator.dag`](jane_orchestrator.dag.md) | 0 | 4 | Semantic validation of ``TaskConfig`` beyond the JSON Schema (task-config.schema.json description): exactly one ``collect`` stage, acyclic graph, every ``from`` |
| [`jane_orchestrator.db`](jane_orchestrator.db.md) | 1 | 0 | The orchestrator's own PostgreSQL database: connection pool and schema migrations. |
| [`jane_orchestrator.engine`](jane_orchestrator.engine.md) | 2 | 0 | Queue engine: workers with leases over the orchestrator's PostgreSQL (``FOR UPDATE SKIP LOCKED``). |
| [`jane_orchestrator.executors`](jane_orchestrator.executors.md) | 2 | 0 | Calls to the services the orchestrator combines (collector.v1, handler.v1, storage.v1, registry.v1). |
| [`jane_orchestrator.idempotency`](jane_orchestrator.idempotency.md) | 0 | 1 | ``Idempotency-Key`` storage in the orchestrator DB, so several API instances share it. |
| [`jane_orchestrator.limits`](jane_orchestrator.limits.md) | 2 | 3 | Effective limits (``limits.schema.json``): platform → source → task → stage → request, with hard caps. |
| [`jane_orchestrator.routing`](jane_orchestrator.routing.md) | 2 | 5 | Fan-out of the stage DAG: which items a material or a handler result creates downstream (pure logic). |
| [`jane_orchestrator.runs`](jane_orchestrator.runs.md) | 1 | 0 | Runs: creation (with a snapshot of the task, source and effective limits), state, cancellation, items, the material trace and the ``Job`` view (run_id = job_id, |
| [`jane_orchestrator.schedule`](jane_orchestrator.schedule.md) | 1 | 2 | Next fire time of a ``Schedule`` (manual \| once \| cron \| interval), IANA time zones via zoneinfo. |
| [`jane_orchestrator.service`](jane_orchestrator.service.md) | 2 | 0 | Management operations behind ``orchestrator.v1``: sources, tasks, runs, connections, limits, activations with audit, problem groups, unknown materials, executor |
| [`jane_orchestrator.settings`](jane_orchestrator.settings.md) | 9 | 1 | Settings and limits of the orchestrator. Every limit has a safe default documented in README.md. |
| [`jane_orchestrator.stored_raw`](jane_orchestrator.stored_raw.md) | 0 | 1 | RAW references recorded by the orchestrator itself; no reads of storage-owned tables. |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`Admin`](jane_orchestrator.service.md#клас-admin) | клас | `jane_orchestrator.service` |
| [`binding_matches`](jane_orchestrator.conditions.md#функція-binding_matches) | функція | `jane_orchestrator.conditions` |
| [`build_app`](jane_orchestrator.app.md#функція-build_app) | функція | `jane_orchestrator.app` |
| [`caller`](jane_orchestrator.auth.md#функція-caller) | функція | `jane_orchestrator.auth` |
| [`collect_stage_id`](jane_orchestrator.routing.md#функція-collect_stage_id) | функція | `jane_orchestrator.routing` |
| [`Concurrency`](jane_orchestrator.settings.md#клас-concurrency) | клас | `jane_orchestrator.settings` |
| [`condition_uses_entity`](jane_orchestrator.conditions.md#функція-condition_uses_entity) | функція | `jane_orchestrator.conditions` |
| [`ContractDefaults`](jane_orchestrator.settings.md#клас-contractdefaults) | клас | `jane_orchestrator.settings` |
| [`ContractSchemas`](jane_orchestrator.contract.md#клас-contractschemas) | клас | `jane_orchestrator.contract` |
| [`Core`](jane_orchestrator.core.md#клас-core) | клас | `jane_orchestrator.core` |
| [`CronError`](jane_orchestrator.schedule.md#клас-cronerror) | виняток | `jane_orchestrator.schedule` |
| [`Database`](jane_orchestrator.db.md#клас-database) | клас | `jane_orchestrator.db` |
| [`delivery_key`](jane_orchestrator.common.md#функція-delivery_key) | функція | `jane_orchestrator.common` |
| [`Effective`](jane_orchestrator.limits.md#клас-effective) | dataclass | `jane_orchestrator.limits` |
| [`effective_forward_unknown`](jane_orchestrator.dag.md#функція-effective_forward_unknown) | функція | `jane_orchestrator.dag` |
| [`Engine`](jane_orchestrator.engine.md#клас-engine) | клас | `jane_orchestrator.engine` |
| [`EngineLimits`](jane_orchestrator.settings.md#клас-enginelimits) | клас | `jane_orchestrator.settings` |
| [`EngineMetrics`](jane_orchestrator.core.md#клас-enginemetrics) | dataclass | `jane_orchestrator.core` |
| [`etag`](jane_orchestrator.common.md#функція-etag) | функція | `jane_orchestrator.common` |
| [`evaluate`](jane_orchestrator.conditions.md#функція-evaluate) | функція | `jane_orchestrator.conditions` |
| [`ExecutorConfig`](jane_orchestrator.settings.md#клас-executorconfig) | модель Pydantic | `jane_orchestrator.settings` |
| [`ExecutorError`](jane_orchestrator.executors.md#клас-executorerror) | dataclass | `jane_orchestrator.executors` |
| [`Executors`](jane_orchestrator.executors.md#клас-executors) | клас | `jane_orchestrator.executors` |
| [`flatten`](jane_orchestrator.limits.md#функція-flatten) | функція | `jane_orchestrator.limits` |
| [`get_path`](jane_orchestrator.common.md#функція-get_path) | функція | `jane_orchestrator.common` |
| [`glob_to_regex`](jane_orchestrator.conditions.md#функція-glob_to_regex) | функція | `jane_orchestrator.conditions` |
| [`idempotency_store`](jane_orchestrator.idempotency.md#функція-idempotency_store) | функція | `jane_orchestrator.idempotency` |
| [`LimitsLayer`](jane_orchestrator.limits.md#клас-limitslayer) | dataclass (незмінний) | `jane_orchestrator.limits` |
| [`main`](jane_orchestrator.__main__.md#функція-main) | функція | `jane_orchestrator.__main__` |
| [`material_of`](jane_orchestrator.routing.md#функція-material_of) | функція | `jane_orchestrator.routing` |
| [`material_url`](jane_orchestrator.conditions.md#функція-material_url) | функція | `jane_orchestrator.conditions` |
| [`merge_limits`](jane_orchestrator.limits.md#функція-merge_limits) | функція | `jane_orchestrator.limits` |
| [`new_id`](jane_orchestrator.common.md#функція-new_id) | функція | `jane_orchestrator.common` |
| [`NewItem`](jane_orchestrator.routing.md#клас-newitem) | dataclass | `jane_orchestrator.routing` |
| [`next_fire`](jane_orchestrator.schedule.md#функція-next_fire) | функція | `jane_orchestrator.schedule` |
| [`now`](jane_orchestrator.common.md#функція-now) | функція | `jane_orchestrator.common` |
| [`parse_cron`](jane_orchestrator.schedule.md#функція-parse_cron) | функція | `jane_orchestrator.schedule` |
| [`parse_etag`](jane_orchestrator.common.md#функція-parse_etag) | функція | `jane_orchestrator.common` |
| [`PreconditionFailed`](jane_orchestrator.service.md#клас-preconditionfailed) | виняток | `jane_orchestrator.service` |
| [`Principal`](jane_orchestrator.auth.md#клас-principal) | dataclass (незмінний) | `jane_orchestrator.auth` |
| [`Queue`](jane_orchestrator.settings.md#клас-queue) | клас | `jane_orchestrator.settings` |
| [`resolve_service_limits`](jane_orchestrator.settings.md#функція-resolve_service_limits) | функція | `jane_orchestrator.settings` |
| [`result_context`](jane_orchestrator.routing.md#функція-result_context) | функція | `jane_orchestrator.routing` |
| [`rfc3339`](jane_orchestrator.common.md#функція-rfc3339) | функція | `jane_orchestrator.common` |
| [`route_material`](jane_orchestrator.routing.md#функція-route_material) | функція | `jane_orchestrator.routing` |
| [`route_result`](jane_orchestrator.routing.md#функція-route_result) | функція | `jane_orchestrator.routing` |
| [`run_workers`](jane_orchestrator.__main__.md#функція-run_workers) | функція | `jane_orchestrator.__main__` |
| [`Runs`](jane_orchestrator.runs.md#клас-runs) | клас | `jane_orchestrator.runs` |
| [`ServiceLimits`](jane_orchestrator.settings.md#клас-servicelimits) | клас | `jane_orchestrator.settings` |
| [`Settings`](jane_orchestrator.settings.md#клас-settings) | модель Pydantic | `jane_orchestrator.settings` |
| [`stage_bindings_match`](jane_orchestrator.conditions.md#функція-stage_bindings_match) | функція | `jane_orchestrator.conditions` |
| [`stage_map`](jane_orchestrator.dag.md#функція-stage_map) | функція | `jane_orchestrator.dag` |
| [`stored_raw_id`](jane_orchestrator.stored_raw.md#функція-stored_raw_id) | функція | `jane_orchestrator.stored_raw` |
| [`Timeouts`](jane_orchestrator.settings.md#клас-timeouts) | клас | `jane_orchestrator.settings` |
| [`topo_order`](jane_orchestrator.dag.md#функція-topo_order) | функція | `jane_orchestrator.dag` |
| [`Transfer`](jane_orchestrator.settings.md#клас-transfer) | клас | `jane_orchestrator.settings` |
| [`unflatten`](jane_orchestrator.limits.md#функція-unflatten) | функція | `jane_orchestrator.limits` |
| [`UnknownDecision`](jane_orchestrator.routing.md#клас-unknowndecision) | dataclass | `jane_orchestrator.routing` |
| [`url_pattern_matches`](jane_orchestrator.conditions.md#функція-url_pattern_matches) | функція | `jane_orchestrator.conditions` |
| [`validate_task`](jane_orchestrator.dag.md#функція-validate_task) | функція | `jane_orchestrator.dag` |
| [`Worker`](jane_orchestrator.engine.md#клас-worker) | клас | `jane_orchestrator.engine` |
