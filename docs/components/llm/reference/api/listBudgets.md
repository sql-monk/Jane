# GET /v1/budgets

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L385). Не редагуйте вручну.

**Визначення бюджетів за рівнями й поточні витрати**

| Властивість | Значення |
|---|---|
| operationId | `listBudgets` |
| Метод і шлях | `GET /v1/budgets` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | budgets |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Бюджети. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `BudgetDefinition` | так |  |
| `items[].scope_type` | enum: `platform`, `source`, `task` | так |  |
| `items[].scope_id` | `string` | так |  |
| `items[].budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `items[].budget.amount` | `number` | так | мін. `0` |
| `items[].budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `items[].budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `items[].max_requests_per_minute` | `integer` | ні | мін. `1` |
| `items[].status` | `BudgetStatus` | ні | Стан одного бюджету в поточному вікні. У `CompletionResult.budget` — кожен бюджет, що діяв на виклик (зокрема бюджет запиту; один рівень може мати кілька записів із різними `limit.period`). |
| `items[].status.scope_type` | enum: `platform`, `source`, `task` | так |  |
| `items[].status.scope_id` | `string` | так |  |
| `items[].status.spent` | `Money` | так | Фактично списані витрати вікна (без резервів викликів, що ще виконуються). |
| `items[].status.limit` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `items[].status.resets_at` | `string` (date-time) | ні | Скидання календарного вікна (`day`/`week`/`month`); для `run` і `total` відсутнє. |
| `items[].status.exhausted` | `boolean` | так | `spent ≥ limit.amount`: у цьому вікні не пройде жоден виклик (навіть безкоштовної моделі), доки вікно не скинеться чи бюджет не збільшать. За `false` виклик теж відхиляється (429 `budget_exhausted`), якщо `spent + зарезервовано + його найгірша оцінка` не вміщується в ліміт. |

Приклад `list`:

```json
{
  "items": [
    {
      "scope_type": "platform",
      "scope_id": "platform",
      "budget": {
        "amount": 50,
        "currency": "USD",
        "period": "day"
      },
      "max_requests_per_minute": 60
    },
    {
      "scope_type": "task",
      "scope_id": "news-tg-events",
      "budget": {
        "amount": 5,
        "currency": "USD",
        "period": "day"
      }
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
