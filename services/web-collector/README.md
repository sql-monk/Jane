# Web Collector

Колектор вебсторінок платформи Jane: знаходить URL за стратегіями пошуку (`seed_list`, `recursive`, `sitemap`, `feed`, `listing`, `url_template`, `api_feed`), дотримується меж обходу, `robots.txt` і лімітів хоста та віддає матеріали через API `collector.v1`. Працює окремо, без Orchestrator; власний стан — SQLite.

Повна документація модуля — [docs/components/web-collector](../../docs/components/web-collector/README.md).

## Запуск

З кореня репозиторію, порт 8101:

```powershell
uv run --package jane-web-collector python -m jane_web_collector
```

Тестовий сайт для перевірок:

```powershell
uv run python -m jane_testsite --port 8080
```

Docker-образ:

```powershell
docker build -f services/web-collector/Dockerfile -t jane-web-collector .
```

Покроковий приклад із реальними запитами — [quickstart.md](../../docs/components/web-collector/quickstart.md); змінні середовища й ліміти — [configuration.md](../../docs/components/web-collector/configuration.md).

## Тести

```powershell
just test web-collector
```

Тести запускають сервіс і тестовий сайт у процесі, Docker не потрібен; повний прогін триває понад 10 хвилин. Вибірка тестів — аргументи pytest, наприклад `just test web-collector -k robots`; тести стратегій лежать у `strategies/discovery/tests/`. Перевірка стабільності одного тесту — `scripts/repeat_test.py` (опис у його заголовку).

## Структура

```text
services/web-collector/
├── src/jane_web_collector/   # сервіс: API, ядро обходу, стан, рендеринг
├── strategies/discovery/     # стратегії пошуку sitemap, feed, listing, url_template, api_feed
├── tests/                    # тести сервісу проти тестового сайту
├── scripts/repeat_test.py    # повторний запуск тестів для пошуку нестабільних
└── Dockerfile
```

Як підключити власну стратегію — [strategies/discovery/README.md](strategies/discovery/README.md).
