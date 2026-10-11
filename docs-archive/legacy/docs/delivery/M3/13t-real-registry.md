# WP-13t. Реальний registry в e2e-фікстурах, обов'язковий e2e, уточнення матриці

**Гілка:** `wp/13t-real-registry-fixtures` · **Код перевірено на:** `b24ffc1` · **База:** `3a7108f` (WP-13r,
у `codex/jane-integration` це `08b4110`) · **Стан:** review

Наскрізне доручення координатора за фінальним рев'ю M3, частина A. `.jane-wp` не створювався. Змінено лише
дозволені шляхи: `tests/e2e/**`, `docs/acceptance/**`, `scripts/dev.py` (код виходу e2e),
`.github/workflows/ci.yml` (env job e2e), цей звіт. `tests/e2e/test_r04_active_replays.py` не змінено.

## Результат

### 1. Оркестровані сценарії беруть пакети з реального registry (знахідка 1)
- `conftest.extractor` публікує приклад екстрактора SDK у **реальний registry** стеку. Що відбувається:
  створення пакета, публікація канонічного архіву, погодження (`approved`), перевірка дайджесту
  відповіді registry й завантаженого архіву (`ETag` і SHA-256). Фікстура повертає
  `package_id@version` + дайджест registry. `conftest.orchestrated` замість `package-host` вимагає
  `registry`.
- `jane_e2e/registry.py`: нові `publish_archive` / `publish_fixture_package`. Вони ідемпотентні на
  спільному стеку: наявний пакет використовується повторно, а наявна версія мусить мати той самий
  дайджест. Маніфест перевіряється схемою контракту.
- `E2EStack.publish_local_package` (його викликає `test_r04_active_replays.py`) тепер публікує в реальний
  registry і повертає ref. `active.package_ref` дає канонічний архів registry, тож той самий ref дійсний і
  для прямого виклику з `package_archive`, і для версії в registry.
- `compose.e2e.yaml` (мінімально):
  - типові `JANE_HANDLER_RUNTIME_REGISTRY_URL` і `JANE_LLM_REGISTRY_URL` → `http://registry:8000`;
  - `JANE_REGISTRY_RUNTIME_PROFILES` → профіль runtime (`/v1/info`), бо registry перевіряє залежності
    екстракторів;
  - `package-host` без каталогу архівів.
- `package_host.py` більше не віддає архівів, лишилися тільки «шлюзи» `download_url` R-04. Це **З**
  blob-сховища, позначене в коді й матриці.
- `test_m2_llm_routing.py` (S-M2-05, S-M2-11) і `test_reliability_orchestrated.py` (R-01/03/08)
  публікують фікстури через `registry_package`. Через оркестратора тепер на registry проходять:
  S-M1-03/05/06 (`test_m1.py`), S-M2-08 (`test_m2_storage.py`) і S-M2-09 (`test_m2_limits.py`).
  У S-M1-03 додано перевірку `package_sources` runtime.
- Знайдено й виправлено прогалину фікстури. `e2e.instock-product-extractor` не мав тестів пакета, і
  реальний registry відхилив його з 422 `tests_required`; `package-host` цього не перевіряв. Додано ті
  самі два тести, що й у `e2e.improvable-product-extractor`: код ідентичний, CLI runtime дає 2/2.

### 2. `standin_web_material` (знахідка 2)
- R-02, R-05, R-06 runtime (`test_reliability.py`) і R-06 storage (`test_r06_storage_registry.py`) беруть
  матеріал з **реального Web Collector** (`POST /v1/fetches`). Це дешево: колектор і так працює в
  спільному стеку.
- S-M2-05a лишився з матеріалом, який тест формує сам, і в матриці явно позначений як **«вхід прямого
  виклику»**. Обґрунтування: перевіряється політика прапорця асистента, а не колектор. До того ж URL
  матеріалу Web Collector `http://testsite:8080/…` збігся б зі скриптом класифікації асистента в
  `llm-seed.yaml` (S-M2-06), і сценарій перестав би перевіряти те, що мав. Новий пункт «Як читати» в
  `matrix.md` описує цю позначку. Докстрінг `jane_e2e/materials.py` більше не називає хелпер
  тимчасовим замінником.

### 3. Обов'язковий e2e (знахідка 3)
- `JANE_E2E_REQUIRED=1` змінює поведінку так:
  - `conftest.stack`: без Docker — `pytest.fail`;
  - хук `pytest_runtest_makereport`: кожен skip e2e-сценарію стає failed; xfail не зачіпається;
  - `scripts/dev.py e2e`: pytest exit 5 (нічого не зібрано) — помилка.
- У job e2e (`.github/workflows/ci.yml`) змінна задана. Без неї локальна поведінка попередня.

### 4. Формулювання матриці (знахідка 4)
- Критерій 11 (зведення, деталі) і S-M2-05 у `scenarios.md`: «сторінка з ін'єкцією проходить як дані
  (**З**); стійкість до ін'єкції — unit WP-10, на реальній LLM не перевірено». Пояснено, чому сценарій не
  може виявити вплив: сід відповідає `faq` на будь-які дані з `<h1>FAQ</h1>`.
- Критерій 8, «Що доводить»: прибрано обіцянку kill колектора посеред ланцюжка. Тепер там R-01 (kill
  репліки оркестратора), R-02 (kill і рестарт виконавця) і R-03 (розрив мережі). Додано пряму примітку,
  що kill колектора посеред ланцюжка e2e не відтворює. Нового сценарію немає.

### 5. Масштаб після сценаріїв (знахідка 5)
Нова фікстура `scale` у `conftest.py`: її фіналізатор повертає кожен масштабований сервіс до 1 репліки.
Її використовують `test_r04_idempotency.py` (колектори, LLM ×2) і `test_r06_storage_registry.py`
(storage, registry ×2).

Маркування оновлено в `docs/acceptance/matrix.md` (критерії 2, 3, 8, 11, 13, «Як читати») і
`docs/acceptance/scenarios.md` (принципи 3 і 5, змінні, таблиця, S-M1-03, S-M2-01, S-M2-05a, S-M2-05,
S-M2-11, надійність).

## Команди перевірки та їхній вивід

```text
$ uv run --all-packages ruff check tests/e2e scripts/dev.py
All checks passed!
$ uv run --all-packages ruff format --check tests/e2e scripts/dev.py
38 files already formatted
$ uv run --all-packages mypy tests/e2e
Success: no issues found in 36 source files
$ uv run --all-packages mypy scripts
Success: no issues found in 4 source files
```

Обов'язковий режим, перевірено тимчасовим тестовим модулем (після перевірки видалено):

```text
=== default (no JANE_E2E_REQUIRED)
SKIPPED [1] tests\e2e\test_zz_tmp_required.py:5: precondition not reached
XFAIL tests/e2e/test_zz_tmp_required.py::test_tmp_xfail - known defect
1 skipped, 1 xfailed in 0.17s
=== JANE_E2E_REQUIRED=1
JANE_E2E_REQUIRED=1: the scenario was skipped, which is an error here: Skipped: precondition not reached
XFAIL tests/e2e/test_zz_tmp_required.py::test_tmp_xfail - known defect
1 failed, 1 xfailed in 0.18s
=== no docker on PATH, default
SKIPPED [1] tests\e2e\test_zz_tmp_docker.py:4: docker не знайдено
1 skipped in 0.03s
=== no docker on PATH, JANE_E2E_REQUIRED=1
___________________ ERROR at setup of test_tmp_needs_stack ____________________
JANE_E2E_REQUIRED=1, but docker не знайдено
1 error in 0.03s
=== zero collected, default            ($ python scripts/dev.py e2e -k no_such_scenario_xyz)
71 deselected in 2.37s
dev exit=0
=== zero collected, JANE_E2E_REQUIRED=1
71 deselected in 2.04s
JANE_E2E_REQUIRED=1: no e2e scenario was collected
dev exit=5
```

Тести пакета-фікстури після додавання (CLI runtime, Docker-пісочниця):

```text
$ uv run --all-packages python -m jane_handler_runtime.cli test tests/e2e/packages/e2e.instock-product-extractor --image jane-e2e-wp13t-local-python-extractor:1
Package e2e.instock-product-extractor@1.0.0 (sha256:fa1a5ef86207ef82f53965879d7916a9f231562090faedbdce59e5997e040ea6), backend=docker
  PASS in-stock-card: expected success, got success
  PASS category-page-empty: expected empty, got empty
2 passed, 0 failed
```

### CI

[CI 37825596907](https://github.com/sql-monk/Jane/actions/runs/37825596907) (`workflow_dispatch` на
`b24ffc1`): `completed success`, усі 12 job: lint, unit, web, contract, isolation, stack, e2e, limits і
чотири adapters. Рядок job e2e (`JANE_E2E_REQUIRED: 1`, `uv run --all-packages pytest tests/e2e -m e2e -v`):

```text
======================= 71 passed in 1318.40s (0:21:58) ========================
```

0 skipped, 0 failed, 0 xfailed. Серед них уражені сценарії: S-M1-03/05/06, S-M2-05a, S-M2-05 (обидва),
S-M2-08, S-M2-09, S-M2-11, R-01, R-02, R-03, R-05, R-06 (runtime, storage, registry), R-08 (обидва),
R-04 `test_r04_idempotency.py` (13) і всі 9 `test_r04_active_replays.py` (зокрема orchestrator через
`publish_local_package` → registry). Повний журнал job — `.jane/wp13t-ci-e2e-37825596907.log`
у checkout (не комітиться).

### Локальні прогони
Адресний прогін 26 уражених сценаріїв на одному стеку (`jane-e2e-wp13t-local`, Windows, Docker Desktop)
двічі переривала пауза на вимогу людини: контейнери зупиняли посеред прогону. Тому як доказ ці прогони
**недійсні**. Перший прогін до зупинки дав 21 PASSED. Єдиний FAILED, S-M2-11, і виявив `tests_required`
фікстури (виправлено в `50ac5a1`). Другий прогін зупинено на першому сценарії. Стек прибрано (`down -v`;
контейнерів, томів і пісочниць проєкту — 0). Повторювати не став: CI на тому самому коді пройшов увесь e2e.

## Відомі обмеження
- Оркестратор спільного стеку, як і раніше, без виконавця `registry` (`executors-none.json`). Етапи
  зафіксовано дайджестом registry, і runtime та LLM-шлюз завантажують архіви з registry. Але оркестратор
  не звіряє пакет із registry під час створення завдання; так працює лише S-M2-04/06/07 зі своїм стеком.
  Для критеріїв 3 і 11 це не потрібно.
- Пакети `jane.storage-*` на спільному стеку виконує storage як вбудовані (`JANE_STORAGE_REGISTRY_URL`
  порожній). Це штатний режим WP-07, не замінник. Етапи storage з дайджестами registry перевіряє S-M2-01.
- Web Collector спільного стеку бере правила `testsite.web-rules` з локального каталогу правил
  (`JANE_WEB_COLLECTOR_RULES_DIR`). Це штатна можливість колектора; правила з registry перевіряє S-M2-01.
- Прямі виклики runtime без оркестратора (S-M1-01/02, R-02/05/06, частина S-M2-08) лишаються з
  локальним inline-архівом SDK. Це навмисно: критерій 1, сторонній застосунок.

## Неперевірені інтеграції
- Реальна LLM — не перевірено на реальному сервісі: стійкість до ін'єкції лише в unit WP-10.
- Локальний адресний Docker-прогін на Windows недійсний (див. вище), тож Linux CI — єдиний повний доказ.

## Запити до інших власників
| Кому | Що потрібно | Навіщо |
|---|---|---|
| Координатор | Під час злиття зважити на паралельні зміни `tests/e2e/compose.e2e.yaml` (автентифікація, ContentRef). Тут змінено типові URL registry для runtime і LLM, `JANE_REGISTRY_RUNTIME_PROFILES` і блок `package-host` (команда й том) | Можливі текстові конфлікти поруч із рядками токенів і allowlist |
| R-04 (агент `test_r04_active_replays.py`) | `stack.publish_local_package` тепер публікує в реальний registry (сервіс `registry` має працювати; `orchestrated` його вже піднімає). `active.package_ref` дає канонічний архів registry. `package-host` архівів не віддає | Оркестрований R-04 і так пройшов у CI 37825596907; нові сценарії мають брати пакети з registry |
