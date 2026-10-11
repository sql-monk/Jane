# Модель помилок і каталог кодів

Усі API Jane повертають помилки як `application/problem+json` (RFC 9457) за схемою
[`schemas/common/problem.schema.json`](../schemas/common/problem.schema.json).

```json
{
  "type": "urn:jane:problem:validation_failed",
  "title": "Validation failed",
  "status": 422,
  "code": "validation_failed",
  "retryable": false,
  "errors": [{"pointer": "/stages/1/handler/version", "code": "invalid_format", "message": "must be an exact semantic version"}],
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

Правила:

- `type` = `urn:jane:problem:<code>`; `code` — стабільний машинний код; рішення клієнт приймає за `code`.
- `retryable: true` — операцію можна повторити з тим самим `Idempotency-Key` (з урахуванням `Retry-After`).
- `detail` не містить секретів, токенів, вмісту матеріалів чи промптів.
- Невідомий клієнтові `code` обробляється за HTTP-статусом (`5xx`, `429` — повторювані; інші `4xx` — ні).
- Новий код додається лише в `KnownErrorCode` схеми й у цю таблицю (зміна `contracts/` через координатора).

| code | HTTP | retryable | Коли |
|---|---|---|---|
| `bad_request` | 400 | ні | Тіло не розбирається (не JSON, неправильне кодування) |
| `validation_failed` | 422 | ні | Тіло або параметри не відповідають схемі; деталі в `errors[]` |
| `unauthenticated` | 401 | ні | Немає токена або токен недійсний |
| `forbidden` | 403 | ні | Бракує scope або ролі |
| `not_found` | 404 | ні | Ресурсу немає |
| `method_not_allowed` | 405 | ні | Метод не підтримується |
| `conflict` | 409 | ні | Ресурс уже існує або стан не дозволяє дію |
| `version_exists` | 409 | ні | Версія пакета вже опублікована (версії незмінні) |
| `idempotency_in_progress` | 409 | так | Запит із цим `Idempotency-Key` ще виконується |
| `job_not_cancellable` | 409 | ні | Job цього виду не можна скасувати |
| `upstream_conflict` | 409 | ні | Конфлікт під час перенесення змін батьківського пакета у форк |
| `precondition_failed` | 412 | ні | `If-Match` не збігається з ETag |
| `precondition_required` | 428 | ні | Для зміни ресурсу потрібен `If-Match` |
| `idempotency_key_reused` | 422 | ні | Той самий ключ з іншим тілом запиту |
| `payload_too_large` | 413 | ні | Тіло більше за ліміт — передайте вміст як blob |
| `unsupported_media_type` | 415 | ні | Непідтримуваний Content-Type |
| `limit_exceeded` | 422 | ні | Запит перевищує ефективний ліміт або hard cap (`details.limit`, `details.path`) |
| `rate_limited` | 429 | так | Перевищено частоту; заголовок `Retry-After` |
| `budget_exhausted` | 429 | ні* | Вичерпано бюджет LLM (`details.period`). *Календарне вікно (`day`/`week`/`month`) скидається: повтор має сенс після `details.period_resets_at`. Для `period: run` і `total` вікно не скидається (`period_resets_at` немає): повтор того самого запиту має сенс лише після збільшення бюджету (новий запуск має власне вікно `run`) — як повторна доставка в [handler-packages.md](handler-packages.md) |
| `secret_detected` | 422 | ні | У пакеті, параметрах чи правилах знайдено схоже на секрет значення |
| `dependency_not_allowed` | 422 | ні | Залежність пакета відсутня в профілі runtime |
| `digest_mismatch` | 422 | ні | Дайджест пакета не збігається з очікуваним |
| `schema_mismatch` | 422 | ні | Дані не відповідають схемі контракту пакета |
| `out_of_scope` | 422 | ні | URL поза межами обходу |
| `access_denied_by_policy` | 403 | ні | Заборонено `robots.txt` або політикою доступу |
| `source_unavailable` | 502 | так* | Джерело (сайт, Telegram) повернуло помилку або недоступне; `details.http_status` (web) або `details.reason` (Telegram). *Окремі випадки, які повтор не змінить (канал недоступний — `channel_unavailable`, сесію відхилено — `account_unauthorized`), мають `retryable: false`: рішення про повтор приймайте за полем `retryable` відповіді |
| `upstream_unavailable` | 502 | так | Недоступний сусідній сервіс Jane або зовнішній провайдер (LLM, сховище) |
| `internal_error` | 500 | так | Непередбачена помилка |
| `not_implemented` | 501 | ні | Можливість не реалізована цим сервісом (див. `/v1/info` capabilities) |
| `service_unavailable` | 503 | так | Сервіс перевантажений або не готовий |
| `timeout` | 504 | так | Операція не вклалась у тайм-аут |

Помилки виконання обробника (виняток у коді екстрактора, порушення пісочниці, невідповідність
схемі) — **не HTTP-помилки**: виклик завершується `200` з `HandlerResult.status = failed` і
`failure.kind`, див. [`handler-result.schema.json`](../schemas/handler-result.schema.json).
HTTP-помилка означає, що виклик не відбувся (невалідний запит, пакет не знайдено, сервіс недоступний).
