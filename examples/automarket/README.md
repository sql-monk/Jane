# Каталог авторинку

Сценарій налаштовує в запущеній Jane деталізовані оголошення AUTO.RIA та RST.ua. Зберігаються публічні характеристики транспорту, опис, комплектація, фото та походження даних. Значення, яких немає на сторінці, пропускаються. Avtobazar.ua позначено недоступним: він перенаправляє на новинний Autocentre.ua; користувач відхилив заміну на InfoCar.

## Пакети

Пакети спільні з [каталогом сайтів](../sites/README.md) і лежать лише в [examples/sites/packages](../sites/packages): одна версія пакета — один архів і один digest, хоч би який сценарій його публікував.

| Пакет | Версія | Роль |
|---|---|---|
| `autos.autoria-rules` | 1.1.1 | Обхід каталогу AUTO.RIA і карток оголошень |
| `autos.autoria-ad-page` | 2.0.0 | Повна картка AUTO.RIA → `ad_car` |
| `autos.autoria-search-page` | 2.0.0 | Часткове оновлення `ad_car` зі сторінки пошуку; публікується, але етапами цього сценарію не використовується |
| `autos.rst-rules` | 1.1.0 | Обхід каталогу RST.ua і карток оголошень |
| `autos.rst-car-ads` | 2.0.0 | Плитки каталогу й картки RST.ua → `ad_car` |
| `jane.storage-files` | версія checkout | RAW у `raw-files` |
| `jane.storage-mongodb` | 2.0.0 | Сутності в `results-mongo` |

Тип сутності — `ad_car` (таксономія типів оголошень). Він фіксований у пакетах: обидва джерела містять лише оголошення авто. Версії 2.0.0 змінили тільки тип (`car_ad` → `ad_car`); поля, ключ і схеми ті самі.

## Запуск

Потрібні Python/uv, запущений стек із Registry, Web Collector, Handler Runtime і Storage з MongoDB, а також уже налаштовані підключення `raw-files` та `results-mongo` (MongoDB, база `jane_results`, див. `infra/config/storage-connections.json`). У Registry має бути затверджений `jane.storage-mongodb` тієї версії й digest, що в checkout. Секрети читаються зі службового файлу стеку та посилань підключень; у пакети й Git вони не копіюються. Сценарій використовує [контрактні клієнти прикладів](../jane_examples.py).

Виконувати з кореня checkout:

```powershell
uv sync --all-packages --frozen
uv run --all-packages python examples/automarket/setup_automarket.py check
uv run --all-packages python examples/automarket/setup_automarket.py apply --stack-file .jane/stack-jane-demo.json --cancel-active --allow-generated-packages
uv run --all-packages python examples/automarket/setup_automarket.py run --stack-file .jane/stack-jane-demo.json --receipt .jane/automarket-runtime.json
```

`apply --cancel-active` скасовує незавершені попередні запуски лише `ads-autoria`, `ads-rst` та `ads-avtobazar`; збережені дані залишаються. Нові версії екстракторів проходять тести у справжньому runtime перед затвердженням. Підключення сховищ зберігаються без перезапису. Оновлення конфігурацій використовує ETag та `If-Match`.

`--allow-generated-packages` — явний дозвіл опублікувати нові LLM-версії. Якщо пакет забороняє автоматичні зміни, драйвер дозволяє їх лише на час upload та відновлює попередню заборону в `finally`, зокрема при помилці. Походження залишається `llm`; вже опубліковані версії не переписуються. `--http-timeout` задає HTTP timeout у секундах (типово 120), окремо від очікування job (`--timeout`).

Транспортні повтори обмежено `--transport-retries` (типово 2) та `--retry-delay` (2 секунди); перед повтором локальна адреса уточнюється через Docker. Повтор POST дозволений лише з незмінним Idempotency-Key. `--test-retries` (типово 2) створює новий тестовий job лише після термінального `failed` з явним `error.retryable=true`; наступний ключ походить від digest та попереднього job ID. Повторний запуск драйвера використовує ті самі job. Загальне очікування обмежено `--timeout`; провали тестових assertions не повторюються й не затверджуються.

## Обхід і розклад

| Параметр | Типово | Налаштування |
|---|---:|---|
| Інтервал | 21600 с (6 год) | Розклад `ads-autoria` та `ads-rst` у Jane |
| Перекриття запусків | `skip` | Наступний запуск пропускається, доки попередній триває |
| Сторінок за регулярний запуск | 120 | `apply --pages` |
| Сторінок за початкову перевірку | 11 | `run --validation-pages`; включає сторінки каталогу |
| Глибина | 5 | `limits.crawl.max_depth` завдання |
| Запитів на хост | 1/с, не паралельно | Ліміти джерела; `robots.txt` може додатково зменшити частоту |
| Повторне відвідування картки | 21600 с | `revisit_interval_seconds` |
| Очікування перевірки | 1800 с | `--timeout` |

Каталог нарощується обмеженим інкрементальним обходом перших сторінок за датою додавання. Цей ліміт не означає повне завантаження всіх оголошень автобазару. Для першої перевірки збирається до десяти карток; етап екстракції приймає лише розділ `ad`, а не короткі плитки списку.

Початкова перевірка `run` задає лише для цього запуску `revisit_interval_seconds=0`: сторінки перечитуються навіть після недавнього збору. Регулярне завдання має інтервал повторного відвідування 21600 секунд. Наявність старого crawler state не підтверджує, що новий екстрактор уже записав сутності.

## Збереження та перевірка

Кожне завдання має чотири етапи: збір, збереження RAW у files, екстракція повної картки, збереження `ad_car` у MongoDB (`jane.storage-mongodb` через `results-mongo`; актуальний стан — колекція `ad_car`, історія — `ad_car.history`). Природний ключ — `site + ad_id`, scope — ідентифікатор джерела (`autoria-cars` або `autos-rst`). Повторні спостереження оновлюють актуальний стан і залишають історію за правилами [Storage](../../services/storage/README.md). Записи `car_ad`, зібрані раніше в PostgreSQL, не переносяться.

`run` завершується успішно лише після запису сутностей обох джерел. `verify` перечитує receipt, перевіряє успішний стан запусків, точну версію та digest екстрактора, поля за схемою та активний шестигодинний розклад. Кожне спостереження має відповідний RAW: перевіряються його збережені байти за SHA-256 та повна відповідність полів після повторної екстракції. Порожній каталог є помилкою. Receipt містить перевірені поля, run ID та походження; секретів у ньому немає. Типовий receipt — `.jane/automarket-runtime.json`; файли в `evidence/` — записи попередніх запусків, вони не перезаписуються.

```powershell
uv run --all-packages pytest examples/tests/test_automarket.py examples/tests/test_automarket_navigation.py
uv run --all-packages python examples/automarket/setup_automarket.py verify --stack-file .jane/stack-jane-demo.json --receipt .jane/automarket-runtime.json
```

Публікація пакета з тим самим номером версії та іншим digest відхиляється. Для зміни коду або схем потрібна нова версія пакета.

## Черга запущеного стеку

Воркери оркестратора обробляють спільну чергу. Якщо великі попередні каталоги затримують обробку, можна додати обмежену кількість штатних воркерів без заміни контейнера API:

```powershell
docker build -f services/orchestrator/Dockerfile -t jane-automarket-orchestrator:local .
uv run python examples/automarket/queue_workers.py --stack-file .jane/stack-jane-demo.json --compose-root . --workers 2 --task-id ads-autoria --task-id ads-rst --image jane-automarket-orchestrator:local
```

Додатковий контейнер має окреме ім'я `<project>-automarket-priority-worker`, два потоки в наведеній команді, вимкнений scheduler і політику рестарту `unless-stopped`. Необов'язковий внутрішній фільтр `JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS` дозволяє йому споживати лише AUTO.RIA/RST зі спільної черги. Без фільтра штатний порядок загальної черги залишається чинним. Контейнер не має HTTP-портів і користується підключеннями стеку. Кількість потоків налаштовується через `--workers`; ліміт Handler Runtime залишається окремим обмеженням. Повторний виклик перевіряє project, кількість потоків, фільтр та образ перед використанням наявного контейнера. Воркер виконує етапи за конфігурацією завдань і не знає типів сутностей чи підключень сховищ: перехід на `ad_car` і `results-mongo` змінює лише документи завдань (`apply`), а не контейнер воркера.
