# Адаптер Storage: mongodb

Адаптер `mongodb` (пакет `jane-storage-mongodb`, пакет збереження `jane.storage-mongodb`, PyMongo `AsyncMongoClient`): колекції сутностей, історії, доставок, об'єктів і фрагментів RAW; коміт — CAS одного документа з полем `pending`, реплікасет не потрібен. Секрети (необов'язкові): `username`, `password`.

Параметри підключення, структура даних і обмеження — [адаптери Storage: mongodb](../../../../docs/components/storage/adapters.md#mongodb). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

Набір сумісності C-01…C-16 потребує сервісу dev-стеку:

```powershell
just up --project <проєкт> mongodb
just integration --project <проєкт> services/storage/adapters/mongodb
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
