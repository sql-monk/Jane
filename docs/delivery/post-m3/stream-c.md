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
| C-1: CI й документація | `wp/23a-developer-docs`, `wp23a` | прийнято й запушено, merge `a5b1563` |
| C-2: contracts/python у workspace | буде створено після приймання WP-19 | чекає маркера `merge: accept WP-19` в origin |
| C-3: формат Python-контрактів | `wp/23c-contracts-format`, `wp23c` | прийнято й запушено, merge `0dc2ded` |
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
$ python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
WP-23: 4 changed file(s), 0 outside ownership
$ git merge --no-ff wp/23a-developer-docs -m 'merge: accept WP-23a developer documentation [skip ci]'
Merge made by the 'ort' strategy.
4 files changed, 88 insertions(+), 2 deletions(-)
$ git push origin HEAD:codex/jane-integration
2366213..a5b1563  HEAD -> codex/jane-integration
```

## C-3: форматування Python-контрактів

Виконавець — субагент `c3_format`; фінальний SHA — `f80ddce606eb0ead0092573fef59fe70d4bc4bbd`,
код — `d5232ce`. Незалежний `c3_review`: **accepted**, один раунд;
`c3_contract`: **accepted / compatible**. Звіт — [c3-format.md](../WP-23/c3-format.md).
Після `pull --ff-only` merge `0dc2ded` запушено в `origin/codex/jane-integration`.

`contracts/` виключено з загального ruff; додавання явного `contracts/python` до format-команд
`lint` і `fmt` охоплює всі три Python-файли. У `storage_adapter.py` лише перенесено сигнатуру
`commit_entity`: AST, включно з docstrings, рівний `main`, базі інкременту й інтеграції.

```text
$ uvx --from rust-just just lint
All checks passed!
466 files already formatted
All contract checks passed.
exit=0
$ uv run --all-packages pytest scripts/tests/test_dev.py -q
31 passed in 12.68s
exit=0
$ незалежний прогін scripts/tests/test_dev.py
31 passed in 47.37s
exit=0
$ uv run --script contracts/tools/check_contracts.py --require-redocly
[ok] Redocly lint: ok (Woohoo! Your API descriptions are valid. 🎉)
All contract checks passed.
exit=0
$ uv run --script contracts/tools/compat.py --base main --oasdiff
[усі 7 API: ok; No changes detected]
0 breaking, 0 warning(s).
exit=0
$ python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
WP-23: 3 changed file(s), 0 outside ownership
exit=0
```

Сирі докази — `.jane/wp23c-*.txt` у `wp23c`; цільові перевірки й підсумки включено у Git-звіт.
Push C-3 запустив автоматичний CI [37912943507](https://github.com/sql-monk/Jane/actions/runs/37912943507)
на `b4f966b` (код той самий, фінальний `f80ddce` змінює лише звіт). Повний dispatch потоку C
відкладено до закриття C-2, щоб виконати його один раз після всіх змін коду/збірки.

## Залежності й межі

На початковій перевірці маркер WP-19 відсутній; журнал потоку B `2366213` показує активні B-1…B-4
й очікування WP-19 для B-5. C-2 і C-4 до цих подій не починались.
Контейнери `puluj-g-*` не використовуються. Профілі `dev-laptop` і `single-node` виключено з обсягу.
Реальні зовнішні LLM/IdP/AWS/Telegram без доступу — не перевірено на реальному сервісі.
