# Jane

Jane — модульна платформа, яка збирає матеріали із сайтів і Telegram-каналів, витягує з них структуровані дані та зберігає результати у вибрані сховища. Кожен модуль має власний API й запускається окремо, а Orchestrator поєднує модулі в завдання з розкладом.

Проєкт названо на честь докторки Джейн Гудолл; він не пов'язаний із Jane Goodall Institute.

## Зміст

- [Що робить Jane](#що-робить-jane)
- [Як складається платформа](#як-складається-платформа)
- [Модулі](#модулі)
- [Швидкий старт](#швидкий-старт)
- [Модуль окремо: Web Collector](#модуль-окремо-web-collector)
- [Структура репозиторію](#структура-репозиторію)
- [Обмеження](#обмеження)
- [Що читати далі](#що-читати-далі)

## Що робить Jane

Користувач описує джерело, ланцюжок етапів обробки та розклад. Ланцюжок може розгалужуватися: наприклад, одну сторінку зберегти як RAW і паралельно передати екстрактору. Терміни (джерело, колектор, обробник, екстрактор, завдання) визначено в [ТЗ, розділ 2](TECHNICAL_SPECIFICATION.md#2-основний-принцип).

Можливості поточної реалізації:

- **Вебджерела** — явний список URL, рекурсивний обхід, Sitemap, RSS/Atom, сторінки категорій і пошуку, шаблони URL, API/JSON сайту; стратегії комбінуються.
- **Telegram** — історія каналу, нові повідомлення та редагування.
- **Екстрактори** — Python-пакети, які виконуються в ізольованій контейнерній пісочниці.
- **Збереження** — RAW і сутності в PostgreSQL, SQL Server, MongoDB, MinIO, S3 або файлах; сховище змінюється без зміни коду колектора чи екстрактора.
- **Репозиторій пакетів** — незмінні версії, тести, походження й форки пакетів обробників і правил колекторів.
- **LLM** — як етап ланцюжка та як помічник, що досліджує нове джерело й пропонує або вдосконалює екстрактори.
- **Адміністративний інтерфейс** — джерела, завдання, пакети, результати, помилки й витрати.

## Як складається платформа

![Склад Jane: координація, автономні модулі та зовнішні системи](docs/diagrams/platform/composition.light.png#gh-light-mode-only)
![Склад Jane: координація, автономні модулі та зовнішні системи](docs/diagrams/platform/composition.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](docs/diagrams/platform/composition.light.png), [темне](docs/diagrams/platform/composition.dark.png); джерело — [composition.drawio](docs/diagrams/platform/composition.drawio).

- **Orchestrator керує виконанням.** Він зберігає джерела й завдання, отримує матеріали від колекторів через `collector.v1` і передає їх обробникам через `handler.v1`. Колектори й обробники одне одного не викликають.
- **Модулі автономні.** Колектор, обробник або Registry можна викликати напряму зі стороннього застосунку без Orchestrator.
- **Кожен модуль володіє своїми даними.** Спільної бази немає; чужі дані доступні лише через API. Деталі — [карта власності даних](contracts/docs/data-ownership.md).
- **Registry — опційна залежність.** Правила колектора й пакет обробника можна передати в запиті або взяти з локального каталогу.

## Модулі

Типи модулів, автономність і залежності кожного — у [каталозі модулів](docs/components/README.md).

| Модуль | Призначення |
|---|---|
| [Web Collector](docs/components/web-collector/README.md) | вебсторінки за стратегіями пошуку |
| [Telegram Collector](docs/components/telegram-collector/README.md) | повідомлення й редагування Telegram-каналів |
| [Storage](docs/components/storage/README.md) | запис і читання RAW та сутностей через адаптери |
| [Handler Runtime](docs/components/handler-runtime/README.md) | виконання Python-екстракторів у пісочниці |
| [LLM gateway](docs/components/llm/README.md) | виклики моделей, бюджети, облік витрат |
| [Registry](docs/components/registry/README.md) | пакети обробників: версії, тести, форки |
| [Orchestrator](docs/components/orchestrator/README.md) | джерела, завдання, розклади, виконання ланцюжків |
| [Assistant](docs/components/assistant/README.md) | підготовка джерел і вдосконалення екстракторів з LLM |
| [Admin UI](docs/components/admin/README.md) | керування платформою в браузері |
| [jane-kit](docs/components/jane-kit/README.md) | спільна бібліотека сервісів |
| [jane-extractor-sdk](docs/components/extractor-sdk/README.md) | SDK авторів екстракторів |
| [jane-contracts](docs/components/contracts/README.md) | OpenAPI, JSON Schema, Python Protocol-и |

## Швидкий старт

Піднімає всю платформу з адмінкою на локальному Docker. Кроки виконано 2026-10-11 на Windows 11; на Linux не перевірялися.

Такий стек не зв'язує сервіси між собою: Orchestrator не має виконавців, тож завдання не просуваються. Наскрізний сценарій із даними — від джерела до збережених сутностей — описано в [docs/getting-started/end-to-end.md](docs/getting-started/end-to-end.md).

### Передумови

- uv, just, Docker із Compose v2 і Node.js 24 — версії та встановлення в [DEVELOPMENT.md](DEVELOPMENT.md#встановлення). Без встановленого just рецепт запускається як `uvx --from rust-just just <рецепт>`.
- Команди виконуються з кореня репозиторію.

### Запуск платформи

1. Встановіть залежності workspace:

   ```powershell
   uv sync --all-packages
   ```

2. Зберіть адмінку. Dev-стек віддає готовий `web/admin/dist`:

   ```powershell
   corepack pnpm --dir web/admin install --frozen-lockfile
   corepack pnpm --dir web/admin build
   ```

3. Запустіть сервіси. PostgreSQL, MinIO і тестовий сайт стартують автоматично як залежності; перший запуск збирає образи кілька хвилин:

   ```powershell
   just up proxy storage handler-runtime web-collector telegram-collector orchestrator registry llm assistant
   ```

   Команда чекає health-check усіх контейнерів і друкує адреси. Уривок виводу перевірочного запуску (назву проєкту й порти обирає `just up`):

   ```text
   project: jane-readme   (stack file: .jane/stack-jane-readme.json)
     postgres   127.0.0.1:53633
     minio      http://127.0.0.1:53635
     testsite   http://127.0.0.1:56339
     proxy      http://127.0.0.1:57770
     orchestrator http://127.0.0.1:60241
     auth       api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)
   ```

4. Перевірте стан контейнерів:

   ```powershell
   just ps
   ```

   Очікуваний результат: у стовпці `STATUS` кожного контейнера — `(healthy)`.

5. Отримайте адресу адмінки та ключ адміністратора:

   ```powershell
   just env
   ```

   Потрібні рядки (уривок; ключ генерується під час першого `just up` і зберігається поза Git):

   ```text
   JANE_STACK_PROXY_URL=http://127.0.0.1:57770
   JANE_STACK_AUTH_ADMIN_API_KEY=<ключ>
   ```

6. Відкрийте `JANE_STACK_PROXY_URL` у браузері й введіть ключ на сторінці «Jane — адмінка». Ключ зберігається лише в сесії вкладки.

Через той самий proxy доступні API сервісів: `<JANE_STACK_PROXY_URL>/api/<сервіс>/v1/...`, наприклад `/api/orchestrator/v1/health`. Без ключа захищені операції повертають `401`.

### Прибирання

Команда нижче зупиняє стек і **видаляє всі його дані**: томи баз і сховищ, локально зібрані образи та файл `.jane/stack-<проєкт>.json` зі згенерованими паролями.

```powershell
just down -v
```

Щоб зупинити стек і зберегти дані, виконайте `just down` без `-v`.

## Модуль окремо: Web Collector

Отримує одну сторінку тестового сайту без Docker, Orchestrator і Registry. Так само самостійно запускаються інші модулі — команди в їхніх quickstart з [каталогу](docs/components/README.md).

1. У першому терміналі запустіть тестовий сайт:

   ```powershell
   just testsite
   ```

   ```text
   Jane testsite on http://127.0.0.1:8080/
   ```

2. У другому терміналі запустіть Web Collector:

   ```powershell
   uv run --package jane-web-collector python -m jane_web_collector
   ```

   У журналі з'являється `Uvicorn running on http://127.0.0.1:8101`. Попередження `auth_mode=none` означає, що сервіс приймає запити без ключа — лише для локальної роботи.

3. У третьому терміналі запросіть сторінку товару.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8101/v1/fetches -ContentType application/json -Body '{"source_kind": "web", "url": "http://127.0.0.1:8080/product/laptop-four"}').Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:8101/v1/fetches -H 'Content-Type: application/json' -d '{"source_kind": "web", "url": "http://127.0.0.1:8080/product/laptop-four"}'
   ```

   Відповідь — матеріал за схемою [material.schema.json](contracts/schemas/material.schema.json): HTML сторінки разом із метаданими. Уривок (показано частину полів; `content.data` містить HTML):

   ```json
   {
     "material_id": "web:6d3240c3cbef3a25ea74c63539a5a624",
     "observation_id": "obs_01a128d1447900008577e71a",
     "source": {"kind": "web"},
     "locator": {
       "url": "http://127.0.0.1:8080/product/laptop-four",
       "final_url": "http://127.0.0.1:8080/product/laptop-four",
       "canonical_url": "http://127.0.0.1:8080/product/laptop-four"
     },
     "fetched_at": "2026-10-11T02:36:05Z",
     "format": {"media_type": "text/html", "content_kind": "page", "charset": "utf-8"},
     "content": {"kind": "inline", "media_type": "text/html", "size_bytes": 1093}
   }
   ```

   Кожен виклик — нове спостереження: `material_id` повторюється, `observation_id` і `fetched_at` змінюються.

4. Зупиніть обидва процеси через `Ctrl+C`. Стан Web Collector лишається в `.jane/web-collector/state.db` (каталог поза Git); видаліть каталог, якщо стан не потрібен.

Повний опис API — [collector.v1.yaml](contracts/openapi/collector.v1.yaml); набори очікуваних URL тестового сайту — [tests/fixtures/testsite/README.md](tests/fixtures/testsite/README.md).

## Структура репозиторію

Повна карта з точками входу й тестами — [docs/architecture/repository-map.md](docs/architecture/repository-map.md).

```text
Jane/
├── services/                  # сервіси; кожен — Python-пакет із src/, tests/, Dockerfile і README
│   ├── web-collector/         # Web Collector; strategies/ — стратегії пошуку матеріалів
│   ├── telegram-collector/    # Telegram Collector
│   ├── storage/               # Storage; adapters/ — files, postgres, sqlserver, mongodb, minio, s3
│   ├── handler-runtime/       # Handler Runtime; sandbox/ — образ пісочниці python-extractor-1
│   ├── llm/                   # LLM gateway; packages/ — вбудовані LLM-пакети, config/ — приклад seed
│   ├── registry/              # Registry
│   ├── orchestrator/          # Orchestrator
│   └── assistant/             # Assistant
├── libs/
│   ├── jane-kit/              # спільна бібліотека сервісів і генератор клієнтів jane-codegen
│   └── extractor-sdk/         # SDK Python-екстракторів
├── web/admin/                 # Admin UI: React, TypeScript, Vite, pnpm
├── contracts/                 # openapi/, schemas/, examples/, python/ (Protocol-и), tools/, docs/
├── infra/                     # dev-стек: compose.yaml, proxy/ (Caddy), postgres/, config/, tests/
├── deploy/profiles/           # профілі лімітів і стенд для їх вимірювання
├── examples/                  # відтворювані приклади: пакети, каталог і перевірка цін, Telegram
├── templates/service/         # шаблон нового сервісу для just new-service
├── tests/
│   ├── e2e/                   # наскрізні приймальні сценарії
│   └── fixtures/testsite/     # детермінований тестовий сайт
├── scripts/                   # dev.py — виконавець рецептів just; утиліти розробки
├── docs/diagrams/             # схеми Draw.io та їхні PNG
├── justfile                   # команди розробки
├── pyproject.toml             # uv workspace, налаштування ruff, mypy, pytest
├── TECHNICAL_SPECIFICATION.md # технічне завдання
├── DEVELOPMENT.md             # середовище, команди, CI
└── DOCUMENTATION_REQUIREMENTS.md
```

Точки входу та тести:

- Сервіс запускається як `python -m jane_<сервіс>`; код — `services/<сервіс>/src/jane_<сервіс>/__main__.py`. Handler Runtime має також CLI `jane-handler-runtime` (`cli.py`) з командами `serve`, `run`, `test`, `profile`, `build-image`.
- Тести кожного пакета лежать у його `tests/`; тести dev-стеку — `infra/tests/`, скриптів — `scripts/tests/`, наскрізні — `tests/e2e/`.
- Перевірки, які запускає CI, — `just check`; інші команди — [DEVELOPMENT.md](DEVELOPMENT.md#команди).

## Обмеження

- **Telegram Collector** типово читає записані канали (бекенд `recorded`). Реальний Telegram потребує опційного бекенда `telethon` і облікового запису; у цьому README такий сценарій не перевірявся.
- **Handler Runtime** ізолює код екстракторів у контейнерах Docker або Podman. Тести ізоляції запускаються лише на Linux (`just isolation`).
- **Dev-стек** (`infra/compose.yaml`) призначений для розробки й перевірок: порти відкриваються лише на `127.0.0.1`, облікові дані генеруються локально.
- **Схема** на GitHub показується відповідно до теми; інші переглядачі Markdown можуть показати обидва PNG поспіль.

## Що читати далі

Уся документація з маршрутами для користувача, розробника й адміністратора — [docs/README.md](docs/README.md).

| Потреба | Документ |
|---|---|
| Вимоги до платформи та критерії приймання | [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) |
| Середовище розробки, команди, CI | [DEVELOPMENT.md](DEVELOPMENT.md) |
| API, схеми, перевірка сумісності | [contracts/README.md](contracts/README.md) |
| Формат пакетів обробників | [contracts/docs/handler-packages.md](contracts/docs/handler-packages.md) |
| Модель помилок API | [contracts/docs/errors.md](contracts/docs/errors.md) |
| Власність даних і повтори | [contracts/docs/data-ownership.md](contracts/docs/data-ownership.md) |
| Запуск, конфігурація й API окремого модуля | комплект модуля з [каталогу](docs/components/README.md) |
| Вимоги до документації | [DOCUMENTATION_REQUIREMENTS.md](DOCUMENTATION_REQUIREMENTS.md) |
