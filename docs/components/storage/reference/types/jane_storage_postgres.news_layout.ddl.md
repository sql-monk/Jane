# Модуль `jane_storage_postgres.news_layout.ddl`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/ddl.py](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/ddl.py). Не редагуйте вручну.

DDL of the ``news`` layout: numbered migrations over ``<schema>``.

Every migration is applied once, in order, in the transaction of ``ensure_schema`` and recorded in ``<schema>.jane_layout_migrations``. A released migration is never edited: a change of the layout is a new migration (plus ``rebuild`` when existing rows have to be laid out again).

Statements are templates with one placeholder, ``{s}`` — the quoted schema (validated by the adapter).

## Функції

### Функція `migrations_table_sql`

```python
def migrations_table_sql(schema: str) -> str: ...
```

Код: [ddl.py:297](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/news_layout/ddl.py#L297).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `MIGRATIONS` | `tuple[tuple[int, str], ...]` | `((1, _V1),)` | ``(version, statements)`` in application order; versions start at 1 and grow by one. |
| `MIGRATIONS_TABLE` | — | `'jane_layout_migrations'` |  |
| `PROJECTION_TABLES` | `tuple[str, ...]` | `('source', 'tag', 'topic', 'named_entity', 'article', 'article_tag', 'post', 'po` | Tables of the projection (cleared together by ``rebuild``); dictionaries first. |
| `VIEWS` | `tuple[str, ...]` | `('news_article_with_event', 'article_analysis')` |  |
