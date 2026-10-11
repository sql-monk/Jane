# LLM gateway: швидкий старт

Запуск LLM gateway без бази даних і ключів провайдера: стан у пам'яті процесу, відповіді дає детермінований провайдер `fake`. Результат — запит до моделі зі схемою відповіді, повтор за `Idempotency-Key` і відмова через вичерпаний бюджет.

Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7 і Git Bash), ревізія `48389a3`. На Linux не перевірялися; варіанти Bash виконано в Git Bash на Windows.

## Зміст

- [Передумови](#передумови)
- [Кроки](#кроки)
- [Очікуваний результат](#очікуваний-результат)
- [Прибирання](#прибирання)
- [Що далі](#що-далі)

## Передумови

- uv і Python 3.12 — [середовище розробки](../../development/environment.md).
- Залежності workspace встановлено з кореня репозиторію:

  ```powershell
  uv sync --all-packages
  ```

- Порт `8110` вільний. Інший порт задається змінною `JANE_LLM_PORT`.
- У PowerShell потрібна версія 7: команди нижче використовують `-SkipHttpErrorCheck`.

## Кроки

1. Запустіть сервіс у першому терміналі з кореня репозиторію.

   PowerShell:

   ```powershell
   $env:JANE_LLM_STORE = "memory"
   uv run --package jane-llm python -m jane_llm
   ```

   Bash:

   ```bash
   JANE_LLM_STORE=memory uv run --package jane-llm python -m jane_llm
   ```

   Журнал (уривок; типовий формат — JSON, повідомлення `Uvicorn running on http://127.0.0.1:8110` означає готовність):

   ```text
   store=memory: budgets and usage are per process; use store=postgres for several instances
   {"ts": "2026-10-11T10:28:23.651+00:00", "level": "warning", "logger": "jane.auth", "msg": "auth_mode=none: every caller has every scope - for local tests only", "service": "llm", ...}
   ```

   Попередження `auth_mode=none` означає, що сервіс приймає запити без ключа — лише для локальної роботи.

2. У другому терміналі перевірте стан і псевдоніми моделей.

   PowerShell:

   ```powershell
   (Invoke-WebRequest http://127.0.0.1:8110/v1/health).Content
   (Invoke-WebRequest http://127.0.0.1:8110/v1/model-aliases).Content
   ```

   Bash:

   ```bash
   curl -s http://127.0.0.1:8110/v1/health; echo
   curl -s http://127.0.0.1:8110/v1/model-aliases; echo
   ```

   ```text
   {"status":"ok","checks":{"store":{"status":"ok"}}}
   {"items":[{"alias":"default","provider_id":"fake","model_id":"fake-deterministic-1"}]}
   ```

   Псевдонім `default` і провайдер `fake` створюються під час старту, бо `JANE_LLM_FAKE_PROVIDER_ENABLED` типово `true`.

3. Надішліть запит до моделі зі схемою відповіді. Заголовок `Idempotency-Key` обов'язковий.

   PowerShell:

   ```powershell
   $body = '{"instructions": "Extract the event title.", "data": [{"name": "message", "text": "Concert of the city orchestra on Friday at 19:00"}], "output_schema": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}, "scope": {"purpose": "other", "source_id": "demo"}}'
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8110/v1/completions -ContentType application/json -Headers @{ "Idempotency-Key" = "quickstart-1" } -Body $body).Content
   ```

   Bash:

   ```bash
   BODY='{"instructions": "Extract the event title.", "data": [{"name": "message", "text": "Concert of the city orchestra on Friday at 19:00"}], "output_schema": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}, "scope": {"purpose": "other", "source_id": "demo"}}'
   curl -s -X POST http://127.0.0.1:8110/v1/completions -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-1' -d "$BODY"; echo
   ```

   Відповідь (відформатовано для читання):

   ```json
   {
     "completion_id": "cmp_ffc2d6a6c38c44fdb70f4a1bec357f26",
     "model": {"provider_id": "fake", "model_id": "fake-deterministic-1"},
     "valid": true,
     "validation_errors": [],
     "finish_reason": "stop",
     "usage": {"input_tokens": 262, "output_tokens": 4, "cost": {"amount": 0.0, "currency": "USD"}},
     "budget": [
       {
         "scope_type": "platform",
         "scope_id": "platform",
         "spent": {"amount": 0.0, "currency": "USD"},
         "limit": {"amount": 10.0, "currency": "USD", "period": "day"},
         "exhausted": false,
         "resets_at": "2026-10-12T00:00:00Z"
       }
     ],
     "output": {"title": ""}
   }
   ```

   Провайдер `fake` без сценаріїв повертає мінімальне значення, що відповідає схемі, — тому `title` порожній. Як задати сценарні відповіді — [integration.md](integration.md#сценарні-відповіді-fake).

4. Повторіть той самий запит із тим самим ключем. Шлюз не звертається до провайдера вдруге, а повертає збережену відповідь із заголовком `Idempotency-Replayed`.

   PowerShell:

   ```powershell
   $r = Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8110/v1/completions -ContentType application/json -Headers @{ "Idempotency-Key" = "quickstart-1" } -Body $body
   $r.Headers["Idempotency-Replayed"]; ($r.Content | ConvertFrom-Json).completion_id
   ```

   Bash:

   ```bash
   curl -s -D - -o /dev/null -X POST http://127.0.0.1:8110/v1/completions -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-1' -d "$BODY" | grep -i replayed
   ```

   Вивід PowerShell:

   ```text
   true
   cmp_ffc2d6a6c38c44fdb70f4a1bec357f26
   ```

   Той самий ключ з іншим тілом запиту — 422 `idempotency_key_reused`.

5. Задайте джерелу `demo` нульовий бюджет і повторіть запит від його імені.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Put -Uri http://127.0.0.1:8110/v1/budgets/source/demo -ContentType application/json -Body '{"scope_type": "source", "scope_id": "demo", "budget": {"amount": 0, "currency": "USD", "period": "day"}}').Content
   $r = Invoke-RestMethod -SkipHttpErrorCheck -StatusCodeVariable code -Method Post -Uri http://127.0.0.1:8110/v1/completions -ContentType application/json -Headers @{ "Idempotency-Key" = "quickstart-2" } -Body '{"instructions": "Say hi.", "scope": {"purpose": "other", "source_id": "demo"}}'
   $code; $r.code; $r.detail
   ```

   Bash:

   ```bash
   curl -s -X PUT http://127.0.0.1:8110/v1/budgets/source/demo -H 'Content-Type: application/json' -d '{"scope_type": "source", "scope_id": "demo", "budget": {"amount": 0, "currency": "USD", "period": "day"}}'; echo
   curl -s -X POST http://127.0.0.1:8110/v1/completions -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-2' -d '{"instructions": "Say hi.", "scope": {"purpose": "other", "source_id": "demo"}}'; echo
   ```

   Відповідь на `PUT` — визначення бюджету з поточним станом (`exhausted: true`, бо `amount: 0` не дозволяє жодного виклику):

   ```json
   {"scope_type": "source", "scope_id": "demo", "budget": {"amount": 0.0, "currency": "USD", "period": "day"}, "status": {"scope_type": "source", "scope_id": "demo", "spent": {"amount": 0.0, "currency": "USD"}, "limit": {"amount": 0.0, "currency": "USD", "period": "day"}, "exhausted": true, "resets_at": "2026-10-12T00:00:00Z"}}
   ```

   Вивід PowerShell для відхиленого запиту:

   ```text
   429
   budget_exhausted
   LLM budget of source 'demo' is exhausted (spent 0.000000 + reserved 0.000000 + estimate 0.000000 > 0.0 USD)
   ```

   Повна відповідь (Bash, `application/problem+json`, відформатовано):

   ```json
   {
     "type": "urn:jane:problem:budget_exhausted",
     "title": "LLM budget exhausted",
     "status": 429,
     "detail": "LLM budget of source 'demo' is exhausted (spent 0.000000 + reserved 0.000000 + estimate 0.000000 > 0.0 USD)",
     "instance": "/v1/completions",
     "code": "budget_exhausted",
     "retryable": false,
     "retry_after_seconds": 50547,
     "trace_id": "f5dd4f0c9bdd4dc851232ee6ac1c9ffa",
     "details": {
       "scope_type": "source",
       "scope_id": "demo",
       "period": "day",
       "spent": {"amount": 0.0, "currency": "USD"},
       "limit": {"amount": 0.0, "currency": "USD", "period": "day"},
       "requested_estimate": {"amount": 0.0, "currency": "USD"},
       "period_resets_at": "2026-10-12T00:00:00Z"
     }
   }
   ```

6. Перегляньте облік за рівнями.

   PowerShell:

   ```powershell
   (Invoke-WebRequest "http://127.0.0.1:8110/v1/usage?group_by=scope").Content
   ```

   Bash:

   ```bash
   curl -s "http://127.0.0.1:8110/v1/usage?group_by=scope"; echo
   ```

   ```text
   {"items":[{"requests":1,"input_tokens":262,"output_tokens":4,"cost":{"amount":0.0,"currency":"USD"},"test_mode":false,"scope_type":"source","scope_id":"demo"}],"totals":{"requests":1,"input_tokens":262,"output_tokens":4,"cost":{"amount":0.0,"currency":"USD"}}}
   ```

   Облік містить один запит: повтор за ключем і відхилений запит провайдера не викликали.

## Очікуваний результат

- `GET /v1/health` повертає `"status":"ok"`.
- Запит із `output_schema` повертає `"valid": true` і поле `output`.
- Повтор із тим самим `Idempotency-Key` має `Idempotency-Replayed: true` і той самий `completion_id`.
- Запит від джерела з бюджетом `amount: 0` отримує 429 `budget_exhausted`.

## Прибирання

Зупиніть сервіс через `Ctrl+C`. У режимі `memory` сервіс нічого не записує на диск: конфігурація, бюджети, облік і ключі зникають разом із процесом. Змінну середовища в PowerShell приберіть командою:

```powershell
Remove-Item Env:JANE_LLM_STORE
```

## Що далі

- Виклик LLM-пакета, сценарні відповіді `fake`, підключення Anthropic — [integration.md](integration.md).
- Запуск із PostgreSQL і в Docker — [operations.md](operations.md#запуск-із-postgresql).
- Усі параметри — [configuration.md](configuration.md).
