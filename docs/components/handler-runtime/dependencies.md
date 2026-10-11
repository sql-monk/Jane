# Залежності Handler Runtime

Локальний пакет потребує середовища Runtime, схем і пісочниці. Orchestrator та Registry опційні.

| Залежність | Коли потрібна | Недоступність |
|---|---|---|
| Python ≥3.12, Jane Kit, SDK та [pyproject](../../../services/handler-runtime/pyproject.toml) | Завжди | Старт/імпорт не працює |
| Docker API і image | Docker backend, типовий | 503 до виконання або image startup error |
| contracts JSON Schema | Package/input/output validation | Побудова не працює |
| Registry v1 | Коли немає local/package_archive | Upstream problem |
| Доступний ContentRef | Blob-вхід/archive | Відхилення digest, host, path або size |
| Власна PostgreSQL | state_dsn, shared state | Health/state/збереження відповіді не працюють |

Точні Python-залежності фіксує [uv.lock](../../../uv.lock). У sandbox доступні лише бібліотеки [python-extractor@1](../../../services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json); pip-вимоги пакета звіряються з ним.

## Ізоляція

Docker sandbox має вимкнену мережу, непривілейованого користувача, read-only root filesystem і tmpfs. CPU, memory, wall time, процеси та output обмежені. Сумісний Docker/Podman endpoint має виконувати Docker API; OCI runtime задає docker_runtime.

Subprocess backend вимагає allow_unsafe_subprocess=true та не дає контейнерної ізоляції. Він призначений лише для довіреного локального коду; його тест не підтверджує Docker-гарантії.

## Заміна залежностей

Інший Registry має підтримувати exact version ZIP, digest/ETag та v1 errors; альтернативою є локальний ZIP/package_archive. SandboxBackend реалізує run/kill/ping і SandboxOutcome, але adapter окремо перевіряється на реальну ізоляцію.

Runtime зберігає own job/results/keys. Connections повертає порожній список, PUT не підтримує; він не є Storage/LLM executor зі секретами й не читає таблиці Orchestrator.
