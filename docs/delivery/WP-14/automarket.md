# WP-14: періодичний каталог авторинку

Стан: accepted, незалежний WP-reviewer прийняв код `13294ee` та живі докази 20/20 сутностей. WP-09 accepted та застосований. Базова ревізія: `0b554fce30bce5aa7def84d351575e23862f66b8`.

## Результат

За запитом користувача підготовлено детальний каталог AUTO.RIA та RST.ua з інтервалом шість годин. Avtobazar.ua перевірено на головній, robots та відомих адресах оголошень: перенаправлення на новинний Autocentre.ua. Користувач відхилив InfoCar; це джерело позначається недоступним, його попереднє завдання вимикається.

Пакети AUTO.RIA ad/rules опубліковано у версії 1.1.1, RST ad/rules — 1.1.0; початковий `autos.autoria-search-page@1.0.0` збережено. Нові версії мають походження `llm`. Помилково опубліковані AUTO.RIA 1.1.0 позначено deprecated після GET-перевірки відсутності споживачів; їхні архіви не змінено. Ідентичність `car_ad` (`site + ad_id`, scope джерела) збережена. Необов'язкові поля доповнюють транспорт характеристиками, оснащенням, фото та видимими відомостями про стан. Відсутні значення пропускаються; суперечливі заяви джерела зберігаються окремо.

Артефакти: [приклад та команди](../../../examples/automarket/README.md), [AUTO.RIA](../../../examples/automarket/evidence/autoria.json), [RST](../../../examples/automarket/evidence/rst.json), [недоступний Avtobazar](../../../examples/automarket/evidence/avtobazar-unavailable.json), [20 перевірених сутностей та RAW](../../../examples/automarket/evidence/runtime.json), [активні процеси та scheduler](../../../examples/automarket/evidence/runtime-worker.json), [регресія фактичної навігації RST](../../../examples/tests/test_automarket_navigation.py).

## Виконавці та власність

AUTO.RIA реалізовано субагентом `autoria_implementation` в окремому checkout, RST та перевірку Avtobazar — `marketplace_sampling`. Координатор реалізував налаштування, збереження й перевірку каталогів. Кодовий reviewer `provisioning_review` виявив та перевірив виправлення трьох шляхів хибного успіху: неактивний розклад, незавершений запуск, історичний RAW замість нового спостереження.

Змінено лише `examples/automarket/**`, `examples/tests/test_automarket.py` та цей звіт. Контракти API не змінювалися. Вихідний checkout із незавершеною перебудовою документації збережено.

## Перевірки

```powershell
uv run python examples/automarket/setup_automarket.py check
uv run pytest examples/tests/test_automarket.py examples/tests/test_automarket_navigation.py -q
uv run ruff check examples/automarket examples/tests/test_automarket.py examples/tests/test_automarket_navigation.py
uv run ruff format --check examples/automarket examples/tests/test_automarket.py examples/tests/test_automarket_navigation.py
uv run mypy examples/jane_examples.py examples/automarket examples/tests/test_automarket.py examples/tests/test_automarket_navigation.py --show-error-codes
gitleaks dir examples/automarket --redact --no-banner
```

Фактичний вивід поточного етапу:

```text
automarket: 5 packages and both source/task documents verified
21 passed in 8.38s
All checks passed!
15 files already formatted
Success: no issues found in 13 source files
scanned ~821280 bytes (821.28 KB)
no leaks found
```

Власність перевірено до координаторського об'єднання командою `python .claude/hooks/jane_wp.py check-diff 0b554fce30bce5aa7def84d351575e23862f66b8 --wp <номер>` у відповідних checkout: WP-14 на `3e660a3` — 78 changed files, 0 outside ownership; WP-09 на `28c2291` — 5 changed files, 0 outside ownership. Об'єднаний checkout додатково містить прийнятий WP-09 та окреме координаторське CI-виправлення.

Незалежне рев'ю пакетів повторило 12 fixtures AUTO.RIA, 11 RST, SHA та по три порівняння вихідних сторінок. Реальні HTTP test-runs у Handler Runtime: AUTO.RIA ad 9 passed/0 failed, search 3/0, RST ad 11/0. До затвердження звіти записано в Registry. GET підтвердив `auto_changes_allowed=false` для чотирьох змінених пакетів; тимчасовий дозвіл upload відновлюється також після обриву відповіді PATCH.

## Runtime та обмеження

Стек `jane-demo`; чинні підключення `raw-files` і `results-pg` не перезаписуються. Публікація використовує незмінні digest, тестування перед затвердженням та ETag для оновлення конфігурацій. URL локальних контейнерів уточнюються через Docker після зміни опублікованих портів. Повтор запиту після обриву HTTP обмежений і зберігає Idempotency-Key.

Початковий обхід обмежено одинадцятьма сторінками та глибиною один. Для повторної перевірки після недавнього збору `RunRequest.limits.crawl.revisit_interval_seconds=0` змінює лише цей запуск. Перший RST run мав `discovered=21`, `not_modified=20`, `errors=0` і лише індекс: перевірка відхилила нуль нових сутностей. RAW-regression підтвердила справну навігацію. Повторний запуск отримав 11 матеріалів та записав 10 детальних оголошень. Регулярний інкрементальний обхід запитує максимум 120 сторінок і глибину п'ять; платформа та сайт можуть звузити ліміти. Це не повний одномоментний знімок усього автобазару.

Необов'язковий фільтр завдань [WP-09](../WP-09/automarket-worker.md) прийнято незалежно. `jane-demo-automarket-priority-worker` працює з двома потоками, allowlist `ads-autoria/ads-rst`, без scheduler/HTTP та з restart `unless-stopped`. Образ `jane-automarket-orchestrator:e595c1c` має ID `sha256:6ed92b88115eb6ef03480473f37e1fcba599d9c23aa78453dfac98a5f500dec2`. Основний scheduler увімкнений. Початковий наш загальний consumer із шістьма потоками зупинено. Спільні backend-контейнери не замінювалися, чужі завдання не скасовувалися.

| Джерело | Успішний run | Нових сутностей | SHA та повний replay RAW | Інтервал |
|---|---|---:|---:|---:|
| AUTO.RIA | `run_01M4MMPS6G389RC254QTS9J7BC` | 10 | 10 | 21600 с |
| RST.ua | `run_01M4MN6R1YDVWBWYNTP61KQ0QM` | 10 | 10 | 21600 с |

Верифікація відбулася 2026-10-11 о 04:58 UTC. Обидва run мають 11 матеріалів, із них одна сторінка індексу не є оголошенням. Сховище має 111/112 RAW-об'єктів у відповідних scopes, включно з попередніми обходами; приймання перевіряє тільки 10 нових спостережень кожного run. Для кожного запису перевірено JSON Schema, точний extractor digest, відповідний observation ID, збережені байти SHA-256 та повну рівність полів повторної екстракції.

Попередні RST test-job втратили lease після перевідтворення Handler Runtime іншими паралельними розгортаннями. Обмежений повтор застосовується тільки до термінального `failed` з `error.retryable=true`, з детермінованим наступним ключем; assertions не повторюються. Спільний backend залишено стабільним на час узгодженої перевірки інших каталогів.

## Запити до інших власників

Запит до WP-09 закрито accepted-кодом та його живим застосуванням. Нових API-контрактів немає. Фінальне незалежне приймання перечитало через API всі 20 сутностей та RAW, звірило exact digest, поля replay, розклади й стан Avtobazar; verdict accepted. Вузький незалежний прогін нових сценаріїв — 6 passed; lint/types/secret scan також пройшли.

На базовій ревізії CI `38105687057` був невдалим через шість спрацювань gitleaks у згенерованій документації історичного `dd99d227`. Координатор додав лише шість точних fingerprint у `.gitleaksignore`: explorer звірив значення з публічними ключами ідемпотентності контрактних прикладів. Нові коміти й значення продовжують скануватися. `gitleaks git --log-opts='dd99d227^..dd99d227' --redact --no-banner`: 1 commit, 17.15 MB, no leaks found. Власні артефакти також без витоків. Це окреме координаторське CI-виправлення; незавершені зміни документації основного checkout не включено.
