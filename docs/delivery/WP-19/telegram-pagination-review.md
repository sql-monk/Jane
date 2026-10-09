# WP-19b — незалежне R1 і branch CI

**Вердикт: accepted.** Рецензент `/root/wp19_review` не був автором інкремента.
Frozen HEAD `b29a0406645c6b846211cade14a2a5d9ae697e76`, код
`2e68cf7339e0bac9b70d1464336109d10f7c42a5`, база
`57e621786943583d64a2c5da348aa6b70afee04e`. Це один раунд нового WP-19b;
первісний WP-19 та його accepted R2 не переглядалися.

Рецензент сам запустив старий варіант ізольовано й новий targeted case на двох реальних OS processes,
спільній SQLite та записаному зовнішньому Telegram backend. Компонент не мокався.
Production, contracts, manifests і hooks незмінені; зміни — тест і його звіт.

## Незалежне відтворення

Actual argv із `.jane/wp19b-review-r1-results.json`; cwd — checkout `wp19b`:

```text
uv run --all-packages pytest C:\repos\Jane\.claude\worktrees\wp19b\.jane\wp19b-review-r1-1791554347929263300\red-source\test_processes.py -k test_two_instances_share_state_and_take_over_after_kill -s --basetemp C:\repos\Jane\.claude\worktrees\wp19b\.jane\wp19b-review-r1-1791554347929263300\old-state
1 failed, 6 deselected in 28.97s
EXIT_CODE=1 (очікуване відтворення дефекту)
emitted=11; acknowledged=1; unacked=10; paused_by_backpressure=True

uvx --from rust-just just test telegram-collector -k test_two_instances_share_state_and_take_over_after_kill -s --basetemp C:\repos\Jane\.claude\worktrees\wp19b\.jane\wp19b-review-r1-1791554347929263300\new-state
1 passed, 57 deselected in 12.14s
EXIT_CODE=0
pre-kill emitted=20; acknowledged=10; unacked=10
```

Baseline blob `298e2f5b4da02c4d207de4adbab99f21946fa96e` і SHA256 вихідного та negative source
збігаються з авторськими. Negative delta — лише перша сторінка limit=1 та assertion її розміру.
Новий тест підтвердив 80 emitted і exactly-once 80 після hard kill/takeover,
Idempotency-Replayed і resume-log assertions. Порожня сторінка не скидає cursor;
наступний GET підтверджує отриманий cursor. Threshold=12, queue=10, timeout=20 збережені.

## Інші адресні перевірки

```text
Ruff: All checks passed!; 1 file already formatted; exit=0
Mypy: Success: no issues found in 25 source files; exit=0
Ownership від actual base та integration: 2 changed file(s), 0 outside ownership; exit=0
git diff --check: порожній вивід; exit=0
Own PIDs: 2916, 30092, 48132, 37316; alive=False
Frozen HEAD і tracked clean state до/після незмінні.
```

Docker не використовувався. Реальний зовнішній Telegram не перевірено на реальному сервісі.
Raw proof, exact argv, hashes, process logs та freeze checks — `.jane/wp19b-review-r1-*`;
копію збережено у захищеному `integ-a/.jane/wp19b-followup`.

## Actual branch CI

[CI 37940359810](https://github.com/sql-monk/Jane/actions/runs/37940359810), `event=push`,
точний frozen HEAD `b29a0406645c6b846211cade14a2a5d9ae697e76`: completed / success.
contracts-compat, lint, unit, web-mock-e2e, web, contract, isolation — success;
stack, limits, adapters та e2e — skipped за правилами push. Окремого full dispatch не було.

Справжні підсумки job logs:

```text
1137 passed, 5 skipped, 417 deselected, 33 warnings in 345.73s (0:05:45)
93 passed, 3 warnings in 17.29s
1:56PM INF no leaks found
```

Метадані й logs — `integ-a/.jane/wp19b-branch-ci-result.json`, `wp19b-ci-unit.txt`, `wp19b-ci-lint.txt`.
П'ять unit skips не названо проходженням; незалежний secret scan у lint успішний.
Приймання координатором — merge `88ec1682ec4f7b2a0e6c13745707ddc73ad16122`.
