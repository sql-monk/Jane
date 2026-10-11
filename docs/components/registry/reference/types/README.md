# Типи й члени: Registry

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry](../../../../../services/registry/src/jane_registry). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_registry`](jane_registry.md) | 0 | 0 | Registry of the Jane platform. |
| [`jane_registry.__main__`](jane_registry.__main__.md) | 0 | 1 | Entry point. |
| [`jane_registry.app`](jane_registry.app.md) | 9 | 2 | HTTP API of the registry: ``contracts/openapi/registry.v1.yaml``. |
| [`jane_registry.archive`](jane_registry.archive.md) | 2 | 8 | Canonical package archive and its digest (ADR-0002 §2). |
| [`jane_registry.auth`](jane_registry.auth.md) | 2 | 1 | Authentication and scopes (ADR-0005): ``Authorization: Bearer <token>``, implemented by ``jane_kit.auth``. |
| [`jane_registry.blobs`](jane_registry.blobs.md) | 4 | 0 | Content-addressed archive storage (ADR-0002 §2): object ``<bucket>/<prefix><sha256 hex>``. |
| [`jane_registry.diffing`](jane_registry.diffing.md) | 0 | 4 | Differences between two package versions (``GET /v1/packages/{id}/diff``, ``PackageDiff``). |
| [`jane_registry.export`](jane_registry.export.md) | 2 | 2 | Export of package versions for autonomous use and their offline verification. |
| [`jane_registry.merge`](jane_registry.merge.md) | 2 | 2 | Three-way merge for an explicit upstream port (``POST /v1/packages/{id}/upstream-ports``). |
| [`jane_registry.postgres`](jane_registry.postgres.md) | 1 | 2 | PostgreSQL store of the registry (ADR-0002 §1): own database ``jane_registry``, tables in ``db_schema``. |
| [`jane_registry.profiles`](jane_registry.profiles.md) | 3 | 2 | Runtime profiles and the check of ``dependencies.python`` (ADR-0002 §4, ADR-0003). |
| [`jane_registry.secrets`](jane_registry.secrets.md) | 2 | 2 | Secret detection in package files (ADR-0002 §5, ADR-0006 §6): a finding rejects the publish with 422 ``secret_detected``. |
| [`jane_registry.semver`](jane_registry.semver.md) | 1 | 3 | Semantic Versioning 2.0.0 ordering (``SemVer`` of the contracts: exact versions, no ranges). |
| [`jane_registry.service`](jane_registry.service.md) | 2 | 2 | Domain logic of the registry (registry.v1): packages, immutable versions, statuses, test reports, forks, diff, upstream status and explicit upstream ports. HTTP |
| [`jane_registry.settings`](jane_registry.settings.md) | 10 | 1 | Settings and limits of the registry. Every limit has a safe default documented in README.md. |
| [`jane_registry.store`](jane_registry.store.md) | 10 | 3 | Metadata store of the registry: records, the store protocol and the in-memory implementation. |
| [`jane_registry.testing`](jane_registry.testing.md) | 0 | 5 | Helpers for tests of the registry and of its clients: sample packages and a test runtime profile. |
| [`jane_registry.validation`](jane_registry.validation.md) | 3 | 1 | Validation of a package before publication: manifest schema, kind &lt;-> entry, referenced files, schemas, collector rules, tests (ADR-0002, contracts/docs/hand |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`AlreadyExists`](jane_registry.store.md#клас-alreadyexists) | виняток | `jane_registry.store` |
| [`ArchiveError`](jane_registry.archive.md#клас-archiveerror) | виняток | `jane_registry.archive` |
| [`ArchiveLimits`](jane_registry.archive.md#клас-archivelimits) | dataclass (незмінний) | `jane_registry.archive` |
| [`Authenticator`](jane_registry.auth.md#клас-authenticator) | клас | `jane_registry.auth` |
| [`BlobIntegrityError`](jane_registry.blobs.md#клас-blobintegrityerror) | виняток | `jane_registry.blobs` |
| [`BlobLimits`](jane_registry.settings.md#клас-bloblimits) | клас | `jane_registry.settings` |
| [`BlobStore`](jane_registry.blobs.md#клас-blobstore) | протокол | `jane_registry.blobs` |
| [`build_app`](jane_registry.app.md#функція-build_app) | функція | `jane_registry.app` |
| [`build_components`](jane_registry.app.md#функція-build_components) | функція | `jane_registry.app` |
| [`canonical_archive`](jane_registry.archive.md#функція-canonical_archive) | функція | `jane_registry.archive` |
| [`check_actors`](jane_registry.auth.md#функція-check_actors) | функція | `jane_registry.auth` |
| [`check_dependencies`](jane_registry.profiles.md#функція-check_dependencies) | функція | `jane_registry.profiles` |
| [`check_package_path`](jane_registry.archive.md#функція-check_package_path) | функція | `jane_registry.archive` |
| [`check_unique_paths`](jane_registry.archive.md#функція-check_unique_paths) | функція | `jane_registry.archive` |
| [`Components`](jane_registry.app.md#клас-components) | dataclass | `jane_registry.app` |
| [`ContractSchemas`](jane_registry.validation.md#клас-contractschemas) | клас | `jane_registry.validation` |
| [`DbLimits`](jane_registry.settings.md#клас-dblimits) | клас | `jane_registry.settings` |
| [`DependencyProblem`](jane_registry.profiles.md#клас-dependencyproblem) | dataclass (незмінний) | `jane_registry.profiles` |
| [`diff_files`](jane_registry.diffing.md#функція-diff_files) | функція | `jane_registry.diffing` |
| [`diff_manifest`](jane_registry.diffing.md#функція-diff_manifest) | функція | `jane_registry.diffing` |
| [`DiffLimits`](jane_registry.settings.md#клас-difflimits) | клас | `jane_registry.settings` |
| [`digest_of`](jane_registry.archive.md#функція-digest_of) | функція | `jane_registry.archive` |
| [`escape_pointer`](jane_registry.diffing.md#функція-escape_pointer) | функція | `jane_registry.diffing` |
| [`export_package`](jane_registry.export.md#функція-export_package) | функція | `jane_registry.export` |
| [`ExportError`](jane_registry.export.md#клас-exporterror) | виняток | `jane_registry.export` |
| [`extractor_files`](jane_registry.testing.md#функція-extractor_files) | функція | `jane_registry.testing` |
| [`extractor_manifest`](jane_registry.testing.md#функція-extractor_manifest) | функція | `jane_registry.testing` |
| [`FileBlobStore`](jane_registry.blobs.md#клас-fileblobstore) | клас | `jane_registry.blobs` |
| [`FileContent`](jane_registry.app.md#клас-filecontent) | клас | `jane_registry.app` |
| [`files_from_dir`](jane_registry.archive.md#функція-files_from_dir) | функція | `jane_registry.archive` |
| [`find_contracts_dir`](jane_registry.validation.md#функція-find_contracts_dir) | функція | `jane_registry.validation` |
| [`ForkRequest`](jane_registry.app.md#клас-forkrequest) | клас | `jane_registry.app` |
| [`is_canonical`](jane_registry.archive.md#функція-is_canonical) | функція | `jane_registry.archive` |
| [`is_semver`](jane_registry.semver.md#функція-is_semver) | функція | `jane_registry.semver` |
| [`is_text`](jane_registry.diffing.md#функція-is_text) | функція | `jane_registry.diffing` |
| [`iso`](jane_registry.store.md#функція-iso) | функція | `jane_registry.store` |
| [`Issue`](jane_registry.validation.md#клас-issue) | dataclass (незмінний) | `jane_registry.validation` |
| [`LimitReached`](jane_registry.store.md#клас-limitreached) | виняток | `jane_registry.store` |
| [`main`](jane_registry.__main__.md#функція-main) | функція | `jane_registry.__main__` |
| [`manifest_bytes`](jane_registry.archive.md#функція-manifest_bytes) | функція | `jane_registry.archive` |
| [`max_version`](jane_registry.semver.md#функція-max_version) | функція | `jane_registry.semver` |
| [`MemoryStore`](jane_registry.store.md#клас-memorystore) | клас | `jane_registry.store` |
| [`merge3_lines`](jane_registry.merge.md#функція-merge3_lines) | функція | `jane_registry.merge` |
| [`merge_packages`](jane_registry.merge.md#функція-merge_packages) | функція | `jane_registry.merge` |
| [`MergeConflict`](jane_registry.merge.md#клас-mergeconflict) | dataclass (незмінний) | `jane_registry.merge` |
| [`MergeResult`](jane_registry.merge.md#клас-mergeresult) | dataclass | `jane_registry.merge` |
| [`MetadataStore`](jane_registry.store.md#клас-metadatastore) | протокол | `jane_registry.store` |
| [`now`](jane_registry.store.md#функція-now) | функція | `jane_registry.store` |
| [`oversized_files`](jane_registry.secrets.md#функція-oversized_files) | функція | `jane_registry.secrets` |
| [`package_wire`](jane_registry.service.md#функція-package_wire) | функція | `jane_registry.service` |
| [`PackageCreate`](jane_registry.app.md#клас-packagecreate) | клас | `jane_registry.app` |
| [`PackageFilter`](jane_registry.store.md#клас-packagefilter) | dataclass (незмінний) | `jane_registry.store` |
| [`PackageLimits`](jane_registry.settings.md#клас-packagelimits) | клас | `jane_registry.settings` |
| [`PackagePatch`](jane_registry.app.md#клас-packagepatch) | клас | `jane_registry.app` |
| [`PackageRecord`](jane_registry.store.md#клас-packagerecord) | dataclass | `jane_registry.store` |
| [`PackageValidator`](jane_registry.validation.md#клас-packagevalidator) | клас | `jane_registry.validation` |
| [`parse_profiles`](jane_registry.profiles.md#функція-parse_profiles) | функція | `jane_registry.profiles` |
| [`pick_latest`](jane_registry.store.md#функція-pick_latest) | функція | `jane_registry.store` |
| [`PortPlan`](jane_registry.service.md#клас-portplan) | dataclass (незмінний) | `jane_registry.service` |
| [`postgres_idempotency_store`](jane_registry.postgres.md#функція-postgres_idempotency_store) | функція | `jane_registry.postgres` |
| [`postgres_job_store`](jane_registry.postgres.md#функція-postgres_job_store) | функція | `jane_registry.postgres` |
| [`PostgresStore`](jane_registry.postgres.md#клас-postgresstore) | клас | `jane_registry.postgres` |
| [`Principal`](jane_registry.auth.md#клас-principal) | dataclass (незмінний) | `jane_registry.auth` |
| [`ProfileLimits`](jane_registry.settings.md#клас-profilelimits) | клас | `jane_registry.settings` |
| [`ProfileSource`](jane_registry.profiles.md#клас-profilesource) | клас | `jane_registry.profiles` |
| [`publish_body`](jane_registry.testing.md#функція-publish_body) | функція | `jane_registry.testing` |
| [`PublishRequest`](jane_registry.app.md#клас-publishrequest) | клас | `jane_registry.app` |
| [`read_archive`](jane_registry.archive.md#функція-read_archive) | функція | `jane_registry.archive` |
| [`RecoveryLimits`](jane_registry.settings.md#клас-recoverylimits) | клас | `jane_registry.settings` |
| [`RegistryService`](jane_registry.service.md#клас-registryservice) | клас | `jane_registry.service` |
| [`RequestLimits`](jane_registry.settings.md#клас-requestlimits) | клас | `jane_registry.settings` |
| [`resolve_service_limits`](jane_registry.settings.md#функція-resolve_service_limits) | функція | `jane_registry.settings` |
| [`RevisionMismatch`](jane_registry.store.md#клас-revisionmismatch) | виняток | `jane_registry.store` |
| [`run_extractor_from_archive`](jane_registry.testing.md#функція-run_extractor_from_archive) | функція | `jane_registry.testing` |
| [`RuntimeProfile`](jane_registry.profiles.md#клас-runtimeprofile) | dataclass (незмінний) | `jane_registry.profiles` |
| [`S3BlobStore`](jane_registry.blobs.md#клас-s3blobstore) | клас | `jane_registry.blobs` |
| [`scan_files`](jane_registry.secrets.md#функція-scan_files) | функція | `jane_registry.secrets` |
| [`ScanBudgetExceeded`](jane_registry.secrets.md#клас-scanbudgetexceeded) | виняток | `jane_registry.secrets` |
| [`SecretFinding`](jane_registry.secrets.md#клас-secretfinding) | dataclass (незмінний) | `jane_registry.secrets` |
| [`SecretScanLimits`](jane_registry.settings.md#клас-secretscanlimits) | клас | `jane_registry.settings` |
| [`SemVer`](jane_registry.semver.md#клас-semver) | клас | `jane_registry.semver` |
| [`ServiceLimits`](jane_registry.settings.md#клас-servicelimits) | клас | `jane_registry.settings` |
| [`Settings`](jane_registry.settings.md#клас-settings) | модель Pydantic | `jane_registry.settings` |
| [`sort_versions`](jane_registry.semver.md#функція-sort_versions) | функція | `jane_registry.semver` |
| [`StatusChange`](jane_registry.app.md#клас-statuschange) | клас | `jane_registry.app` |
| [`StatusMismatch`](jane_registry.store.md#клас-statusmismatch) | виняток | `jane_registry.store` |
| [`TestResultsRecord`](jane_registry.app.md#клас-testresultsrecord) | модель Pydantic | `jane_registry.app` |
| [`UpstreamPortRequest`](jane_registry.app.md#клас-upstreamportrequest) | клас | `jane_registry.app` |
| [`verify_archive`](jane_registry.export.md#функція-verify_archive) | функція | `jane_registry.export` |
| [`VerifyReport`](jane_registry.export.md#клас-verifyreport) | dataclass | `jane_registry.export` |
| [`version_wire`](jane_registry.service.md#функція-version_wire) | функція | `jane_registry.service` |
| [`VersionExists`](jane_registry.store.md#клас-versionexists) | виняток | `jane_registry.store` |
| [`VersionRecord`](jane_registry.store.md#клас-versionrecord) | dataclass | `jane_registry.store` |
| [`zip_of`](jane_registry.testing.md#функція-zip_of) | функція | `jane_registry.testing` |
