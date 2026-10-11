# Залежності Orchestrator

Власна PostgreSQL зберігає config, queue, leases, history та keys. Redis/RabbitMQ для engine не потрібні: claims використовують FOR UPDATE SKIP LOCKED.

| Залежність | Коли потрібна | Недоступність |
|---|---|---|
| Python ≥3.12, Jane Kit та [pyproject](../../../services/orchestrator/pyproject.toml) | API/worker | Старт неможливий |
| Власна PostgreSQL | Завжди | API/worker не підтверджують роботу |
| contracts | Валідація API/config | Старт або validation помилковий |
| Collector v1 | Збір | Feed retry/failure |
| Handler v1 | Handler stage | Item retries/failure |
| Storage v1 reader | Stored RAW/reprocessing | Вибірка RAW не працює |
| Registry v1 | Package metadata у відповідних операціях | Сумісність/операція не підтверджується |
| LLM/Assistant | Лише відповідні workflow | Опційні для deterministic DAG |

Версії Python-залежностей — у [uv.lock](../../../uv.lock), тестова PostgreSQL — у [compose](../../../infra/compose.yaml). Без executor можна керувати конфігурацією, але не заявляти pipeline виконаним.

## Сумісна заміна

ExecutorConfig містить executor/role/base_url/capabilities/token_ref. Сумісний collector має collect/material pages/cancel та cursor semantics; handler — inputs/Result/Job/replay/limits. Package/version TaskConfig мають бути доступні виконавцю.

Connections синхронізуються окремою чергою PUT/DELETE. sync_connections=false або capabilities.connections=false вимикає sync для executor. Handler Runtime не приймає керовані connections.

## Власність

Source/task/run/item/problem/audit належать Orchestrator. RAW, сутності й package ZIP залишаються у власників. Stored RAW читається через Storage API та ContentRef; transit refs мають бути доступні до завершення передачі.
