# Гігієна репозиторію

Як Jane не дає закомітити секрети й вийти за межі свого WP: gitleaks, git-хук, хуки Claude Code і правила зберігання локальних облікових даних.

## Зміст

- [Секрети](#секрети)
- [gitleaks](#gitleaks)
- [Git-хук pre-commit](#git-хук-pre-commit)
- [Хуки Claude Code](#хуки-claude-code)
- [Дозволи агентів](#дозволи-агентів)

## Секрети

- Значення секретів ніколи не потрапляють у Git, API, пакети й журнали; конфігурації містять лише посилання `secret_refs` (`env:`, `file:`).
- Облікові дані dev-стеку генерує `just up` у `.jane/stack-<проєкт>.json`; живі ключі зовнішніх сервісів (наприклад, провайдера LLM) — у `.jane/secrets/`. Каталог `.jane/` — у `.gitignore`.
- Локальні доповнення стеку — `infra/compose.local.yaml` (поза Git).
- Тестові ключі в коді й прикладах — явно фіктивні значення.

## gitleaks

Правила — стандартний набір gitleaks, розширений [.gitleaks.toml](../../.gitleaks.toml) з вузькими обґрунтованими винятками (наприклад, `delivery_key` — шістнадцятковий ключ ідемпотентності в прикладах `contracts/`). Кожен виняток описано в самому файлі; винятків на цілий шлях чи правило немає.

Де працює gitleaks 8.30.1:

| Місце | Що сканує |
|---|---|
| CI job `lint` | Усю історію Git (`gitleaks git --redact`) в образі `ghcr.io/gitleaks/gitleaks` |
| Git-хук pre-commit | Застейджені зміни (`gitleaks git --pre-commit --staged --redact`) |
| Хук Claude Code `scan_secrets.py` | Застейджений і незастейджений diff відстежуваних файлів перед `git commit` агента |

## Git-хук pre-commit

```powershell
just hooks
```

Встановлює `pre-commit` у каталог хуків Git (`git rev-parse --git-path hooks`). Наявний чужий хук зберігається як `pre-commit.local`. Без встановленого gitleaks хук лише попереджає й не блокує коміт. Рецепт у межах цього розділу не запускався, щоб не змінювати хуки спільного репозиторію; встановлення хука в тимчасовий репозиторій і блокування секрету перевіряє `scripts/tests/test_dev.py` (`test_pre_commit_hook_blocks_secret`), хуки Claude Code — `scripts/tests/test_hooks.py`.

## Хуки Claude Code

Налаштовані в [.claude/settings.json](../../.claude/settings.json); код — `.claude/hooks/` (копії для Codex — `.codex/hooks/`). Усі запускаються через `uv run --no-project`.

| Хук | Подія | Що робить |
|---|---|---|
| `guard_paths.py` | Перед Edit/Write/NotebookEdit | Блокує запис поза шляхами WP, якщо в checkout є `.jane-wp` |
| `guard_bash.py` | Перед Bash/PowerShell | Завжди: force push, `docker compose down -v` без `-p`. У checkout виконавця: push у `main`, `git merge`, перемикання на `main`, зміна `.jane-wp` і карти шляхів |
| `scan_secrets.py` | Перед Bash/PowerShell | Перед `git commit` сканує diff gitleaks; знахідка блокує команду. Без gitleaks — попередження. Бюджет часу — `JANE_SECRET_SCAN_TIMEOUT_S` (типово 100 с) |
| `format.py` | Після Edit/Write | `*.py` — `ruff format` і `ruff check --fix`, решта зауважень повертається агенту; файли `web/` — `prettier --write`, якщо встановлено. Тайм-аут — `JANE_FORMAT_HOOK_TIMEOUT_S` (типово 20 с). Ніколи не блокує |
| `check_report.py` | Stop, SubagentStop | Один раз нагадує виконавцю про звіт `docs/delivery/WP-NN.md` з виводом команд |

## Дозволи агентів

`.claude/settings.json` дозволяє без підтвердження `uv`, `uvx`, `just`, `pytest`, `ruff`, `mypy`, `pnpm`, `docker compose`, `gitleaks` і безпечні команди git, а забороняє:

- читати `.env`, `.env.*` і будь-які `secrets/`;
- push у `main`/`master`, force push;
- видалення, перейменування й примусове переміщення гілок, `git update-ref`, `git fetch` із refspec.

Межі WP і процес — [процес WP](wp-process.md).
