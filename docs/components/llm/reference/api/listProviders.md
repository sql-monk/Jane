# GET /v1/providers

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L48). Не редагуйте вручну.

**Провайдери LLM і їхні моделі**

| Властивість | Значення |
|---|---|
| operationId | `listProviders` |
| Метод і шлях | `GET /v1/providers` |
| Scope | `llm:admin`, `llm:invoke` |
| Ідемпотентність | — |
| Теги | providers |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Провайдери. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `Provider` | так |  |
| `items[].provider_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].kind` | `string` | так |  |
| `items[].connection_id` | `string` | ні | Кероване підключення kind=llm_provider з посиланням на ключ API.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].enabled` | `boolean` | так |  |
| `items[].models` | array of `object` | так |  |
| `items[].models[].model_id` | `string` | так |  |
| `items[].models[].max_context_tokens` | `integer` | ні | мін. `1` |
| `items[].models[].supports_structured_output` | `boolean` | ні |  |
| `items[].models[].pricing` | `object` | ні |  |
| `items[].limits` | `llm` | ні |  |
| `items[].limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `items[].limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `items[].limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `items[].limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `items[].limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `items[].limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `items[].limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |

Приклад `list`:

```json
{
  "items": [
    {
      "provider_id": "fake",
      "kind": "fake",
      "enabled": true,
      "models": [
        {
          "model_id": "fake-deterministic-1",
          "max_context_tokens": 128000,
          "supports_structured_output": true,
          "pricing": {
            "input_per_mtok": 0,
            "output_per_mtok": 0,
            "currency": "USD"
          }
        }
      ]
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
