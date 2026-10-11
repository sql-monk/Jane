# Orchestrator

Зберігає джерела й завдання, запускає їх вручну або за розкладом і проводить матеріали ланцюжком етапів: колектор (`collector.v1`) → обробники (`handler.v1`). Черга етапів — у власній PostgreSQL з lease.

- Документація модуля: [docs/components/orchestrator](../../docs/components/orchestrator/README.md); швидкий старт — [quickstart.md](../../docs/components/orchestrator/quickstart.md).
- Запуск: `uv run --package jane-orchestrator python -m jane_orchestrator` (API з воркерами) або `… python -m jane_orchestrator worker` (лише воркери); потрібна PostgreSQL (`JANE_ORCHESTRATOR_DATABASE_URL`).
- Тести: `just test orchestrator` (unit і contract), `just test orchestrator -m integration` (потрібна PostgreSQL: dev-стек, `JANE_ORCHESTRATOR_TEST_DSN` або Docker).
- Контракт: [orchestrator.v1.yaml](../../contracts/openapi/orchestrator.v1.yaml).
