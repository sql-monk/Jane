# Контракти Jane

Каталог [contracts/](../../../contracts/) — машинозчитувані контракти всіх модулів Jane: OpenAPI 3.1 сервісів, JSON Schema 2020-12 даних і конфігурацій, перевірені приклади, Python Protocol-и пакета `jane-contracts` та інструменти перевірки, моків і сумісності. Контракт — єдине джерело правди про запити, відповіді й формат даних; сервіси, Admin UI й сторонні застосунки будуються від нього.

## Зміст

- [Межі відповідальності](#межі-відповідальності)
- [Структура каталогу](#структура-каталогу)
- [API та їхні реалізації](#api-та-їхні-реалізації)
- [Сценарії](#сценарії)
- [Автономність](#автономність)
- [Комплект документації](#комплект-документації)

## Межі відповідальності

| Тип | Контракти (специфікації та інструменти, без сервісу) |
|---|---|
| Містить | OpenAPI семи API, спільні компоненти `common.yaml`, схеми даних, приклади, Protocol-и `DiscoveryStrategy` і `StorageAdapter`, лінтер, мок, перевірку сумісності, документи `contracts/docs/` |
| Не містить | Реалізацій сервісів, згенерованих клієнтів і довідників (довідники генерує координатор — [docs/reference](../../reference/README.md)) |
| Змінює | Координатор після перевірки субагентом `contract-guardian`; процес — [експлуатація](operations.md#зміна-контракту) |

## Структура каталогу

```text
contracts/
├── openapi/                    # OpenAPI 3.1, усе під /v1
│   ├── common.yaml             # спільні параметри, заголовки, відповіді-помилки, Job, Health, Info, Connection
│   ├── collector.v1.yaml       # колектори (Web, Telegram)
│   ├── handler.v1.yaml         # обробники (Handler Runtime, Storage, LLM gateway)
│   ├── storage.v1.yaml         # читання збережених RAW і сутностей
│   ├── registry.v1.yaml        # репозиторій пакетів
│   ├── orchestrator.v1.yaml    # джерела, завдання, запуски (для Admin UI)
│   ├── llm.v1.yaml             # LLM gateway: провайдери, аліаси, бюджети
│   └── assistant.v1.yaml       # Assistant: підготовка джерел і вдосконалення екстракторів
├── schemas/                    # JSON Schema 2020-12
│   ├── common/                 # defs, problem, job, limits, content-ref, package-ref, connection, page
│   └── *.schema.json           # material, entity, handler-invocation, handler-result, package-manifest,
│                               # collector-rules, source, task-config
├── examples/
│   ├── schemas/<схема>[@<Def>]/*.json   # валідні приклади схем
│   ├── invalid/schemas/...              # навмисно невалідні приклади (мають відхилятися)
│   └── openapi/*.json                   # Example Objects, на які посилаються OpenAPI
├── python/                     # пакет jane-contracts 1.0.0: Protocol-и (CONTRACT_VERSION 1.1.0)
├── docs/                       # помилки, власність даних, пакети, стратегії, адаптери
├── tools/                      # check_contracts.py, mock.py, compat.py, _common.py (uv-скрипти)
└── redocly.yaml                # правила Redocly lint
```

Обсяг на ревізії `48389a3` (вивід лінтера): 8 OpenAPI-документів, 118 операцій, 16 схем, 46 прикладів схем, 13 невалідних прикладів, 544 приклади в OpenAPI.

## API та їхні реалізації

| Контракт | Реалізує | Споживає |
|---|---|---|
| `collector.v1` | Web Collector, Telegram Collector | Orchestrator, Assistant, Admin UI, сторонні застосунки |
| `handler.v1` | Handler Runtime, Storage, LLM gateway | Orchestrator, Assistant, Admin UI, сторонні застосунки |
| `storage.v1` | Storage | Orchestrator (повторна обробка), Assistant, Admin UI |
| `registry.v1` | Registry | Handler Runtime, Storage, Orchestrator, LLM gateway, Assistant, Admin UI, колектори (правила) |
| `orchestrator.v1` | Orchestrator | Admin UI, Assistant |
| `llm.v1` | LLM gateway | Assistant, Admin UI, Orchestrator |
| `assistant.v1` | Assistant | Orchestrator, Admin UI |
| `DiscoveryStrategy` (Python) | Стратегії Web Collector | Web Collector |
| `StorageAdapter` (Python) | Адаптери Storage | Storage |

Довідники операцій — [docs/reference](../../reference/README.md).

## Сценарії

- **Сторонній застосунок викликає модуль.** Бере OpenAPI модуля, генерує клієнт або пише запити вручну за конвенціями — [інтеграція](integration.md).
- **Розробка без сусіда.** Мок API з прикладів контракту — `just contracts-mock <api>` ([швидкий старт](quickstart.md)).
- **Новий сервіс або сумісна заміна модуля.** Реалізує контракт і перевіряє себе контрактними тестами — [інтеграція](integration.md#контрактні-тести).
- **Зміна контракту.** Лінтер, перевірка зворотної сумісності, оновлення прикладів і споживачів — [експлуатація](operations.md#зміна-контракту).

## Автономність

Контракти не залежать від жодного сервісу: інструменти — самодостатні uv-скрипти з власними залежностями, яким потрібні лише `uv` і Python 3.12. Контракти автономних API (`collector`, `handler`, `storage`, `registry`, `llm`) не посилаються на контракти Orchestrator і Assistant — це перевіряє лінтер. Redocly, Prism і oasdiff — опційні ([залежності](dependencies.md)).

## Комплект документації

| Сторінка | Зміст |
|---|---|
| [quickstart.md](quickstart.md) | Лінтер, мок, запит до моку, генерація клієнта, перевірка сумісності |
| [dependencies.md](dependencies.md) | uv, Python, Node.js, Docker, git і що без них не працює |
| [configuration.md](configuration.md) | Параметри інструментів, змінні середовища, модель лімітів `Limits` |
| [integration.md](integration.md) | Конвенції API, клієнти, моки, контрактні тести, Protocol-и |
| [internals.md](internals.md) | Що перевіряє лінтер, алгоритм сумісності, поведінка моку, приклади |
| [operations.md](operations.md) | Зміна контракту, CI, оновлення oasdiff, типові проблеми |

Документи всередині каталогу: [модель помилок](../../../contracts/docs/errors.md), [власність даних](../../../contracts/docs/data-ownership.md), [пакети обробників](../../../contracts/docs/handler-packages.md), [стратегія пошуку](../../../contracts/docs/discovery-strategy.md), [адаптер збереження](../../../contracts/docs/storage-adapter.md). Бібліотека, що реалізує конвенції в Python-сервісах, — [jane-kit](../jane-kit/README.md).
