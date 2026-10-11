# Jane

Jane — модульна платформа, яка збирає матеріали із сайтів і Telegram-каналів, витягує з них структуровані дані та зберігає результати у вибрані сховища. Кожен модуль має власний API й запускається окремо, а Orchestrator поєднує модулі в завдання з розкладом.

Проєкт названо на честь докторки Джейн Гудолл; він не пов'язаний із Jane Goodall Institute.

## Зміст

- [Що робить Jane](#що-робить-jane)
- [Як складається платформа](#як-складається-платформа)
- [Типи модулів](#типи-модулів)
- [Каталог модулів](#каталог-модулів)
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

## Типи модулів

- **Колектор** — отримує матеріали з джерела й повертає їх із метаданими (`collector.v1`). Бізнес-результатів не зберігає.
- **Обробник** — виконує один етап над переданими даними (`handler.v1`): збереження, витягування або виклик LLM. Екстрактор — це пакет обробника; його код виконує Handler Runtime.
- **Репозиторій** — зберігає пакети обробників і правила колекторів (`registry.v1`).
- **Координація** — Orchestrator виконує завдання; Assistant за допомогою LLM готує джерела, правила й екстрактори.
- **Інтерфейс** — вебзастосунок для оператора.
- **Бібліотека** — спільний код сервісів, SDK екстракторів і контракти.

## Каталог модулів

| Модуль | Тип | Призначення | Окремо | Обов'язкові залежності | Опційні залежності |
|---|---|---|---|---|---|
| [Web Collector](services/web-collector/README.md) | колектор | Вебсторінки за стратегіями пошуку | так | доступ до сайтів, каталог стану | Registry, транзитне сховище, Playwright |
| [Telegram Collector](services/telegram-collector/README.md) | колектор | Повідомлення й редагування каналів | так | клієнт Telegram, каталог стану | Registry, транзитне сховище |
| [Storage](services/storage/README.md) | обробник | Запис і читання RAW та сутностей через адаптери | так | цільове сховище | Registry |
| [Handler Runtime](services/handler-runtime/README.md) | обробник | Виконання Python-екстракторів у пісочниці | так | Docker або Podman | PostgreSQL, Registry |
| [LLM gateway](services/llm/README.md) | обробник | Виклики моделей, бюджети, облік витрат | так | PostgreSQL або режим `memory` | провайдер LLM, Registry |
| [Registry](services/registry/README.md) | репозиторій | Пакети: версії, тести, форки, експорт | так | PostgreSQL, S3 або MinIO | профілі Handler Runtime |
| [Orchestrator](services/orchestrator/README.md) | координація | Джерела, завдання, розклади, черга етапів | поєднує інші | PostgreSQL, виконавці | — |
| [Assistant](services/assistant/README.md) | координація | Підготовка джерел і вдосконалення екстракторів | частково | LLM gateway, Registry, колектор, Handler Runtime | Orchestrator, Storage, PostgreSQL |
| [Admin UI](web/admin/) | інтерфейс | Керування платформою в браузері | на моках API | API сервісів | — |
| [jane-kit](libs/jane-kit/README.md) | бібліотека | Конфігурація й ліміти, помилки, ідемпотентність, job, автентифікація | — | FastAPI, Pydantic | — |
| [jane-extractor-sdk](libs/extractor-sdk/README.md) | бібліотека | Типи й помічники для авторів екстракторів | так | — | — |
| [jane-contracts](contracts/README.md) | контракти | OpenAPI, JSON Schema, Python Protocol-и | так | — | — |

Пояснення до таблиці:

- **Окремо** — чи можна запустити й використати модуль без інших модулів Jane. Assistant без своїх обов'язкових сусідів повертає `upstream_unavailable` для функцій, яким вони потрібні.
- **Каталог стану** колекторів — локальна база SQLite; кілька екземплярів Web Collector узгоджують ліміти хоста через спільний каталог.
- **Цільове сховище** Storage — адаптери PostgreSQL, SQL Server, MongoDB, MinIO, S3 і файлової системи; файловому адаптеру потрібен лише каталог.
- **Handler Runtime** без PostgreSQL тримає стан у пам'яті — це підходить лише для одного екземпляра.
- **LLM gateway** має вбудований детермінований провайдер `fake`; реальні відповіді дає провайдер Anthropic за налаштованим підключенням.
- **Registry** для локальних дослідів працює без зовнішніх сервісів: `JANE_REGISTRY_DB=memory`, `JANE_REGISTRY_BLOB=filesystem`.

## Швидкий старт

Піднімає всю платформу з адмінкою на локальному Docker. Кроки виконано 2026-10-11 на Windows 11, ревізія `dd99d22`; на Linux не перевірялися.

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

Отримує одну сторінку тестового сайту без Docker, Orchestrator і Registry. Так само самостійно запускаються інші модулі — команди в їхніх README з [каталогу](#каталог-модулів).

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

| Потреба | Документ |
|---|---|
| Вимоги до платформи та критерії приймання | [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) |
| Середовище розробки, команди, CI | [DEVELOPMENT.md](DEVELOPMENT.md) |
| API, схеми, перевірка сумісності | [contracts/README.md](contracts/README.md) |
| Формат пакетів обробників | [contracts/docs/handler-packages.md](contracts/docs/handler-packages.md) |
| Модель помилок API | [contracts/docs/errors.md](contracts/docs/errors.md) |
| Власність даних і повтори | [contracts/docs/data-ownership.md](contracts/docs/data-ownership.md) |
| Запуск, конфігурація й API окремого модуля | README модуля з [каталогу](#каталог-модулів) |
| Вимоги до документації | [DOCUMENTATION_REQUIREMENTS.md](DOCUMENTATION_REQUIREMENTS.md) |
