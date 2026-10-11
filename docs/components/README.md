# Каталог модулів

Обери потрібний модуль і відкрий його короткий старт. Залежності в таблиці потрібні для відповідного сценарію; Orchestrator об’єднує їх у спільне завдання.

## Типи модулів

- **Колектор** — отримує матеріали й зберігає власний буфер.
- **Обробник** — перетворює, зберігає дані або викликає LLM.
- **Середовище виконання** — запускає код пакета в sandbox.
- **Репозиторій пакетів** — керує архівами, версіями й походженням.
- **Оркестратор** — поєднує етапи, чергу й розклади.
- **Асистент** — досліджує джерела та готує зміни пакетів.
- **Інтерфейс** — дає користувачу доступ до API модулів.
- **Бібліотека або SDK** — використовується у власному Python-застосунку.

## Одна сторінка модулів

| Модуль | Тип і призначення | Мінімальні залежності | Опційні залежності | Старт |
|---|---|---|---|---|
| [Web Collector](web-collector/README.md) | Колектор сайтів | Власний SQLite, HTTP-джерело | Registry для правил; Chromium для JS | [HTML](web-collector/quickstart.md) |
| [Telegram Collector](telegram-collector/README.md) | Колектор повідомлень | Власний SQLite, recording або Telegram session | Registry для правил; Telethon для акаунта | [Replay](telegram-collector/quickstart.md) |
| [Storage](storage/README.md) | Обробник збереження | Сховище обраного адаптера | Registry для пакетів, secret backend | [Запис](storage/quickstart.md) |
| [LLM](llm/README.md) | Обробник LLM | Підключення провайдера для реального виклику | PostgreSQL для durable state, Registry для пакетів | [Сервіс](llm/quickstart.md) |
| [Handler Runtime](handler-runtime/README.md) | Sandbox для коду пакетів | Docker, runtime image, локальний пакет або Registry | PostgreSQL для durable state | [Пакет](handler-runtime/quickstart.md) |
| [Registry](registry/README.md) | Репозиторій версій | Memory або PostgreSQL; files або S3 | Secret backend | [Публікація](registry/quickstart.md) |
| [Orchestrator](orchestrator/README.md) | Етапи, черга й розклади | Власний PostgreSQL; виконавці потрібних етапів | Registry, інші виконавці | [Конфігурація](orchestrator/quickstart.md) |
| [Assistant](assistant/README.md) | Дослідження й зміни пакетів | LLM для генерації; клієнти обраної дії | Registry, Runtime, Collector, Orchestrator, PostgreSQL | [Сесія](assistant/quickstart.md) |
| [Admin](admin/README.md) | Інтерфейс керування | Node/pnpm для збирання, API обраних модулів | Усі додаткові API за конфігурацією | [Інтерфейс](admin/quickstart.md) |
| [Jane Kit](jane-kit/README.md) | Спільні засоби сервісів | Python | PostgreSQL, зовнішні клієнти за використаним засобом | [Застосунок](jane-kit/quickstart.md) |
| [Extractor SDK](extractor-sdk/README.md) | Засоби екстракторів | Python; залежності власного коду | Handler Runtime для sandbox | [Екстрактор](extractor-sdk/quickstart.md) |

Кожен сервіс має власний стан і може обслуговувати стороннього клієнта. Межі автономності, поведінка за недоступності залежності й правила заміни наведені у `dependencies.md` та `integration.md` модуля. Бібліотеки працюють у процесі клієнта. Спільні принципи: [автономність](../architecture/autonomy.md), [власність даних](../architecture/data.md).
