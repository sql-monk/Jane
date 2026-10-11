# LLM gateway: залежності

Що потрібно LLM gateway для роботи, які версії сумісні та що відбувається, коли залежність недоступна. Факти звірено з `services/llm/pyproject.toml`, `services/llm/Dockerfile`, `infra/compose.yaml` і кодом ревізії `48389a3`.

## Зміст

- [Огляд](#огляд)
- [Середовище виконання](#середовище-виконання)
- [Сховище стану](#сховище-стану)
- [Провайдери LLM](#провайдери-llm)
- [Registry](#registry)
- [Вміст за посиланням](#вміст-за-посиланням)
- [Хто залежить від LLM gateway](#хто-залежить-від-llm-gateway)

## Огляд

| Залежність | Обов'язковість | Навіщо | Без неї |
|---|---|---|---|
| Python 3.12 і пакети з `pyproject.toml` | обов'язкова | виконання сервісу | сервіс не запускається |
| PostgreSQL | обов'язкова для `JANE_LLM_STORE=postgres` (типово) | спільний стан кількох екземплярів, збереження між перезапусками | режим `memory` для одного процесу |
| Провайдер `anthropic` | опційна | реальні відповіді моделі | працює лише `fake` |
| Провайдер `fake` | вбудований | детерміновані відповіді для тестів і локальної роботи | — |
| Registry | опційна | LLM-пакети за `package_id` і `version` | пакет з архіву в запиті або з локального каталогу |
| Каталоги `JANE_LLM_BLOB_ROOTS`, хости `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` | опційні | читання вмісту матеріалів і архівів за посиланням | приймається лише вміст `inline` |

Orchestrator для роботи сервісу не потрібен: виклики приходять від будь-якого клієнта API.

## Середовище виконання

| Компонент | Версія | Джерело |
|---|---|---|
| Python | `>=3.12` | `requires-python` у `services/llm/pyproject.toml` |
| jane-kit | з workspace | `[tool.uv.sources]` |
| httpx | `>=0.27` | виклики Anthropic і Registry |
| PyYAML | `>=6.0` | seed-файл |
| jsonschema | `>=4.23` | перевірка `output_schema` і схем пакетів |
| psycopg[binary], psycopg-pool | `>=3.2` | PostgreSQL |
| Образ Docker | `python:3.12-slim`, uv `0.12.13` | `services/llm/Dockerfile` |

Офіційний SDK `anthropic` не використовується: адаптер звертається до Messages API напряму через httpx (`jane_llm/providers/anthropic.py`).

## Сховище стану

PostgreSQL зберігає конфігурацію, лічильники бюджетів, резерви, журнал витрат, результати викликів обробника, ключі ідемпотентності та job у власній схемі (`JANE_LLM_DB_SCHEMA`, типово `llm`). Сервіс створює схему й таблиці сам під час старту.

- **Сумісна версія:** у dev-стеку — образ `postgres:18` (`infra/compose.yaml`), на ньому пройшли інтеграційні тести `just integration --project jane-doc-llm services/llm` (51 тест, 2026-10-11). Інші версії не перевірялися.
- **Недоступна під час старту:** міграція не виконується, сервіс не стартує. Без `JANE_LLM_DATABASE_URL` у режимі `postgres` старт завершується повідомленням `JANE_LLM_DATABASE_URL is required for store=postgres (or set JANE_LLM_STORE=memory)`.
- **Недоступна під час роботи:** перевірка `store` у `GET /v1/health` стає `down`, відповідь — 503. Поведінку окремих запитів за втрати з'єднання в цій документації не перевірено.

Режим `memory` (`JANE_LLM_STORE=memory`) має ту саму семантику бюджетів і ідемпотентності, але лише в межах одного процесу; у журналі під час старту з'являється попередження `store=memory: budgets and usage are per process`.

## Провайдери LLM

### Anthropic

Адаптер `anthropic` викликає `POST {api_base}/v1/messages` з заголовками `x-api-key` і `anthropic-version` (типово `2023-06-01`). Ключ береться з керованого підключення через `secret_refs.api_key`; адреса `api_base` має бути в `JANE_LLM_PROVIDER_API_BASE_ALLOWLIST` (типово лише `https://api.anthropic.com`). Як підключити — [integration.md](integration.md#підключення-anthropic).

Поведінка за недоступності:

- помилка з'єднання або відповідь `408`, `409`, `429`, `500`, `502`, `503`, `504`, `529` — повтор за політикою `provider.retries` (типово 2 спроби, затримка від 500 мс, з урахуванням `Retry-After`);
- після останньої спроби запит завершується 502 `upstream_unavailable` (`retryable: true`), резерв бюджету знімається, витрати не записуються;
- інший код помилки (наприклад, `400` або `401`) — одразу 502 `upstream_unavailable` з `retryable: false`; у журнал пишеться тип і повідомлення помилки провайдера без вмісту запиту;
- провайдер без підключення або з ключем, що не розв'язується, — 502 з повідомленням `anthropic provider needs a connection with secret_refs.api_key`.

Реальний виклик Anthropic у цій документації не перевірено: ключ провайдера під час підготовки не використовувався.

### fake

Вбудований детермінований провайдер (`jane_llm/providers/fake.py`): рахує токени як кількість символів, поділену на 4, повертає сценарну відповідь з параметрів підключення або мінімальне значення, що відповідає `output_schema`. Його ціна — нуль. Реєструється під час старту разом із псевдонімом `default`, якщо `JANE_LLM_FAKE_PROVIDER_ENABLED=true`. Сценарії й затримки — [integration.md](integration.md#сценарні-відповіді-fake).

## Registry

Потрібен лише для LLM-пакетів, які передано посиланням (`handler.package_id`, `handler.version`) і яких немає в локальному каталозі. Шлюз завантажує архів через `GET /v1/packages/{package_id}/versions/{version}/archive` (`registry.v1`) зі своїм токеном `JANE_LLM_REGISTRY_TOKEN`.

| Ситуація | Результат |
|---|---|
| `JANE_LLM_REGISTRY_URL` не задано | пакет шукається лише в архіві запиту й локальному каталозі; інакше 404 `not_found` |
| Registry повернув 404 | 404 `not_found`: пакета немає ні в архіві, ні в каталозі, ні в Registry |
| Registry недоступний або повернув 5xx | 502 `upstream_unavailable` після повторів `registry.max_attempts` (типово 3) |
| Дайджест архіву не збігся з `handler.digest` | 422 `digest_mismatch` |

## Вміст за посиланням

Матеріали, сутності й архіви пакетів можуть надходити як `ContentRef` за посиланням. Шлюз читає:

- `file://` — лише з каталогів `JANE_LLM_BLOB_ROOTS` (типово порожньо: заборонено);
- `download_url` — лише з хостів `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` (типово порожньо: заборонено), без переходу за перенаправленнями, з тайм-аутом `gateway.content_fetch_timeout_ms`.

Вміст, який не дозволено читати, відхиляється; запит з таким вмістом не викликає модель. У dev-стеку `JANE_LLM_BLOB_ROOTS` вказує на каталоги Storage, змонтовані тільки для читання, — для повторної обробки збережених RAW.

## Хто залежить від LLM gateway

| Модуль | Що використовує | Документація |
|---|---|---|
| Orchestrator | `handler.v1` для етапів `kind: llm`; `PUT`/`DELETE /v1/budgets/...` — переносить `limits.llm` джерел і завдань у бюджети шлюзу | [Orchestrator](../orchestrator/README.md) |
| Assistant | `POST /v1/completions` з `scope.run_id` і бюджетом запуску | [Assistant](../assistant/dependencies.md#llm-gateway) |
| Admin UI | провайдери, псевдоніми, бюджети, облік, підключення | [Admin UI](../admin/README.md) |
