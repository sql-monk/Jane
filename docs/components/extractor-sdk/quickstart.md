# jane-extractor-sdk: швидкий старт

Інструкція створює мінімальний пакет екстрактора, який витягує заголовок HTML-сторінки, перевіряє його тестами pytest у поточному процесі, а потім — у Handler Runtime так, як він виконуватиметься в роботі.

Кроки виконано 2026-10-11 на Windows 11, PowerShell 7, Docker Desktop 29.8, ревізія `c59d26d`. На Linux не перевірялися; команди `uv` ті самі, Bash-варіанти відрізняються лише записом шляхів.

## Зміст

- [Передумови](#передумови)
- [Структура пакета](#структура-пакета)
- [Файли пакета](#файли-пакета)
- [Тести в процесі](#тести-в-процесі)
- [Перевірка в пісочниці](#перевірка-в-пісочниці)
- [Виконання на файлі](#виконання-на-файлі)
- [Прибирання](#прибирання)

## Передумови

- Checkout репозиторію й uv; з кореня репозиторію виконано `uv sync --all-packages` ([середовище розробки](../../development/environment.md)). Команди нижче запускаються з кореня репозиторію.
- Для перевірки в контейнері — Docker і образ профілю `python-extractor@1` ([швидкий старт Handler Runtime](../handler-runtime/quickstart.md#образ-пісочниці)).
- Каталог пакета — будь-який, поза репозиторієм. У прикладі:

  PowerShell:

  ```powershell
  $Q = "$env:TEMP\jane-sdk-quickstart"
  New-Item -ItemType Directory -Force "$Q\hello-title\src\hello_title", "$Q\hello-title\schemas", "$Q\hello-title\tests"
  ```

  Bash (не перевірено на Linux):

  ```bash
  Q=/tmp/jane-sdk-quickstart
  mkdir -p "$Q/hello-title/src/hello_title" "$Q/hello-title/schemas" "$Q/hello-title/tests"
  ```

## Структура пакета

```text
jane-sdk-quickstart/
├── test_hello_title.py              # тести pytest автора (поза пакетом)
└── hello-title/                     # пакет обробника
    ├── jane-package.json            # маніфест
    ├── schemas/page.schema.json     # схема сутності page
    ├── src/hello_title/__init__.py  # порожній
    ├── src/hello_title/main.py      # extract(material, params, ctx)
    └── tests/
        ├── with-title.html          # тест: очікується success
        ├── with-title.expected.json # очікуваний вихід
        └── no-title.html            # тест: очікується empty
```

Каталог `src/` пакета раннер додає в `sys.path`, тому модуль `hello_title.main` імпортується без встановлення. Нормативний опис структури й полів маніфесту — [довідник пакетів](../../reference/packages/README.md).

## Файли пакета

1. `hello-title/jane-package.json` — маніфест. Він оголошує точку входу, сутність `page` з ключем `url`, профіль виконання, відсутність мережі й два тести:

   ```json
   {
     "schema_version": "1",
     "package_id": "example.hello-title",
     "version": "0.1.0",
     "kind": "extractor",
     "title": "Page title",
     "entry": {"runtime": "python", "module": "hello_title.main", "callable": "extract"},
     "input": {"accepts": ["material"], "media_types": ["text/html"]},
     "output": {
       "entities": [
         {"entity_type": "page", "schema": "schemas/page.schema.json", "key_fields": ["url"]}
       ]
     },
     "dependencies": {"runtime_profile": "python-extractor@1", "python": []},
     "access": {"network": "none"},
     "tests": [
       {
         "name": "with-title",
         "input": {"file": "tests/with-title.html", "media_type": "text/html", "url": "https://example.test/a"},
         "expected_status": "success",
         "expected": "tests/with-title.expected.json"
       },
       {
         "name": "no-title",
         "input": {"file": "tests/no-title.html", "media_type": "text/html", "url": "https://example.test/b"},
         "expected_status": "empty"
       }
     ],
     "provenance": {"created_by": "human", "created_at": "2026-10-11T00:00:00Z"}
   }
   ```

2. `hello-title/schemas/page.schema.json` — схема полів сутності. Handler Runtime перевіряє за нею кожну сутність:

   ```json
   {
     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "type": "object",
     "additionalProperties": false,
     "required": ["url", "title"],
     "properties": {
       "url": {"type": "string"},
       "title": {"type": "string", "minLength": 1}
     }
   }
   ```

3. `hello-title/src/hello_title/__init__.py` — порожній файл.

4. `hello-title/src/hello_title/main.py` — код екстрактора. Сторінка без заголовка — коректна відсутність даних (`empty`), а не помилка:

   ```python
   import re

   from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

   TITLE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


   def extract(material: Material, params: dict, ctx: Context) -> ExtractResult:
       match = TITLE.search(ctx.text())
       if not match or not match.group(1).strip():
           ctx.log.info("no <title> on the page", code="hello.no_title")
           return empty()
       url = (material.get("locator") or {}).get("url", "")
       return success([entity("page", {"url": url, "title": match.group(1).strip()})])
   ```

5. Тестові сторінки. `hello-title/tests/with-title.html`:

   ```html
   <html><head><title>Hello, Jane</title></head><body></body></html>
   ```

   `hello-title/tests/no-title.html`:

   ```html
   <html><head></head><body>No title</body></html>
   ```

6. `hello-title/tests/with-title.expected.json` — очікуваний вихід тесту `with-title`. Порівнюється весь `output` (режим `exact`), крім полів `observation`, `provenance` і `schema`, які додає Handler Runtime. Ключ будується з `key_fields`; область `local`, бо тестовий матеріал не має `source.source_id`:

   ```json
   {
     "entities": [
       {
         "entity_type": "page",
         "key": {"scope": "local", "natural": {"url": "https://example.test/a"}},
         "fields": {"url": "https://example.test/a", "title": "Hello, Jane"}
       }
     ]
   }
   ```

## Тести в процесі

7. Створіть `test_hello_title.py` поруч із каталогом пакета. `assert_package_tests_pass` проганяє тести маніфесту, `run_local` — один файл:

   ```python
   from pathlib import Path

   from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

   PKG = Path(__file__).parent / "hello-title"


   def test_manifest_tests():
       assert_package_tests_pass(PKG)


   def test_title_is_extracted():
       result = run_local(PKG, file=PKG / "tests/with-title.html", media_type="text/html", url="https://example.test/a")
       assert result["status"] == "success"
       assert result["output"]["entities"][0]["fields"]["title"] == "Hello, Jane"
   ```

8. Запустіть pytest із середовища SDK:

   ```powershell
   uv run --package jane-extractor-sdk pytest "$Q\test_hello_title.py" -q -p no:cacheprovider
   ```

   ```text
   ..                                                                       [100%]
   2 passed in 0.25s
   ```

   Це швидкий цикл для власного довіреного коду: пакет виконується в поточному процесі без контейнера, схеми сутностей і ліміти не перевіряються.

## Перевірка в пісочниці

9. Проженіть тести маніфесту через Handler Runtime на бекенді `subprocess`. Він виконує код без контейнера й **без ізоляції** — мережа, файли й пам'ять не обмежуються, — тому підходить лише для власних довірених пакетів на машині розробника. Зате, на відміну від pytest, тут працюють перевірка маніфесту, параметрів, схем сутностей і тайм-аут:

   ```powershell
   uv run --package jane-handler-runtime jane-handler-runtime test "$Q\hello-title" --backend subprocess --unsafe-no-sandbox
   ```

   ```text
   package example.hello-title@0.1.0 (sha256:37716453a0e53f686ac9ea34ba7313872e377e155a7b1db9af9fd3aed8f7bf78), backend=subprocess
     PASS with-title: expected success, got success
     PASS no-title: expected empty, got empty
   2 passed, 0 failed
   ```

   Без `--unsafe-no-sandbox` команда відмовляється запускати код і завершується з кодом 2:

   ```text
   {
     "type": "urn:jane:problem:service_unavailable",
     "title": "Service unavailable",
     "status": 503,
     "detail": "subprocess backend is disabled (set JANE_HANDLER_RUNTIME_ALLOW_UNSAFE_SUBPROCESS=true for trusted local packages only)",
     "code": "service_unavailable",
     "retryable": true,
     "retry_after_seconds": 5
   }
   ```

10. Перевірте пакет у контейнері — так, як його виконуватиме Handler Runtime у платформі: образ профілю, бібліотеки профілю, без мережі, з лімітами:

    ```powershell
    uv run --package jane-handler-runtime jane-handler-runtime test "$Q\hello-title"
    ```

    Вивід перевірочного запуску (образ зібрано з тегом `jane-doc-hr/python-extractor:1`, тому додано `--image jane-doc-hr/python-extractor:1`):

    ```text
    package example.hello-title@0.1.0 (sha256:37716453a0e53f686ac9ea34ba7313872e377e155a7b1db9af9fd3aed8f7bf78), backend=docker
      PASS with-title: expected success, got success
      PASS no-title: expected empty, got empty
    2 passed, 0 failed
    ```

    Дайджест однаковий для обох бекендів: це SHA-256 канонічного архіву каталогу, тож саме цей дайджест отримає версія після публікації в Registry.

## Виконання на файлі

11. Виконайте пакет на сторінці без заголовка й подивіться на діагностику з `ctx.log`:

    ```powershell
    uv run --package jane-handler-runtime jane-handler-runtime run "$Q\hello-title" "$Q\hello-title\tests\no-title.html" --url https://example.test/b
    ```

    Уривок виводу (код виходу 0, бо `empty` — успішний стан):

    ```json
    {
      "handler_kind": "extractor",
      "status": "empty",
      "output": {"entities": []},
      "test_mode": true,
      "diagnostics": {
        "messages": [
          {"level": "info", "code": "hello.no_title", "message": "no <title> on the page", "material_id": "web:1e10b7a6eca74ac7ff7da6e42786c37c"}
        ],
        "metrics": {"duration_ms": 3467, "output_bytes": 307, "cpu_ms": 275, "peak_memory_mb": 11.9}
      }
    }
    ```

Bash-варіанти кроків 8–11 (не перевірено на Linux) відрізняються лише шляхами:

```bash
uv run --package jane-extractor-sdk pytest "$Q/test_hello_title.py" -q -p no:cacheprovider
uv run --package jane-handler-runtime jane-handler-runtime test "$Q/hello-title" --backend subprocess --unsafe-no-sandbox
uv run --package jane-handler-runtime jane-handler-runtime test "$Q/hello-title"
uv run --package jane-handler-runtime jane-handler-runtime run "$Q/hello-title" "$Q/hello-title/tests/no-title.html" --url https://example.test/b
```

## Прибирання

Наступна команда видаляє каталог прикладу разом із пакетом і тестами.

PowerShell:

```powershell
Remove-Item -Recurse -Force "$env:TEMP\jane-sdk-quickstart"
```

Bash:

```bash
rm -rf /tmp/jane-sdk-quickstart
```

Контейнери пісочниці Handler Runtime видаляє сам; образ профілю лишається для наступних перевірок.

Далі: як влаштовано результат і контекст — [integration.md](integration.md); що буде з винятками, `None`-полями й `print` — [operations.md](operations.md#типові-помилки-автора).
