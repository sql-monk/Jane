# Registry: швидкий старт

Запускає Registry без PostgreSQL, MinIO та інших сервісів Jane і проводить пакет через основні операції: публікацію, незмінність версії, погодження, форк, diff, експорт і офлайн-перевірку. Кроки виконано 2026-10-11 на Windows 11 (PowerShell 7) з ревізії `48389a3`; варіант Bash перевірено в Git Bash на тому самому комп'ютері, на Linux не перевірявся.

## Зміст

- [Передумови](#передумови)
- [Запуск](#запуск)
- [Публікація пакета](#публікація-пакета)
- [Погодження й форк](#погодження-й-форк)
- [Експорт і перевірка](#експорт-і-перевірка)
- [Прибирання](#прибирання)
- [Що далі](#що-далі)

## Передумови

- Встановлений [uv](https://docs.astral.sh/uv/); залежності workspace підтягуються першим `uv run`.
- Команди виконуються з кореня репозиторію в двох терміналах: у першому працює сервіс, у другому — запити.
- Вільний порт 18400 на `127.0.0.1` (типовий порт Registry — 8105; тут його змінено змінною `JANE_REGISTRY_PORT`).

У цьому режимі метадані живуть у пам'яті процесу й зникають після зупинки, а архіви записуються в каталог `.jane/registry-quickstart` (він поза Git). Профіль runtime `python-extractor@1` береться з файлу Handler Runtime, тож сам Handler Runtime запускати не потрібно.

## Запуск

1. У першому терміналі задайте режим без зовнішніх сервісів і запустіть Registry.

   PowerShell:

   ```powershell
   $env:JANE_REGISTRY_DB = "memory"
   $env:JANE_REGISTRY_BLOB = "filesystem"
   $env:JANE_REGISTRY_BLOB_ROOT = ".jane/registry-quickstart"
   $env:JANE_REGISTRY_PORT = "18400"
   $env:JANE_REGISTRY_RUNTIME_PROFILES = '["services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json"]'
   uv run --package jane-registry python -m jane_registry
   ```

   Bash:

   ```bash
   JANE_REGISTRY_DB=memory JANE_REGISTRY_BLOB=filesystem JANE_REGISTRY_BLOB_ROOT=.jane/registry-quickstart \
   JANE_REGISTRY_PORT=18400 \
   JANE_REGISTRY_RUNTIME_PROFILES='["services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json"]' \
   uv run --package jane-registry python -m jane_registry
   ```

   Журнал — JSON-рядки в stdout. Серед них (уривок, поля `ts` і `instance` прибрано):

   ```text
   {"level": "warning", "logger": "jane.auth", "msg": "auth_mode=none: every caller has every scope - for local tests only", "service": "registry"}
   {"level": "info", "logger": "uvicorn.error", "msg": "Uvicorn running on http://127.0.0.1:18400 (Press CTRL+C to quit)", "service": "registry"}
   ```

   Попередження `auth_mode=none` означає, що сервіс приймає запити без ключа з усіма правами — лише для локальної роботи. Рядок `registry started` містить ефективні ліміти.

2. У другому терміналі перевірте стан.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Uri http://127.0.0.1:18400/v1/health).Content
   ```

   Bash:

   ```bash
   curl -s http://127.0.0.1:18400/v1/health
   ```

   ```json
   {"status":"ok","checks":{"metadata_store":{"status":"ok"},"blob_store":{"status":"ok"}}}
   ```

## Публікація пакета

Опублікуємо екстрактор [examples.testsite-price-extractor](../../../examples/packages/examples.testsite-price-extractor/) з репозиторію.

3. Створіть пакет. Кожен `POST` Registry вимагає заголовок `Idempotency-Key`: повтор із тим самим ключем повертає ту саму відповідь і нічого не створює вдруге.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18400/v1/packages -ContentType application/json -Headers @{'Idempotency-Key' = 'qs-create'} -Body '{"package_id": "examples.testsite-price-extractor", "kind": "extractor", "title": "Jane test site: price and availability only"}').Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18400/v1/packages -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-create' -d '{"package_id": "examples.testsite-price-extractor", "kind": "extractor", "title": "Jane test site: price and availability only"}'
   ```

   ```json
   {"package_id":"examples.testsite-price-extractor","kind":"extractor","title":"Jane test site: price and availability only","latest_version":null,"auto_changes_allowed":true,"deprecated":false,"created_at":"2026-10-11T10:28:33.602Z","updated_at":"2026-10-11T10:28:33.602Z","forks_count":0}
   ```

4. Зберіть канонічний архів каталогу пакета (команда однакова для обох оболонок):

   ```powershell
   uv run --package jane-registry jane-registry archive examples/packages/examples.testsite-price-extractor --out .jane/registry-quickstart/price-1.0.0.zip
   ```

   ```text
   .jane\registry-quickstart\price-1.0.0.zip  sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9
   ```

   Той самий дайджест записано в [examples/packages.lock.json](../../../examples/packages.lock.json). На Linux шлях у виводі буде з `/`.

5. Опублікуйте версію.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions -ContentType application/zip -Headers @{'Idempotency-Key' = 'qs-publish'} -InFile .jane/registry-quickstart/price-1.0.0.zip).StatusCode
   ```

   Bash:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions -H 'Content-Type: application/zip' -H 'Idempotency-Key: qs-publish' --data-binary @.jane/registry-quickstart/price-1.0.0.zip
   ```

   ```text
   201
   ```

6. Перегляньте версії пакета.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Uri http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions).Content
   ```

   Bash:

   ```bash
   curl -s http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions
   ```

   ```json
   {"items":[{"package_id":"examples.testsite-price-extractor","version":"1.0.0","digest":"sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9","status":"draft","test_status":"unknown","size_bytes":13587,"created_at":"2026-10-11T10:28:42.530Z","created_by":"human","published_by":"anonymous"}],"next_cursor":null}
   ```

   `digest` збігається з дайджестом кроку 4. Нова версія — `draft`; тестів ще ніхто не записав, тому `test_status: unknown`. Повна версія з маніфестом, переліком файлів і історією статусів — `GET /v1/packages/examples.testsite-price-extractor/versions/1.0.0`.

7. Переконайтеся, що версія незмінна: та сама публікація з новим ключем відхиляється.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -SkipHttpErrorCheck -Method Post -Uri http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions -ContentType application/zip -Headers @{'Idempotency-Key' = 'qs-publish-again'} -InFile .jane/registry-quickstart/price-1.0.0.zip).StatusCode
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions -H 'Content-Type: application/zip' -H 'Idempotency-Key: qs-publish-again' --data-binary @.jane/registry-quickstart/price-1.0.0.zip
   ```

   PowerShell друкує `409`; Bash — тіло помилки:

   ```json
   {"type":"urn:jane:problem:version_exists","title":"Version exists","status":409,"detail":"version 1.0.0 already exists; versions are immutable","instance":"/v1/packages/examples.testsite-price-extractor/versions","code":"version_exists","retryable":false,"trace_id":"51e95af6c8647479add5bd603ed7ab53"}
   ```

## Погодження й форк

8. Погодьте версію.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions/1.0.0/status -ContentType application/json -Headers @{'Idempotency-Key' = 'qs-approve'} -Body '{"status": "approved", "reason": "quickstart"}').StatusCode
   ```

   Bash:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/versions/1.0.0/status -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-approve' -d '{"status": "approved", "reason": "quickstart"}'
   ```

   ```text
   200
   ```

9. Створіть форк — незалежну копію з посиланням на батька.

   PowerShell:

   ```powershell
   (Invoke-WebRequest -Method Post -Uri http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/forks -ContentType application/json -Headers @{'Idempotency-Key' = 'qs-fork'} -Body '{"new_package_id": "my.price-extractor", "from_version": "1.0.0", "title": "My price extractor"}').Content
   ```

   Bash:

   ```bash
   curl -s -X POST http://127.0.0.1:18400/v1/packages/examples.testsite-price-extractor/forks -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-fork' -d '{"new_package_id": "my.price-extractor", "from_version": "1.0.0", "title": "My price extractor"}'
   ```

   ```json
   {"package_id":"my.price-extractor","kind":"extractor","title":"My price extractor","latest_version":"1.0.0","auto_changes_allowed":false,"deprecated":false,"created_at":"2026-10-11T10:28:43.043Z","updated_at":"2026-10-11T10:28:43.306Z","fork_of":{"package_id":"examples.testsite-price-extractor","version":"1.0.0","digest":"sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"},"forks_count":0}
   ```

   Форк одразу має версію `1.0.0` з файлами батька; `auto_changes_allowed: false` захищає його від автоматичних змін LLM.

10. Порівняйте форк із батьком. Для першої версії форку `from` за замовчуванням — версія батька з `fork_of`.

    PowerShell:

    ```powershell
    (Invoke-WebRequest -Uri "http://127.0.0.1:18400/v1/packages/my.price-extractor/diff?to=1.0.0").Content
    ```

    Bash:

    ```bash
    curl -s "http://127.0.0.1:18400/v1/packages/my.price-extractor/diff?to=1.0.0"
    ```

    Уривок відповіді (з десяти файлів показано два, усі мають `unchanged`):

    ```json
    {
      "from": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0", "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"},
      "to": {"package_id": "my.price-extractor", "version": "1.0.0", "digest": "sha256:0c5780cbe5359a4897c309173ae653d64b47fc020f62f2e3a0d07db3fdc8e13c"},
      "manifest_changes": [
        {"pointer": "/fork_of", "op": "add", "new": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0", "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"}},
        {"pointer": "/package_id", "op": "replace", "old": "examples.testsite-price-extractor", "new": "my.price-extractor"},
        {"pointer": "/provenance/based_on", "op": "add", "new": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0", "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9"}},
        {"pointer": "/provenance/change_summary", "op": "replace", "old": "Partial price and availability update for the reproducible price-check example.", "new": "Fork of examples.testsite-price-extractor@1.0.0."},
        {"pointer": "/provenance/created_at", "op": "remove", "old": "2026-09-30T00:00:00Z"}
      ],
      "files": [
        {"path": "schemas/params.schema.json", "status": "unchanged"},
        {"path": "src/jane_example_price/main.py", "status": "unchanged"}
      ]
    }
    ```

    Код і схеми не змінилися; відрізняється лише маніфест: новий `package_id`, `fork_of` і походження.

## Експорт і перевірка

11. Експортуйте погоджену версію для використання без Registry (однаково для обох оболонок):

    ```powershell
    uv run --package jane-registry jane-registry export examples.testsite-price-extractor@1.0.0 --registry http://127.0.0.1:18400 --out .jane/registry-quickstart/export
    ```

    ```text
    examples.testsite-price-extractor@1.0.0  sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9  .jane\registry-quickstart\export\examples.testsite-price-extractor-1.0.0.zip
    ```

12. Перевірте архів офлайн:

    ```powershell
    uv run --package jane-registry jane-registry verify .jane/registry-quickstart/export/examples.testsite-price-extractor-1.0.0.zip
    ```

    Уривок (поле `path` прибрано):

    ```json
    {
      "ok": true,
      "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9",
      "package": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0", "kind": "extractor"},
      "checks": {"digest": true, "canonical": true, "manifest": true, "scan_limit": true, "secrets": true},
      "errors": []
    }
    ```

    Код виходу `0`. Цей архів можна виконати Handler Runtime без Registry — приклад запуску тестів і запису звіту у версію наведено в [Схеми й тести](../../reference/packages/schemas-and-tests.md#запуск-тестів).

## Прибирання

13. Зупиніть Registry в першому терміналі через `Ctrl+C`. Метадані зникають разом із процесом.

14. Команда нижче видаляє каталог `.jane/registry-quickstart` з архівами, зібраним ZIP і експортом цього сценарію.

    PowerShell:

    ```powershell
    Remove-Item -Recurse -Force .jane/registry-quickstart
    ```

    Bash:

    ```bash
    rm -rf .jane/registry-quickstart
    ```

## Що далі

- Запуск із PostgreSQL і MinIO, моніторинг і резервування — [operations.md](operations.md).
- Усі змінні середовища й ліміти — [configuration.md](configuration.md).
- Перенесення змін батька у форк, пошук пакетів, звіти тестів, автентифікація — [integration.md](integration.md).
- Формат пакетів — [Пакети обробників](../../reference/packages/README.md).
