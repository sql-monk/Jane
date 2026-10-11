# jane-extractor-sdk: залежності

SDK має нуль залежностей поза стандартною бібліотекою Python: його копіюють в образ пісочниці, де під час виконання нічого не встановлюється. Інструменти навколо SDK — опційні.

## Зміст

- [Огляд](#огляд)
- [Python](#python)
- [Профіль виконання](#профіль-виконання)
- [Інструменти перевірки](#інструменти-перевірки)
- [Встановлення поза workspace](#встановлення-поза-workspace)

## Огляд

| Залежність | Обов'язковість | Навіщо | Версія |
|---|---|---|---|
| Python | обов'язкова | інтерпретатор | `>=3.12` ([pyproject.toml](../../../libs/extractor-sdk/pyproject.toml)) |
| Бібліотеки профілю | опційна, для коду пакета | розбір HTML, XML, JSON | точні версії профілю `python-extractor@1` |
| pytest | опційна | тести автора з `jane_extractor_sdk.testing` | з dev-залежностей workspace |
| Handler Runtime (CLI або сервіс) | опційна | перевірка пакета в пісочниці, виконання | з того самого репозиторію |
| Docker | опційна | пісочниця Handler Runtime | див. [залежності Handler Runtime](../handler-runtime/dependencies.md) |

## Python

SDK використовує лише стандартну бібліотеку (`json`, `importlib`, `zipfile`, `hashlib`, `base64`, `codecs`, `mimetypes` та інші). Пакет `jane_extractor_sdk` позначено `py.typed`: перевіряльник типів бачить сигнатури `extract`, `ExtractResult` і помічників.

## Профіль виконання

У пісочниці код пакета виконується в образі профілю `python-extractor@1`: Python 3.12, SDK `0.1.0` і фіксований набір бібліотек — `beautifulsoup4`, `lxml`, `selectolax`, `parsel`, `cssselect`, `html5lib`, `jsonpath-ng`, `jmespath`, `python-dateutil`, `regex`, `w3lib` та їхні залежності. Точні версії друкує `jane-handler-runtime profile`; опис — [python-extractor-1.json](../../../services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json).

Пакет оголошує потрібні бібліотеки в `dependencies.python` маніфесту як вимоги PEP 508, наприклад `"lxml>=6"`. Handler Runtime і Registry перевіряють їх проти точних версій профілю; бібліотека поза профілем — помилка `dependency_not_allowed`. Встановити бібліотеку під час виконання неможливо: у пісочниці немає мережі.

Локальні тести (`run_local`) виконують код у вашому інтерпретаторі, тож там доступні ті бібліотеки, що встановлені локально. Використовуйте лише бібліотеки профілю, інакше пакет пройде pytest, але не пройде перевірку Handler Runtime.

## Інструменти перевірки

- **pytest** — для `assert_package_tests_pass` і `run_local`; SDK від pytest не залежить, `assert_package_tests_pass` кидає звичайний `AssertionError`.
- **Handler Runtime CLI** — `jane-handler-runtime test` і `run` ([швидкий старт](quickstart.md#перевірка-в-пісочниці)). Без Docker доступний лише бекенд `subprocess` — без ізоляції, для довірених пакетів.

Без цих інструментів SDK працює далі: недоступність Handler Runtime означає лише, що пакет не перевірено в пісочниці.

## Встановлення поза workspace

SDK не опубліковано в PyPI. У власному проєкті автора його встановлюють із checkout репозиторію:

```powershell
uv pip install <шлях-до-репозиторію>/libs/extractor-sdk
```

Перевірено 2026-10-11 у чистому віртуальному середовищі Python 3.12: встановлено `jane-extractor-sdk==0.1.0`, `import jane_extractor_sdk` експортує `Context`, `Diagnostic`, `DiagnosticsLog`, `EntityOut`, `ExtractResult`, `Material`, `Unrecognized`, `empty`, `entity`, `success`, `unrecognized`.
