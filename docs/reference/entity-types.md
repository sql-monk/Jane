# Типи сутностей

Довідник типів сутностей (`entity_type`), які пишуть пакети прикладів Jane: таксономія товарів і оголошень, правила вибору типу й колекції MongoDB, у які потрапляє кожен тип. Чому тип обирає екстрактор, а не сховище, пояснює [ADR-0011](../adr/0011-data-placement.md).

Актуально для пакета `jane.storage-mongodb@2.0.0` і пакетів прикладів версій 2.0.0 (2026-10-12, [план](../delivery/mongo-entities.md)).

## Зміст

- [Формат типу](#формат-типу)
- [Таксономія](#таксономія)
- [Правила вибору типу](#правила-вибору-типу)
- [Колекції MongoDB](#колекції-mongodb)
- [Відповідність розділів сайтів](#відповідність-розділів-сайтів)

## Формат типу

`entity_type` — рядок за шаблоном `^[a-z][a-z0-9_]{0,63}$` ([entity.schema.json](../../contracts/schemas/entity.schema.json)). Пакет оголошує свої типи в `output.entities` маніфесту ([маніфест](packages/manifest.md)). Тип разом із канонічним ключем ідентифікує сутність у сховищі, і за ним читає Storage API (`GET /v1/entities?entity_type=…`).

Контракт не обмежує набір типів. Таксономія нижче — домовленість для пакетів прикладів і реальних сайтів, а не перелік, який перевіряє Storage.

## Таксономія

Товари — `product_<група>`, оголошення — `ad_<група>`.

| Тип | Що входить | Джерела зараз |
|---|---|---|
| `product_food` | продукти, напої, алкоголь | varus, epicentrk, prostor |
| `product_beauty` | косметика, парфуми, гігієна й догляд | prostor, varus, epicentrk |
| `product_household` | побутова хімія | varus, epicentrk, prostor |
| `product_book` | книжки | yakaboo, epicentrk |
| `product_kids` | іграшки, дитячий транспорт, дитячі товари, настільні ігри | bi-ua, epicentrk, varus, prostor, yakaboo |
| `product_electronics` | електроніка, ноутбуки | shops (5 магазинів), epicentrk |
| `product_appliance` | побутова техніка | epicentrk |
| `product_tools` | інструменти, будівництво й ремонт, сантехніка, освітлення, підлога | epicentrk |
| `product_garden` | сад і город | epicentrk, varus |
| `product_home` | дім, інтер'єр, меблі, товари для дому | epicentrk, varus, prostor |
| `product_clothing` | одяг, взуття, аксесуари, галантерея | epicentrk, prostor, varus |
| `product_auto` | автотовари | epicentrk |
| `product_pet` | зоотовари | epicentrk, varus, prostor |
| `product_sport` | спорт і туризм | epicentrk, prostor, varus |
| `product_office` | канцтовари, шкільне | epicentrk, yakaboo, varus, bi-ua |
| `product_health` | медичні товари, БАДи | epicentrk, prostor, varus |
| `product_other` | сезонні розділи, «Несортовані», решта | — |
| `ad_car` | авто | autoria, rst, avtobazar, classified-auto-ria |
| `ad_realty` | нерухомість | domria, classified-dim-ria |
| `ad_goods` | речі: електроніка, дім, одяг | bon, olx, shafa, ria |
| `ad_other` | решта оголошень | — |

Типи, які таксономія не змінює:

| Тип | Що це |
|---|---|
| `product` | товар тестового магазину (`examples/packages`, приймальний сценарій ТЗ §12) |
| `event` | подія з Telegram-прикладу (`examples/packages`) |
| `article` | стаття новинного сайту або публічної сторінки Telegram-каналу |
| `news_article` | нормалізована й проаналізована новина (`examples/news`) |
| `news_event` | подія, виділена з новини (`examples/news`) |
| `post` | допис Telegram-каналу (`examples/channels`, `examples/sites`) |

## Правила вибору типу

1. **Тип обирає екстрактор.** Storage кладе сутність у колекцію її `entity_type` і нічого не вгадує.
2. **Джерело типу.** Екстрактор картки бере тип одним із двох способів:
   - за таблицею «префікс `category_path` → тип» у пакеті сайту;
   - фіксованим параметром етапу, якщо завдання охоплює одну категорію (наприклад, магазини електроніки — `product_electronics`).
3. **Невідома категорія** — `product_other` або `ad_other`, а не новий тип.
4. **Екстрактор цін не вгадує.** Часткове оновлення (ціна, наявність) має той самий тип, що й картка, бо тип входить в ідентичність сутності. Якщо екстрактор цін не може визначити цей тип, він не пише сутність і повертає статус `unrecognized`.
5. **Зміна відповідності створює нову сутність.** Після перенесення розділу в інший тип наступний збір пише сутність в іншу колекцію. Стара лишається у своїй колекції разом з історією.

## Колекції MongoDB

Сутності пише адаптер `jane.storage-mongodb@2.0.0`. Для підключення `results-mongo` dev-стеку база — `jane_results`, префікс колекцій `params.prefix` — порожній ([підключення Storage](../../infra/README.md#підключення-storage)).

| Колекція | Вміст |
|---|---|
| `<prefix><entity_type>`, наприклад `product_book` | актуальний стан сутностей типу |
| `<prefix><entity_type>.history`, наприклад `product_book.history` | історія версій сутностей типу |
| `<prefix>_deliveries` | ключі доставки; зберігаються безстроково ([ADR-0008](../adr/0008-api-and-delivery-semantics.md)) |
| `<prefix>_objects`, `<prefix>_object_chunks` | RAW і документи результатів, якщо етап пише їх у MongoDB |

`entity_type` не починається з `_` і не містить крапки, тому колекції типів не перетинаються ні зі службовими, ні з колекціями історії. Тип `system` потребує непорожнього префікса: MongoDB резервує імена `system.*`. Індекси, атомарність, каталог, пошук і статистика описані в розділі [адаптери: mongodb](../components/storage/adapters.md#mongodb).

Каталог типів сховища показує `GET /v1/entity-types?connection_id=results-mongo`. У ньому лише типи, для яких уже збережено сутності, з точною кількістю. Сторінка «Результати» Admin UI будує з нього картки типів.

## Відповідність розділів сайтів

Таблиці «розділ сайту → тип» зберігаються в пакетах сайтів, а не в Storage. Розділ шукається за найдовшим префіксом `category_path` (без урахування регістру, варіантів апострофа й зайвих пробілів); розділ поза таблицею дає `*_other`. Таблиця однакова в екстракторі картки й екстракторі цін одного сайту — це перевіряє `examples/tests/test_sites.py`.

| Де | Як задано тип |
|---|---|
| `examples/sites/packages/catalog.*` | таблиця `CATEGORY_TYPES` в екстракторах карток і цін bi-ua, epicentrk, prostor, varus, yakaboo |
| `examples/sites/packages/ads.bon-ads` | таблиця розділів верхнього рівня bon.ua |
| `examples/sites/packages/ads.domria-listing`, `autos.*`, `examples/classifieds/packages` | фіксований тип пакета: джерело охоплює одну категорію |
| `examples/shops/packages` | обов'язковий параметр етапу `entity_type`; завдання ноутбуків — `product_electronics` |

### Каталоги

| Сайт | Розділ → тип |
|---|---|
| bi-ua | Дитячий транспорт; Колекційні та ігрові фігурки; Конструктори; Машинки, роботи, трансформери; М'які та інтерактивні іграшки; Для активного відпочинку; Настільні ігри та пазли; Сюжетно-рольові набори; Творчість і розвиток → `product_kids`; Товари для школи → `product_office`; Подарунки → `product_other` |
| epicentrk | Автотовари → `product_auto`; Будівництво та ремонт, Інструменти, Освітлення, Покриття для підлоги, Сантехніка → `product_tools`; Дитячі товари → `product_kids`; Дім та інтер'єр, Меблі → `product_home` (Дім та інтер'єр › Книги → `product_book`); Електроніка → `product_electronics`; Зоотовари → `product_pet`; Краса та здоров'я → `product_beauty`; Медичні товари → `product_health`; Одяг, взуття, аксесуари → `product_clothing`; Офіс і канцтовари → `product_office`; Побутова техніка → `product_appliance`; Побутова хімія → `product_household`; Продукти → `product_food`; Сад та город → `product_garden`; Спорттовари, Туристичні товари → `product_sport`; Товари для бізнесу → `product_other` |
| prostor | Волосся, Косметика, Обличчя, Парфуми, Тіло → `product_beauty`; Галантерея → `product_clothing`; Дім → `product_home` (› Зоотовари → `product_pet`, › Продукти → `product_food`, › Спортивні товари → `product_sport`); Дітям → `product_kids`; Здоров`я → `product_health`; Побутова хімія → `product_household`; Продукти → `product_food`; Чоловікам — лише підрозділи (› Спідня білизна, › Чоловічі шкарпетки → `product_clothing`; › Чоловічі засоби для стайлінгу → `product_beauty`); Великдень › Кондитерський декор → `product_food`; Святий Миколай › Дитяча косметика → `product_beauty`; решта сезонних і збірних розділів → `product_other` |
| varus | продуктові розділи, зокрема VARUS CAFE і Алкоголь → `product_food` (Здорове харчування та Еко товари › БАДи → `product_health`); Гігієна та догляд → `product_beauty` (› Товари для здоров'я → `product_health`); Побутова хімія → `product_household`; Товари для дітей → `product_kids` (› Шкільні товари → `product_office`); Товари для дому → `product_home` (› Канцтовари → `product_office`, › Одяг, взуття та аксесуари → `product_clothing`, › Сад та город → `product_garden`, › Спорт та розваги, › Товари для кемпінгу та відпочинку → `product_sport`); Товари для тварин → `product_pet`; Головна, Тютюнові вироби → `product_other` |
| yakaboo | Книжки → `product_book`; Ігри та творчість, Настільні ігри → `product_kids`; Кольорові олівці, Рюкзаки, сумки шкільні, Шкільні зошити → `product_office`; Супутні товари, Часто шукають → `product_other` |

Екстрактори цін bi-ua, epicentrk, prostor і yakaboo беруть тип із хлібних крихт сторінки категорії й повертають `unrecognized`, якщо розділ не в таблиці або глибший підрозділ має інший тип. Екстрактор цін VARUS визначає тип за категоріями самого товару тією самою функцією, що й картка. Залишковий ризик: товар, який трапився на сторінці іншого розділу, ніж у хлібних крихтах його картки (наприклад, подарунковий набір у сезонному розділі), отримає ціну в колекції розділу сторінки.

### Оголошення

| Джерело | Тип |
|---|---|
| bon.ua | Нерухомість → `ad_realty`; Транспорт → `ad_car`; Електроніка, побутова техніка; Дім та Дача; Одяг, взуття, аксесуари; Дитячий світ; Запчастини для транспорту; Будівництво та ремонт; Спорт, відпочинок; Хобі, музика, мистецтво; Краса та здоров'я; Обладнання → `ad_goods`; Робота, Резюме, Послуги, Тварини та рослини → `ad_other`. Сторінка категорії без розділу верхнього рівня → `unrecognized` |
| dom.ria.com (domria), classified-dim-ria | `ad_realty` |
| AUTO.RIA (картки й пошук), RST.ua, Avtobazar InfoCar, classified-auto-ria | `ad_car` |
| classified-olx (ноутбуки), classified-ria (мобільні), classified-shafa | `ad_goods` |

В одній колекції можуть лежати сутності різних пакетів з різними ключами: наприклад, `ad_car` отримує оголошення autos.* (ключ `site` + `ad_id`) і classifieds.auto-ria-ads (ключ `site` + `listing_id`), тож одне оголошення AUTO.RIA з двох джерел — дві сутності з різними `scope`.
