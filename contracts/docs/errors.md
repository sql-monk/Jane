# Помилки Jane

API повертає `application/problem+json`. Клієнт приймає рішення за `code`, HTTP-статусом і `retryable`; текст `detail` призначений для читача.

## Формат

Обов’язкові поля: `type`, `title`, `status`, `code`. Поля `errors`, `trace_id`, `retry_after_seconds` і `details` додають контекст. Повний контракт — [Problem](../schemas/common/problem.schema.json).

```json
{"type":"urn:jane:problem:limit_exceeded","title":"Limit exceeded","status":422,"code":"limit_exceeded","retryable":false}
```

## Каталог кодів

Нижче — типові значення з [KNOWN_CODES](../../libs/jane-kit/src/jane_kit/errors.py). Конкретна операція може явно задати інший статус або `retryable`; перевіряй відповідь та [OpenAPI](../openapi/).

| Код | HTTP | retryable | Значення |
|---|---|---|---|
| `bad_request` | 400 | `false` | Некоректний запит або JSON |
| `validation_failed` | 422 | `false` | Запит не відповідає схемі |
| `unauthenticated` | 401 | `false` | Немає чинної автентифікації |
| `forbidden` | 403 | `false` | Недостатньо прав |
| `not_found` | 404 | `false` | Ресурс відсутній |
| `method_not_allowed` | 405 | `false` | HTTP-метод не підтримується |
| `conflict` | 409 | `false` | Конфлікт поточного стану |
| `version_exists` | 409 | `false` | Версія пакета вже існує |
| `idempotency_in_progress` | 409 | `true` | Операція з цим ключем ще виконується |
| `job_not_cancellable` | 409 | `false` | Job уже не можна скасувати |
| `upstream_conflict` | 409 | `false` | Конфлікт у залежному сервісі |
| `precondition_failed` | 412 | `false` | Передумова не виконана |
| `precondition_required` | 428 | `false` | Потрібна передумова |
| `idempotency_key_reused` | 422 | `false` | Ключ повторено з іншим запитом |
| `payload_too_large` | 413 | `false` | Перевищено розмір запиту |
| `unsupported_media_type` | 415 | `false` | Тип вмісту не підтримується |
| `limit_exceeded` | 422 | `false` | Перевищено ефективний ліміт |
| `rate_limited` | 429 | `true` | Тимчасовий ліміт частоти |
| `budget_exhausted` | 429 | `false` | Бюджет вичерпано |
| `secret_detected` | 422 | `false` | Виявлено секрет у пакеті |
| `dependency_not_allowed` | 422 | `false` | Залежність заборонено |
| `digest_mismatch` | 422 | `false` | Хеш не збігається |
| `schema_mismatch` | 422 | `false` | Дані не відповідають очікуваній схемі |
| `out_of_scope` | 422 | `false` | Операція поза дозволеною областю |
| `access_denied_by_policy` | 403 | `false` | Доступ заборонено політикою |
| `source_unavailable` | 502 | `true` | Джерело недоступне |
| `upstream_unavailable` | 502 | `true` | Залежний сервіс недоступний |
| `internal_error` | 500 | `true` | Внутрішня помилка |
| `not_implemented` | 501 | `false` | Операцію не реалізовано |
| `service_unavailable` | 503 | `true` | Сервіс тимчасово недоступний |
| `timeout` | 504 | `true` | Перевищено час очікування |

## Повторні спроби

За `retryable: true` повторюй ту саму операцію з тим самим `Idempotency-Key`, дотримуючись `Retry-After` або `retry_after_seconds`. Змінений запит потребує нового ключа. При `false` спочатку усунь причину: конфігурацію, схему, права або бюджет.

Асинхронна відповідь `202` означає прийняття job; підсумковий стан читається через API jobs. [Виконання й надійність](../../docs/architecture/execution.md) пояснює повтори та підтвердження доставки.

Діагностика: [проблеми платформи](../../docs/operations/troubleshooting.md), [jane-kit errors](../../docs/components/jane-kit/reference/types/generated/jane_kit.errors.md).
