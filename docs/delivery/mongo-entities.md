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
- Відкладено: Storage ходить у MongoDB кореневим користувачем стеку, а не окремою роллю, як `jane_storage_results` у PostgreSQL (потрібен одноразовий `mongo-provision`).

### Нотатки для E (`jane-demo`)

- Контейнерами сервісів `jane-demo` керують знімки `compose.private.json` (`scripts/admin_operations_deploy.py`); `just up --project jane-demo storage` перезібрав би образ і підключив інший том — не використовувати.
- MongoDB: `docker compose -f infra/compose.yaml -p jane-demo up -d --wait mongodb` зі змінними з файлу стеку (паролі `JANE_MONGO_*` там уже є) і вручну дописати `services.mongodb` у `.jane/stack-jane-demo.json`; `just up` перезаписує цей файл і втрачає `admin_review_deployment`.
- Storage: перестворити зі знімка (той самий образ і томи) з новим образом адаптера й двома змінними `JANE_SECRET_DEV_MONGO_*`, `up -d --no-deps storage`.
- `results-mongo` зареєструвати в Orchestrator (`PUT /v1/connections/results-mongo`).
