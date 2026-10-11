# Модуль `jane_orchestrator.idempotency`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/idempotency.py](../../../../../services/orchestrator/src/jane_orchestrator/idempotency.py). Не редагуйте вручну.

``Idempotency-Key`` storage in the orchestrator DB, so several API instances share it.

jane-kit's shared :class:`jane_kit.stores.postgres.PgIdempotencyStore` (R17) on the table ``idempotency_keys`` (migration 7 added the claim ``owner``/``token``/``lease_until``): a claim of a stopped instance is taken over after ``limits.claims.in_progress_lease_ms``; a live instance renews its claims (``heartbeat_interval_ms``); a request whose claim was taken over cannot overwrite the new one.

## Функції

### Функція `idempotency_store`

```python
def idempotency_store(db: Database, owner: str, claims: ClaimLimits) -> PgIdempotencyStore: ...
```

Код: [idempotency.py:18](../../../../../services/orchestrator/src/jane_orchestrator/idempotency.py#L18).
