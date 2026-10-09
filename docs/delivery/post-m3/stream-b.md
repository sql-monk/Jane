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
| B-3: дві репліки й L2 | `wp/22c-shared-host-replicas`, `wp22c` | виконання |
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
