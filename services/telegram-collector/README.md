# Telegram Collector

Колектор каналів Telegram платформи Jane: історія, нові повідомлення й редагування (редагування — нове спостереження того самого `material_id`), курсори каналів між зборами, API `collector.v1`. Типовий бекенд `recorded` відтворює канали з JSON-записів; бекенд `telethon` (extra) працює з реальним Telegram і на реальному сервісі не перевірявся. Власний стан — SQLite.

Повна документація модуля — [docs/components/telegram-collector](../../docs/components/telegram-collector/README.md).

## Запуск

З кореня репозиторію, порт 8102, канали з записів (Bash; у PowerShell змінну задайте через `$env:`):

```bash
JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR=examples/telegram/recordings uv run --package jane-telegram-collector python -m jane_telegram_collector
```

З Telethon:

```powershell
uv sync --package jane-telegram-collector --extra telethon
```

Docker-образ:

```powershell
docker build -f services/telegram-collector/Dockerfile -t jane-telegram-collector .
```

Покроковий приклад на записаному каналі — [quickstart.md](../../docs/components/telegram-collector/quickstart.md); змінні середовища й ліміти — [configuration.md](../../docs/components/telegram-collector/configuration.md).

## Тести

```powershell
just test telegram-collector
```

Тести запускають сервіс на записаних каналах, Docker і dev-стек не потрібні. Вибірка — аргументи pytest, наприклад `just test telegram-collector -k edits`.

## Структура

```text
services/telegram-collector/
├── src/jane_telegram_collector/   # сервіс: API, збір каналів, бекенди клієнта, стан
├── tests/                         # тести сервісу на бекенді recorded
└── Dockerfile
```
