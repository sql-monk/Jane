# Assistant: будова

Assistant складає пропозиції з доказів колектора, LLM аналізу, Registry пакетів і тестових результатів Handler Runtime. Користувацька сесія зберігається окремо від коротших jobs, які продовжують її етапи.

[Компоненти](#компоненти) · [Onboarding](#onboarding) · [Дані](#дані) · [Стани](#стани) · [Розробка](#розробка)

## Компоненти

```text
services/assistant/src/jane_assistant/
├── app.py             # API і job lifecycle
├── clients.py         # Neighbours та bearer refs
├── onboarding.py      # Session, sampling, proposals, acceptance
├── sampling.py        # Diversity і coverage confidence
├── improvement.py     # Аналіз проблем, форк, тести, bindings
├── unknown.py         # Пропозиція для невідомого матеріалу
├── material.py        # Digest і зменшення великих fixtures
├── guards.py          # Рання політика generated code
├── search.py          # none/static/http_json source search
└── state.py           # Власні sessions/jobs/idempotency
```

OnboardingService використовує SessionStore й Neighbours; state реалізації зберігають сесію.

![OnboardingService використовує SessionStore й Neighbours; state реалізації зберігають сесію.](../../diagrams/assistant/types.light.png)

[Темна тема](../../diagrams/assistant/types.dark.png) · [Редаговане джерело](../../diagrams/assistant/types.drawio)

## Onboarding

Запит із URL/username або текстом визначає кандидатів. Неоднозначність переводить Session у needs_disambiguation; явний вибір запускає sampling. Колектор віддає матеріали через API, diversity pool зменшує повторювані зразки, а confidence визначає достатність coverage. Нестача доказів дає insufficient_sample, не вигадану впевненість.

LLM аналізує типи, структурами знаходить схожі пакети, тестує існуючі екстрактори і за thresholds прив’язує, форкає або генерує новий. Generated code проходить early import policy, schema checks і тести runtime. Proposal містить evidence, ризики та draft; apply/activate відбувається лише за дозволеної політики.

Sampling набирає різні зразки до достатнього confidence або явного обмеження.

![Sampling набирає різні зразки до достатнього confidence або явного обмеження.](../../diagrams/assistant/sampling-process.light.png)

[Темна тема](../../diagrams/assistant/sampling-process.dark.png) · [Редаговане джерело](../../diagrams/assistant/sampling-process.drawio)

## Дані

Власна PostgreSQL таблиця sessions має session_id, doc JSON, version та updated_at. JobStore й IdempotencyStore Jane Kit у тій самій схемі зберігають jobs/claims/leases. CAS version не дозволяє одночасним candidate-selection/acceptance мовчки перезаписати сесію.

Session посилається на jobs і результати сусідів через ідентифікатори; чужі таблиці не читаються.

![Session посилається на jobs і результати сусідів через ідентифікатори; чужі таблиці не читаються.](../../diagrams/assistant/data.light.png)

[Темна тема](../../diagrams/assistant/data.dark.png) · [Редаговане джерело](../../diagrams/assistant/data.drawio)

Improvement-runs listing будується з jobs та їхніх результатів; окрема таблиця improvement_runs не створюється. Пакети належать Registry, матеріали — колекторам/Storage, завдання — Orchestrator. Пропозиції можуть містити fixture copies; резервна копія Assistant не є копією всіх первинних джерел.

## Стани

Session stages: sampling, needs_disambiguation, analyzing, proposals_ready, insufficient_sample, applying, completed та failed/cancelled. Job має свій queued/running/cancelling/succeeded/failed/cancelled. Завершена job із proposals_ready може очікувати людину; completed сесія означає завершене застосування.

Сесія може чекати вибору або acceptance між завершеними jobs.

![Сесія може чекати вибору або acceptance між завершеними jobs.](../../diagrams/assistant/sessions.light.png)

[Темна тема](../../diagrams/assistant/sessions.dark.png) · [Редаговане джерело](../../diagrams/assistant/sessions.drawio)

## Розробка

```powershell
uv run --all-packages pytest services/assistant/tests/test_app.py services/assistant/tests/test_units.py services/assistant/tests/test_lists.py
```

[Контрактні фейки сусідів](../../../services/assistant/tests/assistant_fakes/) дозволяють перевірити реальний Assistant; [test_process_e2e.py](../../../services/assistant/tests/test_process_e2e.py) запускає процесний сценарій із контрольованими сусідами. PostgreSQL state tests потребують own test DSN. Справжній зовнішній LLM/Telegram не підтверджується цими фейками.

## Застосовність діаграм

Context — запуск/залежності; types — класи/протоколи; data — власна ER; sampling-process — алгоритм; onboarding-flow у integration — API-послідовність; sessions — стани/користувацькі рішення. Окрема UI deployment N/A: вебформа належить Admin, Assistant є HTTP процесом.
