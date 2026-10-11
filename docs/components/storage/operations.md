# Storage: експлуатація

Постійні дані належать адаптерам; memory-конфігурації connections, jobs і недавні invocation results потребують окремого відтворення після рестарту.

[Спостереження](#спостереження) · [Оновлення](#оновлення) · [Резервування](#резервування) · [Відновлення](#відновлення) · [Типові проблеми](#типові-проблеми)

## Спостереження

`GET /v1/health` перевіряє готовність процесу, `GET /v1/info` показує доступні adapters/packages та контрактні limits. Успішний health без цільового тестового запису не доводить доступність кожного сховища. `POST /v1/connections/{id}/test` з Idempotency-Key перевіряє конкретну connection.

`/metrics` містить загальні HTTP/health метрики та `storage_writes_total{adapter,status}` і `storage_failed_invocations_total{kind}`. Структуровані журнали містять trace_id/request_id, configured limits і перелік завантажених пакетів; секретні значення не виводьте. Для росту conflict failures перевірте concurrent writers, lock timeout і conflict_retries, а не лише збільшуйте attempts.

## Стан і статистика сховища (WP-24)

`GET /v1/storage-status?connection_id=raw-files` потребує `storage:read` та повертає останню
явну перевірку. `POST /v1/storage-status/checks` з тілом `{"connection_id":"raw-files"}`
і `Idempotency-Key` потребує `connections:write`, негайно повертає 202 Job + Location.
Опитуйте GET Location до succeeded; result містить StorageStatus. Job перевіряє health і статистику.
Звичайний `POST /v1/connections/raw-files/test` перевіряє лише health, без інвентаризації. GET не відкриває адаптер, не читає payload та не обходить backend.
GET `/v1/connections` і `/v1/connections/{id}` доступні також читачу `storage:read`.

До перевірки, після рестарту, DELETE чи зміни визначення: availability `unknown`, checked_at null,
невідомі числові показники null. Snapshot локальний процесу: за кількох реплік наступний GET може
потрапити в іншу репліку і повернути unknown. Це відображається чесно; потрібна sticky routing,
якщо оператор хоче бачити одну перевірку між репліками. Нові записи не оновлюють snapshot;
використовуйте checked_at для оцінки свіжості та явну повторну перевірку.

Filesystem під час явної перевірки рахує stored-object metadata у namespace підключення:
`object_count` та суму payload `total_size_bytes`. Це не вільний/зайнятий диск, не кількість сутностей,
не history або metadata overhead; файли поза індексом Jane не входять. Payload не читається.
Інші адаптери наразі віддають null та `adapter_statistics_not_supported`; нулі лише для перевіреного
порожнього файлового namespace. Причина помилки не містить resolved secrets.

Фільтри матеріалів залишаються `source_id`, `material_id`/`material_ids`, `since`/`until` за `stored_at`
(початок включно, кінець виключно), `connection_id`, cursor/limit. Стан обробки належить оркестратору;
storage не читає його таблиці. Зовнішні сховища не обходяться заради статистики.

Приклад для стороннього читача: `GET /v1/storage-status?connection_id=raw-files`
з `Authorization: Bearer <ключ зі storage:read>`. Звичайна команда тестів:
`uv run pytest services/storage/tests services/storage/adapters/files/tests -q`.


Інвентаризація виконується в JobRunner з налаштованими `jobs.max_concurrent_jobs`, `jobs.max_queued_jobs`,
`jobs.job_timeout_ms`; probe додатково обмежено `timeouts.request_timeout_ms` (типово 30000 ms).
У filesystem cancel/timeout встановлює cooperative stop event; worker припиняє обходи між metadata records.
Помилка статистики не скасовує успішний health: availability available, статистики null,
причина statistics_check_failed. POST replay повертає той самий Job і Idempotency-Replayed=true.

## Оновлення

1. Завершіть або скасуйте власні активні jobs, зупиніть писачів у ті самі adapters.
2. Збережіть connections file/secret refs, пакети та всі постійні дані.
3. Оновіть pinned environment і дистрибутиви адаптерів; формат їхніх даних звірте з compatibility tests.
4. Запустіть процес, перевірте info, connection test і окрему тестову delivery.

Jobs та HTTP idempotency cache не є спільними між екземплярами. Дедуплікація постійної доставки забезпечується адаптером, але `GET /v1/invocations/{id}` іншого процесу може не знати недавнього invocation. Додавання екземпляра не переносить його connections, тож застосуйте той самий initial file або контрольовані API PUT.

## Резервування

Для filesystem зупиніть усіх писачів і скопіюйте весь base_path разом з entities/history/deliveries/objects/index. Копія лише RAW файлів утрачає entity history і delivery дедуплікацію. У quickstart каталозі:

```powershell
uv run python -c "from shutil import copytree; copytree('.jane/storage-demo', '.jane/storage-backup')"
```

Ціль має бути новим каталогом; copytree не перезаписує існуючий backup. Для PostgreSQL/MongoDB/SQL Server використайте consistent backup власного сховища; для S3/MinIO збережіть objects і metadata/index того самого адаптера. Secret values резервуються окремим захищеним механізмом, не в пакеті чи репозиторії. Власний transit_dir є TTL даними, не заміною постійного backup.

## Відновлення

Для filesystem відновіть у новий каталог:

```powershell
uv run python -c "from shutil import copytree; copytree('.jane/storage-backup', '.jane/storage-restored')"
```

Змініть connection.params.base_path на `.jane/storage-restored`, запустіть Storage й перевірте entity state/history, кількість об’єктів та SHA-256 вмісту. Повтор відомої delivery має повернути duplicate. Старий каталог збережіть до успішної перевірки. Для database/object-store адаптера відновлюйте всі власні collections/tables/keys узгоджено, після чого так само перевірте API.

Процедура цього розділу звірена з даними адаптера; власний backup/restore цикл у цьому модульному пакеті не виконувався. Координатор має окремі platform backup/restore докази у [звіті експлуатації](../../delivery/documentation/DOC-08.md).

## Типові проблеми

| Симптом | Перевірка | Дія |
|---|---|---|
| `not_found` пакета | info.capabilities.packages, version, registry_url | Встановіть пакет або налаштуйте Registry |
| `connection_error` у HTTP 200 | HandlerResult.failure і connection test | Права каталогу, endpoint, driver, secrets |
| `validation_failed` / `digest_mismatch` | Строгий params_schema і package digest | Звірте exact version/digest; не вимикайте validation |
| `payload_too_large` | transfer.max_request_body_bytes | Надішліть ContentRef blob і налаштуйте дозволений transport |
| Metadata є, material відсутній | Persistent URI / inline threshold / transit_dir | Налаштуйте власний transit або використайте /content |
| `stale` чи `partially_stale` | observation ordering і field_orders | Перевірте час джерела; stale не є connection failure |
| `idempotency_key_reused` | Ключ і точне тіло | Для нової доставки новий ключ |
| Об’єкт не знайдено після рестарту | Той самий base_path/connection | Відновіть connections file; не створюйте порожній інший root |

[Параметри й ліміти](configuration.md), [API-послідовність](integration.md#виклик-і-відповіді).
