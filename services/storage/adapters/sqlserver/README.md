# Адаптер Storage: sqlserver

Адаптер `sqlserver` (пакет `jane-storage-sqlserver`, пакет збереження `jane.storage-sqlserver`, драйвер pymssql з FreeTDS — ODBC не потрібен): ті самі чотири таблиці з ключами за SHA-256; коміт сутності — один пакет T-SQL у транзакції. Секрети: `username`, `password`.

Параметри підключення, структура даних і обмеження — [адаптери Storage: sqlserver](../../../../docs/components/storage/adapters.md#sqlserver). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

Набір сумісності C-01…C-16 потребує сервісу dev-стеку:

```powershell
just up --project <проєкт> sqlserver
just integration --project <проєкт> services/storage/adapters/sqlserver
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
