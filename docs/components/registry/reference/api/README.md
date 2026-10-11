# API registry.v1

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml). Не редагуйте вручну.

**Jane Handler Registry API**, версія `1.0.0`.

Репозиторій пакетів обробників усіх типів і правил колекторів (WP-05, ТЗ §7, §13.2). Технологія — docs/adr/0002-package-registry.md: власний сервіс із метаданими у власній БД і незмінними архівами (content-addressed, sha256) у blob-сховищі.

- Версія незмінна: повторна публікація тієї самої версії — 409 `version_exists`.
- Дайджест архіву (`sha256:`) обчислює репозиторій; споживачі перевіряють його.
- Секрети в пакеті відхиляються (`secret_detected`); вимоги до підключень — лише в маніфесті.
- Форк — незалежна копія з `fork_of`; зміни батька не впливають на форк. Перенесення змін батька — лише явною командою (`POST /upstream-ports`), результат — нова версія форку.
- Архів версії (`GET .../archive`) достатній для автономного використання без репозиторію.

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| GET | `/v1/packages` | [listPackages](listPackages.md) | `registry:read` | Пошук пакетів |
| POST | `/v1/packages` | [createPackage](createPackage.md) | `registry:write` | Створити пакет (без версій) |
| GET | `/v1/packages/{package_id}` | [getPackage](getPackage.md) | `registry:read` | Пакет і його налаштування |
| PATCH | `/v1/packages/{package_id}` | [updatePackage](updatePackage.md) | `registry:write` | Змінити налаштування пакета (назва, опис, заборона автозмін, застарілість) |
| GET | `/v1/packages/{package_id}/versions` | [listPackageVersions](listPackageVersions.md) | `registry:read` | Версії пакета |
| POST | `/v1/packages/{package_id}/versions` | [publishPackageVersion](publishPackageVersion.md) | `registry:write` | Опублікувати нову незмінну версію |
| GET | `/v1/packages/{package_id}/versions/{version}` | [getPackageVersion](getPackageVersion.md) | `registry:read` | Версія пакета — маніфест, дайджест, файли, статус |
| GET | `/v1/packages/{package_id}/versions/{version}/archive` | [downloadPackageArchive](downloadPackageArchive.md) | `registry:read` | Архів версії для автономного використання (ETag = дайджест) |
| GET | `/v1/packages/{package_id}/versions/{version}/file` | [getPackageFile](getPackageFile.md) | `registry:read` | Один файл версії (для редактора й diff в адмінці) |
| POST | `/v1/packages/{package_id}/versions/{version}/status` | [setPackageVersionStatus](setPackageVersionStatus.md) | `registry:approve` | Змінити статус версії (погодити, відхилити, позначити застарілою) з аудитом |
| POST | `/v1/packages/{package_id}/versions/{version}/test-results` | [recordTestResults](recordTestResults.md) | `registry:write` | Записати звіт прогону тестів версії (від handler-runtime або асистента) |
| POST | `/v1/packages/{package_id}/forks` | [forkPackage](forkPackage.md) | `registry:write` | Створити незалежний форк від версії |
| GET | `/v1/packages/{package_id}/diff` | [diffPackage](diffPackage.md) | `registry:read` | Відмінності між версіями або від батька (для форку) |
| GET | `/v1/packages/{package_id}/upstream` | [getUpstreamStatus](getUpstreamStatus.md) | `registry:read` | Оновлення батьківського пакета для форку |
| POST | `/v1/packages/{package_id}/upstream-ports` | [portUpstreamChanges](portUpstreamChanges.md) | `registry:write` | Явно перенести зміни батька у форк новою версією (асинхронно) |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `registry:read` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `registry:write` | Запит на скасування job (ідемпотентний) |
