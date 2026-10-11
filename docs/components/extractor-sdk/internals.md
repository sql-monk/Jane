# jane-extractor-sdk: будова

Сторінка описує модулі SDK, протокол раннера між Handler Runtime і кодом пакета, побудову сутностей, порівняння результатів тестів і утиліти пакета. Код — [libs/extractor-sdk/src/jane_extractor_sdk](../../../libs/extractor-sdk/src/jane_extractor_sdk/__init__.py).

## Зміст

- [Модулі](#модулі)
- [Протокол раннера](#протокол-раннера)
- [Побудова сутностей](#побудова-сутностей)
- [Порівняння в тестах](#порівняння-в-тестах)
- [Утиліти пакета](#утиліти-пакета)
- [Гарантії](#гарантії)

## Модулі

| Модуль | Для кого | Призначення |
|---|---|---|
| `jane_extractor_sdk` | автор | реекспорт: `Context`, `ExtractResult`, `Material`, `success`, `empty`, `unrecognized`, `entity` та інші |
| `types` | автор | `ExtractResult`, `EntityOut`, `EntityKey`, `Unrecognized`, `Diagnostic` (TypedDict) |
| `result` | автор | помічники результату й сутності |
| `context` | автор | `Context`, `DiagnosticsLog` |
| `testing` | автор | `run_local`, `run_package_tests`, `assert_package_tests_pass`, `apply_param_defaults` |
| `runner` | Handler Runtime, образ | раннер у пісочниці, `PROTOCOL_VERSION`, `execute` |
| `entities` | Handler Runtime, `testing` | `to_entity_record`, `build_key`, `observation_of` |
| `compare` | Handler Runtime, `testing` | `compare_output` для тестів |
| `package` | Handler Runtime, Registry, автор | канонічний архів, дайджест, безпечне розпакування, матеріал із файлу, вхід тесту |

Handler Runtime імпортує SDK як бібліотеку (архів, порівняння, побудова сутностей), а в пісочниці запускає раннер SDK з образу. Тому runtime і образ мають містити SDK з однаковою версією протоколу.

## Протокол раннера

![Протокол раннера SDK: файли /work, виклик extract, відповідь у stdout](../../diagrams/extractor-sdk/runner-protocol.light.png#gh-light-mode-only)
![Протокол раннера SDK: файли /work, виклик extract, відповідь у stdout](../../diagrams/extractor-sdk/runner-protocol.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/extractor-sdk/runner-protocol.light.png), [темне](../../diagrams/extractor-sdk/runner-protocol.dark.png); джерело — [runner-protocol.drawio](../../diagrams/extractor-sdk/runner-protocol.drawio).

Раннер запускається командою `python -I -m jane_extractor_sdk.runner <каталог>`. Каталог (у контейнері — `/work`, лише для читання) містить:

```text
/work/
├── request.json   # запит протоколу
├── package/       # розпакований пакет; package/src додається в sys.path
└── inputs/0       # вміст blob-входу, якщо він був (inline-вміст лишається в request.json)
```

Перевірочний запуск раннера напряму (Windows, без контейнера) на пакеті з [quickstart.md](quickstart.md). `request.json`, версія протоколу 1:

```json
{
  "protocol": 1,
  "entry": {"runtime": "python", "module": "hello_title.main", "callable": "extract"},
  "package_dir": "package",
  "params": {},
  "test_mode": false,
  "inputs": [
    {
      "input": {
        "kind": "material",
        "material": {
          "material_id": "web:37f58c3315be7800d9d1452bf60ed101",
          "locator": {"url": "https://example.test/a"},
          "content": {"kind": "inline", "media_type": "text/html", "encoding": "utf-8", "data": "<html><head><title>Hello, Jane</title></head></html>"}
        }
      },
      "content_file": null
    }
  ]
}
```

```powershell
uv run --package jane-extractor-sdk python -I -m jane_extractor_sdk.runner <каталог>
```

Раннер пише в оригінальний stdout рівно один JSON-документ і завершується з кодом 0:

```json
{"protocol": 1, "results": [{"status": "success", "entities": [{"entity_type": "page", "fields": {"url": "https://example.test/a", "title": "Hello, Jane"}}]}], "violations": [], "metrics": {"duration_ms": 14}}
```

На Windows у `metrics` лише `duration_ms`; у Linux-контейнері раннер додає `cpu_ms` і `peak_memory_mb`.

Порядок роботи:

1. Перенаправляє дескриптор stdout у stderr, щоб `print` коду пакета не зіпсував протокол; оригінальний stdout залишає для відповіді.
2. Читає `request.json`; інша версія протоколу — код виходу 3 без відповіді.
3. Ставить аудит-хук (`sys.addaudithook`), що записує події мережі (`socket.connect`, `socket.getaddrinfo`, `socket.gethostbyname`, `socket.sendto`, `socket.bind`) і процесів (`subprocess.Popen`, `os.system`, `os.posix_spawn`, `os.exec`, `os.fork`, `os.spawn`) — до 50 записів з номером входу.
4. Імпортує `entry.module` і бере `entry.callable`. Помилка імпорту — `error` зі `stage: import` для кожного входу.
5. Для кожного входу створює `Context` (вміст — з `content_file` або inline) і викликає `extract(material, params, ctx)`. Виняток — `error` зі `stage: extract`, `type`, `message`, `traceback`; раннер продовжує з наступним входом.
6. Нормалізує результат: має бути словником зі статусом `success`, `empty` або `unrecognized` і серіалізуватися в JSON без `NaN` та `Infinity`; повідомлення `ctx.log` додаються перед `diagnostics` результату.
7. Додає `metrics`: `cpu_ms` і `peak_memory_mb` (з `resource` і cgroup контейнера; на Windows — немає), `duration_ms`.

Аудит-хук — не межа безпеки: обійти його можна, тому мережу й файлову систему обмежує контейнер. Хук лише пояснює, чому код упав, і дає Handler Runtime підставу для `sandbox_violation`.

## Побудова сутностей

`to_entity_record` у `entities.py` перетворює `EntityOut` на `EntityRecord` контракту ([entity.schema.json](../../../contracts/schemas/entity.schema.json)). Його використовують Handler Runtime і `run_local`:

| Поле | Як заповнюється |
|---|---|
| `key` | якщо немає: `{"scope": source.source_id або "local", "natural": {поле: значення}}` з `key_fields`; не утворюється, якщо поле ключа відсутнє або не скаляр |
| `observation` | з матеріалу: `observation_id`, `observed_at` = `fetched_at`, `sequence` і `content_sha256` з `revision`, `material_id` |
| `schema` | `<package_id>@<version>#<entity_type>` (лише Handler Runtime) |
| `provenance` | пакет, `invocation_id`, `run_id`, `stage_id` (лише Handler Runtime) |

Сутність без ключа Handler Runtime відхиляє як `schema_mismatch`, `run_local` — повертає як є.

## Порівняння в тестах

`compare_output(expected, actual, mode)` порівнює очікуваний `output` тесту з фактичним і повертає список `{"pointer", "expected", "actual"}`:

- поля `observation`, `provenance`, `schema` сутностей ігноруються з обох боків;
- `exact` — однакові ключі й значення, однакова довжина й порядок масивів;
- `subset` — очікувані ключі мають бути у фактичному, зайві дозволено; кожен очікуваний елемент масиву має відповідати окремому фактичному елементу в будь-якому порядку;
- числа `1` і `1.0` рівні, `true` і `1` — ні.

Handler Runtime і `run_package_tests` порівнюють однаково, але Handler Runtime додатково перевіряє схеми сутностей.

## Утиліти пакета

- **`build_archive(package_dir)`** — канонічний zip ([integration.md](integration.md#архів-і-дайджест)); без `jane-package.json` — `PackageError`.
- **`digest_of(data)`** — `sha256:<hex>`.
- **`safe_unpack(archive, dest, limits)`** — розпакування недовіреного архіву: шляхи лише відносні з `/`, без `..`, без символьних посилань, ліміти розміру архіву, розпакованого вмісту й кількості файлів (`UnpackLimits` задає викликач — Handler Runtime чи Registry).
- **`material_from_bytes`, `material_from_file`** — `Material` з inline-вмістом: `material_id` — `web:` + перші 32 символи SHA-256 URL (як у Web Collector) або `file:` + SHA-256 вмісту; `observation_id` — `obs_local_` + SHA-256 вмісту; текстові типи — `utf-8`, решта — `base64`.
- **`case_input(package_dir, case)`** — `HandlerInput` для тесту маніфесту з `file`, `material` (з необов'язковим `content_file`), `entities` або `data`.

## Гарантії

- **Лише стандартна бібліотека.** SDK працює в будь-якому Python 3.12 і в образі без мережі.
- **Чистий канал протоколу.** Вивід коду пакета не потрапляє у відповідь раннера.
- **Ізоляція входів за помилками.** Виняток на одному вході не зупиняє обробку інших; Handler Runtime повідомляє першу помилку.
- **Детермінований архів.** Той самий каталог дає ті самі байти й дайджест на Windows і Linux.
