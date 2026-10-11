# Швидкий старт Registry

Запустіть один Registry із метаданими в пам’яті й файловими архівами. Потрібні uv, checkout Jane і Python із [.python-version](../../../.python-version). Команди виконуються з кореня репозиторію на Windows або Linux.

## 1. Підготовка й offline-перевірка

```powershell
uv sync --all-packages
uv run python -c "from pathlib import Path; Path('.jane').mkdir(exist_ok=True)"
uv run --all-packages jane-registry archive examples/documentation/minimal-package --out .jane/documentation.simple-product-1.0.0.zip
uv run --all-packages jane-registry verify .jane/documentation.simple-product-1.0.0.zip --contracts contracts
```

archive друкує шлях і digest; verify повертає JSON-звіт із ok. Це перевірка формату й секретів, а виконання тестів належить Runtime. При ok=false вивчіть issues до публікації.

## 2. Незалежний API

```powershell
uv run --all-packages python -c "from pathlib import Path; from jane_registry.settings import Settings; from jane_registry.app import build_app; from jane_kit.service import run; s=Settings(db='memory',blob='filesystem',blob_root=Path('.jane/registry-doc'),runtime_profiles=['services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json'],host='127.0.0.1',port=8105,auth_mode='none'); run(build_app(s),s)"
```

Файл профілю дозволяє перевірити Python-залежності без запущеного Runtime. auth_mode=none у цьому прикладі призначений для loopback; мережевому серверу потрібна [автентифікація](configuration.md). Сервер тримає термінал до Ctrl+C.

В іншому терміналі:

```powershell
uv run python -c "import httpx; r=httpx.get('http://127.0.0.1:8105/v1/health'); print(r.status_code); print(r.json())"
uv run python -c "import httpx; r=httpx.get('http://127.0.0.1:8105/v1/packages'); r.raise_for_status(); print(r.json())"
```

Новий Registry повертає порожні items і next_cursor=null. Публікація та перевірка digest — у [інтеграції](integration.md).

## 3. Завершення та проблеми

Ctrl+C закриває процес. Архіви в .jane/registry-doc залишаються; метадані memory втрачаються. Видаляйте каталог лише коли тестові архіви більше не потрібні.

| Ознака | Дія |
|---|---|
| Потрібний DB_URL | Для цього прикладу потрібен db=memory |
| Потрібний BLOB_ROOT | Файловий backend потребує каталогу |
| dependency_not_allowed | Звірити профіль та бібліотеки |
| secret_detected | Прибрати секрет із пакета |
| version_exists | Прочитати наявний digest або підняти версію |

Мінімальний HTTP-запуск на обох ОС потребує окремого доказу приймання; перевірки — у [звіті](../../delivery/documentation/DOC-05-registry.md).
