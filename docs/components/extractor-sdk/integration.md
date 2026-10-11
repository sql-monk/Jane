# jane-extractor-sdk: інтеграція

Сторінка описує контракт між кодом екстрактора й Handler Runtime з боку автора: що отримує `extract`, що повертати, як працювати з контекстом, як запускати пакет локально та як пакет потрапляє в Jane. Сигнатури всіх публічних членів — [довідник типів](reference/types/README.md).

## Зміст

- [Функція extract](#функція-extract)
- [Результат](#результат)
- [Сутності](#сутності)
- [Контекст](#контекст)
- [Локальний запуск через CLI](#локальний-запуск-через-cli)
- [Архів і дайджест](#архів-і-дайджест)
- [Композиція в Jane](#композиція-в-jane)
- [Без SDK і сумісна заміна](#без-sdk-і-сумісна-заміна)

## Функція extract

Точку входу задає `entry` маніфесту: модуль і ім'я функції, типово `extract`.

```python
def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult: ...
```

| Аргумент | Що містить |
|---|---|
| `material` | для входу `material` — документ `Material` ([material.schema.json](../../../contracts/schemas/material.schema.json)): `material_id`, `observation_id`, `source`, `locator.url`, `fetched_at`, `format`, `content`; для входів `entities` і `data` (пакети `transform`) — сам об'єкт входу |
| `params` | параметри етапу з підставленими типовими значеннями й перевірені за `params_schema` |
| `ctx` | [контекст](#контекст): вміст, діагностика, тестовий режим |

`extract` викликається окремо для кожного входу запиту, кожного разу з новим `ctx`. Між викликами в одному процесі зберігаються лише глобальні змінні модуля; між запитами — нічого, бо кожен запит виконується в новому контейнері.

## Результат

| Ситуація | Що повернути | `HandlerResult.status` |
|---|---|---|
| сутності знайдено | `success([entity(...), ...])` | `success` |
| матеріал зрозумілий, потрібних сутностей у ньому немає | `empty()` | `empty` |
| формат невідомий або розібраний частково | `unrecognized(reason, signature=..., entities=[...])` | `unrecognized` |
| помилка коду або даних, які не мали б траплятися | `raise` будь-який виняток | `failed`, `failure.kind: execution_error` |

![Робота автора пакета й відповідність результату extract статусу HandlerResult](../../diagrams/extractor-sdk/author-workflow.light.png#gh-light-mode-only)
![Робота автора пакета й відповідність результату extract статусу HandlerResult](../../diagrams/extractor-sdk/author-workflow.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/extractor-sdk/author-workflow.light.png), [темне](../../diagrams/extractor-sdk/author-workflow.dark.png); джерело — [author-workflow.drawio](../../diagrams/extractor-sdk/author-workflow.drawio).

- `success(entities=None, *, data=None, diagnostics=None)` — `data` для пакетів `transform`; перевіряється за `output.data_schema`.
- `empty(*, diagnostics=None)` — розрізняє «тут немає товару» і «не вдалося розібрати».
- `unrecognized(reason, *, signature=None, entities=None, diagnostics=None)` — `signature` групує проблемні матеріали (наприклад `"missing-selector:.price"`): за нею Jane збирає вибірки для вдосконалення екстрактора. Передані `entities` роблять результат частковим (`partial: true`).
- Статус `failed` повернути не можна: раннер відхиляє його як недійсний, і результат усе одно стає `failed`.

Також `failed` встановлює Handler Runtime, якщо вихід не відповідає схемам (`schema_mismatch`), код звертався до мережі чи процесів (`sandbox_violation`), перевищено час або пам'ять (`timeout`, `resource_exceeded`). Порядок перевірок — [класифікація результату](../handler-runtime/internals.md#класифікація-результату).

## Сутності

```python
entity("product", {"sku": "a-100", "title": "Kettle", "price": None}, completeness="partial")
```

| Параметр | Значення |
|---|---|
| `entity_type` | тип з `output.entities` маніфесту; неоголошений тип — `schema_mismatch` |
| `fields` | поля за схемою типу; ключі зі значенням `None` **відкидаються** |
| `key` | `{"scope": ..., "natural": {...}}`; без нього Handler Runtime будує ключ з `key_fields` і `source.source_id` матеріалу |
| `cleared` | назви полів, які треба явно очистити у сховищі |
| `completeness` | `full` або `partial` — чи всі поля сутності знайдено |
| `confidence` | число, впевненість екстрактора |

Пропущене поле не означає «видалити» (ТЗ §6): частковий результат оновлює лише передані поля. Щоб очистити поле, назвіть його в `cleared`. Якщо повертати сутність словником без `entity()`, значення `null` у `fields` дає `schema_mismatch`.

Handler Runtime додає до кожної сутності `observation` (порядок спостережень), `schema` (`<package_id>@<version>#<entity_type>`) і `provenance` (пакет, дайджест, `invocation_id`). Їх не потрібно і не варто заповнювати в коді.

## Контекст

| Член | Що дає |
|---|---|
| `ctx.text(errors="replace")` | вміст як текст: inline `utf-8` — як є, інакше байти декодуються за `charset()` |
| `ctx.bytes()` | сирі байти вмісту; blob уже завантажено й перевірено Handler Runtime |
| `ctx.charset()` | кодування з `content.charset`, потім `format.charset`, інакше `utf-8`; невідомі назви пропускаються |
| `ctx.log` | `DiagnosticsLog`: `debug`, `info`, `warning`, `error`, `add(level, message, *, code, selector, pointer)` |
| `ctx.test_mode` | чи це тестовий прогін |
| `ctx.params`, `ctx.material` | ті самі `params` і `material`, що й аргументи |

Повідомлення `ctx.log` потрапляють у `HandlerResult.diagnostics.messages` разом із `material_id`; `code` і `selector` допомагають групувати проблеми. Вміст `print` і журналів Python іде в stderr і лише хвостом — у `diagnostics.logs_ref`, тому для діагностики використовуйте `ctx.log`.

Код пакета нічого не завантажує сам: у пісочниці немає мережі, а вміст матеріалу вже передано.

## Локальний запуск через CLI

CLI Handler Runtime виконує пакет із каталогу або zip без сервісів Jane:

| Команда | Що робить |
|---|---|
| `jane-handler-runtime test <пакет>` | тести маніфесту; `--case <назва>` — вибрані, `--json` — звіт `TestReport` |
| `jane-handler-runtime run <пакет> <файл> --media-type text/html --url <URL>` | один виклик на файлі; `--params '{"k": "v"}'` або `--params @params.json` |
| `jane-handler-runtime run <пакет> material.json --material` | вхід — готовий документ `Material` |
| `jane-handler-runtime run ... --source-id shop` | область ключа сутностей замість `local` |

Типовий бекенд — `docker`; `--backend subprocess --unsafe-no-sandbox` запускає код без ізоляції, лише для довірених пакетів. Коди виходу й інші параметри — [конфігурація Handler Runtime](../handler-runtime/configuration.md#параметри-cli); перевірений приклад — [quickstart.md](quickstart.md#перевірка-в-пісочниці).

Тест маніфесту може брати вхід із сирого файлу (`input.file`, `media_type`, `url`), з документа `Material` (`input.material`; поле `content_file` у ньому підставляє вміст із файлу пакета), або з JSON сутностей чи даних (`input.entities`, `input.data`). Формат тестів — [довідник пакетів](../../reference/packages/README.md).

## Архів і дайджест

Канонічний zip і дайджест обчислюються однаково в SDK, Handler Runtime і Registry, тож дайджест локального каталогу збігається з дайджестом опублікованої версії:

```python
from pathlib import Path

from jane_extractor_sdk.package import build_archive, digest_of

archive = build_archive(Path("hello-title"))
print(len(archive), digest_of(archive))
```

Архів: один запис на файл, імена за зростанням, без стиснення, дата 1980-01-01, права `0644`, без кешів (`__pycache__`, `.pytest_cache` та інші) і `.pyc`; символьні посилання заборонено. Архів передають у `package_archive` запиту `handler.v1` ([приклад](../handler-runtime/quickstart.md#http-сервіс)) або публікують у Registry.

## Композиція в Jane

- **Registry** зберігає версії пакета й звіти їхніх тестів, перевіряє `dependencies.python` за профілем, який публікує Handler Runtime — [Registry](../registry/README.md). Самі тести Registry не запускає: звіт приносить той, хто проганяв `POST /v1/test-runs`.
- **Orchestrator** у кожному етапі завдання посилається на конкретну версію пакета; виконує її Handler Runtime.
- **Assistant** генерує й вдосконалює екстрактори за допомогою LLM у тому самому форматі: код лише зі стандартною бібліотекою й SDK, перевірка — `POST /v1/test-runs`.
- **Storage** зберігає сутності, які повернув екстрактор, як окремий етап; SDK і Handler Runtime у сховища не пишуть.

## Без SDK і сумісна заміна

Помічники SDK необов'язкові: `extract` може повертати звичайний словник `{"status": "success", "entities": [...]}` — раннер перевіряє лише статус і серіалізацію в JSON. Обов'язковий тільки раннер SDK в образі профілю: саме він імпортує код пакета й говорить із Handler Runtime протоколом версії 1.

Інший виконавець пакетів може використати той самий раннер (`python -I -m jane_extractor_sdk.runner <каталог>`) або реалізувати [протокол раннера](internals.md#протокол-раннера) самостійно; пакети при цьому не змінюються.
