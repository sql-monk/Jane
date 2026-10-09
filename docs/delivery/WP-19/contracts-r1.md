# WP-19: contract-guardian, прохід 1

Вердикт: **breaking** на frozen `f79c8438a840ce1214a071cc43d66a1c6a37c5d5`; code `14d0337`.
Незалежний агент `wp19_contracts`, не автор WP. База WP `2c70543`, main `37a30e2`, integration `2a1a821`.
Tracked checkout чистий, файли й Git-стан guardian не змінював.

## Блокуюче зауваження

SQLite stores/sqlite.py:153 і PG stores/postgres.py:218 видаляють in-progress claim після
закінчення lease до перевірки fingerprint. TTL ключа ще діє. Це порушує common.yaml:28 і ADR-0008:
інше тіло з тим самим ключем має отримати 422 idempotency_key_reused.

Незалежний in-memory SQLite repro через справжній run_idempotent:

```text
key TTL still live: True
remembered fingerprint: original-body
actual: 202 {'job_id': 'unexpected-new-job'} replayed= False
handler calls: ['executed changed body']
expected: 422 idempotency_key_reused; handler not called
```

PG має ту саму DELETE-before-compare за читанням коду. Guardian окремий PG repro не запускав;
незалежний wp-reviewer R1 підтвердив SQLite і реальний PG окремими repro.
Потрібне виправлення WP-19: fingerprint до TTL, атомарний same-body takeover з новим token/owner/lease,
regression для обох backend. Рецензент також підтвердив окрему same-process гонку token; її перевірить повторний прохід.

## Shape і споживачі

Actual delta contracts/: 3 files changed, 23 insertions(+), 6 deletions(-).
Storage response media types text/plain і */* додані, старі залишені; storage transit fallback описаний;
max_parallel_fetches уточнений як per-collection без зміни shape/minimum/defaults/hard_caps.
ContentRef/Protocol/x-jane-* власних змін WP-19 не мають. Reverse inherited integration diff не є WP delta;
при merge зберегти common/errors/assistant example/Protocol formatting/oasdiff pin з integration.

Updated/unaffected: storage API/adapters; kit media matcher/ContentWriter/Reader; collector producers;
runtime/orchestrator/assistant/LLM/registry; 10 admin generated files. R04 дефект зачіпає POST-сервіси
на нових shared stores і їхніх клієнтів; storage на власному store цим дефектом прямо не зачеплений.
Погоджені actions: A після merge додає e2e runtime storage transit root; B-5 прибирає sync/text workaround.
Ці actions не breaking. Files-only R18: S3/MinIO transit і producer download_url поза обсягом.
Спільної міжсервісної БД або залежності автономних сервісів від orchestrator не додано.
Решта behavioral table, terminal/cancellation semantics, secret policy і migrations сумісні за ручним проходом.
PG migrations guardian перевірив кодом, SQLite legacy tests виконав.

## Справжні підсумки перевірок guardian

```text
uv run contracts/tools/check_contracts.py --require-redocly
[ok] Redocly lint: ok (Woohoo! Your API descriptions are valid. 🎉)
Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=118,
openapi_documents=8, openapi_examples=534, operations=118, python_files=3,
schema_examples=46, schemas=16
All contract checks passed.
exit 0

uv run contracts/tools/compat.py --base 2c70543
0 breaking, 0 warning(s).
exit 0

uv run contracts/tools/compat.py --base origin/codex/jane-integration --oasdiff
oasdiff assistant.v1.yaml: ok
oasdiff collector.v1.yaml: ok
oasdiff handler.v1.yaml: ok
oasdiff llm.v1.yaml: ok
oasdiff orchestrator.v1.yaml: ok
oasdiff registry.v1.yaml: ok
oasdiff storage.v1.yaml: ok
0 breaking, 0 warning(s).
exit 0

uv run contracts/tools/compat.py --base main --oasdiff
# ті самі 7 oasdiff documents: ok; середину скорочено
0 breaking, 0 warning(s).
exit 0

node web/admin/scripts/gen-api.mjs --check
gen-api: 10 generated files are up to date
exit 0

uv run --frozen --no-sync pytest -q -p no:cacheprovider libs/jane-kit/tests/test_contracts.py libs/jane-kit/tests/test_jobs.py libs/jane-kit/tests/test_content_writer.py libs/jane-kit/tests/test_stores_sqlite.py
35 passed in 5.49s
exit 0

uv run --frozen --no-sync pytest -q -p no:cacheprovider services/storage/tests/test_reprocess_reads.py services/assistant/tests/test_storage_material.py
21 passed in 8.32s
exit 0
```

Один початковий harness мав TypeError migrate(c); після правильного migrate() наведений runtime defect відтворено.
Full local just check/e2e не запускали; Linux і зовнішні LLM/IdP/AWS/Telegram не перевірені цим проходом.
