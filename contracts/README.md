# Контракти Jane

Машинозчитувані контракти всіх сервісів (ТЗ §13.1 п.6). Конвенції — скіл
[`.claude/skills/jane-contracts`](../.claude/skills/jane-contracts/SKILL.md); рішення — [`docs/adr/`](../docs/adr/README.md).
Після прийняття WP-00 змінюються лише через координатора й субагента `contract-guardian`.

## Структура

```text
contracts/
  openapi/            OpenAPI 3.1, версія /v1
    common.yaml         спільні параметри, відповіді-помилки, job, health, info
    collector.v1.yaml   спільний контракт колекторів (web, telegram)
    handler.v1.yaml     спільний протокол обробника (runtime, storage, llm)
    storage.v1.yaml     читання збережених даних
    registry.v1.yaml    репозиторій пакетів
    orchestrator.v1.yaml керування (для адмінки)
    llm.v1.yaml         LLM-шлюз
    assistant.v1.yaml   асистент джерел
  schemas/            JSON Schema 2020-12 (дані й конфігурації)
    common/             defs, problem, job, limits, content-ref, package-ref, connection, page
    material, entity, handler-invocation, handler-result, package-manifest,
    collector-rules, source, task-config
  examples/
    schemas/<schema>[@<Def>]/*.json   валідні приклади (перевіряються)
    invalid/schemas/…                 навмисно невалідні (мають відхилятися)
    openapi/*.json                    Example Objects, на які посилаються OpenAPI
  python/             пакет jane-contracts: Protocol-и DiscoveryStrategy і StorageAdapter
  docs/               помилки, власність даних, пакети, стратегії, адаптери
  tools/              check_contracts.py, mock.py, compat.py (uv scripts)
  redocly.yaml        конфігурація Redocly lint
```

## Команди

| Що | Команда |
|---|---|
| Лінтер контрактів (усе однією командою) | `uv run contracts/tools/check_contracts.py` (у CI: `--require-redocly`) |
| Мок API без Node | `uv run contracts/tools/mock.py <api> --port <порт>` |
| Мок Prism (з валідацією запитів) | `npx --yes @stoplight/prism-cli@5.16.0 mock contracts/openapi/<api>.v1.yaml -p <порт>` |
| Перелік операцій API | `uv run contracts/tools/mock.py <api> --list` |
| Зворотна сумісність | `uv run contracts/tools/compat.py --base main [--oasdiff]` |
| Самоперевірка compat | `uv run contracts/tools/compat.py --self-test` |
| Один файл для генераторів | `npx --yes @redocly/cli@2.54.3 bundle contracts/openapi/<api>.v1.yaml -o build/<api>.v1.yaml` |

Потрібні лише `uv` (Python 3.12+) і, для Redocly/Prism, Node.js. Працює на Windows і Linux.

## Хто що реалізує й споживає

| API / інтерфейс | Реалізує | Споживає | Мок (типовий порт) |
|---|---|---|---|
| `collector.v1` | WP-02/03 (web), WP-04 (telegram) | WP-09, WP-11, сторонні | `mock.py collector --port 4101` |
| `handler.v1` | WP-06 (runtime), WP-07/08 (storage), WP-10 (llm) | WP-09, WP-11, WP-12 (тести), сторонні | `mock.py handler --port 4106` |
| `storage.v1` | WP-07 | WP-09 (повторна обробка), WP-11, WP-12 | `mock.py storage --port 4107` |
| `registry.v1` | WP-05 | WP-06, WP-07, WP-09, WP-10, WP-11, WP-12, колектори (правила) | `mock.py registry --port 4105` |
| `orchestrator.v1` | WP-09 | WP-12, WP-11 (автоактивація), WP-13 | `mock.py orchestrator --port 4109` |
| `llm.v1` | WP-10 | WP-11, WP-12, WP-09 (синхронізація бюджетів) | `mock.py llm --port 4110` |
| `assistant.v1` | WP-11 | WP-09 (невідомі матеріали, проблеми), WP-12 | `mock.py assistant --port 4111` |
| `DiscoveryStrategy` | WP-02 (ядро, реєстр), WP-03 (стратегії) | WP-02 | — (Python Protocol) |
| `StorageAdapter` + набір сумісності | WP-07 (ядро, files, postgresql, набір), WP-08 | WP-07 | — (Python Protocol) |

## Документи

- [Модель помилок і коди](docs/errors.md)
- [Карта власності даних, дедуплікація й повтори](docs/data-ownership.md)
- [Що є пакетом для кожного типу обробника](docs/handler-packages.md)
- [Стратегія пошуку матеріалів (WP-02/03)](docs/discovery-strategy.md)
- [Адаптер збереження й сценарії сумісності (WP-07/08)](docs/storage-adapter.md)
