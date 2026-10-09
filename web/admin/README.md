# Jane — адмінка (`web/admin`)

Браузерний застосунок (TypeScript, React, Vite, pnpm) для всього, що вимагає ТЗ §10: джерела й стратегії обходу,
завдання, розклади, ланцюжки етапів, підключення, LLM, ліміти й бюджети; пакети обробників і правила колекторів,
форки й оновлення батька, редактор коду, diff, тести без запису, активація й відкат з аудитом; матеріали,
результати, помилки, прогрес, витрати, скасування, повторна обробка; сесії асистента й групи проблем.

Адмінка не має власного бекенду: вона звертається до API сервісів через reverse proxy
`<api_base>/<service>/v1/...` (ADR-0005). API-клієнти й типи **згенеровані з `contracts/`** — вручну не пишуться.

## Швидкий старт

```text
corepack enable
corepack pnpm install --frozen-lockfile
corepack pnpm mocks          # 7 контрактних моків (uv run contracts/tools/mock.py <api>), порти 4611..4617
corepack pnpm dev            # http://127.0.0.1:4600, Vite проксіює /api/<service> на моки
```

Проти реального стеку: `JANE_ADMIN_API_TARGET=http://127.0.0.1:<порт проксі з just env>` перед `pnpm dev`
(`/api/*` іде в reverse proxy Jane без змін). Гібрид — окремі сервіси замість моків:
`JANE_ADMIN_TARGET_LLM=http://127.0.0.1:8110`, `JANE_ADMIN_TARGET_STORAGE=...` (ключ — ім'я контракту
великими літерами: ORCHESTRATOR, REGISTRY, STORAGE, LLM, HANDLER, ASSISTANT, COLLECTOR).

## Команди

| Команда                       | Що робить                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| `pnpm lint`                   | свіжість згенерованих клієнтів (`gen-api --check`), eslint, prettier               |
| `pnpm typecheck`              | `tsc` (strict, `extends ../../tsconfig.base.json`)                                 |
| `pnpm test`                   | unit-тести vitest (дані сусідів — лише `contracts/examples`)                       |
| `pnpm gen:api`                | перегенерувати `src/api/generated/*` після зміни `contracts/`                      |
| `pnpm e2e`                    | Playwright на контрактних моках (браузер: `pnpm exec playwright install chromium`) |
| `pnpm e2e:real <url>`         | Playwright на реальному стеку через reverse proxy (див. «Режими e2e»)              |
| `pnpm e2e:real:prepare <id>`  | тестові зв'язки реальних сервісів в ізольованому Compose-проєкті                   |
| `pnpm e2e -- --grep @hybrid`  | сценарії проти окремих реальних сервісів (потрібні `JANE_ADMIN_TARGET_*`)          |
| `pnpm build` / `pnpm preview` | production-збірка в `dist/` і її перегляд з тим самим проксі                       |

`just web` і CI job `web` запускають `install --frozen-lockfile`, `lint`, `typecheck`, `test`, `build`.
Окремий CI job `web-mock-e2e` встановлює Chromium і виконує повний `pnpm e2e` на контрактних моках без Docker;
pnpm store, Chromium і uv кешуються, HTML-звіт та артефакти помилок зберігаються в Actions.

## Режими e2e

| Режим         | Як запустити                                                           | Що виконується                                                                                         |
| ------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Моки          | `pnpm e2e`                                                             | 26 сценаріїв `@mock` із контрактними прикладами, 2 auth, маскування помилки; `@hybrid` пропускаються   |
| Гібрид        | `JANE_ADMIN_TARGET_<API>=<url сервісу>` + `pnpm e2e -- --grep @hybrid` | реальні orchestrator, registry, handler-runtime, storage, LLM, assistant; сценарії самі засівають дані |
| Реальний стек | `pnpm e2e:real <url reverse proxy> --project <compose-project>`        | auth, маскування помилки, `@hybrid` проти `<url>/api/<service>`; `@mock` пропускаються                 |

Для повного прогону на локальному Compose-стеку спочатку зберіть UI та підніміть потрібні профілі:

```text
corepack pnpm --dir web/admin build
just up proxy storage registry handler-runtime web-collector orchestrator assistant llm --project jane-admin-real
corepack pnpm --dir web/admin e2e:real:prepare jane-admin-real
corepack pnpm --dir web/admin e2e:real http://127.0.0.1:<порт proxy з just env> --project jane-admin-real
```

`e2e:real` читає ключ адміністратора з `env.JANE_API_KEY_ADMIN` у
`.jane/stack-<compose-project>.json`, який генерує `just up`. Той самий ключ `just env` показує як
`JANE_STACK_AUTH_ADMIN_API_KEY`; його не потрібно копіювати в окрему змінну.
Без `--project` можна задати `JANE_STACK_FILE`; інакше wrapper шукає єдиний стек цього checkout з адресою
proxy, що збігається з переданим URL. Немає ключа, адреса не збігається або стек неоднозначний — запуск
зупиняється до Playwright. Значення `JANE_ADMIN_E2E_API_KEY` для real-режиму завжди береться зі стек-файлу;
wrapper не друкує ключ і не приймає незалежне значення цієї змінної як заміну.

`e2e:real:prepare` читає створений `just up` файл `.jane/stack-<id>.json` і тимчасовим Compose
override (лише для цього тестового проєкту, як `tests/e2e/compose.e2e.yaml`) задає: адреси реальних
виконавців orchestrator (виконавець `llm` — для пакетів `kind: llm`), адресу registry для handler-runtime,
web-collector і LLM-шлюзу, джерело runtime-профілю для registry, сусідів асистента (registry, orchestrator,
web-collector) і його псевдоніми моделей `e2e-admin-cheap` / `e2e-admin-strong`, а також том `storage-data`
у handler-runtime лише для читання з `JANE_HANDLER_RUNTIME_BLOB_ROOTS` — без нього повторна обробка RAW
адаптера files падає з `validation_failed` (ADR-0004: `file://` лише на одному вузлі зі спільним томом).
Файли `infra/` і секрети стеку він не змінює та не друкує.
Для Storage типовий dev-стек використовує `raw-files` + `jane.storage-files` і `results-pg` +
`jane.storage-postgresql`; нестандартні підключення/пакети задають
`JANE_ADMIN_E2E_STORAGE_CONNECTION`, `JANE_ADMIN_E2E_STORAGE_PACKAGE`,
`JANE_ADMIN_E2E_RESULTS_CONNECTION`, `JANE_ADMIN_E2E_RESULTS_PACKAGE`.
`JANE_ADMIN_E2E_SCHEMA_RETRIES` (типово `1`) задає `gateway.max_schema_retries` LLM у тестовому override;
задавайте однакове значення під час `e2e:real:prepare` і `e2e:real`. Сценарій невдалого LLM-елемента перевіряє
точну кількість викликів (успішна сторінка + невдала сторінка та її schema retries) і показане UI число запитів.

Гібридні сценарії для orchestrator і registry засівають унікальні джерела, завдання й пакети через реальні API.
Registry (WP-05) є в `main`: для справжнього прогону тестів пакета запустіть handler-runtime з
`JANE_HANDLER_RUNTIME_REGISTRY_URL=<url registry>`, далі задайте
`JANE_ADMIN_TARGET_HANDLER=<runtime> JANE_ADMIN_TARGET_REGISTRY=<registry>` і виконайте
`pnpm e2e -- --grep @hybrid`. `e2e/registry-standin.ts` лишається для ізольованої перевірки runtime:
його вмикає `JANE_ADMIN_E2E_REGISTRY_STANDIN_PORT`.

Режим реального стеку пропускає 26 сценаріїв `@mock`, прив'язаних до статичних прикладів контрактів.
Замість більшості з них `@hybrid` перевіряє реальний orchestrator (джерела, завдання, розклад, запуск у тестовому
режимі та скасування, ліміти, підключення й їх синхронізація, аудит), registry (публікація, погодження, форк,
правила, diff), handler-runtime із реальним registry (тести пакета), storage (RAW і результати), LLM та assistant;
`hybrid-m2-cycle` — збір testsite, trace, повторну обробку збереженого RAW з етапу й одного матеріалу, активацію
й відкат з аудитом; `hybrid-m2-problems` — групу проблем реального запуску, вдосконалення через асистента
(`unresolved`, нова версія, пропозиція типів даних), невідомі матеріали зі станом передачі в LLM і витрати LLM.
Зовнішню LLM замінює детермінований провайдер `fake` (WP-10): специфікації налаштовують його через API LLM
(підключення зі скриптованими `responses`, провайдер, псевдоніми; `e2e/llm-scripts.ts`).
Сценарій `problem-redaction.spec.ts` запускається в обох режимах і перевіряє помилку `problem+json` із секретом.
Що з `@mock` лишається лише на моках і чому — таблиця в `docs/delivery/WP-12.md` (розділ WP-12d).

## Конфігурація (`public/config.json`, замінюється при розгортанні без перезбірки)

| Параметр                                                               | Типово                                                                          | Опис                                                                                                     |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `api_base`                                                             | `/api`                                                                          | префікс reverse proxy (може бути абсолютним URL)                                                         |
| `services.<api>`                                                       | orchestrator, registry, storage, llm, handler-runtime, assistant, web-collector | ім'я сервісу в проксі                                                                                    |
| `auth.mode`                                                            | `api_key`                                                                       | `api_key` (dev: ключ у sessionStorage), `oidc` (Authorization Code + PKCE), `none` (лише локальні тести) |
| `auth.authority`, `auth.client_id`, `auth.scope`, `auth.redirect_path` | —, —, `openid profile`, `/auth/callback`                                        | для `oidc`                                                                                               |
| `polling.initial_ms` / `max_ms` / `multiplier`                         | 1000 / 15000 / 1.5                                                              | опитування job з backoff                                                                                 |
| `page_size`                                                            | 50                                                                              | `limit` списків (сервіс обрізає до свого максимуму)                                                      |
| `preview_max_bytes`                                                    | 262144                                                                          | скільки байтів збереженого матеріалу завантажувати для перегляду (HTTP Range)                            |

Змінні dev/e2e: `JANE_ADMIN_PORT` (4600), `JANE_ADMIN_MOCK_PORT_BASE` (4611), `JANE_ADMIN_API_TARGET`,
`JANE_ADMIN_TARGET_<API>`.

## Безпека

- Секрети ніде не відображаються: API містить лише посилання `env:`/`file:`/`vault:` і стан їх розв'язання.
  Додатковий захист (`redactSecrets`) застосовано не в клієнті API, а в точках показу: у `JsonView` (усі
  JSON-фрагменти відповідей — параметри, ліміти, діагностика, маніфести, деталі аудиту) і на екрані
  «Підключення» (таблиця, посилання на секрети, завантаження в редактор). Помилки API показують тільки локальний
  текст, відомий код контракту й числовий HTTP-статус: `title`, `detail`, `errors[].message`, `trace_id` і
  `details` не відображаються, бо навіть валідний `problem+json` може містити секрет. Централізовано в `unwrap` його свідомо
  не ввімкнено: інакше маски потрапляли б у форми конфігурацій і поверталися б у сервіс під час збереження.
  Скалярні поля в таблицях (назви, URL, статуси) показуються як є — за контрактом це не секрети.
  Тест `settings-secrets.spec.ts` перевіряє, що навіть «помилково» повернені сервісом значення не з'являються.
- Форма підключення приймає лише посилання на секрети; параметри з іменами на кшталт `password` відхиляються.
- Ключ API dev-режиму — лише в `sessionStorage`, передається як `Authorization: Bearer`, не потрапляє в URL,
  DOM чи `localStorage` (тести `auth.spec.ts`, `LoginPage.test.tsx`).
- Вміст матеріалів — дані: показується як текст, ніколи як HTML (`dangerouslySetInnerHTML` заборонено eslint).

## Структура

`src/api/generated` — типи з контрактів і JSON Schema (ajv валідує редактори конфігурацій);
`gen:api` також створює статичні Ajv-валідатори, щоб редактори працювали зі строгим CSP Caddy без `unsafe-eval`;
`src/api` — клієнти openapi-fetch, problem+json, job-опитування; `src/pages` — екрани; `src/components` —
редактори (CodeMirror), DAG, diff, звіти тестів; `e2e` — Playwright; `dev-proxy.ts` — проксі dev/e2e.
