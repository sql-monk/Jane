# Storage: швидкий старт

Запустіть один процес із filesystem-адаптером і запишіть одну сутність. Orchestrator, Registry та Docker для цього прикладу не потрібні.

## Передумови

Потрібні Python версії [.python-version](../../../.python-version), uv і каталог з правом запису. Всі команди виконуйте з кореня checkout на Windows або Linux.

```powershell
uv sync --all-packages
```

## Налаштування

Збережіть `storage-connections.local.json` у корені. `base_path` — відносний шлях від робочої директорії процесу; для сервісної установки виберіть абсолютний шлях.

```json
{"connections": [{"connection_id": "docs-files", "kind": "filesystem", "params": {"base_path": ".jane/storage-demo"}}]}
```

Збережіть `.env.storage.local`:

```ini
JANE_STORAGE_HOST=127.0.0.1
JANE_STORAGE_PORT=8107
JANE_STORAGE_AUTH_MODE=none
JANE_STORAGE_CONNECTIONS_FILE=storage-connections.local.json
```

## Запуск

```powershell
uv run --all-packages --env-file .env.storage.local python -m jane_storage
```

Процес слухає `127.0.0.1:8107`. У другому терміналі:

```powershell
curl http://127.0.0.1:8107/v1/health
curl http://127.0.0.1:8107/v1/info
```

Health має `status: ok`; capabilities містять `filesystem` і пакет із `package_id=jane.storage-files`, `version=1.0.0`. `auth_mode=none` призначений для локального loopback; віддалений доступ налаштовуйте за [конфігурацією](configuration.md#автентифікація).

## Перший запис

Виконайте Python-приклад у другому терміналі, зберігши його як `storage-client.local.py`:

```python
import json
from urllib.request import Request, urlopen

base = "http://127.0.0.1:8107"
entity = {
    "entity_type": "product",
    "key": {"scope": "docs-demo", "natural": {"sku": "A-100"}},
    "fields": {"sku": "A-100", "price": 1299},
    "observation": {
        "observation_id": "obs_docs_1",
        "observed_at": "2026-10-11T10:00:00Z",
    },
}
body = {
    "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
    "inputs": [{"kind": "entities", "entities": [entity]}],
    "connections": {"target": "docs-files"},
    "delivery": {"delivery_key": "docs-storage-1"},
}
request = Request(
    base + "/v1/invocations",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "Idempotency-Key": "docs-storage-1"},
)
with urlopen(request, timeout=35) as response:
    result = json.load(response)
    print(result["status"], result["output"]["writes"][0]["status"])
with urlopen(base + "/v1/entities?connection_id=docs-files&entity_type=product") as response:
    print(json.load(response)["items"])

```

```powershell
uv run python storage-client.local.py
```

Перший виклик друкує `success written` та одну сутність зі станом `price=1299`. Повтор із тим самим тілом і ключем дає `duplicate`; після перезапуску HTTP-кеш утрачається, але адаптер зберігає дедуплікацію доставки. Нове спостереження потребує нових `observation_id`, `delivery_key` і `Idempotency-Key`.

## Зупинка

Натисніть Ctrl+C у терміналі сервісу. Каталог `.jane/storage-demo` залишається; видаляйте його лише якщо ці тестові дані більше не потрібні. [Діагностика](operations.md#типові-проблеми), [інші адаптери](dependencies.md#адаптери).
