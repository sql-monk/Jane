# CI

Конвеєр GitHub Actions [.github/workflows/ci.yml](../../.github/workflows/ci.yml): які job є, від чого залежать, коли запускаються і як відтворити кожен локально.

## Зміст

- [Коли запускається](#коли-запускається)
- [Конвеєр](#конвеєр)
- [Job](#job)
- [Відтворення локально](#відтворення-локально)

## Коли запускається

- `push` у `main` і в гілки `wp/**`;
- кожен `pull_request`;
- вручну (`workflow_dispatch`).

Новий запуск для тієї самої ревізії скасовує попередній (`concurrency: ci-<ref>`, `cancel-in-progress`). Права — лише `contents: read`. Версії інструментів закріплено змінними: `UV_VERSION=0.12.13`, `JUST_VERSION=1.58.0`, `GITLEAKS_VERSION=8.30.1`. Усі job — на `ubuntu-24.04`, з `uv sync --all-packages --locked` (крім `web` і `contracts-compat`).

## Конвеєр

![Залежності job CI та умови їх запуску](../diagrams/development/ci-pipeline.light.png#gh-light-mode-only)
![Залежності job CI та умови їх запуску](../diagrams/development/ci-pipeline.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/development/ci-pipeline.light.png), [темне](../diagrams/development/ci-pipeline.dark.png); джерело — [ci-pipeline.drawio](../diagrams/development/ci-pipeline.drawio).

Стрілка — залежність `needs`: наступний job стартує лише після успіху попереднього. Падіння `lint` зупиняє весь ланцюжок, окрім `contracts-compat`, який незалежний.

## Job

| Job | Залежить від | Умова | Що виконує |
|---|---|---|---|
| `lint` | — | завжди | `just lint`, `just types`, gitleaks по всій історії Git (`fetch-depth: 0`) |
| `unit` | `lint` | завжди | Playwright Chromium, `just unit` |
| `contract` | `unit` | завжди | `just contract` з `JANE_CONTRACTS_REDOCLY=1` (Redocly обов'язковий) |
| `contracts-compat` | — | завжди | `just contracts-compat <base> --oasdiff` |
| `web` | `lint` | завжди | `scripts/dev.py web`: pnpm install, lint, typecheck, test, build Admin UI |
| `web-mock-e2e` | `lint` | завжди | Playwright-регресія Admin UI на моках контрактів (`pnpm e2e`), артефакт звіту |
| `isolation` | `unit` | завжди | `just isolation` |
| `stack` | `contract` | PR, вручну, push у `main` | `just up`, `just integration`, журнали за падіння, `just down -v` |
| `adapters` | `contract` | PR, вручну, push у `main` | Матриця `sqlserver`, `mongodb`, `minio`, `s3`: `just up <адаптер>`, інтеграційні тести адаптера, `just down -v` |
| `e2e` | `contract` | вручну, push у `main` | `just e2e -v` з `JANE_E2E_REQUIRED=1` (пропуск сценарію — помилка) |
| `limits` | `contract` | лише вручну | Вимірювання профілю лімітів `ci` (`deploy/profiles/harness/limits_harness.py`), артефакт `.jane/limits/` |

Базова ревізія `contracts-compat`: для PR — `origin/<base_ref>`; для push у `main` — попередній стан `main` (`github.event.before`); інакше — `git merge-base origin/main HEAD`.

Кожен job зі стеком задає власний `JANE_COMPOSE_PROJECT` (`jane-ci-<run_id>-<attempt>`, `jane-adapter-…`, `jane-e2e-…`), тож паралельні job не ділять контейнери й томи.

## Відтворення локально

| Job | Локальна команда |
|---|---|
| `lint` | `just lint`, `just types`; gitleaks — `gitleaks git --redact` ([гігієна](hygiene.md)) |
| `unit`, `contract`, `web` | `just check` (виконує всі три разом із `lint` і `types`) |
| `contracts-compat` | `just contracts-compat main --oasdiff` |
| `isolation` | `just isolation` (лише Linux) |
| `stack` | `just up`, `just integration`, `just down -v` |
| `adapters` | `just up sqlserver`, `just integration services/storage/adapters/sqlserver/tests -v`, `just down -v` |
| `e2e` | `just e2e -v` |
| `web-mock-e2e` | `corepack pnpm --dir web/admin e2e` |

Локальний `just contract` без `JANE_CONTRACTS_REDOCLY=1` пропускає Redocly — CI може впасти на тому, що локально пройшло: перевірте `just contracts-check --redocly` з Node.js.
