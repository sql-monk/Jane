# Сценарії приймання (e2e)

Сценарії для віх M1 і M2 (plan.md §6) і сценарії надійності WP-13. Який сценарій закриває який
критерій ТЗ §12, показано в [matrix.md](matrix.md). Код лежить у [`tests/e2e/`](../../tests/e2e).

## Принципи

1. **Лише реальні компоненти Jane.** Сервіс, який приймаємо, ніколи не мокається. Сценарій іде через
   публічні API за контрактами. Кожен запит і кожна відповідь перевіряються схемою з `contracts/openapi`
   (`jane_kit.contracts.ContractClient`), тож розбіжність із контрактом валить сценарій.
2. **Замінники зовнішніх систем позначаються явно:** фейковий провайдер LLM (WP-10), записаний або фейковий
   клієнт Telegram (WP-04), статичний пошуковий провайдер (WP-11), SeaweedFS замість AWS S3 (WP-01).
   У матриці вони мають позначку **З**.
3. **Тимчасові замінники компонентів** мають позначку **Т**. У M1 використано лише `package-host`:
   він віддає архів локального пакета runtime через HTTP у сценаріях з оркестратором. Це перевірка
   виконання локального пакета, а не перевірка реального registry; для M2 потрібен окремий сценарій із registry.
4. **Незалежність від стану.** Кожен прогін має свій `run_id`, від якого залежать `source_id` (а отже
   `key.scope` сутностей), `observation_id` і `delivery_key`. Тому сценарії можна повторювати на тому самому
   стеку. Сховище перевіряється через `storage.v1`: список об'єктів, метадані й вміст. У S-M1-01
   RAW-файл додатково читається прямо з тому; таблиці PostgreSQL ці сценарії прямо не читають.
5. **Сервіс, якого немає в `main`**, дає `skip` з причиною («WP-NN ще не злито в main»), а не падіння.

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

Змінні: `JANE_E2E_PROJECT`, `JANE_E2E_KEEP`, `JANE_E2E_WAIT_TIMEOUT` (типово 900 с),
`JANE_E2E_SANDBOX_WALL_TIME_MS` (типово 60000; ліміт запиту до пісочниці), `JANE_E2E_DOCKER_SOCKET`,
`JANE_E2E_DOCKER_GID`, `JANE_E2E_SANDBOX_IMAGE`.

## Стан сценаріїв

| ID | Назва | Критерії | Сервіси | Стан |
|---|---|---|---|---|
| S-M1-01 | Web Collector → RAW у files ‖ екстракція локальним пакетом → PostgreSQL | 1, 2, 8, 12 | testsite, web-collector, storage, handler-runtime, postgres | **пройдено на гілці WP-13** |
| S-M1-02 | Колекція з курсорним підтвердженням і повторною доставкою → RAW та екстракція | 1, 2, 12 | web-collector, storage, handler-runtime | **пройдено на гілці WP-13** |
| S-M1-03 | M1-завдання через оркестратор: RAW, екстракція, trace, unknown | 2, 8, 11, 12 | + orchestrator, локальний `package-host` (Т) | **пройдено на гілці WP-13** |
| S-M1-04 | Рекурсивний збір зі стороннього застосунку, runtime через CLI | 1, 10 | web-collector, handler-runtime | **пройдено на гілці WP-13** |
| S-M1-05 | Заміна сховища лише конфігурацією завдання (PostgreSQL ↔ files) | 3 | orchestrator, storage, handler-runtime | **пройдено на гілці WP-13** |
| S-M1-06 | Новий прогін дає нове спостереження й подію історії | 8 | orchestrator, storage, handler-runtime | **пройдено на гілці WP-13** |
| S-M2-01 | Репозиторій: пакети всіх типів, версії, форк, оновлення батька | 7, 9 | registry, runtime, storage, llm, orchestrator | ще не реалізовано в WP-13 |
| S-M2-02 | Telegram: історія, нові, редагування як ревізії → збереження | 1, 8, 12 | telegram-collector, storage | **1 passed на спільній гілці WP-01a/00a/13** (Telegram — З) |
| S-M2-03 | Стратегії пошуку окремо й у комбінаціях проти `expected_urls.json` | 10 | web-collector (+WP-03), testsite | **10 Docker e2e пройшли на гілці WP-13** (`test_m2_discovery.py`) |
| S-M2-04 | Каталог і перевірка цін — окремі завдання | 5 | orchestrator, web-collector, runtime, storage | ще не реалізовано в WP-13 |
| S-M2-05a | Невідома сторінка: асистент викликає LLM лише з прапорцем (без оркестратора) | 11 | testsite, assistant, llm, postgres | **реалізовано, проходить** (LLM — З) |
| S-M2-05 | Невідомі сторінки в завданні: LLM лише з прапорцем | 11 | orchestrator, web-collector, runtime, storage, llm | **пройдено на гілці `wp/13-llm-routing`** (`test_m2_llm_routing.py`; LLM — З, архіви пакетів — `package-host` Т); сторінки з ін'єкцією на testsite немає |
| S-M2-06 | Нове джерело через асистента → варіанти → пакет → тести → активація | 4 | assistant, llm, registry, web-collector, runtime, orchestrator | ще не реалізовано в WP-13 |
| S-M2-07 | Проблемні приклади → нова версія → тести → активація → відкат | 6 | orchestrator, assistant, llm, registry, runtime | ще не реалізовано в WP-13 |
| S-M2-08 | Усі 6 адаптерів: RAW + сутності; заміна в конфігурації завдання | 3, 12 | storage (+WP-08), orchestrator, усі сховища | **1 Docker e2e пройшов на гілці WP-13**; незалежний повтор пройшов |
| S-M2-09 | Зміна лімітів без зміни коду | 13 | orchestrator, виконавці | **1 Docker e2e пройшов на гілці WP-13** (кількість сторінок); темп ще не виміряно |
| S-M2-10 | Адмінка на реальному API (Playwright) | 6, 7 (UI) | admin, усі API | WP-12 частково перевірив реальні API; повний Caddy прогін відкритий |
| S-M2-11 | Ланцюжок з умовами `when` і LLM-етапом | 2 | orchestrator, web-collector, runtime, storage, llm | **пройдено на гілці `wp/13-llm-routing`** (`test_m2_llm_routing.py`; LLM — З, архіви пакетів — `package-host` Т) |
| R-01 | Kill воркера оркестратора посеред ланцюжка | 8 | orchestrator ×2, виконавці | чекає WP-09 |
| R-02 | Kill і рестарт кожного сервісу; повтор після рестарту — дубль | 8 | storage, handler-runtime (далі — усі) | **реалізовано для storage і runtime, проходить** |
| R-03 | Розрив мережі між оркестратором і виконавцем | 8 | orchestrator, виконавці | чекає WP-09 |
| R-04 | Повторна доставка на кожен виконавець | 8 | усі виконавці | storage, runtime — у S-M1-01 і R-02; інші — з WP |
| R-05 | Запізнілий результат не замінює новішого | 8 | storage, handler-runtime | **реалізовано, проходить** |
| R-06 | Кілька екземплярів кожного компонента | 8 | усі | **runtime ×2 реалізовано, проходить**; інші — з WP |
| R-07 | Повний цикл LLM → тести → активація → відкат під навантаженням і з рестартами | 6, 8 | orchestrator, assistant, llm, registry, runtime, storage | чекає WP-09, 05 |
| R-08 | Обмежена черга стримує збір (backpressure) | 8, 13 | orchestrator, web-collector | чекає WP-09, 02 |

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
   (прив'язка `url_patterns: /product/*`) → `store-products`. Версію й дайджест локального екстрактора
   зафіксовано; його архів runtime отримує з тестового `package-host` (**Т**).
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
1. Публікація в registry (`POST /v1/packages`, `…/versions`): екстрактор testsite, `jane.storage-files`,
   `jane.storage-postgresql` (`jane-storage-packages publish`), LLM-пакет WP-10, правила колектора
   testsite.
2. Етапи завдання посилаються на `package_id@version` з дайджестом із registry. Runtime завантажує архів
   (`JANE_HANDLER_RUNTIME_REGISTRY_URL`) і перевіряє хеш, прогін дає `success`.
3. Форк екстрактора → нова версія батька. Дайджест і файли форку не змінилися, `GET …/upstream` показує
   оновлення, `GET …/diff` — відмінності. `POST …/upstream-ports` створює нову версію форку. Етап на
   форку до активації працює тим самим кодом.
4. Секрет у пакеті відхиляється (`secret_detected`), а форк не копіює підключень.

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

### S-M2-05a. Невідома сторінка: асистент і LLM-шлюз напряму
`tests/e2e/test_m2.py::test_s_m2_05a_unknown_page_goes_to_llm_only_with_flag`. Сторінка
`/pages/event-spring-meetup` testsite має тип `unknown`, матеріал формує замінник колектора (**Т**). Кроки:

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
матеріалів, облік витрат ведеться. Вміст сторінки з ін'єкцією не змінює поведінки.

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

LLM — **З** (провайдер `fake` з ненульовими цінами, скрипти — `tests/e2e/config/llm-seed.yaml`). Архів
LLM-пакета — через `package-host` (**Т**). Асистент у цьому маршруті не бере участі: оркестратор
передає невідомі матеріали етапу `unmatched_materials`; шлях через асистента — S-M2-05a.
**Сторінки з ін'єкцією testsite не має** (див. `tests/fixtures/testsite/README.md`), тож цю частину
e2e не перевіряє; доказ поки що — `services/llm/tests/test_injection.py` (WP-10), запит — у звіті WP-13.

### S-M2-06. Нове джерело через асистента
`POST /v1/onboarding-sessions` (лише назва testsite; пошуковий провайдер — **З**, LLM — **З** WP-10) →
адаптивна вибірка через реальний колектор → кілька пропозицій з охопленням, вартістю й ризиками →
`candidate-selection` → `acceptance`. Результат: пакет у registry, його тести пройшли в реальному runtime,
створено джерело й завдання в оркестраторі. Прогін завдання дає сутності в storage.

### S-M2-07. Вдосконалення екстрактора
Екстрактор, який не розпізнає частину сторінок (`unrecognized`, наприклад товар без ціни), дає в
оркестраторі групу проблем (`/v1/problem-groups`). Далі `POST /v1/improvement-runs` → нова версія в registry
(походження `llm`), нові й старі тести в runtime, перевірка всіх прив'язок → активація в етапі
(`activations`) → повторна обробка RAW (`/v1/reprocessing`) дає `success` → відкат на попередню версію →
поведінка повертається → аудит (`/v1/audit-events`) містить активацію й відкат. Окремо перевіряється, що
заборона автозмін пакета блокує автоактивацію.

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

LLM — **З**, архіви пакетів-фікстур — `package-host` (**Т**; реальний registry тут не перевіряється).

## Надійність

| ID | Як відтворюємо | Що очікуємо |
|---|---|---|
| R-01 | Два воркери оркестратора. Посеред прогону один отримує `docker kill`, потім рестарт | прогін завершено; кожен ефект один раз (кількість записів у storage = кількості матеріалів); lease перехоплено; retries не витрачено на kill |
| R-02 | `docker kill` + `up` кожного сервісу між доставкою й повтором (зараз — storage і handler-runtime) | повтор з тим самим `delivery_key` дає `duplicate: true`; runtime повертає той самий `invocation_id` (стан у PostgreSQL) |
| R-03 | `docker network disconnect` виконавця на час прогону, потім `connect` | оркестратор повторює з backoff, після відновлення прогін завершується без дублів |
| R-04 | Той самий `delivery_key` на кожен виконавець (storage, runtime, llm, колектори — `Idempotency-Key`) | дубль без побічного ефекту, `Idempotency-Replayed: true`; інше тіло дає 422 `idempotency_key_reused` |
| R-05 | Новіше спостереження (ціна 199), потім старіше (ціна 249) того самого товару | стан лишається 199; старіше отримує `stale`, `price` у `stale_fields`, подія є в історії |
| R-06 | `--scale <сервіс>=2` (зараз — handler-runtime); запит на екземпляр 1, повтор на екземпляр 2 | повтор — дубль із тим самим `invocation_id`; результат читається з іншого екземпляра; далі так само для колекторів (спільний стан), registry, llm (спільний бюджет), assistant, orchestrator (воркери не дублюють) |
| R-07 | S-M2-07 з рестартом асистента й runtime посередині | цикл завершується або відновлюється без втрати й дублювання версій; відкат працює |
| R-08 | Малий `limits.queue.max_unacked_materials`, повільний споживач | колектор призупиняється, пам'ять не росте, після споживання продовжує |

Реалізовані зараз: `tests/e2e/test_reliability.py` — `test_r_02_…`, `test_r_05_…`, `test_r_06_…`.
