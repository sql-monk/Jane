# Перевірка щогодинного моніторингу новин

На 2026-10-11 у чинному `jane-demo` налаштовано 12 увімкнених джерел: 8 сайтів і 4 публічні Telegram-канали. Для кожного отримано реальний матеріал, виконано LLM-аналіз, перевірено цитати й збережено сутності; незалежне читання Storage API підтвердило всі 12 source scopes. Зафіксовано 23 перевірені статті/дописи. Джерела й завдання належать групі `news-analysis`; розклад — `3600` секунд, `Europe/Kyiv`, overlap `skip`.

Докази: [verification.live.json](verification.live.json) містить SHA-256 матеріалів, invocation IDs, версії пакетів і підтвердження записів; [verification.runtime.json](verification.runtime.json) — поточні task refs, розклад, сутності, статуси запусків і хеші реально імпортованих модулів. RAW збережено в `raw-files`, результати — через керований `results-pg`. Секрети, повний HTML і повні цитати до Git-звіту не входять.

## Джерела і збережені сутності

| Джерело | Регіон | Транспорт | Перевірених записів |
|---|---|---|---:|
| Українська правда | Україна | RSS + статті | 1 |
| Укрінформ | Україна | RSS + статті | 1 |
| BBC News | Європа | RSS + статті | 2 |
| The Guardian | Європа | RSS + статті | 1 |
| NPR | США | RSS + статті | 1 |
| ABC News | США | RSS + статті | 1 |
| РИА Новости | Росія | RSS + статті | 4 |
| RT на русском | Росія | RSS + статті | 3 |
| Суспільне Новини | Україна | Публічна Telegram-стрічка | 4 |
| DW Главное | Європа | Публічна Telegram-стрічка | 1 |
| Голос Америки | США | Публічна Telegram-стрічка | 3 |
| ТАСС | Росія | Публічна Telegram-стрічка | 1 |

Для кожного запису `evidence_validation=verified`, є сутності та авторське ставлення до них. RSS/статті й публічні стрічки перевірено на реальному HTTP зі штатними TLS і robots; сертифікати не обходилися. Telegram-парсер відділяє власний допис від reply, preview, footer та інших повідомлень. Короткі підготовчі samples — [samples/web](samples/web) і [samples/telegram](samples/telegram).

## Реальна спільна подія

[BBC](https://www.bbc.co.uk/news/articles/cw33x4y8k82no) і [NPR](https://www.npr.org/2026/10/10/g-s1-147682/attack-on-riyadh-airport-killed-12-people-and-wounded-over-300-more-saudi-authorities-say) отримали однаковий збережений `event_id`:

```text
news-event-813fbcab5cfd8bc2e1993a4657e05170
date: 2026-10-10
action: attack
object: King Khalid International Airport
city: Riyadh
country: Saudi Arabia
```

Дату підтверджено дослівним посиланням на Saturday та датою публікації основної статті. Головний названий об'єкт збігається; уточнення про термінали залишаються в описі. Читання Storage API підтвердило обидві `news_article` та спільну `news_event`.

BBC проаналізовано профілем `cheap`, фактична оцінка ідентичності `0.85`. Для NPR використано окремий незмінний validation-пакет із тією самою production-схемою та інструкціями, але профілем `default` (`claude-sonnet-5-5`), оцінка `0.78`. Штатні щогодинні завдання використовують `cheap`. Попередній cheap-аналіз NPR пропустив дату і чесно залишився `ungrouped`; цей доказ не означає, що cheap завжди об'єднає таку пару.

Новинні завдання явно налаштовують евристичний поріг `0.75`; типовий поріг нормалізатора лишається `0.9`. Оцінки моделі не підвищувалися та не трактуються як виміряна точність. Повний конкретний ключ, цитати, походження дати й перевірка явного часу потрібні незалежно від порога. Невідома дата, загальний об'єкт чи неоднозначна подія залишаються `ungrouped`.

Повторний provider-виклик заради оцінки не робився. Для свіжої перевірки NPR повторно використано справжній LLM-результат лише після точного збігу canonical JSON bytes усіх підготовлених полів статті. HTML мав інший RAW SHA через змінні атрибути; receipt зберігає обидва RAW SHA, початкові invocation/observation та явне `llm_called_on_fresh_raw=false`. Новий матеріал і цитати повторно перевірено, запис прив'язано до справжнього нового спостереження. Поля події, дата й оцінка не редагувалися вручну. Сукупна вартість вибраних validation-викликів — `$0.1493741`.

## Orchestrator і розклад

| Запуск | Run ID | Тригер | Результат |
|---|---|---|---|
| BBC, одна стаття | `run_01M4MJHZNP88WTS8C6EQPBBPBA` | manual | succeeded |
| Суспільне, публічна стрічка | `run_01M4MJHZQMGN2FGWCSSVXARA07` | manual | succeeded |
| RT, звичайний RSS | `run_01M4MKNJHHCK7RP5TVWV4VGK0Q` | manual | succeeded; 3 матеріали на кожному етапі |
| РИА Новости | `run_01M4MKRSD091S7RVYD431YDSDT` | schedule | succeeded |
| Голос Америки | `run_01M4MKRSEHK71WKC9TM47XHNAR` | schedule | succeeded |
| ТАСС після виправлення reply | `run_01M4MQ6F4GP8Z5XKG7K3E7SW6K` | schedule | succeeded; 3 нові перевірені дописи |

Ці запуски пройшли `collect → store-raw / prepare → analyse → verify → store-news`. Це окремі докази доставки через Orchestrator і фактичного scheduled trigger. Статуси всіх перевірених запусків наведені в runtime receipt. Старі scheduled DW і ТАСС завершилися помилками; вони не позначені успішними після виправлень. Пізніші прямі API-прогони перевірили й зберегли результати цих джерел; усі 12 поточних завдань увімкнено зі свіжими пакетами.

Окремий [verification.tass-postfix.json](verification.tass-postfix.json) підтверджує справжній наступний щогодинний запуск ТАСС о `2026-10-11T05:33:00Z`: пакети `prepare@1.0.1`, `analyse@1.1.1`, `verify@1.1.2`, усі шість етапів завершені. Storage API повернув три нові дописи `399752/399753/399754` з `verified`, які належать саме observation цього запуску; ТАСС має вже чотири перевірені записи. Стан початкового snapshot із 23 новинами збережено без переписування історичного часу. Спроба ручного запуску отримала `409` через активний scheduled run і не створила дубль.

## Поточні пакети і розгортання

Task refs: `news.article-analysis@1.1.1`, `news.article-normalize@1.1.2`, `news.web-article@1.0.2`, `news.telegram-public-posts@1.0.1`; усі 18 потрібних пакетів опубліковані й approved. Точні digest — у [config.lock.json](config.lock.json). Історичні receipt зберігають фактичні версії власних викликів. Локальні `.gitattributes` зберігають незмінні байти опублікованих package archives на Windows і Linux.

У чинному Handler Runtime передається прикріплений оригінальний Material до transform; LLM приймає його разом із сутностями. Orchestrator поєднує `run_round_robin` зі свіжим `task_ids` allowlist з main: фільтруються обидві фази fair claim, feed, scheduler і reaper. Усередині запуску лишається FIFO; leases, delivery keys і ліміти паралельності збережені.

Імпортовані параметри: 12 Orchestrator workers, wait/retry `1000/5000` мс, Handler Runtime 8 jobs, Web Collector 32 jobs із timeout 4 години. Оновлення розгорнуті поверх поточних образів зі збереженням ports/env; точні SHA-256 та health на момент спостереження — у runtime receipt. Розгортання узгоджено з іншими активними задачами Jane. Їхні collector/priority workers, дані та jobs збережено. Спільний Collector під навантаженням каталогів мав event-loop затримки; його performance-оновлення координується власниками Collector окремо.

## Перевірки коду

Координатор виконав завершальний news-набір після оновлень Telegram/нормалізатора:

```powershell
uv run --all-packages pytest examples/news/test_analysis.py examples/news/test_web_article.py examples/news/test_telegram_sources.py examples/news/test_web_sources.py -q
```

```text
106 passed in 2.15s
```

Після додавання перевірок повторного використання аналізу окремий analysis-набір: `85 passed in 0.73s`; незалежний reviewer: `85 passed in 1.20s`. Завершальна незалежна перевірка тією самою news-командою: `114 passed in 1.19s`. Нормалізатор перевірено через справжній `jane_storage.merge`: grouped → ungrouped явно очищує старий `event_id`, regroup відновлює його. Telegram package runtime: `6 passed, 0 failed`; pytest: `9 passed`.

```powershell
uv run --all-packages pytest services/orchestrator/tests/test_item_queue_ordering.py services/orchestrator/tests/test_task_workers.py -q -x
```

```text
19 passed in 63.92s
Independent reviewer: 19 passed in 73.19s
```

Перевірено великий старий backlog, кілька workers, паралельність, retry keys, прострочені leases, блоковані рядки й task allowlist у FIFO/fair. Раніше незалежний component-прогін news + LLM + Handler Runtime без integration-маркерів дав `102 passed, 17 deselected, 13 warnings in 15.82s`; integration-тести не приписуються цій команді. Ruff/format, mypy змінених компонентів і `git diff --check` пройшли. `setup_news.py export` фактично повернув `Validated 18 packages and 12 sources/tasks`.

## Межі підтвердження та відтворення

`verified` підтверджує відповідність цитат конкретному оригіналу, формат і перевірки атрибуції. Правдивість фактів у самому джерелі автоматично не доводиться. Семантичні оцінки й canonical names формує LLM; точне групування може пропускати той самий інфопривід за різних формулювань. За сумнівів результат зберігається без event ID.

Стартові ліміти — до 3 статей або текстових Telegram-дописів на джерело за запуск; медіадописи без тексту пропускаються. Публічний `t.me/s` дає видиму поточну стрічку, без приватних каналів та повної історії. Діє чинний платформний LLM-бюджет; його не збільшували.

Команди налаштування, перевірки й діагностики — у [README](README.md#налаштування-та-запуск). `.jane/stack-jane-demo.json`, приватні checkpoints і deployment receipts лишаються локальними. Для відтворення використовуйте Git-байти пакетів і точні refs із config lock, а не змінюйте вже опубліковану версію. Перевірено точний збіг усіх 63 package files у Git index із опублікованими робочими байтами. Gitleaks новинного каталогу: `no leaks found`. Статична перевірка Markdown: 35 посилань, по одному H1, закриті позначені fenced blocks, помилок немає; фактичний рендер не є доказом цього звіту. Незалежний reviewer прийняв код і живі докази.
