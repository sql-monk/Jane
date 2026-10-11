# WP-24 — contract-guardian R2

Незалежний `guardian24`, ревізія `0f77194`, база `1eb6dbd`; виправлення від `bc518f9`. Вердикт **compatible-with-actions**, блокерів R1 більше немає, нових не виявлено.

- Inventory окремим POST `/v1/storage-status/checks` із Idempotency-Key, 202 Job/Location і replay.
- Existing ConnectionTest health-only; statistics failure не змінює availability здорового адаптера.
- ETag перевірено перед публікацією snapshot, scope tables exact, Python Protocol незмінено.
- Cooperative cancellation filesystem scan встановлює stop event через finally.

Справжній підсумковий вивід незалежних перевірок:

```text
uv run contracts/tools/check_contracts.py --require-redocly
Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=127,
openapi_documents=8, openapi_examples=584, operations=127,
python_files=3, schema_examples=46, schemas=16
All contract checks passed.
exit 0

uv run contracts/tools/compat.py --base 1eb6dbd --oasdiff
No breaking changes to report, but the specs are different.
0 breaking, 0 warning(s).
exit 0

uv run contracts/tools/compat.py --base bc518f9
0 breaking, 0 warning(s).
exit 0

node scripts/gen-api.mjs --check
gen-api: 10 generated files are up to date
exit 0

uv run --no-sync pytest libs/jane-kit/tests/test_auth_scopes.py services/storage/tests/test_storage_status.py services/storage/tests/test_auth.py services/storage/tests/test_contract.py services/storage/tests/test_secret_policy.py -q -p no:cacheprovider
76 passed in 14.10s
exit 0
```

## Дії після verdict

1. WP-25 async consumer завершено `83a6b2`, інтегровано `32885b8`: запуск фонового check, опитування job, terminal snapshot refresh; окреме незалежне R2.
2. Координатор додав до storage-adapter docs і admin README точний опис: health-only ConnectionTest оновлює доступність, скидає statistics у null/not_checked; новий async check відновлює counts. Лише документальна зміна.
3. Координаторський browser smoke виконав реальний Filesystem Storage HTTP сценарій: **1 passed (55.7s)**, assertions точного payload і реальних counts/bytes, snapshot після reload. Інші API — контрактні моки.
