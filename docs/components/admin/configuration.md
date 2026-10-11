# Admin UI: конфігурація

Адмінку налаштовують без перезбирання: файл `config.json` поруч зі статикою читається під час кожного завантаження сторінки. Змінні середовища нижче стосуються лише dev-сервера Vite і тестів. Джерело — [src/config.ts](../../../web/admin/src/config.ts), [dev-proxy.ts](../../../web/admin/dev-proxy.ts), [vite.config.ts](../../../web/admin/vite.config.ts).

## Зміст

- [config.json](#configjson)
- [Типові значення](#типові-значення)
- [Автентифікація](#автентифікація)
- [Змінні dev-сервера](#змінні-dev-сервера)
- [CSP reverse proxy](#csp-reverse-proxy)
- [Ліміти](#ліміти)
- [Застосування змін](#застосування-змін)

## config.json

Адмінка запитує `/config.json` із `cache: "no-store"`. У репозиторії два однакові файли: [web/admin/public/config.json](../../../web/admin/public/config.json) (dev-сервер і збирання) і [infra/proxy/admin-config.json](../../../infra/proxy/admin-config.json) (proxy dev-стеку).

```json
{
  "api_base": "/api",
  "services": {
    "orchestrator": "orchestrator",
    "registry": "registry",
    "storage": "storage",
    "llm": "llm",
    "handler": "handler-runtime",
    "assistant": "assistant",
    "collector": "web-collector"
  },
  "auth": { "mode": "api_key" },
  "polling": { "initial_ms": 1000, "max_ms": 15000, "multiplier": 1.5 },
  "page_size": 50,
  "preview_max_bytes": 262144
}
```

| Параметр | Тип | Типово | Допустимі значення | Вплив |
|---|---|---|---|---|
| `api_base` | рядок | `/api` | відносний префікс або абсолютна URL | база всіх API: `<api_base>/<сервіс>/v1/...`; кінцеві `/` відкидаються |
| `services.<ключ>` | рядок | ім'я сервісу | `^[a-z0-9][a-z0-9._-]*$` | сегмент шляху proxy для контракту |
| `auth.mode` | рядок | `api_key` | `api_key`, `none`, `oidc` | спосіб входу ([Автентифікація](#автентифікація)) |
| `auth.authority` | рядок | — | URL постачальника | обов'язковий для `oidc` |
| `auth.client_id` | рядок | — | ідентифікатор клієнта | обов'язковий для `oidc` |
| `auth.scope` | рядок | `openid profile` | області OIDC | запит токена |
| `auth.redirect_path` | рядок | `/auth/callback` | шлях адмінки | повернення після входу |
| `auth.post_logout_redirect_path` | рядок | `/` | шлях адмінки | повернення після виходу |
| `polling.initial_ms` | число | `1000` | ≥ 100 | перша пауза опитування job і списків, що змінюються |
| `polling.max_ms` | число | `15000` | ≥ 100, не менше `initial_ms` | верхня межа паузи |
| `polling.multiplier` | число | `1.5` | ≥ 1 | множник паузи після кожного опитування |
| `page_size` | ціле | `50` | ≥ 1 | `limit` списків; сервіс обмежує його своїм максимумом |
| `preview_max_bytes` | ціле | `262144` | ≥ 1 | скільки байтів вмісту збереженого об'єкта запитувати для перегляду (`Range`) |

Ключі `services`: `orchestrator`, `registry`, `storage`, `llm`, `handler`, `assistant`, `collector`. Ключ `handler` — це Handler Runtime (тести пакетів), `collector` — колектор за замовчуванням для вкладки помилок збору, якщо Orchestrator не повідомив ім'я виконавця-колектора.

## Типові значення

Відсутній або некоректний параметр замінюється типовим значенням без помилки: рядок не того формату, число поза межами, нечислове значення. `config.json`, що не є JSON-об'єктом, або відповідь не `200` — усі значення типові. Єдина фатальна помилка — `auth.mode = "oidc"` без `authority` чи `client_id`: адмінка показує «Не вдалося завантажити config.json» і не стартує.

## Автентифікація

| `auth.mode` | Вхід | Де зберігається облікове | Що надсилається |
|---|---|---|---|
| `api_key` | поле «Ключ API» на сторінці входу | `sessionStorage`, ключ `jane.admin.api_key` | `Authorization: Bearer <ключ>` |
| `oidc` | кнопка «Увійти через IdP», Authorization Code + PKCE | `sessionStorage` (стан і користувач `oidc-client-ts`) | `Authorization: Bearer <access token>` |
| `none` | без входу | — | без заголовка; лише для сервісів з `auth_mode=none` |

Ключ не потрапляє в `localStorage`, URL чи текст сторінки; він живе до закриття вкладки або «Вийти». За `oidc` токен оновлюється автоматично (`automaticSilentRenew`), а ім'я користувача (email, name або sub) показується внизу бічної панелі. Сервіси мають працювати в режимі `jwt` із JWKS того самого постачальника — опис режимів у [jane-kit](../jane-kit/README.md). Режим `oidc` на ревізії `48389a3` не перевірявся з реальним постачальником.

## Змінні dev-сервера

Ці змінні читає Node.js-процес Vite або Playwright. Зібрана адмінка їх не використовує.

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ADMIN_PORT` | `4600` | порт `pnpm dev`, `pnpm preview` і e2e; слухає `127.0.0.1`, порт строгий (`strictPort`) |
| `JANE_ADMIN_MOCK_PORT_BASE` | `4611` | порт першого мока; ціле 1024–65000, інакше помилка старту; порядок: orchestrator, registry, storage, llm, handler, assistant, collector |
| `JANE_ADMIN_API_TARGET` | — | адреса reverse proxy Jane; весь `/api/*` іде туди без зміни шляху замість моків |
| `JANE_ADMIN_TARGET_<API>` | — | базова адреса одного реального сервісу замість мока (`<API>` — `ORCHESTRATOR`, `REGISTRY`, `STORAGE`, `LLM`, `HANDLER`, `ASSISTANT`, `COLLECTOR`); префікс `/api/<сервіс>` знімається |
| `JANE_ADMIN_E2E_API_KEY` | — | ключ для e2e проти стеку; `pnpm e2e:real` бере його з `.jane/stack-<проєкт>.json` сам |
| `CI` | — | e2e не перевикористовує вже запущені сервери й повторює невдалий тест один раз |

Без `JANE_ADMIN_API_TARGET` dev-сервер проксіює `/api/<сервіс>` на `http://127.0.0.1:<JANE_ADMIN_MOCK_PORT_BASE + i>` і знімає префікс. Імена сервісів у proxy dev-сервера фіксовані (`handler-runtime`, `web-collector` тощо) і мають збігатися з `services` у `config.json`.

## CSP reverse proxy

Proxy dev-стеку ([infra/proxy/Caddyfile](../../../infra/proxy/Caddyfile)) додає до кожної відповіді:

```text
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' {$JANE_CSP_CONNECT_SRC:}; frame-ancestors 'none'; base-uri 'self'; form-action 'self' {$JANE_CSP_FORM_ACTION:}; object-src 'none'
```

| Змінна compose | Типово | Коли потрібна |
|---|---|---|
| `JANE_CSP_CONNECT_SRC` | порожньо | `api_base` на іншому origin або `oidc` — додайте origin API і постачальника ідентичності |
| `JANE_CSP_FORM_ACTION` | порожньо | `oidc`, якщо постачальник приймає форму виходу на своєму origin |

`script-src 'self'` забороняє `eval`, тому валідатори JSON Schema компілюються заздалегідь (`pnpm gen:api`), а не в браузері. Також proxy задає `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`; `index.html` має `<meta name="referrer" content="no-referrer">`.

## Ліміти

Числа, що впливають на навантаження адмінки, задаються в `config.json`: `page_size`, `preview_max_bytes`, `polling.*`. Решта обмежень (розміри відповідей, частота запитів, бюджети) належить сервісам і редагується на сторінках «Ліміти» й «LLM» — [посібник](../../user-guide/limits.md).

## Застосування змін

| Що змінено | Як застосувати |
|---|---|
| `config.json` на сервері | перезавантажити сторінку в браузері; перезбирання не потрібне |
| `web/admin/public/config.json` | `pnpm dev` бере зміни одразу; для `dist` — нове збирання або заміна `dist/config.json` |
| змінні dev-сервера | перезапустити `pnpm dev` / `pnpm preview` / `pnpm mocks` |
| `JANE_CSP_*`, `JANE_ADMIN_CONFIG_PATH` | перестворити контейнер proxy (`just up` з тими самими сервісами) |
| вибрана тема | застосовується одразу й синхронізується між вкладками |
