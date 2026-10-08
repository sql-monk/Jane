# Розробка Jane

Короткий довідник для людей і агентів. Правила роботи — [CLAUDE.md](CLAUDE.md) і [plan.md](plan.md).
Відтворювані приклади (каталог, перевірка цін, Telegram) — [examples/README.md](examples/README.md);
експлуатація (незалежний і спільний запуск, ліміти, оновлення, резервування) — [docs/operations/](docs/operations/README.md).

## Встановлення

| Що | Версія | Як |
|---|---|---|
| uv | ≥ 0.12 | https://docs.astral.sh/uv/ — сам завантажить Python 3.12 (`.python-version`) |
| just | ≥ 1.40 | `uv tool install rust-just` (або без встановлення: `uvx --from rust-just just <рецепт>`) |
| Docker | Compose v2 | Docker Desktop (Windows) або Docker Engine (Linux) |
| gitleaks | ≥ 8.19 | https://github.com/gitleaks/gitleaks — для pre-commit і хука Claude Code |
| Node.js | 24 (`.node-version`) | лише для адмінки `web/admin`; pnpm — через `corepack enable` |

Далі: `uv sync --all-packages` і `just hooks` (git pre-commit із gitleaks).

## Команди

Усі рецепти `justfile` — один виклик `scripts/dev.py` (Python, stdlib), тож однаково працюють на Windows і Linux.
Без just: `uv run --no-project python scripts/dev.py <команда>`. Невідомі аргументи `check`, `unit`, `contract`,
`integration`, `isolation`, `test` передаються pytest без `--` (`just unit -v -k limits`).

| Команда | Що робить |
|---|---|
| `just check` | lint + types + unit + contract (+ web, якщо є `web/*`) — те саме, що CI |
| `just lint` / `just fmt` | ruff check + ruff format --check + лінтер контрактів / автовиправлення |
| `just types` | mypy (strict) для кожного члена workspace, `scripts/`, `infra/tests/` |
| `just unit` / `just contract` | тести без маркерів (+ офлайнові тести `examples/` і `deploy/profiles/` окремою сесією) / `@pytest.mark.contract` + лінтер `contracts/` |
| `just test <сервіс> [аргументи pytest]` | тести одного сервісу чи бібліотеки (`web-collector`, `jane-kit`, `testsite`) без `integration` |
| `just integration [--project <ім'я>]` | тести `@pytest.mark.integration` проти стеку цього checkout (або названого проєкту; потрібен `just up`) |
| `just isolation` | тести `@pytest.mark.isolation` (лише Linux; WP-06) |
| `just up [сервіси]` / `just down [-v]` | dev-стек з унікальним compose-проєктом, див. [infra/README.md](infra/README.md) |
| `just e2e [-v]` | наскрізні сценарії `tests/e2e/`; окремий compose-проєкт, автоматичне прибирання |
| `just env` / `just ps` / `just logs [сервіс]` | адреси й згенеровані облікові дані / стан / журнали стеку |
| `just new-service <ім'я>` | `services/<ім'я>/` із `templates/service/` + `uv lock` |
| `just testsite` | тестовий сайт на `http://127.0.0.1:8080` ([опис і очікувані URL](tests/fixtures/testsite/README.md)) |
| `just gen-client <openapi.yaml> <тека>` | клієнт і моделі з контракту (`jane-codegen`) |
| `just hooks` | встановити git pre-commit (gitleaks) |

## Монорепозиторій

- uv workspace, члени — за шаблонами `libs/*`, `services/*`, `templates/service`, `tests/fixtures/testsite`.
  Новий сервіс (`services/<ім'я>/pyproject.toml`) стає членом без змін кореневого `pyproject.toml`;
  `uv.lock` оновлює `uv lock` (його дозволено змінювати кожному WP).
- Залежність від спільної бібліотеки: `dependencies = ["jane-kit"]` + `[tool.uv.sources] jane-kit = { workspace = true }`.
- Маркери pytest: `contract`, `integration`, `isolation`; решта — unit. Тести кожного пакета — у його `tests/`
  (режим `--import-mode=importlib`, однакові імена файлів у різних пакетах дозволені).
- Згенерований код — у теках `_generated/` (ruff і mypy їх пропускають).
- Кінці рядків — LF (`.gitattributes`), кодування — UTF-8 (`.editorconfig`).

## CI

`.github/workflows/ci.yml`, Linux runner: `lint` (ruff, mypy, gitleaks) → `unit` → `contract`; паралельно
`web` (адмінка: install, lint, typecheck, test, build) та `isolation` (тести ізоляції пісочниці, plan.md §9);
`stack` — повний стек і інтеграційні тести, `adapters` — адаптери storage на SQL Server, MongoDB, MinIO, S3
(на `main`, PR і вручну); `e2e` — приймальні сценарії (на `main` і вручну); `limits` — вимірювання профілю `ci`
(лише вручну, `gh workflow run ci --ref <гілка>`).

## Хуки Claude Code

`.claude/settings.json`: захист шляхів WP і заборони (координатор), сканування секретів перед `git commit`
(`.claude/hooks/scan_secrets.py`), форматування змінених файлів (`.claude/hooks/format.py`: ruff для `.py`,
prettier для `web/**`, м'яко), нагадування про звіт. Дозволи: `uv`, `uvx`, `just`, `pytest`, `ruff`, `mypy`,
`pnpm`, `docker compose`, `gitleaks`, безпечні команди `git`; заборонено `git push` у `main` і force push.

## Вебзастосунки (`web/*`)

Адмінка — [`web/admin`](web/admin/README.md) (запуск на моках і на реальному стеку, команди, e2e). Спільна конфігурація:

- Кожен `web/<app>` — окремий pnpm-проєкт зі своїм `pnpm-lock.yaml` (корінь не є pnpm-workspace, тож WP-12
  не змінює кореневих файлів). pnpm фіксується полем `"packageManager": "pnpm@11.27.1"` у `package.json`.
- TypeScript: `"extends": "../../tsconfig.base.json"` ([tsconfig.base.json](tsconfig.base.json)).
- Prettier: конфігурація [`.prettierrc.json`](.prettierrc.json) у корені; prettier — devDependency застосунку.
- `just web` і CI запускають `pnpm install --frozen-lockfile` і скрипти `lint`, `typecheck`, `test`, `build` (якщо є).
- API-клієнти генеруються з `contracts/` у `src/api/generated/` (виключено з prettier).
