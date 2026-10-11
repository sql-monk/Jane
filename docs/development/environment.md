# Середовище розробки

Що встановити на Windows або Linux, щоб збирати, тестувати й запускати Jane. Версії нижче — ті, з якими працює CI (`.github/workflows/ci.yml`) і з якими перевірено цей розділ на Windows 11 (ревізія `48389a3`). На Linux кроки не перевірялися, окрім того, що CI виконує ті самі команди на `ubuntu-24.04`.

## Зміст

- [Інструменти](#інструменти)
- [Встановлення інструментів](#встановлення-інструментів)
- [Підготовка репозиторію](#підготовка-репозиторію)
- [Відмінності Windows і Linux](#відмінності-windows-і-linux)

## Інструменти

| Інструмент | Версія | Для чого | Обов'язковий |
|---|---|---|---|
| `uv` | 0.12.13 | Python, залежності workspace, запуск скриптів | так |
| Python | 3.12 (`.python-version`) | Усі пакети; uv завантажує сам | так (через uv) |
| `just` | 1.58.0 (пакет `rust-just`) | Рецепти `justfile` | так (або `uvx --from rust-just just …`) |
| `git` | — | Репозиторій, перевірка сумісності контрактів | так |
| Docker з Compose v2 | перевірено Docker 29.8.0, Compose v5.5.1 | `just up`, інтеграційні, e2e й ізоляційні тести, Handler Runtime | для стеку й тестів зі стеком |
| Node.js | 24 (`.node-version`), перевірено 24.19.0 | Admin UI, Redocly, Prism | для `just web` і Admin UI |
| `corepack` | з Node.js | Закріплений pnpm 11.27.1 (`packageManager` у `web/admin/package.json`) | для Admin UI |
| `gitleaks` | 8.30.1 | Пошук секретів у pre-commit і хуках | бажано |
| Chromium для Playwright | версія пакета з `uv.lock` | Тести `fetch.render_js` Web Collector | ні: без нього тести пропускаються локально |
| draw.io desktop | — | Експорт PNG діаграм (`scripts/docs_diagrams.py export`) | лише для експорту |

## Встановлення інструментів

Команди встановлення — з документації інструментів; у цьому розділі не виконувались (на машині перевірки `uv` встановлено через `winget`).

1. `uv` — за [інструкцією uv](https://docs.astral.sh/uv/getting-started/installation/), наприклад:

   PowerShell:

   ```powershell
   winget install --id astral-sh.uv -e
   ```

   Bash (Linux):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. `just` — через `uv`, однаково на обох ОС:

   ```powershell
   uv tool install "rust-just==1.58.0"
   ```

   Без встановлення рецепт запускається як `uvx --from rust-just just <рецепт>`.

3. Docker: Docker Desktop (Windows, WSL 2) або Docker Engine з плагіном Compose (Linux). Тести ізоляції Handler Runtime потребують Linux ([команди](checks.md#тести)).
4. Node.js 24 і pnpm:

   ```powershell
   corepack enable
   ```

   На Windows `corepack enable` може потребувати прав адміністратора; без нього використовуйте `corepack pnpm …`, як у рецептах.

5. Chromium для тестів рендерингу Web Collector (необов'язково):

   ```powershell
   uv run --package jane-web-collector playwright install chromium
   ```

   CI додає `--with-deps --only-shell` і ставить змінну `CI`, з якою відсутній Chromium — помилка, а не пропуск тесту.

## Підготовка репозиторію

1. Встановіть залежності всіх пакетів workspace (dev- та integration-групи типово):

   ```powershell
   uv sync --all-packages
   ```

   Членів workspace `uv` знаходить за шаблонами кореневого `pyproject.toml`: `contracts/python`, `libs/*`, `services/*`, `services/storage/adapters/*`, `templates/service`, `tests/fixtures/testsite`.

2. Перегляньте рецепти:

   ```powershell
   just --list
   ```

3. Встановіть git-хук пошуку секретів ([гігієна](hygiene.md)):

   ```powershell
   just hooks
   ```

4. Переконайтеся, що все зелене:

   ```powershell
   just check
   ```

   Підсумок наприкінці — таблиця кроків `lint`, `types`, `unit`, `contract`, `web` зі станом `ok` або `FAILED`.

5. Для Admin UI окремо: `corepack pnpm --dir web/admin install --frozen-lockfile` (інструкції — `web/admin/CLAUDE.md`).

## Відмінності Windows і Linux

- Рецепти `just` однакові: `justfile` не використовує оболонку, кожен рядок виконує `scripts/dev.py`.
- `just isolation` на Windows лише друкує `isolation tests run on Linux only (plan.md §9); skipped on win32` і завершується з кодом `0`.
- Змінні середовища: PowerShell — `$env:NAME = "value"`, Bash — `NAME=value команда`.
- Файли секретів `file:/run/secrets/...` — шлях Linux-контейнера; на Windows поза контейнером задавайте шлях усередині дозволеного каталогу сервісу.
