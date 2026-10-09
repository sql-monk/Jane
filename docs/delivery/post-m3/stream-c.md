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
| C-2: contracts/python у workspace | `wp/23b-contracts-workspace`, `wp23b` | прийнято й запушено, merge `fdad210`; фінальний CI success |
| C-3: формат Python-контрактів | `wp/23c-contracts-format`, `wp23c` | прийнято й запушено, merge `0dc2ded` |
| C-4: прибирання | `wp/23d-cleanup-safety`, `wp23d` | active: окремий виконавець готує ignored копію; review / Apply ще не було |

Поточний фінальний CI C: **dispatch count 1**, run **37942655574**, SHA `133bb5a`; **success, 14/14 jobs**.
C-4 виконується. Нижчі записи count 0 / C-4 not_started — історичні знімки до поточного стану.

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

## C-2: accepted і злито

Автор `c2_workspace`: код `3a70b939f8ca34321e2a369f0b86a839ee1a820e`, остаточний звіт/HEAD
`22f83662efaac0a64a91a2bc9078b0bcec04a793`, чистий checkout `wp23b`, гілка запушена.
Незалежний `c3_review` / wp-reviewer: **accepted**, раунд 1, для точного остаточного SHA.
Після fresh fetch та `pull --ff-only` прийняте злиття
`fdad2106c0fb6531639d1071d720a990a646b0b7` запушено в `codex/jane-integration`.
Звіт із командами й обмеженнями — [c2-workspace.md](../WP-23/c2-workspace.md).

`contracts/python` — 19-й член uv workspace; кореневе джерело
`jane-contracts = { workspace = true }` успадковують усі вісім споживачів.
Їхні локальні path-overrides вилучено. `members()` читає root manifest, mypy реально включає
три файли Protocol-пакета. Версії та sources 109 зовнішніх пакетів незмінні.
Вкладені адаптери не підтримують локальне workspace-джерело в uv 0.12.13; перевірене root inheritance
обходить цю особливість без повернення jane-contracts до path-залежності.

Справжні підсумки автора:

```text
uv lock --check: Resolved 109 packages; exit=0
uv sync --all-packages --locked: 19 local packages; exit=0
just types: 22 mypy sessions, 370 files; Protocol: 3 source files; exit=0
just lint: All checks passed; 484 files already formatted; exit=0
JANE_CONTRACTS_REDOCLY=1 just contract: Redocly ok; 109 passed, 3 skipped, 1 warning; exit=0
pytest scripts/tests/test_dev.py: 32 passed; exit=0
check-diff: 14 changed file(s), 0 outside ownership; exit=0
```

Рецензент незалежно виконав lock/check, locked sync, 32 dev-тести, mypy трьох Protocol-файлів,
lint та ownership; усе exit 0. Він звірив фактичні Linux Docker build/import журнали
storage, web-collector та llm: три збірки й три перевірки exit 0; storage містить точні шість
adapter entry points, Protocol імпортується із site-packages. Dockerfile не змінені.
`contracts/` не змінено, окремий contract-guardian не потрібен. Локальні full check/e2e не запускались.
Сирі докази — `.jane/wp23b-*.txt` у `wp23b`; тимчасові Docker tags автора прибрано.

Три contract skips: два потребують PostgreSQL dev-stack LLM, третій — контракту template service;
наявний FastAPI warning `Duplicate Operation ID cancelJob` не приховано. Docker перевірено на трьох
класах контексту, повний integration gate лишається CI. Зовнішні LLM/IdP/AWS/Telegram —
не перевірено на реальному сервісі; профілі dev-laptop/single-node виключені.

Запит власнику storage / WP-19: `services/storage/README.md:253` у рецепті нового адаптера має
застарілий `jane-contracts = { path = "../../../../contracts/python", editable = true }`.
Прибрати лише цей override, послатися на root source inheritance у DEVELOPMENT; path-джерело
jane-storage зберегти. Чужий README не редагувався. Рецензент визнав це зовнішньою документальною
дією, яка не блокує C-2 з явним запитом; копіювання старого рядка поверне workspace/path conflict.

Branch CI [37936808211](https://github.com/sql-monk/Jane/actions/runs/37936808211)
на `22f83662efaac0a64a91a2bc9078b0bcec04a793` ще in_progress при прийманні;
contracts-compat/lint/web — success, unit/web-mock-e2e тривають. Це push CI, не фінальний dispatch.
Потік B уже злив B-5 як `f0fde81` і записав intent свого фінального CI; C чекає його actual success.
**Повний dispatch C: count 0; C-4 не починався, людський cleanup script не змінено й не виконано.**

### C-2: завершення branch CI — failure

2026-10-09 16:37 (Київ): actual `gh run view` для
[37936808211](https://github.com/sql-monk/Jane/actions/runs/37936808211), точний SHA
`22f83662efaac0a64a91a2bc9078b0bcec04a793`: **completed / failure**.
contracts-compat, lint, web, web-mock-e2e — success; unit — failure;
isolation, stack, contract, limits, adapters, e2e — skipped після падіння unit.
Журнал невдалого job збережено в ignored `.jane/wp23b-branch-ci-failed.txt` checkout `integ-c`.

```text
FAILED services/telegram-collector/tests/test_processes.py::test_two_instances_share_state_and_take_over_after_kill
AssertionError: condition not reached
status=running; paused_by_backpressure=True
emitted=11; acknowledged=1; unacked=10; max_unacked_materials=10
1 failed, 1136 passed, 5 skipped, 417 deselected, 33 warnings in 317.71s
examples/deploy offline unit session: 93 passed, 3 warnings in 15.48s
recipe unit: exit=1
```

Запит власнику Telegram Collector (WP-04 / власнику `services/telegram-collector/**`):
усунути залежність тесту `test_processes.py:196` від розміру першої сторінки materials.
Фактичний log містить наступний GET з `after=c_0000000000000001`: перша сторінка мала одну
матеріальну одиницю. Тест після двох GET припиняє ACK і чекає `emitted >= 12`, хоча ACK=1 та
queue=10 дозволяють рівно 11. Це пояснює зафіксований стан backpressure; робочий діагноз —
гонка тестового споживача, а не доведений дефект packaging C-2. Власнику потрібна зміна споживання
сторінок/ACK із збереженням перевірок shared state, kill/takeover та exactly-once; не послаблювати
assertions і не збільшувати timeout як заміну виправленню.

Readonly `git diff bb1982b 22f8366 -- services/telegram-collector libs/jane-kit contracts/python`
порожній; Telegram Collector не залежить від jane-contracts. Фінальний CI B
[37937013460](https://github.com/sql-monk/Jane/actions/runs/37937013460) на
`bb1982b9f6b1e2593fb2f1ab60a436e6945f15b1` уже має unit/contract/isolation success,
але stack/limits/e2e ще працюють. У C немає власності на цей тест: чужий код не редагувався,
запит передано через цей журнал; інший чат не повідомлявся.

Branch CI не названо зеленим. Прийняте незалежним review злиття C-2 збережено; фінальне закриття
коду C-2/C-3 чекає окремого точного integration CI. Повний C dispatch досі 0, не дубльовано
ні branch run, ні B final run; локальні повні набори та успішні targeted gates не повторювались.

### Запит C-2 до storage — виконано власником

2026-10-09 16:42 (Київ): origin підтвердив accepted WP-19a — авторський документальний коміт
`251419212656ca867221f9373e97ae749739fa76`, merge
`f4c62bbd9774203e6eeff9de4aab2ca81ce4dd37`, запис A `cb7434b`.
У `services/storage/README.md` власник вилучив саме jane-contracts path-override,
додав root workspace inheritance та посилання на DEVELOPMENT; jane-storage path source збережено.
Звіт — [workspace-doc-followup.md](../WP-19/workspace-doc-followup.md).
Readonly diff звірено: лише README і звіт; додаткові тести/review для документів не потрібні.
Цей документальний запит закрито. Telegram CI owner request лишається відкритим;
фінальний B run ще виконує e2e, C dispatch count 0, cleanup C-4 не починався.

## Фінальний CI B успішний; C очікує прийнятого Telegram follow-up

2026-10-09 17:02 (Київ): actual `gh run view`
[37937013460](https://github.com/sql-monk/Jane/actions/runs/37937013460) для точного
`bb1982b9f6b1e2593fb2f1ab60a436e6945f15b1`: **completed / success**, усі 14 jobs.
contracts-compat, lint, unit, web, web-mock-e2e, contract, isolation, stack, limits, e2e,
adapters mongodb/s3/sqlserver/minio — success. Повні метадані й steps збережено в
`.jane/stream-b-final-ci-37937013460.json` checkout `integ-c`.
Origin-журнал B підтверджує accepted B-1…B-5; цей SHA передує C-2 і не підміняє потрібного CI C.
Повний real22 браузерний набір workflow не запускає; його проходження тут не заявляється.

Власник A взяв Telegram CI-запит у WP-19b: code `2e68cf7`, звіт/HEAD
`b29a0406645c6b846211cade14a2a5d9ae697e76`; old-fail/new-pass відтворення вже є,
але незалежне review та branch CI ще тривають, прийнятого злиття немає.
Origin `50f5e23` містить запит перевірити виправлення єдиним фінальним CI C.
Щоб цей run перевірив усунення відомої гонки, C чекає accepted WP-19b в integration;
свої успішні перевірки та чуже review не повторює. Код C-2/C-3 уже є у свіжій integration,
що підтверджено ancestry-перевіркою.

**Фінальний C dispatch count 0, intent/run ID ще не створено.** Перед майбутнім dispatch
перевірити свіжі journal/state/gh runs, зафіксувати expected SHA й intent, потім виконати лише один run.
C-4 чекає цього CI success; людський cleanup script лишається незміненим, -Apply не виконувався.

## WP-19b прийнято; єдиний фінальний CI C запущено

2026-10-09 17:12–17:14 (Київ): fresh origin містить
`88ec1682ec4f7b2a0e6c13745707ddc73ad16122 merge: accept WP-19b Telegram short-page test consumer`.
Origin status `133bb5a` підтверджує незалежне accepted R1 нового інкремента та old-fail/new-pass
відтворення, threshold=12, timeout=20, queue=10, exactly-once=80 збережено.
Actual [branch CI 37940359810](https://github.com/sql-monk/Jane/actions/runs/37940359810)
на `b29a0406645c6b846211cade14a2a5d9ae697e76` — completed/success, 7 jobs success,
4 skipped за правилами push. Telegram owner request C-2 закрито цим прийнятим інкрементом.
B за origin `cbe8653` фактично завершений; final CI 14/14, API e2e 79 passed.
Чужі успішні тести/review не повторювались.

Перед dispatch перевірено origin-журнал C та ignored `.jane/stream-c-state.json`: count 0,
`.jane/stream-c-full-ci.json` відсутній. Actual gh list показав лише B final run 37937013460
і старі M3 runs. Після `pull --ff-only` HEAD та origin integration —
`133bb5a0604ccbc3ce41a820216d4751f301a47b`, detached HEAD без `.jane-wp`;
ancestry C-2 `fdad210`, C-3 `0dc2ded`, WP-19b `88ec168` перевірено.

Intent **2026-10-09T14:13:49.1497106Z**, expected SHA
`133bb5a0604ccbc3ce41a820216d4751f301a47b`, dispatch count 1 та attempts 0 збережено
в `.jane/stream-c-full-ci.json` **до** виклику; attempts 1 записано перед мережею.

```text
$ gh workflow run ci --ref codex/jane-integration --repo sql-monk/Jane
https://github.com/sql-monk/Jane/actions/runs/37942655574
exit=0
$ gh run view 37942655574 --repo sql-monk/Jane --json status,conclusion,headSha,event,url,createdAt,jobs
status=in_progress; conclusion=""; event=workflow_dispatch
headSha=133bb5a0604ccbc3ce41a820216d4751f301a47b
createdAt=2026-10-09T14:14:08Z
```

Фінальний run — [37942655574](https://github.com/sql-monk/Jane/actions/runs/37942655574);
actual SHA рівний expected SHA. ID/URL, dispatch exit/time та метадані записано у власний ignored стан;
сирий вивід — `.jane/stream-c-full-ci-dispatch.txt`, JSON — `.jane/stream-c-full-ci-37942655574.json`.
**Це один фінальний dispatch C, verdict ще не отримано.** Продовжувати саме цей run;
невідомий результат спершу шукати в gh, жодного дублюючого dispatch.
Локальні full check/e2e не запускались. C-4 і застосування cleanup — лише після actual success цього run.

## Фінальний CI C — success; C-4 відкрито

2026-10-09 17:52 (Київ): actual `gh run view`
[37942655574](https://github.com/sql-monk/Jane/actions/runs/37942655574) для точного SHA
`133bb5a0604ccbc3ce41a820216d4751f301a47b`: **completed / success**, завершено
`2026-10-09T14:48:22Z`. Усі 14 jobs success, жодного повторного dispatch/rerun.
Повний JSON зі steps — `.jane/stream-c-full-ci-37942655574.json`; actual log —
`.jane/stream-c-final-ci-log.txt` у `integ-c`.

| Job | Фактичний підсумок | Job ID |
|---|---|---|
| lint | success; Ruff pass, 484 formatted, 22 mypy sessions включно з Protocol 3 files | 113860750407 |
| contracts-compat | success; oasdiff 0 breaking, 0 warnings | 113860750736 |
| unit | success; 1137 passed / 5 skipped, offline examples/profiles 93 passed | 113861103865 |
| web | success; lint/typecheck/build, 11 test files / 58 tests passed | 113861103879 |
| web-mock-e2e | success; 38 passed / 19 skipped | 113861103864 |
| contract | success; 109 passed / 3 skipped | 113863733795 |
| isolation | success; 7 passed | 113863733908 |
| stack | success; integration 300 passed | 113864180048 |
| limits | success; ci profile verdict pass | 113864180160 |
| adapters (mongodb) | success; 22 passed | 113864180116 |
| adapters (s3) | success; 27 passed / 10 skipped | 113864180246 |
| adapters (minio) | success; 17 passed | 113864180360 |
| adapters (sqlserver) | success; 17 passed | 113864180378 |
| e2e | success; 79 passed, без skips, 1550.96s | 113864180122 |

Межі: unit skips — git/gitleaks відсутні в runner; contract skips — PostgreSQL LLM dev-stack
та template contract. S3 job пропустив 10 parametrized MinIO recovery cases через відсутній
MinIO у його dev-stack; окремий MinIO job пройшов 17 тестів. Admin job виконує mock-регресію,
19 real/hybrid тестів пропущено; повний browser real22 не оголошено перевіреним.
Зовнішні LLM/IdP/AWS/Telegram — не перевірено на реальному сервісі;
dev-laptop/single-node виключені з обсягу. Наявні FastAPI warnings і runner Node20 deprecation
не приховано. Локальні повні набори не повторювались.

C-2/C-3 мають незалежне приймання та повний exact-SHA CI; зовнішні запити storage/Telegram
закриті їхніми власниками. Origin B `cbe8653` підтверджує закриття B-1…B-5 та final B 14/14;
WP-19 marker `ee78fc5` і WP-19b `88ec168` є в integration. Гейт C-4 відкрито.

Окремий автор `c4_cleanup`: checkout `C:/repos/Jane/.claude/worktrees/wp23d`, branch
`wp/23d-cleanup-safety`, база `40272ca38941e45a7284fb7635748fba48301358`, `.jane-wp = 23`.
Власність — власна ignored `.jane/cleanup-post-m3.ps1`, власні перевірки/logs `.jane/`, tracked
звіт `docs/delivery/WP-23/c4-cleanup.md`; журнал веде лише координатор.
До worktree скопійовано людський оригінал SHA256
`5D54EC5CAFA78D6BE0D9BC357601190CA7D05BBD3ADEF7F18FA4E014DCE6B78F`.
Людський скрипт ще не змінено, реального dry-run/-Apply ще не було.
Автор готує захист active/checked-out refs, immutable local+origin archive tags, Git exit checks,
bounds/reparse/orphan safeguards і збереження .jane; до застосування — незалежний reviewer ≤2 раунди.
Force-with-lease також не використовується: для remote race потрібен no-force CAS guard або
refs залишаються з явною причиною. Код кандидата й fixture checks ще не прийняті.
