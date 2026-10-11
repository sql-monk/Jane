# PUT /v1/providers/{provider_id}

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L109). Не редагуйте вручну.

**Створити або замінити провайдера (облікові дані — через connection_id)**

| Властивість | Значення |
|---|---|
| operationId | `putProvider` |
| Метод і шлях | `PUT /v1/providers/{provider_id}` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | providers |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `provider_id` | path | `string` | так |  |
| `If-Match` | header | `string` | ні | ETag ресурсу для оптимістичного блокування. Розбіжність — 412 `precondition_failed`. |

## Тіло запиту

Тип вмісту `application/json`, схема `Provider`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `provider_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | `string` | так |  |
| `connection_id` | `string` | ні | Кероване підключення kind=llm_provider з посиланням на ключ API.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `enabled` | `boolean` | так |  |
| `models` | array of `object` | так |  |
| `models[].model_id` | `string` | так |  |
| `models[].max_context_tokens` | `integer` | ні | мін. `1` |
| `models[].supports_structured_output` | `boolean` | ні |  |
| `models[].pricing` | `object` | ні |  |
| `models[].pricing.input_per_mtok` | `number` | так | мін. `0` |
| `models[].pricing.output_per_mtok` | `number` | так | мін. `0` |
| `models[].pricing.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits` | `llm` | ні |  |
| `limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.budget.amount` | `number` | так | мін. `0` |
| `limits.budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits.budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |

Приклад `openaiCompatible`:

```json
{
  "provider_id": "main-llm",
  "kind": "openai_compatible",
  "connection_id": "llm-main",
  "enabled": true,
  "models": [
    {
      "model_id": "large-model-2026",
      "max_context_tokens": 200000,
      "supports_structured_output": true,
      "pricing": {
        "input_per_mtok": 3,
        "output_per_mtok": 15,
        "currency": "USD"
      }
    }
  ],
  "limits": {
    "max_requests_per_minute": 30
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Провайдера збережено. | `Provider` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `provider_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | `string` | так |  |
| `connection_id` | `string` | ні | Кероване підключення kind=llm_provider з посиланням на ключ API.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `enabled` | `boolean` | так |  |
| `models` | array of `object` | так |  |
| `models[].model_id` | `string` | так |  |
| `models[].max_context_tokens` | `integer` | ні | мін. `1` |
| `models[].supports_structured_output` | `boolean` | ні |  |
| `models[].pricing` | `object` | ні |  |
| `models[].pricing.input_per_mtok` | `number` | так | мін. `0` |
| `models[].pricing.output_per_mtok` | `number` | так | мін. `0` |
| `models[].pricing.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits` | `llm` | ні |  |
| `limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.budget.amount` | `number` | так | мін. `0` |
| `limits.budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits.budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |

Приклад `openaiCompatible`:

```json
{
  "provider_id": "main-llm",
  "kind": "openai_compatible",
  "connection_id": "llm-main",
  "enabled": true,
  "models": [
    {
      "model_id": "large-model-2026",
      "max_context_tokens": 200000,
      "supports_structured_output": true,
      "pricing": {
        "input_per_mtok": 3,
        "output_per_mtok": 15,
        "currency": "USD"
      }
    }
  ],
  "limits": {
    "max_requests_per_minute": 30
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `412`, `422`.
