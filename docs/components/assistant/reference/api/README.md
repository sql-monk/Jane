# Assistant: HTTP API

Асинхронні операції створюють jobs; onboarding зберігає також довгоживу сесію зі зразками, кандидатами й пропозиціями.

## Операції

| Сценарій | Довідник | Результат |
|---|---|---|
| Почати onboarding | [startOnboarding](generated/startOnboarding.md) | 202 Job, session link |
| Списки й деталі сесій | [listOnboardingSessions](generated/listOnboardingSessions.md), [getOnboardingSession](generated/getOnboardingSession.md) | Cursor list / session |
| Вибрати кандидата | [selectCandidate](generated/selectCandidate.md) | Продовження sampling |
| Прийняти пропозицію | [acceptProposal](generated/acceptProposal.md) | Apply/optional activation job |
| Поліпшити пакет | [startImprovement](generated/startImprovement.md), [listImprovementRuns](generated/listImprovementRuns.md) | Job і результат/пропозиція |
| Невідомий матеріал | [analyzeUnknownMaterial](generated/analyzeUnknownMaterial.md) | Job/suggestion за політикою |
| Job detail/cancel | [getJob](generated/getJob.md), [cancelJob](generated/cancelJob.md) | Server job state |

Scope робочих операцій — `assistant:use`; info/health — за спільною policy. [Повний generated індекс](generated/README.md), [assistant.v1](../../../../../contracts/openapi/assistant.v1.yaml), [scopes](../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py).

## Спільна поведінка

Bearer/scopes застосовує сервер; health публічний. Побічні POST мають Idempotency-Key: те саме тіло replay, інше тіло — `idempotency_key_reused`, незавершений claim — `idempotency_in_progress`. PUT використовує ETag/If-Match там, де це передбачено контрактом. Помилки HTTP — application/problem+json; client рішення приймає за code. Довгі операції повертають 202 Job/Location, polling завершується succeeded/failed/cancelled; cursor списки мають items/next_cursor.

Точні required поля, status codes, JSON pointers і приклади містять generated операції та [спільний контракт](../../../../../contracts/openapi/common.yaml). Невідомі поля результату читач терпить, документи налаштувань строгі.

## Приклади й стани

[Прямий клієнт](../../quickstart.md#прямий-виклик) показує 202/polling і failure boundary без сусідів. [Integration](../../integration.md) описує candidate selection/acceptance; [Session states](../../internals.md#стани) відрізняються від Job states. Не трактуйте succeeded sampling job як активоване джерело.
