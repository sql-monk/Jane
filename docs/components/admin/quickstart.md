# Admin UI: швидкий старт

Запуск адмінки без сервісів Jane (на контрактних моках), проти dev-стеку через reverse proxy, збирання статики й перевірки. Кроки виконано 2026-10-11 на Windows 11 (Git Bash і PowerShell), ревізія `48389a3`; на Linux не перевірялися — команди ті самі, бо скрипти адмінки написані на Node.js без залежності від оболонки.

## Зміст

- [Передумови](#передумови)
- [Запуск на моках](#запуск-на-моках)
- [Інші порти](#інші-порти)
- [Запуск проти стеку](#запуск-проти-стеку)
- [Збирання статики](#збирання-статики)
- [Перевірки](#перевірки)
- [Прибирання](#прибирання)

## Передумови

- Node.js 24 і corepack (входить до Node.js); pnpm встановлювати окремо не потрібно — його запускає `corepack pnpm`.
- uv — моки API запускаються як `uv run contracts/tools/mock.py`.
- Команди виконуються з кореня репозиторію.

Версії й поведінка за відсутності залежностей — [dependencies.md](dependencies.md).

## Запуск на моках

Моки віддають приклади з контрактів `contracts/openapi/*.v1.yaml`, тож адмінка показує демонстраційні дані без жодного сервісу.

1. Встановіть залежності адмінки:

   ```powershell
   corepack pnpm --dir web/admin install --frozen-lockfile
   ```

   Наприкінці виводу — `Done in … using pnpm v…`.

2. У першому терміналі запустіть моки — по одному на кожен API:

   ```powershell
   corepack pnpm --dir web/admin mocks
   ```

   Очікуваний результат — сім рядків `jane mock '<api>' on http://127.0.0.1:<порт>`. Уривок перевірочного запуску з базовим портом 18711 (типово 4611):

   ```text
   jane mock 'llm' on http://127.0.0.1:18714 (15 operations)
   jane mock 'registry' on http://127.0.0.1:18712 (19 operations)
   jane mock 'storage' on http://127.0.0.1:18713 (7 operations)
   jane mock 'handler' on http://127.0.0.1:18715 (12 operations)
   jane mock 'orchestrator' on http://127.0.0.1:18711 (36 operations)
   jane mock 'collector' on http://127.0.0.1:18717 (17 operations)
   jane mock 'assistant' on http://127.0.0.1:18716 (12 operations)
   ```

3. У другому терміналі запустіть dev-сервер Vite. Він віддає адмінку й проксіює `/api/<сервіс>/*` на моки:

   ```powershell
   corepack pnpm --dir web/admin dev
   ```

   У виводі — адреса сервера. Уривок перевірочного запуску з портом 18700 (типово 4600):

   ```text
   VITE v8.3.1  ready in 958 ms
   ➜  Local:   http://127.0.0.1:18700/
   ```

4. Відкрийте адресу в браузері. З'явиться сторінка «Jane — адмінка» з полем «Ключ API». Моки ключ не перевіряють — введіть будь-який непорожній рядок і натисніть «Увійти».

5. Очікуваний результат — сторінка «Огляд» із даними прикладів: одне джерело `shop-example`, завдання «Повний збір каталогу Shop Example», запуск у стані `running`, відкрита група проблем, витрати LLM `0.42 USD`, три виконавці (один `degraded`). Ліва панель веде на всі розділи.

## Інші порти

Порти задають змінні середовища: `JANE_ADMIN_PORT` — dev-сервер, `JANE_ADMIN_MOCK_PORT_BASE` — перший мок (решта — наступні шість портів). Обидва процеси мають отримати однакову `JANE_ADMIN_MOCK_PORT_BASE`. Опис змінних — [configuration.md](configuration.md#змінні-dev-сервера).

Bash (перевірено в Git Bash):

```bash
JANE_ADMIN_MOCK_PORT_BASE=18711 corepack pnpm --dir web/admin mocks
JANE_ADMIN_PORT=18700 JANE_ADMIN_MOCK_PORT_BASE=18711 corepack pnpm --dir web/admin dev
```

PowerShell (кожна команда — у своєму терміналі; не перевірено):

```powershell
$env:JANE_ADMIN_MOCK_PORT_BASE = "18711"; corepack pnpm --dir web/admin mocks
$env:JANE_ADMIN_PORT = "18700"; $env:JANE_ADMIN_MOCK_PORT_BASE = "18711"; corepack pnpm --dir web/admin dev
```

## Запуск проти стеку

Потрібен запущений dev-стек із reverse proxy — [Платформа з Admin UI](../../getting-started/platform.md). Адресу proxy і ключ адміністратора показує `just env` (`JANE_STACK_PROXY_URL`, `JANE_STACK_AUTH_ADMIN_API_KEY`). Не публікуйте ключ.

### Зібрана адмінка через proxy

Proxy dev-стеку віддає `web/admin/dist`, якщо каталог існував під час `just up`. Зберіть адмінку ([Збирання статики](#збирання-статики)) до старту стеку, відкрийте `JANE_STACK_PROXY_URL` і введіть ключ.

Перевірено на стеку `just up --project jane-doc-ui proxy orchestrator`:

- `/`, `/tasks/abc` (пряме посилання на сторінку) — `200`, відповідь містить заголовок `Content-Security-Policy`;
- `/config.json` — `Cache-Control: no-store`;
- `/api/orchestrator/v1/sources` без ключа — `401` з `"code":"unauthenticated"`, з ключем — `200`.

### Dev-сервер проти proxy

Dev-сервер передає весь `/api/*` на proxy без змін, якщо задано `JANE_ADMIN_API_TARGET`. Так зручно змінювати код адмінки й одразу бачити реальні дані.

Bash (перевірено: через dev-сервер `/api/orchestrator/v1/sources` з ключем — `200`, без ключа — `401`; неправильний ключ у браузері — банер «Сесія недійсна або прострочена (401)»):

```bash
JANE_ADMIN_API_TARGET=http://127.0.0.1:<порт proxy> corepack pnpm --dir web/admin dev
```

PowerShell (не перевірено):

```powershell
$env:JANE_ADMIN_API_TARGET = "http://127.0.0.1:<порт proxy>"; corepack pnpm --dir web/admin dev
```

### Один реальний сервіс замість мока

Змінна `JANE_ADMIN_TARGET_<API>` (наприклад `JANE_ADMIN_TARGET_LLM=http://127.0.0.1:8110`) замінює один мок базовою адресою сервісу; префікс `/api/<сервіс>` dev-сервер знімає. Інші API лишаються на моках. Не перевірено в цьому запуску.

## Збирання статики

```powershell
corepack pnpm --dir web/admin build
```

Уривок виводу:

```text
dist/index.html                     0.45 kB │ gzip:   0.31 kB
dist/assets/index-BfEMofkw.css     20.79 kB │ gzip:   4.87 kB
dist/assets/index-C49Qe8kp.js   1,408.57 kB │ gzip: 369.48 kB │ map: 5,398.30 kB
✓ built in 1.46s
```

Результат — каталог `web/admin/dist`. Його можна переглянути локально з тим самим proxy на моки або на стек:

```powershell
corepack pnpm --dir web/admin preview
```

Перевірено з `JANE_ADMIN_PORT=18701`: сторінка `/runs` і `/api/registry/v1/packages` на моках — `200`. Розгортання — [operations.md](operations.md#розгортання).

## Перевірки

```powershell
corepack pnpm --dir web/admin lint
corepack pnpm --dir web/admin typecheck
corepack pnpm --dir web/admin test
```

- `lint` — актуальність згенерованих типів (`gen-api --check`), ESLint без попереджень, Prettier;
- `typecheck` — `tsc` без виводу помилок;
- `test` — модульні тести Vitest. Уривок:

  ```text
   Test Files  12 passed (12)
        Tests  62 passed (62)
  ```

Браузерні тести Playwright на моках (збирають адмінку й піднімають моки самі; перший запуск — кілька хвилин):

```powershell
corepack pnpm --dir web/admin e2e -- --grep auth
```

```text
  ok 1 [chromium] › e2e\auth.spec.ts:5:3 › auth and navigation › unauthenticated users are sent to the login page (1.1s)
  ok 2 [chromium] › e2e\auth.spec.ts:11:3 › auth and navigation › the API key stays in sessionStorage, is sent as Bearer and is never displayed (20.2s)

  2 passed (5.0m)
```

Без `--grep` виконується весь набір. Проти стеку — `corepack pnpm --dir web/admin e2e:real <адреса proxy> --project <проєкт>`; підготовка виконавців стеку — `e2e:real:prepare <проєкт>`. Набір проти стеку в цій перевірці не запускався.

## Прибирання

- Зупиніть dev-сервер і моки через `Ctrl+C`. Стану на диску вони не лишають.
- Каталоги `web/admin/dist`, `web/admin/playwright-report`, `web/admin/test-results` і `web/admin/node_modules` — результати збирання й тестів поза Git; видаліть їх, якщо не потрібні.
- Стек зупиняйте за інструкцією [Платформа з Admin UI](../../getting-started/platform.md).
