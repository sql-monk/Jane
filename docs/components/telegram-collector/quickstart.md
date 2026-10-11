# Telegram Collector: швидкий старт

Запустіть автономний replay одного повідомлення без доступу до Telegram.

## Передумови

Python 3.12+, uv, checkout Jane; команди з кореня. Окремий directory `.jane/docs-telegram` містить recordings і state.

```powershell
uv sync --package jane-telegram-collector
uv run --package jane-telegram-collector python -c "from pathlib import Path; from jane_telegram_collector.recorded import Recording; r=Recording.create(Path('.jane/docs-telegram/recordings'), channel_id='-1001234567890', username='jane_demo'); r.post('Jane demo')"
```

## Запуск сервісу

```powershell
uv run --package jane-telegram-collector python -c "from pathlib import Path; from jane_telegram_collector.settings import Settings; from jane_telegram_collector.app import build_app; from jane_kit.service import run; s=Settings(state_dir=Path('.jane/docs-telegram/state'), recordings_dir=Path('.jane/docs-telegram/recordings'), port=8193); run(build_app(s), s)"
```

Запуск використовує `127.0.0.1:8193`, `auth_mode=none`, backend recorded.

## Перше повідомлення

У другому терміналі:

```powershell
uv run --package jane-telegram-collector python -c "import httpx; r=httpx.post('http://127.0.0.1:8193/v1/fetches', json={'source_kind':'telegram','telegram':{'channel_username':'jane_demo','message_id':1}}); r.raise_for_status(); m=r.json(); assert m['source']['kind']=='telegram'; print(m)"
```

Очікуйте Material із channel/message locator, текстом і content hash. Для колекції використайте [клієнт](integration.md#мінімальний-клієнт). Зупинка — Ctrl+C.

## Реальний Telegram

```powershell
uv sync --package jane-telegram-collector --extra telethon
```

Налаштуйте client_backend=`telethon`, [telegram_account connection](configuration.md) із references на вже авторизовану session та api_id/api_hash. Зовнішній Telegram не перевіряється offline replay.
