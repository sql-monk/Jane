# WP-27 — повний CI та розгортання адмінки

Користувач 2026-10-11 доручив виконати повний CI гілки, виправити збої, після успіху розгорнути можливості в робочий стек і оновити `main` на GitHub. Поточна перевірювана ревізія — `ada35865a3270e4ae85c945b2b29c2222380260f`.

## CI та виправлення

| Запуск | Ревізія | Результат |
|---|---|---|
| [38094143658](https://github.com/sql-monk/Jane/actions/runs/38094143658) | `7307fc3` | Збій strict mypy у тесті storage та допоміжному Telegram-скрипті |
| [38094271140](https://github.com/sql-monk/Jane/actions/runs/38094271140) | `fe9d5c5` | 13 завдань успішні; e2e: 1 failed, 78 passed |
| [38096339188](https://github.com/sql-monk/Jane/actions/runs/38096339188) | `ada3586` | Усі 14 завдань успішні; e2e: 79 passed |

Виправлено типи тесту storage без послаблення assertions (`fe9d5c5`); незалежне рев’ю — accepted. Telethon у допоміжному скрипті завантажується через `importlib`, як опційний backend (`a309b14`): mypy scripts/infra — 8 source files без помилок, ruff clean, `--help` exit 0. Реальний Telegram-вхід не виконувався.

Детермінований збій e2e спричинила застаріла позитивна вибірка S-M2-06: актуальний асистент дотримується переданого `seed_list`, а попередня реалізація доповнювала його sitemap/feed/recursive. Сім URL давали один news-list та по два приклади інших типів; confidence дорівнював `0.783673`, нижче незмінного порога `0.8`. До fixture додано наявну `/news/page/2/`; по два приклади всіх чотирьох типів дають `0.9125`. Assertions посилено, додано перевірку восьми матеріалів (`ada3586`); production-код і поріг достатності не змінені. Незалежне рев’ю — accepted; ruff, mypy файлу й diff-check — exit 0.

Merge актуального `main` (`91876d1`) зберіг нове оформлення, навігацію «Сховища» та візуальний редактор. Незалежне рев’ю — accepted; після merge локально **78 unit passed** і typecheck exit 0.

## Остаточне підтвердження CI

Повний GitHub Actions run перевірив `ada35865a3270e4ae85c945b2b29c2222380260f`: **14/14 success**. Успішні lint, web, unit, contracts-compat, contract, isolation, stack, mandatory e2e, web-mock-e2e, limits і чотири адаптери (SQL Server, MongoDB, MinIO, S3).

Фактичний вивід відповідних jobs:

```text
unit: 1191 passed, 5 skipped, 417 deselected, 33 warnings in 379.21s (0:06:19)
offline: 101 passed, 3 warnings in 16.66s
stack: 300 passed, 1313 deselected, 10 warnings in 272.42s (0:04:32)
web-mock-e2e: 20 skipped; 58 passed (1.0m)
e2e: 79 passed in 1565.25s (0:26:05)
```

Mandatory e2e не має пропущених сценаріїв; пропуски інших профілів не видаються за виконані перевірки. Останній unit skip — локальна наявність gitleaks у тесті hooks; окремий CI lint завершився успішно.

## Розгортання

Розгорнуто 2026-10-11 у `jane-demo`: [адмінка](http://127.0.0.1:54347/storages). Джерело storage та статичної адмінки — перевірена ревізія `ada3586`. Образ `jane-demo-storage:latest` має revision label з повним SHA; manifest digest — `sha256:36505774c933778b558ddfc7cbd9ad295772292e10c7ab7b50ddc8ba38588fd8`.

Конфігурація й credentials взяті з наявного `C:/repos/Jane/.jane/stack-jane-demo.json`. Оновлено лише storage і статику; Compose — `up -d --no-deps --no-build --wait --wait-timeout 120 storage`. Попередні assets залишено, новий index замінено останнім. Production build: 167 modules transformed, built in 962ms; storage build — exit 0.

Резервна копія: `C:/repos/Jane/.jane/backups/admin-ada35865a327` — попередні dist, конфігурація, приватний stack-state та filesystem storage. Під час копіювання storage й оркестратор зупинені; перед зупинкою підтверджено відсутність активних runs. PostgreSQL/MinIO не замінювалися. Старі шари Docker виявилися недоступними для tag/commit; файлову систему чинного контейнера успішно експортовано й імпортовано у локальний rollback image `jane-demo-storage:before-admin-ada35865a327` з параметрами запуску. Аварійний запуск цього резервного образу не перевірявся; це не резервна копія всієї PostgreSQL/MinIO.

Усі робочі demo-контейнери healthy/running. Збережено всі томи; інші **19 із 20** контейнерів зберегли ID та образи. Docker після stop/start оркестратора змінив його динамічний порт `56225 → 52310`; stack metadata оновлено. Порт storage `54345` та URL адмінки збережені. Локальні незакомічені зміни паралельної документаційної роботи в кореневому checkout не включені до цього постачання й не перезаписані.

## Перевірки після розгортання

Реальні API: збережені object-вибірки обох connections до/після збігаються. Після restart статус спочатку unknown; асинхронні checks завершилися succeeded, обидва connections available.

```text
raw-files: available; object_count=46; total_size_bytes=79906340
results-pg: available; object_count=null; total_size_bytes=null;
            unavailable_reason=adapter_statistics_not_supported
samples_preserved=true
demo_healthy=true; volumes_preserved=true
other_container_ids_and_images_unchanged=19
Live admin: storages/materials/chain property grid/mobile passed;
no page errors; no configuration writes
```

Headless browser на реальному стеку виконав вхід, відкрив сторінки сховищ та матеріалів, показав непорожній збережений вміст, відкрив нове завдання з вкладкою ланцюжка й грідом «Назва / Тип / Значення», перевірив вигляд 390×844. Desktop/mobile screenshots переглянуті візуально. Локальні докази (ignored): `.jane/live-storages.png`, `.jane/live-materials.png`, `.jane/live-chain.png`, `.jane/live-storages-mobile.png`, `.jane/deployment-verification.json`.

Цей smoke не створював нового TaskConfig і не запускав новий користувацький ланцюжок. Рекурсивне редагування JSON/масивів, зв’язки, валідація та збереження перевірені сценаріями WP-26; це не оголошується реальним виконанням нового ланцюжка. Статистика описує об’єкти connection і байти payload, а не місткість диска/бази.

## Передача в main

Координатор виконує дозволений користувачем fast-forward push у GitHub `main`. `91876d1` є предком перевіреної ревізії; після неї додається лише цей звіт та актуалізація delivery status/WP-27. Код постачання тотожний ревізії повного CI. Локальний main checkout із паралельними незакоміченими змінами не перемикається.
