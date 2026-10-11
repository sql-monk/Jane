# Типи й члени Orchestrator

[Повний каталог декларацій](generated/README.md) охоплює public symbols, methods/properties, parameters/defaults, inheritance та код. Нижче — семантика й винятки понад сигнатури.

## Модулі

| Модуль | Призначення членів |
|---|---|
| [core](generated/jane_orchestrator.core.md) | Core/open/close, own DB/schemas/executors/limits |
| [db](generated/jane_orchestrator.db.md) | Database/open/close/ping/transaction/migrate, Jsonb та schema migration constants |
| [service](generated/jane_orchestrator.service.md) | Admin config CRUD/validation, run/reprocess, connection/limit/activation/audit views |
| [engine](generated/jane_orchestrator.engine.md) | Engine claims/feed/item/schedule/sync/reap; Worker threads і Heartbeat |
| [runs](generated/jane_orchestrator.runs.md) | Runs snapshot creation/views/job/cancel і run counts |
| [executors](generated/jane_orchestrator.executors.md) | ExecutorRegistry/client routing, HTTP failure і health |
| [dag](generated/jane_orchestrator.dag.md) | stage_map/topo_order/validate_task/effective_forward_unknown |
| [routing](generated/jane_orchestrator.routing.md) | NewItem/UnknownDecision/MaterialRouting, route_material/route_result та deterministic fan-out |
| [conditions](generated/jane_orchestrator.conditions.md) | Evaluate conditions, URL/binding/entity matching |
| [limits](generated/jane_orchestrator.limits.md) | Platform/effective limits, hard caps та provenance |
| [schedule](generated/jane_orchestrator.schedule.md) | Cron/timezone parsing, next tick, overlap semantics |
| [stored_raw](generated/jane_orchestrator.stored_raw.md) | RAW metadata → Material без читання таблиць Storage |
| [common](generated/jane_orchestrator.common.md) | ID/time/ETag/delivery key helpers |
| [auth](generated/jane_orchestrator.auth.md) | Principal/caller scopes |
| [contract](generated/jane_orchestrator.contract.md) | OpenAPI/JSON schema request validation |
| [idempotency](generated/jane_orchestrator.idempotency.md) | Own PostgreSQL claims adapter |
| [settings](generated/jane_orchestrator.settings.md) | Settings/ExecutorConfig/contracts/internal limits |
| [app](generated/jane_orchestrator.app.md) | HTTP app/lifespan/threaded DB routes |
| [__main__](generated/jane_orchestrator.__main__.md) | API та standalone worker process |

## Контракт операцій

Admin methods приймають schema-valid config та actor, а повертають document/version або run/job views. CRUD missing → NotFound; duplicate → Conflict; неправильний If-Match → precondition_failed. Validate_task дає errors/warnings, не запускає job. Run creation перевіряє source/DAG/effective limits і зберігає snapshot транзакційно.

Database transaction повертає connection контекст; commit/rollback належить context manager. Database.open виконує own migrations; PostgreSQL exception не є гарантією побічного ефекту виконавця. Core.close закриває DB/clients; Worker.stop зупиняє свій loop. Heartbeat context продовжує lease на час зовнішньої роботи.

Engine.claim_item/feed повертає mapping або None. Process_item/feed виконує вже взяту lease; запис захищений owner/status check. Retryable executor errors планують backoff; non-retryable завершують failure. Reap обробляє drained/cancelled/timeout runs. Worker не створює новий delivery key після lease takeover.

ExecutorConfig.syncs_connections — read-only property: явний sync_connections, інакше role/capabilities. Settings.executor_configs читає list/file без token resolution; all_executors вирішує token_ref/default і зупиняє старт при невирішеному ref. Token і token_ref одночасно не дозволені.

## Чисті функції

Topo_order повертає list stage IDs або None при cycle. Validate_task повертає tuple errors/warnings; schema validation перед ним — обов’язок caller. Effective_forward_unknown бере task override, потім source, потім false.

Route_material повертає MaterialRouting із NewItem і UnknownDecision; route_result формує downstream items за selected output/when. ContentRef передається посиланням; функції не виконують HTTP або business writes. Нові items потребують unique key у DB. Schedule parsing/invalid timezone/config може підняти validation/value errors; вводи перевіряються контрактом до scheduling.

## Приклад перевірки DAG

```python
import json
from pathlib import Path
from jane_orchestrator.dag import topo_order, validate_task

source = json.loads(Path("examples/documents/source.testsite-shop.json")
                    .read_text(encoding="utf-8"))
task = json.loads(Path("examples/documents/task.testsite-catalog.json")
                  .read_text(encoding="utf-8"))
errors, warnings = validate_task(task, source,
                                {"raw-files", "results-pg"})
assert not errors
assert topo_order(task) is not None
```

Виконайте через uv run --all-packages python із кореня checkout. Це семантика DAG, не executor/pipeline test. [Сторонній HTTP-клієнт](../../integration.md#клієнт-запуску) показує job/run protocol; [configuration](../../configuration.md) — budgets, [internals](../../internals.md) — queue/routing semantics.
