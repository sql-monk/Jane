# WP-14: періодичний каталог авторинку

Стан: review; фінальний runtime receipt та інтеграція спеціального воркера ще готуються. Базова ревізія: `0b554fce30bce5aa7def84d351575e23862f66b8`.

## Результат

За запитом користувача підготовлено детальний каталог AUTO.RIA та RST.ua з інтервалом шість годин. Avtobazar.ua перевірено на головній, robots та відомих адресах оголошень: перенаправлення на новинний Autocentre.ua. Користувач відхилив InfoCar; це джерело позначається недоступним, його попереднє завдання вимикається.

Пакети `autos.autoria-ad-page`, `autos.autoria-rules`, `autos.rst-car-ads`, `autos.rst-rules` підготовлено у версії 1.1.0; початковий `autos.autoria-search-page@1.0.0` збережено. Ідентичність сутності `car_ad` (`site + ad_id`, scope джерела) збережена. Нові необов'язкові поля доповнюють транспорт характеристиками, оснащенням, фото та видимими відомостями про стан. Значення, яких немає на сторінці, пропускаються. Суперечливі заяви джерела зберігаються окремо.

Артефакти: [приклад та команди](../../../examples/automarket/README.md), [AUTO.RIA](../../../examples/automarket/evidence/autoria.json), [RST](../../../examples/automarket/evidence/rst.json), [недоступний Avtobazar](../../../examples/automarket/evidence/avtobazar-unavailable.json).

## Виконавці та власність

AUTO.RIA реалізовано субагентом `autoria_implementation` в окремому checkout, RST та перевірку Avtobazar — `marketplace_sampling`. Координатор реалізував налаштування, збереження й перевірку каталогів. Кодовий reviewer `provisioning_review` виявив та перевірив виправлення трьох шляхів хибного успіху: неактивний розклад, незавершений запуск, історичний RAW замість нового спостереження.

Змінено лише `examples/automarket/**`, `examples/tests/test_automarket.py` та цей звіт. Контракти API не змінювалися. Вихідний checkout із незавершеною перебудовою документації збережено.

## Перевірки

```powershell
uv run python examples/automarket/setup_automarket.py check
uv run pytest examples/tests/test_automarket.py -q
uv run ruff check examples/automarket examples/tests/test_automarket.py
uv run ruff format --check examples/automarket examples/tests/test_automarket.py
uv run mypy examples/jane_examples.py examples/automarket examples/tests/test_automarket.py --show-error-codes
gitleaks dir examples/automarket --redact --no-banner
python .claude/hooks/jane_wp.py check-diff 0b554fce30bce5aa7def84d351575e23862f66b8 --wp 14
```

Фактичний вивід поточного етапу:

```text
automarket: 5 packages and both source/task documents verified
12 passed in 9.46s
All checks passed!
14 files already formatted
Success: no issues found in 12 source files
scanned ~626595 bytes (626.59 KB)
no leaks found
WP-14: 77 changed file(s), 0 outside ownership
```

Незалежне рев'ю пакетів повторило 12 fixtures AUTO.RIA, 11 RST, перевірку SHA та по три порівняння вихідних сторінок. Авторські прогони runtime CLI використовували довірений subprocess; остаточна публікація виконує тести через справжній запущений Handler Runtime.

## Runtime та обмеження

Стек `jane-demo`; чинні підключення `raw-files` і `results-pg` не перезаписуються. Публікація використовує незмінні digest, тестування перед затвердженням та ETag для оновлення конфігурацій. URL локальних контейнерів уточнюються через Docker після зміни опублікованих портів. Повтор запиту після обриву HTTP обмежений і зберігає Idempotency-Key.

Початковий обхід обмежено одинадцятьма сторінками та глибиною один. Регулярний інкрементальний обхід запитує максимум 120 сторінок і глибину п'ять; платформа та сайт можуть звузити ці ліміти. Це не повний одномоментний знімок усього автобазару.

У спільній черзі виявлено понад 700 операцій екстракції перед новими запусками. Для штатного окремого воркера готується необов'язковий фільтр завдань WP-09; загальні воркери продовжують обробляти інші каталоги. Чужі завдання не скасовуються.

## Запити до інших власників

WP-09: необов'язковий внутрішній фільтр `task_ids` для спеціального consumer. Новий API-контракт не потрібен. Приймання WP-14 залежить від успішних нових запусків обох джерел і збереженого runtime receipt.

На базовій ревізії GitHub CI `38105687057` вже був невдалим через шість спрацювань gitleaks у згенерованій документації з історичного коміту `dd99d227`; ці файли поза поточним пакетом робіт. Перевірка власних артефактів витоків не виявила.
