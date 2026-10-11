# Jane Kit: залежності

Jane Kit встановлюється як Python-пакет у застосунок-власник.

## Обов’язкові пакети

Python — `>=3.12`; версія бібліотеки — `0.1.0`. [pyproject.toml](../../../libs/jane-kit/pyproject.toml) задає FastAPI, Pydantic 2, pydantic-settings, Uvicorn, httpx, PyYAML, jsonschema, referencing, prometheus-client і PyJWT із криптографією. Відтворюваний набір залежностей checkout фіксує [uv.lock](../../../uv.lock).

## Опційні залежності

| Механізм | Що потрібне | За недоступності |
|---|---|---|
| PostgreSQL stores | Extra `postgres`: psycopg із binary і pool; власна PostgreSQL БД | Сховище не відкриється; health check має показати недоступність |
| JWT | JWKS endpoint, issuer, audience | Відомі кешовані ключі тимчасово працюють; без ключів — 503 |
| Генерація моделей | datamodel-code-generator у середовищі або через uvx | Генерація повертає помилку |
| Перевірка контрактів | Каталог `contracts/` або `JANE_CONTRACTS_DIR` | Перевірки потребують явно доступних схем |
| Blob-контент | Реалізація blob loader/store | URI сам по собі не надає доступу до bytes |

```powershell
uv sync --package jane-kit --extra postgres
```

## Заміна реалізації

`JobRunner` приймає `JobStore`; ідемпотентність працює через `IdempotencyStore`. Оберіть in-memory, SQLite чи PostgreSQL реалізацію або власний клас відповідного Protocol. Перевірте атомарні claim, lease та fencing; просте збереження JSON не замінює їхніх гарантій.

Orchestrator, Registry та Storage не є залежностями бібліотеки.
