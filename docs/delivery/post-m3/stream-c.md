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
| C-2: contracts/python у workspace | `wp/23b-contracts-workspace`, `wp23b` | active після WP-19 `ee78fc5`; окремий виконавець |
| C-3: формат Python-контрактів | `wp/23c-contracts-format`, `wp23c` | прийнято й запушено, merge `0dc2ded` |
| C-4: прибирання | `.jane/cleanup-post-m3.ps1` | останнім: після WP-19, завершення B і фінального CI C |

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
на `b4f966b` (код той самий, фінальний `f80ddce` змінює лише звіт). Результат — **success**:
`contracts-compat`, `lint`, `unit`, `web-mock-e2e`, `web`, `isolation`, `contract` — success;
`stack`, `adapters`, `e2e`, `limits` — skipped за правилами push. Повний dispatch потоку C
відкладено до закриття C-2, щоб виконати його один раз після всіх змін коду/збірки.

## Залежності й межі

На початковій перевірці маркер WP-19 відсутній; журнал потоку B `2366213` показує активні B-1…B-4
й очікування WP-19 для B-5. C-2 і C-4 до цих подій не починались.
Контейнери `puluj-g-*` не використовуються. Профілі `dev-laptop` і `single-node` виключено з обсягу.
Реальні зовнішні LLM/IdP/AWS/Telegram без доступу — не перевірено на реальному сервісі.

## Автоматичне продовження C-2 / C-4

Знімок перед продовженням, 2026-10-09 13:41: fetch на `c9f3c81` не містив маркера `merge: accept WP-19`. Попередній
координатор A передав незавершений WP-19 наступному координатору — [handoff A](stream-a-handoff.md).
Потік B прийняв B-1…B-4 і оновлення матриці, але B-5 та фінальний CI ще чекають WP-19.
**C-2 не розпочато; C-4 не розпочато; cleanup script не змінювався, dry-run / -Apply не виконувались.**
Повний `workflow_dispatch` потоку C: **count 0**.

У цьому самому чаті створено heartbeat **Jane C після WP-19 і потоку B**,
id `jane-c-wp-19-b`, **ACTIVE**, перевірка кожні 5 хвилин. Створення підтверджено
`automation_update`, перегляд відкрив картку; локальна конфігурація підтверджує ACTIVE і поточний
thread `01a11ff4-80de-7d33-8aed-c1b486b53404`. Незмінний стан не повідомляється.

Продовження збережено в prompt автоматизації:

1. Після маркера WP-19 координатор додає до WP-23 лише відсутній шлях
   `services/storage/adapters/*/pyproject.toml` у `.claude/wp-paths.json` (його також читає `.Codex`).
   Далі окремий виконавець у свіжому `wp23b`, `.jane-wp = 23`, виконує C-2;
   звіт — `docs/delivery/WP-23/c2-workspace.md`. Gates: `uv lock --check`,
   `uv sync --all-packages --locked`, `just types`, `just lint`, `just contract`; незалежне рев'ю ≤2 раунди.
   У разі непропорційного ризику — документоване рішення лишити path-залежність, як дозволяє handoff.
2. Після злиття C-2 — один повний CI в integration; перед dispatch перевірити записаний intent/run ID,
   щоб не створити дубліката. Записати точний SHA, URL і actual verdict, дочекавшись завершення.
3. C-4 виконати останнім після завершення B і CI C. Код скрипта за потреби змінює окремий виконавець
   у власному `wp23d`, з незалежним review перед застосуванням; ignored script лишається поза Git.
   Захистити активні checkout/refs A/B/C; незлиті refs архівувати точними тегами зі збереженням
   local/remote колізій, перевіряти push тегів до видалення. Dirty / незлиті worktree лишити.
   Перед рекурсивною операцією перевірити absolute target у workspace; лише native PowerShell.
   `.jane` зберегти до видалення; координатор перевіряє dry-run перед `-Apply`, записує числа у журнал.
4. Коли C-1…C-4 фактично закриті та фінальний CI success — фінальний журнал і одне речення людині,
   вимкнути лише heartbeat потоку C. `main`, force push і чужі автоматизації не змінювати.

Checkout `integ-c`, `wp23a`, `wp23c` залишаються доступними; C-1/C-3 та їхні перевірки не повторювати.

## C-2: старт після приймання WP-19

2026-10-09 16:04: свіжий fetch підтвердив маркер `ee78fc5 merge: accept WP-19 shared stores and files
ContentRef transit`, вершина integration — `2d4a101`. Гейт C-2 відкрито; cleanup C-4 досі не починався.
Координатор додав до карти WP-23 точний відсутній шлях `services/storage/adapters/*/pyproject.toml`.
Виконавець отримує окремий checkout `wp23b` від свіжої integration, `.jane-wp = 23` і звіт
`docs/delivery/WP-23/c2-workspace.md`; незалежне рев'ю та required checks лишаються обов'язковими.
Фінальний CI C ще не запускався (dispatch count 0); після злиття C-2 він буде запущений один раз.

### Черга фінального CI

У `.github/workflows/ci.yml` concurrency group — `ci-${{ github.ref }}`, `cancel-in-progress: true`.
Окремі dispatch B/C на `codex/jane-integration` скасували б попередній run. Тому після приймання C-2
фінальний dispatch C чекатиме завершення фінального CI B; C не створює нового run, поки B працює.
Він перевірить свіжий integration SHA з усіма змінами C-2/C-3. A за своїм handoff запускає підсумковий
CI після завершення B/C. Це зберігає один повний dispatch C і не змінює workflow чи обсяг перевірок.
