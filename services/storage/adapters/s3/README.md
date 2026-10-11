# Адаптер Storage: s3

Адаптер `s3` (пакет `jane-storage-s3`, пакет збереження `jane.storage-s3`, boto3 ≥ 1.35.66): сутності, історія, записи доставок і RAW — об'єкти в бакеті `params.bucket`. Атомарність — лише умовні `PutObject` (`If-None-Match: *`, `If-Match`). Секрети: `access_key`, `secret_key`, необов'язковий `session_token`. Цей самий код використовує адаптер [minio](../minio/README.md).

Параметри підключення й обмеження — [адаптери Storage: s3](../../../../docs/components/storage/adapters.md#s3). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Розкладка й атомарність

Ключі в бакеті (`entities/`, `history/`, `deliveries/`, `objects/`, `index/objects/`), три кроки `commit_entity` (заявка доставки, CAS знімка з подією в `pending`, перенесення в історію) і межа умовного видалення в MinIO описано в [адаптери Storage: розкладка й атомарність](../../../../docs/components/storage/adapters.md#розкладка-й-атомарність).

## Тести

Набір сумісності C-01…C-16 запускається на SeaweedFS — S3-сумісному замінникові, незалежному від MinIO; на AWS S3 не перевірявся:

```powershell
just up --project <проєкт> s3
just integration --project <проєкт> services/storage/adapters/s3
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
