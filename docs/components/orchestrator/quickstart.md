# Швидкий старт Orchestrator

Orchestrator із власною PostgreSQL збирає дві сторінки тестового сайту через Web Collector і зберігає їх як RAW-файли через Storage. Джерело, завдання й запуск створюються через API. Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7 і Git Bash), ревізія `48389a3`; на Linux не перевірялися.

## Зміст

- [Передумови](#передумови)
- [Що запускається](#що-запускається)
- [Кроки](#кроки)
- [Без виконавців](#без-виконавців)
- [Прибирання](#прибирання)

## Передумови

- uv, just, Docker із Compose v2 — [DEVELOPMENT.md](../../../DEVELOPMENT.md#встановлення). Без встановленого just: `uvx --from rust-just just <рецепт>`.
- Залежності workspace: `uv sync --all-packages`.
- Усі команди — з кореня репозиторію; вільні порти 18610–18612 і 18620. Інші порти потребують змін у [examples/quickstart](examples/quickstart/).
- Сервіси запускаються без автентифікації (`auth_mode=none`) і слухають лише `127.0.0.1` — тільки для локальної перевірки.

## Що запускається

| Процес | Порт | Роль |
|---|---|---|
| PostgreSQL (Docker, проєкт `jane-doc-orch`) | обирає `just up` | Власна база `jane_orchestrator` |
| Тестовий сайт | 18620 | Джерело сторінок |
| Web Collector | 18611 | Виконавець `collector` |
| Storage | 18612 | Виконавець `handler` (пакет `jane.storage-files`) і `storage_read` |
| Orchestrator | 18610 | API і 2 воркери |

Файли прикладу лежать у [examples/quickstart](examples/quickstart/):

| Файл | Що описує |
|---|---|
| [executors.json](examples/quickstart/executors.json) | Три виконавці Orchestrator |
| [rules/quickstart.testsite-rules/1.0.0](examples/quickstart/rules/quickstart.testsite-rules/1.0.0/rules.json) | Правила Web Collector: дві сторінки товарів (`seed_list`) |
| [connection.json](examples/quickstart/connection.json) | Підключення `quickstart-raw` (файлова система, `.jane/orchestrator-quickstart/raw`) |
| [source.json](examples/quickstart/source.json) | Джерело `quickstart-testsite` з правилами колектора |
| [task.json](examples/quickstart/task.json) | Завдання `quickstart-products`: `collect` → `store-raw` |

Правила колектора читаються з локального каталогу (`JANE_WEB_COLLECTOR_RULES_DIR`), тож Registry не потрібен.

## Кроки

1. Підніміть PostgreSQL в окремому compose-проєкті:

   ```powershell
   just up --project jane-doc-orch postgres
   ```

   Уривок виводу (порт обирає `just up`; у перевірці його зафіксовано змінною `JANE_PORT_POSTGRES=18600`):

   ```text
   project: jane-doc-orch   (stack file: .jane/stack-jane-doc-orch.json)
     postgres   127.0.0.1:18600
     db-orchestrator postgresql://127.0.0.1:18600/jane_orchestrator
   ```

   `just up` створює базу `jane_orchestrator` і окремого користувача з паролем, що зберігається в `.jane/stack-jane-doc-orch.json`.

2. У першому терміналі запустіть тестовий сайт:

   ```powershell
   just testsite --port 18620
   ```

   ```text
   Jane testsite on http://127.0.0.1:18620/
   ```

3. У другому терміналі запустіть Web Collector.

   PowerShell:

   ```powershell
   $env:JANE_WEB_COLLECTOR_PORT = '18611'
   $env:JANE_WEB_COLLECTOR_STATE_DIR = '.jane/orchestrator-quickstart/web-collector'
   $env:JANE_WEB_COLLECTOR_RULES_DIR = 'docs/components/orchestrator/examples/quickstart/rules'
   uv run --package jane-web-collector python -m jane_web_collector
   ```

   Bash:

   ```bash
   JANE_WEB_COLLECTOR_PORT=18611 \
   JANE_WEB_COLLECTOR_STATE_DIR=.jane/orchestrator-quickstart/web-collector \
   JANE_WEB_COLLECTOR_RULES_DIR=docs/components/orchestrator/examples/quickstart/rules \
   uv run --package jane-web-collector python -m jane_web_collector
   ```

   У журналі з'являється `Uvicorn running on http://127.0.0.1:18611`.

4. У третьому терміналі запустіть Storage. `CONTENT_FILES_DIR` потрібен лише для повторної обробки збережених RAW ([integration.md](integration.md#повторна-обробка-збережених-raw)).

   PowerShell:

   ```powershell
   $env:JANE_STORAGE_PORT = '18612'
   $env:JANE_STORAGE_CONTENT_FILES_DIR = '.jane/orchestrator-quickstart/raw/objects'
   uv run --package jane-storage python -m jane_storage
   ```

   Bash:

   ```bash
   JANE_STORAGE_PORT=18612 \
   JANE_STORAGE_CONTENT_FILES_DIR=.jane/orchestrator-quickstart/raw/objects \
   uv run --package jane-storage python -m jane_storage
   ```

5. У четвертому терміналі запустіть Orchestrator з DSN бази з `just env`.

   PowerShell:

   ```powershell
   $env:JANE_ORCHESTRATOR_DATABASE_URL = ((just env --project jane-doc-orch | Select-String '^JANE_STACK_DB_ORCHESTRATOR_DB_DSN=').Line -split '=', 2)[1]
   $env:JANE_ORCHESTRATOR_PORT = '18610'
   $env:JANE_ORCHESTRATOR_EXECUTORS_FILE = 'docs/components/orchestrator/examples/quickstart/executors.json'
   $env:JANE_ORCHESTRATOR_LOG_FORMAT = 'console'
   uv run --package jane-orchestrator python -m jane_orchestrator
   ```

   Bash:

   ```bash
   export JANE_ORCHESTRATOR_DATABASE_URL=$(just env --project jane-doc-orch | sed -n 's/^JANE_STACK_DB_ORCHESTRATOR_DB_DSN=//p')
   JANE_ORCHESTRATOR_PORT=18610 \
   JANE_ORCHESTRATOR_EXECUTORS_FILE=docs/components/orchestrator/examples/quickstart/executors.json \
   JANE_ORCHESTRATOR_LOG_FORMAT=console \
   uv run --package jane-orchestrator python -m jane_orchestrator
   ```

   Під час першого старту створюється схема. Уривок журналу:

   ```text
   WARNING jane.auth: auth_mode=none: every caller has every scope - for local tests only
   WARNING jane_orchestrator.settings: executor has no bearer token {"executor": "web-collector"}
   INFO    jane_orchestrator.db: schema migrated {"version": 1}
   INFO    jane_orchestrator.db: schema migrated {"version": 7}
   INFO    uvicorn.error: Uvicorn running on http://127.0.0.1:18610 (Press CTRL+C to quit)
   ```

   Попередження про токен очікуване: локальні виконавці працюють без автентифікації.

6. У п'ятому терміналі перевірте стан і виконавців. Далі всі запити — з цього терміналу; у PowerShell задайте змінні один раз:

   ```powershell
   $api = 'http://127.0.0.1:18610/v1'
   $ex = 'docs/components/orchestrator/examples/quickstart'
   Invoke-RestMethod "$api/health" | ConvertTo-Json -Compress -Depth 5
   (Invoke-RestMethod "$api/executors").items | Select-Object executor, role, status
   ```

   ```text
   {"status":"ok","checks":{"database":{"status":"ok"}}}

   executor      role         status
   --------      ----         ------
   web-collector collector    ok
   storage       handler      ok
   storage-read  storage_read ok
   ```

7. Зареєструйте підключення для RAW-файлів. Orchestrator зберігає його й надсилає виконавцям:

   ```powershell
   Invoke-RestMethod -Method Put -Uri "$api/connections/quickstart-raw" -ContentType application/json -InFile "$ex/connection.json" | ConvertTo-Json -Depth 5
   ```

   Одразу після запиту синхронізація в стані `pending`; за секунду-дві `GET "$api/connections/quickstart-raw"` показує:

   ```json
   {"executor": "storage", "sync_status": "synced", "synced_at": "2026-10-11T10:44:29.3Z"}
   ```

8. Створіть джерело. `POST` створення вимагає `Idempotency-Key`:

   ```powershell
   Invoke-RestMethod -Method Post -Uri "$api/sources" -Headers @{'Idempotency-Key' = 'quickstart-source-1'} -ContentType application/json -InFile "$ex/source.json" | ConvertTo-Json -Depth 5
   ```

   ```json
   {
     "kind": "web",
     "title": "Jane test site",
     "locator": {"url": "http://127.0.0.1:18620/"},
     "source_id": "quickstart-testsite",
     "collector_rules": {"version": "1.0.0", "package_id": "quickstart.testsite-rules"},
     "created_at": "2026-10-11T10:44:36.443Z",
     "updated_at": "2026-10-11T10:44:36.443Z"
   }
   ```

9. Перевірте й створіть завдання:

   ```powershell
   Invoke-RestMethod -Method Post -Uri "$api/task-validations" -ContentType application/json -InFile "$ex/task.json" | ConvertTo-Json -Compress
   Invoke-RestMethod -Method Post -Uri "$api/tasks" -Headers @{'Idempotency-Key' = 'quickstart-task-1'} -ContentType application/json -InFile "$ex/task.json" | Out-Null
   ```

   ```text
   {"valid":true,"errors":[],"warnings":[],"effective_forward_unknown_to_llm":false}
   ```

10. Запустіть завдання й дочекайтесь кінцевого стану:

    ```powershell
    $run = Invoke-RestMethod -Method Post -Uri "$api/tasks/quickstart-products/runs" -Headers @{'Idempotency-Key' = 'quickstart-run-1'} -ContentType application/json -Body '{"reason": "quickstart"}'
    do { Start-Sleep -Seconds 1; $job = Invoke-RestMethod "$api/jobs/$($run.job_id)" } while ($job.status -in 'queued', 'running', 'cancelling')
    $job | ConvertTo-Json -Depth 5
    ```

    Відповідь на запуск — `Job` у стані `queued`; через кілька секунд:

    ```json
    {
      "job_id": "run_01M4N917B5JQXQ7JW8M46RE54X",
      "kind": "run",
      "status": "succeeded",
      "created_at": "2026-10-11T10:44:42.875Z",
      "updated_at": "2026-10-11T10:44:46.263Z",
      "progress": {"completed": 2, "total": 2, "unit": "items", "counters": {"materials": 2}},
      "links": {
        "self": "/v1/jobs/run_01M4N917B5JQXQ7JW8M46RE54X",
        "cancel": "/v1/jobs/run_01M4N917B5JQXQ7JW8M46RE54X/cancel",
        "run": "/v1/runs/run_01M4N917B5JQXQ7JW8M46RE54X"
      },
      "started_at": "2026-10-11T10:44:43.276Z",
      "finished_at": "2026-10-11T10:44:46.266Z",
      "idempotency_key": "quickstart-run-1"
    }
    ```

11. Перегляньте запуск, елементи етапу й шлях матеріалу:

    ```powershell
    Invoke-RestMethod "$api/runs/$($run.job_id)" | ConvertTo-Json -Depth 6
    $items = Invoke-RestMethod "$api/runs/$($run.job_id)/items?stage_id=store-raw"
    $items.items | Select-Object item_id, status, result_status, attempts, material_id
    Invoke-RestMethod "$api/materials/$($items.items[0].material_id)/trace" | ConvertTo-Json -Depth 8
    ```

    Уривок запуску — по два елементи на етапах, обидва виклики обробника `success`:

    ```json
    {
      "status": "succeeded",
      "trigger": "manual",
      "stages": [
        {"stage_id": "collect", "counts": {"completed": 2}},
        {"stage_id": "store-raw", "counts": {"completed": 2, "success": 2}, "handler": {"version": "1.0.0", "package_id": "jane.storage-files"}}
      ],
      "counters": {"materials": 2, "unknown_materials": 0},
      "backpressure": false,
      "collection_id": "job_937dc4c4b04945899d224b5bdc65686e"
    }
    ```

    ```text
    item_id                        status    result_status attempts material_id
    -------                        ------    ------------- -------- -----------
    itm_01M4N918XKTS9RWZ4Y983JWTRN completed success              1 web:22be6f10b0be61ac98484bc71817cc43
    itm_01M4N919WMCANN2REN0MZ1MTMM completed success              1 web:33ff398d154b658ae710e19726c55a1a
    ```

    Уривок простежуваності: спостереження, версія пакета з digest, виклик і збережений об'єкт:

    ```json
    {
      "material_id": "web:22be6f10b0be61ac98484bc71817cc43",
      "observations": [
        {
          "observation_id": "obs_01a12a90a34d0000ebfc19e4",
          "run_id": "run_01M4N917B5JQXQ7JW8M46RE54X",
          "task_id": "quickstart-products",
          "stages": [
            {
              "stage_id": "store-raw",
              "status": "completed",
              "attempts": 1,
              "handler": {"digest": "sha256:b87649411631a78b58f4e44e304dab362526e21861705a2e04f8a8a6d6aec12f", "version": "1.0.0", "package_id": "jane.storage-files"},
              "invocation_id": "inv_01a12a90a55964eadc906b2b2b17",
              "result_status": "success",
              "outputs": [{"kind": "stored_object", "object_id": "obj_ed87ba60eab8ace207ac76747d712e37", "connection_id": "quickstart-raw"}]
            }
          ],
          "fetched_at": "2026-10-11T10:44:44Z",
          "content_sha256": "fbff2501c24e5e29e62bfffae13666cb953c0976e7bc03eba046fa3cd01364eb"
        }
      ],
      "source_id": "quickstart-testsite",
      "url": "http://127.0.0.1:18620/product/laptop-four"
    }
    ```

    Збережені сторінки лежать у `.jane/orchestrator-quickstart/raw`.

Кроки 6–10 у Bash (перевірено в Git Bash на Windows):

```bash
API=http://127.0.0.1:18610/v1
EX=docs/components/orchestrator/examples/quickstart
curl -s $API/health
curl -s -X PUT $API/connections/quickstart-raw -H 'Content-Type: application/json' --data-binary @$EX/connection.json
curl -s -X POST $API/sources -H 'Idempotency-Key: quickstart-source-1' -H 'Content-Type: application/json' --data-binary @$EX/source.json
curl -s -X POST $API/task-validations -H 'Content-Type: application/json' --data-binary @$EX/task.json
curl -s -X POST $API/tasks -H 'Idempotency-Key: quickstart-task-1' -H 'Content-Type: application/json' --data-binary @$EX/task.json
JOB=$(curl -s -X POST $API/tasks/quickstart-products/runs -H 'Idempotency-Key: quickstart-run-1' -H 'Content-Type: application/json' -d '{"reason": "quickstart"}' | sed -E 's/.*"job_id":"([^"]+)".*/\1/')
until curl -s $API/jobs/$JOB | grep -Eq '"status":"(succeeded|failed|cancelled)"'; do sleep 1; done
curl -s $API/jobs/$JOB
```

Ці команди виконувалися після PowerShell-варіанта з тими самими `Idempotency-Key`: `POST /v1/sources` і `/v1/tasks` повернули збережені відповіді `201`, а запуск — той самий `job_id` без створення нового запуску. Так працює ідемпотентність API.

## Без виконавців

Якщо пропустити кроки 2–4 (або залишити `executors.json` порожнім), кроки 6–9 працюють так само, а запуск переходить у `running` і не отримує матеріалів: подача повторюється з помилкою `503` і завершується `failed` з кодом `timeout` лише після `timeouts.run_timeout_ms` (типово 6 годин). Скасуйте такий запуск через `POST "$api/runs/<run_id>/cancel"`. Цей варіант у межах документації не запускався; поведінку описано за кодом ([dependencies.md](dependencies.md#поведінка-без-виконавців)).

## Прибирання

1. Зупиніть Orchestrator, Storage, Web Collector і тестовий сайт через `Ctrl+C`.
2. Команда нижче зупиняє PostgreSQL і **видаляє всі дані проєкту `jane-doc-orch`**: том бази з джерелами, завданнями й запусками та файл `.jane/stack-jane-doc-orch.json` із паролями:

   ```powershell
   just down -v --project jane-doc-orch
   ```

3. Видаліть локальний стан прикладу — збережені RAW і стан Web Collector у каталозі `.jane/orchestrator-quickstart` (поза Git).

   PowerShell:

   ```powershell
   Remove-Item -Recurse -Force .jane/orchestrator-quickstart
   ```

   Bash:

   ```bash
   rm -rf .jane/orchestrator-quickstart
   ```
