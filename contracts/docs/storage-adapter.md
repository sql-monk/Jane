# Адаптери Storage

Storage використовує обраний адаптер для RAW, сутностей, історії та підтвердження доставки.

- [Підключення й заміна адаптера](../../docs/components/storage/integration.md).
- [Конфігурація Storage](../../docs/components/storage/configuration.md).
- [Публічні типи й Protocol-и](../../docs/components/storage/reference/types/README.md).
- [HTTP API Storage](../../docs/components/storage/reference/api/README.md).

## Спостереження за станом (WP-24)

Для операторів — [Storage: експлуатація](../../docs/components/storage/operations.md#стан-і-статистика-сховища-wp-24).

Storage Read API містить discovery підключень та `GET /v1/storage-status?connection_id=…`.
Це snapshot фонового `POST /v1/storage-status/checks` (202 Job, Idempotency-Key), локальний процесу; restart і зміна визначення
роблять його unknown. GET ніколи не обходить backend. `checked_at` показує свіжість,
`statistics.checked_at` — час останнього агрегату; null числові поля з `unavailable_reason` означають
невідоме значення. `scope=connection_objects` означає лише збережені об’єкти namespace цього connection,
а `total_size_bytes` — payload bytes з metadata, не disk usage. Filesystem підтримує explicit inventory
індексу metadata, зовнішні адаптери поки не підтримують aggregate. Інвентаризація не змінює StorageAdapter
Protocol: необов’язкова локальна capability `object_statistics` не є вимогою до сторонніх адаптерів.
API не приписує стан обробки матеріалу: це власність оркестратора.


Звичайний ConnectionTest не виконує inventory; його ok залишається результатом health.
Фонова statistics_check_failed зберігає успішну availability available та null counts.
Job read/cancel доступні handler:invoke, handler:test або connections:write; створення status check —
connections:write. JobRunner застосовує concurrency/queue/timeout/retention budgets.

Звичайний `POST /v1/connections/{id}/test` також оновлює availability/checked_at у cached snapshot, але скидає statistics до `null` із причиною `not_checked`, оскільки не виконує inventory. Щоб знову отримати counts/bytes, запускайте `POST /v1/storage-status/checks`.
