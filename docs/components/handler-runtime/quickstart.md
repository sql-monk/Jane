# Handler Runtime: швидкий старт

Інструкція запускає Handler Runtime без інших модулів Jane: спочатку CLI на прикладі пакета екстрактора, потім HTTP-сервіс із викликом `POST /v1/invocations`. Пакет передається архівом у запиті, стан тримається в пам'яті.

Кроки виконано 2026-10-11 на Windows 11 з Docker Desktop 29.8 (Linux-контейнери), ревізія `c59d26d`, PowerShell 7. На Linux не перевірялися; команди `uv` ті самі, відрізняється лише спосіб задати змінні середовища — показано окремо.

## Зміст

- [Передумови](#передумови)
- [Образ пісочниці](#образ-пісочниці)
- [Тести пакета через CLI](#тести-пакета-через-cli)
- [Виклик на локальному файлі](#виклик-на-локальному-файлі)
- [HTTP-сервіс](#http-сервіс)
- [Прибирання](#прибирання)
- [Що далі](#що-далі)

## Передумови

- Checkout репозиторію, uv і Docker (Docker Desktop на Windows, Docker Engine на Linux) — встановлення в [середовищі розробки](../../development/environment.md).
- Залежності workspace встановлено з кореня репозиторію:

  ```powershell
  uv sync --all-packages
  ```

- Команди виконуються з кореня репозиторію. Приклад пакета — [testsite-product-extractor](../../../libs/extractor-sdk/examples/testsite-product-extractor/jane-package.json): картки товарів тестового сайту.

## Образ пісочниці

1. Зберіть образ профілю `python-extractor@1`. Команда надсилає Docker лише Dockerfile профілю, `requirements.txt` і код SDK:

   ```powershell
   uv run --package jane-handler-runtime jane-handler-runtime build-image
   ```

   Типовий тег — `jane/python-extractor:1` (параметр `profile_images`, [configuration.md](configuration.md#профілі-й-образи)). Журнал збирання йде в stderr, тег — у stdout. Уривок виводу перевірочного запуску, де образ зібрано з `--tag jane-doc-hr/python-extractor:1`, щоб не змінювати наявний:

   ```text
   Step 11/11 : CMD ["python", "-I", "-m", "jane_extractor_sdk.runner", "/work"]
    ---> Using cache
    ---> 289c3d00fdc9
   Successfully built 289c3d00fdc9
   Successfully tagged jane-doc-hr/python-extractor:1
   jane-doc-hr/python-extractor:1
   ```

   Якщо образ зібрано з іншим тегом, додавайте до команд `run` і `test` параметр `--image <тег>`.

2. Перегляньте бібліотеки профілю — лише їх пакет може вказати в `dependencies.python`:

   ```powershell
   uv run --package jane-handler-runtime jane-handler-runtime profile
   ```

   ```text
   python-extractor@1: Python 3.12
     beautifulsoup4==4.15.0
     cssselect==1.5.0
     html5lib==1.1
     jmespath==1.1.0
     jsonpath-ng==1.8.0
     lxml==6.1.3
     parsel==1.12.0
     python-dateutil==2.9.0.post0
     regex==2026.9.10
     selectolax==0.3.34
     six==1.17.0
     soupsieve==2.10
     typing-extensions==4.16.0
     w3lib==2.4.1
     webencodings==0.6.1
   ```

## Тести пакета через CLI

3. Проженіть тести маніфесту пакета. Кожен тест — окремий контейнер у тестовому режимі:

   ```powershell
   uv run --package jane-handler-runtime jane-handler-runtime test libs/extractor-sdk/examples/testsite-product-extractor
   ```

   Очікуваний результат — усі тести `PASS`, код виходу 0. Вивід перевірочного запуску (з `--image jane-doc-hr/python-extractor:1`):

   ```text
   package testsite.product-extractor@1.0.0 (sha256:b9cf7747029a7bbc8d24ad24c44ede0ae36595ec5d3ac1c7144dbbda4b722929), backend=docker
     PASS product-phone-alpha: expected success, got success
     PASS product-phone-gamma-out-of-stock: expected success, got success
     PASS category-page-empty: expected empty, got empty
     PASS unknown-page-empty: expected empty, got empty
     PASS product-without-price-unrecognized: expected unrecognized, got unrecognized
   5 passed, 0 failed
   ```

   Дайджест — SHA-256 канонічного zip-архіву каталогу пакета; той самий каталог дає той самий дайджест на Windows і Linux.

## Виклик на локальному файлі

4. Виконайте пакет на одній сторінці. `--url` стає `locator.url` матеріалу, `-o` записує `HandlerResult` у файл (без `-o` — у stdout):

   ```powershell
   uv run --package jane-handler-runtime jane-handler-runtime run libs/extractor-sdk/examples/testsite-product-extractor libs/extractor-sdk/examples/testsite-product-extractor/tests/product-phone-alpha/page.html --media-type text/html --url http://127.0.0.1:8080/product/phone-alpha -o result.json
   ```

   У перевірочному запуску додано `--image jane-doc-hr/python-extractor:1`. Код виходу 0 означає `success` або `empty`, 1 — `unrecognized` або `failed`, 2 — виклик не відбувся (недійсний пакет чи параметри, немає пісочниці). Уривок `result.json` (поля `observation` і `provenance` сутності пропущено):

   ```json
   {
     "invocation_id": "inv_dced1a740456410f9b5c14c593aca75e",
     "handler": {
       "package_id": "testsite.product-extractor",
       "version": "1.0.0",
       "digest": "sha256:b9cf7747029a7bbc8d24ad24c44ede0ae36595ec5d3ac1c7144dbbda4b722929"
     },
     "handler_kind": "extractor",
     "status": "success",
     "output": {
       "entities": [
         {
           "entity_type": "product",
           "fields": {
             "sku": "phone-alpha",
             "title": "Phone Alpha",
             "price": {"amount": 299.0, "currency": "UAH"},
             "availability": "in_stock",
             "url": "http://127.0.0.1:8080/product/phone-alpha"
           },
           "completeness": "full",
           "key": {"scope": "local", "natural": {"sku": "phone-alpha"}},
           "schema": "testsite.product-extractor@1.0.0#product"
         }
       ]
     },
     "test_mode": true,
     "duplicate": false,
     "delivery_key": "cli:obs_local_ed3d75422039bccf31d4544c",
     "diagnostics": {
       "metrics": {"duration_ms": 3016, "output_bytes": 392, "cpu_ms": 302, "peak_memory_mb": 14.4}
     }
   }
   ```

   `key` побудовано з `key_fields` маніфесту; область ключа `local`, бо матеріал із файлу не має `source.source_id` (задайте `--source-id`).

## HTTP-сервіс

5. Запустіть сервіс на `127.0.0.1:18301`. Без `JANE_HANDLER_RUNTIME_AUTH_MODE` сервіс приймає запити без ключа — лише для локальної роботи.

   PowerShell:

   ```powershell
   $env:JANE_HANDLER_RUNTIME_PORT = "18301"
   uv run --package jane-handler-runtime jane-handler-runtime serve
   ```

   Bash (не перевірено на Linux):

   ```bash
   JANE_HANDLER_RUNTIME_PORT=18301 uv run --package jane-handler-runtime jane-handler-runtime serve
   ```

   У перевірочному запуску образ задано змінною `JANE_HANDLER_RUNTIME_PROFILE_IMAGES='{"python-extractor@1": "jane-doc-hr/python-extractor:1"}'`. У журналі з'являється `Uvicorn running on http://127.0.0.1:18301` і попередження `auth_mode=none`. Попередження FastAPI `Duplicate Operation ID cancelJob` не впливає на роботу: сервіс замінює типове скасування job власним, яке ще й зупиняє контейнер.

6. У другому терміналі перевірте стан:

   ```powershell
   (Invoke-WebRequest http://127.0.0.1:18301/v1/health).Content
   ```

   ```json
   {"status":"ok","checks":{"sandbox":{"status":"ok"},"state":{"status":"ok"}}}
   ```

   `sandbox` — доступність Docker Engine, `state` — сховища стану.

7. Підготуйте запит `handler.v1`: пакет іде в `package_archive` як канонічний zip у base64, сторінка — як матеріал з inline-вмістом. Збережіть скрипт як `make_request.py` у будь-якому каталозі:

   ```python
   """Builds a handler.v1 request: the package goes inline as a canonical zip (base64)."""

   import base64
   import json
   import sys
   from pathlib import Path

   from jane_extractor_sdk.package import build_archive, load_manifest, material_from_file

   package_dir, page, url, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
   manifest = load_manifest(package_dir)
   request = {
       "handler": {"package_id": manifest["package_id"], "version": manifest["version"]},
       "package_archive": {
           "kind": "inline",
           "media_type": "application/zip",
           "encoding": "base64",
           "data": base64.b64encode(build_archive(package_dir)).decode("ascii"),
       },
       "inputs": [{"kind": "material", "material": material_from_file(page, media_type="text/html", url=url)}],
       "delivery": {"delivery_key": "quickstart-0001"},
   }
   out.write_text(json.dumps(request), encoding="utf-8")
   print(f"{out}: {out.stat().st_size} bytes")
   ```

   ```powershell
   uv run --package jane-handler-runtime python make_request.py libs/extractor-sdk/examples/testsite-product-extractor libs/extractor-sdk/examples/testsite-product-extractor/tests/product-phone-alpha/page.html http://127.0.0.1:8080/product/phone-alpha request.json
   ```

   ```text
   request.json: 23181 bytes
   ```

8. Викличте обробник. `Idempotency-Key` обов'язковий і має дорівнювати `delivery.delivery_key`.

   PowerShell:

   ```powershell
   $r = Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18301/v1/invocations -ContentType application/json -Headers @{ "Idempotency-Key" = "quickstart-0001" } -InFile request.json
   $r.StatusCode; ($r.Content | ConvertFrom-Json).output.entities[0].fields | ConvertTo-Json -Compress
   ```

   Bash (не перевірено на Linux):

   ```bash
   curl -s -X POST http://127.0.0.1:18301/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-0001' --data-binary @request.json
   ```

   Вивід PowerShell-варіанта:

   ```text
   200
   {"sku":"phone-alpha","title":"Phone Alpha","price":{"amount":299.0,"currency":"UAH"},"availability":"in_stock","url":"http://127.0.0.1:8080/product/phone-alpha"}
   ```

9. Повторіть той самий запит — це повторна доставка. Сервіс не запускає пісочницю вдруге, а повертає збережений результат:

   ```powershell
   $r = Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18301/v1/invocations -ContentType application/json -Headers @{ "Idempotency-Key" = "quickstart-0001" } -InFile request.json
   $r.Headers["Idempotency-Replayed"]; ($r.Content | ConvertFrom-Json) | Select-Object invocation_id, status, duplicate
   ```

   ```text
   true

   invocation_id                        status  duplicate
   -------------                        ------  ---------
   inv_ea3d8326cfec4339933caf517a3ba989 success      True
   ```

Асинхронний режим, тест-прогони й опитування job — [integration.md](integration.md).

## Прибирання

- Зупиніть сервіс через `Ctrl+C`. За штатної зупинки сервіс видаляє тимчасовий кеш пакетів (`%TEMP%\jane-packages-*` на Windows, `/tmp/jane-packages-*` на Linux). Після примусового завершення процесу каталог лишається — видаліть його вручну. Стан у пам'яті зникає разом із процесом.
- Видаліть `result.json`, `request.json` і `make_request.py`.
- Контейнери пісочниці сервіс видаляє сам після кожного виклику. Перевірка, що їх не лишилося (порожній вивід):

  ```powershell
  docker ps -a --filter label=io.jane.handler-runtime.sandbox=1 --format "{{.Names}}"
  ```

- Наступна команда видаляє образ пісочниці. Виконуйте її, лише якщо образ зібрано для цієї інструкції і ним не користуються інші стеки Jane:

  ```powershell
  docker image rm jane/python-extractor:1
  ```

## Що далі

- Написати власний екстрактор — [швидкий старт SDK](../extractor-sdk/quickstart.md).
- Налаштувати ліміти, автентифікацію, Registry і PostgreSQL — [configuration.md](configuration.md).
- Викликати сервіс зі свого застосунку — [integration.md](integration.md).
