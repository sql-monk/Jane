# WP-23 / C-2. Python Protocol-пакет у uv workspace

**Гілка:** `wp/23b-contracts-workspace` · **Ревізія коду:** `3a70b939f8ca34321e2a369f0b86a839ee1a820e` ·
**База:** `b336922149c3b379f6946c82f6ee924b1720c56a` (`origin/codex/jane-integration` після fetch) ·
**Стан:** review · **Дата:** 2026-10-09.

Залежність відкрив маркер `ee78fc5`: `merge: accept WP-19 shared stores and files ContentRef transit`.
Координатор до старту автора додав власність `services/storage/adapters/*/pyproject.toml` у `b336922`.
Worktree: `C:/repos/Jane/.claude/worktrees/wp23b`, `.jane-wp = 23`; журнал потоку автор не змінював.

## Результат

- [`pyproject.toml`](../../../pyproject.toml): `contracts/python` став 19-м членом workspace;
  єдине спільне джерело `jane-contracts = { workspace = true }` розміщене в кореневому `tool.uv.sources`.
  Вісім локальних path-overrides вилучено з web-collector, storage та шести адаптерів. Залежність
  `jane-contracts` у `project.dependencies` кожного споживача збережена.
- [`scripts/dev.py`](../../../scripts/dev.py): `members()` читає актуальні `tool.uv.workspace.members`
  замість окремого списку шаблонів. Результат упорядкований і без повторів.
  Новий тест у [`scripts/tests/test_dev.py`](../../../scripts/tests/test_dev.py) звіряє знайдені пакети
  з `uv.lock` і явно вимагає Python Protocol-пакет.
- Mypy exclude пропускає решту `contracts/`, але включає `contracts/python`;
  `just types` реально перевірив усі три файли `jane_contracts`.
  Інструменти `contracts/tools` лишаються PEP 723-скриптами зі своїм лінтером; формат Protocol-пакета
  перевіряє наявна команда C-3. [`DEVELOPMENT.md`](../../../DEVELOPMENT.md) описує фактичний workspace
  та успадкування джерела.
- [`uv.lock`](../../../uv.lock): додано лише workspace membership та metadata шести адаптерів.
  Версії й хеші зовнішніх залежностей не змінено; resolver і до, і після зміни має 109 пакетів.
- Dockerfile читались без правок. Реальні образи storage, web-collector та llm зібрались;
  runtime-перевірки довели встановлений wheel Protocol-пакета, реєстрацію шести адаптерів і
  packaging сервісу без залежності від Protocol-пакета.

Жоден файл `contracts/`, API, Protocol, сценарій e2e, Dockerfile або параметр лімітів не змінений.
Contract-guardian для цього інкременту не потрібен; незалежний wp-reviewer призначає координатор.

## Рішення про вкладені адаптери

Пряме перенесення всіх восьми джерел на локальні `workspace = true` не працює у закріпленому
uv **0.12.13**. `uv workspace list` у корені бачить 19 пакетів, а з
`--directory services/storage/adapters/files` — лише `jane-storage-files`:
під час metadata discovery uv зупиняється на вкладеному проєкті під `services/storage`.
Ця особливість уже описана у README storage та коментарях pyproject адаптерів.

Спроба локального `workspace = true` для `jane-contracts` дає:

```text
$ uv lock                                      (.jane/wp23b-lock-debug.txt)
Using CPython 3.12.12
  × Failed to build `jane-storage-files @
  │ file:///C:/repos/Jane/.claude/worktrees/wp23b/services/storage/adapters/files`
  ├─▶ Failed to parse entry: `jane-contracts`
  ╰─▶ `jane-contracts` references a workspace in `tool.uv.sources` (e.g.,
      `jane-contracts = { workspace = true }`), but is not a workspace member
```

Перенесення також `jane-storage` і `jane-storage-s3` на локальні workspace-джерела відтворило ту саму
помилку для `jane-storage` (`.jane/wp23b-lock-refresh.txt`); цю експериментальну правку повернено.
Новий lock без кешу та `--no-config` також не обходили помилку discovery.

Рішення — кореневе джерело `jane-contracts = { workspace = true }`, яке успадковують усі члени,
без локальних overrides. Саме таке успадкування визначає
[документація uv](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources).
Path-джерела **інших** залежностей адаптерів (`jane-storage`, `jane-storage-s3`) лишаються чинними.
Це виконане перенесення `jane-contracts` у workspace; fallback із збереженням його path-залежності не використано.

## Відповідність «Готово, коли» C-2

| Умова | Доказ | Результат |
|---|---|---|
| Старт після прийняття WP-19 | Маркер `ee78fc5`, база `b336922` | так |
| `contracts/python` у workspace, немає path-джерел `jane-contracts` | `uv workspace list`; пошук pyproject показує лише кореневе workspace-джерело | так |
| Повний locked sync | `uv lock --check`, `uv sync --all-packages --locked`: exit 0 | так |
| Protocol-пакет охоплений перевіркою типів | `just types`: `mypy contracts/python/src`, 3 файли | так |
| Типи, lint, contract | 22 успішні mypy-сесії; lint exit 0; 109 passed, 3 skipped | так із наведеними skips |
| Docker packaging без сторонніх правок | 3 реальні Docker build + 3 runtime import checks | так |
| Власність | `check-diff origin/codex/jane-integration`: 0 поза власністю | так |
| Незалежне review та фінальний CI інтеграції | Робота координатора після цього звіту | очікуються |

## Відповідність DoD (plan.md §4)

| Пункт | Стан | Примітка |
|---|---|---|
| API за контрактом, контрактні тести | так | Контрактів не змінено; лінтер із required Redocly, compat self-test і контрактні тести пройшли |
| Unit та інтеграційні тести, одна команда | так у межах зміни | `pytest scripts/tests/test_dev.py`: 32 passed; перевірено Linux packaging. Повний service integration — фінальний CI |
| Документація запуску й конфігурації | так | DEVELOPMENT: члени workspace, root source inheritance, mypy coverage |
| Dockerfile, health, журнали, метрики, кілька екземплярів | н/з | Нового сервісу немає; наявні Dockerfile без правок, три образи зібрані |
| Власність шляхів | так | 13 файлів коду/документації до звіту; зі звітом 14 |

## Команди перевірки та їхній вивід

Windows, CPython **3.12.12**, uv **0.12.13**, just **1.58.0** через
`uvx --from rust-just just`. Docker Desktop **29.8.0**, Linux containers; фактичний
Python у `python:3.12-slim` — **3.12.15**, uv у build — **0.12.13**.
Повні виводи збережено у `.jane/wp23b-*.txt` власного worktree.

```text
$ uv lock --check                              (.jane/wp23b-lock-check.txt)
Using CPython 3.12.12
Resolved 109 packages in 20ms
exit=0

$ uv sync --all-packages --locked               (.jane/wp23b-sync.txt)
Using CPython 3.12.12
Creating virtual environment at: .venv
Resolved 109 packages in 14ms
... 19 локальних пакетів зібрані ...
Prepared 19 packages in 27.44s
Installed 105 packages in 55.50s
...
 + jane-contracts==1.0.0 (from file:///C:/repos/Jane/.claude/worktrees/wp23b/contracts/python)
...
exit=0

$ uvx --from rust-just just types               (.jane/wp23b-types.txt)
$ uv run --all-packages mypy contracts\python\src
Success: no issues found in 3 source files
... 19 workspace-пакетів: Success ...
$ uv run --all-packages mypy scripts infra/tests
Success: no issues found in 6 source files
$ uv run --all-packages mypy examples
Success: no issues found in 9 source files
$ uv run --all-packages mypy deploy/profiles
Success: no issues found in 9 source files
exit=0
```

У `just types` — **22** успішні окремі mypy-сесії, загалом **370** перевірених source-файлів.

```text
$ uvx --from rust-just just lint                (.jane/wp23b-lint.txt)
$ uv run --all-packages ruff check .
All checks passed!
$ uv run --all-packages ruff format --check . contracts/python
484 files already formatted
... усі офлайнові перевірки контрактів [ok] ...
[skip] Redocly lint
All contract checks passed.
exit=0

$ JANE_CONTRACTS_REDOCLY=1 uvx --from rust-just just contract
                                                (.jane/wp23b-contract.txt)
... JSON Schema, OpenAPI, conventions/examples, Python interfaces, mocks, autonomy: [ok] ...
[ok] Redocly lint: ok (Woohoo! Your API descriptions are valid. 🎉)
Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=118, openapi_documents=8, openapi_examples=541, operations=118, python_files=3, schema_examples=46, schemas=16
All contract checks passed.
$ uv run --script contracts/tools/compat.py --self-test
... case 0–7: [ok] ...
[ok] identical schema has no findings
[ok] default oasdiff image is pinned by tag and digest: tufin/oasdiff:v1.33.0@sha256:6263a96dd2ef0726c54e21fea9b8e1607eac4841add0079324b424c1f52b819c
$ uv run --all-packages pytest -m contract
=== 109 passed, 3 skipped, 1447 deselected, 1 warning in 150.56s (0:02:30) ====
exit=0

$ uv run --all-packages --locked pytest -q scripts/tests/test_dev.py
                                                (.jane/wp23b-dev-tests.txt)
................................                                         [100%]
32 passed in 13.84s
exit=0

$ python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
                                                (.jane/wp23b-ownership.txt)
WP-23: 13 changed file(s), 0 outside ownership
exit=0
```

### Docker packaging

Попередньо `uv sync --frozen --no-dev --no-editable --dry-run --package ...` у трьох ізольованих
копіях точного набору `COPY` пройшов (storage із шістьма `--package` адаптерів, web-collector, llm;
`.jane/wp23b-packaging.txt`). Далі ті самі незмінені Dockerfile **реально** зібрані:

```text
$ docker build --progress plain -f services/storage/Dockerfile -t jane-wp23b-storage:packaging .
$ docker build --progress plain -f services/web-collector/Dockerfile -t jane-wp23b-web-collector:packaging .
$ docker build --progress plain -f services/llm/Dockerfile -t jane-wp23b-llm:packaging .
... кожен build завершив exporting/naming/unpacking to image ...
exit=0                                          (.jane/wp23b-docker-{service}.txt)

$ docker run --rm --network none --entrypoint python jane-wp23b-storage:packaging -c "..."
protocol= /app/.venv/lib/python3.12/site-packages/jane_contracts/storage_adapter.py
adapters= ['filesystem', 'minio', 'mongodb', 'postgresql', 's3', 'sqlserver']
exit=0
$ docker run --rm --network none --entrypoint python jane-wp23b-web-collector:packaging -c "..."
protocol= /app/.venv/lib/python3.12/site-packages/jane_contracts/discovery.py
exit=0
$ docker run --rm --network none --entrypoint python jane-wp23b-llm:packaging -c "..."
llm import ok; protocols are not selected
exit=0                                         (.jane/wp23b-docker-{service}-import.txt)
```

Runtime checks імпортували відповідні модулі; storage додатково перевірив точний набір entry points
`jane.storage.adapters`, llm — відсутність `jane_contracts` у встановлених дистрибутивах.
Сервіси й зовнішні БД не запускались. Три тимчасові image tags видалено без force
(`.jane/wp23b-docker-cleanup.txt`); `docker image ls --filter reference='jane-wp23b-*'` порожній.
Контейнери запускались із `--rm --network none`, без портів і власних persistent volumes.
Контейнери `puluj-g-*` та стеки інших потоків не змінювались.

## Конфігурація й ліміти

Нових runtime-параметрів або лімітів немає. Package source централізовано у кореневому pyproject;
PEP 723-залежності інструментів контрактів і версії зовнішніх бібліотек не змінені.

## Відомі обмеження

- `just contract`: два skips потребують dev-stack PostgreSQL для llm; третій — відсутній контракт
  шаблонного сервісу. Це не повне runtime-приймання сервісів.
- Наявний warning FastAPI: `Duplicate Operation ID cancelJob` у handler-runtime contract test.
- Standalone `uv sync` із каталогу вкладеного адаптера не відкриває root workspace. Наявні README
  адаптерів описують кореневі `just up` / `just integration` / `just down`, які використовують
  root workspace; їхні CLI-аргументи не змінені. Нова централізована source-конфігурація призначена
  для root workspace та наявних frozen Docker build, які перевірені вище.
- Docker packaging перевірено на трьох класах build-контексту, а не на кожному сервісному образі;
  решта образів і весь e2e — фінальний CI інтеграції координатора. Повний `just check` і `just e2e`
  локально не запускалися.
- Незалежне review та exact-SHA GitHub CI ще не є доказом цього звіту: їх фіксує координатор.

## Неперевірені інтеграції

Реальні LLM, IdP, AWS, Telegram — **не перевірено на реальному сервісі**. Цей інкремент не змінює їхні API
чи клієнти. Профілі `dev-laptop` і `single-node` виключено з обсягу за рішенням людини.

## Запити до інших власників

| Кому | Що потрібно | Навіщо |
|---|---|---|
| Власник `services/storage/README.md` / координатор | Оновити приклад pyproject адаптера в розділі «Адаптери»: прибрати рядок path-джерела `jane-contracts`, послатися на root source inheritance з DEVELOPMENT. Рядок path-джерела `jane-storage` зберегти | README поза шляхами C-2; старий override для `jane-contracts` тепер суперечить workspace membership |
| Координатор C | Призначити незалежного wp-reviewer; після прийняття злити інкремент та виконати один узгоджений фінальний workflow_dispatch інтеграції | Review та CI — умови прийняття, локальні targeted gates їх не підміняють |
