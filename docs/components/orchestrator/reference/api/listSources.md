# GET /v1/sources

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L43). Не редагуйте вручну.

**Джерела**

| Властивість | Значення |
|---|---|
| operationId | `listSources` |
| Метод і шлях | `GET /v1/sources` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | sources |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `kind` | query | `string` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка джерел. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `source` | так |  |
| `items[].source_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `items[].title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `items[].description` | `string` | ні | макс. довжина `4000` |
| `items[].locator` | `object` | так |  |
| `items[].locator.url` | `string` (uri) | ні |  |
| `items[].locator.telegram_username` | `string` | ні |  |
| `items[].locator.telegram_channel_id` | `string` | ні |  |
| `items[].collector_rules` | `package-ref` | ні | Версія правил колектора за замовчуванням (пакет kind=collector-rules). Може бути відсутня до завершення підключення джерела. |
| `items[].collector_rules.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].collector_rules.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `items[].collector_rules.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `items[].limits` | `limits` | ні | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `items[].limits.concurrency` | `object` | ні |  |
| `items[].limits.rate` | `object` | ні |  |
| `items[].limits.crawl` | `object` | ні |  |
| `items[].limits.timeouts` | `object` | ні |  |
| `items[].limits.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `items[].limits.queue` | `object` | ні |  |
| `items[].limits.sandbox` | `object` | ні |  |
| `items[].limits.llm` | `object` | ні |  |
| `items[].limits.transfer` | `object` | ні |  |
| `items[].limits.telegram` | `object` | ні |  |
| `items[].forward_unknown_to_llm` | `boolean` | ні | «Передавати в LLM невідомі сторінки» (ТЗ §8, критерій 11). За замовчуванням вимкнено: матеріал без відповідного обробника лише реєструється як невідомий.; типово `false` |
| `items[].expected_entity_types` | array of `string` | ні | Очікувані типи даних джерела (наприклад product, price, event). Розширення пропонує асистент, приймає користувач. |
| `items[].change_policy` | `object` | ні | Як активуються версії правил і екстракторів, створені LLM для цього джерела. |
| `items[].change_policy.llm_versions` | enum: `manual_approval`, `auto_after_checks`, `forbidden` | ні | типово `"manual_approval"` |
| `items[].connections` | `object` | ні | Логічне ім'я → connection_id (наприклад http-автентифікація сайту або обліковий запис Telegram). |
| `items[].labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `items[].created_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `list`:

```json
{
  "items": [
    {
      "source_id": "shop-example",
      "kind": "web",
      "title": "Shop Example",
      "locator": {
        "url": "https://shop.example.test/"
      },
      "forward_unknown_to_llm": false
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
