# Експорт і сумісність пакетів

Архів версії достатній, щоб виконати пакет без Registry: його можна завантажити, перевірити офлайн і передати виконавцю. Розділ про сумісність пояснює, що в пакетах може змінюватися без поломки наявних етапів і що вимагає нової версії.

## Зміст

- [Експорт версії](#експорт-версії)
- [Офлайн-перевірка архіву](#офлайн-перевірка-архіву)
- [Автономне використання](#автономне-використання)
- [Сумісність](#сумісність)

## Експорт версії

CLI `jane-registry export` завантажує архів версії й, рекурсивно, архіви всіх `dependencies.packages`, перевіряє, що байти, `ETag` і `digest` версії збігаються, і записує:

```text
<out>/<package_id>-<version>.zip     точний канонічний архів із Registry
<out>/jane-export.json               індекс: пакет, версія, digest, файл, розмір, статус, kind
```

| Аргумент | Типово | Зміст |
|---|---|---|
| `<package_id>@<version>` | — | Версія для експорту |
| `--registry URL` | обов'язковий | Базова адреса Registry |
| `--out DIR` | обов'язковий | Каталог результату; створюється, якщо немає |
| `--no-dependencies` | вимкнено | Не завантажувати залежності |
| `--token-env VAR` | — | Змінна середовища з bearer-токеном |
| `--timeout-ms N` | `30000` | Тайм-аут HTTP |
| `--max-packages N` | `100` | Найбільший розмір ланцюжка залежностей |

Код виходу: `0` — успіх, `2` — експорт не вдався (помилка HTTP, розбіжність дайджесту, завеликий ланцюжок). Приклад (Registry із [quickstart](../../components/registry/quickstart.md) на порту 18400):

```powershell
uv run --package jane-registry jane-registry export examples.testsite-price-extractor@1.0.0 --registry http://127.0.0.1:18400 --out .jane/registry-quickstart/export
```

```text
examples.testsite-price-extractor@1.0.0  sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9  .jane\registry-quickstart\export\examples.testsite-price-extractor-1.0.0.zip
```

Файл `jane-export.json` після цієї команди:

```json
{
  "format": "jane-export@1",
  "exported_at": "2026-10-11T09:59:45Z",
  "registry": "http://127.0.0.1:18400",
  "root": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0"},
  "packages": [
    {
      "package_id": "examples.testsite-price-extractor",
      "version": "1.0.0",
      "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9",
      "file": "examples.testsite-price-extractor-1.0.0.zip",
      "size_bytes": 13587,
      "status": "approved",
      "kind": "extractor"
    }
  ]
}
```

Без CLI архів отримують запитом `GET /v1/packages/{id}/versions/{v}/archive`; дайджест — у заголовках `ETag` і `X-Jane-Package-Digest`. Окремий файл версії читає `GET …/versions/{v}/file?path=<шлях>` (текст — `text/plain`, інше — `application/octet-stream`).

## Офлайн-перевірка архіву

`jane-registry verify <archive.zip> [--digest sha256:…] [--contracts <каталог contracts>]` не звертається до Registry. Очікуваний дайджест береться з `--digest` або з `jane-export.json` поруч з архівом.

| Перевірка в `checks` | Що означає |
|---|---|
| `digest` | Дайджест архіву збігається з очікуваним (якщо його відомо) |
| `canonical` | Архів точно в канонічній формі |
| `manifest` | Маніфест і файли проходять перевірки Registry (потрібен каталог `contracts/`) |
| `referenced_files` | Замість `manifest`, якщо `contracts/` не знайдено: усі файли з маніфесту є |
| `scan_limit` | Жоден файл не перевищує ліміт сканування секретів |
| `secrets` | Секретів не знайдено |

Код виходу: `0` — `ok: true`, `1` — перевірку не пройдено. Ліміти перевірки — ті самі змінні `JANE_REGISTRY_LIMITS__PACKAGES__*` і `JANE_REGISTRY_LIMITS__SECRETS__*`, що й у сервісу.

```powershell
uv run --package jane-registry jane-registry verify .jane/registry-quickstart/export/examples.testsite-price-extractor-1.0.0.zip
```

```json
{
  "path": ".jane\\registry-quickstart\\export\\examples.testsite-price-extractor-1.0.0.zip",
  "ok": true,
  "digest": "sha256:d143e1e9b7a4f3f2ea28886cc6fd37c29cb9915fce772d1a84b1ea6ea6bfa2f9",
  "package": {"package_id": "examples.testsite-price-extractor", "version": "1.0.0", "kind": "extractor"},
  "checks": {"digest": true, "canonical": true, "manifest": true, "scan_limit": true, "secrets": true},
  "errors": []
}
```

## Автономне використання

| Виконавець | Як використати архів без Registry |
|---|---|
| Handler Runtime | CLI `jane-handler-runtime run <zip> <файл>` або `test <zip>`; через API — архів у `HandlerInvocation.package_archive` |
| LLM gateway | Архів LLM-пакета в `HandlerInvocation.package_archive` |
| Storage | Стандартні пакети `jane.storage-*` вбудовані; інші — архівом у виклику |
| Web Collector, Telegram Collector | Файл правил inline у запиті або з локального файла |

Карта залежностей модулів від Registry — [data-ownership.md](../../../contracts/docs/data-ownership.md); формат виклику — [довідник handler.v1](../api/handler/README.md).

## Сумісність

**Посилання на версію.** Етап завдання фіксує `package_id@version` (+ `digest`). Нова версія пакета, зокрема перенесення змін у форк, ніколи не підміняє ту, що вже активна: потрібна явна активація в Orchestrator.

**Формат маніфесту.** `schema_version` — константа `"1"`, а верхній рівень маніфесту не допускає невідомих полів. Нове поле маніфесту — зміна контракту [package-manifest.schema.json](../../../contracts/schemas/package-manifest.schema.json), яку перевіряє інструмент сумісності контрактів (`just contracts-compat`).

**Вихід пакета.** Споживачі результатів залежать від `entity_type`, `key_fields` і схем сутностей. Зміна ключа або видалення поля — major-версія пакета; нове необов'язкове поле — minor ([Версії, архів і дайджест](versions-and-archive.md#номер-версії)). Registry вид зміни не перевіряє.

**Профіль runtime.** Пакет посилається на профіль за іменем із номером (`python-extractor@1`). Registry перевіряє залежності лише під час публікації й наявні версії повторно не перевіряє, тож зміна бібліотек профілю не помічається Registry. Handler Runtime перевіряє профіль під час виконання й відхиляє відсутній профіль або образ із `dependency_not_allowed`.

**API Registry.** Операції версіоновано префіксом `/v1` (`registry.v1`). Можливості конкретного екземпляра — `GET /v1/info`: підтримувані `handler_kinds`, формат архіву (`zip`, `stored`, `sha256`), завантажені профілі runtime, підтримка `upstream_ports`.
