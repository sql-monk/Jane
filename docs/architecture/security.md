# Безпека

Як Jane автентифікує викликачів, зберігає секрети, ізолює код екстракторів і обмежує мережеві звернення. Спільний код — [libs/jane-kit](../../libs/jane-kit/src/jane_kit/) (`auth.py`, `auth_scopes.py`, `secrets.py`, `content.py`); параметри окремого сервісу — `configuration.md` модуля з [каталогу](../components/README.md).

## Зміст

- [Автентифікація](#автентифікація)
- [Дозволи операцій](#дозволи-операцій)
- [Ключі між сервісами](#ключі-між-сервісами)
- [Секрети й підключення](#секрети-й-підключення)
- [Ізоляція коду екстракторів](#ізоляція-коду-екстракторів)
- [Мережеві межі](#мережеві-межі)
- [Proxy і Admin UI](#proxy-і-admin-ui)

## Автентифікація

Кожен сервіс перевіряє заголовок `Authorization: Bearer <токен>` сам; спільного шлюзу автентифікації немає. Режим задає змінна `JANE_<СЕРВІС>_AUTH_MODE`.

| Режим | Поведінка |
|---|---|
| `none` | типове значення в коді: кожен викликач має всі дозволи. Сервіс відмовляється стартувати на не-loopback адресі без `AUTH_NONE_ALLOW_REMOTE=true` і пише попередження в журнал |
| `api_key` | ключі з `JANE_<СЕРВІС>_API_KEYS` (JSON) або файла `API_KEYS_FILE`; запис ключа — `name`, `scopes` і `sha256` ключа або посилання `secret_ref`. Сервіс зберігає лише SHA-256 і порівнює в постійному часі. Режим dev-стеку |
| `jwt` | ключі з JWKS за `https`-адресою, обов'язкові `iss`, `aud`, `exp`; лише алгоритми RS, PS, ES. Дозволи — з claim `scope`. Не перевірено з реальним постачальником ідентичності |

- **Відмова за неповної конфігурації.** Без ключів, JWKS або з нерозв'язним посиланням сервіс не стартує.
- **Помилки:** `401 unauthenticated` із заголовком `WWW-Authenticate: Bearer`, `403 forbidden`.
- **Відкриті точки:** `GET /v1/health` — без токена; `GET /metrics` — без токена, поки `metrics_public=true` (типово). `GET /v1/info` і опис OpenAPI потребують будь-якого дійсного токена. Операція без запису в таблиці дозволів — заборонена.

## Дозволи операцій

Дозвіл має вигляд `<сервіс>:<дія>`; таблиці дозволів кожного API — [auth_scopes.py](../../libs/jane-kit/src/jane_kit/auth_scopes.py) і розділ «Scopes операцій» [contracts/README.md](../../contracts/README.md).

| API | Дозволи |
|---|---|
| `collector.v1` | `collector:run`, `collector:read`, `connections:write` |
| `handler.v1` | `handler:invoke`, `handler:test`, `connections:write` |
| `storage.v1` | `storage:read` (разом із дозволами `handler.v1`) |
| `llm.v1` | `llm:invoke`, `llm:admin` (разом із дозволами `handler.v1`) |
| `registry.v1` | `registry:read`, `registry:write`, `registry:approve` |
| `orchestrator.v1` | `orchestrator:read`, `orchestrator:write`, `orchestrator:admin` (`admin` включає читання й запис; підключення та ліміти платформи потребують `admin`) |
| `assistant.v1` | `assistant:use` |

Registry додатково розрізняє автора версії: запис ключа може мати `actor` (`human`, `llm`, `import`). Ключ з `actor: llm` (у dev-стеку — ключ Assistant) публікує лише версії з `created_by: llm`.

У dev-стеку `just up` генерує окремий ключ для кожної ідентичності — `admin`, `orchestrator`, `assistant`, `registry`, `handler-runtime`, `storage`, `llm`, `web-collector`, `telegram-collector` — і передає сервісам лише їхні SHA-256 ([infra/compose.yaml](../../infra/compose.yaml)). Ключ `admin` має всі дозволи; ним користуються Admin UI і приклади.

## Ключі між сервісами

Власний токен сервіс отримує зі свого середовища й надсилає сусідові в `Authorization: Bearer`.

| Сервіс | Налаштування вихідного токена |
|---|---|
| Orchestrator | `JANE_ORCHESTRATOR_SERVICE_TOKEN_REF` (`env:…`), окремий `token_ref` виконавця має пріоритет |
| Assistant | `JANE_ASSISTANT_SERVICE_TOKEN_REF` і `*_TOKEN_REF` сусідів |
| Storage, Handler Runtime, LLM gateway | `JANE_<СЕРВІС>_REGISTRY_TOKEN` — токен для Registry |
| Web Collector, Telegram Collector | `JANE_<СЕРВІС>_REGISTRY_TOKEN_ENV` — назва змінної з токеном для Registry |
| Registry | `JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF` — для читання `/v1/info` Handler Runtime |

Токени зберігаються як `SecretStr`: вони не потрапляють у журнали, `repr` і відповіді API.

## Секрети й підключення

Підключення ([connection.schema.json](../../contracts/schemas/common/connection.schema.json)) містить несекретні `params` і `secret_refs` — посилання на секрети. Значення секрету через API не проходить, у пакетах не зберігається й під час форкування не копіюється; його розв'язує виконавець у власному середовищі.

| Посилання | Правило розв'язання |
|---|---|
| `env:<змінна>` | лише змінні з префіксом `JANE_SECRET_` |
| `file:<шлях>` | лише файли строго всередині `/run/secrets`; символьні посилання й `..` не виводять за межі каталогу |
| `vault:…` | дозволено схемою, але відхиляється реалізацією |

Порушення правила — помилка `secret_ref_not_allowed` (`422`) під час створення підключення. Перевірка підключення повертає лише ознаки, чи розв'язано секрети, без значень.

- **Orchestrator** зберігає лише `secret_refs` і поширює підключення виконавцям (`PUT /v1/connections/{id}`).
- **LLM gateway** читає ключі провайдерів із файлів у `/run/secrets`; у dev-стеку туди змонтовано `.jane/secrets` лише для читання. Ключі вставляє людина; у документації й прикладах вони не використовуються.
- **Storage** дозволяє мережеві підключення лише до хостів зі списку `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` (типово порожній).

## Ізоляція коду екстракторів

Handler Runtime виконує кожен виклик екстрактора в окремому контейнері Docker або Podman ([docker_sandbox.py](../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py)).

| Обмеження | Як забезпечено |
|---|---|
| Мережа | `network_mode=none`; пакет, що вимагає `access.network` інше, ніж `none`, відхиляється |
| Файлова система | коренева ФС лише для читання; `/tmp` — tmpfs з `noexec`; код пакета копіюється в анонімний том лише для читання; томи хоста не монтуються |
| Привілеї | `cap_drop=ALL`, `no-new-privileges`, користувач `65534:65534`, типовий seccomp |
| Ресурси | `sandbox.cpu_cores` (1.0), `sandbox.memory_mb` (512, без swap), `sandbox.max_processes` (16), `sandbox.tmpfs_mb` (64) |
| Час і вивід | `sandbox.wall_time_ms` (30 000), `sandbox.max_output_bytes` (4 МіБ) |
| Середовище | лише змінні `HOME` і `PYTHON*`; секретів у контейнері немає |

У дужках — типові значення; верхні межі сервісу й профілів лімітів — налаштування [Handler Runtime](../components/handler-runtime/README.md). Режим `subprocess` без ізоляції вмикається лише явним `JANE_HANDLER_RUNTIME_ALLOW_UNSAFE_SUBPROCESS=true`.

Межа довіри: у dev-стеку контейнер Handler Runtime отримує сокет Docker хоста, щоб створювати пісочниці, тобто сам процес Handler Runtime може керувати контейнерами хоста. Тести ізоляції запускаються лише на Linux (`just isolation`).

## Мережеві межі

- **Читання вмісту за посиланням.** Handler Runtime і LLM gateway читають `file://` лише в каталогах `BLOB_ROOTS` (типово порожньо — відмова) і завантажують HTTP лише з хостів `DOWNLOAD_HOST_ALLOWLIST`; редиректи не виконуються.
- **Web Collector** не звертається до link-local адрес (`deny_link_local`) і надсилає облікові дані підключень лише на дозволені origin (`connection_origin_allowlist`, типово жодного); поважає `robots.txt`, якщо правила не задають іншої політики для контрольованого користувачем ресурсу.
- **LLM gateway** звертається лише до адрес провайдерів зі списку `PROVIDER_API_BASE_ALLOWLIST` (типово `https://api.anthropic.com`). Вміст сторінок і повідомлень передається моделі як дані, а не як інструкції.
- **Dev-стек** публікує порти лише на `127.0.0.1` (`JANE_BIND`).

## Proxy і Admin UI

Proxy dev-стеку (Caddy, [infra/proxy/Caddyfile](../../infra/proxy/Caddyfile)) віддає Admin UI і передає `/api/<сервіс>/…` відповідному сервісу без префікса; інші шляхи `/api/` — `404`. Відповіді мають заголовки `Content-Security-Policy` (`default-src 'self'`, `frame-ancestors 'none'`, `object-src 'none'`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`. Proxy не перевіряє ключі — це робить кожен сервіс. Admin UI зберігає ключ лише в сесії вкладки браузера.
