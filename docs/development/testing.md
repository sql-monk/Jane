# Тести

Де лежать тести Jane, як їх позначати маркерами, які рецепти що збирають і за якими правилами писати нові. Команди запуску — [Команди перевірки](checks.md#тести).

## Зміст

- [Розташування](#розташування)
- [Маркери](#маркери)
- [Налаштування pytest](#налаштування-pytest)
- [Правила](#правила)
- [Тестові дані й допоміжні засоби](#тестові-дані-й-допоміжні-засоби)

## Розташування

```text
Jane/
├── libs/<бібліотека>/tests/              # unit- і контрактні тести бібліотек (jane-kit, extractor-sdk)
├── services/<сервіс>/tests/              # тести сервісу: unit, contract, integration
├── services/web-collector/strategies/discovery/tests/   # стратегії пошуку
├── services/storage/adapters/<адаптер>/tests/           # адаптери: integration з dev-стеком
├── templates/service/tests/              # шаблон: unit і контрактний тест (копіюється в новий сервіс)
├── tests/fixtures/testsite/tests/        # тестовий сайт і його очікувані набори URL
├── infra/tests/                          # dev-стек: конфігурація автентифікації, smoke стеку
├── scripts/tests/                        # scripts/dev.py і хуки Claude Code
├── examples/tests/                       # офлайн-перевірка відтворюваних прикладів
├── deploy/profiles/tests/                # профілі лімітів і стенд їх вимірювання
├── tests/e2e/                            # наскрізні приймальні сценарії (поза testpaths)
└── web/admin/                            # Admin UI: vitest (src/), Playwright (e2e/)
```

Каталоги `tests/` усередині пакетів обробників (`.../package/tests/`, `tests/e2e/packages/*/tests/`, `examples/**/packages/*/tests/`) — не pytest, а тестові випадки пакета: вхід (`page.html`) і очікуваний результат (`expected.json`). Їх виконує тестовий запуск пакета обробника, наприклад `POST /v1/test-runs` контракту `handler.v1` ([пакети обробників](../reference/packages/README.md)).

Кореневий `testpaths`: `libs`, `services`, `templates/service`, `tests/fixtures`, `scripts/tests`, `infra/tests`. `examples/` і `deploy/profiles/` збираються окремою сесією `just unit`, бо їхні `conftest.py` додають у `sys.path` модулі з загальними назвами. `tests/e2e` збирає лише `just e2e`.

## Маркери

| Маркер | Значення | Хто запускає |
|---|---|---|
| без маркера | Unit-тест: без мережі поза процесом, без Docker | `just unit`, `just test`, CI job `unit` |
| `contract` | Перевіряє API проти OpenAPI-контракту | `just contract`, CI job `contract` |
| `integration` | Потребує dev-стеку (`just up`) або інших зовнішніх процесів | `just integration`, CI job `stack` і `adapters` |
| `isolation` | Ізоляція пісочниці Handler Runtime, лише Linux | `just isolation`, CI job `isolation` |
| `e2e` | Наскрізний сценарій на повному стеку; маркер реєструє `tests/e2e/conftest.py` | `just e2e`, CI job `e2e` |

Маркери оголошено в кореневому `pyproject.toml`; `--strict-markers` робить невідомий маркер помилкою. Позначення модуля цілком — `pytestmark = pytest.mark.contract`.

## Налаштування pytest

- `--import-mode=importlib`: кожен пакет має власний `tests/` без конфліктів імен.
- `asyncio_mode = "auto"`: async-тести без декоратора.
- `--strict-config`, `-ra` (підсумок пропусків і падінь).
- Попередження `PytestUnraisableExceptionWarning` — помилка.

## Правила

- **Не мокати сам компонент.** Сервіс тестується справжнім застосунком (`TestClient(build_app(...))`); моки — лише сусіди й лише з контрактів: `jane_kit.contracts.build_mock_app` або `just contracts-mock` ([jane-kit](../components/jane-kit/integration.md#контрактні-тести-й-моки)).
- **Контрактний тест** перевіряє кожну відповідь через `ContractClient`; `uncovered()` показує операції без перевірки.
- **Інтеграційний тест** знаходить стек через `jane_kit.devstack.load_stack()` і пропускається, якщо стеку немає; `just integration` передає `JANE_STACK_FILE`, тож тест не підхопить стек іншого checkout.
- **Ліміти** в тестах задаються шарами конфігурації, а не зміною типових значень у коді.
- **Не послаблювати** тести, щоб пройти; тести з браузером (`fetch.render_js`) локально без Chromium пропускаються, а в CI (змінна `CI`) падають.
- **Кросплатформність**: шляхи через `pathlib`, тимчасові файли — фікстура `tmp_path`.

## Тестові дані й допоміжні засоби

| Засіб | Призначення |
|---|---|
| [Тестовий сайт](../../tests/fixtures/testsite/README.md) | Детермінований сайт: сторінки, Sitemap, RSS/Atom, API, пошук, пастки; набори очікуваних URL для кожної стратегії |
| `jane_testsite.serve_in_thread()` | Тестовий сайт у фоновому потоці на випадковому порту (для pytest) |
| `jane_kit.devstack.load_stack()` | Адреси й облікові дані стеку `just up` |
| `contracts/examples/` | Валідні приклади запитів і відповідей для тестів і моків |
| `tests/e2e/jane_e2e/` | Помічники наскрізних сценаріїв: клієнти, стек, публікація пакетів у Registry |
| `tests/e2e/packages/` | Пакети обробників для наскрізних сценаріїв |
