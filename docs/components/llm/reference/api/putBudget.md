# PUT /v1/budgets/{scope_type}/{scope_id}

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L434). Не редагуйте вручну.

**Задати бюджет рівня (оркестратор синхронізує сюди ліміти llm.budget джерел і завдань)**

| Властивість | Значення |
|---|---|
| operationId | `putBudget` |
| Метод і шлях | `PUT /v1/budgets/{scope_type}/{scope_id}` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | budgets |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `scope_type` | path | enum: `platform`, `source`, `task` | так |  |
| `scope_id` | path | `string` | так |  |

## Тіло запиту

Тип вмісту `application/json`, схема `BudgetDefinition`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `scope_type` | enum: `platform`, `source`, `task` | так |  |
| `scope_id` | `string` | так |  |
| `budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `budget.amount` | `number` | так | мін. `0` |
| `budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `max_requests_per_minute` | `integer` | ні | мін. `1` |
| `status` | `BudgetStatus` | ні | Стан одного бюджету в поточному вікні. У `CompletionResult.budget` — кожен бюджет, що діяв на виклик (зокрема бюджет запиту; один рівень може мати кілька записів із різними `limit.period`). |
| `status.scope_type` | enum: `platform`, `source`, `task` | так |  |
| `status.scope_id` | `string` | так |  |
| `status.spent` | `Money` | так | Фактично списані витрати вікна (без резервів викликів, що ще виконуються). |
| `status.spent.amount` | `number` | так | мін. `0` |
| `status.spent.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `status.limit` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `status.limit.amount` | `number` | так | мін. `0` |
| `status.limit.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `status.limit.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `status.resets_at` | `string` (date-time) | ні | Скидання календарного вікна (`day`/`week`/`month`); для `run` і `total` відсутнє. |
| `status.exhausted` | `boolean` | так | `spent ≥ limit.amount`: у цьому вікні не пройде жоден виклик (навіть безкоштовної моделі), доки вікно не скинеться чи бюджет не збільшать. За `false` виклик теж відхиляється (429 `budget_exhausted`), якщо `spent + зарезервовано + його найгірша оцінка` не вміщується в ліміт. |

Приклад `task`:

```json
{
  "scope_type": "task",
  "scope_id": "news-tg-events",
  "budget": {
    "amount": 5,
    "currency": "USD",
    "period": "day"
  }
}
```

Приклад `llmOff`:

```json
{
  "scope_type": "task",
  "scope_id": "shop-price-check",
  "budget": {
    "amount": 0,
    "currency": "USD",
    "period": "run"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Збережено. | `BudgetDefinition` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `scope_type` | enum: `platform`, `source`, `task` | так |  |
| `scope_id` | `string` | так |  |
| `budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `budget.amount` | `number` | так | мін. `0` |
| `budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `max_requests_per_minute` | `integer` | ні | мін. `1` |
| `status` | `BudgetStatus` | ні | Стан одного бюджету в поточному вікні. У `CompletionResult.budget` — кожен бюджет, що діяв на виклик (зокрема бюджет запиту; один рівень може мати кілька записів із різними `limit.period`). |
| `status.scope_type` | enum: `platform`, `source`, `task` | так |  |
| `status.scope_id` | `string` | так |  |
| `status.spent` | `Money` | так | Фактично списані витрати вікна (без резервів викликів, що ще виконуються). |
| `status.spent.amount` | `number` | так | мін. `0` |
| `status.spent.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `status.limit` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `status.limit.amount` | `number` | так | мін. `0` |
| `status.limit.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `status.limit.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `status.resets_at` | `string` (date-time) | ні | Скидання календарного вікна (`day`/`week`/`month`); для `run` і `total` відсутнє. |
| `status.exhausted` | `boolean` | так | `spent ≥ limit.amount`: у цьому вікні не пройде жоден виклик (навіть безкоштовної моделі), доки вікно не скинеться чи бюджет не збільшать. За `false` виклик теж відхиляється (429 `budget_exhausted`), якщо `spent + зарезервовано + його найгірша оцінка` не вміщується в ліміт. |

Приклад `task`:

```json
{
  "scope_type": "task",
  "scope_id": "news-tg-events",
  "budget": {
    "amount": 5,
    "currency": "USD",
    "period": "day"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `422`.
