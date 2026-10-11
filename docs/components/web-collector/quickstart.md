# Web Collector: швидкий старт

Запустіть Collector та локальний HTTP-сайт у двох терміналах. Registry, Orchestrator і Storage для прикладу не потрібні.

## Передумови

Python 3.12+, uv, checkout Jane. Робоча директорія — корінь. Цей запуск використовує loopback, `auth_mode=none` і окрему папку `.jane/docs-web`.

```powershell
uv sync --package jane-web-collector
uv run --package jane-web-collector python -c "from pathlib import Path; p=Path('.jane/docs-web/site'); p.mkdir(parents=True, exist_ok=True); (p/'index.html').write_text('<h1>Jane demo</h1>', encoding='utf-8')"
```

## Локальне джерело

У першому терміналі:

```powershell
uv run --package jane-web-collector python -m http.server 8191 --bind 127.0.0.1 --directory .jane/docs-web/site
```

У другому терміналі запустіть лише Collector, передавши конфігурацію через Python:

```powershell
uv run --package jane-web-collector python -c "from pathlib import Path; from jane_web_collector.app import build_app; from jane_web_collector.settings import Settings; from jane_kit.service import run; s=Settings(state_dir=Path('.jane/docs-web/state'), port=8192); run(build_app(s), s)"
```

## Перший матеріал

У третьому терміналі:

```powershell
uv run --package jane-web-collector python -c "import httpx; r=httpx.post('http://127.0.0.1:8192/v1/fetches', json={'source_kind':'web','url':'http://127.0.0.1:8191/index.html'}); r.raise_for_status(); m=r.json(); assert m['source']['kind']=='web'; assert m['content']['kind']=='inline'; print(m)"
```

Очікуйте Material із locator URL, observation_id, content hash та inline HTML. Згенеровані ID й fetched_at змінюються при запуску; їх не фіксуйте як expected.

## Потік і зупинка

[Сторонній клієнт](integration.md#мінімальний-клієнт) запускає колекцію для того самого джерела. Завершіть Collector і HTTP-сайт Ctrl+C. `.jane/docs-web/state/state.db` зберігає локальний стан.

Для `fetch.render_js` потрібен render extra й Chromium:

```powershell
uv sync --package jane-web-collector --extra render
uv run --package jane-web-collector playwright install chromium
```

Browser installation потребує мережі; для звичайного HTML-прикладу цей крок пропускається.
