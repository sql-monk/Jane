# jane-extractor-sdk

jane-extractor-sdk — бібліотека для авторів екстракторів Jane на Python. Автор пише функцію `extract(material, params, ctx)`, повертає результат помічниками SDK і перевіряє пакет локально; Handler Runtime виконує той самий код у пісочниці. Тип модуля — бібліотека; залежить лише від стандартної бібліотеки Python.

Екстрактор — це пакет обробника: маніфест `jane-package.json`, код, схеми сутностей і тести. SDK дає коду пакета типи, контекст і раннер; формат самого пакета описує [довідник пакетів](../../reference/packages/README.md). Виконує пакет сервіс [Handler Runtime](../handler-runtime/README.md), в образ пісочниці якого SDK встановлено.

## Зміст

- [Призначення й межі](#призначення-й-межі)
- [Можливості](#можливості)
- [Мінімальний екстрактор](#мінімальний-екстрактор)
- [Сценарії](#сценарії)
- [Автономність](#автономність)
- [Обмеження](#обмеження)
- [Комплект документації](#комплект-документації)

## Призначення й межі

| Відповідає за | Не відповідає за |
|---|---|
| сигнатуру `extract` і типи вхідних даних та результату | ізоляцію, ліміти й перевірку схем — це Handler Runtime |
| помічники результату: `success`, `empty`, `unrecognized`, `entity` | формат маніфесту й життєвий цикл пакета — це [довідник пакетів](../../reference/packages/README.md) і Registry |
| контекст: вміст матеріалу, діагностика, тестовий режим | завантаження матеріалів — вміст передає Handler Runtime |
| раннер у пісочниці та його протокол з Handler Runtime | збереження сутностей — це Storage |
| канонічний архів і дайджест, матеріал із файлу, локальні тести в процесі | публікацію пакета — це Registry |

## Можливості

- **Результат** — `success(entities, data=...)`, `empty()`, `unrecognized(reason, signature=..., entities=...)`; виняток у `extract` дає `failed`.
- **Сутність** — `entity(entity_type, fields, key=..., cleared=..., completeness=..., confidence=...)`; поля зі значенням `None` відкидаються.
- **Контекст** — `ctx.text()`, `ctx.bytes()`, `ctx.charset()`, `ctx.log.info(...)`, `ctx.test_mode`, `ctx.params`.
- **Локальні тести** — `run_local` і `assert_package_tests_pass` виконують пакет у поточному процесі pytest без контейнера.
- **Пакет** — `build_archive` і `digest_of` дають ті самі байти й дайджест, що й Registry; `material_from_file` робить матеріал із локального файлу.
- **Раннер** — `python -I -m jane_extractor_sdk.runner <workdir>`: протокол версії 1 між Handler Runtime і кодом пакета.

## Мінімальний екстрактор

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

Повний пакет із маніфестом, схемою й тестами та його перевірка — [quickstart.md](quickstart.md). Більший приклад — [testsite-product-extractor](../../../libs/extractor-sdk/examples/testsite-product-extractor/src/testsite_products/main.py): JSON-LD і мікродані, усі чотири стани.

## Сценарії

| Сценарій | Інструмент | Де описано |
|---|---|---|
| Написати й швидко перевірити екстрактор | `run_local`, `assert_package_tests_pass` у pytest | [quickstart.md](quickstart.md) |
| Перевірити пакет так, як у роботі | `jane-handler-runtime test` | [quickstart.md](quickstart.md#перевірка-в-пісочниці) |
| Виконати пакет на файлі | `jane-handler-runtime run` | [integration.md](integration.md#локальний-запуск-через-cli) |
| Зібрати архів і дайджест для публікації або виклику | `build_archive`, `digest_of` | [integration.md](integration.md#архів-і-дайджест) |
| Згенерувати екстрактор LLM | Assistant використовує той самий формат і профіль | [integration.md](integration.md#композиція-в-jane) |

## Автономність

SDK не залежить від інших модулів Jane і сторонніх бібліотек. Код пакета можна писати й тестувати з одним лише SDK; для перевірки в пісочниці потрібен Handler Runtime у режимі CLI — без Registry, Orchestrator і баз даних. Подробиці — [dependencies.md](dependencies.md).

## Обмеження

- **Python 3.12.** SDK вимагає `>=3.12`; профіль `python-extractor@1` — Python 3.12.
- **Лише бібліотеки профілю.** Пакет може використовувати стандартну бібліотеку й бібліотеки профілю `python-extractor@1`; встановити інші під час виконання не можна.
- **Без мережі й процесів.** У пісочниці немає мережі; спроба з'єднання чи запуску процесу дає `failed: sandbox_violation`, навіть якщо код перехопив виняток.
- **Локальні тести не ізольовані.** `run_local` не перевіряє схеми сутностей і не застосовує ліміти — остаточна перевірка лише через Handler Runtime.
- **Не опубліковано в PyPI.** Встановлюється з репозиторію, версія `0.1.0`.

## Комплект документації

| Документ | Зміст |
|---|---|
| [quickstart.md](quickstart.md) | мінімальний пакет, тести pytest, перевірка в пісочниці |
| [dependencies.md](dependencies.md) | Python, профіль виконання, Handler Runtime |
| [configuration.md](configuration.md) | що впливає на виконання коду: параметри, тестовий режим, ліміти |
| [integration.md](integration.md) | API для автора, локальний запуск, архів, місце в Jane |
| [internals.md](internals.md) | протокол раннера, побудова сутностей, порівняння тестів |
| [operations.md](operations.md) | версії SDK і профілю, типові помилки авторів |

Довідники:

- типи й функції SDK — [reference/types](reference/types/README.md) (HTTP API немає — [reference/api](reference/api/README.md));
- формат пакетів обробників — [довідник пакетів](../../reference/packages/README.md);
- API, яким Handler Runtime виконує пакети, — [довідник handler.v1](../../reference/api/handler/README.md).
