# HTTP API Registry

[Індекс усіх операцій](generated/README.md) містить method/path, параметри, body, відповіді та security із [registry.v1](../../../../../contracts/openapi/registry.v1.yaml). Нижче — поведінка клієнта та приклади понад декларації.

## Операції

| Операції | Призначення й гарантія |
|---|---|
| [listPackages](generated/listPackages.md), [getPackage](generated/getPackage.md) | Пошук/metadata, cursor pagination, ETag |
| [createPackage](generated/createPackage.md), [updatePackage](generated/updatePackage.md) | Створити каталог; update не змінює bytes версії |
| [listPackageVersions](generated/listPackageVersions.md), [getPackageVersion](generated/getPackageVersion.md) | Точні версії, digest/status/test_status |
| [publishPackageVersion](generated/publishPackageVersion.md) | ZIP або manifest/files; незмінна draft version |
| [getPackageFile](generated/getPackageFile.md), [downloadPackageArchive](generated/downloadPackageArchive.md) | Вміст файлу або точний canonical ZIP з ETag |
| [setPackageVersionStatus](generated/setPackageVersionStatus.md) | Явний дозволений перехід status з історією |
| [recordTestResults](generated/recordTestResults.md) | Запис уже виконаного TestReport; Registry не запускає тест |
| [forkPackage](generated/forkPackage.md), [diffPackage](generated/diffPackage.md) | Незалежний fork і порівняння файлів |
| [getUpstreamStatus](generated/getUpstreamStatus.md), [portUpstreamChanges](generated/portUpstreamChanges.md) | Побачити parent changes і явно перенести в нову version |
| [getJob](generated/getJob.md), [cancelJob](generated/cancelJob.md) | Асинхронна операція/скасування |
| [getHealth](generated/getHealth.md), [getServiceInfo](generated/getServiceInfo.md) | Доступність, capabilities/limits |

## Автентифікація й concurrency

Мережевий клієнт передає bearer token з registry scope: read/write/approve/admin за операцією та правами власника. Local none дозволяє всі scopes. Health доступний без bearer; info/metrics правила задає Jane Kit.

POST із побічним ефектом потребує Idempotency-Key. Той самий body/key повертає replay; інше body — 422 idempotency_key_reused, in-progress — 409. Metadata update використовує If-Match/ETag, mismatch — 412. Cursor непрозорий: передайте next_cursor назад без декодування.

## Асинхронність і errors

Тривала операція повертає 202 Job та Location; опитуйте Job до succeeded/failed/cancelled, тоді читайте result/error. Cancel приймається 202, для кінцевого job повертається 200. Не підміняйте Job state станом package version.

| Код | Значення для клієнта |
|---|---|
| validation_failed | Неправильний manifest/body/file/test report |
| dependency_not_allowed | Profile/library не дозволені |
| secret_detected | Публікація відхилена; прибрати секрет |
| version_exists | Точний номер уже опублікований |
| conflict | Package, status або merge конфлікт |
| precondition_failed | Metadata revision змінилася |
| limit_exceeded / payload_too_large | Перевищений package/request budget |
| upstream_unavailable | Profile/blob залежність недоступна |
| unauthorized / forbidden / not_found | Token/scope/owner або відсутній ресурс |

Помилка — application/problem+json; рішення приймайте за code і retryable. Прочитайте [чинний каталог](../../../../../contracts/docs/errors.md) для HTTP mapping.

## Приклади

[Публікація з перевіркою bytes/digest](../../integration.md#публікація-й-digest) і [offline export](../../integration.md#експорт-і-виконання) показують незалежного клієнта. Статуси/незмінність — у [internals](../../internals.md); ліміти — в [configuration](../../configuration.md).
