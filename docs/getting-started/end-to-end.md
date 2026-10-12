# Наскрізний сценарій: від джерела до збережених сутностей

Сценарій піднімає ланцюжок Jane на Docker, публікує пакети в Registry, створює джерело й два незалежні завдання та виконує їх на тестовому магазині: повний каталог товарів і перевірку цін за розкладом. Результат — RAW-сторінки у файлах і картки товарів у MongoDB (колекція `product`), де перевірка цін оновила лише ціну й наявність.

Виконано 2026-10-12 на Windows 11, Docker Desktop, ревізія `f4eaf3f1`; на Linux не перевірявся. Передумови й підготовка — [початок роботи](README.md).

## Зміст

- [Що відбувається](#що-відбувається)
- [1. Запуск ланцюжка](#1-запуск-ланцюжка)
- [2. Виконання сценарію](#2-виконання-сценарію)
- [3. Перевірка результату](#3-перевірка-результату)
- [4. Прибирання](#4-прибирання)
- [Типові проблеми](#типові-проблеми)

## Що відбувається

| Крок | Модуль | Дія |
|---|---|---|
| `publish` | Registry | публікує й погоджує 7 пакетів: правила колектора, два екстрактори, пакети збереження `jane.storage-files` і `jane.storage-mongodb`, пакети Telegram-прикладу |
| `apply` | Orchestrator | створює підключення `raw-files` і `results-mongo`, джерело `testsite-shop` і завдання `testsite-catalog` |
| `catalog` | Orchestrator → Web Collector, Storage, Handler Runtime | запуск повного каталогу: сторінки категорій із пагінацією → RAW у файлах, картки товарів → MongoDB |
| `price-check` | Orchestrator | створює завдання `testsite-price-check` з розкладом і чекає його першого запуску за розкладом: 4 URL товарів → лише `price` і `availability` |
| `verify` | Storage, Orchestrator | перевіряє результат через публічні API читання |

Документи джерела, завдань і підключень — [examples/documents](../../examples/documents/); пакети — [examples/packages](../../examples/packages/). Як етапи завдання проходять дані — [виконання завдання](../architecture/task-execution.md).

## 1. Запуск ланцюжка

Ланцюжок піднімає `deploy/profiles/stack.py`: він додає до `infra/compose.yaml` зв'язування сервісів (виконавці Orchestrator, адреси Registry), профіль лімітів `dev-laptop` і образ пісочниці екстракторів. Звичайний `just up` такого зв'язування не робить — [чому](platform.md#звязування-сервісів).

```powershell
uv run --all-packages python deploy/profiles/stack.py up --project jane-doc-start
```

Перший запуск збирає образи сервісів і пісочниці — кілька хвилин. Порти на `127.0.0.1` обирає Docker; у перевірочному запуску їх зафіксовано змінними `JANE_PORT_<СЕРВІС>`. Кінець виводу:

```text
project: jane-doc-start   profile: dev-laptop   stack file: C:/repos/Jane/.jane/stack-jane-doc-start.json
  testsite           http://127.0.0.1:18904
  registry           http://127.0.0.1:18911
  storage            http://127.0.0.1:18906
  handler-runtime    http://127.0.0.1:18907
  web-collector      http://127.0.0.1:18908
  orchestrator       http://127.0.0.1:18910
  mongodb            127.0.0.1:18912
```

Стек складається з testsite, Registry, Storage, Handler Runtime, Web Collector, Orchestrator, а також PostgreSQL, MinIO і MongoDB як їхніх залежностей. MongoDB стартує разом зі Storage для підключення `results-mongo`; її адреса — останній рядок виводу. Сервіси працюють у режимі `api_key`; ключі згенеровано в `.jane/stack-jane-doc-start.json`. Адреси без секретів показує команда:

```powershell
uv run --all-packages python deploy/profiles/stack.py env --project jane-doc-start
```

## 2. Виконання сценарію

```powershell
uv run --all-packages python examples/jane_examples.py demo --project jane-doc-start
```

Сценарій тривав менше хвилини. Вивід перевірочного запуску (час — UTC); уривок: у JSON-підсумку показано один товар із чотирьох:

```text
[23:58:11Z] registry: jane.storage-files@1.0.0 sha256:b87649411631a78b58f4e44e304dab362526e21861705a2e04f8a8a6d6aec12f approved
[23:58:11Z] registry: jane.storage-mongodb@2.0.0 sha256:2307eeb9e72b59a234f812a9f8dc716b05a9ac4643e843a520dac2ba3d8faad3 approved
[23:58:11Z] registry: examples.testsite-web-rules@1.0.0 sha256:db018cbb61ab3d33b74033494bb293530954279a176a34ab043de7af16e36d7d approved
[23:58:11Z] registry: examples.testsite-catalog-extractor@1.0.0 sha256:5d5df84301dad59b47d4fc3a087de46f6cac12e01a7617579421178b125c84e2 approved
[23:58:12Z] registry: examples.testsite-price-extractor@1.0.0 sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9 approved
[23:58:12Z] registry: examples.telegram-rules@1.0.0 sha256:cc734c10a59bb73d2dda0fc1c1c8fdb228c56a993aa43c39eb78067d68332eba approved
[23:58:12Z] registry: examples.telegram-event-extractor@1.0.0 sha256:37143cc4a36963d4825aac6fd7cac108f1479005af26ab24309d499859f17d55 approved
[23:58:12Z] orchestrator: source testsite-shop -> 201
[23:58:12Z] orchestrator: task testsite-catalog -> 201 (warnings: 0)
[23:58:12Z] catalog: run run_01M4PPE51SAX3V30QGZBNW2T11 started
[23:58:36Z] catalog: run run_01M4PPE51SAX3V30QGZBNW2T11 succeeded
[23:58:36Z] orchestrator: task testsite-price-check -> 201 (warnings: 0)
[23:58:36Z] price-check: first scheduled run at 2026-10-11T23:58:51Z
[23:58:52Z] price-check: scheduled run run_01M4PPFB9168MXQ2RKPYHE7KSN started
[23:58:56Z] price-check: run run_01M4PPFB9168MXQ2RKPYHE7KSN succeeded
{
  "ok": true,
  "failures": [],
  "raw_objects": 23,
  "entities": 16,
  "catalog_run": "run_01M4PPE51SAX3V30QGZBNW2T11",
  "price_check_run": "run_01M4PPFB9168MXQ2RKPYHE7KSN",
  "partial_updates": {
    "laptop-four": {
      "completeness": "partial",
      "record_fields": [
        "availability",
        "price",
        "sku"
      ],
      "applied_fields": [
        "availability",
        "price",
        "sku"
      ],
      "package": {
        "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9",
        "version": "1.0.0",
        "package_id": "examples.testsite-price-extractor"
      },
      "state_fields": [
        "availability",
        "category",
        "price",
        "sku",
        "title",
        "url"
      ],
      "state_version": 2,
      "price_observation_is_price_check": true,
      "title_observation_kept_from_catalog": true
    },
    … ще 3 товари з тими самими полями …
  },
  "platform_profile": "dev-laptop"
}
summary: .jane/examples-jane-doc-start.json
```

Що означає результат:

- `"ok": true` — усі перевірки `verify` пройшли.
- `raw_objects: 23` — Storage зберіг усі 23 сторінки каталогу як RAW у підключенні `raw-files`.
- `entities: 16` — 16 карток товарів у підключенні сутностей `results-mongo` з усіма полями картки. У базі `jane_results` це колекція `product` (16 документів) і її історія `product.history` (20 версій: 16 із каталогу й 4 з перевірки цін).
- `partial_updates` — для кожного з 4 товарів перевірки цін запис має `completeness: partial` і лише поля `price`, `availability`, `sku`; поля `title`, `category`, `url` лишилися з повного каталогу, версія стану — 2.

Лічильники етапів запуску каталогу з підсумку `.jane/examples-jane-doc-start.json`: `collect` — 23 матеріали, `store-raw` — 23 успішні записи, `extract-products` і `store-products` — по 16 (екстрактор отримує лише сторінки `*/product/*`). Решта 7 матеріалів — сторінки, що не є товарами, — враховано як невідомі (`unknown_materials: 7`): їм не відповідає жоден прив'язаний екстрактор, а `forward_unknown_to_llm` вимкнено, тож LLM не викликався.

Кожен крок можна виконати окремо: `publish`, `apply`, `catalog`, `price-check`, `verify` — з тими самими аргументами.

## 3. Перевірка результату

Сутності читаються з Storage через `storage.v1`. Ключ адміністратора стеку лежить у файлі стеку; не виводьте його в журнали.

PowerShell:

```powershell
$key = (Get-Content .jane/stack-jane-doc-start.json | ConvertFrom-Json).env.JANE_API_KEY_ADMIN
$r = Invoke-RestMethod -Headers @{Authorization = "Bearer $key"} -Uri "http://127.0.0.1:18906/v1/entities?connection_id=results-mongo&entity_type=product&scope=testsite-shop&limit=100"
$r.items | ForEach-Object { [pscustomobject]@{sku = $_.fields.sku; price = $_.fields.price.amount; availability = $_.fields.availability; version = $_.version} } | Format-Table -AutoSize
```

Bash:

```bash
key=$(python -c "import json; print(json.load(open('.jane/stack-jane-doc-start.json'))['env']['JANE_API_KEY_ADMIN'])")
curl -s -H "Authorization: Bearer $key" "http://127.0.0.1:18906/v1/entities?connection_id=results-mongo&entity_type=product&scope=testsite-shop&limit=100"
```

Замініть порт `18906` на адресу `storage` зі свого виводу кроку 1. Вивід PowerShell перевірочного запуску:

```text
sku              price availability version
---              ----- ------------ -------
case-red         19,00 in_stock           1
charger-fast     29,00 in_stock           1
headphones-pro  149,00 in_stock           1
laptop-five    1299,00 in_stock           1
laptop-four    1199,00 out_of_stock       2
laptop-one      899,00 in_stock           1
laptop-three   1099,00 in_stock           1
laptop-two      999,00 in_stock           1
phone-alpha     299,00 in_stock           2
phone-beta      349,00 in_stock           1
phone-delta     449,00 in_stock           1
phone-epsilon   499,00 in_stock           1
phone-eta       599,00 in_stock           1
phone-gamma     399,00 out_of_stock       2
phone-zeta      549,00 preorder           2
stand-desk       39,00 in_stock           1
```

Версію 2 мають саме ті 4 товари, які читало завдання перевірки цін. Bash-варіант повертає ту саму відповідь у JSON: `items` з полями `entity_type`, `canonical_key`, `key`, `fields`, `field_orders`, `version` і курсор `next_cursor`.

RAW-сторінки повертає `GET /v1/objects?connection_id=raw-files&source_id=testsite-shop` того самого сервісу; кожен об'єкт містить шлях файлу в томі Storage і метадані матеріалу (`material_id`, `observation_id`, `url`, `fetched_at`).

## 4. Прибирання

Команда нижче зупиняє стек і **видаляє всі його дані**: контейнери, томи баз і сховищ, локально зібрані образи сервісів і пісочниці, файл `.jane/stack-jane-doc-start.json` з ключами, файл виконавців і копію записів Telegram.

```powershell
uv run --all-packages python deploy/profiles/stack.py down --project jane-doc-start
```

Очікуваний результат — порожній перелік залишків:

```json
{
  "project": "jane-doc-start",
  "leftovers": {}
}
```

Підсумок сценарію `.jane/examples-jane-doc-start.json` команда не видаляє; видаліть файл, якщо він не потрібен.

## Типові проблеми

| Ознака | Причина й дія |
|---|---|
| `POST /v1/packages/examples.testsite-catalog-extractor/versions -> 422` з `unknown runtime profile python-extractor@1; known: none configured` | стек піднято звичайним `just up` без зв'язування: Registry не знає профілів Handler Runtime. Підніміть стек через `deploy/profiles/stack.py up` |
| `no stack file .jane/stack-<project>.json` | стек із цією назвою проєкту не запущено; назва в `--project` має збігатися в усіх командах |
| `stack <project> has no registry, orchestrator` | стек піднято без потрібних сервісів; типовий набір `stack.py up` містить усі потрібні |
| запуск `failed` або `TimeoutError` | журнал сервісу: `docker logs jane-doc-start-orchestrator-1`; час очікування задає `--timeout` (типово 600 с на запуск) |
