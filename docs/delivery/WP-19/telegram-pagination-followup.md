# WP-19b. Споживання коротких Telegram materials-сторінок перед kill

**Гілка:** `wp/19b-telegram-pagination-test` · **Ревізія коду:**
`2e68cf7339e0bac9b70d1464336109d10f7c42a5` · **База / merge-base:**
`57e621786943583d64a2c5da348aa6b70afee04e` · **Стан:** review.

Це окремий інкремент для нового запиту з
[stream-c.md](../post-m3/stream-c.md#c-2-завершення-branch-ci--failure).
Прийняті WP-19 і WP-19a, їхні worktrees і попередні звіти не переглядалися й не змінювалися.

## Діагноз і межі

Власноруч завантажено actual unit job `113841074007` через `gh api --allow-escape-sequences` у
`.jane/wp19b-ci-job-113841074007.txt`. Branch CI
[37936808211](https://github.com/sql-monk/Jane/actions/runs/37936808211) на точному
`22f83662efaac0a64a91a2bc9078b0bcec04a793` — `completed / failure`.
Log містить GET `after=c_0000000000000001`, тобто перша сторінка мала один матеріал,
а падіння `test_two_instances_share_state_and_take_over_after_kill` —
`emitted=11`, `acknowledged=1`, `unacked=10`, `paused_by_backpressure=true`, queue limit 10.
Після другого GET тест припиняв ACK і чекав `emitted >= 12`; з ACK 1 черга дозволяла максимум 11.

Readonly `git diff bb1982b 22f8366 -- services/telegram-collector libs/jane-kit contracts/python`
порожній, exit 0 (`.jane/wp19b-c2-source-delta.txt`). Actual B CI
[37937013460](https://github.com/sql-monk/Jane/actions/runs/37937013460) на
`bb1982b9f6b1e2593fb2f1ab60a436e6945f15b1` мав unit `completed / success`, увесь run ще
`in_progress` на перевірці (`.jane/wp19b-b-unit-status.txt`). Це підтверджує intermittent baseline
помилку тестового consumer; source delta C-2 в перевірених компонентах відсутня.

Власність: тільки [test_processes.py](../../../services/telegram-collector/tests/test_processes.py)
та цей новий звіт. Production code, manifests, contracts, queue, початкові assertions і timeouts не змінено.

## Мінімальне виправлення й детермінований доказ

Перша реальна сторінка навмисно запитується з `limit=1`, і додатковий assertion перевіряє один матеріал.
Наступні GET/ACK тривають за фактично отриманим cursor у predicate наявного bounded `wait_for`,
поки виконується **початкове** `stats.emitted >= 12`. Кількість матеріалів на сторінці не використовується
як припущення про прогрес. `after` зберігає останній cursor і при порожній сторінці.
Default `wait_for` **20 s**, pre-kill GET `wait_ms=5000`, post-kill GET `limit=7 / wait_ms=2000`,
`wait_done` і HTTP/process-start timeouts лишилися початковими. `Idempotency-Replayed`, hard kill A,
shared-state takeover B, `status=succeeded`, exactly-once **80** і resume log assertions збережено.

**Old-fail:** на baseline consumer змінено тільки перший request `limit=10 -> 1` і додано той самий
short-page assertion. Один адресний прогін реальних двох OS processes дав **1 failed / 57 deselected,
32.53 s, exit 1**; failure view детерміновано `emitted=11 / ACK=1 / unacked=10 / paused=true`.
**New-pass:** той самий short-page case з виправленим consumer — **1 passed / 57 deselected,
11.69 s, exit 0**; pre-kill `emitted=15 / ACK=5 / unacked=10`, після kill/takeover — 80 emitted,
exactly-once 80 та replay assertions пройшли. Повторів успішного прогону чи повних suites не було.

Negative source збережено в `.jane/wp19b-old-consumer.py`, patch — `.jane/wp19b-old-consumer.diff`.
Baseline файл / fixture — `.jane/wp19b-baseline-test_processes.py` і `-conftest.py`.
Baseline test blob: `298e2f5b4da02c4d207de4adbab99f21946fa96e`;
SHA256 baseline: `abbace0709c0e1e11aade36abfdf99421de956e22d904acc257ec0c514333a1c`;
SHA256 виконаного negative variant: `a69b81494d0fc2d4a52530fec14cd81d7574c8f1c1134af179759b03e8ccd814`.

`.jane/wp19b-red-repro.py` читає exact baseline через git, створює лише ignored копії test/conftest,
перевіряє byte equality short-page variant з уже виконаним negative source й зберігає hashes та exact
pytest argv у `.jane/wp19b-red-repro-metadata.json`. Підготовка wrapper — exit 0;
його окремий повторний pytest не запускався, бо той самий source уже дав наведений real red output.
Незалежний reviewer може відтворити red **без редагування frozen tracked source**:

```text
uv run --all-packages python .jane/wp19b-red-repro.py --run
```

Original red й green pytest виконано через `just test telegram-collector -k` саме цієї функції;
сирі outputs і збережені process logs / SQLite files — `.jane/wp19b-old-fail.txt`, `-new-pass.txt`,
`-old-run/`, `-new-run/`. Сервіс не мокався: два реальні OS processes використовували власну SQLite
і built-in recorded Telegram backend; на реальному Telegram не перевірено.

## Команди перевірки та справжній вивід

```text
$ uvx --from rust-just just test telegram-collector -k test_two_instances_share_state_and_take_over_after_kill --basetemp .jane/wp19b-old-run -s
[...]
E       AssertionError: condition not reached: {'collection_id': 'job_5fa32fba01c94082b359e50c8fd3bdf7', 'status': 'running', 'paused_by_backpressure': True, 'source_kind': 'telegram', 'mode': 'full', 'state_key': 'shared', 'created_at': '2026-10-09T13:47:42Z', 'stats': {'discovered': 11, 'fetched': 11, 'emitted': 11, 'acknowledged': 1, 'unacked': 10, 'duplicates': 0, 'skipped_out_of_scope': 0, 'skipped_robots': 0, 'not_modified': 0, 'errors': 0, 'frontier_size': 0, 'bytes_fetched': 277, 'by_strategy': {'telegram_history': 11}}, 'source_id': 'news-tg', 'effective_limits': {'queue': {'max_unacked_materials': 10}, 'rate': {'min_delay_ms_per_host': 100}, 'retries': {'backoff_multiplier': 2.0, 'initial_backoff_ms': 0, 'jitter': True, 'max_attempts': 2, 'max_backoff_ms': 0}, 'telegram': {'max_flood_wait_seconds': 300, 'max_media_bytes': 20971520, 'max_messages_per_run': 10000}, 'timeouts': {'connect_timeout_ms': 15000, 'request_timeout_ms': 30000}, 'transfer': {'idempotency_ttl_seconds': 86400, 'inline_max_bytes': 262144, 'job_retention_seconds': 86400, 'transit_ttl_seconds': 604800}}}
=========================== short test summary info ===========================
FAILED services/telegram-collector/tests/test_processes.py::test_two_instances_share_state_and_take_over_after_kill
====================== 1 failed, 57 deselected in 32.53s ======================
error: recipe `test` failed on line 45 with exit code 1
EXIT_CODE=1
```

```text
$ uvx --from rust-just just test telegram-collector -k test_two_instances_share_state_and_take_over_after_kill --basetemp .jane/wp19b-new-run -s
[...]
services\telegram-collector\tests\test_processes.py short first page: 1 item; pre-kill stats: {'discovered': 15, 'fetched': 15, 'emitted': 15, 'acknowledged': 5, 'unacked': 10, 'duplicates': 0, 'skipped_out_of_scope': 0, 'skipped_robots': 0, 'not_modified': 0, 'errors': 0, 'frontier_size': 0, 'bytes_fetched': 381, 'by_strategy': {'telegram_history': 15}}
takeover succeeded: 80 emitted; exactly-once 80 verified

====================== 1 passed, 57 deselected in 11.69s ======================
EXIT_CODE=0
```

```text
$ uv run --all-packages ruff check services/telegram-collector/tests/test_processes.py
All checks passed!
EXIT_CODE=0
```

```text
$ uv run --all-packages ruff format --check services/telegram-collector/tests/test_processes.py
1 file already formatted
EXIT_CODE=0
```

```text
$ uv run --all-packages mypy services/telegram-collector/src services/telegram-collector/tests
Success: no issues found in 25 source files
EXIT_CODE=0
```

```text
$ python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
WP-19: 2 changed file(s), 0 outside ownership
EXIT_CODE=0
```

```text
$ python .claude/hooks/jane_wp.py check-diff 57e621786943583d64a2c5da348aa6b70afee04e
WP-19: 2 changed file(s), 0 outside ownership
EXIT_CODE=0
```

```text
$ git diff --check
EXIT_CODE=0
```

```text
$ uv run --all-packages python .jane/wp19b-cleanup.py
old-run: PID=42900; alive=False; log=.jane/wp19b-old-run/test_two_instances_share_state0/service-61791-1791553654483316600.log
old-run: PID=18816; alive=False; log=.jane/wp19b-old-run/test_two_instances_share_state0/service-61792-1791553659524065600.log
new-run: PID=44424; alive=False; log=.jane/wp19b-new-run/test_two_instances_share_state0/service-59772-1791553776228058800.log
new-run: PID=41280; alive=False; log=.jane/wp19b-new-run/test_two_instances_share_state0/service-59773-1791553779227940300.log
Docker not used: fixture starts only its own two OS processes on free ports and its own SQLite file.
EXIT_CODE=0
```

## Cleanup та незавершені gates

Fixture `service_factory` у teardown зупинив тільки власні processes. Перевірено PID з чотирьох власних
process logs: 42900, 18816 (red), 44424, 41280 (green) — `alive=False`, exit 0.
Docker не потрібен цьому fixture й не запускався; чужі Jane / Puluj-g processes та контейнери не чіпались.
`full just check`, full local e2e, завершені suites і workflow dispatch не запускалися.

Потрібні незалежний bounded R1 **цього нового WP-19b**, автоматичні branch CI gates після normal push
і merge координатором. Прийняте первісне WP-19 не є предметом цього review;
фінальний повний CI A лишається один після завершення B/C. Запит власнику Telegram виконано кодом цього інкремента,
статус журналів потоків веде координатор.
