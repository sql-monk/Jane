# Assistant: типи й публічні члени

Generated довідник перелічує всі публічні декларації поточного source: класи/інтерфейси/протоколи, конструктори, методи, функції, поля, властивості й constants. Сторінка кожного модуля містить сигнатури, parameters/results, source links та доступність property. Ручні пояснення нижче допомагають вибрати точку розширення; generated файли змінює тільки генератор.

## Навігація

| Завдання | Типи та модулі |
|---|---|
| Повний перелік | [Generated index](generated/README.md) |
| Побудувати app та dependency injection | [build_app, Dependencies, request models](generated/jane_assistant.app.md) |
| Onboarding state/proposals | [Session, ExtractorPlan, SessionStore, OnboardingService](generated/jane_assistant.onboarding.md) |
| Memory/Postgres state | [ServiceState, InMemoryState, PostgresState](generated/jane_assistant.state.md) |
| HTTP сусіди | [Neighbours](generated/jane_assistant.clients.md) |
| Source search | [SearchProvider](generated/jane_assistant.search.md) |
| Diversity/coverage | [sampling](generated/jane_assistant.sampling.md) |
| Material digest/fixtures | [material](generated/jane_assistant.material.md) |
| Поліпшення/unknown | [improvement](generated/jane_assistant.improvement.md), [unknown](generated/jane_assistant.unknown.md) |
| Code policy й schema validation | [guards](generated/jane_assistant.guards.md) |

## Стан і помилки

Session є mutable domain object, збереження має version/CAS у SessionStore. ServiceState об’єднує own session/job/idempotency stores; Neighbours конфігурує HTTP клієнти та token refs. Помилки JaneError повертаються Problem або job.error; generated сигнатури не означають, що довільний missing neighbor автоматично замінюється.

## Приклад використання

[Прямий HTTP клієнт](../../quickstart.md#прямий-виклик) запускає onboarding job. Для інтеграційного тесту передайте Dependencies із transport сусідів за контрактами; сам Assistant, sampling та guards залиште реальними. [Стани і власність даних](../../internals.md#стани).
