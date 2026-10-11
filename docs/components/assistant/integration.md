# Assistant: інтеграція

Assistant надає асинхронні операції onboarding, improvement та unknown-material analysis. Прямий клієнт може запускати їх без Admin; [локальний приклад](quickstart.md#прямий-виклик) показує polling job і явну межу відсутньої залежності.

## Мінімальний onboarding

Налаштуйте URL Web Collector або Telegram Collector, LLM, Registry та Handler Runtime у середовищі Assistant. Для LLM створіть aliases `cheap` і `strong`, або змініть `llm_model_cheap`/`llm_model_strong` на наявні aliases. Якщо сусіди вимагають auth, задайте їхні token refs; загальний `service_token_ref` застосовується лише коли окремий ref не задано.

```ini
JANE_ASSISTANT_LLM_URL=http://127.0.0.1:8110
JANE_ASSISTANT_REGISTRY_URL=http://127.0.0.1:8106
JANE_ASSISTANT_COLLECTOR_WEB_URL=http://127.0.0.1:8102
JANE_ASSISTANT_HANDLER_RUNTIME_URL=http://127.0.0.1:8104
JANE_ASSISTANT_LLM_MODEL_CHEAP=default
JANE_ASSISTANT_LLM_MODEL_STRONG=default
```

Порти в цьому прикладі — задані оператором адреси, а не гарантія конкретного compose-профілю. Для Docker використовуйте внутрішні service addresses. Запит із `auto_activation=false` готує пропозиції; activation потребує Orchestrator та успішних тестів кожного екстрактора. Fake-модель шлюзу не створює змістовний екстрактор за самою схемою; повний сценарій потребує відповідних відповідей або реальної моделі.

Сесія збирає зразки, перевіряє пакет і застосовує явно прийняту пропозицію.

![Сесія збирає зразки, перевіряє пакет і застосовує явно прийняту пропозицію.](../../diagrams/assistant/onboarding-flow.light.png)

[Темна тема](../../diagrams/assistant/onboarding-flow.dark.png) · [Редаговане джерело](../../diagrams/assistant/onboarding-flow.drawio)

## Вибір і прийняття

`startOnboarding` віддає Job і session link. Якщо сесія має `needs_disambiguation`, надішліть `candidate_id` у `selectCandidate`; вибір продовжує sampling. Коли `proposals_ready`, `acceptProposal` отримує proposal_id із наявного результату і `activate`/source_id. Створення або форк пакета передує його прив’язці; не вигадуйте id пропозиції чи пакета.

Onboarding session status відрізняється від Job status: `needs_disambiguation` або `proposals_ready` може означати завершену поточну job, але очікування рішення користувача в сесії.

## Поліпшення й невідомі матеріали

Improvement приймає точне посилання package_id/version/digest і непорожні problem_samples. Зразок містить material або material_ref; другий варіант потребує Storage URL і `storage_connection_id`/`object_id`. `policy.approval=manual` готує пропозицію; `auto_after_checks` застосовує її лише після перевірок реалізації. Bindings вказують task_id/stage_id і потребують Orchestrator.

Unknown analysis виконується лише за `forward_unknown_to_llm=true`; результат нижче `unknown.min_confidence` не пропонує впевнене рішення. Дані джерел залишаються даними, а generated code проходить allowlist і runtime sandbox. [Контрактні операції](reference/api/README.md).

## Заміна сумісного сусіда

Заміна URL/token ref не змінює Assistant API. Потрібно зберегти відповідний Jane контракт, моделі та ContentRef доступність. Заміна search provider має окремі налаштування; [конфігурація](configuration.md#пошук).
