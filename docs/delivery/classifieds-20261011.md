# Збір оголошень із п'яти сайтів — 2026-10-11

## Статус і призначення

Статус: **прийнято незалежним рев'ю**. Для кожного з п'яти сайтів отримано реальні сутності та підтверджено всі видані поля за власними RAW-картками/JSON і PostgreSQL. Останні перевірені запуски дали 139 сутностей загалом; це кількість перевірених результатів запусків, а не загальна накопичена кількість записів сховища.

Налаштування охоплює OLX, AUTO.RIA, DIM.RIA, RIA.com та Shafa.ua. Користувач погодив Shafa.ua замість IZI.ua, який перенаправляє на Shafa. OLX збережено: HTTP-клієнт отримував 403, тоді як Chromium завантажував справжні оголошення.

## Зміни

- Десять пакетів у [packages](../../examples/classifieds/packages): екстрактор і правила для кожного сайта. Природний ключ `classified_ad` — `site` та `listing_id`; область ключа — джерело.
- П'ять незалежних джерел `classified-*` і завдань `classifieds-*`. Ланцюжок: збір → RAW у `raw-files`; екстракція → сутності в `results-pg`.
- Обов'язкові поля: сайт, ID оголошення, заголовок і URL. Ціна, валюта та місце додаються за наявності підтвердження у відповідній картці RAW.
- Для OLX — явний `fetch.transport=browser`: оригінальні байти документа через Chromium без JavaScript і підресурсів. Вихідні з'єднання проходять через існуючий EgressProxy. CDP зупиняє редирект до звернення до наступного URL; Fetcher перевіряє scope, robots і ліміти кожного переходу.
- Browser transport відхиляє POST та managed credentials. Облік бюджету включає повний отриманий документ, навіть якщо матеріал обрізано.
- Контракт правил доповнено необов'язковим параметром транспорту та прикладами. Оновлені споживачі: Web Collector, Registry, Assistant і згенеровані клієнти адміністративного інтерфейсу.
- Правила Shafa 1.0.1 дозволяють лише дві HTTPS головні сторінки, `/` та `/uk/`, щоб допустити реальний редирект між ними. Версія екстрактора — 1.0.0.
- [setup_classifieds.py](../../examples/classifieds/setup_classifieds.py) визначає актуальні порти через Docker, перевіряє архіви, зберігає checkpoints і повторно використовує тільки успішні збережені runtime tests з відповідним digest. Джерело створюється перед валідацією завдання.

## Налаштування

URL, бюджети та розклад зберігаються у [sites.json](../../examples/classifieds/sites.json). Збір обмежено вибраними каталогами; це не повний обхід усіх оголошень сайтів.

Розклад — 09:00 і 21:00, `Europe/Kyiv`, без перекриття запусків. Частота запитів до хоста — 0,5/с; паралельність до одного хоста — 1. Матеріал — до 5 MiB; бюджет запуску — 20 MiB. Shafa та OLX збирають одну початкову сторінку. Доступ і повні сторінки не включаються до Git.

Відтворювані команди наведені у [README](../../examples/classifieds/README.md). Зафіксовані пакети, документи джерел/завдань та фактичні runtime reports — [release.json](../../examples/classifieds/deployed/release.json).

## Перевірки компонентів

Незалежний рев'юер не був автором реалізації. Для Chromium використано ізольований Linux-контейнер із локальною копією checkout; production під час тестів не змінювався.

| Перевірка | Фактичний результат |
| --- | --- |
| Browser transport, попередній render_js і egress | `2 passed in 12.23s`; `53 passed, 2 deselected in 118.01s` — усі 55 випадків, без skip |
| Новий облік повного завантаження, budget, truncation/204 та redirects | `7 passed in 54.63s`, без skip |
| Наявні HTTP GET/POST після зміни обліку | `5 passed in 7.26s` |
| Тайм-аут browser page pool, cancellation і наступний реальний GET після звільнення слота | Незалежно `2 passed in 0.62s`; Chromium `1 passed in 7.45s`, без skip |
| Налаштування, відновлення та незалежна перевірка полів | `66 passed in 2.46s`; незалежно OLX/RIA, усі п'ять fixtures і JSON PINIA — `30 passed, 36 deselected in 0.44s` |
| П'ять екстракторів у запущеному Handler Runtime | Для кожного `2 passed, 0 failed`; фактичні звіти збережено в Registry |
| Collector ruff / mypy | `All checks passed!`; `Success: no issues found in 23 source files` |
| Контракти, незалежний guardian | lint PASS; compatibility — 0 breaking changes, 0 warnings; OpenAPI diff — без змін API |
| Згенеровані адміністративні клієнти | `gen-api: 10 files up to date` |
| Адміністративні клієнти | TypeScript typecheck і production build PASS; згенеровані клієнти включено в прийнятий компонент `5246407` для спільної інтеграції адмінки |
| Нові пакети, gitleaks | `no leaks found` |

Критичні перевірки використовують реальний Chromium і лічильники тестового HTTP-сервера: заборонений redirect target отримав нуль запитів, дозволений — один; після вичерпання бюджету наступний seed не завантажувався.

Основні команди:

```powershell
python -m pytest services/web-collector/tests/test_browser_transport.py services/web-collector/tests/test_render_js.py services/web-collector/tests/test_egress_policy.py
python -m pytest examples/tests/test_classifieds.py -q
python examples/classifieds/setup_classifieds.py check
node web/admin/scripts/gen-api.mjs --check
```

Для Linux review встановлено pytest, pytest-asyncio і psutil; `JANE_WEB_COLLECTOR_CONTRACTS_DIR` вказував на контракти checkout, `JANE_WEB_COLLECTOR_HOST=127.0.0.1`. Chromium відповідав версії Playwright production image. Тимчасові review-контейнери й image після тестів прибрано.

## Реальна перевірка

Перевірка кожного запуску повинна підтвердити не лише `succeeded`, а й ненульову кількість сутностей, SHA-256 збереженого RAW, observation lineage, кожне видане поле та стан PostgreSQL. Ціна/валюта/місце мають походити з тієї самої картки або JSON-об'єкта, що й ID, заголовок та URL.

Перші п'ять запусків перервалися після перевідтворення сервісів. Фактичні невдалі звіти збережено в [attempt1](../../examples/classifieds/deployed/attempt1). Наступна спроба [attempt2](../../examples/classifieds/deployed/attempt2) отримала матеріали AUTO.RIA, DIM.RIA і RIA.com, але downstream items не отримали спроби до таймауту. Shafa повернув нуль через redirect scope; правила виправлено до 1.0.1.

Незалежна діагностика підтвердила початкову глобальну FIFO чергу Orchestrator. Після узгодженого розгортання фактично імпортований сервіс використовує `run_round_robin`, 12 workers та коротке очікування `idempotency_in_progress` 1000 ms. Це дозволило завершити DIM.RIA і Shafa.

Незалежний рев'юер повторно перевірив чотири сайти через актуальні API. О 09:00 `Europe/Kyiv` розклад самостійно створив ці запуски (`trigger: schedule`); вони завершилися за 26–33 s. Для кожного — один RAW із правильним SHA-256, observation lineage, відповідність усіх виданих полів власній картці/JSON та поточному стану PostgreSQL; `verified: true`, помилок немає.

| Сайт | Запуск | Перевірені сутності |
| --- | --- | --- |
| AUTO.RIA | `run_01M4MRQXDASCK15AMVRNCHV8XK` | 21 |
| DIM.RIA | `run_01M4MRQXDWWPJESKN1KDENDJ53` | 22 |
| RIA.com | `run_01M4MRQXE1Z4SXDZ25SZ3YGDYS` | 20 |
| Shafa.ua | `run_01M4MRQXF6DX6PHGPN1ASR5EZ2` | 24 |
| OLX | `run_01M4MT7Q936YWM5MF2Z34R3P9B` | 52 |

RIA.com потребував виправлення саме незалежної перевірки: суцільний текст картки з'єднував число моделі з ціною. Екстрактор і PostgreSQL уже містили правильні значення. Тепер перевірка читає лише `span.price.js-price` всередині власного `adv_<listing_id>`; дев'ять нових regression cases відхиляють неправильні поля, суму/валюту та ціну сусідньої картки. Опубліковані архіви залишилися байтово незмінними.

AUTO.RIA та RIA.com у третій спробі отримали по одному матеріалу, але `/materials` відповідав за 31–35 секунд, collection lease втрачався та відновлювався. Run досягнув бюджету 300 секунд. Діагностика власника Collector підтвердила синхронний sitemap commit до 60000 URL і сканування всієї frontier на heartbeat. Прийнято та розгорнуто спільне виправлення `1d1420f`: короткі порції seed transactions, індексовані лічильники та продовження budget без масового UPDATE; continuation і всі черги збережено. Heartbeat 500 ms обмежує порції запису приблизно до 125 ms; у контрольному вимірюванні `/v1/health` відповів за 1,031 s, `/materials` — за 0,812–1,953 s. Подальші живі запуски AUTO.RIA та RIA.com завершилися успішно.

OLX `run_01M4MQXJ08Z5C001W85KVWE90H` досягнув deadline без матеріалів. Native Chromium із того самого образу, user agent, заголовків і effective limits отримав справжній каталог HTTP 200 за 4,694 s; robots дозволяв URL. Scheduled запуск о 09:00 завершився порожнім після трьох HTTP timeout; його негативний звіт збережено в [attempt6](../../examples/classifieds/deployed/attempt6). Shared host slot уже надано, backoff/waiter відсутні: затримка виникала далі всередині браузера.

Прийнято та розгорнуто guard `15bb32d`: очікування browser page pool обмежене наявним `request_timeout_ms`, warning містить лише host і ліміт, cancellation не втрачає slot. Окреме виправлення типізації assertions `991d539` зберігає точні перевірки. Driver start, `render_js`, robots, outbound policy та max_pages зберігають попередню поведінку.

Після узгодженого оновлення Collector о 06:25:50 UTC реальний запуск OLX завершився за 13 s: один RAW і 52 сутності. Незалежний рев'юер звірив кожну власну `l-card`, title/URL, `ad-price`, location/date та PostgreSQL. SHA-256 RAW — `cef34300cea0503a00ae9d1a963ad28116647df043c885e687a32788a8ff90a2`. Фінальний CLI звіт має `verified: true`, `checked_entities: 52`, `errors: []`.

Уточнено автоматичну перевірку OLX: вона читає ціну лише з власного `p[data-testid=ad-price]`, а DOM evidence виключає невидимий style/script/svg. Число моделі більше не з'єднується з ціною; CSS не перевищує текстовий cap5000. `RawNode.text()` для JSON scripts збережено. Додано 13 regression cases, включно з хибними полями, ціною сусідньої картки та прихованими числами; опубліковані пакети не змінювалися.

## Поточне розгортання

Collector — `jane-demo-classifieds-browser-guard:15bb32d-947803d4`, image `sha256:82ad1d201b6656a5f36d7f1d3c4358da19f5e9adf5166a37718c95f67154c786`. Образ походить від точного поточного operations image `947803d4` і додає лише прийнятий `render.py`. Після оновлення пройшли всі 25 перевірок: ENV, порти, томи, мережі, group_add, healthcheck, команда, користувач, shm та решта Collector/Discovery/Kit/schema збережені. Доказ — [collector-rollout.json](../../examples/classifieds/deployed/collector-rollout.json).

Фінальний [runtime.json](../../examples/classifieds/deployed/runtime.json) містить актуальні image IDs, порти, source/plugin hashes та canonical schemas трьох споживачів. П'ять файлів Collector і два Discovery збігаються з checkout; operations Kit збережений із окремою provenance. Це знімок переліку компонентів, а не твердження про тотожність цілого образу Git HEAD. Проби читають файли й дозволені поля API/ENV без ініціалізації Settings/SQLite. Непублікований старий Orchestrator залишений окремим записом.

Під одночасним повним обходом великих сторонніх каталогів спостерігалися затримки API та короткі переходи Docker health в unhealthy; наступний snapshot підтвердив healthy. Окремий fairness/sitemap patch власника каталогів ще проходить рев'ю й не включений до цього прийнятого результату. Успішні запуски та отримані сутності підтверджені незалежно від Docker health marker.

## GitHub CI

База `main` перед фінальною публікацією — `cad468925e8cc716b26d9d6e49ed76f49fa615f7`. Її [CI 38116615586](https://github.com/sql-monk/Jane/actions/runs/38116615586) завершився успішно: 13 required jobs, включно з e2e; manual-only limits job очікувано пропущено. Це перевірка бази, а не нових файлів оголошень. Новий результат узгоджується зі спільною інтеграцією адмінки для одного CI на точному фінальному SHA; до його завершення загальний CI нової реалізації не оголошується успішним.

## Межі та повторний запуск

Зміна опублікованого архіву потребує нової версії пакета. Порожній результат, помилка збору або розбіжність із RAW/PG дають ненульовий exit code. Повторний запуск використовує новий run ID; збережені схвалені архіви та успішні runtime tests не запускаються повторно без причини.

Зміни зроблено в окремому worktree, щоб зберегти незавершену переробку документації основного checkout. Публікація в `main` виконується координатором звичайним fast-forward push після перевірки поточного remote head; force push не використовується.
