# Jane Kit: швидкий старт

Створіть мінімальний локальний сервіс із журналами, health endpoint і метриками.

## Передумови

Python 3.12+, uv і checkout Jane. Команди виконуються в корені репозиторію. Для наведеного прикладу достатньо Python-процесу; зовнішні сервіси не потрібні.

```powershell
uv sync --package jane-kit
```

Збережіть наступний код у `demo_service.py` в корені checkout.

```python
from jane_kit.config import JaneSettings
from jane_kit.service import create_app, run

settings = JaneSettings(service_name="demo-service", port=8190)
app = create_app(settings, auth_scopes={"GET /hello": ()})

@app.get("/hello")
def hello():
    return {"message": "Jane"}

if __name__ == "__main__":
    run(app, settings)
```

## Запуск

```powershell
uv run --package jane-kit python demo_service.py
```

Сервіс слухає `127.0.0.1:8190`. У другому терміналі:

```powershell
uv run --package jane-kit python -c "import httpx; r=httpx.get('http://127.0.0.1:8190/hello'); r.raise_for_status(); print(r.json())"
```

Очікуване JSON-тіло:

```json
{"message": "Jane"}
```

Перевірте також `GET /v1/health`, `GET /v1/info` та `GET /metrics`. Зупинка — Ctrl+C.

## Далі

У локальному прикладі `auth_mode=none`; його типовий режим дозволяє слухати лише loopback. Для доступу інших машин налаштуйте [API keys або JWT](configuration.md#автентифікація), задайте scopes маршрутів і додайте [власні health checks](reference/types/README.md).
