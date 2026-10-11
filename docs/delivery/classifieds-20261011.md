# Збір оголошень із п'яти сайтів — 2026-10-11

## Статус і призначення

Статус: **перевірка запущеної версії триває**. Пакети та тести компонентів перевірені, але прийняття потребує реальних сутностей для кожного сайта, зіставлених зі збереженими RAW і PostgreSQL.

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
| Налаштування, відновлення та незалежна перевірка полів | `44 passed in 3.41s` |
| П'ять екстракторів у запущеному Handler Runtime | Для кожного `2 passed, 0 failed`; фактичні звіти збережено в Registry |
| Collector ruff / mypy | `All checks passed!`; `Success: no issues found in 23 source files` |
| Контракти, незалежний guardian | lint PASS; compatibility — 0 breaking changes, 0 warnings; OpenAPI diff — без змін API |
| Згенеровані адміністративні клієнти | `gen-api: 10 files up to date` |
| Адміністративний інтерфейс | TypeScript typecheck і production build PASS; HTTP 200 із bundle `index-BCIqREjx.js` |
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

Перші п'ять запусків перервалися після перевідтворення сервісів. Фактичні невдалі звіти збережено в [attempt1](../../examples/classifieds/deployed/attempt1). Нові AUTO.RIA, DIM.RIA і RIA.com отримали матеріали, але їхні downstream items не отримали жодної спроби до таймауту. Shafa повернув нуль через redirect scope; правила виправлено до 1.0.1.

Незалежна діагностика підтвердила у фактично імпортованому основному Orchestrator глобальне `ORDER BY i.seq`, 12 workers та очікування `idempotency_in_progress` до 120000 ms. Давній backlog перешкоджає обробці нових завдань. Узгоджується спільне розгортання справедливої черги із чатом новин; чужі задачі, стани й дані не скидаються.

## GitHub CI

Початковий `main` — `0b554fce30bce5aa7def84d351575e23862f66b8`. Його [CI 38105687057](https://github.com/sql-monk/Jane/actions/runs/38105687057) уже завершився невдало на gitleaks; lint, types і contracts-compat пройшли, залежні jobs були пропущені. Цей запуск не є перевіркою нової реалізації. Результат CI фінального commit потрібно перевірити окремо.

## Межі та повторний запуск

Зміна опублікованого архіву потребує нової версії пакета. Порожній результат, помилка збору або розбіжність із RAW/PG дають ненульовий exit code. Повторний запуск використовує новий run ID; збережені схвалені архіви та успішні runtime tests не запускаються повторно без причини.

Зміни зроблено в окремому worktree, щоб зберегти незавершену переробку документації основного checkout. Після прийняття потрібні звичайний fast-forward push у `main` та перевірка фактичного SHA, без force push.
