# jane-storage-s3 — адаптер S3

Адаптер `s3` сервісу storage (WP-08), boto3. Реєстрація — entry points `jane.storage.adapters` → `s3`,
`jane.storage.packages` → `jane.storage-s3` ([механізм](../../README.md#адаптери)). Цей самий код — основа адаптера
[`minio`](../minio/README.md) (інший профіль, той самий протокол).

## Підключення

```json
{"connection_id": "raw-s3", "kind": "s3",
 "params": {"bucket": "jane-raw", "region": "eu-central-1", "sse": "aws:kms", "sse_kms_key_id": "alias/jane"},
 "secret_refs": {"access_key": "env:JANE_S3_ACCESS_KEY", "secret_key": "env:JANE_S3_SECRET_KEY"}}
```

| Параметр | Типово | Опис |
|---|---|---|
| `bucket` | — (обов'язковий) | бакет |
| `region` | `us-east-1` | регіон (для AWS визначає endpoint) |
| `endpoint` | — | URL S3-сумісного сервісу (для AWS не потрібен) |
| `addressing_style` | `auto` | `auto` / `path` / `virtual` |
| `create_bucket` | `false` | `ensure_schema` створює відсутній бакет |
| `sse`, `sse_kms_key_id` | — | шифрування на боці сервера: `AES256` або `aws:kms` |
| `verify_tls` | `true` | `false` або шлях до CA-bundle |
| `prefix` | — | префікс ключів; параметр етапу `prefix` його перекриває |

Секрети: `access_key`, `secret_key`, необов'язковий `session_token`. Без ключів адаптер не відкривається (не бере
облікових даних з оточення).

## Розкладка й атомарність

| Ключ (у бакеті, під `<prefix>/`) | Вміст |
|---|---|
| `entities/<entity_type>/<sha256(canonical_key)>.json` | `EntitySnapshot` (+ `pending` — подія історії цієї версії, доки її не перенесено) |
| `history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json` | `HistoryEvent` |
| `deliveries/<sha256(delivery_key)>.json` | `DeliveryRecord` (+ `claimed_at`) |
| `objects/<object_key>` + `objects/<object_key>.meta.json` | байти (`x-amz-meta-sha256`, `Content-Type` = медіатип) + `ObjectRecord` |
| `index/objects/<object_id>.json` | `ObjectRecord` (пошук за `object_id`, перелік) |

Лише умовні `PutObject` (`If-None-Match: *` — створити, `If-Match: <ETag>` — замінити), які мають AWS S3, MinIO і
SeaweedFS. `commit_entity`:

1. **Заявка доставки** — `PUT deliveries/…` з `If-None-Match: *`. 412 → ключ уже є: завершена доставка →
   `DUPLICATE`; заявка коміту, що ще триває → `CONFLICT` (ядро повторить); «мертва» заявка (її коміт програв гонку
   або впав понад `lock_stale_ms` тому) видаляється, і заявка повторюється.
2. **CAS знімка** — `PUT entities/…` з `If-Match` знімка, прочитаного на `expected_version` (`If-None-Match: *` для
   нової сутності). Новий знімок містить свою подію історії в `pending`, тож запис знімка — **єдина точка коміту**:
   стан, версія й подія з'являються разом. 412 → заявку видаляємо (компенсація) → `CONFLICT`.
3. **Перенесення** — `PUT history/…/<version>.json` і зняття `pending` (`If-Match`). Збій тут нічого не втрачає:
   читачі й наступний коміт спершу переносять `pending`.

Порівняно з порядком у contracts/docs/storage-adapter.md (доставка → історія → знімок) історія пишеться після CAS:
так осиротіла подія історії не блокує наступних комітів і не потребує перезапису «чужої» версії (див. звіт WP-08).
RAW: байти `If-None-Match: *` (гонка з іншим вмістом → `AdapterError(retryable=False)`), потім `.meta.json`
`If-None-Match: *` (точка коміту об'єкта), потім індекс.

## Ліміти

| Параметр | Типово | Де задається |
|---|---|---|
| `connect_timeout_ms` / `command_timeout_ms` | 10000 / 30000 | `params` підключення або `JANE_STORAGE_LIMITS__ADAPTERS__…` |
| `pool_max_size` | 10 | те саме (пул HTTP-з'єднань boto3) |
| `lock_stale_ms` | 120000 | те саме — вік заявки доставки без знімка, після якого вона вважається залишком збою |
| `retry_max_attempts` | 3 | `params` підключення (усього спроб одного запиту в botocore, режим `standard`) |

## Обмеження

- `list_entities` / `list_objects` читають документи за префіксом (O(n) GET на сторінку з фільтрами); порядок —
  за ключем (хеш канонічного ключа / `object_id`), а не за часом.
- botocore може читати власні змінні оточення (`AWS_ENDPOINT_URL`, `~/.aws/config`) для незаданих параметрів;
  у контейнері сервісу їх не задавати.
- Перевірено на SeaweedFS 4.47 (dev-стек). Реальний AWS S3 — **не перевірено на реальному сервісі**.

## Тести

```text
just up --project jane-wp08 s3
just integration --project jane-wp08 services/storage/adapters/s3   # C-01…C-16 + відновлення після збою
just down -v --project jane-wp08
```

`tests/test_s3_config.py` (валідація підключення, без сервісів) входить у `just check`.
