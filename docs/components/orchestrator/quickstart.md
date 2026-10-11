# Швидкий старт Orchestrator

Мінімальний API потребує власної PostgreSQL. Без collector/handler він перевіряє конфігураційний контур; фактичний DAG потребує своїх виконавців.

## Мінімальний сервер

Потрібні checkout Jane, uv, Python із [.python-version](../../../.python-version) та власна БД jane_orchestrator із правами міграцій. Версія тестової PostgreSQL — в [compose](../../../infra/compose.yaml). Не додавайте DSN-пароль до репозиторію.

PowerShell:

```powershell
$env:JANE_ORCHESTRATOR_DATABASE_URL = $env:JANE_DOCUMENTATION_ORCHESTRATOR_DSN
$env:JANE_ORCHESTRATOR_RUN_WORKERS = 'false'
uv sync --all-packages
uv run --all-packages jane-orchestrator
```

Linux/Bash:

```bash
export JANE_ORCHESTRATOR_DATABASE_URL="$JANE_DOCUMENTATION_ORCHESTRATOR_DSN"
export JANE_ORCHESTRATOR_RUN_WORKERS=false
uv sync --all-packages
uv run --all-packages jane-orchestrator
```

JANE_DOCUMENTATION_ORCHESTRATOR_DSN — обрана для цього прикладу зовнішня змінна, не параметр Orchestrator. Задайте її вашим DSN перед запуском. Типові host/port — 127.0.0.1:8109. Сервер відкриває own database і створює таблиці.

В іншому терміналі:

```powershell
uv run python -c "import httpx; r=httpx.get('http://127.0.0.1:8109/v1/health'); print(r.status_code); print(r.json())"
uv run python -c "import httpx; r=httpx.get('http://127.0.0.1:8109/v1/sources'); r.raise_for_status(); print(r.json())"
```

Для нової DB sources порожній. Health перевіряє власну PostgreSQL; він не доводить executor health. При api_key/jwt другий запит потребує bearer token. Ctrl+C зупиняє API без видалення БД.

## Перший pipeline

Для реального збору потрібні Registry, collector, Runtime, Storage і пакети. Повний профіль описаний у [README](../../../README.md#швидкий-старт):

```powershell
uv run --all-packages python deploy/profiles/stack.py up --project jane-doc-orch --profile dev-laptop
uv run --all-packages python examples/jane_examples.py demo --project jane-doc-orch
uv run --all-packages python deploy/profiles/stack.py env --project jane-doc-orch
```

Demo публікує пакети, створює source/task, збирає каталог, перевіряє ціни й Storage. Критерій — ok=true, failures=[], фактичні RAW/entities. Кількості залежать від fixture revision. Coordinator-run demo не замінює доказ мінімального API.

Команда видаляє стенд jane-doc-orch **разом із його тестовими даними**:

```powershell
uv run --all-packages python deploy/profiles/stack.py down --project jane-doc-orch
```

## Діагностика

| Ознака | Дія |
|---|---|
| Не стартує | DSN, права міграцій, contracts path |
| Queued без прогресу | Workers, role та capabilities |
| Upstream unavailable | Health/base_url/token сусіда |
| Task validation errors | Виправити source/DAG/connection |
| Sync pending | Executor не підтвердив connection PUT |

Мінімальний запуск на обох ОС потребує окремого незалежного підтвердження; стан — у [звіті](../../delivery/documentation/DOC-05-orchestrator.md).
