# WP-19: повний CI перед прийманням

[Workflow 37929680616](https://github.com/sql-monk/Jane/actions/runs/37929680616),
`workflow_dispatch`, гілка `wp/19-post-m3-shared-stores-contentref`,
HEAD `ff12c6a435ebb5a1997e284d08bc4e7f1189eb4d`, код `7a6904c`.
Фактичний результат: **success, 14/14 jobs success**. Рецензент R2 — accepted;
guardian — compatible-with-actions (e2e root додає A; B-5 прибирає workaround).

| Перевірка | Справжній результат |
|---|---|
| Unit основного workspace | 1136 passed, 5 skipped, 417 deselected, 33 warnings in 310.07s |
| Додаткові unit-сценарії | 83 passed, 3 warnings in 15.53s |
| Повний стек / integration | 300 passed, 1258 deselected, 10 warnings in 284.88s; 0 skipped |
| SQL Server adapter job | 17 passed, 7 deselected in 4.01s |
| MongoDB adapter job | 22 passed, 5 deselected in 11.07s |
| MinIO adapter job | 17 passed, 4 deselected in 6.75s |
| S3 adapter job | 27 passed, 10 skipped, 9 deselected in 14.91s |
| Web mock Playwright | 29 passed (25.7s), 14 навмисно виключених real-тестів |
| Обов'язковий e2e | 75 passed in 1399.68s (0:23:19); 75 PASSED case lines, 0 skipped/xfailed/failed; JANE_E2E_REQUIRED=1 |
| Gitleaks / lint / types / contract / isolation / web | Jobs success; secret scan: no leaks found |
| Limits ci | Job success; verdict warn лише L1 single-gap jitter; решта L1–L8 ok |

5 unit skips — CLI git/gitleaks hook-тести, бо binary gitleaks не встановлений у unit job;
окремий lint job виконав справжній Docker gitleaks scan. 10 S3-job skips — параметри `[minio]`
recovery-тестів: цей job піднімає лише S3. Повний stack job із 300 passed без пропусків
перевірив обидва варіанти S3/MinIO. Локальні 66 skips worker не видаються за перевірки;
їхні backend-випадки перевірені в CI. Зовнішні AWS/LLM/IdP/Telegram без доступу не перевірені.

Limits artifact `limits-ci-37929680616-1`, каталог `ci-20261009T123113Z`, той самий чистий HEAD;
Ubuntu 24.04.5, Docker 28.0.4, 4 CPU/15.6 GiB, foreign containers 0.
L1 single gap `0.013018131256103516 s < 0.015 s` — warn; компенсований gap, середня швидкість,
віконний ліміт і collection succeeded — ok. OOM і рестартів 0. Профілі dev-laptop/single-node виключені з обсягу.

Скорочені справжні виводи:

```text
$ gh run view 37929680616 --repo sql-monk/Jane --json status,conclusion,jobs --jq '{status,conclusion,done:([.jobs[]|select(.status=="completed")]|length),total:(.jobs|length),pending:[.jobs[]|select(.status!="completed")|{name,status}]}'
{"conclusion":"success","done":14,"pending":[],"status":"completed","total":14}

2026-10-09T12:31:05.5856305Z   JANE_E2E_REQUIRED: 1
2026-10-09T12:54:32.5534359Z ======================= 75 passed in 1399.68s (0:23:19) ========================
2026-10-09T12:36:38.8104906Z ======== 300 passed, 1258 deselected, 10 warnings in 284.88s (0:04:44) =========
2026-10-09T12:24:20.6350036Z 12:24PM INF no leaks found
2026-10-09T12:35:39.3069172Z verdict: warn   results: .jane/limits/ci-20261009T123113Z
```

Повний JSON API — `.jane/wp19-a-ci-result.json` координатора, сирі job logs — `.jane/wp19-a-ci-*.txt`,
profile artifact — `.jane/wp19-a-limits-artifact/`. Логи отримані через GitHub jobs API, а не зі старого run.
Це CI гілки WP-19 перед merge. Після завершення B/C координатор A виконає один фінальний CI integration;
цей документ його не підміняє. Main змінює людина.
