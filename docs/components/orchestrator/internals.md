# Будова й дані Orchestrator

Core відкриває Database, schemas, executor clients та limits. Admin реалізує config API; Engine/Worker виконують feed, item, schedule і sync.

## Класи й модулі

![Класи Orchestrator](../../diagrams/orchestrator/classes.light.png)

[Темна тема](../../diagrams/orchestrator/classes.dark.png) · [Draw.io](../../diagrams/orchestrator/classes.drawio)

Dag/conditions/routing — чиста перевірка graph та fan-out. Executors ізолює HTTP, Runs зберігає snapshot/views, Stored_raw відновлює Material зі Storage metadata. Декларації — в [довіднику](reference/types/README.md).

## Дані

![Дані Orchestrator](../../diagrams/orchestrator/data.light.png)

[Темна тема](../../diagrams/orchestrator/data.dark.png) · [Draw.io](../../diagrams/orchestrator/data.drawio)

[db.py](../../../services/orchestrator/src/jane_orchestrator/db.py) створює sources/tasks/runs/items, activations/audit_events, connections/connection_sync/platform_limits і problem/unknown таблиці. Run зберігає snapshot. Items мають unique(run_id,stage_id,item_key). Схема показує логічні зв’язки, не кожен є SQL foreign key.

Міграції idempotent і серіалізовані advisory lock. Queue claims використовують SKIP LOCKED/lease: кілька процесів поділяють own database.

## Алгоритм

![Алгоритм доставки](../../diagrams/orchestrator/delivery-flow.light.png)

[Темна тема](../../diagrams/orchestrator/delivery-flow.dark.png) · [Draw.io](../../diagrams/orchestrator/delivery-flow.drawio)

TaskConfig має рівно один collect, існуючі input.from та ациклічний DAG; handler потребує input. Topo_order повертає порядок або None при циклі.

Feed читає Material page, транзакційно створює items і лише тоді просуває cursor. Queue/inflight caps зупиняють читання, buffer колектора дає backpressure. Routing застосовує bindings/when; матеріал має observation_id item_key, похідний — upstream item_id + edge index.

Handler викликається зі сталим delivery_key. Result/downstream items/item completion пишуться однією транзакцією. Повтор після crash зберігає ключ; відсутність дублю ефекту вимагає idempotent executor зі shared state у межах TTL.

## Стани й повтори

![Стани item](../../diagrams/orchestrator/states.light.png)

[Темна тема](../../diagrams/orchestrator/states.dark.png) · [Draw.io](../../diagrams/orchestrator/states.drawio)

Queued/retrying отримує lease й стає running. Retryable error повторюється з backoff у межах attempts; non-retryable завершується failed. Expired lease можна забрати; max_lease_reclaims обмежує падіння й не тотожний retries.max_attempts.

Run має queued/running/cancelling і кінцеві стани [контракту](../../../contracts/openapi/orchestrator.v1.yaml). Cancel не відкочує записані бізнес-дані. Idempotency_in_progress паркує item зі сталим ключем, не створює нову доставку.
