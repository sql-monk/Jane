# Типи сутностей

Довідник типів сутностей (`entity_type`), які пишуть пакети прикладів Jane: таксономія товарів і оголошень, правила вибору типу й колекції MongoDB, у які потрапляє кожен тип. Чому тип обирає екстрактор, а не сховище, пояснює [ADR-0011](../adr/0011-data-placement.md).

Актуально для ревізії `118707e` (2026-10-12) і пакета `jane.storage-mongodb@2.0.0`. Переведення прикладів на ці типи ще триває ([план](../delivery/mongo-entities.md)).

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

Таблиці відповідності «розділ сайту → тип» зберігаються в пакетах сайтів, а не в Storage:

| Де | Що там |
|---|---|
| `examples/sites/packages/catalog.*` | екстрактори карток і цін каталогів bi-ua, epicentrk, prostor, varus, yakaboo |
| `examples/sites/packages/{ads,autos}.*` | екстрактори оголошень сайтів |
| `examples/classifieds/packages`, `examples/automarket/packages` | екстрактори оголошень classifieds і automarket |
| документи завдань `examples/shops` | фіксований тип `product_electronics` у параметрі етапу |

Таблиці по сайтах буде додано сюди, коли пакети сайтів переведуть на нові типи.
