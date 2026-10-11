# Assistant: швидкий старт

Запустіть сервіс окремо й перевірте health, capabilities та явну помилку відсутньої залежності. Для завершеного onboarding підключіть сусідів, перелічених у [залежностях](dependencies.md).

## Передумови

Python версії [.python-version](../../../.python-version), uv; команди з кореня checkout працюють на Windows і Linux.

```powershell
uv sync --all-packages
```

## Налаштування та запуск

Збережіть `.env.assistant.local`:

```ini
JANE_ASSISTANT_HOST=127.0.0.1
JANE_ASSISTANT_PORT=8000
JANE_ASSISTANT_AUTH_MODE=none
```

```powershell
uv run --all-packages --env-file .env.assistant.local python -m jane_assistant
```

У другому терміналі:

```powershell
curl http://127.0.0.1:8000/v1/health
curl http://127.0.0.1:8000/v1/info
```

Очікуйте `status: ok`, `capabilities.state: memory`, `operations` із onboarding/improvement/unknown_materials та `false` для неналаштованих сусідів. Порт за замовчуванням успадковано з Jane Kit: `8000`.

## Прямий виклик

Збережіть `assistant-client.local.py` й виконайте `uv run python assistant-client.local.py`:

```python
import json
import time
from urllib.request import Request, urlopen

base = "http://127.0.0.1:8000"
request = Request(
    base + "/v1/onboarding-sessions",
    data=json.dumps({"query": "https://example.test", "source_kind": "web", "auto_activation": False}).encode(),
    headers={"Content-Type": "application/json", "Idempotency-Key": "docs-assistant-1"},
)
with urlopen(request) as response:
    job = json.load(response)
    print(response.status, job["job_id"])
for attempt in range(30):
    with urlopen(base + "/v1/jobs/" + job["job_id"]) as response:
        job = json.load(response)
    if job["status"] in {"succeeded", "failed", "cancelled"}:
        print(job["status"], job.get("error"), job.get("result"))
        break
    time.sleep(min(1 + attempt, 5))
else:
    raise TimeoutError("Job is still running; continue polling its Location")

```

Сервіс приймає запит із HTTP 202. Без Web Collector job завершується `failed` із `error.code: upstream_unavailable`; цей результат підтверджує межу автономності, а не завершений onboarding. Для робочого сценарію налаштуйте `JANE_ASSISTANT_COLLECTOR_WEB_URL`, `LLM_URL`, `REGISTRY_URL`, `HANDLER_RUNTIME_URL` та токени за [інтеграцією](integration.md#мінімальний-onboarding).

## Зупинка

Ctrl+C закриває процес і сусідні HTTP-клієнти. Без `state_dsn` jobs та сесії втрачаються. [Постійний стан](configuration.md#постійний-стан) потрібний для відновлення після рестарту та кількох екземплярів. Реальні зовнішні LLM/Telegram тут не перевірено.
