# jane-kit: залежності

Що потрібно бібліотеці, з якими версіями вона перевірена і що стається, коли залежність недоступна. Джерела — [libs/jane-kit/pyproject.toml](../../../libs/jane-kit/pyproject.toml) і `uv.lock` ревізії `48389a3`.

## Зміст

- [Середовище](#середовище)
- [Обов'язкові пакети](#обовязкові-пакети)
- [Опційні залежності](#опційні-залежності)
- [Поведінка за недоступності](#поведінка-за-недоступності)
- [Підключення як залежності workspace](#підключення-як-залежності-workspace)

## Середовище

| Залежність | Вимога | Примітка |
|---|---|---|
| Python | `>=3.12` | Код використовує узагальнення `class X[T]` і `asyncio.timeout` |
| ОС | Windows, Linux | `jane_kit.secrets.read_secret_file` має окремі реалізації для POSIX і Windows |

## Обов'язкові пакети

| Пакет | Вимога `pyproject.toml` | Версія в `uv.lock` | Для чого |
|---|---|---|---|
| `fastapi` | `>=0.115` | 0.141.1 | `create_app`, маршрути job, обробники помилок |
| `pydantic` | `>=2.9` | 2.13.5 | Моделі `Limits`, `Job`, `Problem` |
| `pydantic-settings` | `>=2.6` | 2.15.0 | `JaneSettings` зі змінних середовища |
| `prometheus-client` | `>=0.21` | 0.26.0 | `/metrics` |
| `httpx` | `>=0.27` | 0.28.1 | `ServiceClient`, JWKS, завантаження `download_url`, реєстр правил |
| `jsonschema` | `>=4.23` | 4.26.0 | Валідація за JSON Schema 2020-12 контрактів |
| `referencing` | `>=0.35` | 0.37.0 | `$ref` між файлами контрактів |
| `PyYAML` | `>=6.0` | 6.0.3 | OpenAPI-документи, файли лімітів і ключів у YAML |
| `uvicorn` | `>=0.32` | 0.54.0 | `jane_kit.service.run` |
| `pyjwt[crypto]` | `>=2.10` | 2.15.1 | Режим автентифікації `jwt` (RS\*, PS\*, ES\*) |

## Опційні залежності

| Залежність | Як підключити | Хто потребує |
|---|---|---|
| `psycopg[binary,pool]>=3.2` (3.3.6, pool 3.3.3) | `jane-kit[postgres]` | `jane_kit.stores.postgres` — спільні сховища job і ключів у PostgreSQL |
| PostgreSQL | Власна база сервісу | Ті самі сховища; інтеграційні тести бібліотеки — з `postgres:18` dev-стеку |
| SQLite | Стандартний `sqlite3` Python | `jane_kit.stores.sqlite` — файл стану одного вузла |
| `datamodel-code-generator` (0.83.0 у dev-групі workspace) | Встановлений модуль або `uvx` | `jane-codegen models` і `jane-codegen client` без `--no-models` |
| Каталог `contracts/` | Репозиторій або образ (`/app/contracts`) | `jane_kit.schemas`, `jane_kit.rules`, `jane_kit.contracts` |
| JWKS постачальника ідентичності | `jwt_jwks_url` | Режим `auth_mode=jwt` |
| Registry (`registry.v1`) | `registry_url` у `RulesLoader` | Завантаження правил колектора за `rules_ref`, якщо локального пакета немає |

## Поведінка за недоступності

| Що недоступне | Поведінка |
|---|---|
| `psycopg` не встановлено | Імпорт `jane_kit.stores.postgres` падає з `ImportError`; решта бібліотеки працює |
| PostgreSQL під час старту | `PgDatabase.open` чекає з'єднання до `connect_timeout_ms`, потім виняток — сервіс не стартує |
| PostgreSQL під час роботи | Операції сховища кидають винятки `psycopg`; запит закінчується `500 internal_error`, job лишається з попереднім станом. Невдалий heartbeat записується в журнал і повторюється на наступному такті |
| Каталог `contracts/` | `ContractSchemas.locate` кидає `ContractsNotFound` із назвою налаштування — сервіс не стартує |
| JWKS | Відомі ключі з кешу лишаються чинними; без жодного ключа кожен запит отримує `503 service_unavailable` з `Retry-After`; нова спроба завантаження — не частіше `jwt_jwks_refresh_cooldown_seconds` |
| Секрет `env:` / `file:` ключа API | `SecretRefError` під час старту — сервіс не стартує (значення секрету в повідомленні немає) |
| `download_url` або `file://` у `ContentRef` | `502 upstream_unavailable` (мережа, тайм-аут, 5xx — `retryable: true`), `404 not_found` для відсутнього файла |
| Registry для правил | `502 upstream_unavailable` (`retryable: true`) від `RulesLoader`; без `registry_url` і локального пакета — `422 validation_failed` |
| `datamodel-code-generator` і `uvx` | `jane-codegen` з моделями кидає `RuntimeError`; `--no-models` працює без нього |

## Підключення як залежності workspace

Сервіс репозиторію оголошує бібліотеку як залежність workspace — так зроблено в усіх `services/*` і в [шаблоні](../../../templates/service/pyproject.toml):

```toml
[project]
dependencies = [
    "jane-kit",
]

[tool.uv.sources]
jane-kit = { workspace = true }
```

Для сховищ PostgreSQL додайте `"jane-kit[postgres]"`. Після зміни залежностей:

```powershell
uv lock
uv sync --all-packages
```

Поза workspace бібліотеку підключають шляхом до каталогу, як у [швидкому старті](quickstart.md): `uv run --no-project --with ./libs/jane-kit ...`. На PyPI пакет не публікується.
