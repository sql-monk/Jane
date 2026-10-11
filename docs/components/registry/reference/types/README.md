# Типи й члени Registry

[Повний каталог декларацій](generated/README.md) містить усі публічні типи/члени, сигнатури, параметри, defaults, успадкування, доступ полів/properties та посилання на код. Нижче наведено семантику модулів, правила винятків і мінімальні приклади.

## Модулі

| Модуль | Призначення публічних членів |
|---|---|
| [app](generated/jane_registry.app.md) | Components/build_components/build_app складають stores, auth, schemas, routes і lifespan |
| [service](generated/jane_registry.service.md) | RegistryService виконує create/update/publish/status/report/fork/diff/port; wire functions формують v1 відповіді |
| [store](generated/jane_registry.store.md) | PackageRecord/VersionRecord/PackageFilter, MetadataStore та MemoryStore; pick_latest/media_matches/domain_matches задають пошук |
| [postgres](generated/jane_registry.postgres.md) | PostgresStore та shared job/idempotency adapters; open/migrate, optimistic updates, uniqueness |
| [blobs](generated/jane_registry.blobs.md) | BlobStore/FileBlobStore/S3BlobStore; put/get/exists працюють із bytes за digest |
| [archive](generated/jane_registry.archive.md) | Canonical ZIP, digest, безпечні шляхи й unpack limits |
| [validation](generated/jane_registry.validation.md) | ContractSchemas/PackageValidator перевіряють JSON і semantic references |
| [profiles](generated/jane_registry.profiles.md) | ProfileSource читає/cache profile; dependency checks звіряють library versions |
| [secrets](generated/jane_registry.secrets.md) | Secret findings/scan budgets/entropy; oversized unscanned файли відхиляються |
| [diffing](generated/jane_registry.diffing.md) | File metadata й bounded unified diff |
| [merge](generated/jane_registry.merge.md) | Тристороннє merge файлів/manifest; conflicts повертаються як дані |
| [export](generated/jane_registry.export.md) | Export closure/index та offline VerifyReport |
| [semver](generated/jane_registry.semver.md) | SemVer/order; build metadata не впливає на порівняння |
| [testing](generated/jane_registry.testing.md) | Test summary/report shape; не запускає sandbox |
| [auth](generated/jane_registry.auth.md) | Principal/scopes/owner access; bridge спільного Authenticator |
| [settings](generated/jane_registry.settings.md) | Settings/ServiceLimits/resolve_service_limits |
| [__main__](generated/jane_registry.__main__.md) | CLI serve/archive/verify/export та exit codes |

## Контракт членів і помилки

RegistryService async methods приймають principal, package/version та validated payload, повертають records або плани. Get package/version → NotFound; create → Conflict при duplicate; update → precondition_failed при неправильному ETag; publish → ValidationFailed/LimitExceeded/Forbidden, secret_detected або dependency_not_allowed; set_status → Conflict при забороненому чи concurrent переході.

Prepare_port повертає PortPlan із conflicts і merged files; apply_port публікує новий номер. Конфлікт — очікуваний результат аналізу, не дозвіл примусово замінити файли. Download відсутнього blob для відомої version → UpstreamUnavailable.

MetadataStore backend methods використовують власні AlreadyExists/VersionExists/RevisionMismatch/StatusMismatch/LimitReached; Service перетворює їх на JaneError. Callers backend рівня обробляють ці типи самі. Lifecycle open/close/check належить власнику Components.

Archive functions працюють із mapping path→bytes; unsafe path/ZIP/size → ArchiveError. Verify_archive повертає VerifyReport.ok/issues, а export_package може підняти ExportError/HTTP error при download/digest/dependency closure. SemVer(raw) піднімає ValueError для невалідного формату.

Record dataclass fields мають доступ із [декларацій](generated/jane_registry.store.md); search_fields — обчислювана read-only property, повертає похідний mapping manifest. Зміна local record не замінює транзакційний update store.

## Приклад canonical archive

```python
from pathlib import Path
from jane_registry.archive import canonical_archive, digest_of, files_from_dir

data = canonical_archive(files_from_dir(
    Path("examples/documentation/minimal-package")))
assert digest_of(data).startswith("sha256:")
```

Приклад використовується після uv sync із кореня checkout; він не запускає пакет. [Публікація через HTTP](../../integration.md#публікація-й-digest) показує Service behavior ззовні. Конфігураційні члени й обмеження докладно описані в [configuration](../../configuration.md).
