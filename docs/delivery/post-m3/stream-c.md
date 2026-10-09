# Потік C: гігієна репозиторію й документація після M3

Координатор: Codex. Доручення: [stream-c-handoff.md](stream-c-handoff.md), спільні правила:
[README.md](README.md). Початкова база — `03a172d` від `origin/codex/jane-integration`, 2026-10-09.

Код і збірку виконують окремі субагенти у власних worktree на `wp/23<x>-<назва>`, `.jane-wp = 23`.
Кожен такий інкремент перевіряє незалежний wp-reviewer (не більше двох раундів), зміни `contracts/`
також перевіряє contract-guardian. Документальні зміни — без рецензента й тестів.

Checkout координатора для злиттів — `.claude/worktrees/integ-c`, detached HEAD, без `.jane-wp`.
Перед кожним злиттям: `git fetch origin`, `git pull --ff-only origin codex/jane-integration`,
`git merge --no-ff <гілка>` з повідомленням `merge: accept WP-23…`,
`git push origin HEAD:codex/jane-integration`. `integ-a`, `main` і force push не використовуються.

## Стан завдань

| Завдання | Гілка / worktree | Стан |
|---|---|---|
| C-1: CI й документація | `wp/23a-developer-docs`, `wp23a` | підготовлено; лише Markdown і коментар workflow |
| C-2: contracts/python у workspace | буде створено після приймання WP-19 | чекає маркера `merge: accept WP-19` в origin |
| C-3: формат Python-контрактів | `wp/23c-contracts-format`, `wp23c` | виконує окремий субагент |
| C-4: прибирання | `.jane/cleanup-post-m3.ps1` | останнім: після WP-19 і завершення потоку B |

## C-1: факти й перевірки

`DEVELOPMENT.md` і кореневий `README.md` описують aliases WP-18, закріплений образ oasdiff WP-21,
`JANE_OASDIFF_IMAGE`, списки асистента WP-15, спільний per-host лімітер Web Collector WP-16 і власні
ліміти `collector.shared_host_*`, storage `conflict_retries`, LLM `provider.request_timeout_ms`,
асистента `llm_call.request_timeout_ms`. У `contracts-compat` додано лише коментар про джерело образу.

Джерела: `contracts/tools/compat.py`, `services/{assistant,llm,web-collector,storage}/src/*/settings.py`,
`services/assistant/src/jane_assistant/app.py`, відповідні README, [WP-18](../WP-18.md), [WP-21](../WP-21.md).
Команди контрактів і конфігурація CI звірені з `justfile`, `scripts/dev.py`, `.github/workflows/ci.yml`.
Локальний повний `just check` і `just e2e` не запускаються за правилами потоків; повний CI буде один
раз після злиття C-2/C-3.

```text
$ перевірка локальних Markdown-посилань у README.md, DEVELOPMENT.md, stream-c.md
Local Markdown links: 29 checked, 0 missing
$ git diff --check
(порожній вивід, exit 0)
```

## Залежності й межі

На початковій перевірці маркер WP-19 відсутній; журнал потоку B `2366213` показує активні B-1…B-4
й очікування WP-19 для B-5. C-2 і C-4 до цих подій не починались.
Контейнери `puluj-g-*` не використовуються. Профілі `dev-laptop` і `single-node` виключено з обсягу.
Реальні зовнішні LLM/IdP/AWS/Telegram без доступу — не перевірено на реальному сервісі.
