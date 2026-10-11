# Швидкий старт Handler Runtime

Виконайте локальний пакет без Registry, Orchestrator і Storage. Потрібні uv, checkout Jane, Python із [.python-version](../../../.python-version), Docker API та Linux containers. На Windows використовуйте Docker Desktop.

## 1. Підготовка

Команди виконуються з кореня репозиторію на Windows або Linux:

```powershell
uv sync --all-packages
uv run --all-packages jane-handler-runtime profile --json
uv run --all-packages jane-handler-runtime build-image --profile python-extractor@1
```

Profile показує дозволені бібліотеки. Build-image створює jane/python-extractor:1 із profile requirements та SDK. Для production зафіксуйте image digest через profile_images.

## 2. Тести пакета

```powershell
uv run --all-packages jane-handler-runtime test examples/documentation/minimal-package
```

[documentation.simple-product@1.0.0](../../../examples/documentation/minimal-package/jane-package.json) має product та empty кейси. Очікуваний критерій — два PASS та 2 passed, 0 failed. Coordinator-run із реальним Docker підтверджений окремо у [звіті](../../delivery/documentation/DOC-05-handler-runtime.md); наведення команди не є новим запуском.

## 3. Один матеріал

```powershell
uv run --all-packages jane-handler-runtime run examples/documentation/minimal-package examples/documentation/minimal-package/tests/product/input.txt --media-type text/plain
```

Очікуються status=success, точний package digest і одна product entity. Звірте output.entities з [expected.json](../../../examples/documentation/minimal-package/tests/product/expected.json). CLI створює Material із файла та test_mode=true; результат не зберігається в бізнес-БД.

| Exit code | Значення |
|---|---|
| 0 | run: success/empty; test: усі PASS |
| 1 | run: unrecognized/failed; test: є FAIL |
| 2 | Виклик не відбувся: package/params/backend помилка |

## HTTP і завершення

```powershell
uv run --all-packages jane-handler-runtime serve
```

Успадковані host/port — 127.0.0.1:8000. Для HTTP потрібен package_archive або registry_url: локальний CLI-каталог не публікує пакет серверу. Ctrl+C завершує сервіс; CLI закриває store, Docker sandbox прибирається після виклику. Постійний package_cache_dir може залишитися.

503 service_unavailable означає недоступний engine; dependency_not_allowed — неправильний profile/library; digest_mismatch — різні байти. Timeout/OOM після запуску повертає HandlerResult.failed. Деталі — [API](reference/api/README.md).
