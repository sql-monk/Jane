# Карта репозиторію

Код автономного модуля, його тести й налаштування розташовані разом. Спільні контракти, бібліотеки й інфраструктура мають окремі каталоги.

## Зміст

- [Дерево папок](#дерево-папок)
- [Точки входу](#точки-входу)
- [Контракти та бібліотеки](#контракти-та-бібліотеки)
- [Тести та інструменти](#тести-та-інструменти)
- [Документація](#документація)

## Дерево папок

```text
Jane/
├── services/
│   ├── web-collector/        # API, crawl engine, правила й стратегії
│   ├── telegram-collector/   # API, канали, курсори й ревізії
│   ├── handler-runtime/      # API, CLI, пісочниця й профілі Python
│   ├── storage/              # API, merge, packages й adapters/
│   ├── llm/                  # API, gateway, providers/ й packages/
│   ├── registry/             # API, версії, blobs, export й forks
│   ├── orchestrator/         # API, DAG, engine, schedules й PostgreSQL
│   └── assistant/            # API, onboarding й improvement
├── libs/
│   ├── jane-kit/             # HTTP-шар, jobs, auth, limits й content
│   └── extractor-sdk/        # API автора екстрактора й приклади
├── web/admin/                # React, сторінки, API-клієнти й OIDC
├── contracts/
│   ├── openapi/              # HTTP API
│   ├── schemas/              # JSON Schema
│   ├── python/               # Protocol-и
│   ├── examples/             # Валідні й невалідні приклади
│   └── tools/                # Lint, сумісність та моки
├── examples/                 # Виконувані сценарії й пакети
├── infra/                    # Compose, proxy, provisioning й configs
├── deploy/profiles/          # Профілі, stack manager і limits harness
├── templates/service/        # Шаблон нового сервісу
├── tests/                    # Інтеграції, автономність і testsite
├── scripts/                  # Dev-команди й генерація документації
├── docs/                     # Активна документація
└── docs-archive/             # Ізольований архів попередніх документів
```

## Точки входу

| Модуль | Старт процесу | Побудова API та ядро |
|---|---|---|
| Web Collector | [__main__.py](../../services/web-collector/src/jane_web_collector/__main__.py) | [app](../../services/web-collector/src/jane_web_collector/app.py), [engine](../../services/web-collector/src/jane_web_collector/engine.py) |
| Telegram Collector | [__main__.py](../../services/telegram-collector/src/jane_telegram_collector/__main__.py) | [app](../../services/telegram-collector/src/jane_telegram_collector/app.py) |
| Handler Runtime | [__main__.py](../../services/handler-runtime/src/jane_handler_runtime/__main__.py), [cli](../../services/handler-runtime/src/jane_handler_runtime/cli.py) | [app](../../services/handler-runtime/src/jane_handler_runtime/app.py), [runtime](../../services/handler-runtime/src/jane_handler_runtime/runtime.py) |
| Storage | [__main__.py](../../services/storage/src/jane_storage/__main__.py) | [app](../../services/storage/src/jane_storage/app.py), [engine](../../services/storage/src/jane_storage/engine.py) |
| LLM | [__main__.py](../../services/llm/src/jane_llm/__main__.py) | [app](../../services/llm/src/jane_llm/app.py), [gateway](../../services/llm/src/jane_llm/gateway.py) |
| Registry | [__main__.py](../../services/registry/src/jane_registry/__main__.py) | [app](../../services/registry/src/jane_registry/app.py), [service](../../services/registry/src/jane_registry/service.py) |
| Orchestrator | [__main__.py](../../services/orchestrator/src/jane_orchestrator/__main__.py) | [app](../../services/orchestrator/src/jane_orchestrator/app.py), [engine](../../services/orchestrator/src/jane_orchestrator/engine.py) |
| Assistant | [__main__.py](../../services/assistant/src/jane_assistant/__main__.py) | [app](../../services/assistant/src/jane_assistant/app.py), [onboarding](../../services/assistant/src/jane_assistant/onboarding.py) |
| Admin | [main.tsx](../../web/admin/src/main.tsx) | [App](../../web/admin/src/App.tsx), [сторінки](../../web/admin/src/pages/) |

Назви встановлюваних команд задані в `pyproject.toml` модуля. Параметри старту та конфігурацію потрібно брати з його [документації](../components/README.md).

## Контракти та бібліотеки

| Каталог | Призначення |
|---|---|
| [contracts/openapi](../../contracts/openapi/) | Операції, поля HTTP-документів, responses і scopes |
| [contracts/schemas](../../contracts/schemas/) | Матеріали, сутності, пакети, завдання й спільні типи |
| [contracts/python](../../contracts/python/src/jane_contracts/) | Контракти адаптерів і стратегій discovery |
| [jane-kit/src](../../libs/jane-kit/src/jane_kit/) | Спільна реалізація сервісних можливостей |
| [extractor-sdk/src](../../libs/extractor-sdk/src/) | Типи й інструменти автора екстрактора |
| [storage/adapters](../../services/storage/adapters/) | Окремі пакети адаптерів із власними тестами |

## Тести та інструменти

Unit-тести сервісу знаходяться в `services/<name>/tests/`; тести бібліотеки — у `libs/<name>/tests/`. [Спільні tests](../../tests/) містять інтеграції та перевірки автономності. [Testsite](../../tests/fixtures/testsite/) дає контрольовані джерела для прикладів і перевірок.

Стратегії discovery мають додаткові тести у [strategies/discovery/tests](../../services/web-collector/strategies/discovery/tests/). Admin має тести біля компонентів та окремі [Playwright-сценарії](../../web/admin/e2e/).

[justfile](../../justfile) — головний список команд, [.python-version](../../.python-version) і [.node-version](../../.node-version) задають runtime-версії, [uv.lock](../../uv.lock) фіксує Python-залежності. Для документації призначено [scripts/docs](../../scripts/docs/).

## Документація

[docs/README.md](../README.md) веде до огляду, модулів, сценаріїв, довідників, розробки й експлуатації. Нові рішення зберігаються у [ADR](../adr/README.md), стан пакетів документації — у [delivery/documentation](../delivery/documentation/status.md).

Кореневі ТЗ, вимоги та плани залишаються джерелами вимог і організації робіт. Архів ізольований від активної навігації та використовується для відновлення історії.
