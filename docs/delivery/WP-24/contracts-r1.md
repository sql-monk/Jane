# WP-24 — contract-guardian R1

Рев’ю незалежного субагента `guardian24`, інтеграційна ревізія `81ccee2`, база `1eb6dbd`. Вердикт: **breaking** за семантикою; структурна сумісність без порушень.

## Блокери

1. Повна інвентаризація metadata в синхронному `POST /connections/{id}/test` обмежувалася лише `request_timeout_ms` (30000 ms у профілях), а не `sync_response_max_ms` (25000 ms). Контракт не описував `202 + Job`. Потрібна окрема асинхронна операція інвентаризації.
2. Помилка статистики змінювала чинний `ConnectionTestResult.ok` на false після успішного `adapter.health()`. Потрібно зберегти результат перевірки доступності й окремо відобразити помилку статистики.

## Перевірки й справжній вивід

```text
uv run --no-sync contracts/tools/check_contracts.py --require-redocly
[ok] JSON Schema meta-validation and $refs
[ok] OpenAPI 3.1 validation
[ok] Jane API conventions and inline examples
[ok] Standalone schema examples
[ok] Python interfaces compile
[ok] Mock server can serve every operation
[ok] Autonomous APIs do not reference orchestrator/assistant contracts
[ok] Redocly lint: ok (Woohoo! Your API descriptions are valid. 🎉)
Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=124,
openapi_documents=8, openapi_examples=569, operations=124,
python_files=3, schema_examples=46, schemas=16
All contract checks passed.
exit 0

uv run contracts/tools/compat.py --base 1eb6dbd --oasdiff
No breaking changes to report, but the specs are different.
0 breaking, 0 warning(s).
exit 0

node scripts/gen-api.mjs --check
gen-api: 10 generated files are up to date
exit 0

uv run --no-sync pytest libs/jane-kit/tests/test_auth_scopes.py -q -p no:cacheprovider
33 passed in 1.34s
exit 0
```

## Дії координатора

WP-24 повернуто на виправлення: нова операція `POST /v1/storage-status/checks` з `Idempotency-Key`, `202`, `Job` і `Location`. WP-25 переведе «Перевірити зараз» на нову операцію та опитування job. Чинний connection test збереже результат health; cached GET статусу залишається коротким. Після виправлення — guardian R2 і незалежний WP-reviewer.
