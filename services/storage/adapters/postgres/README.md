# Адаптер Storage: postgresql

Адаптер `postgresql` (пакет `jane-storage-postgres`, пакет збереження `jane.storage-postgresql`, драйвер asyncpg): таблиці `<prefix>entities`, `<prefix>entity_history`, `<prefix>deliveries`, `<prefix>objects`; коміт сутності — одна транзакція. Секрети: `username`, `password`.

Параметри підключення, структура даних і обмеження — [адаптери Storage: postgresql](../../../../docs/components/storage/adapters.md#postgresql). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Розкладка news

Параметр підключення `"layout": "news"` (разом з окремою схемою, наприклад `"schema": "news"`) додає до таблиць рушія реляційну проєкцію `article`, `post`, `news_article` і `news_event`. Її пише `commit_entity` у тій самій транзакції, а міграції застосовує `ensure_schema`. Код — пакет [news_layout](src/jane_storage_postgres/news_layout/__init__.py), опис таблиць і правил — [розкладка news](../../../../docs/components/storage/adapters.md#розкладка-news).

Перебудова проєкції з усіх збережених знімків (наприклад, після нової міграції розкладки). Пароль передається лише змінною середовища:

```powershell
$env:PGPASSWORD = "<пароль>"
uv run python -m jane_storage_postgres.news_layout rebuild --host <host> --port 5432 --database jane_storage_results --user <user> --schema news
```

## Тести

Юніт-тести мапінгу розкладки news (`tests/test_news_layout_mapping.py`) працюють без бази. Набір сумісності C-01…C-16 (також із `layout: "news"`) і тести розкладки (`tests/test_news_layout.py`) потребують сервісу dev-стеку:

```powershell
just up --project <проєкт> postgres
just integration --project <проєкт> services/storage/adapters/postgres
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
