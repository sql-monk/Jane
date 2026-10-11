# Assistant: швидкий старт

Запуск Assistant без Docker і бази даних разом з LLM gateway у режимі `memory` з провайдером `fake`. Результат — аналіз невідомого матеріалу, відмова за вимкненого прапорця, поведінка за ненастроєного сусіда та повний процесний сценарій на контрактних фейках сусідів.

Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7), ревізія `48389a3`; сервіси слухали інші порти, у командах — 8110 і 8111. На Linux не перевірялися. Варіанти Bash для кроків 1–2 не виконувалися; HTTP-запити ті самі, що в PowerShell.

## Зміст

- [Передумови](#передумови)
- [Запуск](#запуск)
- [Невідомий матеріал](#невідомий-матеріал)
- [Недоступний сусід](#недоступний-сусід)
- [Повний сценарій на фейках сусідів](#повний-сценарій-на-фейках-сусідів)
- [Підключення реального джерела з fake-моделлю](#підключення-реального-джерела-з-fake-моделлю)
- [Очікуваний результат](#очікуваний-результат)
- [Прибирання](#прибирання)

## Передумови

- uv і Python 3.12 — [середовище розробки](../../development/environment.md); залежності встановлено командою `uv sync --all-packages` з кореня репозиторію.
- PowerShell 7 (команди використовують `-SkipHttpErrorCheck`).
- Порти `8110` і `8111` вільні.
- Команди виконуються з кореня репозиторію.

## Запуск

1. У першому терміналі запустіть LLM gateway без бази.

   PowerShell:

   ```powershell
   $env:JANE_LLM_STORE = "memory"
   uv run --package jane-llm python -m jane_llm
   ```

   Bash:

   ```bash
   JANE_LLM_STORE=memory uv run --package jane-llm python -m jane_llm
   ```

2. У другому терміналі запустіть Assistant з адресою шлюзу. Без `JANE_ASSISTANT_STATE_DSN` стан тримається в пам'яті; порт задано явно, бо типовий `8000` часто зайнятий.

   PowerShell:

   ```powershell
   $env:JANE_ASSISTANT_PORT = "8111"
   $env:JANE_ASSISTANT_LLM_URL = "http://127.0.0.1:8110"
   uv run --package jane-assistant python -m jane_assistant
   ```

   Bash:

   ```bash
   JANE_ASSISTANT_PORT=8111 JANE_ASSISTANT_LLM_URL=http://127.0.0.1:8110 uv run --package jane-assistant python -m jane_assistant
   ```

   У журналі з'являються `auth_mode=none: every caller has every scope - for local tests only` і `Application startup complete.`

3. У третьому терміналі перевірте, яких сусідів бачить Assistant:

   ```powershell
   (Invoke-RestMethod http://127.0.0.1:8111/v1/info).capabilities | ConvertTo-Json -Compress -Depth 5
   ```

   ```json
   {"operations":["onboarding","improvement","unknown_materials"],"search_provider":"none","neighbours":{"llm":true,"registry":false,"collector_web":false,"collector_telegram":false,"handler_runtime":false,"orchestrator":false,"storage":false},"local_schema_validation":true,"state":"memory"}
   ```

   `local_schema_validation: true` — Assistant знайшов `contracts/schemas` і перевірятиме згенеровані правила й маніфести локально.

## Невідомий матеріал

4. Підготуйте тіла запитів з прикладу матеріалу контракту — сторінки товару «Kettle A-100»:

   ```powershell
   $material = Get-Content contracts/examples/schemas/material/web-product-page.json -Raw | ConvertFrom-Json
   $off = @{ source_id = "shop-example"; forward_unknown_to_llm = $false; material = $material } | ConvertTo-Json -Depth 20
   $on = @{ source_id = "shop-example"; forward_unknown_to_llm = $true; material = $material } | ConvertTo-Json -Depth 20
   ```

5. Надішліть матеріал із вимкненим прапорцем «Передавати в LLM невідомі сторінки». Assistant відмовляє до будь-якого виклику моделі:

   ```powershell
   $r = Invoke-RestMethod -SkipHttpErrorCheck -StatusCodeVariable code -Method Post -Uri http://127.0.0.1:8111/v1/unknown-materials -ContentType application/json -Headers @{ "Idempotency-Key" = "unknown-1" } -Body $off
   $code; $r.code; $r.detail
   ```

   ```text
   403
   access_denied_by_policy
   forward_unknown_to_llm is off: unknown materials are not sent to the LLM
   ```

6. Створіть у LLM gateway псевдоніми `cheap` і `strong`, якими користується Assistant. Без них запити до моделі отримують 404 від шлюзу, а job Assistant завершується `failed` з `upstream_unavailable` і повідомленням `LLM request failed: HTTP 404: not_found`.

   ```powershell
   foreach ($alias in "cheap", "strong") {
     (Invoke-WebRequest -Method Put -Uri "http://127.0.0.1:8110/v1/model-aliases/$alias" -ContentType application/json -Body "{`"alias`": `"$alias`", `"provider_id`": `"fake`", `"model_id`": `"fake-deterministic-1`"}").Content
   }
   ```

   ```text
   {"alias":"cheap","provider_id":"fake","model_id":"fake-deterministic-1"}
   {"alias":"strong","provider_id":"fake","model_id":"fake-deterministic-1"}
   ```

7. Задайте провайдеру `fake` сценарну відповідь для цього матеріалу — так поводилася б справжня модель:

   ```powershell
   $conn = '{"connection_id": "fake-scripts", "kind": "llm_provider", "params": {"provider": "fake", "responses": [{"when_data_contains": "Kettle A-100", "output": {"material_type": "product_page", "confidence": 0.9, "relevant": true, "entity_types": ["product"]}}]}}'
   (Invoke-WebRequest -Method Put -Uri http://127.0.0.1:8110/v1/connections/fake-scripts -ContentType application/json -Body $conn).StatusCode
   (Invoke-WebRequest -Method Put -Uri http://127.0.0.1:8110/v1/providers/fake -ContentType application/json -Body '{"provider_id": "fake", "kind": "fake", "connection_id": "fake-scripts", "enabled": true, "models": [{"model_id": "fake-deterministic-1", "max_context_tokens": 128000, "supports_structured_output": true, "pricing": {"input_per_mtok": 0, "output_per_mtok": 0, "currency": "USD"}}]}').StatusCode
   ```

   ```text
   201
   200
   ```

8. Надішліть матеріал з увімкненим прапорцем. Відповідь — 202 і job; результат — у `GET /v1/jobs/{job_id}`:

   ```powershell
   $job = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8111/v1/unknown-materials -ContentType application/json -Headers @{ "Idempotency-Key" = "unknown-4" } -Body $on
   Start-Sleep 2
   Invoke-RestMethod "http://127.0.0.1:8111/v1/jobs/$($job.job_id)" | ConvertTo-Json -Compress -Depth 5
   ```

   ```json
   {"job_id":"job_cfe2040cfd8b484ca2d31be532ffdb08","kind":"unknown_material","status":"succeeded","created_at":"2026-10-11T10:39:52.011786Z","updated_at":"2026-10-11T10:39:52.157771Z","started_at":"2026-10-11T10:39:52.011786Z","finished_at":"2026-10-11T10:39:52.157771Z","result":{"classification":{"material_type":"product_page","confidence":0.9},"suggestion":{"action":"new_extractor","details":"no extractor handles product_page materials carrying product"}},"idempotency_key":"unknown-4","links":{"self":"/v1/jobs/job_cfe2040cfd8b484ca2d31be532ffdb08","cancel":"/v1/jobs/job_cfe2040cfd8b484ca2d31be532ffdb08/cancel"},"labels":{"source_id":"shop-example"}}
   ```

   Без сценарію (крок 7) `fake` повертає мінімальну відповідь за схемою, і результат — `{"classification":{"material_type":"","confidence":0.0},"suggestion":{"action":"none",…}}`.

## Недоступний сусід

9. Почніть підключення сайту. Колектор не налаштовано, тому job і сесія завершуються `failed`:

   ```powershell
   $job = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8111/v1/onboarding-sessions -ContentType application/json -Headers @{ "Idempotency-Key" = "onboarding-1" } -Body '{"query": "https://shop.example.test/"}'
   Start-Sleep 2
   $s = Invoke-RestMethod "http://127.0.0.1:8111$($job.links.session)"; $s.status; $s.error.code; $s.error.detail
   ```

   ```text
   failed
   upstream_unavailable
   collector is not configured for the assistant
   ```

   Назва замість URL без налаштованого пошукового провайдера дає `failed` з `validation_failed`: `no search provider configured; give an exact URL or @channel`.

## Повний сценарій на фейках сусідів

10. Процесний e2e-тест запускає Assistant окремим процесом (`python -m jane_assistant`) і піднімає фейки LLM gateway, Registry, Web Collector, Handler Runtime, Orchestrator і Storage, що відповідають контрактам, на вільних портах. Сценарій: нове джерело за назвою → варіанти → прийняття з активацією (створюються джерело й завдання) → проблемні приклади → нова версія з ручним погодженням → погодження й активація → відкат.

    ```powershell
    just test assistant -k process_e2e
    ```

    ```text
    collected 140 items / 139 deselected / 1 selected

    services\assistant\tests\test_process_e2e.py .                           [100%]

    ===================== 1 passed, 139 deselected in 10.20s ======================
    ```

    Код сценарію — `services/assistant/tests/test_process_e2e.py`, фейки — `services/assistant/tests/assistant_fakes/`.

## Підключення реального джерела з fake-моделлю

Необов'язковий крок: показує, що з детермінованим `fake` підключення доходить до вибірки, але не набирає впевненості. Потрібні ще два процеси — тестовий сайт і Web Collector — і перезапуск Assistant з адресою колектора та меншою вибіркою:

```powershell
uv run python -m jane_testsite --host 127.0.0.1 --port 8080
```

```powershell
uv run --package jane-web-collector python -m jane_web_collector
```

```powershell
$env:JANE_ASSISTANT_COLLECTOR_WEB_URL = "http://127.0.0.1:8101"
$env:JANE_ASSISTANT_LIMITS__LLM__MAX_ONBOARDING_SAMPLES = "10"
uv run --package jane-assistant python -m jane_assistant
```

Після `POST /v1/onboarding-sessions` з `{"query": "http://127.0.0.1:8080/"}` і очікування близько хвилини сесія (уривок `GET /v1/onboarding-sessions/{session_id}`):

```json
{"status": "insufficient_sample", "query": "http://127.0.0.1:8080/", "selected_candidate_id": "cand_1", "sample": {"materials": 10, "distinct_types": 1, "confidence": 0.0, "sufficient": false, "message": "reached limits.llm.max_onboarding_samples=10 with confidence 0.00"}, "costs": {"amount": 0.0, "currency": "USD"}}
```

Справжня модель розрізняє типи матеріалів, і сесія доходить до `proposals_ready`; з реальною моделлю цей сценарій у документації не перевірявся. Web Collector пише стан у `.jane/web-collector/` — видаліть каталог після перевірки.

## Очікуваний результат

- `capabilities.neighbours.llm` — `true`, решта сусідів — `false`.
- Невідомий матеріал без прапорця — 403 `access_denied_by_policy`; з прапорцем — job `succeeded` з класифікацією й порадою.
- Підключення без колектора — сесія `failed` з `upstream_unavailable`.
- Процесний e2e — `1 passed`.

## Прибирання

Зупиніть процеси через `Ctrl+C`. Обидва сервіси тримали стан у пам'яті й нічого не записали на диск. Змінні середовища PowerShell приберіть:

```powershell
Remove-Item Env:JANE_LLM_STORE, Env:JANE_ASSISTANT_PORT, Env:JANE_ASSISTANT_LLM_URL -ErrorAction SilentlyContinue
Remove-Item Env:JANE_ASSISTANT_COLLECTOR_WEB_URL, Env:JANE_ASSISTANT_LIMITS__LLM__MAX_ONBOARDING_SAMPLES -ErrorAction SilentlyContinue
```

Процесний e2e-тест зупиняє свої процеси й фейки сам.
