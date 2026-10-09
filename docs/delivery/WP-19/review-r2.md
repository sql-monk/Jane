# WP-19: незалежне рев'ю, останній раунд 2

**ВЕРДИКТ: accepted.** Агент `wp19_review`, не автор WP.
Frozen HEAD `ff12c6a435ebb5a1997e284d08bc4e7f1189eb4d`,
code `7a6904c5ec345815a389f0663e800d6887811f5a`.

Обидва початкові repro без змін, exit 0: SQLite/PG `EXPECTED422 handler_calls=0`;
same-process replay `{'from': 'current-request'}`, `replayed=True`.
SHA256 початкових scripts і точні commands збережені в manifest.

Самостійні normal/regression runs: 27 passed SQLite/Kit, 22 passed реальний PG split/json;
додаткові direct-sync generation, active-token cleanup, async cancellation — 9 passed.
Адресні API: runtime 2, assistant 1, registry 2, llm 1, orchestrator 1, web 1, Telegram 1 passed.
Разом R2: **67 passed**, усі normal runs exit 0.
Перевірено fingerprint до TTL, same-body takeover, different-body 422 без handler,
reuse після key TTL, legacy NULL lease, old complete/release, heartbeat нової generation.

ContextVar copy-on-write і capture token до to_thread коректні; фактичні consumers використовують
shared async entrypoints. HTTP shape незмінний.
Mypy 44 source files, no issues; Ruff All checks passed, 4 files already formatted.
Ownership actual base та integration: 95 changed / 0 outside; main має лише успадкований
coordinator wp-paths із бази. Hooks/settings не змінені.
JobStore fencing і storage rotation кодом R1-fix не зачеплені: доведені R1 mutants чинні
(lease check: 1 failed; close-immediately+forget-every-PUT: 2 failed).

Точні commands/exit/outputs у `.jane/wp19-review-r2/` координатора:
`wp19-review-r2.py`, `wp19-review-r2-results.json`, `wp19-review-r2-*.txt`;
додатковий harness `test_wp19_review_r2_extra.py`.

Справжні скорочені виводи (середину журналів пропущено):

```text
$ uvx --from rust-just just test jane-kit -k "idempotency or claim_of_a_stopped or heartbeat_renews_only or expired_keys_are_forgotten or migration_keeps_legacy"
===================== 27 passed, 276 deselected in 9.39s ======================
EXIT_CODE=0

$ uvx --from rust-just just test jane-kit -m integration -k "idempotency or concurrent_claims_of_one_key or take_over_fencing_and_heartbeat or migration_of_earlier_layouts or gc_deletes_expired_keys"
===================== 22 passed, 281 deselected in 16.41s =====================
EXIT_CODE=0

$ uv run --all-packages python C:\repos\Jane\.claude\worktrees\wp19\.jane\wp19-review-r1-r04.py
SQLITE EXPECTED422 handler_calls= 0
POSTGRES EXPECTED422 handler_calls= 0
EXIT_CODE=0

$ uv run --all-packages python C:\repos\Jane\.claude\worktrees\wp19\.jane\wp19-review-r1-same-process.py
idempotency claim was taken over before completion
idempotency claim was taken over before completion
SQLITE REPLAY= {'from': 'current-request'} replayed= True expected current-request; stale completion must be fenced
POSTGRES REPLAY= {'from': 'current-request'} replayed= True expected current-request; stale completion must be fenced
EXIT_CODE=0
```

Cleanup own project `jane-review-wp19-r2` у finally, down exit 0; containers, два volumes,
network видалені, Docker label checks порожні. Tracked checkout чистий, frozen SHA незмінний.
Повний CI/e2e — наступний gate координатора. Linux та зовнішні LLM/IdP/AWS/Telegram,
MongoDB/SQLServer/S3 цим review не перевірялися. Погоджений e2e transit root додає координатор після merge.
