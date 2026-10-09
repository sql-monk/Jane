# Після M3: фінальний CI трьох потоків

Стан: **accepted, повний підсумковий CI success**.
Перевірений Git SHA — **`9d9fb4c07624710158c75ea18f38cc201779453f`**.
[Workflow 37953732904](https://github.com/sql-monk/Jane/actions/runs/37953732904):
`workflow_dispatch`, `codex/jane-integration`, **14/14 jobs success**,
створено `2026-10-09T15:42:29Z`, завершено `2026-10-09T16:17:02Z`.

## Гейти й єдиний запуск

- WP-19 accepted, merge `ee78fc5`, незалежне R2 і guardian завершені; R17 та
  files-транзит R18 закрито. Оригінальні перевірки не повторювалися.
- Документальний WP-19a accepted; новий тестовий WP-19b accepted, merge `88ec168`,
  незалежне R1, deterministic old-fail/new-pass та automatic branch CI success.
  Оригінальне WP-19 review не відкривалося повторно.
- [Потік B](stream-b.md): B-1…B-5 accepted/merged, full CI
  [37937013460](https://github.com/sql-monk/Jane/actions/runs/37937013460) на
  `bb1982b9f6b1e2593fb2f1ab60a436e6945f15b1` — success 14/14.
- [Потік C](stream-c.md): C-1…C-4 закриті; full CI
  [37942655574](https://github.com/sql-monk/Jane/actions/runs/37942655574) на
  `133bb5a0604ccbc3ce41a820216d4751f301a47b` — success 14/14. C-4 accepted R2,
  merge `81f8443`; coordinator Apply exit 0 і післяопераційна перевірка PASS.
  Завершення опубліковано `9d9fb4c`; unknown orphan paths збережено за guards.

A перечитав origin-журнали, перевірив живі B/C runs і наявність accepted merges
в ancestry. Чистий `integ-a` на `codex/jane-integration`, без `.jane-wp`,
оновлено `pull --ff-only`; HEAD дорівнював live origin SHA вище.
Перед dispatch у `.jane/wp19-a-coordinator.json` та
`.jane/final-a-ci/dispatch-intent.json` збережено exact SHA й intent
`2026-10-09T15:42:14.8359994Z`, count **1**, attempts **1**.

```text
$ gh workflow run ci --repo sql-monk/Jane --ref codex/jane-integration
https://github.com/sql-monk/Jane/actions/runs/37953732904
EXIT_CODE=0
```

Actual event/head SHA збіглися з intent. Дублікатів dispatch/rerun і локального
full check/e2e не було. Наступні пробудження перевіряли саме записаний run ID.

## Фактичні jobs

Джерело — `gh run view 37953732904 --repo sql-monk/Jane --json
databaseId,headSha,event,status,conclusion,url,createdAt,updatedAt,jobs`, exit 0.

| Job | Результат | Job ID |
|---|---|---|
| contracts-compat | success | 113898839767 |
| lint | success | 113898840013 |
| web-mock-e2e | success | 113899221155 |
| unit | success | 113899221165 |
| web | success | 113899221215 |
| contract | success | 113901794241 |
| isolation | success | 113901794286 |
| limits | success | 113902191566 |
| stack | success | 113902191691 |
| e2e | success | 113902191712 |
| adapters (s3) | success | 113902191920 |
| adapters (mongodb) | success | 113902191945 |
| adapters (sqlserver) | success | 113902191961 |
| adapters (minio) | success | 113902191968 |

Actual logs отримано `gh run view 37953732904 --repo sql-monk/Jane --job <ID> --log`,
exit 0 для e2e/stack/lint/limits. Підсумки:

```text
e2e   Run just e2e -v       JANE_E2E_REQUIRED: 1
e2e   2026-10-09T16:16:58Z  79 passed in 1569.08s (0:26:09)
stack 2026-10-09T15:56:10Z  300 passed, 1259 deselected, 10 warnings in 281.69s (0:04:41)
lint  Secret scan (gitleaks) no leaks found
limits verdict: pass       results: .jane/limits/ci-20261009T155043Z
```

У raw e2e log — **79 окремих PASSED**, 0 skipped/xfailed/failed/error;
mandatory `JANE_E2E_REQUIRED=1` підтверджено. Stack — 300 passed, 0 skipped;
1259 deselected — тести інших наборів. Failure-only stack-log steps навмисно
skipped після успіху; жодного job не пропущено.

## Limits і збережені докази

Артефакт **`limits-ci-37953732904-1`**, ID `11627871790`,
SHA256 archive digest `15d73e5254cef2a51a1ce59cdfaf3c25446312aa0a63a27d2cd3dd02e554c476`.
Завантажений `ci-20261009T155043Z/results.json` підтверджує exact Git SHA,
`git_dirty=false`, profile `ci`, verdict **pass**, усі L1–L8 pass і всі checks ok.
L1 single-gap jitter `0.01796746253967285 s >= 0.015 s`; warning немає.
L7: peak `626.1 MiB <= 10240`, OOM/restarts 0.

Сирі JSON, intent/response, чотири job logs, limits artifact і receipt із SHA256
локальних доказів збережено у захищеному coordinator checkout
`C:/repos/Jane/.claude/worktrees/integ-a/.jane/final-a-ci/`.
Receipt — `receipt.json`; оригінальні author/reviewer докази WP-19/19a/19b також
збережені в цьому checkout до cleanup C.

Межі: workflow запускає admin mock suite, а не повний browser real22.
Зелені jobs не означають відсутності всіх навмисних skips у unit/contract/adapters/mock
наборах; нуль skips підтверджено саме для mandatory API e2e і stack.
Зовнішні LLM/IdP/AWS/Telegram — **не перевірено на реальному сервісі**.
`dev-laptop`/`single-node` виключені з обсягу; S3/MinIO-транзит та producer
`download_url` не входять до прийнятого files-транзиту R18.

## Передача людині

Після CI live integration дорівнювала перевіреному `9d9fb4c…`;
`origin/main` `37a30e294745a9001ff2f57c87c1013bfe087414` — його предок.
Пізніше A додає **лише цей звіт і status.md**: Git diff поза `docs/` має бути порожнім.
CI перевіряв exact SHA вище; пізніший документальний SHA не оголошується окремо протестованим.
Точний актуальний SHA для людського `merge --ff-only` збережено в checkpoint і передано в чаті.
Злиття/push `main` виконує людина; A не змінює main, refs/worktrees чи чужі автоматизації.
Після передачі результату зупиняється лише heartbeat A `jane-a-ci-b-c`.
