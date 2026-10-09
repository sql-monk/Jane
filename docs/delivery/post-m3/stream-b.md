# Потік B: приймання й адмінка після M3

Координатор: Codex. Доручення: [stream-b-handoff.md](stream-b-handoff.md);
обов'язкові правила: [README.md](README.md). Початкова база — `03a172d` від
`origin/codex/jane-integration` (2026-10-09), після приймання WP-20 `7a38c21`.

Кожен інкремент виконує окремий субагент у своєму worktree, `.jane-wp = 22`.
Код приймається після незалежного wp-reviewer (не більше двох раундів),
`contracts/` — також після окремого contract-guardian. Локально запускаються
лише адресні перевірки; новий/змінений e2e — один раз, повтор лише після падіння.
Повний CI потоку — один dispatch після всіх прийнятих злиттів.

Злиття виконує координатор у `.claude/worktrees/stream-b-coord` без `.jane-wp`:
detached checkout інтеграційної вершини, `fetch`, `pull --ff-only origin
codex/jane-integration`, `merge --no-ff` із маркером `merge: accept`,
`push origin HEAD:codex/jane-integration`. Окремий checkout ізолює потік B від
checkout потоку A. `main` і force push не використовуються.

## Стан інкрементів

| Завдання | Гілка / worktree | Стан |
|---|---|---|
| B-1: матриця й сценарії | `wp/22a-acceptance-matrix`, `wp22a` | accepted; `a967228` (документи) |
| B-2: решта real-адмінки | `wp/22b-admin-real-coverage` | виконання; база `2366213` |
| B-3: дві репліки й L2 | `wp/22c-shared-host-replicas`, `wp22c` | accepted; `753f3e9`, review 1 |
| B-4: приклад info з limits | `wp/22d-assistant-info-example`, `wp22d` | accepted; `256334c`, review 1, compatible |
| B-5: S-M3-02 після WP-19 | `wp/22e-storage-contract-cleanup` | очікує маркера `merge: accept WP-19` в origin |

## Початкові перевірки

```text
$ git fetch origin
exit 0
$ git log origin/codex/jane-integration --oneline --grep='^merge: accept WP-19' -3
(порожньо: залежність B-5 ще не прийнята)
$ gh run view 37905643300 --repo sql-monk/Jane --json conclusion,headSha,headBranch,url
conclusion=success
headBranch=wp/21-post-m3-followups
headSha=f69854e429cedf71a6eedfb03897f7518a0da9c5
url=https://github.com/sql-monk/Jane/actions/runs/37905643300
```

Виявлено сторонні контейнери `puluj-g-*` та стек потоку A `jane-wp19-*`;
потік B використовує лише власні унікальні compose-проєкти й прибирає їхні томи.
Профілі `dev-laptop` і `single-node` виключено з обсягу. Реальні зовнішні
LLM/IdP/AWS/Telegram без доступу — не перевірено на реальному сервісі.

## Запити до інших власників

Поки немає. B-5 має явну залежність від приймання WP-19 потоком A.


## B-1: accepted

Злиття: `eebe53493a076673bd02a0aa55095a7e13d26133`; незалежне рев’ю й тести не потрібні для документів за правилами потоку.


Дата: 2026-10-09. Гілка: `wp/22a-acceptance-matrix`. База: `03a172d8454ce6006ae44057335bbbf97fdf21de`.
Коміт: `a967228c12358c0c4121a624d2ef69e8eebc873d`. Worktree: `C:/repos/Jane/.claude/worktrees/wp22a`; `.jane-wp = 22`.
Стан: готово до злиття координатором; документи без коду, tests/review за спільними правилами не запускались.

### Результат

- Оновлено лише `docs/acceptance/matrix.md` і `docs/acceptance/scenarios.md`.
- S-M2-10: 25 повністю / 0 частково / 1 навмисний мок із 26; real-набір — 18. Межі доказів WP-20 збережено: повний 18 passed на 3a3251c, адресні контролі змінених специфікацій на df7f252. Нові 9 @mock та ще непокриті real частини перелічено явно.
- Окремий розділ «Після M3» містить CI 37905643300, R-03 через attempt_history/available_at та S-M3-01/02 із stored_materials.object_ids і початковим sha256 Telegram.
- Обидва блоки «Фінальна ревізія» побайтово однакові з базовим SHA. Тимчасові обходи S-M3-02 та зовнішні замінники збережено до B-5/WP-19.
- Профілі dev-laptop і single-node позначено виключеними з поточного обсягу за спільними правилами; історична таблиця M3 збережена.

### Справжній вивід перевірок

```text
$ python -X utf8 .claude/hooks/jane_wp.py check-diff 03a172d8454ce6006ae44057335bbbf97fdf21de
WP-22: 2 changed file(s), 0 outside ownership
exit=0

$ git diff --check 03a172d8454ce6006ae44057335bbbf97fdf21de HEAD
(виводу немає)
exit=0

$ git diff --stat 03a172d8454ce6006ae44057335bbbf97fdf21de HEAD
docs/acceptance/matrix.md    | 47 ++++++++++++++++++++++++++++-----
 docs/acceptance/scenarios.md | 62 +++++++++++++++++++++++++++++++-------------
 2 files changed, 85 insertions(+), 24 deletions(-)

$ git rev-parse HEAD
a967228c12358c0c4121a624d2ef69e8eebc873d
```

### Read-only перевірка GitHub

```text
$ gh run view 37905643300 --repo sql-monk/Jane --json headBranch,headSha,status,conclusion,url
{"conclusion":"success","headBranch":"wp/21-post-m3-followups","headSha":"f69854e429cedf71a6eedfb03897f7518a0da9c5","status":"completed","url":"https://github.com/sql-monk/Jane/actions/runs/37905643300"}
exit=0

$ gh run view 37905643300 --repo sql-monk/Jane --job 113740900134 --log
(скорочено до потрібних рядків; повний вивід у .jane/wp22a-ci-e2e-full.txt)
e2e	Run just e2e -v	2026-10-09T08:40:50.6720398Z   JANE_E2E_REQUIRED: 1
e2e	Run just e2e -v	2026-10-09T09:04:20.3262933Z tests/e2e/test_reliability_orchestrated.py::test_r_03_partition_to_storage_isolated_retry_waits_for_backoff_without_duplicates PASSED [ 94%]
e2e	Run just e2e -v	2026-10-09T09:04:33.7901412Z tests/e2e/test_reprocessing_stored.py::test_s_m3_01_reprocessing_takes_exactly_the_given_stored_objects PASSED [ 98%]
e2e	Run just e2e -v	2026-10-09T09:04:47.4475531Z tests/e2e/test_reprocessing_stored.py::test_s_m3_02_telegram_json_raw_is_restored_and_reprocessed_with_its_sha256 PASSED [100%]
e2e	Run just e2e -v	2026-10-09T09:04:47.4479081Z ======================= 77 passed in 1435.40s (0:23:55) ========================
exit=0
```

Повні докази: `.jane/wp22a-ci-summary.json`, `.jane/wp22a-ci-e2e-full.txt`; вибірка — `.jane/wp22a-ci-e2e.txt`; власність — `.jane/wp22a-check-diff.txt`; diff-check — `.jane/wp22a-diff-check.txt`.

### Запити до інших власників

Нових запитів немає. Відомі межі real-адмінки — B-2, усунення обходів S-M3-02 після маркера прийняття WP-19 — B-5. Журнал потоку не редагувався: координатор переносить цей звіт у stream-b.md.

### Push власної гілки

```text
$ git push -u origin wp/22a-acceptance-matrix
To https://github.com/sql-monk/Jane.git
 * [new branch]      wp/22a-acceptance-matrix -> wp/22a-acceptance-matrix
branch 'wp/22a-acceptance-matrix' set up to track 'origin/wp/22a-acceptance-matrix'.
exit=0
```


## B-3: accepted

Злиття: `306af36a0300b03dd42aab67703386f10439d981`. Незалежний wp-reviewer: **accepted**, раунд 1 (2026-10-09).

Рецензент сам виконав: check-diff — 4 changed / 0 outside; diff --check — exit 0; Ruff — All checks passed, 2 files already formatted; Docker — 0 контейнерів / 0 томів. Перевірено окремі PID і mounts, aggregate concurrency/rate, живе поновлення понад TTL, SIGKILL і обмежене TTL очікування. 50 мс допускається для окремого інтервалу, повний span перевіряється без накопичення допуску. Успішний e2e не повторювали.


Гілка: `wp/22c-shared-host-replicas`. База: `03a172d` (`origin/codex/jane-integration`). SHA: `753f3e9e4b9e48bf4b9beee57c7c1f1b7a4e8270`. Стан: **review** — незалежного wp-reviewer призначає координатор.

### Результат

Додано два e2e у `tests/e2e/test_shared_host_replicas.py`, тестову compose-накладку та обгортку справжнього testsite HTTP handler. Репліки працюють в окремих Docker-контейнерах, з різними PID та одним проєктним томом `STATE_DIR`. Продуктові сторінки й robots.txt віддає справжній TestSiteHandler; обгортка лише записує час старту/завершення та контрольовано затримує відповіді. Колектор не змінено, запити/відповіді колектора перевіряються контрактним collector.v1 клієнтом.

Перша фаза навантажує спільний слот (1) тривалими відповідями; друга вимірює спільний інтервал 250 мс на миттєвих відповідях. Обидві репліки реально виконують по 8 товарних запитів, часові діапазони їхньої роботи перекриваються. Перевіряється кожна пауза і тривалість всіх 18 стартів, включно з robots.txt. Допуск 50 мс враховує доставку дозволеного запиту до потоку testsite; для повної тривалості він застосовується лише один раз.

TTL-сценарій спершу тримає живий запит понад TTL (10.687 с при TTL 8 с), доводячи поновлення його слота та блокування другої репліки. Після SIGKILL перший HTTP handler testsite відпускається, але мертвий процес не може звільнити слот. Жива репліка стартувала через 6.454 с після kill, що менше 8 + 0.05 (shared host poll) + 0.5 (доставка/планування) = 8.55 с. Початки HTTP-запитів і маркери kill вимірюються одним монотонним годинником testsite.

README.shared-hosts.md описує конфігурацію, типові значення й запуск. Production-ліміти не змінено; `collector.shared_host_*` задаються через конфігурацію тестового стека.

### Локальні перевірки та справжній вивід

`JANE_E2E_PROJECT=jane-wp22c-local JANE_E2E_REQUIRED=1 uv run --all-packages pytest tests/e2e/test_shared_host_replicas.py -m e2e -v -s`

Перший запуск через Node child environment упав до контейнерів: compose plugin не знайдено (`unknown shorthand flag: 'f' in -f`), 3 setup/teardown errors in 3.43s. Весь вивід: `.jane/wp22c-e2e-setup-failure.txt`. Повтор після цього падіння через штатний authenticated exec environment:

```text
L2 Docker topology: {"project": "jane-wp22c-local-shared-hosts-1b0769", "containers": ["310f0ff96f81", "26818414f2f4"], "pids": [78575, 79292], "state_volumes": ["jane-wp22c-local-shared-hosts-1b0769_web-collector-data", "jane-wp22c-local-shared-hosts-1b0769_web-collector-data"], "shared_host_ttl_seconds": 8, "shared_host_poll_ms": 50}
L2 parallel: {"requests":18,"product_requests_per_replica":[8,8],"max_in_flight":1,"min_start_gap_s":0.005914442001085263,"start_span_s":6.592995988998155} (requests_by_replica див. повний лог)
L2 interval: {"requests":18,"product_requests_per_replica":[8,8],"max_in_flight":1,"min_start_gap_s":0.23368372999539133,"start_span_s":4.279775071001495} (requests_by_replica див. повний лог)
L2 dead-owner TTL: {"live_slot_held_s": 10.687000000034459, "shared_host_ttl_seconds": 8, "shared_host_poll_s": 0.05, "kill_duration_s": 3.4693035270029213, "successor_start_after_kill_s": 6.454179512998962, "allowed_after_kill_s": 8.55}
======================== 2 passed in 157.69s (0:02:37) ========================
exit_code=0
```

Повний вивід: `.jane/wp22c-e2e.txt` (перелічені replica markers скорочено вище). Окремі e2e після успіху не повторювались. Повний just check / just e2e локально не запускались.

```text
$ .venv/Scripts/ruff.exe format tests/e2e/jane_e2e/host_probe.py tests/e2e/test_shared_host_replicas.py
1 file reformatted, 1 file left unchanged
$ .venv/Scripts/ruff.exe check tests/e2e/jane_e2e/host_probe.py tests/e2e/test_shared_host_replicas.py
All checks passed!

$ .venv/Scripts/python.exe .claude/hooks/jane_wp.py check-diff 03a172d
WP-22: 4 changed file(s), 0 outside ownership

exit_code=0

```

Власний проект `jane-wp22c-local-shared-hosts-1b0769` виконав `down --remove-orphans -v --rmi local` у fixture finalizer; стандартна session fixture також прибрала свій порожній `jane-wp22c-local`. Контейнери `puluj-g-*` і стек B-2 не змінювались. Перевірка залишків (`.jane/wp22c-cleanup.txt`):

```text
$ docker ps -a --filter label=com.docker.compose.project=jane-wp22c-local-shared-hosts-1b0769 --format {{.Names}}
$ docker volume ls --filter label=com.docker.compose.project=jane-wp22c-local-shared-hosts-1b0769 --format {{.Name}}
containers_remaining=0
volumes_remaining=0

```

### CI та рев'ю

Push власної гілки успішний, `.jane/wp22c-push.txt`. CI: [37913459478](https://github.com/sql-monk/Jane/actions/runs/37913459478), SHA `753f3e9e4b9e48bf4b9beee57c7c1f1b7a4e8270`, на момент передачі queued. Повний CI після злиттів потоку запускає координатор. Контракти не змінювались, окремий contract-guardian не потрібний.

Незалежний wp-reviewer: accepted, раунд 1; підсумок перевірок наведено вище. Merge, main і force push виконавець не робив.

### Запити до інших власників

Немає. Зміни лише у tests/e2e/**; docs/acceptance, infra та код сервісів не змінено.


### Оновлення CI B-3

[37913459478](https://github.com/sql-monk/Jane/actions/runs/37913459478), SHA `753f3e9e4b9e48bf4b9beee57c7c1f1b7a4e8270`: **completed / success**.

## B-4: accepted

Злиття: `78835c3fe16b35294a7db4588bfabece8a416217`. Незалежний wp-reviewer: **accepted**, раунд 1; окремий contract-guardian: **compatible** на `256334c18d459634afb6ec2ff6a753cf8261e695`.

Рецензент сам виконав: ownership 3 changed / 0 outside; auth regression 4 passed; generated 10 files up to date; ESLint/Prettier/diff-check exit 0. Raw browser log: 1 passed / exit 0, кейс не повторювали після успіху.

Guardian сам виконав check_contracts --require-redocly (539 examples / All contract checks passed), compat --base origin/codex/jane-integration --oasdiff (усі 7 API ok / 0 breaking, 0 warnings), compat від бази03a172d (0/0), чотири групи scope-тестів для семи API (28 passed in 1.80s), gen-api --check (10 up to date). Route.choose: default unchanged; assistantCi exact fixture для collector/handler/storage/registry/orchestrator/llm/assistant. Реалізації й споживачі всіх семи API, jane-kit та registry runtime-profile не потребують змін; mock адмінки оновлено, generated актуальний.

Фінальна зміна лише адитивна: default info лишається першим; operationId, scopes, security, ServiceInfo та limits незмінні. Первісний CI37912804009 на086ba95 був failed (4 scope failures через inline Info), це виправлено256334c; фінальний CI37914220697 ще in_progress на момент приймання, фінальний gate потоку виконується після всіх злиттів.

Нижче — авторський звіт на момент передачі у review; поточні вердикти наведено вище.


Гілка: `wp/22d-assistant-info-example`. База: `03a172d8454ce6006ae44057335bbbf97fdf21de`. Фінальний SHA: `256334c18d459634afb6ec2ff6a753cf8261e695` (forward fix після `086ba95681bc11a96c546ce2e8c931a175a2a971`), pushed. Стан: **review**; незалежні wp-reviewer і contract-guardian ще мають надати вердикти.

### Результат

- Додано `contracts/examples/openapi/assistant-info-ci.json`: ServiceInfo асистента з повними `limits` у формі PlatformLimits, скопійованими з чинного `contracts/examples/schemas/common/limits@PlatformLimits/ci.json` (профіль ci, бюджет 0.01 USD/day, min_onboarding_confidence 0.8, defaults і hard_caps).
- Спільний `common.yaml#/components/pathItems/Info` має новий named example `assistantCi`; попередній generic example `info` лишився першим. `assistant.v1.yaml` зберігає початковий `$ref` на спільний Info. Операції, schema, scope, auth, коди відповідей і типова mock-відповідь незмінні.
- `web/admin/e2e/post-m3.spec.ts` отримує відповідь від контрактного mock через `Prefer: example=assistantCi`, звіряє все тіло з `openapiExample("assistant-info-ci")` і перевіряє показ/перевизначення порогу в UI. Ручне доповнення limits та helper schemaExample видалено.
- Фінальний diff від бази — лише три файли: common.yaml, assistant-info-ci.json, post-m3.spec.ts. Код services/, infra/ й журнал координатора не редаговано. Після CI-дефекту координатор явно узгодив ownership common.yaml.

### Споживачі контракту

Усі сім API — **assistant, collector, handler, llm, orchestrator, registry, storage** — використовують спільний Info і тепер бачать додатковий named example assistantCi. Перший generic info, схема ServiceInfo та auth залишаються попередніми, тому стандартні відповіді mock.py незмінні. Єдиний споживач нового named example — змінений mock-сценарій адмінки. Сервіси й generated API не потребують змін. Генератор підтвердив 10 актуальних generated files.

B-2: точний шлях fixture — `contracts/examples/openapi/assistant-info-ci.json`; читання через `openapiExample("assistant-info-ci")`, відповідь mock через `Prefer: example=assistantCi`.

### Перевірки й виправлення після CI

CI на 086ba95: [37912804009](https://github.com/sql-monk/Jane/actions/runs/37912804009), **failed** у contract: 4 failed, 104 passed, 3 skipped. Конкретно assistant: test_table_equals_contract, test_every_operation_declares_its_scopes, test_table_scopes_equal_contract, test_health_and_info_match_jane_kit. Причина: початкове розгортання спільного Info втратило identity path item, за якою auth-тести відрізняють загальні health/info від scope tables. Raw log: `.jane/wp22d-ci-failed-37912804009.txt`. На цьому run completed lint/contracts-compat/web/web-mock-e2e були success; загального success немає.

Forward fix 256334c відновлює common Info ref і додає лише приклад до його examples. Jane-kit і тести не змінено та не послаблено. Після fix запущено **лише чотири відповідні assistant auth-тести**, contract lint з Redocly і compat з oasdiff. Результат: 4 passed; 539 валідних OpenAPI examples; усі сім API oasdiff ok, 0 breaking / 0 warnings. Push запускає звичайний CI; повний workflow вручну не запускався. Новий CI на 256334c: [37914220697](https://github.com/sql-monk/Jane/actions/runs/37914220697), **in_progress** на момент живої перевірки через gh run list; verdict ще немає.

Один успішний local browser case: `node scripts/e2e.mjs post-m3.spec.ts --grep=min_onboarding_confidence --reporter=list`, JANE_ADMIN_PORT=4780, JANE_ADMIN_MOCK_PORT_BASE=4781, cwd web/admin. **1 passed (3.4m)**, сам scenario 14.7s, EXIT_CODE=0. Case виконано на 086ba95; після fix payload fixture й mock-сценарій бітово незмінні (git diff --exit-code 086ba95 HEAD для цих двох файлів → 0), тож успішний case не повторювався.

Повні just check/e2e локально не запускались. Сервісні DoD про Dockerfile, README, ліміти й метрики не застосовні: це адитивний fixture і споживач у mock-тесті; API-поведінка незмінна. Власність: WP-22: 3 changed file(s), 0 outside ownership; робоче дерево чисте.

### Локальні startup failures і cleanup

- Direct node_repl child runner завис у Playwright worker setup без browser і без результату понад 319 s після Running 1 test. Watchdog позначив setup failure й завершив лише його дерево процесів. Raw `wp22d-e2e.txt`, окремий `wp22d-e2e-setup-failure.txt`.
- Corepack retry впав до сценарію: активний pnpm 12.8.1 намагався auto-install і відхилив ignored node_modules junction як hoist directory. Raw `wp22d-e2e-retry.txt`. Package.json та pnpm-lock.yaml root/worktree перед junction були перевірені як тотожні.
- Native retry із grep-аргументом із пробілами повернув No tests found, case не виконувався. Raw `wp22d-e2e-exec.txt`. Виправлений selector --grep=min_onboarding_confidence дав один успішний case.
- Native shutdown затримав завершення після ok 1; підтверджені лише власні 7 mock.py listener processes 4781…4787 і vite4780 зупинено. Фінальний runner завершився exit0. Bind-and-close кожного127.0.0.1:4780…4787 підтвердив вільні порти; чужі процеси/контейнери не зупинялись. Raw `wp22d-cleanup.txt`.
- Перші targeted auth startups не виконали тести: root .venv не мав jwt; пакетний uv без dev не мав pytest. Штатний `uv run --frozen --package jane-kit --group dev python -m pytest` виконав рівно 4 потрібні тести. Усі startup logs збережені; lock/code не змінено.

### Реальний вивід фінальних перевірок

### auth-fix-dev

```text
Installed 36 packages in 1.81s
....                                                                     [100%]
4 passed in 2.88s

EXIT_CODE=0
```

### contracts-fix

```text
$ uv.exe run contracts/tools/check_contracts.py --require-redocly
[ok] JSON Schema meta-validation and $refs
[ok] OpenAPI 3.1 validation
[ok] Jane API conventions and inline examples
[ok] Standalone schema examples
[ok] Python interfaces compile
[ok] Mock server can serve every operation
[ok] Autonomous APIs do not reference orchestrator/assistant contracts
[ok] Redocly lint: ok (Woohoo! Your API descriptions are valid. 🎉)

Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=118, openapi_documents=8, openapi_examples=539, operations=118, python_files=3, schema_examples=46, schemas=16
All contract checks passed.

EXIT_CODE=0
```

### compat-fix

```text
$ uv.exe run contracts/tools/compat.py --base origin/codex/jane-integration --oasdiff
Base: origin/codex/jane-integration (24 contract files); working tree: 24 files; added: 0
oasdiff: docker image tufin/oasdiff:v1.33.0@sha256:6263a96dd2ef0726c54e21fea9b8e1607eac4841add0079324b424c1f52b819c (pinned default)
oasdiff assistant.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff collector.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff handler.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff llm.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff orchestrator.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff registry.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.
oasdiff storage.v1.yaml: ok
No breaking changes to report, but the specs are different.
Run 'oasdiff diff' to see structural differences.

0 breaking, 0 warning(s).

EXIT_CODE=0
```

### generated

```text
$ node.exe web/admin/scripts/gen-api.mjs --check
gen-api: 10 generated files are up to date

EXIT_CODE=0
```

### eslint

```text
$ node.exe node_modules/eslint/bin/eslint.js e2e/post-m3.spec.ts --max-warnings 0

EXIT_CODE=0
```

### format-recheck

```text
$ node.exe web/admin/node_modules/prettier/bin/prettier.cjs --check web/admin/e2e/post-m3.spec.ts contracts/examples/openapi/assistant-info-ci.json
Checking formatting...
All matched files use Prettier code style!

EXIT_CODE=0
```

### ownership-final-fix

```text
WP-22: 3 changed file(s), 0 outside ownership

EXIT_CODE=0
```

### e2e-final

```text
e2e: contract mocks (contracts/tools/mock.py)
[WebServer] (node:21180) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
[WebServer] (Use `node --trace-warnings ...` to show where the warning was created)
[WebServer] (node:37780) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
[WebServer] (Use `node --trace-warnings ...` to show where the warning was created)

Running 1 test using 1 worker

(node:36336) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
  ok 1 [chromium] › e2e\post-m3.spec.ts:63:3 › post-M3 admin (WP-20) @mock › assistant: min_onboarding_confidence of the assistant is shown and can be set for one onboarding (14.7s)

  1 passed (3.4m)

EXIT_CODE=0
```

### payload-unchanged

```text
git diff --exit-code 086ba95681bc11a96c546ce2e8c931a175a2a971 HEAD -- contracts/examples/openapi/assistant-info-ci.json web/admin/e2e/post-m3.spec.ts
No output; EXIT_CODE=0
```

### commit-fix

```text
$ git.exe commit -m fix: preserve shared assistant info contract identity -m Co-authored-by: Codex <noreply@openai.com>
12:52PM INF 0 commits scanned.
12:52PM INF scanned ~153 bytes (153 bytes) in 323ms
12:52PM INF no leaks found
[wp/22d-assistant-info-example 256334c] fix: preserve shared assistant info contract identity
 2 files changed, 3 insertions(+), 24 deletions(-)

EXIT_CODE=0
```

### push-fix

```text
To https://github.com/sql-monk/Jane.git
   086ba95..256334c  wp/22d-assistant-info-example -> wp/22d-assistant-info-example

EXIT_CODE=0
```

### cleanup

```text
Verified own listener command lines: seven contracts/tools/mock.py processes on ports4781..4787 and vite preview on4780.
Stop-Process -Id 40448,45740,18976,43440,21788,30772,14596,37780 -Force: exit0.
Get-NetTCPConnection -State Listen filtered4780..4787: no output, exit0.
Post-cleanup bind-and-close on each127.0.0.1 port4780..4787: all free.
Native e2e runner completed EXIT_CODE=0 with1passed(3.4m).
```

### Запити до інших власників

Нових немає. До accepted потрібні незалежні wp-reviewer, contract-guardian і рішення координатора за CI.
