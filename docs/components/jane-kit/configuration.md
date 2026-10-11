# Jane Kit: налаштування

`JaneSettings` описує процес, `Limits` — модель операційних лімітів. Сервіс-нащадок встановлює власний `env_prefix`.

## Параметри процесу

Для безпосереднього `JaneSettings` префікс змінних — `JANE_`; `__` відділяє вкладені поля. У сервісах Jane він замінений їхнім префіксом.

| Поле | Типове значення | Призначення |
|---|---|---|
| `service_name` | `jane-service` | Назва в журналах та info |
| `instance_id` | host + PID + новий UUID | Ідентичність конкретного запуску |
| `host`, `port` | `127.0.0.1`, `8000` | Адреса Uvicorn |
| `log_level`, `log_format` | `INFO`, `json` | Рівень і формат; формат також `console` |
| `metrics_enabled` | `true` | Маршрут метрик |
| `health_check_timeout_ms` | `2000` | Межа одного health check, мінімум 1 |
| `limits_file` | `null` | JSON/YAML/TOML профіль лімітів |

Зміни settings застосовуються при побудові нового застосунку або перезапуску; автоматичного перечитування середовища немає.

## Автентифікація

| Поле | Типове значення | Поведінка |
|---|---|---|
| `auth_mode` | `none` | `none`, `api_key` або `jwt` |
| `auth_none_allow_remote` | `false` | Віддалений bind у none заборонений |
| `api_keys`, `api_keys_file` | `[]`, `null` | Список ключів та додатковий JSON/YAML файл |
| `jwt_jwks_url`, `jwt_issuer`, `jwt_audience` | `null` | Обов’язкові для jwt |
| `jwt_algorithms` | `["RS256","ES256"]` | Дозволені асиметричні алгоритми |
| `jwt_scope_claim` | `scope` | Claim зі scopes |
| `jwt_leeway_seconds` | `30` | Допуск годинника, 0–600 с |
| `jwt_jwks_cache_ttl_seconds` | `300` | Термін кешу, мінімум 1 с |
| `jwt_jwks_timeout_ms` | `5000` | Тайм-аут завантаження JWKS |
| `jwt_jwks_refresh_cooldown_seconds` | `10` | Пауза між повторними завантаженнями |
| `jwt_jwks_max_bytes` | `1048576` | Максимум JWKS, мінімум 1024 bytes |
| `auth_max_token_bytes` | `16384` | Межа довжини заголовка з токеном |
| `metrics_public` | `true` | Чи відкриті метрики без bearer token |

API key має `name`, `scopes` та рівно одне із `sha256` чи `secret_ref`. Значення секрету не включайте в конфігурацію, що зберігається в Git. `env:` та `file:` підтримуються; `vault:` у цьому build не реалізований. JWKS потребує HTTPS; HTTP допускається для loopback.

## Успадковані ліміти

Порядок: defaults → файл → environment → передані `LimitLayer`. Нижчий шар може перевизначити значення; hard cap може лише звузитися.

```python
from pydantic import Field
from jane_kit.config import Limits, LimitLayer, resolve_limits

class WorkLimits(Limits):
    max_items: int = Field(default=100, ge=1)

resolved = resolve_limits(
    WorkLimits,
    LimitLayer("platform", values={"max_items": 80}, hard_caps={"max_items": 50}),
)
assert resolved.limits.max_items == 50
print(resolved.explain())
```

`on_exceed="error"` замість типового `"clamp"` повертає `LimitError`. Невідомі поля, null та послаблення hard cap теж є помилками. Поля `Limits` незмінні після валідації.

| Модель | Типові ліміти |
|---|---|
| `JobLimits` | 4 активні job; 1000 у черзі; тайм-аут 3600000 ms; retention 86400 с; Retry-After 1 с |
| `IdempotencyLimits` | TTL 86400 с; 10000 in-memory записів |
| `PageLimits` | 50 записів за замовчуванням; максимум 500 |

Точні типи, обмеження та всі члени — у [довіднику](reference/types/README.md).
