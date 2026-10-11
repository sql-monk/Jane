# jane-kit: швидкий старт

Створює мінімальний сервіс на `jane-kit` у тимчасовому каталозі поза репозиторієм, запускає його й перевіряє стандартні ресурси, ліміт, помилку Problem і автентифікацію за API-ключем. Кроки виконано 2026-10-11 на Windows 11 (PowerShell і Git Bash), ревізія `48389a3`; на Linux не перевірялися.

## Передумови

- `uv` 0.12 або новіший; Python 3.12 uv знаходить або завантажує сам.
- Робочий каталог — корінь репозиторію Jane: бібліотеку встановлює `uv` із `libs/jane-kit`.
- Вільний порт `18820` на `127.0.0.1`.

## Кроки

1. Створіть каталог і файл сервісу.

   PowerShell:

   ```powershell
   New-Item -ItemType Directory -Force "$env:TEMP/jane-hello"
   ```

   Bash:

   ```bash
   mkdir -p /tmp/jane-hello
   ```

   Збережіть у цьому каталозі файл `hello.py`:

   ```python
   """Minimal Jane service on jane-kit."""

   from pydantic import Field
   from pydantic_settings import SettingsConfigDict

   from jane_kit.config import JaneSettings, Limits, resolve_limits
   from jane_kit.errors import LimitExceeded
   from jane_kit.service import create_app, run


   class Settings(JaneSettings):
       model_config = SettingsConfigDict(env_prefix="HELLO_", extra="ignore", env_nested_delimiter="__")

       service_name: str = "hello"
       port: int = 18820


   class HelloLimits(Limits):
       max_name_length: int = Field(default=32, ge=1)


   settings = Settings()
   limits = resolve_limits(HelloLimits, *settings.platform_layers("HELLO_LIMITS__"))
   app = create_app(settings, limits=limits, auth_scopes={"GET /v1/hello/{name}": "hello:read"})


   @app.get("/v1/hello/{name}")
   async def hello(name: str) -> dict[str, str]:
       if len(name) > limits.limits.max_name_length:
           raise LimitExceeded(
               "name is too long",
               details={"path": "max_name_length", "limit": limits.limits.max_name_length},
           )
       return {"greeting": f"Hello, {name}!"}


   if __name__ == "__main__":
       run(app, settings)
   ```

   Що тут відбувається: `Settings` читає змінні середовища з префіксом `HELLO_`; `HelloLimits` оголошує ліміт із безпечним типовим значенням; `create_app` додає `/v1/health`, `/v1/info`, `/metrics`, журнали, обробку помилок і перевірку scopes за таблицею `auth_scopes`.

2. Запустіть сервіс із кореня репозиторію. `uv` створює тимчасове середовище з `jane-kit` і його залежностями.

   PowerShell:

   ```powershell
   uv run --no-project --with ./libs/jane-kit python "$env:TEMP/jane-hello/hello.py"
   ```

   Bash:

   ```bash
   uv run --no-project --with ./libs/jane-kit python /tmp/jane-hello/hello.py
   ```

   У журналі (JSON-рядки) з'являються попередження про режим `none` і адреса. Уривок:

   ```text
   {"ts": "2026-10-11T09:59:48.933+00:00", "level": "warning", "logger": "jane.auth", "msg": "auth_mode=none: every caller has every scope - for local tests only", "service": "hello", ...}
   {"ts": "2026-10-11T09:59:48.936+00:00", "level": "info", "logger": "uvicorn.error", "msg": "Uvicorn running on http://127.0.0.1:18820 (Press CTRL+C to quit)", "service": "hello", ...}
   ```

3. У другому терміналі викличте сервіс.

   PowerShell:

   ```powershell
   (Invoke-WebRequest http://127.0.0.1:18820/v1/health).Content
   (Invoke-WebRequest http://127.0.0.1:18820/v1/hello/Jane).Content
   (Invoke-WebRequest http://127.0.0.1:18820/v1/info).Content
   ```

   Bash:

   ```bash
   curl -s http://127.0.0.1:18820/v1/health
   curl -s http://127.0.0.1:18820/v1/hello/Jane
   curl -s http://127.0.0.1:18820/v1/info
   ```

   Очікуваний результат:

   ```text
   {"status":"ok","checks":{}}
   {"greeting":"Hello, Jane!"}
   {"service":"hello","version":"0.1.0","api_versions":["v1"],"capabilities":{},"auth_mode":"none","limits":{"defaults":{}}}
   ```

   `limits.defaults` порожній, бо `max_name_length` немає в `limits.schema.json`: `/v1/info` показує лише ліміти контракту ([конфігурація](configuration.md#ліміти-в-v1info)).

4. Перевищте ліміт — ім'я довше за 32 символи:

   ```bash
   curl -s http://127.0.0.1:18820/v1/hello/abcdefghijklmnopqrstuvwxyzabcdefghij
   ```

   Відповідь `422` з `Content-Type: application/problem+json`:

   ```json
   {
     "type": "urn:jane:problem:limit_exceeded",
     "title": "Limit exceeded",
     "status": 422,
     "detail": "name is too long",
     "instance": "/v1/hello/abcdefghijklmnopqrstuvwxyzabcdefghij",
     "code": "limit_exceeded",
     "retryable": false,
     "trace_id": "14f6a6d82bff4b25c0dce737010b72cd",
     "details": {"path": "max_name_length", "limit": 32}
   }
   ```

   У PowerShell `Invoke-WebRequest` для `4xx` кидає виняток; тіло відповіді — у `$_.ErrorDetails.Message` блоку `catch`.

5. Зупиніть сервіс (`Ctrl+C`) і запустіть його з автентифікацією за API-ключем та зменшеним лімітом. Ключ `demo-reader-key` — тестове значення лише для цього прикладу; сервіс зберігає тільки його SHA-256.

   PowerShell:

   ```powershell
   $env:HELLO_AUTH_MODE = "api_key"
   $env:HELLO_DEMO_KEY = "demo-reader-key"
   $env:HELLO_API_KEYS = '[{"name": "reader", "scopes": ["hello:read"], "secret_ref": "env:HELLO_DEMO_KEY"}]'
   $env:HELLO_LIMITS__MAX_NAME_LENGTH = "4"
   uv run --no-project --with ./libs/jane-kit python "$env:TEMP/jane-hello/hello.py"
   ```

   Bash:

   ```bash
   HELLO_AUTH_MODE=api_key HELLO_DEMO_KEY=demo-reader-key \
   HELLO_API_KEYS='[{"name": "reader", "scopes": ["hello:read"], "secret_ref": "env:HELLO_DEMO_KEY"}]' \
   HELLO_LIMITS__MAX_NAME_LENGTH=4 \
   uv run --no-project --with ./libs/jane-kit python /tmp/jane-hello/hello.py
   ```

   У журналі старту — `"msg": "authentication enabled", ..., "auth_mode": "api_key", "api_keys": ["reader"]`.

6. Перевірте відповіді (Bash; `HELLO_DEMO_KEY=demo-reader-key` — той самий демонстраційний ключ, що й у кроці 5):

   ```bash
   curl -s http://127.0.0.1:18820/v1/hello/Jane
   curl -s -H "Authorization: Bearer $HELLO_DEMO_KEY" http://127.0.0.1:18820/v1/hello/Jane
   curl -s -H "Authorization: Bearer $HELLO_DEMO_KEY" http://127.0.0.1:18820/v1/hello/Janet
   curl -s http://127.0.0.1:18820/v1/health
   ```

   PowerShell-еквівалент запиту з ключем:

   ```powershell
   (Invoke-WebRequest http://127.0.0.1:18820/v1/hello/Jane -Headers @{Authorization = "Bearer demo-reader-key"}).Content
   ```

   Очікуваний результат (тіла Problem скорочено до `status` і `code`):

   | Запит | Відповідь |
   |---|---|
   | без ключа | `401`, `unauthenticated`, `detail`: `bearer token required` |
   | з ключем, ім'я `Jane` | `200`, `{"greeting":"Hello, Jane!"}` |
   | з ключем, ім'я `Janet` | `422`, `limit_exceeded`, `details.limit`: `4` (ліміт зі змінної середовища) |
   | `/v1/health` без ключа | `200`, `{"status":"ok","checks":{}}` — health завжди відкритий |

   Ключ без scope `hello:read` отримує `403` з кодом `forbidden` і `details.required_scopes`: `["hello:read"]` (перевірено з другим ключем `["hello:other"]`).

## Прибирання

Зупиніть сервіс (`Ctrl+C`). Команди нижче видаляють тимчасовий каталог із `hello.py` і змінні середовища поточної сесії PowerShell; тимчасове середовище `uv` лишається в кеші `uv` і нічого не змінює в репозиторії.

PowerShell:

```powershell
Remove-Item -Recurse -Force "$env:TEMP/jane-hello"
Remove-Item Env:HELLO_AUTH_MODE, Env:HELLO_DEMO_KEY, Env:HELLO_API_KEYS, Env:HELLO_LIMITS__MAX_NAME_LENGTH
```

Bash:

```bash
rm -rf /tmp/jane-hello
```

## Далі

- Сервіс у репозиторії з Dockerfile, тестами й job — [створення сервісу](../../development/new-service.md).
- Усі параметри `JaneSettings`, режими автентифікації й ліміти — [конфігурація](configuration.md).
- Job, ідемпотентність, пагінація, клієнти — [інтеграція](integration.md).
