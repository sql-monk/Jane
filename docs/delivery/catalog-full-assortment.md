# Повні каталоги п’яти магазинів

Дата: 11.10.2026. Обсяг: весь опублікований український асортимент Будинку іграшок, Епіцентру, PROSTOR, VARUS і Yakaboo; товари, доступні характеристики, наявність та історія цін.

## Реалізовано

- Повне discovery через товарні sitemap; VARUS обходить динамічне дерево категорій і брендів через публічний API, оскільки загальний список має серверне обмеження.
- Нативні завдання Jane: `incremental`, інтервал 900 секунд, `overlap: skip`. Бюджет частини: 400 сторінок для HTML-магазинів, 100 API-сторінок для VARUS. Період повторного допуску відомого URL — 86400 секунд.
- Незавершені частини продовжуються між запусками. Надлишок активної черги зберігається стисненим; незавершена sitemap/API-навігація має checkpoint. Невиконані позичені URL повертаються після failure/cancel; GC не видаляє потрібний donor.
- Індексована черга на SQLite та міграція старого frontier. Нові URL обробляються перед повторними відвідуваннями.
- Короткі транзакції discovery дають виконувати heartbeat і API навіть при відхиленні всіх URL. Транзакційні counters прибирають повні скани черги; завершення частини створює логічний checkpoint без переписування мільйонів URL. Наступна частина позичає лише вікно свого бюджету. Sitemap-кеш читається зі збереженого donor без копіювання BLOB; GC враховує також залишок лише у spool.
- Ціни й metadata зберігаються в `results-pg`; відсутня ціна не вигадується. PROSTOR зберігає відомі характеристики й наявність відсутнього товару без ціни; попередня ціна лишається останнім відомим спостереженням.
- Адитивні опції `api_feed`: `body_page_path`, `partitions`, `item_url_base`. Оновлено Collector, схему Registry, згенеровані валідатори й типи адмінки.

Конфігурації, пакети, команди й обмеження: [examples/sites/README.md](../../examples/sites/README.md). Вимоги API: [discovery-strategy.md](../../contracts/docs/discovery-strategy.md).

## Перевірене охоплення discovery

| Магазин | Перевірено | Межа твердження |
|---|---:|---|
| Будинок іграшок | 118 580 унікальних UA URL, 6 sitemap | Повний sitemap inventory; не число збережених сутностей |
| Епіцентр | 5 110 671 UA URL, 103 sitemap | 639 091 власних і 4 471 580 товарів маркетплейсу; 3 дублікати вилучено |
| PROSTOR | 9 339 унікальних UA URL | Повний sitemap inventory |
| VARUS | 6 724 API-підрозділи | Root повідомляє 32 055 товарів, але обмежує список 208 сторінками; точний унікальний SKU count ще не доведено |
| Yakaboo | 977 sitemap shards | Увесь index включено; точна кількість товарних UA URL ще не порахована |

Машинні докази: [inventory.json](../../examples/sites/catalogs/inventory.json). Discovery не обмежено колишніми 3–4 категоріями. Російські/регіональні дублі карток відсіюються правилами URL.

## Живі сутності й оновлення цін

Для кожного сайту через справжні Collector, HandlerRuntime і Storage API отримано свіже спостереження вже збереженого товару й застосовано часткове оновлення ціни. Сума може залишитися такою самою; перевіряється саме нове спостереження, а не вигадана зміна ціни.

| Магазин | Свіжа ціна, UAH | Збережено властивостей | History / version |
|---|---:|---:|---|
| Будинок іграшок | 2199 | 8 | 1 → 2 |
| Епіцентр | 3519 | 13 | 1 → 2 |
| PROSTOR | 174 | 11 | 1 → 2 |
| VARUS | 18,9 | 9 | 1 → 2 |
| Yakaboo | 257 | 13 | 1 → 2 |

У всіх п’яти price field order містить новий `observation_id`, значення відповідає живому output, `attributes` і всі непередані metadata збережено. Докази містять ключі, timestamps, digests, invocation IDs та before/after: [price-verification.json](../../examples/sites/catalogs/price-verification.json). Видалення попередньої ненульової `old_price` після завершення знижки доведено окремою регресією SDK + реального `storage.merge`; production ціни не підроблялися.

Усі вже збережені товари перевіряє [catalog_status.py](../../examples/sites/catalog_status.py): схеми відповідного сайту, числові ціни, назви властивостей і приклади історії. Поточні стиснені каталоги й результат перевірки: [catalogs/](../../examples/sites/catalogs/). IDs п’яти повних запусків, їхні знімки Collector і приклади provenance: [initial-runs.json](../../examples/sites/catalogs/initial-runs.json); API-перевірки виконувалися послідовно, timestamps не є одним атомарним знімком.

## Перевірки з фактичним виводом

```text
setup_sites.py check bi epicentrk prostor varus yakaboo: check кожного сайту: ok
examples/tests/test_sites.py: 5 passed in 4.47s
POST body/URL/cursor/partition HTTP tests: 15 passed in 2.82s
core continuation/crawl regression: 26 passed in 72.68s
independent core continuation: 8 passed in 32.72s; regression: 18 passed in 43.78s
independent indexed queue / legacy migration / cancelled spool: 2 passed in 1.02s; 1 passed in 0.46s
performance continuation/crawl/API regression: 34 passed in 42.86s
shared navigation cache / overflow-only GC regression: 5 passed in 3.33s
independent performance checks: 9 passed in 16.74s; overflow-only GC: 1 passed in 0.15s
registry reviewed-publication policy: 8 passed in 1.26s
PROSTOR SDK + storage.merge: 5 passed in 0.77s
contracts check --require-redocly: All contract checks passed; Redocly ok; 16 schemas, 47 schema examples
contracts compat --base origin/main --oasdiff: 7 API ok; 0 breaking, 0 warnings
gen-api.mjs --check: 10 generated files are up to date
admin TypeScript + Vite build: exit 0
lint: All checks passed; 532 files already formatted
mypy examples: Success: no issues found in 45 source files
verify_prices.py --project jane-demo: 5/5 success; exit 0
gitleaks v8.30.1, Git index export: 0 findings; exit 0
gitleaks git, 0b554fc..181d587: 4 commits scanned; no leaks found; exit 0
```

Рев’ю ядра: `accepted` незалежним `wp-reviewer`. Контракти: приймання дозволено, обов’язкові зауваження закрито; необов’язково розширити Assistant для генерації нових опцій — поточні пакети застосовуються напряму. Це координаторська задача без призначеного номера WP, тому `.jane-wp` не створювався.

## Поточна запущена версія

Окремий performance patch також має незалежне `accepted`. На 120 000 URL завершення checkpoint змінило два рядки БД, GC тривав 0,0003 с, позичення 400 URL — 0,031 с; лічильники узгоджені. На 12 000 sitemap URL перевірено heartbeat та доступність API під час seeding, включно з повністю відхиленими scope URL. Це локальні виміри, а не вимір повного 5,1-мільйонного циклу.

Пакети опубліковано й схвалено, п’ять джерел і десять завдань оновлено через API `jane-demo`. Разовий `--reviewed-package-updates` перевіряє пакети перед публікацією та відновлює заборону автоматичних змін після кожного upload, навіть при помилці. Походження LLM лишається в маніфестах.

Collector, Registry і адмінка розгорнуті. SHA-256 `state.py`, `crawler.py` та `engine.py` у контейнері збігаються з перевіреним checkout. Адмінка опублікована в незмінному релізі `admin-585ce80c05a1b673`. Порти й томи існуючого стеку збережено.

Старі запуски з обмеженими категоріями вже мали terminal collector, але утримували `overlap: skip` в оркестраторі. 04:56 UTC скасовано лише ці п’ять старих catalog runs і через Collector API скинуто лише їхні старі checkpoints. Товари та історія PostgreSQL збережені. О 05:02 UTC запущено п’ять нових повних обходів і відновлено нативний розклад 900 секунд із `overlap: skip`.

Знімок 05:07–05:10 UTC містить 2316 товарів: BI — 329, Епіцентр — 315, PROSTOR — 533, VARUS — 839, Yakaboo — 300. Для всіх п’яти `schema_invalid: 0`. Подальша API-перевірка історії BI, PROSTOR і VARUS підтвердила нові сутності з provenance саме нового повного запуску. Епіцентр і Yakaboo ще перелічують sitemap; їхні початкові збережені сутності походять із попередніх запусків і живої перевірки цін. Ранні sitemap Yakaboo містять RU категорії й фільтри; перевірені пізні UA товарні URL відповідають правилам.

Перевірені фактичні ліміти спільного стеку: Collector — 32 jobs і 4 години на job; HandlerRuntime — 8 jobs та 8 паралельних invocation; Orchestrator — 12 workers. Маніфести нормалізовано до LF, дев’ять змінених пакетів повторно опубліковано як `1.1.1`: байти всіх 19 пакетів і їхні digests збігаються з Git index. Уже запущені jobs зберігають свою версію `1.1.0`; наступні використовуватимуть `1.1.1`.

## Межі результату

Повний первинний збір ще не завершено. Знімки явно мають `full_scan_complete: false`. Наявність розкладу чи sitemap inventory не доводить, що всі картки вже збережено.

Ціна конкретного товару оновлюється під час його повторного відвідування. Інтервал 15 хвилин запускає чергову частину збору й не гарантує оновлення кожного товару раз на добу. Для BI мінімальна оцінка первинного циклу — близько 3 діб; для багатомільйонного Епіцентру цикл може тривати місяці. Помилки джерел, час спостереження та черга мають перевірятися через API й історію сутностей.
