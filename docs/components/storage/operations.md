# Storage: експлуатація

Постійні дані належать адаптерам; memory-конфігурації connections, jobs і недавні invocation results потребують окремого відтворення після рестарту.

[Спостереження](#спостереження) · [Оновлення](#оновлення) · [Резервування](#резервування) · [Відновлення](#відновлення) · [Типові проблеми](#типові-проблеми)

## Спостереження

`GET /v1/health` перевіряє готовність процесу, `GET /v1/info` показує доступні adapters/packages та контрактні limits. Успішний health без цільового тестового запису не доводить доступність кожного сховища. `POST /v1/connections/{id}/test` з Idempotency-Key перевіряє конкретну connection.

`/metrics` містить загальні HTTP/health метрики та `storage_writes_total{adapter,status}` і `storage_failed_invocations_total{kind}`. Структуровані журнали містять trace_id/request_id, configured limits і перелік завантажених пакетів; секретні значення не виводьте. Для росту conflict failures перевірте concurrent writers, lock timeout і conflict_retries, а не лише збільшуйте attempts.

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
