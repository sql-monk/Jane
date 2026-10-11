# Storage: швидкий старт

Запуск Storage окремо, без Docker, Orchestrator і Registry: файловий адаптер записує HTML-сторінку й сутність товару, повтор того самого `delivery_key` повертає дубль, запізніле спостереження потрапляє лише в історію, а API читання повертає результат.

Кроки виконано 2026-10-11 на Windows 11 (PowerShell і Git Bash), ревізія `c59d26d`, з `JANE_STORAGE_PORT=18200`; нижче — типовий порт `8107`. На Linux команди Bash не перевірялися.

## Зміст

- [Передумови](#передумови)
- [Запуск сервісу](#запуск-сервісу)
- [Підготовка запитів](#підготовка-запитів)
- [Запис і дубль](#запис-і-дубль)
- [Запізніле спостереження](#запізніле-спостереження)
- [Читання результатів](#читання-результатів)
- [Що лежить у каталозі](#що-лежить-у-каталозі)
- [Прибирання](#прибирання)
- [Далі](#далі)

## Передумови

- uv і Python 3.12+ — [середовище розробки](../../development/environment.md).
- Команди виконуються з кореня репозиторію. Відносний `base_path` підключення адаптер рахує від робочого каталогу сервісу, тобто від кореня.

## Запуск сервісу

1. Встановіть залежності workspace. Адаптери — окремі пакети, тому потрібен `--all-packages`:

   ```powershell
   uv sync --all-packages
   ```

2. У першому терміналі запустіть Storage:

   ```powershell
   uv run --all-packages python -m jane_storage
   ```

   У журналі (JSON) з'являються рядки `storage ready` зі списком адаптерів і пакетів та `Uvicorn running on http://127.0.0.1:8107`. Попередження `auth_mode=none` означає, що сервіс приймає запити без ключа — лише для локальної роботи.

3. У другому терміналі перевірте health:

   ```powershell
   (Invoke-WebRequest -Uri http://127.0.0.1:8107/v1/health).Content
   ```

   ```text
   {"status":"ok","checks":{}}
   ```

## Підготовка запитів

Створіть каталог `.jane/storage-quickstart` (він поза Git) і три файли в ньому.

`connection.json` — підключення файлового адаптера; секретів воно не потребує:

```json
{
  "connection_id": "quickstart-files",
  "kind": "filesystem",
  "title": "Quickstart files",
  "params": {"base_path": ".jane/storage-quickstart/data"}
}
```

`write-1.json` — один виклик із двома входами: HTML-сторінка (RAW) і сутність товару:

```json
{
  "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
  "connections": {"target": "quickstart-files"},
  "delivery": {"delivery_key": "quickstart-1"},
  "inputs": [
    {
      "kind": "material",
      "material": {
        "material_id": "web:quickstart-a-100",
        "observation_id": "obs_quickstart_0001",
        "source": {"kind": "web", "source_id": "shop-example"},
        "locator": {"url": "https://shop.example.test/product/a-100"},
        "fetched_at": "2026-10-11T10:00:00Z",
        "format": {"media_type": "text/html"},
        "revision": {"content_sha256": "06f441ff0f8d8018b29669de7ef7675f11bffe23d07ff62ee8696aae8c922ba1"},
        "content": {"kind": "inline", "media_type": "text/html", "encoding": "utf-8", "data": "<html><body><h1>Kettle A-100</h1><p>1299 UAH</p></body></html>"},
        "collector": {"name": "manual", "version": "0"}
      }
    },
    {
      "kind": "entities",
      "entities": [
        {
          "entity_type": "product",
          "key": {"scope": "shop-example", "natural": {"sku": "A-100"}},
          "fields": {"title": "Kettle A-100", "price": 1299},
          "observation": {"observation_id": "obs_quickstart_0001", "observed_at": "2026-10-11T10:00:00Z"}
        }
      ]
    }
  ]
}
```

`write-2.json` — ціна того самого товару, але зі **старішого** спостереження (`observed_at` на годину раніше):

```json
{
  "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
  "connections": {"target": "quickstart-files"},
  "delivery": {"delivery_key": "quickstart-2"},
  "inputs": [
    {
      "kind": "entities",
      "entities": [
        {
          "entity_type": "product",
          "key": {"scope": "shop-example", "natural": {"sku": "A-100"}},
          "fields": {"price": 1199},
          "observation": {"observation_id": "obs_quickstart_0000", "observed_at": "2026-10-11T09:00:00Z"}
        }
      ]
    }
  ]
}
```

Поля `Material` і `EntityRecord` описані в [material.schema.json](../../../contracts/schemas/material.schema.json) і [entity.schema.json](../../../contracts/schemas/entity.schema.json). `revision.content_sha256` — SHA-256 рядка `data`.

## Запис і дубль

1. Зареєструйте підключення.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Put -Uri http://127.0.0.1:8107/v1/connections/quickstart-files -ContentType application/json -InFile .jane/storage-quickstart/connection.json).StatusCode
   ```

   Bash:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' -X PUT http://127.0.0.1:8107/v1/connections/quickstart-files -H 'Content-Type: application/json' --data-binary @.jane/storage-quickstart/connection.json
   ```

   Очікуваний результат — `201` (підключення створено); повторний `PUT` того самого документа дає `200`.

2. Надішліть запис. Заголовок `Idempotency-Key` обов'язковий і має дорівнювати `delivery.delivery_key`.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8107/v1/invocations -ContentType application/json -Headers @{"Idempotency-Key" = "quickstart-1"} -InFile .jane/storage-quickstart/write-1.json).Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:8107/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-1' --data-binary @.jane/storage-quickstart/write-1.json
   ```

   Уривок відповіді `HandlerResult` (відформатовано; `invocation_id`, `started_at`, `finished_at` і `handler.digest` пропущено):

   ```json
   {
     "handler_kind": "storage",
     "status": "success",
     "delivery_key": "quickstart-1",
     "output": {
       "writes": [
         {
           "status": "written",
           "target": {"adapter": "filesystem", "connection_id": "quickstart-files"},
           "object": {
             "object_id": "obj_358c44b3866e4b33bd68301a1b96b90e",
             "adapter": "filesystem",
             "locator": {"path": "objects/shop-example/2026/10/11/web_quickstart-a-100/obs_quickstart_0001.html"},
             "media_type": "text/html",
             "size_bytes": 62,
             "sha256": "06f441ff0f8d8018b29669de7ef7675f11bffe23d07ff62ee8696aae8c922ba1",
             "connection_id": "quickstart-files"
           },
           "delivery_key": "quickstart-1"
         },
         {
           "status": "written",
           "target": {"adapter": "filesystem", "connection_id": "quickstart-files"},
           "entity": {"entity_type": "product", "canonical_key": "shop-example|{\"sku\":\"A-100\"}", "version": 1},
           "applied_fields": ["price", "title"],
           "stale_fields": [],
           "delivery_key": "quickstart-1#0"
         }
       ]
     },
     "duplicate": false
   }
   ```

   RAW-сторінка отримала ключ доставки виклику (`quickstart-1`), сутність — `quickstart-1#0`.

3. Повторіть ту саму команду. Відповідь має `"duplicate": true`, обидва підтвердження — `"status": "duplicate"` з тими самими `object_id` і `version: 1`; нового запису немає. Заголовок відповіді `Idempotency-Replayed: true` показує, що цей екземпляр уже бачив ключ.

## Запізніле спостереження

Надішліть `write-2.json` з ключем `quickstart-2`.

PowerShell:

```powershell
(Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8107/v1/invocations -ContentType application/json -Headers @{"Idempotency-Key" = "quickstart-2"} -InFile .jane/storage-quickstart/write-2.json).Content
```

Bash:

```bash
curl -s -X POST http://127.0.0.1:8107/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-2' --data-binary @.jane/storage-quickstart/write-2.json
```

Уривок відповіді:

```json
{
  "status": "success",
  "output": {
    "writes": [
      {
        "status": "stale",
        "target": {"adapter": "filesystem", "connection_id": "quickstart-files"},
        "entity": {"entity_type": "product", "canonical_key": "shop-example|{\"sku\":\"A-100\"}", "version": 2},
        "applied_fields": [],
        "stale_fields": ["price"],
        "delivery_key": "quickstart-2#0"
      }
    ]
  },
  "duplicate": false
}
```

Ціна `1199` старіша за збережену `1299`, тому поточний стан не змінився, але версія зросла до `2`: оновлення записане в історію з `stale_fields: ["price"]`.

## Читання результатів

1. Поточний стан сутностей типу `product`:

   ```powershell
   (Invoke-WebRequest -Uri "http://127.0.0.1:8107/v1/entities?connection_id=quickstart-files&entity_type=product").Content
   ```

   ```json
   {"items":[{"entity_type":"product","canonical_key":"shop-example|{\"sku\":\"A-100\"}","key":{"natural":{"sku":"A-100"},"scope":"shop-example"},"fields":{"price":1299,"title":"Kettle A-100"},"field_orders":{"price":{"observed_at":"2026-10-11T10:00:00.000000Z","observation_id":"obs_quickstart_0001"},"title":{"observed_at":"2026-10-11T10:00:00.000000Z","observation_id":"obs_quickstart_0001"}},"cleared_fields":[],"version":2,"updated_at":"2026-10-11T10:00:39.094204Z"}],"next_cursor":null}
   ```

2. Історія сутності. Канонічний ключ передається в параметрі `key` і має бути закодований для URL.

   PowerShell:

   ```powershell
   $key = [uri]::EscapeDataString('shop-example|{"sku":"A-100"}')
   (Invoke-WebRequest -Uri "http://127.0.0.1:8107/v1/entity-history?connection_id=quickstart-files&entity_type=product&key=$key").Content
   ```

   Bash:

   ```bash
   curl -s --get http://127.0.0.1:8107/v1/entity-history --data-urlencode connection_id=quickstart-files --data-urlencode entity_type=product --data-urlencode 'key=shop-example|{"sku":"A-100"}'
   ```

   Відповідь містить два записи, новіший перший: запізнілий (`delivery_key: quickstart-2#0`, `stale_fields: ["price"]`) і початковий (`quickstart-1#0`, `applied_fields: ["price", "title"]`).

3. Збережені об'єкти й вміст сторінки:

   ```powershell
   (Invoke-WebRequest -Uri "http://127.0.0.1:8107/v1/objects?connection_id=quickstart-files").Content
   (Invoke-WebRequest -Uri "http://127.0.0.1:8107/v1/objects/obj_358c44b3866e4b33bd68301a1b96b90e/content?connection_id=quickstart-files").Content
   ```

   Перша команда повертає один елемент з `object` (той самий `object_id`) і зведенням `material` (`material_id`, `source_id`, `url`, `fetched_at`). Друга — байти сторінки без змін:

   ```text
   <html><body><h1>Kettle A-100</h1><p>1299 UAH</p></body></html>
   ```

## Що лежить у каталозі

Файловий адаптер створив у `.jane/storage-quickstart/data` таку структуру (імена з хешем — SHA-256 ключа):

```text
data/
├── deliveries/<sha256(delivery_key)>.json          # 3 записи доставки: quickstart-1, quickstart-1#0, quickstart-2#0
├── entities/product/<sha256(canonical_key)>.json   # поточний стан, version 2
├── history/product/<sha256(canonical_key)>/
│   ├── 000000000001.json                           # перше оновлення
│   └── 000000000002.json                           # запізніле оновлення
├── index/objects/obj_358c44b3866e4b33bd68301a1b96b90e.json
└── objects/shop-example/2026/10/11/web_quickstart-a-100/
    ├── obs_quickstart_0001.html                    # сторінка байт-у-байт
    └── obs_quickstart_0001.html.meta.json          # метадані Material
```

Призначення кожного файлу — [адаптери: filesystem](adapters.md#filesystem).

## Прибирання

1. Зупиніть сервіс у першому терміналі через `Ctrl+C`. Підключення `quickstart-files` зникне разом із процесом: воно зберігалося лише в пам'яті.
2. Команда нижче **видаляє всі записані дані** прикладу (RAW, сутності, історію, записи доставок) і файли запитів.

   PowerShell:

   ```powershell
   Remove-Item -Recurse -Force .jane/storage-quickstart
   ```

   Bash:

   ```bash
   rm -rf .jane/storage-quickstart
   ```

## Далі

- Той самий сценарій із PostgreSQL та іншими сховищами — [адаптери](adapters.md) і [інтеграція](integration.md#самостійне-використання).
- Тести пакета (`POST /v1/test-runs`), підключення з секретами, читання великих RAW — [інтеграція](integration.md).
