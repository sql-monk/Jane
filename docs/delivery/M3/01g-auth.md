# WP-01g. Автентифікація й scopes у всіх сервісах (B2, фінальне рев'ю M3)

**Гілка:** `wp/01g2-service-auth` (перебазована; попередня `wp/01g-service-auth` на `0a5b56b` лишилась без змін, без
force push) · **База:** `origin/codex/jane-integration` `3ec9358` (послідовно `3c98542` → `03a31fa` → `f1c78e9` →
`3ec9358`) · **Доручення:** наскрізне, координатор за фінальним рев'ю M3 (без `.jane-wp`) · **Стан:** review

## Результат

Блокер M3 B2 закрито: ADR-0005 реалізовано одним модулем jane-kit, і **кожен із 8 сервісів сам перевіряє токен
і scope кожної операції**; усі стеки (dev, e2e, профілі, приклади) працюють у `api_key` з ключами, які
генеруються локально і в git не потрапляють; сервіси викликають сусідів власними токенами.

| Фаза | Що зроблено | Де |
|---|---|---|
| 1. jane-kit | Режими `none`/`api_key`/`jwt`; ключі зберігаються хешем (`sha256`) або задаються `secret_ref` (`env:`/`file:`, розв'язується один раз на старті й одразу хешується); scopes на ключ; JWT лише RS*/PS*/ES* за JWKS (кеш з TTL, тайм-аут, невідомий `kid` → одне оновлення з cooldown), `iss`/`aud`/`exp` обов'язкові, `nbf`, відмова `alg=none`/`HS*`, ключ і алгоритм заголовка мусять збігатися; 401 `unauthenticated` / 403 `forbidden` у `problem+json`; fail-closed на неповну конфігурацію; `none` — попередження й лише loopback. Одна точка підключення — `create_app(..., auth_scopes=...)`: middleware автентифікує, залежність застосунку авторизує маршрут; маршрут без рядка в таблиці — 403, а на старті — відмова стартувати | [`auth.py`](../../../libs/jane-kit/src/jane_kit/auth.py), [`auth_scopes.py`](../../../libs/jane-kit/src/jane_kit/auth_scopes.py), [`service.py`](../../../libs/jane-kit/src/jane_kit/service.py), [`config.py`](../../../libs/jane-kit/src/jane_kit/config.py) (`JaneSettings` успадковує `AuthSettings`) |
| 2. 8 сервісів | Таблиці scopes на кожну операцію кожного контракту; тест звіряє таблиці з `contracts/openapi/*.v1.yaml` (рівність множин операцій). storage, handler-runtime, llm, обидва колектори, assistant — один рядок у `create_app`. orchestrator і registry переведено на спільний модуль (тепер працює й `jwt`); їхні обробники лишили власні перевірки (ім'я принципала для аудиту, `actor` registry), наявні тести зелені | `services/*/src/*/app.py`, `services/orchestrator/src/jane_orchestrator/auth.py`, `services/registry/src/jane_registry/auth.py` |
| 3. Вихідні виклики | orchestrator → виконавці: `token_ref` виконавця або власний `SERVICE_TOKEN_REF` (відкритий `token` ще приймається з попередженням); assistant → кожен сусід: `SERVICE_TOKEN_REF` + окремий `*_TOKEN_REF` на сусіда (старий `SERVICE_TOKEN_ENV` лишився як застарілий); registry → runtime (`GET /v1/info` профілів): `RUNTIME_PROFILES_TOKEN_REF`; llm → registry: токен тепер `SecretStr`; runtime/storage/колектори → registry вже мали налаштування токена — підключено в стеках. Нерозв'язне посилання — сервіс не стартує | `settings.py`/`clients.py`/`profiles.py` відповідних сервісів |
| 4. Стеки | `infra/compose.yaml`: усі 8 застосунків у `api_key`; ключі — лише як `${JANE_API_KEY_<ID>_SHA256}` з scopes кожного клієнта, власні токени — `${JANE_API_KEY_<ID>}` у середовищі того, хто викликає. `just up` генерує ключі 9 ідентичностей у `.jane/stack-<project>.json` (як паролі PostgreSQL), `just env` показує `JANE_STACK_AUTH_ADMIN_API_KEY`. e2e (`E2EStack`), профілі (`stack.py`) і приклади генерують ті самі змінні; клієнти harness (`JaneClient`, `Api` прикладів, limits harness, CLI публікації пакетів storage) надсилають ключ оператора стеку | [`infra/compose.yaml`](../../../infra/compose.yaml), [`scripts/dev.py`](../../../scripts/dev.py), [`devstack.py`](../../../libs/jane-kit/src/jane_kit/devstack.py), `tests/e2e/jane_e2e/{clients,stack,registry}.py`, `deploy/profiles/{stack.py,harness/limits_harness.py}`, `examples/jane_examples.py` |
| 5. Тести | jane-kit: 28 тестів `test_auth.py` (api_key: ок/немає/невірний/бракує scope/`Basic`; `secret_ref` env/file/YAML-файл; fail-closed — 9 випадків; ключі не в повідомленнях; `none` + loopback; таблиця покриває всі маршрути, зокрема підключені роутери; jwt: RS256/ES256 ок, прострочений, чужий `iss`, чужий `aud`, `nbf` у майбутньому, без `exp`, `alg=none`, HS256 з публічним ключем як секретом, чужий ключ, ES256-заголовок з RSA-ключем, невідомий `kid` з одним оновленням JWKS і cooldown, недоступний IdP → 503, справжній HTTP-JWKS на 127.0.0.1) + 9 `test_auth_scopes.py`; у кожному сервісі `tests/test_auth.py` (401 без токена, 403 без scope, health відкритий, `/v1/info` правдивий, вихідні токени); `infra/tests/test_auth_config.py` — матриця стеку без Docker | див. «Команди» |
| 6. Документація | Розділ «Автентифікація (ADR-0005)» у README кожного сервісу (scopes операцій, власні токени), довідник змінних у README jane-kit, правдивий розділ у `docs/operations/README.md` (що до M3 `api_key` у 6 сервісах нічого не захищав; матриця ідентичностей), примітки в `infra/`, `deploy/profiles/`, `examples/` README, `backup-restore.md` | |

### Рішення, які ADR-0005 / контракт лишали відкритими

- **Код 401** — `unauthenticated` (так у `common.yaml` `Unauthenticated` і `contracts/docs/errors.md`), а не
  `unauthorized`, як у тексті доручення.
- **`/v1/info`** — будь-який дійсний токен без scope: у `common.yaml` path item `Info` не має `security: []` і
  оголошує 401. Тому registry читає профілі runtime з `GET <runtime>/v1/info` власним ключем без scopes runtime.
  **`/metrics`** поза контрактом — типово без токена (скрейпер Prometheus у внутрішній мережі),
  `METRICS_PUBLIC=false` вимагає дійсний токен. `/openapi.json`, `/docs` — дійсний токен. `/v1/health` — завжди
  відкритий.
- **Scopes без явного рядка в ADR:** читання підключень — `connections:write` або базовий scope виконавця
  (`collector:read` / `handler:invoke`); `/v1/jobs` — scopes операцій, чиї job сервіс веде; перевірка правил
  колектора — `collector:read` або `collector:run`; скидання стану колектора — `collector:run`; читання
  провайдерів і псевдонімів llm — `llm:invoke` або `llm:admin`, бюджети й usage — лише `llm:admin`;
  `orchestrator:admin` і далі дає читання й запис (як було). Усе — в одному файлі `jane_kit/auth_scopes.py`.
- **`none`** — лише loopback (ADR: «сервіс слухає 127.0.0.1»): з `HOST=0.0.0.0` сервіс не стартує, якщо явно не
  задано `AUTH_NONE_ALLOW_REMOTE=true`. Образи (`HOST=0.0.0.0`) без налаштованої автентифікації тепер не
  стартують — це навмисно.
- **Недоступний IdP** без ключів у кеші — 503 `service_unavailable` (retryable), а не 401: токен не
  обов'язково поганий.
- **Авторизація як залежність застосунку**, а не в middleware: FastAPI 0.141 тримає підключені роутери
  (`jobs_router`) як вкладений `_IncludedRouter`, і лише після маршрутизації відомий шаблон шляху
  (`scope["route"]`). Middleware робить 401 до будь-якої обробки; 403 — залежність, що виконується до
  обробника. Перевірка покриття на старті бере маршрути застосунку й OpenAPI-документ.

### Ключ адмінки в real-e2e (`JANE_ADMIN_E2E_API_KEY`)

Як було: ключ **ніде не перевірявся** — у `infra/compose.yaml` жоден сервіс не задавав `AUTH_MODE`, тож усі, зокрема
orchestrator і registry, працювали в `none` і приймали будь-який `Bearer`. Тепер `just up` генерує
`JANE_API_KEY_ADMIN`, а кожен сервіс приймає його хеш з усіма scopes своїх API (тест
`infra/tests/test_auth_config.py::test_service_runs_with_api_keys` перевіряє «admin = усі scopes сервісу»).
Для `pnpm e2e:real` треба передати той самий ключ: `JANE_ADMIN_E2E_API_KEY=<just env →
JANE_STACK_AUTH_ADMIN_API_KEY>`. `web/admin/scripts/configure-real-stack.mjs` працює без змін: він бере `env` зі
стек-файлу (тепер з ключами й хешами), а виконавці без токенів отримують власний токен оркестратора
(`SERVICE_TOKEN_REF`). У `web/admin` нічого не змінено (запит нижче).

### Узгодження з B1 (ContentRef)

handler-runtime і llm з кореня `/var/lib/jane/storage/objects` читають RAW усіх джерел, тому `POST /v1/invocations`
і `GET /v1/invocations/{id}` у них вимагають токен і `handler:invoke` без винятків (`llm:invoke`/`llm:admin`
недостатньо). Тести: `services/handler-runtime/tests/test_auth.py`, `services/llm/tests/test_auth.py` (401 без
токена, 403 з `handler:test`, з ключем без scopes, з `llm:invoke`, з `llm:admin`). Монтування й корені — у гілці B1;
моя гілка томів не змінює (попереднє повідомлення про `storage-data` скасовано координатором).

## Відповідність доручення

| Умова | Чим перевірено | Результат |
|---|---|---|
| jane-kit: режими, хеші, `secret_refs`, JWT за JWKS (TTL, тайм-аут, `iss`/`aud`/`exp`/`nbf`, `alg=none`/HS*, невідомий `kid`), 401/403 problem+json, health відкритий, `/v1/info` правдивий, fail-closed, `none` → попередження | `libs/jane-kit/tests/test_auth.py` (28) | так |
| Підключення у 8 сервісах зі scopes на кожну операцію, звірено з OpenAPI | `test_auth_scopes.py::test_table_equals_contract[*]` (7 контрактів), старт-перевірка покриття маршрутів, `services/*/tests/test_auth.py` | так |
| orchestrator і registry на спільному модулі, наявні тести зелені | `just test orchestrator`, інтеграційні orchestrator (39), `just test registry` | так |
| Вихідні виклики власним токеном; токени виконавців через `env:`-посилання; assistant — окремий токен на сусіда | `services/orchestrator/tests/test_auth.py`, `services/assistant/tests/test_auth.py`, `services/registry/tests/test_auth.py`; dev-стек: синхронізація підключення orchestrator → storage/llm (`synced`), registry → runtime профілі з токеном (без токена — 401) | так |
| Стеки в `api_key`; ключі генеруються в `.jane/`, у git немає | `infra/tests/test_auth_config.py` (11), smoke dev-стеку, CI `stack`/`e2e`/`limits` | так (див. CI) |
| Ключ адміністратора real-e2e приймають усі сервіси | `test_service_runs_with_api_keys` (admin = усі scopes), smoke через Caddy з ключем `admin` | так; Playwright real-e2e не запускав |
| Документація | README 8 сервісів, jane-kit, operations | так |

## Відповідність DoD (plan.md §4)

| Пункт | Стан | Примітка |
|---|---|---|
| API за контрактом, контрактні тести | так | `bearerAuth`/401/403 за `common.yaml`; таблиці = контракт; `contracts/` не змінено |
| Unit- та інтеграційні тести, одна команда | так | `just test <сервіс>`; jane-kit — `just test jane-kit` |
| README | так | розділ «Автентифікація (ADR-0005)» у кожному сервісі |
| Dockerfile, health, журнали, метрики, кілька екземплярів | так | health відкритий для healthcheck compose; ключі — лише конфігурація (кілька екземплярів однакові); старт журналює режим та імена ключів, не значення |
| Власність шляхів | так | лише дозволені дорученням шляхи; групування нижче |

## Змінені файли за власниками (`.claude/wp-paths.json`)

| Власник | Файли |
|---|---|
| WP-01 (scaffold-ci) | `libs/jane-kit/{pyproject.toml, README.md, src/jane_kit/{auth.py, auth_scopes.py, config.py, devstack.py, service.py}, tests/{test_auth.py, test_auth_scopes.py}}`, `infra/{compose.yaml, README.md, tests/test_auth_config.py}`, `scripts/dev.py`, `uv.lock` (спільний; + `pyjwt[crypto]` → `pyjwt`, `cryptography`, `cffi`, `pycparser`, без `httpx2`) |
| WP-02 web-collector | `services/web-collector/{README.md, src/jane_web_collector/app.py, tests/test_auth.py}` |
| WP-04 telegram-collector | `services/telegram-collector/{README.md, src/jane_telegram_collector/app.py, tests/test_auth.py}` |
| WP-05 registry | `services/registry/{README.md, src/jane_registry/{app.py, auth.py, profiles.py, settings.py}, tests/{test_auth.py, test_service_ops.py}}` |
| WP-06 handler-runtime | `services/handler-runtime/{README.md, src/jane_handler_runtime/app.py, tests/test_auth.py}` |
| WP-07 storage | `services/storage/{README.md, src/jane_storage/app.py, tests/test_auth.py}` |
| WP-09 orchestrator | `services/orchestrator/{README.md, src/jane_orchestrator/{app.py, auth.py, settings.py}, tests/test_auth.py}` |
| WP-10 llm | `services/llm/{README.md, src/jane_llm/{app.py, settings.py}, tests/test_auth.py}` |
| WP-11 assistant | `services/assistant/{README.md, src/jane_assistant/{app.py, clients.py, settings.py}, tests/test_auth.py}` |
| WP-13 integration | `tests/e2e/jane_e2e/{clients.py, registry.py, stack.py}` (лише токени) |
| WP-14 limits/ops | `deploy/profiles/{README.md, stack.py, harness/limits_harness.py}`, `examples/{README.md, jane_examples.py}` (лише токени), `docs/operations/{README.md, backup-restore.md}` (автентифікація) |
| звіт | `docs/delivery/M3/01g-auth.md` |

`web/admin/**`, `contracts/**`, `docs/adr/**`, `templates/**` не змінено. Зміна наявного тесту одна:
`services/registry/tests/test_service_ops.py::test_api_keys_and_scopes` раніше читав `/v1/info` без токена;
тепер перевіряє, що без токена — 401, а з ключем `reader` — `auth_mode=api_key` (посилення за контрактом `Info`).

## Команди перевірки та їхній вивід

Локально: Windows 11, Docker Desktop 29.8.0, `uv run --all-packages` (тест-набори запускалися по пакетах).

```text
$ uv run --all-packages ruff check . ; ruff format --check . ; uv lock --check
All checks passed!
428 files already formatted
Resolved 109 packages in 6ms
$ uv run --all-packages mypy <пакет>/src <пакет>/tests        # кожен змінений пакет
mypy libs/jane-kit: Success: no issues found in 28 source files
mypy services/storage: Success: no issues found in 29 source files
mypy services/handler-runtime: Success: no issues found in 24 source files
mypy services/llm: Success: no issues found in 25 source files
mypy services/web-collector: Success: no issues found in 37 source files
mypy services/telegram-collector: Success: no issues found in 21 source files
mypy services/assistant: Success: no issues found in 35 source files
mypy services/orchestrator: Success: no issues found in 28 source files
mypy services/registry: Success: no issues found in 28 source files
mypy scripts infra/tests: Success: no issues found in 6 source files

$ uv run --all-packages pytest libs/jane-kit/tests/test_auth.py libs/jane-kit/tests/test_auth_scopes.py \
    services/*/tests/test_auth.py infra/tests/test_auth_config.py -m "not integration" -q
60 passed, 2 deselected, 1 warning in 5.52s

# повні набори сервісів (= just test <сервіс>: -m "not integration and not isolation") після підключення таблиць
$ pytest services/storage            -> 180 passed, 111 deselected in 51.80s
$ pytest services/llm                -> 57 passed, 34 deselected in 8.86s
$ pytest services/telegram-collector -> 38 passed in 94.26s
$ pytest services/assistant          -> 66 passed, 5 deselected in 28.82s
$ pytest services/handler-runtime    -> 43 passed, 13 deselected, 26 warnings in 84.74s
$ pytest services/web-collector      -> 141 passed in 490.48s
# після переведення orchestrator/registry, токенів assistant/llm і генерації ключів:
$ pytest libs/jane-kit infra/tests scripts/tests templates/service services/assistant services/llm \
    services/registry services/orchestrator -m "not integration and not isolation" -q
SKIPPED [1] templates\service\tests\test_contract.py:61: service contract not in contracts/openapi yet
500 passed, 1 skipped, 117 deselected in 295.48s (0:04:55)
$ pytest services/orchestrator -m integration -q              # PostgreSQL у Docker (orch_support)
39 passed, 23 deselected in 649.82s (0:10:49)
$ pytest services/orchestrator/tests/test_auth.py services/orchestrator/tests/test_contract.py -q
5 passed in 94.44s (0:01:34)
$ pytest examples deploy/profiles -m "not contract and not integration and not isolation" -q   # після rebase на f1c78e9
83 passed, 3 warnings in 53.85s
$ pytest infra/tests scripts/tests -m "not integration" -q
45 passed, 8 deselected in 40.91s
```

Smoke на dev-стеку (`just up --project jane-01g proxy storage registry handler-runtime web-collector
telegram-collector orchestrator llm assistant` — усі контейнери `Healthy`, `exit 0`), усе через Caddy
`/api/<сервіс>/…`, ключі — зі стек-файлу:

```text
storage             health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
handler-runtime     health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
web-collector       health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
telegram-collector  health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
orchestrator        health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
registry            health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
llm                 health=200 no-token=401 wrong-key=401 admin=200 info(no-token)=401 info.auth_mode=api_key -> OK
assistant           health=200 no-token=401 wrong-key=401 admin=404 info(no-token)=401 info.auth_mode=api_key -> OK
registry POST /v1/packages with web-collector key -> 403 scope registry:write required -> OK
orchestrator GET /v1/sources with web-collector key -> 401 -> OK
ALL OK
```

(`admin=404` в assistant — авторизований `GET /v1/jobs/job_smoke` неіснуючого job.) Виклики між сервісами
власними токенами: `node web/admin/scripts/configure-real-stack.mjs jane-01g` (скрипт адмінки без змін; виконавці
без токенів) → `PUT /v1/connections/smoke-auth-files` в orchestrator:

```text
executors: {'web-collector': 'ok', 'handler-runtime': 'ok', 'storage': 'ok', 'storage-read': 'ok', 'registry': 'ok', 'llm': 'ok', 'assistant': 'ok'}
PUT connection -> 200
storage: sync_status synced; llm: sync_status synced
handler-runtime: failed "executor does not use managed connections (not_implemented)"   # 501, бізнес-логіка, не 401/403
web-collector: failed "PUT /v1/connections/smoke-auth-files: HTTP 422"                   # kind filesystem колектору не підходить
```

registry → handler-runtime (`GET /v1/info` профілів) у контейнері registry з його конфігурацією:

```text
sources ['http://handler-runtime:8000/v1/info'] token_ref env:JANE_SECRET_REGISTRY_TOKEN
profiles ['python-extractor@1'] errors []
without token errors ["http://handler-runtime:8000/v1/info: HTTPStatusError: Client error '401 Unauthorized' ..."]
```

`just down --project jane-01g -v` → exit 0 (контейнери, томи й образи проєкту видалено).

CI на `5f77bdf` (код; наступні коміти — лише документація):

- push-прогін [37850656014](https://github.com/sql-monk/Jane/actions/runs/37850656014) скасовано concurrency-групою
  через dispatch того самого ref;
- `gh workflow run ci --ref wp/01g-service-auth` → [37850701212](https://github.com/sql-monk/Jane/actions/runs/37850701212):
  lint ✓, unit ✓, contract ✓, web ✓, isolation ✓, stack ✓, adapters (sqlserver, mongodb, minio, s3) ✓,
  **e2e ✓ — `71 passed in 1338.08s (0:22:18)`** (`JANE_E2E_REQUIRED=1`, пропусків немає).
  `limits`: спроба 1 — `L6 sandbox … -> fail`, `verdict: fail` (L1–L5, L8 — pass; деталі лише в артефакті
  `limits-ci-37850701212-1`, я його не завантажував); `gh run rerun --failed` → спроба 2 — L1–L6, L8 `pass`,
  `verdict: pass`, run `completed success`. Локальне відтворення L6 з тим самим профілем
  (`limits_harness.py run --profile ci --only L6 --allow-busy`, 30 сторонніх контейнерів) — `verdict: pass`
  (cold start p95 4.19 с при межі 15 с, `timeout` і `resource_exceeded` як треба, паралельних пісочниць 2 ≤ 2).
  Причину першого `fail` не встановлено; L6 кличе runtime тим самим ключем, що й L8, який пройшов.

## Rebase на інтеграційну ревізію і L6

**Rebase.** `git rebase origin/codex/jane-integration` (на час rebase — `bf69429`, далі лише документація до `3ec9358`;
у базі вже злито WP-14d, WP-13s, B1 `wp/01h-content-ref-policy`, M3 should-fix `69ab303`, WP-12d `bf69429`). Конфлікти
два, обидві сторони збережено:

- `services/llm/src/jane_llm/settings.py` — імпорти: `from pydantic import Field, SecretStr, field_validator`
  (`field_validator` — B1/should-fix для `api_base`, `SecretStr` — мій токен registry);
- `services/handler-runtime/README.md` — абзац B1 «Політика ContentRef (WP-01h)» і мій розділ «Автентифікація».

`infra/compose.yaml`, `tests/e2e/compose.e2e.yaml`, settings orchestrator/web-collector/telegram, `ci.yml`
злилися без конфліктів (мої рядки автентифікації поруч із монтуванням `storage-data:ro`, `BLOB_ROOTS` і allowlist B1).
Перевірив нові шляхи на токени: `ContentReader` B1 ходить лише до blob/`download_url` (`package-host`, не сервіси Jane),
«шлюзи» R-04 WP-13s (`jane_e2e/active.py`) — теж до `package-host`; виклик LLM у R-04 (`llm.http.post("/v1/completions")`)
іде через `JaneClient` і отримує ключ стеку; `configure-real-stack.mjs` WP-12d вмикає `REGISTRY_URL`/`ORCHESTRATOR_URL`/
`COLLECTOR_WEB_URL` асистента — асистент іде туди власним токеном із базового compose (`SERVICE_TOKEN_REF`), а
`llm`-виконавець оркестратора — токеном оркестратора (`handler:invoke` у llm є). `executors.py` після should-fix
(`keepalive_expiry`) і далі ставить `Authorization` у клієнта виконавця.

```text
$ uv run --all-packages ruff check . ; ruff format --check .
444 files already formatted
$ uv run --all-packages mypy <пакет>/src <пакет>/tests
mypy libs/jane-kit: Success: no issues found in 30 source files
mypy services/storage: Success: no issues found in 29 source files
mypy services/handler-runtime: Success: no issues found in 25 source files
mypy services/llm: Success: no issues found in 30 source files
mypy services/web-collector: Success: no issues found in 39 source files
mypy services/telegram-collector: Success: no issues found in 23 source files
mypy services/assistant: Success: no issues found in 36 source files
mypy services/orchestrator: Success: no issues found in 31 source files
mypy services/registry: Success: no issues found in 28 source files
mypy scripts infra/tests: Success: no issues found in 6 source files
$ uv run --all-packages pytest libs/jane-kit infra/tests scripts/tests services/llm services/handler-runtime     services/assistant services/registry services/orchestrator services/storage     services/web-collector/tests/test_auth.py services/telegram-collector/tests/test_auth.py     -m "not integration and not isolation" -q
788 passed, 259 deselected, 32 warnings in 488.98s (0:08:08)
```

**Причина L6 у першій спробі `limits` CI 37850701212** (`gh run download 37850701212 -n limits-ci-37850701212-1`,
`results.json` і `raw/r1-L6-runtime.jsonl`): з автентифікацією **не пов'язана**. Усі виклики runtime пройшли
(холодні старти, тайм-аут, паралельні пісочниці, `/v1/info` — 200); впала одна блокувальна перевірка:

```text
FAIL blocker memory exceeded -> failure.kind execution_error == resource_exceeded
{"case": "memory", "elapsed_s": 0.33183123099999534, "status": "failed", "failure": {"kind": "execution_error",
 "details": {"error": "Expecting value: line 1 column 1 (char 0)", "exit_code": 137, "max_processes": 16},
 "message": "sandbox runner produced no valid result (exit code 137)", "retryable": false}}
OK   blocker cold start p95, s 0.2589876870000012 <= 15.0
OK   blocker wall time exceeded -> failure.kind timeout == timeout
OK   blocker parallel sandboxes 2 <= 2
OK   blocker parallel invocations finished 4 == 4
```

Пісочницю вбив OOM (код 137 = SIGKILL через 0.33 с після старту, під час виділення `memory_mb` + 256 МБ), але Docker
повернув `State.OOMKilled = false`, тож `executor.py` (класифікує `resource_exceeded` лише за
`outcome.oom_killed`, який `docker_sandbox.py` бере з `inspect_container().State.OOMKilled`) віднесла відмову до
`execution_error`. На cgroup v2 (ubuntu-24.04) прапорець OOMKilled виставляється за подією OOM від containerd і може
не встигнути до `wait`/`inspect` або не стосуватися PID 1, якщо OOM-killer вибрав дочірній процес; у другій спробі й
локально (`--only L6`) та сама перевірка — `resource_exceeded`. Це нестабільна класифікація OOM у handler-runtime
(WP-06), не дефект автентифікації; код пісочниці поза моїм дорученням, тож не правив — запит нижче.

## Конфігурація й ліміти

| Параметр (env `<PREFIX>…`) | Типове значення | Де задається |
|---|---|---|
| `AUTH_MODE` | `none` | `jane_kit.auth.AuthSettings` (усі сервіси); у стеках — `api_key` |
| `API_KEYS` / `API_KEYS_FILE` | `[]` / — | там само |
| `JWT_JWKS_URL` / `JWT_ISSUER` / `JWT_AUDIENCE` | — | там само (обов'язкові для `jwt`) |
| `JWT_ALGORITHMS` | `["RS256","ES256"]` | там само |
| `JWT_SCOPE_CLAIM` / `JWT_LEEWAY_SECONDS` | `scope` / 30 | там само |
| `JWT_JWKS_CACHE_TTL_SECONDS` / `JWT_JWKS_TIMEOUT_MS` | 300 / 5000 | там само |
| `JWT_JWKS_REFRESH_COOLDOWN_SECONDS` / `JWT_JWKS_MAX_BYTES` | 10 / 1048576 | там само |
| `AUTH_MAX_TOKEN_BYTES` | 16384 | там само |
| `METRICS_PUBLIC` / `AUTH_NONE_ALLOW_REMOTE` | `true` / `false` | там само |
| orchestrator `SERVICE_TOKEN_REF`, виконавець `token_ref` | — | `jane_orchestrator.settings` |
| assistant `SERVICE_TOKEN_REF`, `<сусід>_TOKEN_REF` | — | `jane_assistant.settings` |
| registry `RUNTIME_PROFILES_TOKEN_REF` | — | `jane_registry.settings` |

## Відомі обмеження

- Ключ `api_key` статичний: ротація — новий запис у `API_KEYS` і перезапуск; відкликання JWT до `exp` немає
  (стандартна властивість stateless JWT).
- `api_key`-стеки: хеші ключів передаються сервісам через змінні середовища контейнерів; самі ключі — лише в
  середовищі їхнього власника (orchestrator, assistant…) і в ігнорованому стек-файлі.
- Для `none` сервіс без явного `HOST` слухає `127.0.0.1`; сторонні запуски образів без `AUTH_MODE` тепер
  падають на старті (навмисно, fail-closed).
- `templates/service` (не мій шлях) отримує автентифікацію з `create_app` автоматично, але без таблиці scopes —
  лише автентифікація (запит нижче).

## Неперевірені інтеграції

- `jwt` з реальним IdP (Keycloak, Entra ID, OAuth2 client credentials) — **не перевірено на реальному сервісі**;
  перевірено з локальним JWKS (httpx-транспорт і справжній HTTP-сервер на 127.0.0.1). Жоден стек не запускається в
  `jwt`.
- Playwright real-e2e адмінки (`pnpm e2e:real`) локально не запускав; через Caddy з ключем `admin` перевірено
  smoke-скриптом (усі 8 сервісів) і в CI e2e — через клієнти harness (прямо, не через Caddy).

## Запити до інших власників

| Кому | Що потрібно | Навіщо |
|---|---|---|
| WP-00 / координатор (ADR-0005) | Записати в ADR рішення, які він лишав відкритими: `/v1/info` — будь-який дійсний токен; `/metrics` — типово відкритий; scopes читання підключень, `/v1/jobs`, перевірки правил і скидання стану колектора, читання llm; `none` лише на loopback | Щоб наступні сервіси не вирішували це заново; зараз джерело правди — `jane_kit/auth_scopes.py` |
| WP-00 (contracts) | Розглянути `security: [{bearerAuth: [<scope>]}]` на операціях OpenAPI (або `x-jane-scope`) | Тоді `test_table_equals_contract` звірятиме й самі scopes, не лише перелік операцій |
| WP-12 (admin) | `scripts/e2e.mjs --real` — брати ключ із `.jane/stack-<project>.json` (`env.JANE_API_KEY_ADMIN`), якщо `JANE_ADMIN_E2E_API_KEY` не задано; у README «Режими e2e» — звідки ключ (`just env` → `JANE_STACK_AUTH_ADMIN_API_KEY`) | Real-e2e у стеку `api_key` без ручного копіювання ключа; без ключа адмінка отримає 401 |
| WP-06 (handler-runtime) | Класифікувати OOM надійно: після `wait` за коду 137 без тайм-ауту перечитати `State.OOMKilled` (коротко, з тайм-аутом з конфігурації) і/або читати лічильник `oom_kill` з `memory.events` cgroup v2 контейнера; лише якщо OOM не підтверджено — `execution_error` | L6 `limits` CI 37850701212 спроба 1: `exit_code 137`, `OOMKilled=false` → `execution_error` замість `resource_exceeded` (нестабільний блокер профілю `ci`) |
| WP-01 (templates/service) | `create_app(..., auth_scopes=...)` у шаблоні з таблицею для прикладних маршрутів і рядок у README про автентифікацію | Нові сервіси одразу з таблицею scopes (зараз — лише автентифікація) |
