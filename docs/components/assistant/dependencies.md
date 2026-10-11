# Assistant: залежності

Сам процес може стартувати без сусідів. Кожна функція має явно визначені залежності; їхню доступність показує `GET /v1/info` у `capabilities.neighbours`.

## Сценарії

| Сценарій | Необхідні сусіди | Опційні |
|---|---|---|
| Health/info та порожні списки | Немає | PostgreSQL для постійного стану |
| Onboarding вебджерела | Web Collector, LLM, Registry, Handler Runtime | Search при неоднозначному текстовому запиті |
| Onboarding Telegram | Telegram Collector, LLM, Registry, Handler Runtime | Search; реальний Telegram потребує власних облікових даних колектора |
| Прийняти й активувати пропозицію | Registry, Handler Runtime, Orchestrator | Default storage package/connection для draft |
| Поліпшення екстрактора | Registry, Handler Runtime, LLM | Storage при `material_ref`, Orchestrator для bindings |
| Невідомий матеріал | LLM; Registry при відповідному пошуку пакета | Вимикається через `forward_unknown_to_llm=false` |

Неналаштований URL або недоступний сусід не замінюється вигаданими даними: потрібний виклик завершується `upstream_unavailable`. [Neighbours](../../../services/assistant/src/jane_assistant/clients.py) звертається до HTTP API; чужі таблиці не читаються.

## Версії та власний стан

Python `>=3.12`, Jane Kit і psycopg/binary/pool — [pyproject.toml](../../../services/assistant/pyproject.toml), точні версії — [uv.lock](../../../uv.lock). HTTP-сумісність визначають контракти `assistant.v1`, `collector.v1`, `handler.v1`, `registry.v1`, `orchestrator.v1`, `llm.v1`, `storage.v1` у [contracts/openapi](../../../contracts/openapi/).

Без `state_dsn` стан memory придатний для одного процесу. Для кількох екземплярів потрібна спільна власна PostgreSQL-схема з sessions, jobs та idempotency. Недоступна база не дозволяє вважати сервіс готовим; health перевіряє `state`.

## Пошуковий провайдер

`none` не виконує зовнішній пошук. `static` читає JSON-файл кандидатів, `http_json` використовує URL-шаблон `{query}` і налаштовані назви полів. Сумісність цього провайдера визначає [SearchProvider](../../../services/assistant/src/jane_assistant/search.py), а не окремий Jane HTTP-контракт.

## Заміна сусіда

Встановіть URL реалізації того самого контракту та відповідний bearer token ref. Наприклад, локальний LLM із aliases `cheap`/`strong` замінює реальний шлюз для інтеграційної перевірки; саме ім’я alias має існувати. Контрактні фейки сусідів у [tests/assistant_fakes](../../../services/assistant/tests/assistant_fakes/) не підміняють Assistant. Повний onboarding із реальними зовнішніми LLM/Telegram у цьому пакеті не відтворено.
