# LLM: будова

Gateway виконує модельний виклик через ProviderAdapter і Store. Store атомарно перевіряє rate/budget перед reservation; provider відповідає за HTTP генерації, gateway — за data/instruction boundaries та output validation.

[Компоненти](#компоненти) · [Алгоритм](#алгоритм) · [Власні дані](#власні-дані) · [Jobs](#jobs) · [Розробка](#розробка)

## Компоненти

```text
services/llm/
├── src/jane_llm/app.py          # API, seed, jobs і connections
├── src/jane_llm/gateway.py      # Моделі, budgets, rate, output validation
├── src/jane_llm/store.py        # Memory/Postgres store та DDL
├── src/jane_llm/prompt.py       # Інструкції й nonce data delimiters
├── src/jane_llm/providers/      # ProviderAdapter, fake, Anthropic
├── src/jane_llm/handler.py      # Виконавець LLM-пакетів
├── packages/                   # Вбудовані declarative пакети
└── tests/                      # Budgets, injection, service, policy
```

Gateway працює через протоколи Store і ProviderAdapter.

![Gateway працює через протоколи Store і ProviderAdapter.](../../diagrams/llm/types.light.png)

[Темна тема](../../diagrams/llm/types.dark.png) · [Редаговане джерело](../../diagrams/llm/types.drawio)

## Алгоритм

Alias визначає provider/model. Gateway перевіряє enabled, connection policy, token caps і pricing, утворює незалежні instructions/data канали та резервує оцінку вартості. Model text перевіряється output_schema; invalid output допускає не більше max_schema_retries додаткових генерацій. Usage враховує кожен provider виклик, включно зі schema retry; після відповіді reservation узгоджується з фактичними токенами.

Nonce data delimiters у [prompt.py](../../../services/llm/src/jane_llm/prompt.py) запобігають перетворенню даних джерела на інструкції для fake injection тесту. Це перевірений механізм побудови prompt, а не гарантія, що довільна зовнішня модель ніколи не виконає injection.

Модельний виклик має rate/budget gate і bounded schema retry.

![Модельний виклик має rate/budget gate і bounded schema retry.](../../diagrams/llm/completion-process.light.png)

[Темна тема](../../diagrams/llm/completion-process.dark.png) · [Редаговане джерело](../../diagrams/llm/completion-process.drawio)

## Власні дані

PostgreSQL store створює config із ключем kind/key, counters із scope/window key, reservations, usage та invocations. Jane Kit додає jobs/idempotency у тій самій власній схемі. Логічні посилання provider/model/scope в JSON не є SQL foreign keys; схеми інших сервісів не читаються.

Стан бюджету поєднує counters, reservations та usage у власній схемі.

![Стан бюджету поєднує counters, reservations та usage у власній схемі.](../../diagrams/llm/data.light.png)

[Темна тема](../../diagrams/llm/data.dark.png) · [Редаговане джерело](../../diagrams/llm/data.drawio)

Прострочені reservations після аварії списуються за початковою оцінкою. Usage зберігає purpose, source/task/run, tokens, cost, currency, test_mode і outcome; test_mode не слід трактувати як відсутність будь-якого provider виклику.

## Jobs

Async completion і handler/test-run jobs використовують стандартний Job lifecycle; sync completion не створює job лише через довгий model call автоматично. Для автономної генерації async треба задати у CompletionRequest.mode.

Async job завершує модельний виклик або записує явну помилку.

![Async job завершує модельний виклик або записує явну помилку.](../../diagrams/llm/jobs.light.png)

[Темна тема](../../diagrams/llm/jobs.dark.png) · [Редаговане джерело](../../diagrams/llm/jobs.drawio)

## Розробка

```powershell
uv run --all-packages pytest services/llm/tests/test_service.py services/llm/tests/test_budget.py services/llm/tests/test_injection.py
```

Тести використовують реальний gateway із детермінованим provider; PostgreSQL multi-instance перевірки потребують окремої тестової бази. Не підміняйте gateway при перевірці його budget/injection алгоритму. [Типи](reference/types/README.md), [API](reference/api/README.md).

## Застосовність діаграм

Context охоплює контекст, запуск, залежності; types — класи/протоколи; data — власну ER; completion-process — алгоритм і retries; completion-flow у integration — API-послідовність; jobs — стани. Окремий UI-процес N/A: шлюз не має UI, форма LLM належить Admin.
