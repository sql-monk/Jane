# Сутності в MongoDB — план

Статус: у роботі (2026-10-12). Координатор — основна сесія; виконавці — субагенти за потоками нижче.

## Рішення

1. **Де лежать дані.** Схему задає код сервісу (міграції, наперед відомі таблиці, зв'язки) → PostgreSQL. Схему задає пакет (поля описує екстрактор і змінює з новою версією пакета) → MongoDB. Байти (RAW, медіа) → files / MinIO / S3. Оформлюється як ADR.
2. **Наявні дані не переносимо.** База `jane_storage_results` у `jane-demo` лишається як є; нові дані збираються вже в MongoDB.
3. **Колекція на тип сутності.** Адаптер MongoDB кладе кожен `entity_type` в окрему колекцію, історію — поруч. Службові колекції (доставки, об'єкти) — окремо й не перетинаються з іменами типів.
4. **Категорії товарів — окремі типи.** Тип товару — нормалізована група `product_<група>`, оголошення — `ad_<група>` (таксономія нижче). Новини й дописи (`article`, `news_article`, `post`, `news_event`) типів не змінюють.
5. **Категорію визначає екстрактор, а не сховище.** `entity_type` входить в ідентичність сутності, за ним читає Storage API, а часткові оновлення (перевірка цін) не несуть категорії. Тому тип обирає екстрактор: за таблицею «префікс `category_path` → тип» у пакеті сайту або фіксованим параметром етапу, якщо завдання охоплює одну категорію. Контракти не змінюються: `entity_type` уже довільний рядок `^[a-z][a-z0-9_]{0,63}$`, а пакет декларує типи в `output.entities`.
6. **Невизначена категорія** → `product_other` / `ad_other`. Екстрактор цін, що не може визначити той самий тип, що й екстрактор картки, не пише сутність (статус `unrecognized`), а не створює її в чужій колекції.
7. **Тестовий магазин** (`examples/packages`, приймальний сценарій ТЗ §12) лишається з типом `product`; змінюється лише сховище.

### Імена колекцій MongoDB

База — `params.database` (для `results-mongo` — `jane_results`), префікс `params.prefix` — типово порожній.

| Колекція | Вміст |
|---|---|
| `<prefix><entity_type>` | актуальний стан, напр. `product_book` |
| `<prefix><entity_type>.history` | історія версій типу |
| `<prefix>_deliveries` | ключі доставки (зберігаються назавжди, ADR-0008) |
| `<prefix>_objects`, `<prefix>_object_chunks` | RAW / документи результатів, якщо їх пишуть у Mongo |

`entity_type` не може починатися з `_` і не містить крапки, тож службові й історичні колекції не перетинаються з колекціями типів.

## Таксономія типів

| Тип | Що входить | Джерела зараз |
|---|---|---|
| `product_food` | продукти, напої, алкоголь | varus, epicentrk, prostor |
| `product_beauty` | косметика, парфуми, гігієна й догляд | prostor, varus, epicentrk |
| `product_household` | побутова хімія | varus, epicentrk, prostor |
| `product_book` | книжки | yakaboo |
| `product_kids` | іграшки, дитячий транспорт, дитячі товари | bi-ua, epicentrk, varus |
| `product_electronics` | електроніка, ноутбуки | shops (5 магазинів), epicentrk |
| `product_appliance` | побутова техніка | epicentrk |
| `product_tools` | інструменти, будівництво й ремонт, сантехніка, освітлення, підлога | epicentrk |
| `product_garden` | сад і город | epicentrk |
| `product_home` | дім, інтер'єр, меблі, товари для дому | epicentrk, varus, prostor |
| `product_clothing` | одяг, взуття, аксесуари, галантерея | epicentrk, prostor |
| `product_auto` | автотовари | epicentrk |
| `product_pet` | зоотовари | epicentrk, varus |
| `product_sport` | спорт і туризм | epicentrk |
| `product_office` | канцтовари, шкільне | epicentrk, yakaboo |
| `product_health` | медичні товари | epicentrk, prostor |
| `product_other` | сезонні розділи, «Несортовані», решта | — |
| `ad_car` | авто | autoria, rst, avtobazar, classified-auto-ria |
| `ad_realty` | нерухомість | domria, classified-dim-ria |
| `ad_goods` | речі: електроніка, дім, одяг | bon, olx, shafa, ria |
| `ad_other` | решта оголошень | — |

Таблиця переходить у `docs/reference/entity-types.md`; відповідність розділів сайту типам — у пакеті кожного сайту.

## Потоки робіт

| Потік | Шляхи | Зміст |
|---|---|---|
| A. Адаптер MongoDB | `services/storage/adapters/mongodb/**`, розділ mongodb у `docs/components/storage/adapters.md`, `docs/components/storage/reference/types/jane_storage_mongodb.md` | колекція на тип; `EntityDiscoveryAdapter` (каталог, пошук), `StorageStatisticsAdapter`; індекси; нова мажорна версія пакета `jane.storage-mongodb` |
| B. Стек і підключення | `deploy/profiles/**`, `infra/**`, `scripts/dev.py` | MongoDB у профілі стеку; зв'язування зі Storage; підключення `results-mongo` в `infra/config/storage-connections.json` |
| C1. Магазини | `examples/shops/**` | екстрактори пишуть `product_electronics` (параметр етапу); збереження → `jane.storage-mongodb` / `results-mongo` |
| C2a. Каталоги сайтів | `examples/sites/packages/catalog.*`, `examples/sites/sites/{bi,epicentrk,prostor,varus,yakaboo}.json`, скрипти `examples/sites/*.py`, `examples/sites/README.md` | таблиці категорій → `product_*` в екстракторах карток і цін; збереження → Mongo |
| C2b. Оголошення, авто, новини сайтів | решта `examples/sites/packages/**` і `examples/sites/sites/*.json` | `ad_*`; новини й Telegram — лише збереження → Mongo |
| C3. Classifieds і automarket | `examples/classifieds/**`, `examples/automarket/**` | `ad_*`; збереження → Mongo |
| C4. Базові приклади | `examples/packages/**`, `examples/documents/**`, `examples/news/**`, `examples/channels/**`, `examples/jane_examples.py`, `examples/packages.lock.json`, `examples/tests/**`, `examples/README.md` | підключення `results-mongo`; збереження → Mongo; типи не змінюються |
| D. Документація | `docs/**` (крім розділів потоку A), `README.md` | ADR, `data-ownership.md`, `docs/reference/entity-types.md`, getting-started, backup-restore, діаграми |
| E. Живий запуск | стек `jane-demo` | MongoDB у стеку, публікація пакетів, по одному завданню з кожної групи, перевірка колекцій і сторінок «Результати» / «Сховища» |

Записи минулих запусків (`deployed/`, `verification*.json`, `catalogs/*.json*`) не змінюються.

## Тести

- A — тести адаптера, зокрема на реальному MongoDB, один раз наприкінці потоку.
- C — тести змінених пакетів і `examples/tests` один раз наприкінці кожного потоку.
- Після всіх потоків — один `just check` і живий запуск E.
- Наявні e2e на PostgreSQL лишаються: адаптер PostgreSQL підтримується далі.

## Порядок

1. Хвиля 1 (паралельно): A, B.
2. Хвиля 2 (паралельно, після погодження таксономії): C1, C2a, C2b, C3, C4.
3. Хвиля 3: D, `just check`, E (E змінює `jane-demo` — після підтвердження).

## Хід виконання

- **B — готово.** `infra/compose.yaml`: Storage залежить від `mongodb` і отримує `JANE_SECRET_DEV_MONGO_USER/PASSWORD`; `results-mongo` в `infra/config/storage-connections.json`; `deploy/profiles/stack.py` піднімає MongoDB разом зі Storage й записує її адресу у файл стеку. Тести: `infra/tests` 19 passed, `deploy/profiles/tests/test_profiles_harness.py` 69 passed.
- **A — готово.** `jane.storage-mongodb` 2.0.0 (`sha256:2307eeb9e72b59a234f812a9f8dc716b05a9ac4643e843a520dac2ba3d8faad3`): колекція на тип, історія в `<тип>.history`, ключі доставки через запис наміру в `_deliveries` (без сканування колекцій типів), ліниві індекси, каталог/пошук/статистика (`size_basis: mongodb_collections_with_indexes`). Тести адаптера на реальному MongoDB 8.0: 34 passed. Супутньо: опис `size_basis` у `storage.v1.yaml`, мітка в `StoragesPage.tsx`, `tests/e2e/test_m2_storage.py` під нову розкладку. Потоки C посилаються на `jane.storage-mongodb@2.0.0`.
- **C4 — готово.** Базові приклади (`examples/documents`, `jane_examples.py`, news, channels) пишуть сутності в `results-mongo` через `jane.storage-mongodb@2.0.0`; `packages.lock.json` перегенеровано (`jane.storage-postgresql` прибрано). `jane_examples.py check` — ok, тести прикладів — 36 passed, `setup_news.py check` — 18 пакетів, 12 джерел/завдань. Супутньо: `results-mongo` в `tests/e2e/config/storage-connections.json`, `tests/e2e/test_m2_prices.py` → `results-mongo`. `examples/news/config.lock.json` і `VERIFICATION.md` — записи розгорнутого стану на PostgreSQL, не змінювались.
- **C1 — готово.** `shops.jsonld-offers` і `shops.product-cards` 2.0.0: тип з обов'язкового параметра етапу `entity_type` (усі 17 `product_*`, без типового значення); завдання ноутбуків — `product_electronics`; збереження → `results-mongo`; `setup_shops.py` замінює наявні джерела й завдання через `PUT` з `If-Match`. `test_shops.py` — 12 passed; тести пакетів — 4 і 3 passed. Супутньо: назви нових типів в Admin UI (`web/admin/src/lib/results-context.ts`).
- **C2b — готово.** `ads.bon-ads` 2.0.0 (таблиця розділів верхнього рівня → `ad_*`, картка й сторінка категорії беруть розділ із хлібних крихт; без розділу — `unrecognized`), `ads.domria-listing` 2.0.0 (фіксовано `ad_realty`); bon, domria, 8 news і 8 tg описів сайтів пишуть у `results-mongo`. Тести пакетів проходять.
- **D — готово.** [ADR-0011](../adr/0011-data-placement.md), [типи сутностей](../reference/entity-types.md), `data-ownership.md`, документація Storage (каталог/пошук/статистика в MongoDB), user-guide, getting-started (інструкції на `results-mongo`; вивід — із запуску 2026-10-11 на PostgreSQL, позначено), резервування MongoDB у `backup-restore.md`, діаграми (`data-ownership`, `task-dataflow`, `dev-stack`, `operations/data-ownership`) з перегенерованими PNG. `docs_check.py README.md docs` — 598 файлів, 0 помилок; `docs_diagrams.py check` — 54 ok.
- **C3 — готово.** `car_ad` → `ad_car`; classifieds: olx, ria, shafa → `ad_goods`, dim-ria → `ad_realty`, auto-ria → `ad_car` (фіксовано в пакетах); екстрактори 2.0.0. Дублікати `autos.*` усунено: єдине джерело — `examples/sites/packages` (каталог `examples/automarket/packages` видалено, `setup_automarket.py` бере пакети звідти). `queue_workers.py` змін не потребує. Тести: 99 passed.
- **Регресія в `main` до цієї роботи:** коміт `96a57191` повернув 9 пакетів каталогів і 5 описів сайтів з 1.1.1 (повний асортимент, працює в `jane-demo`) до 1.0.0. C2a перебудовує 2.0.0 на основі 1.1.1.
- **C2a — готово.** 9 пакетів і 5 описів сайтів каталогів відновлено з `96a57191^` (1.1.1, повний асортимент), зміни 2.0.0 застосовано поверх: таблиці `CATEGORY_TYPES` (однакові в картці й цінах), `unrecognized` для розділів поза таблицею, категорії в короткому запиті VARUS. Пакети 2.0.0: `catalog.{bi-products, epicentrk-products, epicentrk-prices, prostor-product-extractor, prostor-price-extractor, varus-product-extractor, varus-price-extractor, varus-prices-rules, yakaboo-book-extractor, yakaboo-price-extractor}`; `catalog.*-catalog-rules` лишаються 1.1.1. `setup_sites.py`, `catalog_status.py`, `export_sites.py`, `verify_prices.py` працюють з `results-mongo` і `product_*`. `test_sites.py` + `test_price_observations.py` — 37 passed. Відомо: у bi-ua таблиця має лише 5 розділів, що траплялися в даних; решта повного асортименту bi піде в `product_other`, доки таблицю не розширять.
- **Наскрізна перевірка на MongoDB.** `jane_examples.py demo` на чистому ізольованому стеку: `ok: true`, 23 RAW, 16 товарів у колекції `product`, 20 версій у `product.history`, 4 часткові оновлення цін (версія 2); каталог типів, пошук і статистика (`size_basis: mongodb_collections_with_indexes`) повертають дані. Вивід — у [наскрізному сценарії](../getting-started/end-to-end.md). Тимчасові стеки прибрано (`leftovers: {}`).
- **`just check` (2026-10-12):** lint ok, contract ok, web ok (136 тестів); unit — 1346 passed, 1 failed: `libs/jane-kit/tests/test_operations.py::test_durable_telemetry_and_unknown_metrics` залежить від часу й проходить при повторному запуску (`libs/` не змінювались); types — 1 помилка mypy у `examples/sites/packages/news.analysis-entities` (`.normalize`), пакет не змінювався, помилка є від коміту `96a57191`.
- **E — `jane-demo` (2026-10-12, за погодженням власника стенду).**
  - MongoDB: контейнер `jane-demo-mongodb-1` (`mongo:8.0`, том `jane-demo_mongodb-data`, аліас `mongodb` у `jane-demo_default`, порт `127.0.0.1:56585`), маніфест `.jane/operations-deploy/jane-demo/mongodb.private.json`; `services.mongodb` дописано у файл стеку (копія до зміни — `.jane/stack-jane-demo.before-mongo-*.json`).
  - Storage: образ `jane-demo-operations-storage:mongo-2.0.0` — живий образ `jane-demo-storage:admin-e0fb0ff…-c10bd326` із заміненим пакетом `jane_storage_mongodb` 2.0.0; контейнер перестворено з тією самою конфігурацією плюс `JANE_SECRET_DEV_MONGO_*` (маніфест `storage-mongo.private.json`, знімок до зміни — `storage-before-mongo-*.private.json`). Побічно compose видалив два зупинені резервні контейнери `jane-demo-storage-1-before-admin-*` (старші версії; їхні образи лишилися).
  - Завдання (штатними скриптами, без `--run`): `setup_sites.py apply` — 5 каталогів і 5 перевірок цін, bon, domria, 8 новинних сайтів, 8 Telegram-сторінок; `setup_shops.py --no-run` — 5 магазинів; `setup_automarket.py apply` — ads-autoria, ads-rst; `setup_classifieds.py configure` — 5 classifieds; `setup_news.py apply` — 12 завдань аналізу новин. Розклади й ліміти не змінились (звірено перед застосуванням). `news.articles` 1.0.1 — той самий код, що опублікований 1.0.0, але з LF у тестових сторінках (1.0.0 у реєстрі було зібрано з CRLF).
  - Перевірка: Storage бачить `results-mongo` (`availability: available`), `results-pg` читається як раніше. Запуски каталогів о 01:07 UTC уже використовують екстрактори 2.0.0 і `jane.storage-mongodb` і завершились успішно, але з 0 матеріалів — як і всі інкрементальні запуски з ~23:00 до переключення (відомі сторінки ще у вікні повторного відвідування). Тож на момент запису в `results-mongo` сутностей ще немає; перші очікуються із запусками за розкладом, що беруть матеріали (classifieds і магазини — о 09:00 за Києвом, automarket — кожні 6 годин, каталоги — після вікна повторного відвідування). Ручний перевірочний запуск не виконувався: його заблокував класифікатор дозволів.
  - 2026-10-13: штатне розгортання `4f052f61` (`scripts/deploy_admin_review.py apply --strategy drain`, повний CI [38323985107](https://github.com/sql-monk/Jane/actions/runs/38323985107), 14/14; перший прохід `e2e` упав на `502` Docker Hub і пройшов при повторі). Storage, оркестратор і воркер automarket — на образах `4f052f61`, UI — реліз `admin-4f052f61…`, резервна копія — `.jane/backups/admin-4f052f61…`. Розклади після `drain` відновлено. У `results-mongo` — 42 433 сутності, 71,5 MiB: `product_*` 39 179, `article` 1130, `ad_goods` 423, `post` 359, `ad_car` 331, `ad_realty` 192, `news_article` 115, `news_event` 4.
  - Проблема: усі 7322 товари bi-ua потрапили в `product_other` — у повному асортименті bi.ua інші верхні розділи (Творчість і розвиток, Сюжетно-рольові набори, Для активного відпочинку, Настільні ігри та пазли, Подарунки тощо), ніж п'ять у таблиці. Також `product_other`: yakaboo 1306, prostor 250, varus 119, epicentrk 7.
  - 2026-10-13, виправлення bi-ua: `catalog.bi-products` 2.0.1 (верхні розділи повного асортименту → `product_kids`, «Товари для школи» → `product_office`, «Подарунки» → `product_other`), опубліковано в `jane-demo` через `setup_sites.py apply bi` о 08:54 UTC. Після завершення останнього запуску зі старою конфігурацією (09:13:54 UTC) з `product_other` видалено 16 105 сутностей bi-ua і 16 105 записів їхньої історії; резервна копія — `.jane/backups/mongo-bi-ua-product_other-20261013T121414/` (`product_other.jsonl`, `product_other.history.jsonl`, `cutoff.txt`). Ключі доставки в `_deliveries` лишилися (зберігаються назавжди, ADR-0008). Повторна обробка (`POST /v1/reprocessing`) не відібрала жодного матеріалу: завдання каталогів не зберігають RAW, тож bi-ua наповнюється заново інкрементальним обходом (відомі сторінки — після вікна повторного відвідування 86 400 с).
  - Лишилися на `results-pg`: `ads-avtobazar` (вимкнений; опис сайту ввімкнув би його щогодини, тому не застосовувався) і тестові ланцюжки `visual-review-*-20261011`.
- Остаточна таксономія з джерелами й таблиці по сайтах — у [довіднику типів](../reference/entity-types.md).
- Обмеження: документ стану несе `pending` і `search_text`, тож практична межа однієї сутності — кілька МіБ (ліміт BSON 16 МіБ); тип `system` з порожнім префіксом недопустимий (`system.*` зарезервовано MongoDB).
- Відкладено: Storage ходить у MongoDB кореневим користувачем стеку, а не окремою роллю, як `jane_storage_results` у PostgreSQL (потрібен одноразовий `mongo-provision`).

### Нотатки для E (`jane-demo`)

- Контейнерами сервісів `jane-demo` керують знімки `compose.private.json` (`scripts/admin_operations_deploy.py`); `just up --project jane-demo storage` перезібрав би образ і підключив інший том — не використовувати.
- MongoDB: `docker compose -f infra/compose.yaml -p jane-demo up -d --wait mongodb` зі змінними з файлу стеку (паролі `JANE_MONGO_*` там уже є) і вручну дописати `services.mongodb` у `.jane/stack-jane-demo.json`; `just up` перезаписує цей файл і втрачає `admin_review_deployment`.
- Storage: перестворити зі знімка (той самий образ і томи) з новим образом адаптера й двома змінними `JANE_SECRET_DEV_MONGO_*`, `up -d --no-deps storage`.
- `results-mongo` зареєструвати в Orchestrator (`PUT /v1/connections/results-mongo`).
