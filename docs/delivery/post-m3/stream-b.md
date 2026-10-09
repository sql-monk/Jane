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
| B-4: приклад info з limits | `wp/22d-assistant-info-example`, `wp22d` | виконання |
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

Незалежний wp-reviewer: очікує призначення координатором (≤2 раунди). Merge, main і force push виконавець не робив.

### Запити до інших власників

Немає. Зміни лише у tests/e2e/**; docs/acceptance, infra та код сервісів не змінено.
