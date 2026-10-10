# Ціни ноутбуків у реальних магазинах

Робоча конфігурація Jane на справжніх сайтах: **Rozetka**, **Allo**, **Цитрус**, **Фокстрот**, **MOYO**. Кожен
запуск бере перші 5 сторінок категорії ноутбуків (60 / 60 / 47 / 42 / 24 товари на сторінку), RAW — у files, пропозиції `offer` (назва,
бренд, ціна, наявність, посилання, зображення) — у PostgreSQL. Розклад: щодня о 09:00 і 21:00 (Europe/Kyiv).

| Пакет | Що |
|---|---|
| `shops.jsonld-offers` | спільний екстрактор schema.org JSON-LD сторінок категорій (`ItemList → Product → Offer` або `Product.offers[]`); ключ — магазин + id товару |
| `shops.product-cards` | екстрактор карток `div.product-card` з атрибутами `data-price`, `data-title`/`data-name`, `data-code`/`data-product_id`… (Фокстрот, MOYO); та сама сутність `offer` |
| `shops.<магазин>-notebooks-rules` | правила Web Collector: лише 5 сторінок категорії (`seed_list`), `robots.txt` дотримується, `rel=canonical` сторінок 2–5 не вважається дублікатом |

Запуск на стеку зі зв'язаними сервісами (`infra/compose.local.example.yaml` → `infra/compose.local.yaml`):

```text
uv run --all-packages python examples/shops/setup_shops.py --project <compose-project>
```

Скрипт публікує й погоджує пакети, створює підключення, джерела `shop-*` і завдання `notebooks-*`, один раз
запускає кожне й рахує пропозиції в storage. Повторний запуск оновлює джерела (нова версія правил — нова
версія пакета). Тести пакетів без сервісів — `examples/tests/test_shops.py`.

Ввічливість: 1 запит/с на хост, 5 сторінок на магазин за запуск, картки товарів не завантажуються. Comfy
відповідає ботам 403 — його не підключено (обхід захисту від ботів не робимо). Сайтам, що будують список
скриптами, правила можуть увімкнути `fetch.render_js` (headless Chromium у web-collector); цим п'ятьом не потрібно.
