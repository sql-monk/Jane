# jane-storage-minio — адаптер MinIO

Адаптер `minio` сервісу storage (WP-08). Реєстрація — entry points `jane.storage.adapters` → `minio`,
`jane.storage.packages` → `jane.storage-minio` ([механізм](../../README.md#адаптери)).

## Чому спільна основа з `s3`

MinIO реалізує S3 API, тож протокол зберігання (розкладка ключів, умовні записи, алгоритм коміту, відновлення після
збою) — той самий, що в [`jane-storage-s3`](../s3/README.md): `MinioAdapter` — підклас `S3Adapter` з іншим профілем.
Окремий код дублював би найризиковішу частину (атомарність) без жодної різниці в поведінці; натомість спільний код
перевіряється на двох незалежних реалізаціях S3 — MinIO (цей пакет) і SeaweedFS (пакет `s3`). Відмінності — лише
конфігурація:

| | `s3` | `minio` |
|---|---|---|
| `params.endpoint` | необов'язковий (AWS — з `region`) | обов'язковий |
| `addressing_style` | `auto` (virtual-hosted на AWS) | `path` |
| `create_bucket` типово | `false` (бакети AWS готують заздалегідь) | `true` |
| `sse` / `sse_kms_key_id` | так (SSE-S3 / SSE-KMS) | відхиляються (KMS MinIO — налаштування сервера) |

Окремий дистрибутив потрібен, щоб були окремі `kind`, пакет збереження `jane.storage-minio` і `required_connections`
з `kind: minio`.

## Підключення

```json
{"connection_id": "raw-minio", "kind": "minio",
 "params": {"endpoint": "http://minio:9000", "bucket": "jane-raw"},
 "secret_refs": {"access_key": "env:JANE_MINIO_ACCESS_KEY", "secret_key": "env:JANE_MINIO_SECRET_KEY"}}
```

Решта параметрів (`region`, `prefix`, `verify_tls`, `addressing_style`, `create_bucket`), розкладка ключів і ліміти —
як у [s3](../s3/README.md). Об'єкти віддаються як `s3://<bucket>/<key>` (`ContentRef` blob).

## Тести

```text
just up --project jane-wp08 minio
just integration --project jane-wp08 services/storage/adapters/minio   # C-01…C-16 на MinIO
just down -v --project jane-wp08
```

`tests/test_minio_profile.py` (профіль, без сервісів) входить у `just check`. Сценарії відновлення після збою,
неоднозначних відповідей і гонок спільного протоколу — у `adapters/s3/tests/test_recovery.py`, параметризовані
`s3` (SeaweedFS) і `minio` (MinIO): `just integration --project jane-wp08 services/storage/adapters/s3` з обома сервісами.
Обмеження умовного видалення на MinIO — див. [s3/README «Обмеження»](../s3/README.md#обмеження).
