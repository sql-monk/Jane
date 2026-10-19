# Типи й члени: Storage

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage](../../../../../services/storage/src/jane_storage), [services/storage/adapters/files/src/jane_storage_files](../../../../../services/storage/adapters/files/src/jane_storage_files), [services/storage/adapters/postgres/src/jane_storage_postgres](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres), [services/storage/adapters/sqlserver/src/jane_storage_sqlserver](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver), [services/storage/adapters/mongodb/src/jane_storage_mongodb](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb), [services/storage/adapters/minio/src/jane_storage_minio](../../../../../services/storage/adapters/minio/src/jane_storage_minio), [services/storage/adapters/s3/src/jane_storage_s3](../../../../../services/storage/adapters/s3/src/jane_storage_s3). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_storage`](jane_storage.md) | 0 | 0 | Storage of the Jane platform. |
| [`jane_storage.__main__`](jane_storage.__main__.md) | 0 | 1 | Entry point: ``python -m jane_storage`` (host/port from ``JANE_STORAGE_HOST/PORT``). |
| [`jane_storage.adapters`](jane_storage.adapters.md) | 1 | 4 | Adapter registry: adapters are separate distributions discovered through entry points. |
| [`jane_storage.app`](jane_storage.app.md) | 1 | 4 | HTTP API of the storage service. |
| [`jane_storage.codec`](jane_storage.codec.md) | 0 | 16 | Adapter kit: JSON documents for the dataclasses of ``jane_contracts.storage_adapter``. |
| [`jane_storage.compat`](jane_storage.compat.md) | 0 | 0 | Adapter compatibility suite C-01…C-16 (contracts/docs/storage-adapter.md) — reusable by every adapter. |
| [`jane_storage.compat.suite`](jane_storage.compat.suite.md) | 3 | 0 | Scenarios C-01…C-16 as a pytest base class (see :mod:`jane_storage.compat`). |
| [`jane_storage.connections`](jane_storage.connections.md) | 4 | 0 | Managed connections of the storage executor (ADR-0006) and the pool of opened adapters. |
| [`jane_storage.content`](jane_storage.content.md) | 2 | 0 | Reading ``ContentRef`` (inline / blob) with sha256 and size checks (ADR-0004). |
| [`jane_storage.engine`](jane_storage.engine.md) | 2 | 2 | Storage core: applies one entity record or one object to an adapter (contracts/docs/storage-adapter.md). |
| [`jane_storage.formats`](jane_storage.formats.md) | 1 | 6 | Storage formats (TZ §5): RAW web pages as HTML by default, other results as JSON; overridable. |
| [`jane_storage.handler`](jane_storage.handler.md) | 4 | 1 | Storage handler: ``HandlerInvocation`` → ``HandlerResult`` (handler.v1, ``handler_kind: storage``). |
| [`jane_storage.keys`](jane_storage.keys.md) | 0 | 7 | Deterministic keys built by the storage core (contracts/docs/storage-adapter.md). |
| [`jane_storage.merge`](jane_storage.merge.md) | 2 | 3 | Merge of an ``EntityRecord`` into the current state — a pure function (no I/O). |
| [`jane_storage.packages`](jane_storage.packages.md) | 5 | 5 | Storage packages (``kind: storage``): catalog of installed packages, canonical archive, publication. |
| [`jane_storage.policy`](jane_storage.policy.md) | 4 | 3 | Secret policy of storage connections (coordinator decision, same as WP-10 ``llm`` and WP-04 ``telegram-collector``). |
| [`jane_storage.registry_packages`](jane_storage.registry_packages.md) | 1 | 2 | Storage packages from the handler registry (``registry.v1``: ``GET /v1/packages/{id}/versions/{v}/archive``). |
| [`jane_storage.settings`](jane_storage.settings.md) | 9 | 1 | Settings and limits of the service. Every limit has a safe default documented in README.md. |
| [`jane_storage_files`](jane_storage_files.md) | 1 | 1 | Filesystem adapter of the Jane storage handler (``kind: filesystem``). |
| [`jane_storage_postgres`](jane_storage_postgres.md) | 1 | 1 | PostgreSQL adapter of the Jane storage handler (``kind: postgresql``, asyncpg). |
| [`jane_storage_postgres.news_layout`](jane_storage_postgres.news_layout.md) | 0 | 4 | Relational layout ``news`` of the PostgreSQL adapter (connection parameter ``params.layout = "news"``). |
| [`jane_storage_postgres.news_layout.__main__`](jane_storage_postgres.news_layout.__main__.md) | 0 | 1 | CLI of the ``news`` layout: ``python -m jane_storage_postgres.news_layout rebuild --schema news …``. |
| [`jane_storage_postgres.news_layout.ddl`](jane_storage_postgres.news_layout.ddl.md) | 0 | 1 | DDL of the ``news`` layout: numbered migrations over ``<schema>``. |
| [`jane_storage_postgres.news_layout.mapping`](jane_storage_postgres.news_layout.mapping.md) | 4 | 4 | Pure mapping of an entity snapshot to the rows of the ``news`` layout (no database). |
| [`jane_storage_sqlserver`](jane_storage_sqlserver.md) | 1 | 1 | SQL Server adapter of the Jane storage handler (``kind: sqlserver``, pymssql / FreeTDS). |
| [`jane_storage_mongodb`](jane_storage_mongodb.md) | 1 | 1 | MongoDB adapter of the Jane storage handler (``kind: mongodb``, PyMongo ``AsyncMongoClient``). |
| [`jane_storage_minio`](jane_storage_minio.md) | 1 | 1 | MinIO adapter of the Jane storage handler (``kind: minio``). |
| [`jane_storage_s3`](jane_storage_s3.md) | 2 | 1 | S3 adapter of the Jane storage handler (``kind: s3``); also the base of the MinIO adapter. |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`adapter_class`](jane_storage.adapters.md#функція-adapter_class) | функція | `jane_storage.adapters` |
| [`AdapterCompatSuite`](jane_storage.compat.suite.md#клас-adaptercompatsuite) | клас | `jane_storage.compat.suite` |
| [`AdapterPool`](jane_storage.connections.md#клас-adapterpool) | клас | `jane_storage.connections` |
| [`AdapterProvider`](jane_storage.handler.md#клас-adapterprovider) | протокол | `jane_storage.handler` |
| [`Adapters`](jane_storage.settings.md#клас-adapters) | клас | `jane_storage.settings` |
| [`Address`](jane_storage.policy.md#клас-address) | dataclass (незмінний) | `jane_storage.policy` |
| [`AddressError`](jane_storage.policy.md#клас-addresserror) | виняток | `jane_storage.policy` |
| [`ArchiveLimits`](jane_storage.packages.md#клас-archivelimits) | dataclass (незмінний) | `jane_storage.packages` |
| [`available_adapters`](jane_storage.adapters.md#функція-available_adapters) | функція | `jane_storage.adapters` |
| [`backoff_ms`](jane_storage.engine.md#функція-backoff_ms) | функція | `jane_storage.engine` |
| [`build_app`](jane_storage.app.md#функція-build_app) | функція | `jane_storage.app` |
| [`build_data_object`](jane_storage.formats.md#функція-build_data_object) | функція | `jane_storage.formats` |
| [`build_raw_object`](jane_storage.formats.md#функція-build_raw_object) | функція | `jane_storage.formats` |
| [`canonical_archive`](jane_storage.packages.md#функція-canonical_archive) | функція | `jane_storage.packages` |
| [`canonical_key`](jane_storage.keys.md#функція-canonical_key) | функція | `jane_storage.keys` |
| [`check_ref`](jane_storage.registry_packages.md#функція-check_ref) | функція | `jane_storage.registry_packages` |
| [`CompatEnv`](jane_storage.compat.suite.md#клас-compatenv) | клас | `jane_storage.compat.suite` |
| [`CompatTarget`](jane_storage.compat.suite.md#клас-compattarget) | клас | `jane_storage.compat.suite` |
| [`ConflictRetries`](jane_storage.settings.md#клас-conflictretries) | клас | `jane_storage.settings` |
| [`ConflictRetriesExhausted`](jane_storage.engine.md#клас-conflictretriesexhausted) | виняток | `jane_storage.engine` |
| [`ConnectionPolicy`](jane_storage.policy.md#клас-connectionpolicy) | dataclass (незмінний) | `jane_storage.policy` |
| [`ConnectionRegistry`](jane_storage.connections.md#клас-connectionregistry) | клас | `jane_storage.connections` |
| [`ContentError`](jane_storage.content.md#клас-contenterror) | виняток | `jane_storage.content` |
| [`ContentReader`](jane_storage.content.md#клас-contentreader) | клас | `jane_storage.content` |
| [`create_adapter`](jane_storage.adapters.md#функція-create_adapter) | функція | `jane_storage.adapters` |
| [`delivery_from_json`](jane_storage.codec.md#функція-delivery_from_json) | функція | `jane_storage.codec` |
| [`delivery_to_json`](jane_storage.codec.md#функція-delivery_to_json) | функція | `jane_storage.codec` |
| [`DependencyNotAllowed`](jane_storage.packages.md#клас-dependencynotallowed) | виняток | `jane_storage.packages` |
| [`digest_mismatch`](jane_storage.registry_packages.md#функція-digest_mismatch) | функція | `jane_storage.registry_packages` |
| [`dumps`](jane_storage.codec.md#функція-dumps) | функція | `jane_storage.codec` |
| [`ensure_layout`](jane_storage_postgres.news_layout.md#функція-ensure_layout) | функція | `jane_storage_postgres.news_layout` |
| [`entities_format`](jane_storage.formats.md#функція-entities_format) | функція | `jane_storage.formats` |
| [`entity_ack`](jane_storage.codec.md#функція-entity_ack) | функція | `jane_storage.codec` |
| [`entity_delivery_key`](jane_storage.keys.md#функція-entity_delivery_key) | функція | `jane_storage.keys` |
| [`entity_state`](jane_storage.app.md#функція-entity_state) | функція | `jane_storage.app` |
| [`EntityRows`](jane_storage_postgres.news_layout.mapping.md#клас-entityrows) | dataclass (незмінний) | `jane_storage_postgres.news_layout.mapping` |
| [`event_from_json`](jane_storage.codec.md#функція-event_from_json) | функція | `jane_storage.codec` |
| [`event_to_json`](jane_storage.codec.md#функція-event_to_json) | функція | `jane_storage.codec` |
| [`EvidenceRow`](jane_storage_postgres.news_layout.mapping.md#клас-evidencerow) | dataclass (незмінний) | `jane_storage_postgres.news_layout.mapping` |
| [`extension_for`](jane_storage.formats.md#функція-extension_for) | функція | `jane_storage.formats` |
| [`FilesystemAdapter`](jane_storage_files.md#клас-filesystemadapter) | клас | `jane_storage_files` |
| [`format_ts`](jane_storage.codec.md#функція-format_ts) | функція | `jane_storage.codec` |
| [`history_entry`](jane_storage.app.md#функція-history_entry) | функція | `jane_storage.app` |
| [`InvalidFormat`](jane_storage.formats.md#клас-invalidformat) | виняток | `jane_storage.formats` |
| [`InvalidRecord`](jane_storage.merge.md#клас-invalidrecord) | виняток | `jane_storage.merge` |
| [`InvocationResults`](jane_storage.app.md#клас-invocationresults) | клас | `jane_storage.app` |
| [`Invocations`](jane_storage.settings.md#клас-invocations) | клас | `jane_storage.settings` |
| [`key_digest`](jane_storage.keys.md#функція-key_digest) | функція | `jane_storage.keys` |
| [`KindAddresses`](jane_storage.policy.md#клас-kindaddresses) | dataclass (незмінний) | `jane_storage.policy` |
| [`latest_version`](jane_storage_postgres.news_layout.md#функція-latest_version) | функція | `jane_storage_postgres.news_layout` |
| [`load_package`](jane_storage.packages.md#функція-load_package) | функція | `jane_storage.packages` |
| [`loads`](jane_storage.codec.md#функція-loads) | функція | `jane_storage.codec` |
| [`main`](jane_storage.__main__.md#функція-main) | функція | `jane_storage.__main__` |
| [`main`](jane_storage.packages.md#функція-main) | функція | `jane_storage.packages` |
| [`main`](jane_storage_postgres.news_layout.__main__.md#функція-main) | функція | `jane_storage_postgres.news_layout.__main__` |
| [`manifest_test_cases`](jane_storage.app.md#функція-manifest_test_cases) | функція | `jane_storage.app` |
| [`map_snapshot`](jane_storage_postgres.news_layout.mapping.md#функція-map_snapshot) | функція | `jane_storage_postgres.news_layout.mapping` |
| [`material_metadata`](jane_storage.formats.md#функція-material_metadata) | функція | `jane_storage.formats` |
| [`MentionRow`](jane_storage_postgres.news_layout.mapping.md#клас-mentionrow) | dataclass (незмінний) | `jane_storage_postgres.news_layout.mapping` |
| [`merge`](jane_storage.merge.md#функція-merge) | функція | `jane_storage.merge` |
| [`MergeResult`](jane_storage.merge.md#клас-mergeresult) | dataclass (незмінний) | `jane_storage.merge` |
| [`migrations_table_sql`](jane_storage_postgres.news_layout.ddl.md#функція-migrations_table_sql) | функція | `jane_storage_postgres.news_layout.ddl` |
| [`MinioAdapter`](jane_storage_minio.md#клас-minioadapter) | клас | `jane_storage_minio` |
| [`MongoAdapter`](jane_storage_mongodb.md#клас-mongoadapter) | клас | `jane_storage_mongodb` |
| [`network_addresses`](jane_storage.policy.md#функція-network_addresses) | функція | `jane_storage.policy` |
| [`new_id`](jane_storage.handler.md#функція-new_id) | функція | `jane_storage.handler` |
| [`object_delivery_key`](jane_storage.keys.md#функція-object_delivery_key) | функція | `jane_storage.keys` |
| [`object_id_for`](jane_storage.keys.md#функція-object_id_for) | функція | `jane_storage.keys` |
| [`object_key`](jane_storage.keys.md#функція-object_key) | функція | `jane_storage.keys` |
| [`object_record_from_json`](jane_storage.codec.md#функція-object_record_from_json) | функція | `jane_storage.codec` |
| [`object_record_to_json`](jane_storage.codec.md#функція-object_record_to_json) | функція | `jane_storage.codec` |
| [`Objects`](jane_storage.settings.md#клас-objects) | клас | `jane_storage.settings` |
| [`order_from_json`](jane_storage.codec.md#функція-order_from_json) | функція | `jane_storage.codec` |
| [`order_of`](jane_storage.merge.md#функція-order_of) | функція | `jane_storage.merge` |
| [`order_to_json`](jane_storage.codec.md#функція-order_to_json) | функція | `jane_storage.codec` |
| [`package_dir`](jane_storage_files.md#функція-package_dir) | функція | `jane_storage_files` |
| [`package_dir`](jane_storage_postgres.md#функція-package_dir) | функція | `jane_storage_postgres` |
| [`package_dir`](jane_storage_sqlserver.md#функція-package_dir) | функція | `jane_storage_sqlserver` |
| [`package_dir`](jane_storage_mongodb.md#функція-package_dir) | функція | `jane_storage_mongodb` |
| [`package_dir`](jane_storage_minio.md#функція-package_dir) | функція | `jane_storage_minio` |
| [`package_dir`](jane_storage_s3.md#функція-package_dir) | функція | `jane_storage_s3` |
| [`package_dirs`](jane_storage.adapters.md#функція-package_dirs) | функція | `jane_storage.adapters` |
| [`package_from_archive`](jane_storage.packages.md#функція-package_from_archive) | функція | `jane_storage.packages` |
| [`PackageCatalog`](jane_storage.packages.md#клас-packagecatalog) | клас | `jane_storage.packages` |
| [`PackageLimits`](jane_storage.settings.md#клас-packagelimits) | клас | `jane_storage.settings` |
| [`PackageSource`](jane_storage.handler.md#клас-packagesource) | протокол | `jane_storage.handler` |
| [`parse_date`](jane_storage_postgres.news_layout.mapping.md#функція-parse_date) | функція | `jane_storage_postgres.news_layout.mapping` |
| [`parse_time`](jane_storage_postgres.news_layout.mapping.md#функція-parse_time) | функція | `jane_storage_postgres.news_layout.mapping` |
| [`parse_timestamp`](jane_storage_postgres.news_layout.mapping.md#функція-parse_timestamp) | функція | `jane_storage_postgres.news_layout.mapping` |
| [`parse_ts`](jane_storage.codec.md#функція-parse_ts) | функція | `jane_storage.codec` |
| [`PostgresAdapter`](jane_storage_postgres.md#клас-postgresadapter) | клас | `jane_storage_postgres` |
| [`Prepared`](jane_storage.handler.md#клас-prepared) | dataclass | `jane_storage.handler` |
| [`publish`](jane_storage.packages.md#функція-publish) | функція | `jane_storage.packages` |
| [`PublishOutcome`](jane_storage.packages.md#клас-publishoutcome) | dataclass (незмінний) | `jane_storage.packages` |
| [`raw_format`](jane_storage.formats.md#функція-raw_format) | функція | `jane_storage.formats` |
| [`rebuild`](jane_storage_postgres.news_layout.md#функція-rebuild) | функція | `jane_storage_postgres.news_layout` |
| [`redact`](jane_storage.policy.md#функція-redact) | функція | `jane_storage.policy` |
| [`RegistryPackages`](jane_storage.registry_packages.md#клас-registrypackages) | клас | `jane_storage.registry_packages` |
| [`resolve_service_limits`](jane_storage.settings.md#функція-resolve_service_limits) | функція | `jane_storage.settings` |
| [`S3Adapter`](jane_storage_s3.md#клас-s3adapter) | клас | `jane_storage_s3` |
| [`S3Profile`](jane_storage_s3.md#клас-s3profile) | dataclass (незмінний) | `jane_storage_s3` |
| [`safe_segment`](jane_storage.keys.md#функція-safe_segment) | функція | `jane_storage.keys` |
| [`SecretUnresolved`](jane_storage.connections.md#клас-secretunresolved) | виняток | `jane_storage.connections` |
| [`service_url`](jane_storage.policy.md#функція-service_url) | функція | `jane_storage.policy` |
| [`ServiceLimits`](jane_storage.settings.md#клас-servicelimits) | клас | `jane_storage.settings` |
| [`Settings`](jane_storage.settings.md#клас-settings) | модель Pydantic | `jane_storage.settings` |
| [`snapshot_from_json`](jane_storage.codec.md#функція-snapshot_from_json) | функція | `jane_storage.codec` |
| [`snapshot_to_json`](jane_storage.codec.md#функція-snapshot_to_json) | функція | `jane_storage.codec` |
| [`SourceRow`](jane_storage_postgres.news_layout.mapping.md#клас-sourcerow) | dataclass (незмінний) | `jane_storage_postgres.news_layout.mapping` |
| [`SqlServerAdapter`](jane_storage_sqlserver.md#клас-sqlserveradapter) | клас | `jane_storage_sqlserver` |
| [`StorageEngine`](jane_storage.engine.md#клас-storageengine) | клас | `jane_storage.engine` |
| [`StorageHandler`](jane_storage.handler.md#клас-storagehandler) | клас | `jane_storage.handler` |
| [`StoragePackage`](jane_storage.packages.md#клас-storagepackage) | dataclass (незмінний) | `jane_storage.packages` |
| [`stored_object_ref`](jane_storage.engine.md#функція-stored_object_ref) | функція | `jane_storage.engine` |
| [`StoredConnection`](jane_storage.connections.md#клас-storedconnection) | dataclass (незмінний) | `jane_storage.connections` |
| [`Timeouts`](jane_storage.settings.md#клас-timeouts) | клас | `jane_storage.settings` |
| [`Transfer`](jane_storage.settings.md#клас-transfer) | клас | `jane_storage.settings` |
| [`UnknownAdapter`](jane_storage.adapters.md#клас-unknownadapter) | виняток | `jane_storage.adapters` |
| [`utcnow`](jane_storage.codec.md#функція-utcnow) | функція | `jane_storage.codec` |
| [`validate_record`](jane_storage.merge.md#функція-validate_record) | функція | `jane_storage.merge` |
| [`write_projection`](jane_storage_postgres.news_layout.md#функція-write_projection) | функція | `jane_storage_postgres.news_layout` |
