# Адаптер Storage: minio

Адаптер `minio` (пакет `jane-storage-minio`, пакет збереження `jane.storage-minio`): той самий протокол і код, що адаптер [s3](../s3/README.md), з профілем MinIO — `params.endpoint` обов'язковий, адресація `path`, бакет створюється автоматично, `sse` не приймається. Секрети: `access_key`, `secret_key`.

Параметри підключення, структура даних і обмеження — [адаптери Storage: minio](../../../../docs/components/storage/adapters.md#minio). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

Набір сумісності C-01…C-16 потребує сервісу dev-стеку:

```powershell
just up --project <проєкт> minio
just integration --project <проєкт> services/storage/adapters/minio
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
