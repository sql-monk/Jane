# Адаптер Storage: mongodb

Адаптер `mongodb` (пакет `jane-storage-mongodb`, пакет збереження `jane.storage-mongodb@2.0.0`, PyMongo `AsyncMongoClient`) кладе кожен тип сутності в окрему колекцію `<prefix><entity_type>`, наприклад `product_book`. Історія типу — у `<prefix><entity_type>.history`. Службові колекції `<prefix>_deliveries`, `<prefix>_objects` і `<prefix>_object_chunks` з іменами типів не перетинаються. Префікс `prefix` типово порожній.

Коміт сутності — запис наміру в `_deliveries` і CAS одного документа з полем `pending`; реплікасет не потрібен. Адаптер підтримує каталог типів, серверний пошук і статистику сховища (`EntityDiscoveryAdapter`, `StorageStatisticsAdapter`). Секрети (необов'язкові): `username`, `password`.

Розкладку 1.x (`jane_entities`, `jane_entity_history`, …) версія 2 не читає й не переносить.

Параметри підключення, розкладка, механізм ключів доставки, індекси, пошук, статистика й обмеження — [адаптери Storage: mongodb](../../../../docs/components/storage/adapters.md#mongodb). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

`tests/test_mongo_config.py` не потребує сервісів і входить у `just check`: реєстрація, параметри підключення, імена колекцій.

Інтеграційні тести потребують сервісу dev-стеку:

- `tests/test_compat.py` — набір сумісності C-01…C-16, розкладка й ліниві індекси, каталог, пошук і статистика;
- `tests/test_recovery.py` — відновлення після збою й гонки двох екземплярів з одним ключем доставки.

```powershell
just up --project <проєкт> mongodb
just integration --project <проєкт> services/storage/adapters/mongodb
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
