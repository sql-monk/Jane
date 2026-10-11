# Ціни ноутбуків у реальних магазинах

Приклад Jane на справжніх сайтах: для п'яти українських магазинів збирає перші п'ять сторінок категорії ноутбуків, зберігає їх як RAW і витягує пропозиції товарів (`offer`) з ціною й наявністю в PostgreSQL. Завдання далі виконуються за розкладом двічі на день. Загальний опис прикладів — [examples/README.md](../README.md).

## Зміст

- [Магазини й пакети](#магазини-й-пакети)
- [Що створює скрипт](#що-створює-скрипт)
- [Запуск](#запуск)
- [Перевірка без сервісів](#перевірка-без-сервісів)
- [Обмеження](#обмеження)

## Магазини й пакети

| Магазин | Джерело | Правила колектора | Екстрактор |
|---|---|---|---|
| Rozetka | `shop-rozetka` | `shops.rozetka-notebooks-rules` 1.0.1 | `shops.jsonld-offers` |
| Allo | `shop-allo` | `shops.allo-notebooks-rules` 1.0.1 | `shops.jsonld-offers` |
| Цитрус | `shop-citrus` | `shops.citrus-notebooks-rules` 1.0.1 | `shops.jsonld-offers` |
| Фокстрот | `shop-foxtrot` | `shops.foxtrot-notebooks-rules` 1.0.0 | `shops.product-cards` |
| MOYO | `shop-moyo` | `shops.moyo-notebooks-rules` 1.0.0 | `shops.product-cards` |

- **Правила колектора** — один список URL (стратегія `seed_list`) із першими п'ятьма сторінками категорії, без переходу за посиланнями; `robots.txt` дотримується (`robots.mode: respect`). Для сторінок 2–5, які вказують `rel=canonical` на першу, дедуплікацію за canonical вимкнено.
- **`shops.jsonld-offers`** витягує пропозиції зі schema.org JSON-LD сторінок категорій (`ItemList` → `Product` → `Offer` або `Product.offers`).
- **`shops.product-cards`** витягує пропозиції з карток товарів у розмітці сторінки (атрибути `data-*` елементів `div.product-card`).
- **Сутність `offer`**: обов'язкові поля `shop`, `product_id`, `title`, `url`, `price`; додатково `brand`, `image`, `availability`. Ключ — `shop` і `product_id`.

Пакети лежать у [packages/](packages/); тестові сторінки екстракторів — у `tests/` кожного пакета.

## Що створює скрипт

[setup_shops.py](setup_shops.py) на запущеному стеку:

1. Публікує й погоджує в Registry пакети з `packages/` і пакети збереження `jane.storage-files`, `jane.storage-postgresql`. Якщо версія вже є з іншим дайджестом, зупиняється з вимогою підняти версію пакета.
2. Створює в Orchestrator підключення `raw-files` і `results-pg` з [../documents/connections.json](../documents/connections.json).
3. Для кожного магазину створює (або замінює) джерело `shop-<магазин>` з лімітом 1 запит на секунду на хост і завдання `notebooks-<магазин>`:
   - `collect` — Web Collector, режим `full`, не глибше 1 рівня й не більше 10 сторінок за запуск;
   - `store-raw` — усі сторінки в `raw-files`;
   - `extract-offers` — HTML-сторінки екстрактору магазину;
   - `store-offers` — успішні результати в `results-pg`;
   - розклад — cron `0 9,21 * * *`, часовий пояс `Europe/Kyiv`, `overlap: skip`.
4. Запускає кожне завдання один раз, чекає завершення й друкує кількість пропозицій кожного магазину з `storage.v1`. З `--no-run` лише створює все без запуску.

Як Orchestrator виконує такі завдання — [виконання завдання](../../docs/architecture/task-execution.md).

## Запуск

Не перевірено в цій документації: сценарій звертається до справжніх магазинів.

1. Потрібен стек зі зв'язуванням сервісів за зразком [infra/compose.local.example.yaml](../../infra/compose.local.example.yaml): виконавці Orchestrator, адреси Registry, більший ліміт передачі сторінок для Web Collector. Як підняти — [платформа з Admin UI](../../docs/getting-started/platform.md).
2. Запустіть скрипт із назвою compose-проєкту стеку:

   ```powershell
   uv run --all-packages python examples/shops/setup_shops.py --project <проєкт>
   ```

   Параметри: `--no-run` — не запускати завдання; `--timeout` — секунд очікування одного запуску (типово 900).

3. Очікуваний результат: для кожного магазину рядок `run notebooks-<магазин>: succeeded …` і рядок `storage: <N> offers of shop-<магазин>`. Код виходу `1`, якщо хоча б один запуск не `succeeded`.

Створені джерела й завдання лишаються в Orchestrator і виконуються за розкладом, доки їх не видалити або не зупинити стек.

## Перевірка без сервісів

Тести пакетів і правил магазинів працюють без мережі й сервісів: тести маніфестів екстракторів на збережених сторінках і перевірка правил (схема, `robots.txt`, лише `seed_list`, не більше 5 URL).

```powershell
uv run --all-packages pytest examples/tests/test_shops.py -q
```

Вивід перевірочного запуску (2026-10-11, Windows 11, ревізія `48389a3`):

```text
.......                                                                  [100%]
7 passed in 1.12s
```

## Обмеження

- Розмітка магазинів змінюється: екстрактор може почати повертати `empty` або `unrecognized`; тоді потрібна нова версія пакета (і нові тестові сторінки).
- Частина магазинів може обмежувати автоматичні запити; колектор поважає `robots.txt` і ліміт частоти, але успіх не гарантовано.
- Сторінки реальних магазинів часто більші за типовий ліміт передачі вмісту в тілі відповіді (256 КіБ); без сховища blob такі сторінки завершуються помилкою `limit_exceeded`. У зразку `compose.local.example.yaml` для Web Collector ліміт `transfer.inline_max_bytes` піднято до 8 МіБ.
