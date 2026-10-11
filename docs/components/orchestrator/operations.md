# Експлуатація Orchestrator

API і workers працюють разом або окремо з однією власною PostgreSQL. API-only потребує run_workers=false; окремий worker:

```powershell
uv run --all-packages python -m jane_orchestrator worker
```

Standalone команда запускає щонайменше один thread. Engine.workers=0 не вимикає цю команду; використовуйте API-only параметр.

## Спостереження

Health перевіряє own DB, executor status — /v1/executors. Health API не підтверджує доступність package/RAW. Переглядайте run/items, retries/leases, sync, problem groups і unknown materials. Metrics/logs/material trace пов’язують передачі.

![Процес оператора Orchestrator](../../diagrams/orchestrator/operator-process.light.png)

[Темна тема](../../diagrams/orchestrator/operator-process.dark.png) · [Draw.io](../../diagrams/orchestrator/operator-process.drawio)

Перед activation протестуйте package, виконайте test_mode run, перевірте Result і diagnostics. Test mode не є універсальним rollback зовнішніх ефектів: executor має дотриматися свого контракту.

## Оновлення й масштабування

Env/executors застосовуються після restart. Platform limits API зберігає документ у DB, source/task/stage формують новий snapshot. Heartbeat тримайте коротшим за lease з урахуванням часу виклику.

Worker processes мають ділити DB та сумісні executor identity/tokens. Threads не підвищують ліміти сусідів. Scheduler серіалізує due tasks; overlap policy керує очікуванням/пропуском/паралельністю.

## Backup й recovery

Резервуйте всю own DB: configs, snapshots, queue, activation/audit, connection sync, limits і keys. Registry blobs, Storage RAW/results та secrets резервуються окремо. DB Orchestrator не містить package ZIP або бізнес-сутності.

Після restore перевірте migrations/executors/secrets/sync/ContentRef, потім workers/scheduler. Expired leases дозволяють takeover зі сталим ключем. Стара копія state може втратити останні підтвердження: перед повтором звірте зовнішній ефект із executor.

| Проблема | Дія |
|---|---|
| Queued без прогресу | Workers, role/capabilities |
| Багато retrying | Problem code/retryable і health сусіда |
| Lease reclaims | Worker crash, heartbeat, DB/network |
| RAW недоступний | Restore persistent RAW або переотримати |
| Sync failed | Endpoint, secret ref, connections capability |
| Run завершений, даних немає | Storage stage/test_mode/Result writes |

Мінімальний API Windows/Linux, багатовузловий takeover і аварійне recovery потребують окремого незалежного доказу.
