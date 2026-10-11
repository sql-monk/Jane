# jane_orchestrator.idempotency

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.idempotency.idempotency_store](#jane_orchestratoridempotencyidempotency_store)

## jane_orchestrator.idempotency.idempotency_store

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/idempotency.py:18](../../../../../../services/orchestrator/src/jane_orchestrator/idempotency.py#L18).

```python
def idempotency_store(db: Database, owner: str, claims: ClaimLimits) -> PgIdempotencyStore:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `db` | `Database` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |
| `claims` | `ClaimLimits` | `—` | positional-or-keyword |

Результат: `PgIdempotencyStore`.
