# Адаптер Storage: filesystem

Адаптер `filesystem` (пакет `jane-storage-files`, пакет збереження `jane.storage-files`): RAW як файли, сутності, історія й записи доставок — JSON-документи в каталозі `params.base_path`. Секретів і мережевих адрес не потребує.

Параметри підключення, структура даних і обмеження — [адаптери Storage: filesystem](../../../../docs/components/storage/adapters.md#filesystem). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

Набір сумісності не потребує зовнішніх сервісів і входить у тести Storage:

```powershell
just test storage
```
