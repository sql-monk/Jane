# API llm.v1

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml). Не редагуйте вручну.

**Jane LLM Gateway API**, версія `1.0.0`.

LLM-шлюз (WP-10): провайдери, моделі й псевдоніми, бюджети й облік витрат, структуровані запити з валідацією. Сервіс llm **також реалізує спільний протокол обробника** (`handler.v1.yaml`: `/v1/invocations`, `/v1/test-runs`, `/v1/connections`) для пакетів `kind: llm`; цей файл описує лише специфічні для шлюзу операції.

Безпека вмісту (ТЗ §11): довірені інструкції (`instructions`) і недовірені дані (`data`) передаються окремо; шлюз обгортає дані розмежувачами й ніколи не виконує інструкцій із них. Бюджети застосовуються до рівнів platform → source → task; запит із вичерпаним бюджетом — 429 `budget_exhausted` без звернення до провайдера. Повтор із тим самим `Idempotency-Key` не витрачає бюджет удруге. У тестах — детермінований провайдер `fake`.

Бюджет (`Budget` у `limits.schema.json`): виклик дозволено, лише якщо для кожного застосовного бюджету `spent < amount` і `spent + зарезервовано + найгірша оцінка вартості ≤ amount` (оцінка — вхідні токени + `max_output_tokens` за ціною моделі; резерв перевіряється атомарно в спільному сховищі всіх екземплярів). `amount: 0` — «LLM вимкнено» для рівня (і для моделі з нульовою ціною). Вікна: `day`/`week`/`month` (UTC), `total`, `run` — за `scope.run_id`, без нього — сам запит.

Вихід пакета `kind: llm` у `HandlerResult` і `EntityRecord` — правило відображення в `contracts/docs/handler-packages.md` («Пакет `llm`: вихід моделі → результат обробника»).

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| GET | `/v1/providers` | [listProviders](listProviders.md) | `llm:admin`, `llm:invoke` | Провайдери LLM і їхні моделі |
| GET | `/v1/providers/{provider_id}` | [getProvider](getProvider.md) | `llm:admin`, `llm:invoke` | Провайдер |
| PUT | `/v1/providers/{provider_id}` | [putProvider](putProvider.md) | `llm:admin` | Створити або замінити провайдера (облікові дані — через connection_id) |
| DELETE | `/v1/providers/{provider_id}` | [deleteProvider](deleteProvider.md) | `llm:admin` | Видалити провайдера |
| GET | `/v1/model-aliases` | [listModelAliases](listModelAliases.md) | `llm:admin`, `llm:invoke` | Псевдоніми моделей, на які посилаються пакети (default, cheap, strong) |
| PUT | `/v1/model-aliases/{alias}` | [putModelAlias](putModelAlias.md) | `llm:admin` | Призначити псевдонім моделі |
| POST | `/v1/completions` | [createCompletion](createCompletion.md) | `llm:invoke` | Структурований запит до LLM з валідацією виходу за схемою |
| GET | `/v1/budgets` | [listBudgets](listBudgets.md) | `llm:admin` | Визначення бюджетів за рівнями й поточні витрати |
| PUT | `/v1/budgets/{scope_type}/{scope_id}` | [putBudget](putBudget.md) | `llm:admin` | Задати бюджет рівня (оркестратор синхронізує сюди ліміти llm.budget джерел і завдань) |
| DELETE | `/v1/budgets/{scope_type}/{scope_id}` | [deleteBudget](deleteBudget.md) | `llm:admin` | Прибрати бюджет рівня (діє успадкований) |
| GET | `/v1/usage` | [getUsage](getUsage.md) | `llm:admin` | Облік витрат LLM |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `llm:admin`, `llm:invoke` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `llm:admin`, `llm:invoke` | Запит на скасування job (ідемпотентний) |

## Інші контракти модуля

- `handler.v1` — [../../../../reference/api/handler/README.md](../../../../reference/api/handler/README.md)
