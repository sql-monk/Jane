# LLM: залежності

Шлюз має два способи зберігання стану й два встановлені kind провайдерів. Вибір моделі не вимагає Orchestrator.

## Обов’язкові залежності

| Залежність | Умова | Поведінка при недоступності |
|---|---|---|
| Jane Kit | Завжди | HTTP, auth, jobs, ліміти; версія workspace із uv.lock |
| PostgreSQL | Типовий `store=postgres` | Без `database_url` старт відхиляється; помилка стану позначається в health |
| FakeProvider | Локальний `store=memory` | Детермінована відповідь за схемою, без мережевого провайдера |
| Anthropic | `provider.kind=anthropic` | Потрібний дозволений API origin та connection із secret_refs; помилка provider виклику обробляється за retry policy |

Python `>=3.12` визначає [pyproject.toml](../../../services/llm/pyproject.toml); робоча версія — [.python-version](../../../.python-version). Версії httpx, psycopg та jsonschema беріть із [uv.lock](../../../uv.lock). Зовнішній Anthropic не перевірено на реальному сервісі; локальний fake не є доказом його доступності або якості.

## Опційні залежності

| Залежність | Потрібний сценарій | Межа |
|---|---|---|
| Registry `registry.v1` | Виконання віддаленого LLM-пакета | Локальний `packages_dir` або `package_archive` усуває цю залежність |
| Дозволені blob roots/hosts | ContentRef в матеріалах та архіві | Порожні allowlist відхиляють file/download refs |
| Assistant | Генерація пропозицій для джерел | Клієнт шлюзу, не обов’язкова залежність шлюзу |
| Orchestrator | Виконання етапу `llm` | Прямий completion не залежить від нього |

## Власний стан і масштабування

Постійний режим зберігає providers, aliases, connections, budgets, counters, reservations, usage, invocation results, jobs та ключі ідемпотентності в своїй схемі. Всі екземпляри мають використовувати ту саму схему для одного логічного шлюзу. `memory` не дає спільних бюджетів між процесами та втрачає стан після рестарту.

## Заміна залежності

[Псевдонім моделі](integration.md#заміна-провайдера) дозволяє перемикати клієнта між налаштованими провайдерами. Новий kind потребує реалізації протоколу [ProviderAdapter](../../../services/llm/src/jane_llm/providers/base.py) й реєстрації у gateway; самої зміни рядка `kind` недостатньо. Сумісний зовнішній gateway має реалізувати `llm.v1`, включно з budget/usage/idempotency, а не лише endpoint генерації тексту.
