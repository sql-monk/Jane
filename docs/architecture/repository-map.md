# Карта репозиторію

Дерево репозиторію Jane з призначенням каталогів і ключових файлів, точки входу та розташування тестів. Звірено з ревізією `48389a3` (`git ls-files`).

## Зміст

- [Дерево каталогів](#дерево-каталогів)
- [Будова сервісу](#будова-сервісу)
- [Точки входу](#точки-входу)
- [Тести](#тести)
- [Файли поза Git](#файли-поза-git)

## Дерево каталогів

```text
Jane/
├── services/                       # сервіси; кожен — Python-пакет jane-<сервіс>
│   ├── web-collector/              # Web Collector
│   │   └── strategies/discovery/   # стратегії пошуку: sitemap, feed, listing, url_template, api_feed
│   ├── telegram-collector/         # Telegram Collector; бекенди recorded і telethon
│   ├── storage/                    # Storage
│   │   └── adapters/               # адаптери-пакети: files, postgres, sqlserver, mongodb, minio, s3
│   ├── handler-runtime/            # Handler Runtime
│   │   └── sandbox/python-extractor-1/  # образ пісочниці профілю python-extractor@1
│   ├── llm/                        # LLM gateway
│   │   ├── packages/               # вбудований LLM-пакет jane.llm-event-extractor
│   │   └── config/                 # seed.example.yaml — приклад провайдерів і моделей
│   ├── registry/                   # Registry; scripts/scan_bench.py — вимірювання
│   ├── orchestrator/               # Orchestrator
│   └── assistant/                  # Assistant
├── libs/
│   ├── jane-kit/                   # спільна бібліотека сервісів; генератор клієнтів jane-codegen
│   └── extractor-sdk/              # jane-extractor-sdk: типи, запуск і тести екстракторів; examples/
├── contracts/                      # контракти API
│   ├── openapi/                    # collector, handler, storage, registry, orchestrator, llm, assistant (.v1.yaml), common.yaml
│   ├── schemas/                    # JSON Schema: material, entity, source, task-config, package-manifest, …; common/
│   ├── examples/                   # приклади до схем і OpenAPI; invalid/ — негативні
│   ├── python/                     # пакет jane-contracts: Python Protocol-и
│   ├── tools/                      # check_contracts.py, compat.py, mock.py
│   └── docs/                       # нормативні пояснення: помилки, власність даних, пакети, адаптери
├── web/admin/                      # Admin UI: React, TypeScript, Vite, pnpm
│   ├── src/                        # pages/, components/, api/ (generated/ — типи з OpenAPI), auth/, lib/
│   ├── e2e/                        # сценарії Playwright
│   └── scripts/                    # генерація типів API, моки, налаштування реального стеку
├── infra/                          # dev-стек
│   ├── compose.yaml                # контейнери стеку
│   ├── compose.local.example.yaml  # зразок зв'язування сервісів для робочої локальної системи
│   ├── proxy/                      # Caddyfile і конфігурація Admin UI
│   ├── postgres/                   # створення ролей і баз сервісів
│   ├── config/                     # storage-connections.json для dev-стеку
│   └── tests/                      # тести конфігурації стеку
├── deploy/profiles/                # профілі лімітів dev-laptop, ci, single-node і стенд їх вимірювання
│   ├── stack.py                    # стек із профілем лімітів і зв'язуванням сервісів
│   ├── compose.stack.yaml          # накладка на infra/compose.yaml для stack.py
│   ├── check.py, thresholds.json   # перевірка профілю за порогами
│   └── harness/                    # вимірювальний стенд і probe-site
├── examples/                       # відтворювані приклади на тестовому сайті й реальних джерелах
├── templates/service/              # шаблон нового сервісу для just new-service
├── tests/
│   ├── e2e/                        # наскрізні приймальні сценарії; jane_e2e/ — помічники, packages/ — тестові пакети
│   └── fixtures/testsite/          # детермінований тестовий магазин jane-testsite; expected_urls.json
├── scripts/
│   ├── dev.py                      # виконавець рецептів just
│   ├── docs_check.py               # статична перевірка документації
│   ├── docs_diagrams.py            # експорт і перевірка діаграм Draw.io
│   ├── contracts_lint.py           # лінтер контрактів
│   ├── llm_anthropic.py            # підключення провайдера Anthropic до стеку
│   ├── tg_session.py               # створення сесії Telegram у .jane/secrets
│   └── tests/                      # тести скриптів
├── docs/                           # документація; docs/README.md — точка входу
├── docs-archive/                   # попередня документація, поза навігацією
├── .agents/skills/, .claude/, .codex/  # інструкції й хуки агентів
├── .github/workflows/ci.yml        # CI
├── justfile                        # команди розробки
├── pyproject.toml, uv.lock         # uv workspace; налаштування ruff, mypy, pytest
├── TECHNICAL_SPECIFICATION.md      # технічне завдання
├── DOCUMENTATION_REQUIREMENTS.md   # вимоги до документації
├── plan.md                         # пакети робіт і правила
└── README.md
```

Учасники uv workspace: `contracts/python`, `libs/*`, `services/*`, `services/storage/adapters/*`, `templates/service`, `tests/fixtures/testsite`.

## Будова сервісу

Кожен каталог `services/<сервіс>/` має однакову будову:

```text
services/<сервіс>/
├── src/jane_<сервіс>/
│   ├── __main__.py     # точка входу: python -m jane_<сервіс>
│   ├── app.py          # FastAPI-застосунок і маршрути API
│   └── settings.py     # налаштування зі змінних JANE_<СЕРВІС>_*
├── tests/              # тести пакета
├── Dockerfile          # образ сервісу для dev-стеку
├── pyproject.toml      # пакет jane-<сервіс> і його залежності
├── README.md           # коротке призначення й посилання на docs/components/<модуль>/
└── CLAUDE.md           # інструкції агентів для цього сервісу
```

Інші модулі коду описано в `internals.md` модуля з [каталогу](../components/README.md).

## Точки входу

| Що | Команда | Код |
|---|---|---|
| Сервіс | `uv run --package jane-<сервіс> python -m jane_<сервіс>` або скрипт `jane-<сервіс>` | `services/<сервіс>/src/jane_<сервіс>/__main__.py` |
| CLI Handler Runtime | `jane-handler-runtime serve`, `run`, `test`, `profile`, `build-image` | `services/handler-runtime/src/jane_handler_runtime/cli.py` |
| Воркери Orchestrator окремо | `python -m jane_orchestrator worker` | `services/orchestrator/src/jane_orchestrator/__main__.py` |
| Вбудовані пакети Storage | `jane-storage-packages` | `services/storage/src/jane_storage/packages.py` |
| Генератор клієнтів API | `jane-codegen`, `just contracts-gen <api> <каталог>` | `libs/jane-kit/src/jane_kit/codegen.py` |
| Тестовий сайт | `just testsite` або `jane-testsite` | `tests/fixtures/testsite/src/` |
| Admin UI | `corepack pnpm --dir web/admin dev` | `web/admin/src/main.tsx` |
| Dev-стек | `just up`, `just down`, `just env`, `just ps`, `just logs` | `scripts/dev.py` |
| Стек із профілем | `uv run --all-packages python deploy/profiles/stack.py up` | `deploy/profiles/stack.py` |
| Приклади | `uv run --all-packages python examples/jane_examples.py <команда>` | `examples/jane_examples.py` |
| Новий сервіс | `just new-service <назва>` | `templates/service/` |

## Тести

| Де | Що перевіряє | Команда |
|---|---|---|
| `services/*/tests/`, `libs/*/tests/`, `templates/service/tests/` | модульні й контрактні тести пакета | `just test <сервіс>`, `just unit`, `just contract` |
| `services/storage/adapters/*/tests/` | адаптери збереження | `just test storage` |
| `services/web-collector/strategies/discovery/tests/` | стратегії пошуку | `just test web-collector` |
| `tests/fixtures/testsite/tests/` | тестовий сайт | `just unit` |
| `scripts/tests/`, `infra/tests/` | скрипти розробки й конфігурація стеку | `just unit` |
| `examples/tests/` | пакети й документи прикладів без сервісів | `just unit` |
| `deploy/profiles/tests/` | профілі лімітів і стенд | `just unit` |
| `tests/e2e/` | наскрізні сценарії на окремому стеку | `just e2e` |
| `web/admin/src/**/*.test.ts(x)`, `web/admin/e2e/` | Admin UI: модульні тести й Playwright | `just web` |
| маркери `integration`, `isolation` | тести з dev-стеком і тести ізоляції пісочниці (лише Linux) | `just integration`, `just isolation` |

`just check` запускає те саме, що CI: lint, типи, модульні й контрактні тести, а також перевірки `web/admin`. Деталі — [розробка](../development/README.md).

## Файли поза Git

| Шлях | Що містить |
|---|---|
| `.jane/stack-<проєкт>.json` | згенеровані паролі, ключі API й адреси стеку |
| `.jane/secrets/` | файли секретів (ключі провайдерів LLM, сесія Telegram); заповнює людина |
| `.jane/<сервіс>/` | локальний стан сервісу, запущеного без Docker (наприклад `state.db` Web Collector) |
| `infra/compose.local.yaml` | локальне зв'язування сервісів |
| `web/admin/dist/` | зібраний Admin UI |
