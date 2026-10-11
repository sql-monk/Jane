# API assistant.v1

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml). Не редагуйте вручну.

**Jane Source Assistant API**, версія `1.0.0`.

Асистент джерел (WP-11): підключення нового джерела за назвою чи посиланням, вдосконалення екстракторів на проблемних прикладах, обробка невідомих матеріалів (лише коли оркестратор передав їх за увімкненим прапорцем «Передавати в LLM невідомі сторінки»).

Асистент використовує API інших сервісів: collector (вибірка), registry (пошук, форк, публікація пакетів), handler-runtime (тести), llm (запити й бюджет), orchestrator (лише щоб застосувати обраний варіант, якщо користувач дозволив автоактивацію). Усі тривалі операції — 202 + Job. Вміст джерел — дані, не інструкції. Створені версії проходять тести й політику погодження; користувач обирає варіант, якщо не дозволив автоактивацію.

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| GET | `/v1/onboarding-sessions` | [listOnboardingSessions](listOnboardingSessions.md) | `assistant:use` | Сесії підключення, новіші першими (відновлення стану адмінки після перезавантаження) |
| POST | `/v1/onboarding-sessions` | [startOnboarding](startOnboarding.md) | `assistant:use` | Почати підключення джерела (назва сайту/каналу або точне посилання) |
| GET | `/v1/onboarding-sessions/{session_id}` | [getOnboardingSession](getOnboardingSession.md) | `assistant:use` | Стан підключення — кандидати, вибірка, аналіз, варіанти |
| POST | `/v1/onboarding-sessions/{session_id}/candidate-selection` | [selectCandidate](selectCandidate.md) | `assistant:use` | Уточнити неоднозначність — обрати джерело з кандидатів |
| POST | `/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance` | [acceptProposal](acceptProposal.md) | `assistant:use` | Прийняти варіант — опублікувати правила й пакети, прогнати тести, підготувати джерело й завдання |
| GET | `/v1/improvement-runs` | [listImprovementRuns](listImprovementRuns.md) | `assistant:use` | Запуски вдосконалення (job `kind = improvement`), новіші першими |
| POST | `/v1/improvement-runs` | [startImprovement](startImprovement.md) | `assistant:use` | Вдосконалити екстрактор на проблемних прикладах (нова версія або форк) |
| POST | `/v1/unknown-materials` | [analyzeUnknownMaterial](analyzeUnknownMaterial.md) | `assistant:use` | Проаналізувати невідомий матеріал (викликає оркестратор лише за увімкненим прапорцем) |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `assistant:use` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `assistant:use` | Запит на скасування job (ідемпотентний) |
