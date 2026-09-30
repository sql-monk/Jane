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
| `pnpm e2e -- --grep @hybrid`  | сценарії проти окремих реальних сервісів (потрібні `JANE_ADMIN_TARGET_*`)          |
| `pnpm build` / `pnpm preview` | production-збірка в `dist/` і її перегляд з тим самим проксі                       |

`just web` і CI job `web` запускають `install --frozen-lockfile`, `lint`, `typecheck`, `test`.

## Режими e2e

| Режим         | Як запустити                                                                    | Що виконується                                                                                                                                                                                                                                                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Моки          | `pnpm e2e`                                                                      | усі сценарії `@mock` (дані — приклади контрактів) + `auth.spec.ts`; `@hybrid` пропускаються                                                                                                                                                                                                                                                                            |
| Гібрид        | `JANE_ADMIN_TARGET_<API>=<url сервісу>` + `pnpm e2e -- --grep @hybrid`          | сценарії, що самі засівають дані через API реального сервісу: llm (провайдери, бюджети, витрати), assistant (підключення джерела), storage (матеріали, вміст як текст, сутності, запізнілі поля; `JANE_ADMIN_E2E_STORAGE_CONNECTION` — filesystem-підключення, типово `e2e-files`), handler-runtime (тести пакета в пісочниці; потрібен замінник registry, див. нижче) |
| Реальний стек | `pnpm e2e:real <url reverse proxy>` (`JANE_ADMIN_E2E_API_KEY` — справжній ключ) | `auth.spec.ts` + гібридні сценарії llm, assistant, storage (адреси сервісів — `<url>/api/<service>`); сценарії `@mock` пропускаються, бо перевіряють конкретні дані прикладів контрактів                                                                                                                                                                               |

Гібрид handler-runtime: registry (WP-05) ще немає, тож `e2e/registry-standin.ts` віддає один справжній пакет
(`libs/extractor-sdk/examples/testsite-product-extractor`, маніфест перевіряється схемою контракту) за операціями
читання registry.v1. Запуск: runtime з `JANE_HANDLER_RUNTIME_REGISTRY_URL=http://127.0.0.1:4695`, далі
`JANE_ADMIN_TARGET_HANDLER=<runtime> JANE_ADMIN_TARGET_REGISTRY=http://127.0.0.1:4695
JANE_ADMIN_E2E_REGISTRY_STANDIN_PORT=4695 pnpm e2e -- --grep @hybrid`.

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
  JSON-фрагменти відповідей — параметри, ліміти, діагностика, маніфести, деталі аудиту й помилок) і на екрані
  «Підключення» (таблиця, посилання на секрети, завантаження в редактор). Централізовано в `unwrap` його свідомо
  не ввімкнено: інакше маски потрапляли б у форми конфігурацій і поверталися б у сервіс під час збереження.
  Скалярні поля в таблицях (назви, URL, статуси) показуються як є — за контрактом це не секрети.
  Тест `settings-secrets.spec.ts` перевіряє, що навіть «помилково» повернені сервісом значення не з'являються.
- Форма підключення приймає лише посилання на секрети; параметри з іменами на кшталт `password` відхиляються.
- Ключ API dev-режиму — лише в `sessionStorage`, передається як `Authorization: Bearer`, не потрапляє в URL,
  DOM чи `localStorage` (тести `auth.spec.ts`, `LoginPage.test.tsx`).
- Вміст матеріалів — дані: показується як текст, ніколи як HTML (`dangerouslySetInnerHTML` заборонено eslint).

## Структура

`src/api/generated` — типи з контрактів і JSON Schema (ajv валідує редактори конфігурацій);
`src/api` — клієнти openapi-fetch, problem+json, job-опитування; `src/pages` — екрани; `src/components` —
редактори (CodeMirror), DAG, diff, звіти тестів; `e2e` — Playwright; `dev-proxy.ts` — проксі dev/e2e.
