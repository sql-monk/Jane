# Команди перевірки

Усі команди розробки — рецепти `just` у корені репозиторію. `just` не запускає оболонку: кожен рецепт передається в [scripts/dev.py](../../scripts/dev.py) разом з аргументами, тож команди однакові на Windows і Linux, а лапки аргументів зберігаються (`just unit -v -k "not slow"`). Без встановленого just — `uvx --from rust-just just <рецепт>`.

## Зміст

- [Якість коду](#якість-коду)
- [Тести](#тести)
- [Dev-стек](#dev-стек)
- [Контракти й клієнти](#контракти-й-клієнти)
- [Інше](#інше)
- [Перевірені запуски](#перевірені-запуски)

## Якість коду

| Команда | Що робить |
|---|---|
| `just check` | `lint` + `types` + `unit` + `contract` + `web` і таблиця підсумку — те, що CI запускає в окремих job; зайві аргументи йдуть у pytest |
| `just lint` | `ruff check .`, `ruff format --check . contracts/python`, лінтер контрактів (без Redocly) |
| `just fmt` | `ruff check --fix .` і `ruff format .` — **змінює файли** |
| `just types` | `mypy` (strict) окремо для `src/` і `tests/` кожного члена workspace, потім `scripts`, `infra/tests`, `examples`, `deploy/profiles` |
| `just web` | Для кожного `web/<app>` з `package.json`: `pnpm install --frozen-lockfile`, `lint`, `typecheck`, `test`, `build` |
| `just sync` | `uv sync --all-packages` |

Налаштування ruff, mypy і pytest — у кореневому [pyproject.toml](../../pyproject.toml): довжина рядка 110, Python 3.12, `mypy --strict` з плагіном pydantic, каталоги `_generated/` пропускаються.

## Тести

| Команда | Що запускає | Потребує |
|---|---|---|
| `just unit [аргументи]` | Тести без маркерів `contract`, `integration`, `isolation` з `testpaths`; окремою сесією — офлайн-тести `examples/` і `deploy/profiles/` | — |
| `just contract [аргументи]` | Лінтер контрактів, самоперевірка `compat.py`, тести з маркером `contract` | — |
| `just test <ціль> [аргументи]` | Тести одного пакета без `integration` і `isolation`; ціль — `web-collector`, `jane-kit`, шлях або назва дистрибутива | — |
| `just integration [--project <ім'я>] [аргументи]` | Тести з маркером `integration` проти стеку цього checkout (`JANE_STACK_FILE`) | `just up` |
| `just isolation [аргументи]` | Тести ізоляції пісочниці Handler Runtime (`isolation`) | Linux і Docker; на інших ОС — пропуск з кодом `0` |
| `just e2e [аргументи]` | Наскрізні сценарії `tests/e2e` (маркер `e2e`); стек піднімає й прибирає фікстура | Docker |

Аргументи після рецепта передаються в pytest без `--`:

```powershell
just test jane-kit -k limits
just test web-collector -m integration
just unit services/storage/tests -x
```

Код виходу pytest `5` (тестів не знайдено) рецепти вважають успіхом. Виняток — `just e2e` з `JANE_E2E_REQUIRED=1` (CI): відсутність сценаріїв і кожен пропущений сценарій — помилка. Змінні e2e: `JANE_E2E_PROJECT` (compose-проєкт), `JANE_E2E_KEEP=1` (не прибирати стек), `JANE_E2E_WAIT_TIMEOUT` (секунди очікування health, типово 900). Структура тестів і маркери — [Тести](testing.md).

## Dev-стек

Стек — [infra/compose.yaml](../../infra/compose.yaml): PostgreSQL, SQL Server, MongoDB, MinIO, S3 (SeaweedFS), тестовий сайт, proxy і сервіси Jane. Кожен checkout має власний compose-проєкт, порти й томи, тож паралельні стеки не конфліктують.

| Команда | Що робить |
|---|---|
| `just up [сервіси] [--project <ім'я>] [--no-build] [--wait-timeout <с>]` | Генерує облікові дані (перший раз), збирає образи, піднімає сервіси й чекає health; без списку — `postgres sqlserver mongodb minio s3 testsite proxy`; друкує адреси |
| `just ps [--project <ім'я>]` | Стан контейнерів |
| `just logs [сервіси] [--tail <n>]` | Журнали (типово 200 рядків) |
| `just env [--project <ім'я>] [--format dotenv\|json]` | Адреси й згенеровані облікові дані: `JANE_STACK_<СЕРВІС>_<КЛЮЧ>=...` |
| `just down [--project <ім'я>]` | Зупиняє стек, дані зберігаються |
| `just down -v [--project <ім'я>]` | Зупиняє стек і **видаляє** томи, локально зібрані образи та файл `.jane/stack-<проєкт>.json` з паролями й ключами |

Деталі:

- **Назва проєкту** — `JANE_COMPOSE_PROJECT` або `jane-<каталог checkout>-<6 символів хешу шляху>`. `--project` (`-p`) задає інший.
- **Порти** — випадкові вільні порти `127.0.0.1`; конкретний порт — змінна `JANE_PORT_<СЕРВІС>` (наприклад `JANE_PORT_TESTSITE=18840`), адреса прив'язки — `JANE_BIND`.
- **Облікові дані** — генеруються під час першого `just up` і зберігаються в `.jane/stack-<проєкт>.json` (каталог поза Git). Сервіси працюють у режимі `auth_mode=api_key`; ключ оператора — `JANE_STACK_AUTH_ADMIN_API_KEY` у `just env`.
- **Локальні доповнення** — `infra/compose.local.yaml` (поза Git, зразок — `infra/compose.local.example.yaml`) додається до кожного виклику compose: наприклад, зв'язки Registry і Handler Runtime для роботи всієї системи.
- **Тайм-аут очікування** — `--wait-timeout` або `JANE_UP_WAIT_TIMEOUT` (типово 600 с).

Тестовий сайт окремо, без Docker: `just testsite [--host] [--port]` (типово `http://127.0.0.1:8080`) — [опис сайту](../../tests/fixtures/testsite/README.md).

## Контракти й клієнти

| Команда | Що робить |
|---|---|
| `just contracts-check [--redocly]` | Лінтер контрактів |
| `just contracts-compat [ref] [--oasdiff]` | Самоперевірка й зворотна сумісність із git-ревізією (типово `main`) |
| `just contracts-mock <api> [--port] [--host]` | Мок API з прикладів (типово порт `4010`) |
| `just contracts-gen <api> <каталог>` | Python-клієнт контракту без моделей |
| `just gen-client <spec> <каталог>` | Клієнт і моделі довільної OpenAPI-специфікації |

Призначення й приклади — [контракти: швидкий старт](../components/contracts/quickstart.md).

## Інше

| Команда | Що робить |
|---|---|
| `just` або `just --list` | Перелік рецептів з описами |
| `just new-service <ім'я>` | Сервіс із шаблону — [новий сервіс](new-service.md) |
| `just hooks` | git-хук pre-commit з gitleaks — [гігієна](hygiene.md) |
| `python .claude/hooks/jane_wp.py check-diff main` | Файли зміни поза шляхами свого WP — [процес WP](wp-process.md) |

## Перевірені запуски

Виконано 2026-10-11 на Windows 11, ревізія `48389a3`, через `uvx --from rust-just just`.

`just lint` (уривок):

```text
$ uv run --all-packages ruff check .
All checks passed!
$ uv run --all-packages ruff format --check . contracts/python
529 files already formatted
$ uv run --all-packages python scripts/contracts_lint.py
...
All contract checks passed.
```

`just test jane-kit` (уривок):

```text
$ uv run --all-packages pytest libs\jane-kit -m not integration and not isolation
...
=============== 279 passed, 24 deselected, 1 warning in 36.66s ================
```

`just isolation` на Windows:

```text
isolation tests run on Linux only (plan.md §9); skipped on win32
```

`just up testsite --project jane-doc-devkit` з `JANE_PORT_TESTSITE=18840`, потім `just ps`, `just env` і `just down -v` з тим самим проєктом (уривок):

```text
project: jane-doc-devkit   (stack file: .jane/stack-jane-doc-devkit.json)
  testsite   http://127.0.0.1:18840
  auth       api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)
```

```text
NAME                         IMAGE                      COMMAND                  SERVICE    CREATED              STATUS                        PORTS
jane-doc-devkit-testsite-1   jane-doc-devkit-testsite   "python -m jane_test…"   testsite   About a minute ago   Up About a minute (healthy)   127.0.0.1:18840->8080/tcp
```

`just integration` і `just e2e` у межах цього розділу не запускались (потребують повного стеку); їх виконує CI ([CI](ci.md)).
