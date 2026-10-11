# Admin UI: експлуатація

Розгортання статики за reverse proxy, оновлення, моніторинг і типові проблеми. Admin UI не має сервера й бази, тому міграцій, резервування й відновлення власних даних немає: дані належать сервісам ([карта власності даних](../../architecture/data-ownership.md)).

## Зміст

- [Розгортання](#розгортання)
- [Вимоги до reverse proxy](#вимоги-до-reverse-proxy)
- [Оновлення](#оновлення)
- [Моніторинг](#моніторинг)
- [Масштабування](#масштабування)
- [Типові проблеми](#типові-проблеми)

## Розгортання

1. Зберіть статику:

   ```powershell
   corepack pnpm --dir web/admin install --frozen-lockfile
   corepack pnpm --dir web/admin build
   ```

2. Скопіюйте вміст `web/admin/dist` на вебсервер або в reverse proxy. Каталог містить `index.html`, `assets/` з хешованими іменами файлів, source map і `config.json` з `public/`.
3. Покладіть поруч `config.json` для цього розгортання: адреса API, режим входу, параметри опитування ([configuration.md](configuration.md#configjson)). Файл можна замінювати без перезбирання.
4. Налаштуйте маршрути `/api/<сервіс>/*` на сервіси й заголовки безпеки ([Вимоги до reverse proxy](#вимоги-до-reverse-proxy)).

У dev-стеку це робить контейнер `proxy` ([infra/compose.yaml](../../../infra/compose.yaml)):

| Том або змінна | Типово | Призначення |
|---|---|---|
| `JANE_ADMIN_DIST_PATH` → `/srv/admin` | `web/admin/dist`, якщо каталог існує під час `just up`; інакше порожній `infra/proxy/empty` | статика адмінки |
| `JANE_ADMIN_CONFIG_PATH` → `/srv/config/config.json` | `infra/proxy/admin-config.json` | конфігурація адмінки |
| `JANE_CSP_CONNECT_SRC`, `JANE_CSP_FORM_ACTION` | порожньо | доповнення CSP ([configuration.md](configuration.md#csp-reverse-proxy)) |

Запуск усього стеку — [Платформа з Admin UI](../../getting-started/platform.md); розгортання платформи загалом — [архітектура розгортання](../../architecture/deployment.md).

## Вимоги до reverse proxy

| Вимога | Як у dev-стеку ([Caddyfile](../../../infra/proxy/Caddyfile)) |
|---|---|
| `/api/<сервіс>/*` → сервіс із зняттям префікса | `handle_path /api/orchestrator/* { reverse_proxy orchestrator:8000 }` тощо |
| невідомий `/api/*` не віддає `index.html` | `respond "Jane dev proxy: unknown API" 404` |
| `/config.json` без кешування | `Cache-Control: no-store` |
| прямі посилання на сторінки (`/tasks/abc`) віддають `index.html` | `try_files {path} /index.html` |
| заголовки безпеки | `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` |
| заголовок `Authorization` передається сервісам без змін | поведінка `reverse_proxy` за замовчуванням |

Перевірено на стеку `jane-doc-ui` (ревізія `48389a3`): `/` і `/tasks/abc` — `200` з CSP; `/config.json` — `Cache-Control: no-store`; `/api/orchestrator/v1/health` — `200`; `/api/orchestrator/v1/sources` без ключа — `401`.

Для виконавців, яких адмінка адресує за ім'ям (колектор запуску, виконавці підключень), proxy має маршрут `/api/<ім'я виконавця>/*` з тим самим ім'ям, що в реєстрі Orchestrator. У dev-стеку є маршрути `storage`, `handler-runtime`, `web-collector`, `telegram-collector`, `llm`.

## Оновлення

| Що змінилося | Дії |
|---|---|
| код адмінки | `build`, замінити статику; браузери отримають нові файли за хешованими іменами після перезавантаження сторінки |
| контракти `contracts/openapi` чи `contracts/schemas` | `corepack pnpm --dir web/admin gen:api`, перевірки (`lint`, `typecheck`, `test`), `build`, розгорнути |
| `config.json` | замінити файл; користувачі отримають зміни після перезавантаження сторінки |
| адреси або імена сервісів | маршрути proxy і, якщо змінився сегмент, `services` у `config.json` |
| залежності npm | `corepack pnpm --dir web/admin install` оновлює `pnpm-lock.yaml`; у CI — лише `--frozen-lockfile` |

Сумісність: адмінка розрахована на API `/v1` тієї самої ревізії контрактів. Зворотно сумісні розширення контракту (нові поля, нові операції) не ламають зібрану адмінку; нові можливості з'являються після `gen:api` і нового збирання. Відкриті сесії не зберігають стану на сервері, тож оновлення не потребує вікна обслуговування; ключ у `sessionStorage` лишається дійсним після оновлення статики.

## Моніторинг

У адмінки немає health-ендпоінта й метрик: її доступність — це доступність статики й proxy.

| Що перевірити | Як |
|---|---|
| proxy живий | `GET /_proxy/health` → `ok` (dev-стек) |
| статика й конфігурація | `GET /` і `GET /config.json` → `200` |
| сервіси | `GET /api/<сервіс>/v1/health` без токена → `200`; моніторинг сервісів — [експлуатація платформи](../../operations/monitoring.md) |
| виконавці з погляду Orchestrator | блок «Виконавці» на сторінці «Огляд» (`GET /v1/executors`) |
| помилки в браузері | консоль розробника; адмінка не пише журналів на сервер |

## Масштабування

Статика не має стану, тож її можна віддавати з будь-якої кількості екземплярів proxy чи CDN. Навантаження на сервіси задають `page_size` і `polling.*` у `config.json`: менший `page_size` і більші паузи зменшують кількість запитів від відкритих вкладок.

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| `[WARN] This project is configured to use 11.27.1 of pnpm` | corepack запустив іншу версію pnpm; `pmOnFail: warn` | можна ігнорувати; перевірки на ревізії `48389a3` проходять з pnpm 12.8.1 |
| `pnpm lint` падає на Prettier для `README.md` | файл має переноси рядків CRLF | збережіть файл з LF або виконайте `corepack pnpm --dir web/admin format` |
| `pnpm lint` повідомляє, що згенеровані файли застаріли | змінено `contracts/` | `corepack pnpm --dir web/admin gen:api` |
| `pnpm dev` не стартує: порт зайнятий | `strictPort` не шукає інший порт | звільніть порт або задайте `JANE_ADMIN_PORT` |
| на сторінках `upstream_unavailable` | не запущені моки або сервіс | запустіть `pnpm mocks` з тим самим `JANE_ADMIN_MOCK_PORT_BASE` або перевірте сервіс |
| банер «Сесія недійсна або прострочена (401)» | неправильний або відкликаний ключ, прострочений токен | «Увійти знову» з актуальним ключем (`just env`) |
| на дії помилка з кодом `forbidden` | у ключа немає потрібної області | [права ключа](integration.md#права-ключа) |
| «Не вдалося завантажити config.json» | `auth.mode = "oidc"` без `authority` або `client_id` | виправте `config.json` |
| proxy dev-стеку не віддає сторінок адмінки | `web/admin/dist` не існував під час `just up` | зберіть адмінку й повторіть `just up` |
| запити до API блокує браузер (CSP) | `api_base` чи постачальник OIDC на іншому origin | додайте origin у `JANE_CSP_CONNECT_SRC` (і `JANE_CSP_FORM_ACTION` для OIDC) |
| вкладка «Помилки колектора» порожня з помилкою | колектор запуску недоступний через proxy за своїм ім'ям | додайте маршрут `/api/<executor>/*` |
