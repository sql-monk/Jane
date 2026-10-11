# LLM: швидкий старт

Отримайте структуровану відповідь від детермінованого fake-провайдера одним процесом, без PostgreSQL, Registry та зовнішніх API.

## Передумови

Python версії [.python-version](../../../.python-version), uv; команди з кореня checkout однакові на Windows і Linux.

```powershell
uv sync --all-packages
```

## Налаштування

Збережіть `.env.llm.local`:

```ini
JANE_LLM_HOST=127.0.0.1
JANE_LLM_PORT=8110
JANE_LLM_AUTH_MODE=none
JANE_LLM_STORE=memory
JANE_LLM_FAKE_PROVIDER_ENABLED=true
```

## Запуск

```powershell
uv run --all-packages --env-file .env.llm.local python -m jane_llm
```

У другому терміналі перевірте `GET /v1/health` і `GET /v1/model-aliases`:

```powershell
curl http://127.0.0.1:8110/v1/health
curl http://127.0.0.1:8110/v1/model-aliases
```

Health має `status: ok`, а псевдонім `default` посилається на `fake-deterministic-1` провайдера `fake`.

## Перша відповідь

Збережіть `llm-client.local.py` і виконайте `uv run python llm-client.local.py`:

```python
import json
from urllib.request import Request, urlopen

body = {
    "model": "default",
    "instructions": "Return a JSON object matching the schema.",
    "data": [{"name": "sample", "text": "hello"}],
    "output_schema": {
        "type": "object",
        "required": ["ok"],
        "properties": {"ok": {"type": "boolean"}},
    },
    "scope": {"purpose": "other"},
    "mode": "sync",
}
request = Request(
    "http://127.0.0.1:8110/v1/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "Idempotency-Key": "docs-llm-1"},
)
with urlopen(request, timeout=130) as response:
    print(json.load(response))

```

У перевіреному локальному сценарії HTTP 200 містив `output: {"ok": false}`, модель `fake-deterministic-1`, облік токенів та нульову вартість. Це найменше значення, яке fake побудував за схемою; воно не підтверджує якість реальної моделі. Точний контракт — [createCompletion](reference/api/generated/createCompletion.md).

## Зупинка й постійний стан

Ctrl+C зупиняє процес; memory-стан бюджету, usage, jobs і ключів утрачається. Для постійного стану встановіть `JANE_LLM_STORE=postgres` та `JANE_LLM_DATABASE_URL`; [конфігурація](configuration.md#постійний-стан) пояснює власну схему, а [експлуатація](operations.md) — резервування. Зовнішній Anthropic у цьому прикладі не перевірено.
