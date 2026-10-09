# Сценарії приймання (e2e)

Сценарії для віх M1 і M2 (plan.md §6), надійності WP-13 та інкрементів після M3 (WP-20/WP-21).
Який сценарій закриває який критерій ТЗ §12, показано в [matrix.md](matrix.md).
Код лежить у [`tests/e2e/`](../../tests/e2e).

## Фінальна ревізія

Єдиний блок SHA / CI / підсумку остаточного прогону — у
[матриці, «Фінальна ревізія»](matrix.md#фінальна-ревізія); його заповнює потік A.
Нижче — актуальні реалізовані сценарії й докази інтегрованих інкрементів на 2026-10-09.

## Після M3

[CI 37905643300](https://github.com/sql-monk/Jane/actions/runs/37905643300) гілки
`wp/21-post-m3-followups` на `f69854e429cedf71a6eedfb03897f7518a0da9c5` — **completed / success**.
[job e2e](https://github.com/sql-monk/Jane/actions/runs/37905643300/job/113740900134):
`77 passed in 1435.40s (0:23:55)`, `JANE_E2E_REQUIRED=1`; R-03 з історією спроб і S-M3-01/02 — явні **PASSED**.
Це новий доказ після прийняття M3; історична «Фінальна ревізія» збережена.

S-M2-10 після WP-20/R26: **25 повністю / 0 частково / 1 навмисний мок із 26**; real-набір — **18**
(повний прогін `18 passed (4.6m)` на `3a3251c` і адресні контролі змінених специфікацій на `df7f252`).
Окремі UI-докази та межі — [WP-20](../delivery/WP-20.md#команди-перевірки-та-їхній-вивід) і
[матриця](matrix.md#s-m2-10-адмінка-на-реальному-api).

## Принципи

1. **Лише реальні компоненти Jane.** Сервіс, який приймаємо, ніколи не мокається. Сценарій іде через
   публічні API за контрактами. Кожен запит і кожна відповідь перевіряються схемою з `contracts/openapi`
   (`jane_kit.contracts.ContractClient`), тож розбіжність із контрактом валить сценарій. Явний виняток:
   sync replay `POST /v1/completions` під час роботи повертає 409 за загальною конвенцією; поки цей статус
   не додано до OpenAPI endpoint, тіло Problem перевіряється напряму (запит WP-00 у WP-13s). Так само
   (WP-21) `GET /v1/objects/{id}/content` для RAW, збереженого в початковому `text/plain` (S-M3-02): storage.v1
   описує Content-Type як медіатип об'єкта, але перелічує лише `application/octet-stream`, `text/html` і
   `application/json`, тож статус, Content-Type і байти цього виклику перевіряються напряму (запит власнику
   контракту — у [звіті WP-21](../delivery/WP-21.md)).
2. **Замінники зовнішніх систем позначаються явно:** фейковий провайдер LLM (WP-10), записаний або фейковий
   клієнт Telegram (WP-04), статичний пошуковий провайдер (WP-11), SeaweedFS замість AWS S3 (WP-01).
   У матриці вони мають позначку **З**.
3. **Тимчасові замінники компонентів** мають позначку **Т**. Після WP-13t їх у сценаріях немає.
   Оркестровані сценарії публікують пакети-фікстури й приклад екстрактора SDK у реальний registry
   (погодження, `package_id@version`, дайджест registry, перевірка завантаженого архіву), а `package-host`
   лишився тільки «шлюзом» `download_url` для R-04 (**З** blob-сховища) і архівів не віддає.
   Material, який тест як сторонній застосунок сам формує з відповіді testsite для прямого виклику
   виконавця (S-M2-05a, R-04 під час роботи), позначено «вхід прямого виклику»: він не заміщує ланку
   ланцюжка Jane, і висновків про Web Collector із таких сценаріїв не роблять.
4. **Незалежність від стану.** Кожен прогін має свій `run_id`, від якого залежать `source_id` (а отже
   `key.scope` сутностей), `observation_id` і `delivery_key`. Тому сценарії можна повторювати на тому самому
   стеку. Сховище перевіряється через `storage.v1`: список об'єктів, метадані й вміст. У S-M1-01
   RAW-файл додатково читається прямо з тому; таблиці PostgreSQL ці сценарії прямо не читають.
5. **Обов'язковий прогін не пропускає сценарії.** Локально недоступний стек може дати `skip` із причиною.
   Режим `JANE_E2E_REQUIRED=1` (job e2e у CI) робить помилкою і відсутність Docker, і кожен
   `skip` сценарію, а `just e2e` — ще й нуль зібраних сценаріїв (exit 5). Тож зелений обов'язковий прогін
   означає, що виконано кожен зібраний сценарій. Без змінної (локально) поведінка попередня.

## Запуск

```text
uv run --all-packages pytest tests/e2e -m e2e -v            # піднімає стек, проганяє, прибирає (down -v)
JANE_E2E_KEEP=1 uv run --all-packages pytest tests/e2e -v    # стек лишається (повторні прогони швидші)
uv run --all-packages pytest tests/e2e -v -k s_m1_01         # один сценарій
```

`just check` сценаріїв e2e не запускає: `tests/e2e` не входить до `testpaths` кореневого `pyproject.toml`,
а маркер `e2e` реєструє `tests/e2e/conftest.py`. Окремий рецепт `just e2e` запускає їх у CI після WP-01a.

Потрібні Docker (Compose v2) і `uv`. Сервіси Jane описані в `infra/compose.yaml` (WP-01a), а накладка
`tests/e2e/compose.e2e.yaml` додає тестові налаштування. Проєкт унікальний (`jane-e2e-<хеш checkout>` або
`JANE_E2E_PROJECT`), порти хоста обирає Docker, облікові дані генеруються. Файл стеку
`.jane/stack-<проєкт>.json` має ту саму форму, що й у `just up`, тож `just env --project <проєкт>` працює.
Сервіси піднімаються ліниво: сценарій запускає лише те, що йому потрібно. Для handler-runtime стек
збирає образ пісочниці `python-extractor@1` (`jane-handler-runtime build-image`) і передає сервісу
Docker-сокет із групою, визначеною автоматично (`JANE_DOCKER_GID`).

Змінні: `JANE_E2E_PROJECT`, `JANE_E2E_KEEP`, `JANE_E2E_REQUIRED` (`1` — обов'язковий e2e, див. принцип 5),
`JANE_E2E_WAIT_TIMEOUT` (типово 900 с),
`JANE_E2E_SANDBOX_WALL_TIME_MS` (типово 60000; ліміт запиту до пісочниці), `JANE_E2E_DOCKER_SOCKET`,
`JANE_E2E_DOCKER_GID`, `JANE_E2E_SANDBOX_IMAGE`, `JANE_E2E_HTTP_KEEPALIVE_S` (типово 2 с; час простою,
після якого тестовий клієнт не використовує з'єднання повторно; має бути меншим за keep-alive сервісів —
5 с у uvicorn).

## Стан сценаріїв

Повний [CI 37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903) на `cdf261a`,
[job e2e](https://github.com/sql-monk/Jane/actions/runs/37853683903/job/113574852651):
`75 passed in 1486.98s (0:24:46)`, 0 skipped/xfail. Сценарії M1/M2 та надійності таблиці, крім окремого
UI-набору S-M2-10, мають явні рядки **PASSED** в цьому job. Новий R-03 і S-M3-01/02 підтверджено
в CI 37905643300 (розділ «Після M3» вище). Позначка **Р** стосується реальних сервісів Jane;
**З** — названого зовнішнього замінника. Точні назви тестів для критеріїв — у [матриці](matrix.md).

| ID | Назва | Критерії | Сервіси | Стан |
|---|---|---|---|---|
| S-M1-01 | Web Collector → RAW у files ‖ екстракція → PostgreSQL | 1, 2, 8, 12 | web-collector, storage, handler-runtime, postgres, testsite | PASSED, Р |
| S-M1-02 | Колекція з ack і повторною доставкою → RAW та екстракція | 1, 2, 12 | web-collector, storage, handler-runtime | PASSED, Р |
| S-M1-03 | M1-завдання: RAW, екстракція, trace, unknown | 2, 8, 11, 12 | orchestrator, registry, виконавці | PASSED, Р |
| S-M1-04 | Сторонній застосунок: рекурсивний збір, runtime CLI | 1, 10 | web-collector, handler-runtime | PASSED, Р |
| S-M1-05 | Заміна files ↔ PostgreSQL конфігурацією завдання | 3 | orchestrator, storage, handler-runtime, registry | PASSED, Р |
| S-M1-06 | Новий прогін → нове спостереження й подія історії | 8 | orchestrator, storage, handler-runtime, registry | PASSED, Р |
| S-M2-01 | Типи пакетів, версії, форк і оновлення батька | 7, 9 | registry, runtime, storage, llm, orchestrator | PASSED (`test_m2_registry*.py`), Р; LLM — З |
| S-M2-02 | Telegram: історія, нові й редагування → RAW JSON | 1, 8, 12 | telegram-collector, storage | PASSED, Р; Telegram backend — З |
| S-M2-03 | Стратегії окремо й разом проти `expected_urls.json` | 10 | web-collector, testsite | 10 PASSED, Р |
| S-M2-04 | Каталог і перевірка цін — окремі завдання | 5 | orchestrator, registry, виконавці, штатний testsite | PASSED, Р |
| S-M2-05a | Асистент викликає LLM лише з прапорцем, автономно | 11 | assistant, llm, postgres, testsite | PASSED, Р; LLM — З; матеріал — вхід прямого виклику |
| S-M2-05 | Невідомі сторінки й injection-дані в завданні | 11 | orchestrator, registry, виконавці | PASSED, Р; LLM — З; стійкість реальної моделі до ін'єкції не доведена |
| S-M2-06 | Нове джерело → пропозиції → пакет → тести → завдання | 4 | assistant, llm, registry, web-collector, runtime, orchestrator | 2 PASSED, Р; LLM і пошук — З |
| S-M2-07 | Проблеми → версія → тести → активація → відкат | 6 | orchestrator, assistant, llm, registry, runtime | PASSED, Р; LLM — З |
| S-M2-08 | RAW + сутності в усіх 6 адаптерах | 3, 12 | storage, orchestrator, registry, сховища | PASSED, Р; AWS S3 — З (SeaweedFS) |
| S-M2-09 | Ліміти platform → task без перезбирання | 13 | orchestrator, виконавці, registry | PASSED, Р; профіль `ci` виміряний, див. матрицю |
| S-M2-10 | Адмінка через Caddy й реальні API | 4, 6, 7 (UI) | admin, усі API | після WP-20/R26: **25 повністю / 0 частково / 1 навмисний мок**; **18** real-сценаріїв; окремі докази нижче |
| S-M2-11 | Умови `when` і LLM-етап проблемних результатів | 2 | orchestrator, registry, виконавці | PASSED, Р; LLM — З |
| R-01 | Kill воркера посеред активного виклику, takeover lease | 8 | orchestrator ×2, виконавці | PASSED, Р; той самий run/job, одиничні ефекти, 409 без витрати спроби |
| R-02 | Kill/рестарт і replay кожного сервісу | 8 | усі 8 сервісів | PASSED, Р; зовнішні Telegram/LLM — З |
| R-03 | Мережева ізоляція storage, backoff і відновлення | 8 | orchestrator, storage, runtime | CI 37905643300 / PASSED, Р; причинність через `attempt_history` / `available_at`, звірка з trace |
| R-04 | Replay кожного виконавця, також під час активної роботи | 8 | усі 8 сервісів | PASSED, Р; WP-13s включає completions sync/async і onboarding/improvement; зовнішні LLM/Telegram/blob — З |
| R-05 | Запізнілий результат не замінює новішого | 8 | storage, runtime | PASSED, Р |
| R-06 | Дві репліки, спільні job/idempotency/стан | 8 | усі 8 сервісів | PASSED, Р; зовнішні Telegram/LLM — З |
| R-07 | Вдосконалення під навантаженням і з рестартами | 6, 8 | orchestrator, assistant, llm, registry, runtime, storage | 5 PASSED, Р; LLM — З; активна пісочниця кандидата в мить kill не підтверджена |
| R-08 | Backpressure стримує збір і не перевищує max_unacked | 8, 13 | orchestrator, web-collector | 2 PASSED, Р |
| S-M3-01 | Повторна обробка точно вибраних збережених RAW (`object_ids`, R06) | 6 | orchestrator, storage, handler-runtime, registry, web-collector | після M3: CI 37905643300 / PASSED (WP-21); Р |
| S-M3-02 | Telegram JSON-RAW: відновлення вмісту й повторна обробка з тим самим `sha256` (R01) | 1, 12 | telegram-collector, storage, orchestrator | після M3: CI 37905643300 / PASSED (WP-21); Р; Telegram backend — З |

Не перевірені живі зовнішні системи та ручна перевірка Telegram —
[матриця, «Не перевірено на реальних сервісах»](matrix.md#не-перевірено-на-реальних-сервісах).

## M1 — перший наскрізний зріз

### S-M1-01. Web → RAW у files ‖ екстракція локальним пакетом → PostgreSQL
`tests/e2e/test_m1.py::test_s_m1_01_collector_fetch_to_files_and_extraction_to_postgres`

1. Сторонній клієнт викликає `POST /v1/fetches` реального Web Collector для `/product/phone-alpha`
   на testsite та отримує `Material` через `collector.v1`.
2. **Гілка RAW.** Виклик `POST /v1/invocations` storage: `jane.storage-files`, підключення `raw-files`.
   Очікується `success`, `WriteAck.status = written`, файл `.html`, `sha256` збігається. Файл на томі storage
   (`docker compose exec storage cat …`) збігається з відповіддю testsite байт у байт. `GET /v1/objects`
   знаходить рівно один об'єкт цього спостереження, а `GET /v1/objects/{id}/content` повертає ті самі байти.
3. **Повторна доставка RAW** (той самий `delivery_key`): `duplicate: true`, `status: duplicate`, об'єкт і далі один.
4. **Гілка екстракції.** Виклик `POST /v1/invocations` handler-runtime: пакет
   `libs/extractor-sdk/examples/testsite-product-extractor` як inline-архів з дайджестом, без репозиторію,
   у пісочниці Docker. Очікується `success`, одна сутність `product`, ключ `{scope: e2e-<run>, sku:
   phone-alpha}`, поля як в очікуваному результаті пакета, `provenance.package.digest` дорівнює дайджесту архіву.
5. **Збереження сутностей.** `jane.storage-postgresql` у підключення `results-pg` (схема `e2e_results`
   PostgreSQL стеку), очікується `written`. Повторна доставка дає `duplicate`. `GET /v1/entities` показує
   `version = 1` і ті самі поля, `GET /v1/entity-history` — одну подію.

### S-M1-02. Колекція з підтвердженням отримання
`test_s_m1_02_collection_pull_with_ack_then_chain`: Web Collector отримує явний список трьох URL і локальний
пакет правил. Два читання без курсорного підтвердження повертають ті самі `observation_id`; після
підтвердження всі матеріали зберігаються як RAW, товарні сторінки екстрагуються, `/about` не дає товару.

### S-M1-03. M1-завдання через оркестратор
1. Реєстр виконавців оркестратора (`JANE_ORCHESTRATOR_EXECUTORS`): web-collector (`collector`), handler-runtime
   (`handler`), storage (`handler` для `jane.storage-*` і `storage_read`). Підключення `raw-files` і `results-pg`
   задаються через `PUT /v1/connections/{id}` оркестратора і синхронізуються у storage.
2. `POST /v1/sources` (testsite), `POST /v1/tasks` з DAG `collect` → `store-raw` ‖ `extract-products`
   (прив'язка `url_patterns: /product/*`) → `store-products`. Приклад екстрактора SDK опубліковано й
   погоджено в реальному registry; етап посилається на `package_id@version` з дайджестом registry, тож
   runtime завантажує архів із registry й перевіряє дайджест (`package_sources` runtime: `registry`).
3. `POST /v1/tasks/{id}/runs`, далі очікування завершення прогону (`GET /v1/runs/{id}`).
4. Перевірки: `GET /v1/runs/{id}/items` — кожен матеріал пройшов потрібні етапи. `GET /v1/materials/{id}/trace`
   дає ланцюжок матеріал → етап → результат → версія пакета. RAW лежить у files (як у S-M1-01),
   сутності товарів — у PostgreSQL. Категорія та невідома сторінка через `bindings` до екстрактора не
   потрапили, LLM не викликано. Другий технічний запис не створюється.

### S-M1-04. Колектор і екстрактор зі стороннього застосунку
1. `POST /v1/collections` Web Collector з inline-правилами рекурсивного обходу testsite, оркестратор
   не використовується. `GET /v1/collections/{id}/materials` з курсорним підтвердженням повертає саме
   очікуваний рекурсивний набір URL і не завантажує заборонені robots.txt сторінки.
2. Runtime через CLI (`jane-handler-runtime run <пакет> <файл>`) на збереженій сторінці — без інших сервісів.

### S-M1-05. Заміна сховища лише конфігурацією
`test_s_m1_05_storage_swap_is_task_configuration_only`. Два завдання з тим самим колектором і
екстрактором відрізняються лише `handler.package_id` і `connections.target` етапу збереження сутностей:
PostgreSQL (`jane.storage-postgresql` / `results-pg`) і files (`jane.storage-files` / `raw-files`).
Прочитані через API ключі та поля сутностей збігаються.

### S-M1-06. Новий прогін — нове спостереження
`test_s_m1_06_new_observation_is_a_new_record`. Два прогони того самого завдання дають для кожного
матеріалу два різні спостереження RAW і дві події історії сутності. Технічні повтори всередині
кожного прогону не створюють зайвих об'єктів.

## M2 — повний стек

### S-M2-01. Єдиний репозиторій: типи, версії, форки
`tests/e2e/test_m2_registry.py` піднімає реальний registry і перевіряє публікацію пакетів,
архіви та SHA-256, правила Web Collector із registry, виконання екстрактора runtime через
архів registry і завдання оркестратора на незмінній версії форку. Після WP-13t реальний registry
типовий для всіх оркестрованих сценаріїв спільного стеку; цей сценарій має власний стек, бо бере з
registry ще й правила колектора та storage-пакети. LLM-пакет тут лише публікується. Виконання LLM-пакета, дайджести storage-етапів і форки
LLM, storage та правил перевіряє продовження `tests/e2e/test_m2_registry_types.py` (кроки 5–7).

1. Публікація в registry (`POST /v1/packages`, `…/versions`): екстрактор testsite, `jane.storage-files`,
   `jane.storage-postgresql` (`jane-storage-packages publish`), LLM-пакет WP-10, правила колектора
   testsite.
2. Етапи завдання посилаються на `package_id@version` з дайджестом із registry. Runtime завантажує архів
   (`JANE_HANDLER_RUNTIME_REGISTRY_URL`) і перевіряє хеш, прогін дає `success`; неправильний дайджест
   дає 422 `digest_mismatch`.
3. Форк екстрактора → нова версія батька. Дайджест і файли форку не змінилися, `GET …/upstream` показує
   оновлення, `GET …/diff` — відмінності. `POST …/upstream-ports` створює нову версію форку з вмістом
   батька (змінений файл батька є в новій версії форку й відсутній у старій). Етап, зафіксований на
   старій версії форку, і після появи нової виконується старою версією (дайджест у trace).
4. Секрет у пакеті відхиляється (`secret_detected`). Форк storage-пакета зберігає лише
   `required_connections` батька; конкретних підключень у пакеті немає ні в батька, ні у форку.
5. **LLM.** `e2e.llm-page-triage` публікується лише в registry (локальної копії в шлюзі немає,
   `package-host` не запущено). Його тести (`POST /v1/test-runs`) проходять на шлюзі. Завдання
   collect → LLM → `jane.storage-postgresql` з дайджестом registry виконує саме цей архів (`handler` у
   результаті шлюзу й trace) і зберігає `page_triage`; чужий дайджест дає 422 `digest_mismatch`.
   Батьківська 1.1.0 додає шаблон входу, і фейкова модель відповідає на нього інакше. Завдання на 1.0.0
   (батько й форк) відповідають як раніше, завдання на 1.1.0 — по-новому. Форк 1.0.0 незмінний (документ,
   архів байт у байт), `upstream`/`diff` показують шаблон; лише `upstream-ports` дає форк 1.1.0 із
   шаблоном, а завдання на форку 1.0.0 і далі виконує 1.0.0.
6. **Storage.** Етапи `jane.storage-files`/`jane.storage-postgresql` фіксують дайджести registry, storage
   звіряє їх зі своїм пакетом (trace). Повторна публікація 1.0.0 — 409 `version_exists`. Етап із
   дайджестом батьківської 1.1.0 (RAW як JSON) для версії 1.0.0 — `digest_mismatch`, запису немає.
    Зафіксоване завдання після появи 1.1.0 і далі пише `.html`; окремий прогін форку з registry
    перевіряє виконання саме запитаної версії.
   Форк незмінний до `upstream-ports`;
   версії форку, передані як `package_archive`, пишуть `.html` (1.0.0) і JSON (1.1.0); підмінений архів —
    `digest_mismatch`. Етап завдання з форком storage після WP-07c завантажує пакет із registry без
    `package_archive`: item `completed`, run `succeeded`, RAW записано.
7. **Правила колектора.** Джерело зафіксоване на форку `testsite.web-rules` 1.0.0 і збирає
   `/product/phone-alpha` і `/pages/careers`. Після батьківської 1.1.0 (`exclude: */pages/*`) форк і
   збір не змінюються. Джерело на перенесеному форку 1.1.0 збирає лише товар; кожен матеріал несе
   `collector.rules` свого джерела.

**Стан.** Усі сервіси сценарію реальні (**Р**: registry на PostgreSQL + MinIO, runtime, Web Collector,
orchestrator, storage), замінників немає. Крок 1 виконано для всіх чотирьох типів, крок 3 — для форку
екстрактора (маркер батька 1.1.0 у `src/testsite_products/main.py` форку 1.1.0, `diff` з
`parent:1.1.0` — `unchanged`; повторний прогін завдання після появи форку 1.1.0 має в trace дайджест
форку 1.0.0), крок 4 — `secret_detected` для пакета екстрактора й форк `jane.storage-files` з тими самими
`required_connections`. Крок 2 виконано для етапу екстрактора (архів із registry, перевірка
дайджесту, `digest_mismatch`) і правил колектора; storage-етапи `test_m2_registry.py` посилаються на
`jane.storage-*@1.0.0` без дайджесту й виконуються вбудованими адаптерами. Поточну версію сценарію двічі
прогнано окремо на гілці WP-13 (звіт WP-13, «Виправлення після рев'ю інтеграції S-M2-01 і R-04»); у `main`
не злитий. Кроки 5–7 (`test_m2_registry_types.py`, **Р**, LLM — **З**) пройшли **3 Docker e2e поспіль на
  гілці `wp/13g-registry-types`**: 3 passed, 2 xfailed (strict) — тоді ще відкриті форк storage в етапі завдання й
LLM-шлюз, що після кешування виконує іншу версію за чужим дайджестом (звіт WP-13, «Критерій 9: LLM,
storage і форки типів»). Після WP-10d адресний Docker e2e WP-13h підтвердив
  `422 digest_mismatch` на прогрітому кеші LLM; його `xfail` знято. Після WP-07c адресний Docker e2e
  WP-13i підтвердив виконання storage-форку в завданні з registry (`1 passed`), і цей `xfail` знято.
  Не перевірено: архіви решти чотирьох storage-пакетів та повний e2e на спільній ревізії.

### S-M2-02. Telegram
Клієнт Telegram — **З** (записаний бекенд WP-04). Кроки: історія каналу → нові повідомлення →
редагування. Редагування дає нову ревізію (`revision`), а технічна повторна доставка — той самий
`observation_id`. Далі результат зберігається storage (RAW — JSON, ТЗ §5) і проходить через повторну
доставку. Реальний канал використовується лише за наявності тестового доступу; інакше пишемо «не
перевірено на реальному сервісі».

### S-M2-03. Стратегії пошуку матеріалів
`tests/e2e/test_m2_discovery.py` запускає реальні HTTP-колекції Web Collector у Docker Compose:
сім стратегій окремо й три комбінації. Кожна множина канонічних URL має точно збігатися з
`expected_urls.json` після впорядкування query-параметрів; перевіряються `only:*`, відсутність
дублікатів, приватних та зовнішніх URL, `/calendar/` і ненормалізованих редиректів. Для рекурсії
додатково перевіряються лічильники `skipped_robots`, `skipped_out_of_scope` і помилки політики
через HTTP API колектора.

Для кожної стратегії окремо (recursive, sitemap, feeds, categories, search, api, template) запускається
колекція на testsite, а зібрані URL порівнюються з `tests/fixtures/testsite/expected_urls.json`
(`sets.*`). Комбінації (sitemap + recursive, api + recursive, feeds + template) дають об'єднання й
обов'язково містять `only:*`. Перевіряється також: `robots_disallowed` не завантажено, `external_links`
не завантажено, пастка `/calendar/` обмежена, редиректи нормалізовано.

### S-M2-04. Каталог і перевірка цін
Завдання `catalog` (повні картки) і `price-check` (розклад, лише ціна й наявність, `completeness:
partial`). Після каталогу ціну змінено на testsite (або через інший набір сторінок). Перевірка цін
оновлює лише `price` і `availability`, а `title` та інші поля лишаються. Скасування або зміна одного
завдання не впливає на інше.

`tests/e2e/test_m2_prices.py::test_s_m2_04_catalog_and_scheduled_price_check_are_separate_tasks`. Модуль
має власний стек: реальні orchestrator, web-collector, handler-runtime, storage, registry і PostgreSQL
(**Р**); runtime, колектор і оркестратор беруть пакети з registry. Пакети й документи — приклади WP-14 без
змін: правила `examples.testsite-web-rules`, `examples.testsite-catalog-extractor` (`completeness: full`),
`examples.testsite-price-extractor` (`sku`, `price`, `availability`, `completeness: partial`), джерело
`testsite-shop`, завдання `testsite-catalog` і `testsite-price-check`. Пакети публікуються в registry
канонічними архівами, дайджести мають збігтися з `examples/packages.lock.json`, версії погоджуються.
Підключення `raw-files` і `results-pg` беруться з e2e (`tests/e2e/config/storage-connections.json`).

Штатний testsite (WP-01e) має службовий `PUT /_e2e/products/{slug}`: ціна, наявність або назва
одного товару змінюється в пам'яті, обхідник цей шлях не бачить. URL товарів не змінюються, тож
обидва завдання пишуть у ті самі сутності. Оверлей `compose.prices.yaml` більше не використовується.

1. **Каталог.** Ручний запуск `testsite-catalog`: 23 матеріали, 23 RAW у `raw-files`, 16 повних карток
   (`sku`, `title`, `price`, `availability`, `category`, `url` — значення з моделі testsite), `version = 1`,
   в історії кожної — один запис `completeness: full` від екстрактора каталогу.
2. **Скасування каталогу.** `testsite-price-check` створено як у документі: `interval` 3600 с,
   `next_run_at` ≈ створення + 1 год. Другий запуск каталогу скасовано, коли він уже збирав:
   `POST /v1/runs/{id}/cancel` → 202 `cancelling` → `cancelled`. Документ, ETag і `next_run_at` перевірки
   цін не змінилися, її запусків немає, картки ті самі.
3. **Зміна на сайті й розклад.** На сайті змінено: `phone-alpha` — ціну 299→279 і **назву** на
   «Phone Alpha 2027»; `phone-gamma` — ціну й наявність (OutOfStock→InStock); `laptop-four` — ціну;
   `phone-beta`, якого немає в перевірці цін, — ціну. `PUT /v1/tasks/testsite-price-check` з `If-Match`
   змінює лише `schedule.start_at` (зараз + 15 с), документ, ETag і `next_run_at` каталогу ті самі.
   Запуск із `trigger: schedule` має з'явитися не пізніше ніж через 30 с після `start_at` (у прогонах —
   через 0,03–0,88 с). Інших запусків перевірки цін немає, а `next_run_at` після нього дорівнює
   `start_at` + 3600 с.
4. **Часткове оновлення.** Запуск перевірки цін: 4 матеріали, 4 `success`, 4 записи, RAW не додається. Для
   кожного з 4 товарів в історії рівно один запис цього запуску: `completeness: partial`, поля `sku`,
   `price`, `availability` від `examples.testsite-price-extractor`; `applied_fields` містить `price` і
   `availability`, але не `title`, `stale_fields` порожній. У стані нові `price` і `availability`, а
   `title`, `category`, `url` лишилися від каталогу. `phone-alpha` має ціну 279 і назву «Phone Alpha», хоча
   сторінка вже показує нову. У `field_orders` `price` походить зі спостереження перевірки, `title` — з
   іншого. 12 карток поза перевіркою, зокрема `phone-beta`, не змінилися.
5. **Зміна ліміту одного завдання.** `PUT` перевірки цін змінює `crawl.max_pages_per_run` з 20 на 2.
   Ефективний ліміт `collect` перевірки цін — 2 (рівень `task`), каталогу — як і раніше 200 (`task`);
   документ і ETag каталогу ті самі. Ручний запуск перевірки цін читає 2 сторінки й оновлює 2 товари.
   Наступний запуск каталогу читає всі 23 сторінки (+23 RAW) і оновлює повні картки: `phone-alpha`
   отримує нову назву, `phone-beta` — ціну 339, якої перевірка цін не бачила.

Наприкінці перевіряється список запусків. Каталог: `manual` succeeded, `manual` cancelled, `manual`
succeeded. Перевірка цін: `schedule` succeeded, `manual` succeeded. Змінні:
`JANE_E2E_PRICE_CHECK_START_IN_S` (типово 15), `JANE_E2E_SCHEDULE_TOLERANCE_S` (30),
`JANE_E2E_RUN_TIMEOUT_S` (600).

### S-M2-05a. Невідома сторінка: асистент і LLM-шлюз напряму
`tests/e2e/test_m2.py::test_s_m2_05a_unknown_page_goes_to_llm_only_with_flag`. Сторінка
`/pages/event-spring-meetup` testsite має тип `unknown`. Матеріал — **вхід прямого виклику**: тест як
сторонній застосунок формує його з відповіді testsite (`jane_e2e.materials`). Перевіряється політика
прапорця асистента й виклики LLM, а не Web Collector. Матеріал Web Collector тут не взято, бо його URL
`http://testsite:8080/…` збігся б зі скриптом класифікації асистента в `llm-seed.yaml` (S-M2-06). Кроки:

1. `POST /v1/unknown-materials` асистента з `forward_unknown_to_llm: false` дає 403 `access_denied_by_policy`.
   `GET /v1/usage` LLM-шлюзу (`totals.requests`) до й після виклику однаковий.
2. Той самий матеріал із `forward_unknown_to_llm: true` дає 202, job асистента завершується `succeeded`,
   а `totals.requests` шлюзу зростає.

LLM — **З**: вбудований детермінований провайдер `fake` (псевдоніми `cheap`/`strong` задано в
`tests/e2e/config/llm-seed.yaml`). Пошуковий провайдер асистента — **З** (`static`,
`tests/e2e/config/assistant-search.json`). Стан асистента й шлюзу зберігається в PostgreSQL стеку.

### S-M2-05. Невідомі сторінки й LLM
Джерело з `forward_unknown_to_llm: false`, завдання з прив'язками екстракторів, прогін на testsite
(сторінки `unknown`). `GET /v1/usage` шлюзу LLM не показує викликів, `GET /v1/unknown-materials` —
показує матеріали. Після ввімкнення прапорця й повторного прогону виклики є, вони прив'язані до цих
матеріалів, облік витрат ведеться. Сторінка з ін'єкцією обробляється як дані.

`tests/e2e/test_m2_llm_routing.py::test_s_m2_05_unknown_pages_reach_llm_only_after_the_flag_is_enabled`.
Реальні orchestrator, web-collector, handler-runtime, storage, llm (шлюз і LLM-обробник), testsite.
Завдання: `collect` (2 товари й усі 3 сторінки `page_types: unknown`) → `extract-products` (приклад
екстрактора SDK, `bindings: */product/*`, `when` HTML) → `store-products`; окремий етап `unknown-pages`
(LLM-пакет-фікстура `e2e.llm-page-triage`) бере `select: unmatched_materials`. Прапорець задано лише на
джерелі, завдання його успадковує.

1. `POST /v1/task-validations` → `effective_forward_unknown_to_llm: false`. Прогін 1: товари
   екстраговано, етап `unknown-pages` не має жодного елемента, `GET /v1/unknown-materials` оркестратора
   показує рівно 3 невідомі сторінки з `forwarded_to_llm: false`. `GET /v1/usage` шлюзу: 0 запитів у
   scope джерела, загальний лічильник не змінився, `Run.costs.llm` відсутні.
2. `GET` + `PUT /v1/sources/{id}` (`If-Match`) вмикає прапорець; перевірка завдання → `true`.
3. Прогін 2: ті самі 3 матеріали (нові спостереження) мають `forwarded_to_llm: true` і рівно 3 елементи
   етапу `unknown-pages` (`success`). Для кожного `GET /v1/invocations/{id}` LLM-обробника показує вхід
   з цим `material_id`, дайджест пакета, сутність `page_triage` з ключем `material_id` і вартість.
   Trace матеріалу: у прогоні 1 етапів немає (лише реєстрація), у прогоні 2 — `unknown-pages`.
4. Облік: `GET /v1/usage?scope_type=source` — рівно 3 запити, токени й вартість > 0, `purpose: handler`;
   `Run.costs.llm` > 0.

LLM — **З** (провайдер `fake` з ненульовими цінами, скрипти — `tests/e2e/config/llm-seed.yaml`). Архіви
екстрактора й LLM-пакета — з реального registry (WP-13t). Асистент у цьому
маршруті не бере участі: оркестратор передає невідомі матеріали етапу `unmatched_materials`; шлях через
асистента — S-M2-05a. WP-01f додав пряму `/pages/faq-injection`. WP-13n провів її і звичайний FAQ через
цей маршрут ([CI 37002784428](https://github.com/sql-monk/Jane/actions/runs/37002784428)): сторінка з
ін'єкцією проходить як дані (**З**), обидві класифіковані як `faq`, `hijacked` у виході немає. Вплив
ін'єкції цей сценарій виявити не може: сід фейкового провайдера відповідає `faq` на будь-які дані з
`<h1>FAQ</h1>`. Стійкість до ін'єкції — unit WP-10 (`services/llm/tests/test_injection.py`); на реальній
LLM не перевірено.

### S-M2-06. Нове джерело через асистента
`POST /v1/onboarding-sessions` (лише назва testsite; пошуковий провайдер — **З**, LLM — **З** WP-10) →
адаптивна вибірка через реальний колектор → кілька пропозицій з охопленням, вартістю й ризиками →
`candidate-selection` → `acceptance`. Результат: пакет у registry, його тести пройшли в реальному runtime,
створено джерело й завдання в оркестраторі. Прогін завдання дає сутності в storage.

На інтеграційній гілці перевірено два запити: лише назва дала 54 матеріали з основними типами
(`product` 17, `category` 7, `article` 8); підказки з обмеженням на каталог, товари, новини та sitemap
дали 16 матеріалів (`product` 3, `category` 7, `article` 2). Для варіанта з підказками підтверджено
погоджений пакет і 4/4 runtime-тести, виконання завдання та 17 сутностей. LLM і пошук — **З**;
обидва сценарії PASSED у CI 37853683903 (`75 passed in 1486.98s`).

### S-M2-07. Вдосконалення екстрактора
Екстрактор, який не розпізнає частину сторінок (`unrecognized`, наприклад товар без ціни), дає в
оркестраторі групу проблем (`/v1/problem-groups`). Далі `POST /v1/improvement-runs` → нова версія в registry
(походження `llm`), нові й старі тести в runtime, перевірка всіх прив'язок → активація в етапі
(`activations`) → повторна обробка RAW (`/v1/reprocessing`) дає `success` → відкат на попередню версію →
поведінка повертається → аудит (`/v1/audit-events`) містить активацію й відкат. Окремо перевіряється, що
заборона автозмін пакета блокує автоактивацію.

На інтеграційній гілці S-M2-07 пройшов: версія 1.1.0 пройшла 6/6 тестів пакета й 4/4 тестів
на кожній із двох прив'язок; повторна обробка дала `success`, відкат — `unrecognized`, заборона
автозмін — `proposal_only` та 403. LLM — **З**; сценарій PASSED у CI 37853683903 (`75 passed in 1486.98s`).

### S-M2-08. Усі адаптери збереження
`tests/e2e/test_m2_storage.py` послідовно змінює те саме завдання через GET/ETag + PUT для
filesystem, PostgreSQL, SQL Server, MongoDB, MinIO і S3 (SeaweedFS — **З**). Кожний прогін
перевіряє RAW, сутність і історію через `storage.v1`, вміст через нативний інтерфейс сховища,
а повтор того самого виклику обробника — як дублікат без нового ефекту.

Для кожного з filesystem, postgresql, sqlserver, mongodb, minio, s3 (SeaweedFS — **З**) виконується: RAW
testsite і сутності через реальний storage, читання через `storage.v1`, повтор дає дубль, запис видно в
самому сховищі. Заміна адаптера робиться через `PUT /v1/tasks/{id}` (лише `handler.package_id` і
`connections.target`), без зміни образів колектора й екстрактора.

### S-M2-09. Ліміти без зміни коду
`tests/e2e/test_m2_limits.py` встановлює через HTTP ліміт платформи `crawl.max_pages_per_run=1`,
перевіряє походження `platform` і фактичну одну сторінку в колекторі та оркестраторі. Потім змінює
ліміт того самого завдання на 2, перевіряє походження `task` і дві сторінки в наступному прогоні;
початковий документ платформи відновлюється. Темп запитів цей тест не вимірює.

`PUT /v1/limits/platform` (наприклад, `rate.requests_per_second_per_host`, `crawl.max_pages_per_run`) і
ліміти на джерелі або завданні → `GET /v1/limits/effective` показує значення й походження → наступний
прогін дотримується нового ліміту (кількість сторінок, темп). Без перезбирання образів.

### S-M2-10. Адмінка на реальному API
Playwright-сценарії WP-12 проганяються проти стеку: джерела, завдання, пакети, форк з оновленням батька,
редактор, тест без запису, diff, активація й відкат, матеріали й помилки, скасування. Секрети ніде не
відображаються (перевірка DOM і мережевих відповідей).

Після [WP-20/R26](../delivery/WP-20.md#запити-до-інших-власників): **25 повністю / 0 частково / 1 навмисний мок**
із 26; історичний WP-12d — 24/1/1. Рядок №10 повністю підтверджено real `hybrid-assistant-onboarding`:
назва джерела → кандидати й вибір → вибірка → пропозиції з покриттям, вартістю й ризиками → прийняття
з активацією → відновлення після reload; backend — S-M2-06. №18 лишається навмисним мокуванням відповіді
несправного сервісу з секретом. LLM `fake` і пошук `static` — зовнішні замінники (**З**).

Real-набір — **18 сценаріїв**: повний `18 passed (4.6m)`, exit 0 на `3a3251c`; на `df7f252` усі 18
підтверджено сукупно (16 незмінених у повному прогоні, дві змінені специфікації — в адресних контролях).
Це окремий UI-доказ, а не job `web-mock-e2e` у CI. Команди, вивід і відмінності ревізій —
[WP-20](../delivery/WP-20.md#команди-перевірки-та-їхній-вивід); попередні докази M3 —
[журнал потоку B M3](../delivery/M3/stream-b.md).

WP-20 додав 9 `@mock`-сценаріїв №27–35 (`post-m3.spec.ts`): 5 повністю real, 4 частково;
[таблиця WP-20](../delivery/WP-20.md#неперевірені-інтеграції) перелічує межі. Лише на моках: збереження
примітки групи людиною, кнопка повторної обробки прикладів групи, показ `retry_scheduled` / `available_at`,
`observation_ids` і ручні id на сторінці запуску, фільтри `package_id` / `status` запусків вдосконалення.

### S-M2-11. Розгалуження з умовами й LLM-етапом
DAG з `when` (за `material.format.media_type` і `result.status`) і LLM-обробником на проблемних результатах
(**З**: фейковий провайдер). Гілки виконуються лише за умов, результати LLM валідуються схемою й
зберігаються.

`tests/e2e/test_m2_llm_routing.py::test_s_m2_11_conditional_branches_and_llm_on_problem_results`.
Реальні orchestrator, web-collector, handler-runtime, storage, llm, testsite. Вхід: 4 HTML-сторінки
товарів (`phone-alpha`, `phone-beta` — InStock; `phone-gamma` — OutOfStock; `phone-zeta` — PreOrder) і
JSON `/api/v1/products/phone-alpha`. DAG:

```text
collect ─┬─ store-raw-html   when media_type = text/html          → files
         ├─ store-raw-json   when media_type = application/json   → PostgreSQL
         └─ extract-products when media_type = text/html (bindings: */product/*, */api/v1/products/*)
              ├─ store-products   select output,   when result.status = success       → PostgreSQL
              └─ analyze-problems select problems, when result.status = unrecognized  (LLM)
                   └─ store-triage select output,  when result.status = success       → PostgreSQL
```

Екстрактор — пакет-фікстура `e2e.instock-product-extractor`: розпізнає лише пропозиції `InStock`, інші
дають `unrecognized` (`unknown-availability`) з частковою карткою. LLM-пакет — `e2e.llm-page-triage`
(вихід за `output_schema`, сутність `page_triage`). Скрипт фейкового провайдера для `phone-gamma` дає
валідний вихід, для `phone-zeta` — вихід поза схемою.

Перевірки: HTML → files (4 об'єкти `text/html`), JSON → PostgreSQL (1 об'єкт `application/json`);
JSON прив'язано до екстрактора, але `when` за media type його не пропускає; невідомих матеріалів
немає. `store-products` отримав лише `success` (alpha, beta), `analyze-problems` — лише
`unrecognized` (gamma, zeta). LLM для gamma: `success`, сутність `page_triage` записано в PostgreSQL і
прочитано через `storage.v1`; для zeta: `failed/schema_mismatch` з `validation_errors`, `store-triage`
не виконано. Trace gamma: `store-raw-html` → `extract-products` (`unrecognized`, дайджест екстрактора)
→ `analyze-problems` (дайджест LLM-пакета, вихід `page_triage`) → `store-triage` (`results-pg`); trace
JSON — лише `store-raw-json`. Група проблем екстрактора `unknown-availability` має `count: 2`; облік
LLM у scope джерела й `Run.costs.llm` > 0.

LLM — **З**. Архіви пакетів-фікстур `e2e.instock-product-extractor` і `e2e.llm-page-triage` — з реального
registry (WP-13t: опубліковано й погоджено, етапи зафіксовано дайджестами registry).

## Після M3 — повторна обробка збережених RAW

Беклог WP-17 (R06, R01), сценарії WP-21: `tests/e2e/test_reprocessing_stored.py` (маркер `milestone("M3")`).
Історичний CI 37853683903 їх не містить. Обидва сценарії мають явні **PASSED** у
[CI 37905643300, job e2e](https://github.com/sql-monk/Jane/actions/runs/37905643300/job/113740900134)
на `f69854e`: `77 passed in 1435.40s (0:23:55)`, `JANE_E2E_REQUIRED=1`. Локальні прогони WP-21
і тимчасові обходи S-M3-02 збережено в [звіті](../delivery/WP-21.md).

### S-M3-01. Повторна обробка точно вибраних RAW
`test_s_m3_01_reprocessing_takes_exactly_the_given_stored_objects`. Два прогони M1-завдання на двох сторінках
товарів дають по два збережені RAW-спостереження кожного матеріалу. `POST /v1/reprocessing` з
`stored_materials.object_ids` = [RAW товару B з прогону 1, RAW товару A з прогону 2] і `from_stage:
extract-products`: екстраговано рівно ці два спостереження в заданому порядку (`material_ids` взяв би всі
чотири), `store-products` — ті самі два, RAW повторно не записано. Кожен товар має три події історії, і подія
від прогону повторної обробки (`provenance.run_id`) зроблена саме з вибраного спостереження
(`observation.observation_id`). Відсутній `object_id` у списку — прогін `failed` з `error.code: not_found`.

### S-M3-02. Telegram JSON-RAW: відновлення й той самий sha256
`test_s_m3_02_telegram_json_raw_is_restored_and_reprocessed_with_its_sha256`. Реальний Telegram Collector
(записаний бекенд — **З**) збирає два повідомлення (одне не-ASCII). Storage зберігає їх як JSON-документи
Material (типовий формат RAW, що не є вебсторінкою, ТЗ §5): `sha256` об'єкта — це `sha256` документа, а не
повідомлення. `GET /v1/objects/{id}` повертає `material.content` inline з **початковим** вмістом:
текст, `text/plain`, `size_bytes` і `sha256` матеріалу колектора (= `revision.content_sha256`). Далі завдання
джерела `telegram` з етапом `store-original` (`jane.storage-files`, `params.format.raw: original`) і
`POST /v1/reprocessing` з `object_ids` цих JSON-RAW і `from_stage: store-original`: обидва елементи `success`
у заданому порядку, нові об'єкти — `text/plain` з `sha256` і розміром матеріалу колектора, байти збігаються з
текстом повідомлення. До WP-17 відновлений матеріал ніс JSON-документ із медіатипом `text/plain` і чужим
`sha256`.

Під час налагодження S-M3-02 знайдено дефект storage: кожен `PUT /v1/connections/{id}` (також з незмінним
документом, а оркестратор надсилає його після кожного `PUT` у свій реєстр) закриває відкритий адаптер
підключення, і запис, що йде в цю мить, завершується `failed` / `execution_error` «adapter is not open»
з `retryable: false`. Сценарій чекає синхронізації підключень перед прямим записом; дефект описано в
[звіті WP-21](../delivery/WP-21.md) («Запити до інших власників»).

## Надійність

| ID | Як відтворюємо | Що очікуємо |
|---|---|---|
| R-01 | Два воркери оркестратора. Посеред прогону один отримує `docker kill` під час ще активного виклику виконавця, потім рестарт | прогін завершено; кожен ефект один раз (кількість записів у storage = кількості матеріалів); lease перехоплено; повтор виклику отримує 409 `idempotency_in_progress`, обробник виконано один раз; retries не витрачено на kill |
| R-02 | `docker kill` + `up` кожного з 8 сервісів між доставкою й повтором | storage/runtime — дубль і той самий результат; колектори/LLM/registry/assistant/orchestrator — збережені job, матеріали, архіви та облік без повторного ефекту |
| R-03 | `docker network disconnect` виконавця на час прогону, потім `connect` | оркестратор повторює з backoff: `attempt_history` фіксує `retry_scheduled`, `delay_ms` і `available_at`; наступне `claimed.at ≥ available_at`, та сама історія й кількість спроб у trace; наявні межі опитування та ізоляції збережено; після відновлення прогін завершується без дублів |
| R-04 | Той самий `delivery_key` на кожен виконавець (storage, runtime, llm, колектори — `Idempotency-Key`), також поки перший запит ще виконується | дубль без побічного ефекту, `Idempotency-Replayed: true`; інше тіло дає 422 `idempotency_key_reused`; під час роботи: асинхронна операція повертає той самий `202` + `job_id` з `Idempotency-Replayed: true`, синхронний виклик — 409 `idempotency_in_progress` (`retryable`), а після завершення — збережений результат; перша робота завершується, ефект один |
| R-05 | Новіше спостереження (ціна 199), потім старіше (ціна 249) того самого товару | стан лишається 199; старіше отримує `stale`, `price` у `stale_fields`, подія є в історії |
| R-06 | `--scale <сервіс>=2`; запит на екземпляр 1, повтор на екземпляр 2 | runtime — дубль із тим самим `invocation_id`; Web/Telegram Collector — той самий job і матеріали; LLM — той самий completion/job і бюджет; storage — один об'єкт; registry — ті самі пакет, версія й архів; assistant — та сама job/session; orchestrator — та сама job запуску run після takeover (WP-13m, CI 36999629588) |
| R-07 | S-M2-07 з `docker kill` + `start` асистента (окремо — runtime), поки кандидат тестується в runtime, паралельно з прогоном навантаження | цикл завершується або відновлюється без втрати й дублювання версій; відкат працює |
| R-08 | Малий `limits.queue.max_unacked_materials`, повільний споживач | колектор призупиняється, пам'ять не росте, після споживання продовжує |

Реалізовані зараз: `tests/e2e/test_reliability.py` — `test_r_02_…`, `test_r_05_…`, `test_r_06_…` (матеріал
дає реальний Web Collector, `POST /v1/fetches`; так само R-06 storage у `test_r06_storage_registry.py`);
`tests/e2e/test_r04_idempotency.py` — частина R-04/R-06:
`test_r_04_collectors_replay_one_job_without_new_materials[web-collector|telegram-collector]` і
`test_r_04_llm_replay_does_not_spend_usage_twice[sync|async]`, кожен на тому самому та іншому
екземплярі й після рестарту (усі варіанти PASSED у CI 37853683903). Вони надсилають `POST /v1/collections`
і `POST /v1/completions` повторно з тим самим `Idempotency-Key` після завершення першого виклику,
а потім той самий ключ з іншим тілом. Telegram-мережа — записаний backend (**З**), LLM-провайдер —
`fake` (**З**), HTTP-сервіси реальні.

`tests/e2e/test_r04_active_replays.py` — R-04 **під час** незавершеної роботи (інтегровані WP-13r/13s;
усі рядки PASSED у CI 37853683903). Вікно «робота ще йде» визначене спостережуваним станом:

- Telegram Collector: темп `limits.rate.min_delay_ms_per_host = 1000` на 6 записаних каналах; повтор, коли
  колекція `running` і `1 ≤ fetched < 6`;
- handler-runtime (sync/async) і orchestrator (старт run, `/v1/reprocessing`): фікстура
  `e2e.slow-product-extractor` (`delay_seconds = 12`), активна пісочниця видна за Docker-мітками;
- storage, LLM `/v1/invocations` (sync/async), assistant `/v1/unknown-materials`: вміст матеріалу — blob, чий
  `download_url` веде на «шлюз» стенду `package-host` (**З** blob-сховища): сервіс у роботі, поки шлюз тримає
  завантаження, а лічильник шлюзу показує, скільки разів вміст читали;
- registry: `docker pause` MinIO, де registry зберігає архіви: job `upstream-ports` і публікація версії не
  можуть завершитися до `unpause`.

Очікування за контрактом: асинхронна операція вже відповіла, тож повтор отримує той самий `202` + `job_id`
з `Idempotency-Replayed: true`, поки job `running`; синхронний виклик у польоті — 409
`idempotency_in_progress` (`retryable: true`), після завершення — збережений результат (`duplicate: true`);
інше тіло з тим самим ключем — 422 `idempotency_key_reused` і під час роботи. Ефекти перевірено один раз:
матеріали колекції, RAW-об'єкт, пісочниці runtime, `/v1/usage` LLM, версії registry, запуски завдання.

WP-13s додав у той самий модуль LLM `/v1/completions` і job асистента:

- LLM `POST /v1/completions` sync і async: власні підключення й провайдер `fake` прогону з `params.delay_ms`
  (затримка фейкового провайдера, WP-10; межа — `fake.max_delay_ms`); повтор надсилається, коли шлюз
  зажурналював `fake provider holds its answer` з `connection_id` прогону. Sync — 409
  `idempotency_in_progress` (`retryable`), 422 для іншого тіла, потім збережений результат; async — той самий
  `202` + `job_id`, `Idempotency-Replayed`, job `running`; `/v1/usage` завдання — 0 під час утримання, 1 після й
  без змін після повтору; утримано рівно один виклик провайдера;
- assistant: job onboarding (точне посилання на тестовий сайт → вибірка) і improvement (S-M2-07) на власному
  стеку з реальним registry; на час повторів псевдоніми `cheap`/`strong` указують на копію провайдера
  `e2e-assistant` з тими самими скриптами й `delay_ms`. Повтор — той самий `202` + job (і session), 422 для
  іншого тіла, job `running`, облік LLM без змін; потім job `succeeded` (`proposals_ready` / `new_version`
  1.1.0), витрата LLM дорівнює власному обліку job (`costs`), версія опублікована один раз.

`tests/e2e/test_reliability_orchestrated.py` — R-01, R-03, R-08 на завданнях оркестратора (реальні
orchestrator, web-collector, handler-runtime, storage, registry; архіви пакетів — з реального registry
після WP-13t). R-01: дві репліки на одній БД; репліка 1 тримає lease виклику
повільного екстрактора-фікстури `e2e.slow-product-extractor` (виклик довший за lease), отримує
`docker kill`, далі `docker start`. Репліка 2 перехоплює прострочений lease, поки осиротілий виклик
ще виконується; повтор із тим самим `delivery_key` отримує від runtime 409 `idempotency_in_progress`
(лічильник `jane_http_requests_total` і access log runtime), потім результат того самого виклику:
одна пісочниця, `attempts = 1` в усіх item, ефекти в storage один раз. R-03: storage від'єднано від
мережі після збереження RAW, поки повільна екстракція ще стримує `store-products`; цей item —
єдиний незавершений, тож інші item не займають воркер чи слот етапу. Опитування API кожні ~0,1 с дає нижню й верхню
межі кожного очікування: після спроби 1 (3000 мс) і спроби 2 (6000 мс) item не взято раніше за
затримку (допуск 250 мс на транзакцію повтору) й утримано не менше половини затримки, поки жоден
item прогону не виконувався. Причинність backoff доводить історія спроб item (WP-17, R25: `attempt_history`
і `available_at` у `/v1/runs/{id}/items` та trace матеріалу; годинник бази даних, WP-21): історія повна
(менша за `engine.attempt_history_max`), `claimed` 1 → `retry_scheduled` 1 (`delay_ms` = 3000, код
`upstream_unavailable`, `available_at − at` = затримка) → `claimed` 2 → `retry_scheduled` 2 (6000) →
`claimed` 3 … `completed`, без `lease_reclaimed`. Кожне взяття — не раніше за `available_at` попередньої
затримки (запит claim вимагає `available_at <= now()`) і не пізніше за половину затримки після неї; записане
очікування `claimed.at − retry_scheduled.at` лежить у межах опитування (± 250 мс на commit). `available_at`,
який опитування бачило на item у стані `retrying`, — той самий, що в історії, а trace матеріалу віддає той
самий `item_id`, `attempts` і `attempt_history`. R-08:
`queue.max_unacked_materials = 2` рівня завдання — колектор призупиняється, не перевищує межу
(і напряму, без оркестратора) й завершує збір з `unacked = 0`, `acknowledged = 8`.

`tests/e2e/test_r07_improvement_restarts.py` — R-07. Власний стек
S-M2-06/07 (реальний registry скрізь; LLM-провайдер `fake` — **З**). Кожен із двох сценаріїв заново
готує S-M2-07 (екстрактор 1.0.0, дві прив'язки, група проблем) і запускає прогін навантаження: інше
завдання, 19 сторінок товарів, по одному виклику за раз, пакет-фікстура `e2e.slow-product-extractor`
(власний id у registry, `delay_seconds = 5`). Потім стартує вдосконалення. Збій вноситься, коли runtime
показує `running` для свіжого test-run job кандидата 1.1.0, LLM уже відповів, у registry лише 1.0.0.
Активна пісочниця кандидата в мить kill не підтверджена.

- **`assistant`**: `docker kill` + `docker start` асистента.
- **`runtime`**: `docker kill` handler-runtime, коли test-run job кандидата свіжий і `running`, а в
  пісочниці є виклик навантаження; runtime лежить, доки job асистента не завершиться, потім
  `docker start`.

Далі вдосконалення запускається повторно з новим `Idempotency-Key`. Перевіряється:

- у registry рівно `[1.0.0, 1.1.0]`; 1.0.0 не змінився (дайджест опублікованого = дайджест архіву);
- у 1.1.0 `based_on` = 1.0.0, а `assistant_job_id` — повторного job; кожен звіт тестів асистента
  записано один раз;
- на кожну прив'язку рівно одна `auto_activate`; група проблем `resolved` повторним job; LLM
  `improvement` +2 (по одному на job);
- за фактичним виконанням (прогони завдань, `HandlerResult.handler` від runtime на кожен виклик,
  сутності) завдання виконує 1.1.0. Після відкату — 1.0.0, а друга прив'язка лишається на 1.1.0.
  В аудиті одна `stage.auto_activate` і одна `stage.rollback`;
- прогін навантаження `succeeded`, кожен RAW і кожна розпізнана сутність записані один раз.

Після WP-11e/06a/09c перерваний job асистента завершується `failed` після lease, test-run runtime стає
термінальним, обірваний виклик навантаження завершується після рестарту. Три відповідні регресійні
тести та два цикли вдосконалення — **5 PASSED** у CI 37853683903, без xfail.
Деталі — [WP-13](../delivery/WP-13.md), розділ «R-07: вдосконалення з рестартами».
