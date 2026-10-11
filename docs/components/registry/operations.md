# Експлуатація Registry

Довговічному сервісу потрібні власна PostgreSQL і постійний blob backend. Кілька Registry поділяють ці backend та shared job/idempotency stores.

## Спостереження й оновлення

GET /v1/health перевіряє залежності; GET /v1/info показує capabilities/limits; /metrics — Prometheus. Збережіть package_id, version, digest, code та trace_id для діагностики; секрети не логуються.

![Процес оператора Registry](../../diagrams/registry/operator-process.light.png)

[Темна тема](../../diagrams/registry/operator-process.dark.png) · [Draw.io](../../diagrams/registry/operator-process.drawio)

Перед оновленням зробіть узгоджений backup DB/blob, розгорніть ревізію, перевірте health та archive відомого digest. PostgresStore мігрує схему при open. Автоматичний downgrade не гарантується. Env/backend/limits застосовуються після restart; runtime-профілі мають власний refresh interval.

## Backup та відновлення

Копіюйте власну PostgreSQL, blob bucket/root, конфігурацію та secret refs. DB без архівів не дозволяє виконати або експортувати версії. Після restore звірте metadata, archive endpoint, ETag і байти перед відновленням запису.

Export дає переносимі пакети, але не є повною копією ACL, історії статусів і job. Blobs не видаляються лише за віком: потрібна звірка з версіями й backup policy.

## Збій екземпляра

Heartbeat поновлює PostgreSQL claims/job leases. Прострочений in-progress ключ може забрати інший екземпляр; expired job позначається failed із retryable error. Клієнт читає стан і вирішує повторити команду. TTL обмежує replay.

| Проблема | Дія |
|---|---|
| Метадані є, blob відсутній | Відновити точні байти digest із backup |
| ETag змінився | Перечитати metadata перед If-Match |
| Memory process втрачено | Каталог треба створити заново |
| S3 недоступний | Endpoint, bucket, credentials і права |
| Secret detected | Прибрати секрет; пакет відхилено |

AWS/S3 на зовнішньому account і багатовузлове recovery не перевірено на реальному сервісі в цьому пакеті.
