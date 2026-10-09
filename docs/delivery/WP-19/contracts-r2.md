# WP-19: contract-guardian, повторний семантичний прохід

**Вердикт: compatible-with-actions** на `ff12c6a435ebb5a1997e284d08bc4e7f1189eb4d`,
code `7a6904c5ec345815a389f0663e800d6887811f5a`. Агент `wp19_contracts`, не автор WP.
Обидва runtime invariants виправлені; невиправлених контрактних порушень не знайдено.
Tracked checkout чистий; guardian нічого не змінював.

Fingerprint зберігається до key TTL, takeover атомарний і лише для збіжного fingerprint;
початковий expires_at не подовжується. ClaimTokens має окремий ContextVar кожного store,
map змінюється копіюванням. Async begin прив'язує token у caller після to_thread;
complete/release захоплюють конкретний token до dispatch. Heartbeat registry захищений і
працює за token: stale action прибирає лише власну generation. PG split/json мають одну логіку claim/fencing.
Фактичні service consumers викликають shared helper у caller task, додаткових HTTP fields не потрібно.

Самостійний high-level SQLite :memory: repro, exit 0:

```text
lease-expired/live-TTL other-body: 422 idempotency_key_reused handler_calls= 0
same-body takeover: original TTL preserved; current response/Location replayed
key-TTL expired other-body reuse: 201 handler_calls= 2
lease_until/complete: stale action fenced; heartbeat=1; replay=current with Location; completed heartbeat=0
lease_until/release: stale action fenced; heartbeat=1; replay=current with Location; completed heartbeat=0
expires_at/complete: stale action fenced; heartbeat=1; replay=current with Location; completed heartbeat=0
expires_at/release: stale action fenced; heartbeat=1; replay=current with Location; completed heartbeat=0
PASS: independent SQLite in-memory high-level R04 and same-process fencing checks
```

```text
uv run --frozen --no-sync pytest -q -p no:cacheprovider libs/jane-kit/tests/test_idempotency_claims.py libs/jane-kit/tests/test_idempotency.py libs/jane-kit/tests/test_stores_sqlite.py -m 'not integration'
29 passed, 16 deselected in 7.87s
exit 0

git diff f79c843..ff12c6a -- contracts/
# порожній вивід
git diff --name-only f79c843 ff12c6a -- contracts/ web/admin/src/api/generated/ infra/compose.yaml tests/e2e/compose.e2e.yaml
# порожній вивід
git diff --check f79c843 ff12c6a
# порожній вивід, exit 0
```

Незмінні shape/generated результати з власного першого проходу (точна ідентичність source підтверджена):
require-redocly exit 0; compat actual base/main/origin з oasdiff — 0 breaking, 0 warnings,
7 API ok; gen-api — 10 generated files up to date. Inventory з першого проходу чинний,
нових порушень автономності/власності даних/migrations/Problem/Job/Protocol немає.
PG conditional updates і caller context перевірено кодом; author 22 PG tests та original proofs
SQLite/PG перечитані, не оголошуються власним DB запуском guardian. Незалежний wp-reviewer R2 перевіряє PG окремо.

Погоджені cross-owner actions: A після merge додає runtime storage transit root до e2e overlay;
B-5 після merge прибирає storage sync/direct text/plain workaround. Це не breaking changes.
R18 закритий лише в межах files transit; S3/MinIO transit і producer download_url поза обсягом.
Full CI/e2e та приймання WP — наступні gates координатора; зовнішні LLM/IdP/AWS/Telegram не перевірені.
