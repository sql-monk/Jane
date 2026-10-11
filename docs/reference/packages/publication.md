# Публікація й статуси версії

Публікація перетворює каталог пакета на незмінну версію в Registry. Після публікації версія проходить перевірку тестами й погодження; активує її в етапі завдання Orchestrator. Операції — `registry.v1` ([довідник API Registry](../../components/registry/reference/api/README.md)); покроковий приклад із реальним виводом — [quickstart Registry](../../components/registry/quickstart.md).

## Зміст

- [Кроки публікації](#кроки-публікації)
- [Формати тіла](#формати-тіла)
- [Перевірки під час публікації](#перевірки-під-час-публікації)
- [Статуси версії](#статуси-версії)
- [Погодження й активація](#погодження-й-активація)

## Кроки публікації

![Послідовність публікації версії з перевірками й тестами](../../diagrams/packages/publish-sequence.light.png#gh-light-mode-only)
![Послідовність публікації версії з перевірками й тестами](../../diagrams/packages/publish-sequence.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/packages/publish-sequence.light.png), [темне](../../diagrams/packages/publish-sequence.dark.png); джерело — [publish-sequence.drawio](../../diagrams/packages/publish-sequence.drawio).

1. **Створити пакет**, якщо його ще немає: `POST /v1/packages` з `package_id`, `kind`, `title` (і за бажання `description`, `auto_changes_allowed`, `labels`). Пакет без версій — `latest_version: null`. Повторне створення — `409 conflict`.
2. **Опублікувати версію**: `POST /v1/packages/{id}/versions` з тілом zip або JSON. Успіх — `201`, заголовок `Location` і `PackageVersion` зі статусом `draft`, `test_status: unknown`.
3. **Записати звіти тестів**: `POST …/versions/{v}/test-results` ([Схеми й тести](schemas-and-tests.md#звіти-тестів-у-версії)).
4. **Погодити**: `POST …/versions/{v}/status` з `{"status": "approved"}`.

Усі `POST` Registry вимагають заголовок `Idempotency-Key`; без нього — `422 validation_failed`. Повтор із тим самим ключем і тілом повертає збережену відповідь із заголовком `Idempotency-Replayed: true`; той самий ключ з іншим тілом — `422 idempotency_key_reused`. Публікація вимагає scope `registry:write`, зміна статусу — `registry:approve`.

## Формати тіла

| `Content-Type` | Тіло | Коли зручно |
|---|---|---|
| `application/zip` (або `application/x-zip-compressed`) | ZIP із `jane-package.json` у корені | Пакет зібрано з каталогу (`jane-registry archive`, будь-який zip) |
| `application/json` | `{"manifest": {...}, "files": {"<шлях>": {"encoding": "utf-8" або "base64", "data": "..."}}}` | Генерація пакета програмно, зокрема Assistant |

У JSON-тілі `jane-package.json` не передається серед `files` (`manifest_in_files`): його формує Registry з `manifest`. Інший `Content-Type` — `415 unsupported_media_type`. Мінімальна JSON-публікація пакета правил:

```json
{
  "manifest": {
    "schema_version": "1",
    "package_id": "my.channel-rules",
    "version": "1.0.0",
    "kind": "collector-rules",
    "title": "My channel rules",
    "entry": {"collector": "telegram", "rules": "rules.json"},
    "provenance": {"created_by": "human"}
  },
  "files": {
    "rules.json": {
      "encoding": "utf-8",
      "data": "{\"collector\": \"telegram\", \"channels\": [{\"username\": \"jane_events_example\"}]}\n"
    }
  }
}
```

## Перевірки під час публікації

Перевірки виконуються в такому порядку; перша невдала зупиняє публікацію, і нічого не зберігається ([service.py](../../../services/registry/src/jane_registry/service.py)):

| № | Перевірка | Помилка |
|---|---|---|
| 1 | Розмір тіла не більший за `transfer.max_request_body_bytes` | `413 payload_too_large` |
| 2 | Пакет існує | `404 not_found` |
| 3 | ZIP читається: шляхи, симлінки, дублікати, кількість і розмір файлів; є `jane-package.json` з валідним JSON | `422 validation_failed` або `422 limit_exceeded` |
| 4 | Маніфест відповідає схемі | `422 validation_failed` |
| 5 | Кількість і сумарний розмір файлів, шляхи без збігу за регістром | `422 limit_exceeded` або `422 validation_failed` |
| 6 | `package_id`, `kind`, `fork_of`; перевірки понад схему ([список](manifest.md#перевірки-registry-понад-схему)) | `422 validation_failed` |
| 7 | Клієнт з `actor: llm` публікує лише `created_by: llm`; `created_by: llm` лише за `auto_changes_allowed: true` | `403 forbidden` |
| 8 | Такої версії ще немає | `409 version_exists` |
| 9 | Файли не більші за ліміт сканування; секретів немає; сканування вкладається в бюджет часу | `422 limit_exceeded` або `422 secret_detected` |
| 10 | Профіль runtime і Python-вимоги; залежності від пакетів | `422 dependency_not_allowed`, `502 upstream_unavailable` або `422 validation_failed` |
| 11 | Канонічний архів не більший за `packages.max_archive_bytes` | `422 limit_exceeded` |
| 12 | Кількість версій пакета менша за `packages.max_versions_per_package`; версію не опубліковано паралельно | `422 limit_exceeded` або `409 version_exists` |

Помилки мають формат `application/problem+json` ([errors.md](../../../contracts/docs/errors.md)); `errors[].pointer` вказує на поле маніфесту (`/manifest/...`) або файл (`/files/<шлях з ~1 замість />`). Реальна відповідь на файл правил, що не відповідає схемі:

```json
{
  "type": "urn:jane:problem:validation_failed",
  "title": "Validation failed",
  "status": 422,
  "detail": "package is not valid",
  "instance": "/v1/packages/my.channel-rules/versions",
  "code": "validation_failed",
  "retryable": false,
  "errors": [
    {
      "pointer": "/files/rules.json",
      "code": "schema",
      "message": "Additional properties are not allowed ('api_key', 'channels' were unexpected) (at /files/rules.json)"
    }
  ],
  "trace_id": "9d3d550a7c9354951a0236c28c0418b3"
}
```

Ліміти перевірок і їхні типові значення — [конфігурація Registry](../../components/registry/configuration.md).

## Статуси версії

![Стани версії пакета й дозволені переходи](../../diagrams/packages/version-states.light.png#gh-light-mode-only)
![Стани версії пакета й дозволені переходи](../../diagrams/packages/version-states.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/packages/version-states.light.png), [темне](../../diagrams/packages/version-states.dark.png); джерело — [version-states.drawio](../../diagrams/packages/version-states.drawio).

| Статус | Значення | Дозволені переходи |
|---|---|---|
| `draft` | Опубліковано, ще не погоджено | `approved`, `rejected`, `deprecated`, `yanked` |
| `approved` | Можна активувати в етапах | `deprecated`, `yanked` |
| `deprecated` | Не рекомендується для нових прив'язок | `approved`, `yanked` |
| `rejected` | Відхилено; кінцевий | — |
| `yanked` | Заборонено для нових прив'язок, архів доступний; кінцевий | — |

Перехід — `POST /v1/packages/{id}/versions/{v}/status` з `{"status": "...", "reason": "..."}` (`reason` до 2000 символів). Недозволений перехід — `409 conflict` з `details.current`. Кожен перехід додається в `status_history` з часом, іменем клієнта й причиною. Версії `rejected` і `yanked` не враховуються в `latest_version`.

Окремо від статусів версії пакет має прапорець `deprecated` (`PATCH /v1/packages/{id}`) — позначка для всього пакета.

## Погодження й активація

Registry зберігає статус, але не вирішує, яку версію виконувати: етап завдання посилається на версію, а змінює це посилання Orchestrator (`POST /v1/tasks/{task_id}/stages/{stage_id}/activations`):

| Вид активації | Умова в Orchestrator |
|---|---|
| `activate` | Версія `approved` |
| `rollback` | Версія не `yanked` |
| `auto_activate` | Політика джерела дозволяє автоактивацію, пакет має `auto_changes_allowed: true`, `test_summary.status` версії — `passed` |

Ручне погодження — зміна статусу людиною з `registry:approve` (Admin UI). Автоматичне — Assistant після успішних тестів на всіх прив'язках сам ставить `approved` і просить Orchestrator про `auto_activate`. Спільний пакет, який використовують кілька етапів, перевіряють на всіх прив'язках або змінюють через [форк](provenance-and-forks.md#форк).
