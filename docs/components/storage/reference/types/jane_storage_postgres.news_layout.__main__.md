# Модуль `jane_storage_postgres.news_layout.__main__`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/__main__.py](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/__main__.py). Не редагуйте вручну.

CLI of the ``news`` layout: ``python -m jane_storage_postgres.news_layout rebuild --schema news …``.

Connection parameters come from arguments or the libpq environment variables (``PGHOST``, ``PGPORT``, ``PGDATABASE``, ``PGUSER``, ``PGSSLMODE``). The password is read only from an environment variable (``--password-env``, default ``PGPASSWORD``), never from the command line. Prints a JSON summary.

## Функції

### Функція `main`

```python
def main(argv: Sequence[str] | None = None) -> int: ...
```

Код: [__main__.py:91](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/__main__.py#L91).
