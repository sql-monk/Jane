# Повні каталоги п’яти магазинів

Дата: 11.10.2026. Обсяг: весь опублікований український асортимент Будинку іграшок, Епіцентру, PROSTOR, VARUS і Yakaboo; товари, доступні характеристики, наявність та історія цін.

## Зміст

- [Реалізовано](#реалізовано)
- [Перевірене охоплення discovery](#перевірене-охоплення-discovery)
- [Живі сутності й оновлення цін](#живі-сутності-й-оновлення-цін)
- [Перевірки з фактичним виводом](#перевірки-з-фактичним-виводом)
- [Поточна запущена версія](#поточна-запущена-версія)
- [Інцидент PROSTOR 11 жовтня 2026](#інцидент-prostor-11-жовтня-2026)
- [Межі результату](#межі-результату)

## Реалізовано

- Повне discovery через товарні sitemap; VARUS обходить динамічне дерево категорій і брендів через публічний API, оскільки загальний список має серверне обмеження.
- Нативні завдання Jane: `incremental`, інтервал 900 секунд, `overlap: skip`. Бюджет частини: 400 сторінок для HTML-магазинів, 100 API-сторінок для VARUS. Період повторного допуску відомого URL — 86400 секунд.
- Незавершені частини продовжуються між запусками. Надлишок активної черги зберігається стисненим; незавершена sitemap/API-навігація має checkpoint. Невиконані позичені URL повертаються після failure/cancel; GC не видаляє потрібний donor.
- Індексована черга на SQLite та міграція старого frontier. Нові URL обробляються перед повторними відвідуваннями.
- Короткі транзакції discovery дають виконувати heartbeat і API навіть при відхиленні всіх URL. Транзакційні counters прибирають повні скани черги; завершення частини створює логічний checkpoint без переписування мільйонів URL. Наступна частина позичає лише вікно свого бюджету. Sitemap-кеш читається зі збереженого donor без копіювання BLOB; GC враховує також залишок лише у spool.
- XML і gzip розбираються поза циклом подій. Спільний слот типово одного потоку утримується до завершення розбору та приймання документа в чергу; скасування й закриття ітератора звільняють його після фактичного завершення роботи. Ліміт задається через `JANE_WEB_COLLECTOR_SITEMAP_PARSE_WORKERS`. Залежність `sniffio` зафіксована в `uv.lock` як `1.3.1`.
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
document lifetime / cancellation / SDK / resume: 11 passed in 23.68s; optional callable SDK guard: 1 passed in 0.94s
Windows, five gated 50k-entry sitemaps: 2 passed in 31.82s; max health 1.3091 / 1.3587 seconds
independent lifecycle / resume / SDK: 11 passed in 22.50s
independent gzip / DTD / truncation / formats / lastmod: 21 passed in 0.95s
independent queue cap / restart / GC / failed and cancelled loans: 4 passed in 5.63s
independent Linux, five gated 50k-entry sitemaps: 2 passed in 24.66s
Linux max health: 0.9327 / 0.8121 seconds; max lease gaps: 0.9955 / 5.1132 seconds
focused ruff: All checks passed; mypy: Success: no issues found in 6 source files
uv lock --check: Resolved 113 packages; exit 0
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
gitleaks git, all refs: 915 commits scanned; 42.40 MB; no leaks found; exit 0
public catalog credential audit, including decompressed gzip: 10 files checked; 0 credential matches; exit 0
gitleaks staged artifacts, all five gzip expanded: 8 files; 53.28 MB; no leaks found; exit 0
```

Рев’ю ядра: `accepted` незалежним `wp-reviewer`. Контракти: приймання дозволено, обов’язкові зауваження закрито; необов’язково розширити Assistant для генерації нових опцій — поточні пакети застосовуються напряму. Це координаторська задача без призначеного номера WP, тому `.jane-wp` не створювався.

## Поточна запущена версія

Окремий performance patch також має незалежне `accepted`. На 120 000 URL завершення checkpoint змінило два рядки БД, GC тривав 0,0003 с, позичення 400 URL — 0,031 с; лічильники узгоджені. На 12 000 sitemap URL перевірено heartbeat та доступність API під час seeding, включно з повністю відхиленими scope URL. Це локальні виміри, а не вимір повного 5,1-мільйонного циклу.

Пакети опубліковано й схвалено, п’ять джерел і десять завдань оновлено через API `jane-demo`. Разовий `--reviewed-package-updates` перевіряє пакети перед публікацією та відновлює заборону автоматичних змін після кожного upload, навіть при помилці. Походження LLM лишається в маніфестах.

Collector, Registry і адмінка розгорнуті. Спільний стек також містить окремо прийняті зміни Chromium transport та operations; оновлення Collector має зберігати ці файли, чинне середовище, порти, томи й jobs. Адмінка на момент першого catalog deployment опублікована в незмінному релізі `admin-585ce80c05a1b673`.

Фінальний sitemap patch `e68352ec9326c59d7f0e7af196b04ceabbeb33cc` незалежно прийнято й розгорнуто о 07:21:14 UTC. Чинний образ Collector — `sha256:560bda29114a0e96ffc030bbb9eb82bc0a32ef15f1107a35f9c64b1472843251`, tag `jane-catalog-offload:e68352ec9326`. Образ побудовано поверх фактичного `82ad…`; змінені файли збігаються з прийнятим Git commit, wheel `sniffio` перевірено за SHA-256 із lockfile. Після розгортання підтверджено незмінність середовища, портів, томів, мереж, user/shm/security/resource settings, healthcheck, `state.py`, `fetcher.py`, схеми й чотирьох operations-файлів. Jobs і checkpoints не скидались. `engine.py` та контрактні файли цей patch не змінює.

Живий аудит 07:22–07:27 UTC: п’ять послідовних health-запитів повернули HTTP 200 за 1,109 / 0,641 / 0,875 / 0,844 / 0,594 секунди; медіана — 0,844 секунди. Docker має `healthy`, `failing_streak: 0`; серед 1252 рядків логів після рестарту немає `lease_lost`, повторного resume або сигналів обрізання sitemap. Усі вісім перевірок збереження конфігурації, файлів і залежності успішні. Час і логи обмежені вікном цього спостереження. Публічний доказ із хешами, native run IDs, бюджетами й counters: [runtime-verification.json](../../examples/sites/catalogs/runtime-verification.json).

Усі п’ять native tasks мають інтервал 900 секунд і `overlap: skip`; запуски з `trigger: schedule`, `test_mode: false` продовжили попередні частини: BI, Епіцентр і PROSTOR позичили по 400 URL, VARUS і Yakaboo — по одному navigation checkpoint. За наступні дві хвилини BI додав 92 матеріали, Епіцентр — 79, PROSTOR — 108, VARUS — 10. VARUS тимчасово чекав ACK для 500 матеріалів; це обмеження потоку, помилок Collector у цьому run немає. Yakaboo продовжив розбір sitemap й відхилив ще 652 648 URL поза scope, але в цій новій частині товарних матеріалів ще немає. PROSTOR окремо має підтверджені `not_found` і `out_of_scope`; вони збережені в доказі й не трактуються як валідні товари.

Старі запуски з обмеженими категоріями вже мали terminal collector, але утримували `overlap: skip` в оркестраторі. 04:56 UTC скасовано лише ці п’ять старих catalog runs і через Collector API скинуто лише їхні старі checkpoints. Товари та історія PostgreSQL збережені. О 05:02 UTC запущено п’ять нових повних обходів і відновлено нативний розклад 900 секунд із `overlap: skip`.

Знімок із `checked_at: 07:21:51 UTC`, отриманий послідовними API-запитами до 07:24:41 UTC, містить **15 299 товарів**: BI — 2301, Епіцентр — 587, PROSTOR — 2317, VARUS — 9794, Yakaboo — 300. Із них **14 032 мають ціну**. Для всіх п’яти `schema_invalid: 0`. Об’єднання назв доступних властивостей містить відповідно 26, 562, 98, 431 і 30 ключів; це кількість різних властивостей у каталозі, а не в кожному товарі. Історія та provenance підтверджують нові сутності з повного обходу BI, Епіцентру, PROSTOR і VARUS. Yakaboo ще обробляє sitemap; його початкові 300 сутностей походять із попередніх запусків і живої перевірки цін. Ранні sitemap Yakaboo містять RU категорії й фільтри; перевірені пізні UA товарні URL відповідають правилам.

У поточному runtime-доказі завершені native parts BI о 07:17:50 UTC та PROSTOR о 07:17:02 UTC мають `succeeded`, відповідно 400 і 392 fetched URL. BI зберіг `continuation_pending: 116587`, PROSTOR — `7336`; нові scheduled runs позичили з цих checkpoints по 400 URL. Для PROSTOR stats містять 13 помилок, а перша сторінка їхнього списку — п’ять `not_found` / `out_of_scope`, `has_more: true`. Цей результат доводить збереження невиконаної черги, а не завершення всього асортименту.

Перевірені фактичні ліміти спільного стеку: Collector — 32 jobs і 4 години на job; HandlerRuntime — 8 jobs та 8 паралельних invocation; Orchestrator — 12 workers. Маніфести нормалізовано до LF, дев’ять змінених пакетів повторно опубліковано як `1.1.1`: байти всіх 19 пакетів і їхні digests збігаються з Git index. Jobs, створені до цієї публікації, зберегли свою версію `1.1.0`; нові scheduled runs у поточному runtime-доказі використовують `1.1.1`.

## Інцидент PROSTOR 11 жовтня 2026

### Спостереження до виправлення

Під час аудиту 11 жовтня 2026 Collector job `job_9cc8013d1a294a569ac20551b42843e1` уже мав `succeeded` і 380 emitted матеріалів. Orchestrator run `run_01M4N4AX9Z7DBDDNGNGJK76CCN` залишався `running`: прийнято 372 матеріали, завершено 744 handler items, `feed_done: false`. Решта 8 матеріалів залишалася у буфері Collector; їхня відповідь мала `end_of_stream: true`.

Вставка routed inputs у PostgreSQL JSONB повторно завершувалася `psycopg.errors.UntranslatableCharacter`: `\u0000 cannot be converted to text`. Транзакція приймання сторінки відкочувалася до збереження `feed_cursor`, тому звичайний retry знову отримував той самий неприйнятий залишок. Завершення Collector саме собою не встановлює `feed_done`: останню непорожню сторінку потрібно зберегти, а наступний порожній EOF-запит підтверджує її ACK. `overlap: skip` орієнтується на активний run Orchestrator; інтервал 900 секунд не розблоковує помилку приймання матеріалу.

Read-only перевірка підтвердила єдиний NUL у `$.items[0].content.data`: inline `text/html`, `encoding: utf-8`, 245 334 декодованих байти. Фактичні size і SHA-256 збігалися із заявленими; base64 round-trip повернув ідентичні байти, розмір і digest, а закодований рядок не містив NUL. GET виконувався без `after`, з `wait_ms: 0`; ACK і збережений курсор Orchestrator не змінювалися.

### Зміна збереження payload

Прийнятий source commit — `5a3ce874252386b7a7071911c9bf2c02efff619f`. У [engine.py](../../services/orchestrator/src/jane_orchestrator/engine.py) `_jsonb_inputs` перед вставкою inputs переводить лише `material.content.data` із реальним U+0000 та `encoding: utf-8` у `encoding: base64`. Це вже дозволена форма [ContentRef](../../contracts/schemas/common/content-ref.schema.json); споживачі декодують ті самі UTF-8 байти.

Перетворення зберігає `sha256`, `size_bytes`, charset та всі інші поля матеріалу. Оригінальний документ Collector не змінюється; звичайний текст, буквальний рядок `\u0000`, готові base64 і blob references передаються без змін. Логіка курсора, транзакцій, delivery keys і EOF ACK залишається чинною. Для відновлення поточного run після розгортання потрібен його звичайний retry; ручне просування курсора чи скидання стану не застосовувалося.

### Перевірки й стан приймання

[Регресія](../../services/orchestrator/tests/test_feed_content_encoding.py) працює зі справжнім PostgreSQL 18; HTTP-сусіди перевіряються за контрактами. Тестові fixtures створюють і видаляють власну унікальну БД на наявному тестовому PostgreSQL. Перевірено точні байти через `ContentReader`, збережені metadata, durable cursor, читання новим app/worker, наступний порожній EOF ACK і завершення всіх downstream stages без втрат чи повторних ефектів.

```text
PG baseline до виправлення: 1 failed in 15.19s
psycopg.errors.UntranslatableCharacter: unsupported Unicode escape sequence
DETAIL: \u0000 cannot be converted to text; parameter $6
independent NUL regression + existing final EOF ACK: 2 passed in 75.67s
first combined NUL / EOF / M1 run: 1 failed, 2 passed in 110.05s (M1 timeout 30s)
targeted M1 rerun: 1 passed in 29.09s
ruff check: All checks passed; format: 2 files already formatted
mypy engine.py: Success: no issues found in 1 source file
```

Старий M1-тест і його 30-секундний timeout не змінювалися; точна причина першого timeout не доведена. Незалежне source review прийняло виправлення. [CI 38132054531](https://github.com/sql-monk/Jane/actions/runs/38132054531) завершився успішно на точному commit `5a3ce874`: перевірено всі 14 jobs через API з `per_page=100`.

### Відновлення чинного запуску

О 11:23:16–17 UTC оновлено обидва процеси Orchestrator до образу `sha256:be47a9747786a2b7a2267ea62d5a4f0f3980d5f81b9ab0d0f8e9a4d1f7be80f2`. SHA-256 чинного `engine.py` — `25d1ea1cd2fb07ea841ab37966d00919de08e8cdf7409531461434918f265409`, точні байти прийнятого commit `5a3ce874`. Перші десять шарів образу збігаються з фактичною базою `0fe…a8a368`; інші 46 файлів core/kit збережено. Середовище, ресурси, групи, порти, томи й мережеві aliases збережено; Collector560, його container ID, час запуску й конфігурація не змінювалися.

Перед запуском нових процесів власний стан Orchestrator був незмінний у спокійному вікні: `after_stop` та `before_start` мають однаковий SHA-256 `7246d7ddbb7290663c77108fc3fc686724f2b5bf7a807a66429810abef23cfaf`. Після запуску звичайний retry просунув курсор того самого run з hash `db50ff0b…92cd4b0a` до `71bb92a6…eec7bd27`. О 11:23:34.391179 UTC він завершився `succeeded`, `feed_done: true`, `backpressure: false`, без `feed_error`. У кожному з трьох етапів стало 380 завершених items замість 372: решта восьми матеріалів пройшла collect, extract і store. Ручних змін стану через БД чи API, cancel/reset/replay та нових backups або exports не виконувалося.

Перед успішним застосуванням дві спроби завершилися перевірками без запуску нових writers: build не розпізнав локальний image ID, а наступна спроба відхилила різницю `OomKillDisable: null` проти типового `false` і автоматично повернула початкові writers. Відновлення БД не виконувалося. Побудову виправлено перевіреним локальним alias із контролем image ID та базових шарів; порівняння нормалізує лише підтверджений типовий параметр [Docker daemon](https://github.com/moby/moby/blob/master/daemon/daemon_unix.go). Тіло запиту clone та ефективні налаштування лишилися чинними; explicit `true` та інші зміни відхиляються. Незалежний review прийняв фінальний helper з SHA-256 `15fdb9016a8c2cfb3ec1841e71cdce6448a0432bf1a2011306daa6096c184bfd`; реальний preflight перевірив обидві заміни, negative controls — OOM, Env, hostname, Memory, GroupAdd та custom alias.

Жива перевірка Storage API о 11:27:40 UTC підтвердила всі вісім точних canonical keys: schema errors — 0, ціни додатні й скінченні, властивостей відповідно 3 / 14 / 3 / 14 / 15 / 9 / 9 / 6. У кожній історії є той самий run та відповідні observation/material IDs; provenance посилається на `catalog.prostor-product-extractor` версії `1.1.1`. Товар із проблемного NUL-матеріалу також збережений і валідний.

Повторне читання persisted ContentRef після завершення недоступне: штатний cleanup обнулив payload усіх восьми items. Це не підміняється повторним збором або відновленням payload. Доказ точних байтів спирається на початкову read-only перевірку матеріалу й реальну PG-регресію. Зіставлення успішних invocation із кодом дає додатковий висновок: до extraction мала пройти обов’язкова SHA-256 перевірка [ContentReader](../../libs/jane-kit/src/jane_kit/content.py), оскільки Collector завжди додає digest, а fix його зберігає. Це висновок із коду та результату виконання, а не повторне читання payload. Для inline decoder перевіряє hash і ліміт декодованих байтів; він не робить окремого порівняння declared `size_bytes` із довжиною. Початковий матеріал мав підтверджену довжину 245 334 байти, а lossless перетворення зберігає його байти й metadata.

Наступний native run `run_01M4NC23MJQG9RPHZ810M40QC6` почався за розкладом о 11:37:37.717 UTC, `trigger: schedule`, Collector job `job_4fa7767bf2d741fba24eee343f160bb7`, правила `1.1.1`. Він продовжив 400 URL. О 11:38:48 UTC fetched збільшився з 57 до 58, emitted — із 46 до 47; 45 матеріалів уже збережено. Source state просунувся з `known: 5504 / frontier: 3736` до `5562 / 3678`. Collector повідомляв одну помилку джерела; це не подається як збір без помилок. Наступний запуск не створювали вручну. Повний датований доказ із перевірками восьми товарів, п’яти розкладів, schema/provenance та здоров’я: [feed-recovery-verification.json](../../examples/sites/catalogs/feed-recovery-verification.json).

Друга перевірка того самого scheduled run о 11:40:02 UTC підтвердила 106 завершених store items; fetched у job зріс до 119, а collection stats, прочитані наступним запитом, уже мали 120 fetched і 109 emitted. Черга джерела просунулася до `known: 5624 / frontier: 3616`. Єдина зафіксована помилка джерела — `not_found`. У датованому вікні 11:29:58–11:39:58 UTC в логах Collector не було `lease_lost`, SQLite lock/error, OOM чи startup/restart сигналів; контрольний health GET мав HTTP 200 за 31,9 мс. Це спостереження лише за вказане вікно.

Після розгортання перевірено всі п’ять чинних задач: `enabled: true`, `interval_seconds: 900`, `overlap: skip`, `mode: incremental`; digest документів задач не змінився. Read-only вибірки Storage о 11:04:46 UTC для всіх п’яти сайтів валідні за UTF-8 схемами, мають додатну скінченну ціну й 7 / 10 / 15 / 8 / 8 властивостей відповідно. Вибірка Yakaboo походить зі старого subset run; нові збережені сутності саме його поточного повного обходу станом на 11:29:29 UTC залишаються недоведеними. Два початкові процеси Orchestrator збережені зупиненими, exit code 0; нових копій їхніх даних не створено.

## Межі результату

Повний первинний збір ще не завершено. Знімки явно мають `full_scan_complete: false`. Наявність розкладу чи sitemap inventory не доводить, що всі картки вже збережено.

Ціна конкретного товару оновлюється під час його повторного відвідування. Інтервал 15 хвилин запускає чергову частину збору й не гарантує оновлення кожного товару раз на добу. Для BI мінімальна оцінка первинного циклу — близько 3 діб; для багатомільйонного Епіцентру цикл може тривати місяці. Помилки джерел, час спостереження та черга мають перевірятися через API й історію сутностей.
