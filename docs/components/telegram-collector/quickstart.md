# Telegram Collector: швидкий старт

Запуск Telegram Collector на записаному каналі без облікового запису Telegram, Docker і Orchestrator: разове отримання повідомлення, повний збір історії, редагування й новий пост, інкрементальний збір.

Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7 і Git Bash), ревізія `48389a3`; на Linux не перевірялися. Порт 18120 взято для прикладу.

## Зміст

- [Передумови](#передумови)
- [Запуск](#запуск)
- [Отримати одне повідомлення](#отримати-одне-повідомлення)
- [Зібрати історію каналу](#зібрати-історію-каналу)
- [Нові повідомлення й редагування](#нові-повідомлення-й-редагування)
- [Прибирання](#прибирання)

## Передумови

- uv і Python 3.12+ — [DEVELOPMENT.md](../../../DEVELOPMENT.md); залежності встановлено командою `uv sync --all-packages`.
- Команди виконуються з кореня репозиторію.
- Записаний канал — [examples/telegram/recordings/jane_events_example.json](../../../examples/telegram/recordings/jane_events_example.json): канал `jane_events_example` з трьома повідомленнями. Формат записів — [integration.md](integration.md#формат-записаного-каналу).

## Запуск

1. Скопіюйте записи в робочий каталог, щоб змінювати їх, не чіпаючи файлів репозиторію:

   ```powershell
   uv run python -c "import shutil; shutil.copytree('examples/telegram/recordings', '.jane/tg-recordings', dirs_exist_ok=True)"
   ```

2. Запустіть колектор із бекендом `recorded` (типовий).

   PowerShell:

   ```powershell
   $env:JANE_TELEGRAM_COLLECTOR_PORT = "18120"
   $env:JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR = ".jane/tg-recordings"
   uv run --package jane-telegram-collector python -m jane_telegram_collector
   ```

   Bash:

   ```bash
   JANE_TELEGRAM_COLLECTOR_PORT=18120 JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR=.jane/tg-recordings \
     uv run --package jane-telegram-collector python -m jane_telegram_collector
   ```

   У журналі — `Uvicorn running on http://127.0.0.1:18120` і попередження `auth_mode=none` (сервіс приймає запити без ключа, лише для локальної роботи). Стан пишеться в `.jane/telegram-collector/state.db`.

3. В іншому терміналі перевірте сервіс:

   ```powershell
   curl.exe -s http://127.0.0.1:18120/v1/health
   ```

   ```json
   {"status":"ok","checks":{"state_store":{"status":"ok"}}}
   ```

   `GET /v1/info`, поле `capabilities`:

   ```json
   {"source_kinds": ["telegram"], "client_backend": "recorded", "strategies": ["telegram_history", "telegram_updates"], "modes": ["full", "incremental"], "content_delivery": ["auto", "inline"], "rules_sources": ["inline"], "connection_kinds": ["telegram_account"]}
   ```

## Отримати одне повідомлення

PowerShell 7:

```powershell
curl.exe -s -X POST http://127.0.0.1:18120/v1/fetches -H "Content-Type: application/json" -d '{"source_kind": "telegram", "telegram": {"channel_username": "jane_events_example", "message_id": 2}}'
```

Bash:

```bash
curl -s -X POST http://127.0.0.1:18120/v1/fetches -H 'Content-Type: application/json' -d '{"source_kind": "telegram", "telegram": {"channel_username": "jane_events_example", "message_id": 2}}'
```

Відповідь — матеріал (відформатовано):

```json
{
  "material_id": "tg:-1009000000001:2",
  "observation_id": "obs_01a12a69a1f1000079135f17",
  "source": {"kind": "telegram", "name": "Jane events example"},
  "locator": {
    "url": "https://t.me/jane_events_example/2",
    "telegram": {"channel_id": "-1009000000001", "message_id": 2, "channel_username": "jane_events_example"}
  },
  "fetched_at": "2026-10-11T10:02:08Z",
  "published_at": "2026-09-28T11:00:00Z",
  "format": {"media_type": "text/plain", "charset": "utf-8", "content_kind": "message"},
  "revision": {
    "content_sha256": "c9d5ed84c0546ee1c106af335f1a313ee1a59db8fac4a0286edac5beef19d519",
    "source_revision": "1790593200",
    "sequence": 1790593200000,
    "is_edit": false
  },
  "content": {
    "kind": "inline",
    "media_type": "text/plain",
    "charset": "utf-8",
    "encoding": "utf-8",
    "data": "Оголошення: бібліотека зачинена 1 жовтня на санітарний день.",
    "size_bytes": 110,
    "sha256": "c9d5ed84c0546ee1c106af335f1a313ee1a59db8fac4a0286edac5beef19d519"
  },
  "collector": {"name": "telegram-collector", "version": "0.1.0"}
}
```

Повідомлення, якого немає (`message_id: 99`), дає `404 not_found` з `details.reason: "message_not_found"`; невідомий канал — `502 source_unavailable` з `details.reason: "channel_unavailable"`.

## Зібрати історію каналу

1. Збережіть тіло запиту у файл `tg-collection.json`:

   ```json
   {
     "source_kind": "telegram",
     "source_id": "events-channel",
     "state_key": "events-channel",
     "mode": "full",
     "rules": {
       "collector": "telegram",
       "channels": [{"username": "jane_events_example"}]
     }
   }
   ```

2. Запустіть збір (заголовок `Idempotency-Key` обов'язковий).

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18120/v1/collections -ContentType application/json -Headers @{"Idempotency-Key" = "doc-tg-1"} -InFile tg-collection.json).Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18120/v1/collections -H 'Content-Type: application/json' -H 'Idempotency-Key: doc-tg-1' --data @tg-collection.json
   ```

   ```json
   {"job_id":"job_7f1546c444984a18abb8bd7b7c2fc6b8","kind":"collection","status":"queued","created_at":"2026-10-11T10:02:04.847618Z","links":{"self":"/v1/jobs/job_7f1546c444984a18abb8bd7b7c2fc6b8","cancel":"/v1/jobs/job_7f1546c444984a18abb8bd7b7c2fc6b8/cancel"}}
   ```

3. Стан збору — `GET /v1/collections/job_7f1546c444984a18abb8bd7b7c2fc6b8`. Уривок:

   ```json
   {
     "status": "succeeded",
     "mode": "full",
     "state_key": "events-channel",
     "stats": {"discovered": 3, "fetched": 3, "emitted": 3, "acknowledged": 0, "unacked": 3, "duplicates": 0, "errors": 0, "bytes_fetched": 343, "by_strategy": {"telegram_history": 3}}
   }
   ```

4. Матеріали читаються так само, як у будь-якого колектора: `GET /v1/collections/{id}/materials?limit=1` повертає перше повідомлення (`material_id: "tg:-1009000000001:1"`, `discovery.strategy: "telegram_history"`) і `next_cursor: "c_0000000000000001"`; запит з `after=<курсор>` підтверджує прочитане.

5. Курсор каналу після збору — `GET /v1/states/events-channel`:

   ```json
   {"state_key": "events-channel", "collector": "telegram", "updated_at": "2026-10-11T10:02:05Z", "cursors": {"-1009000000001": {"last_message_id": 3, "pts": 3, "username": "jane_events_example"}}}
   ```

## Нові повідомлення й редагування

1. Збережіть скрипт `edit_recording.py`: він редагує повідомлення 1 і додає новий пост у записаний канал за допомогою `Recording` із бекенда `recorded`:

   ```python
   import sys
   from pathlib import Path

   from jane_telegram_collector.recorded import Recording

   path = Path(sys.argv[1]) / "jane_events_example.json"
   rec = Recording(path, channel_id="-1009000000001", username="jane_events_example")
   rec.reload()
   rec.edit(1, "Подія: Лекція про історію міста | 2026-10-05 19:00 | Міська бібліотека")
   new_id = rec.post("Подія: Виставка світлин | 2026-10-20 12:00 | Музей міста")
   print(f"edited message 1, posted message {new_id}")
   ```

   ```powershell
   uv run --package jane-telegram-collector python edit_recording.py .jane/tg-recordings
   ```

   ```text
   edited message 1, posted message 4
   ```

2. Запустіть інкрементальний збір: у `tg-collection.json` замініть `"mode": "full"` на `"mode": "incremental"` і надішліть із новим ключем, наприклад `Idempotency-Key: doc-tg-2`. Статистика:

   ```json
   {"discovered": 2, "fetched": 2, "emitted": 2, "duplicates": 0, "errors": 0, "bytes_fetched": 198, "by_strategy": {"telegram_updates": 2}}
   ```

3. Два матеріали збору (уривок, відформатовано):

   ```json
   [
     {
       "material_id": "tg:-1009000000001:1",
       "published_at": "2026-09-28T09:00:00Z",
       "edited_at": "2026-10-11T10:02:47Z",
       "revision": {"content_sha256": "f83685c2cc0d95f77b3188aac913cd7b2e76c9447ce362e57b60bc05b15fe548", "is_edit": true, "sequence": 1791712967000, "source_revision": "1791712967"},
       "discovery": {"strategy": "telegram_updates"},
       "content": {"data": "Подія: Лекція про історію міста | 2026-10-05 19:00 | Міська бібліотека"}
     },
     {
       "material_id": "tg:-1009000000001:4",
       "published_at": "2026-10-11T10:02:47Z",
       "revision": {"content_sha256": "f7de3291dc090e20dd044457eb155fde2802f8d706f5178fe92417ebed0f0890", "is_edit": false, "sequence": 1791712967000, "source_revision": "1791712967"},
       "discovery": {"strategy": "telegram_updates"},
       "content": {"data": "Подія: Виставка світлин | 2026-10-20 12:00 | Музей міста"}
     }
   ]
   ```

   Редагування повідомлення 1 — нове спостереження того самого `material_id` з `is_edit: true` і більшим `sequence`, ніж у першої ревізії (`1790586000000`). Незмінені повідомлення 2 і 3 не видаються.

4. Курсор після збору: `last_message_id: 4`, `pts: 5`, `last_edit_date: "2026-10-11T10:02:47Z"`.

## Прибирання

1. Зупиніть колектор: `Ctrl+C`.
2. Команда видаляє **весь** стан колектора в цьому каталозі (збори, буфери, курсори каналів, підключення) і копію записів:

   ```powershell
   uv run python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('.jane/telegram-collector', '.jane/tg-recordings')]"
   ```

3. Видаліть файли `tg-collection.json` і `edit_recording.py`.
