# Типи й члени: jane-kit

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit](../../../../../libs/jane-kit/src/jane_kit). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_kit`](jane_kit.md) | 0 | 0 | jane-kit: shared building blocks for Jane services. |
| [`jane_kit.auth`](jane_kit.auth.md) | 7 | 9 | Authentication and scopes of Jane services (ADR-0005), one implementation for every service. |
| [`jane_kit.auth_scopes`](jane_kit.auth_scopes.md) | 0 | 1 | Scopes of every operation of Jane's contracts (ADR-0005 §3), one table per API. |
| [`jane_kit.clients`](jane_kit.clients.md) | 4 | 0 | HTTP client base for calling other Jane services (and base class of generated clients). |
| [`jane_kit.codegen`](jane_kit.codegen.md) | 0 | 4 | Generate typed clients from OpenAPI contracts. |
| [`jane_kit.config`](jane_kit.config.md) | 5 | 4 | Service settings and limits inherited across levels: platform -> source -> task -> stage (-> request). |
| [`jane_kit.content`](jane_kit.content.md) | 4 | 2 | Reading ``ContentRef`` values (ADR-0004) under an explicit operator policy. |
| [`jane_kit.contracts`](jane_kit.contracts.md) | 5 | 4 | Contract helpers over the OpenAPI 3.1 documents in ``contracts/openapi/`` (WP-00). |
| [`jane_kit.devstack`](jane_kit.devstack.md) | 1 | 5 | Access to the local dev stack started by ``just up`` (for integration tests). |
| [`jane_kit.errors`](jane_kit.errors.md) | 14 | 2 | Error model: RFC 9457 Problem Details (``application/problem+json``) per WP-00 contract. |
| [`jane_kit.health`](jane_kit.health.md) | 4 | 1 | ``GET /v1/health`` and ``GET /v1/info`` per WP-00 ``common.yaml`` (pathItems Health, Info). |
| [`jane_kit.idempotency`](jane_kit.idempotency.md) | 7 | 3 | Idempotent request handling by ``Idempotency-Key`` (TZ §11: a repeated technical delivery is a duplicate). |
| [`jane_kit.jobs`](jane_kit.jobs.md) | 11 | 5 | Long-running operations per WP-00 ``schemas/common/job.schema.json`` and ``common.yaml`` pathItems. |
| [`jane_kit.logs`](jane_kit.logs.md) | 1 | 4 | Structured logging: one JSON object per line on stdout, with bound context. |
| [`jane_kit.metrics`](jane_kit.metrics.md) | 1 | 1 | Prometheus metrics with a per-application registry (no global state between app instances). |
| [`jane_kit.pagination`](jane_kit.pagination.md) | 2 | 3 | Cursor pagination per WP-00 conventions: ``?limit=&cursor=`` -> ``{"items": [...], "next_cursor": ... \| null}``. |
| [`jane_kit.rules`](jane_kit.rules.md) | 3 | 1 | Collector rules: schema validation and loading by ``rules_ref`` (shared by the collectors, R17). |
| [`jane_kit.schemas`](jane_kit.schemas.md) | 2 | 1 | Validation against the JSON Schemas of the contracts (``contracts/schemas``, WP-00) - R17. |
| [`jane_kit.secrets`](jane_kit.secrets.md) | 3 | 2 | Secret references of managed connections and allowlists of their destinations (ADR-0006, R17). |
| [`jane_kit.service`](jane_kit.service.md) | 0 | 2 | FastAPI application factory with the standard Jane wiring. |
| [`jane_kit.stores`](jane_kit.stores.md) | 2 | 1 | Shared ``IdempotencyStore`` / ``JobStore`` implementations on a service's own database (R17). |
| [`jane_kit.stores.postgres`](jane_kit.stores.postgres.md) | 3 | 2 | ``IdempotencyStore`` and ``JobStore`` in a service's own PostgreSQL database (R17). |
| [`jane_kit.stores.sqlite`](jane_kit.stores.sqlite.md) | 6 | 0 | ``IdempotencyStore`` and ``JobStore`` in a service's own SQLite state file (R17). |
| [`jane_kit.tracing`](jane_kit.tracing.md) | 0 | 3 | W3C Trace Context (``traceparent``): continue the caller's trace, pass it on (skill jane-contracts §11). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`accepted`](jane_kit.jobs.md#функція-accepted) | функція | `jane_kit.jobs` |
| [`api_key_var`](jane_kit.devstack.md#функція-api_key_var) | функція | `jane_kit.devstack` |
| [`ApiKeyConfig`](jane_kit.auth.md#клас-apikeyconfig) | модель Pydantic | `jane_kit.auth` |
| [`AuthConfigError`](jane_kit.auth.md#клас-authconfigerror) | виняток | `jane_kit.auth` |
| [`Authenticator`](jane_kit.auth.md#клас-authenticator) | клас | `jane_kit.auth` |
| [`authorize`](jane_kit.auth.md#функція-authorize) | функція | `jane_kit.auth` |
| [`AuthSettings`](jane_kit.auth.md#клас-authsettings) | модель Pydantic | `jane_kit.auth` |
| [`BadRequest`](jane_kit.errors.md#клас-badrequest) | виняток | `jane_kit.errors` |
| [`bearer_header`](jane_kit.auth.md#функція-bearer_header) | функція | `jane_kit.auth` |
| [`bind_context`](jane_kit.logs.md#функція-bind_context) | функція | `jane_kit.logs` |
| [`build_mock_app`](jane_kit.contracts.md#функція-build_mock_app) | функція | `jane_kit.contracts` |
| [`check_scopes`](jane_kit.auth.md#функція-check_scopes) | функція | `jane_kit.auth` |
| [`CheckResult`](jane_kit.health.md#клас-checkresult) | модель Pydantic | `jane_kit.health` |
| [`child_traceparent`](jane_kit.tracing.md#функція-child_traceparent) | функція | `jane_kit.tracing` |
| [`ClaimLimits`](jane_kit.stores.md#клас-claimlimits) | клас | `jane_kit.stores` |
| [`clamp_limit`](jane_kit.pagination.md#функція-clamp_limit) | функція | `jane_kit.pagination` |
| [`ClientLimits`](jane_kit.clients.md#клас-clientlimits) | клас | `jane_kit.clients` |
| [`CollectorSchemas`](jane_kit.rules.md#клас-collectorschemas) | клас | `jane_kit.rules` |
| [`configure_logging`](jane_kit.logs.md#функція-configure_logging) | функція | `jane_kit.logs` |
| [`Conflict`](jane_kit.errors.md#клас-conflict) | виняток | `jane_kit.errors` |
| [`ContentReader`](jane_kit.content.md#клас-contentreader) | клас | `jane_kit.content` |
| [`ContentTooLarge`](jane_kit.content.md#клас-contenttoolarge) | клас | `jane_kit.content` |
| [`ContentWriter`](jane_kit.content.md#клас-contentwriter) | dataclass | `jane_kit.content` |
| [`contract_field`](jane_kit.config.md#функція-contract_field) | функція | `jane_kit.config` |
| [`ContractClient`](jane_kit.contracts.md#клас-contractclient) | клас | `jane_kit.contracts` |
| [`contracts_dir`](jane_kit.contracts.md#функція-contracts_dir) | функція | `jane_kit.contracts` |
| [`ContractSchemas`](jane_kit.schemas.md#клас-contractschemas) | клас | `jane_kit.schemas` |
| [`ContractsNotFound`](jane_kit.schemas.md#клас-contractsnotfound) | виняток | `jane_kit.schemas` |
| [`ContractViolation`](jane_kit.contracts.md#клас-contractviolation) | виняток | `jane_kit.contracts` |
| [`create_app`](jane_kit.service.md#функція-create_app) | функція | `jane_kit.service` |
| [`current_context`](jane_kit.logs.md#функція-current_context) | функція | `jane_kit.logs` |
| [`decide_save`](jane_kit.jobs.md#функція-decide_save) | функція | `jane_kit.jobs` |
| [`decode_cursor`](jane_kit.pagination.md#функція-decode_cursor) | функція | `jane_kit.pagination` |
| [`default_project`](jane_kit.devstack.md#функція-default_project) | функція | `jane_kit.devstack` |
| [`encode_cursor`](jane_kit.pagination.md#функція-encode_cursor) | функція | `jane_kit.pagination` |
| [`example_from_schema`](jane_kit.contracts.md#функція-example_from_schema) | функція | `jane_kit.contracts` |
| [`FieldError`](jane_kit.errors.md#клас-fielderror) | модель Pydantic | `jane_kit.errors` |
| [`FileTransitStore`](jane_kit.content.md#клас-filetransitstore) | клас | `jane_kit.content` |
| [`find_repo_root`](jane_kit.devstack.md#функція-find_repo_root) | функція | `jane_kit.devstack` |
| [`find_specs`](jane_kit.contracts.md#функція-find_specs) | функція | `jane_kit.contracts` |
| [`fingerprint`](jane_kit.idempotency.md#функція-fingerprint) | функція | `jane_kit.idempotency` |
| [`Forbidden`](jane_kit.errors.md#клас-forbidden) | виняток | `jane_kit.errors` |
| [`generate_client`](jane_kit.codegen.md#функція-generate_client) | функція | `jane_kit.codegen` |
| [`generate_client_source`](jane_kit.codegen.md#функція-generate_client_source) | функція | `jane_kit.codegen` |
| [`generate_models`](jane_kit.codegen.md#функція-generate_models) | функція | `jane_kit.codegen` |
| [`get_logger`](jane_kit.logs.md#функція-get_logger) | функція | `jane_kit.logs` |
| [`header_value_safe`](jane_kit.rules.md#функція-header_value_safe) | функція | `jane_kit.rules` |
| [`HealthRegistry`](jane_kit.health.md#клас-healthregistry) | клас | `jane_kit.health` |
| [`HealthReport`](jane_kit.health.md#клас-healthreport) | модель Pydantic | `jane_kit.health` |
| [`heartbeat_loop`](jane_kit.stores.md#функція-heartbeat_loop) | функція | `jane_kit.stores` |
| [`HostAllowlist`](jane_kit.secrets.md#клас-hostallowlist) | dataclass (незмінний) | `jane_kit.secrets` |
| [`IdempotencyInProgress`](jane_kit.idempotency.md#клас-idempotencyinprogress) | виняток | `jane_kit.idempotency` |
| [`IdempotencyKeyReused`](jane_kit.idempotency.md#клас-idempotencykeyreused) | виняток | `jane_kit.idempotency` |
| [`IdempotencyLimits`](jane_kit.idempotency.md#клас-idempotencylimits) | клас | `jane_kit.idempotency` |
| [`IdempotencyRecord`](jane_kit.idempotency.md#клас-idempotencyrecord) | dataclass | `jane_kit.idempotency` |
| [`IdempotencyStore`](jane_kit.idempotency.md#клас-idempotencystore) | протокол | `jane_kit.idempotency` |
| [`idempotent`](jane_kit.idempotency.md#функція-idempotent) | функція | `jane_kit.idempotency` |
| [`inline_ref`](jane_kit.content.md#функція-inline_ref) | функція | `jane_kit.content` |
| [`InMemoryIdempotencyStore`](jane_kit.idempotency.md#клас-inmemoryidempotencystore) | клас | `jane_kit.idempotency` |
| [`InMemoryJobStore`](jane_kit.jobs.md#клас-inmemoryjobstore) | клас | `jane_kit.jobs` |
| [`install_auth`](jane_kit.auth.md#функція-install_auth) | функція | `jane_kit.auth` |
| [`install_error_handlers`](jane_kit.errors.md#функція-install_error_handlers) | функція | `jane_kit.errors` |
| [`install_health`](jane_kit.health.md#функція-install_health) | функція | `jane_kit.health` |
| [`install_metrics`](jane_kit.metrics.md#функція-install_metrics) | функція | `jane_kit.metrics` |
| [`JaneError`](jane_kit.errors.md#клас-janeerror) | виняток | `jane_kit.errors` |
| [`JaneSettings`](jane_kit.config.md#клас-janesettings) | модель Pydantic | `jane_kit.config` |
| [`Job`](jane_kit.jobs.md#клас-job) | клас | `jane_kit.jobs` |
| [`JobCancellation`](jane_kit.jobs.md#клас-jobcancellation) | клас | `jane_kit.jobs` |
| [`JobCancelledError`](jane_kit.jobs.md#клас-jobcancellederror) | виняток | `jane_kit.jobs` |
| [`JobCancelRequest`](jane_kit.jobs.md#клас-jobcancelrequest) | модель Pydantic | `jane_kit.jobs` |
| [`JobContext`](jane_kit.jobs.md#клас-jobcontext) | клас | `jane_kit.jobs` |
| [`JobLimits`](jane_kit.jobs.md#клас-joblimits) | клас | `jane_kit.jobs` |
| [`JobProgress`](jane_kit.jobs.md#клас-jobprogress) | клас | `jane_kit.jobs` |
| [`JobRunner`](jane_kit.jobs.md#клас-jobrunner) | клас | `jane_kit.jobs` |
| [`jobs_router`](jane_kit.jobs.md#функція-jobs_router) | функція | `jane_kit.jobs` |
| [`JobStatus`](jane_kit.jobs.md#клас-jobstatus) | перелік | `jane_kit.jobs` |
| [`JobStore`](jane_kit.jobs.md#клас-jobstore) | протокол | `jane_kit.jobs` |
| [`json_pointer`](jane_kit.schemas.md#функція-json_pointer) | функція | `jane_kit.schemas` |
| [`JsonFormatter`](jane_kit.logs.md#клас-jsonformatter) | клас | `jane_kit.logs` |
| [`JwksCache`](jane_kit.auth.md#клас-jwkscache) | клас | `jane_kit.auth` |
| [`layer_from_env`](jane_kit.config.md#функція-layer_from_env) | функція | `jane_kit.config` |
| [`LeaseLimits`](jane_kit.stores.md#клас-leaselimits) | клас | `jane_kit.stores` |
| [`LimitError`](jane_kit.config.md#клас-limiterror) | виняток | `jane_kit.config` |
| [`LimitExceeded`](jane_kit.errors.md#клас-limitexceeded) | виняток | `jane_kit.errors` |
| [`LimitLayer`](jane_kit.config.md#клас-limitlayer) | dataclass (незмінний) | `jane_kit.config` |
| [`Limits`](jane_kit.config.md#клас-limits) | модель Pydantic | `jane_kit.config` |
| [`load_layer`](jane_kit.config.md#функція-load_layer) | функція | `jane_kit.config` |
| [`load_stack`](jane_kit.devstack.md#функція-load_stack) | функція | `jane_kit.devstack` |
| [`Loc`](jane_kit.contracts.md#клас-loc) | dataclass (незмінний) | `jane_kit.contracts` |
| [`main`](jane_kit.codegen.md#функція-main) | функція | `jane_kit.codegen` |
| [`merge`](jane_kit.auth_scopes.md#функція-merge) | функція | `jane_kit.auth_scopes` |
| [`Metrics`](jane_kit.metrics.md#клас-metrics) | клас | `jane_kit.metrics` |
| [`migrate`](jane_kit.stores.postgres.md#функція-migrate) | функція | `jane_kit.stores.postgres` |
| [`new_api_keys`](jane_kit.devstack.md#функція-new_api_keys) | функція | `jane_kit.devstack` |
| [`new_trace_id`](jane_kit.tracing.md#функція-new_trace_id) | функція | `jane_kit.tracing` |
| [`NotFound`](jane_kit.errors.md#клас-notfound) | виняток | `jane_kit.errors` |
| [`OpenAPISpec`](jane_kit.contracts.md#клас-openapispec) | клас | `jane_kit.contracts` |
| [`Operation`](jane_kit.contracts.md#клас-operation) | dataclass (незмінний) | `jane_kit.contracts` |
| [`OriginAllowlist`](jane_kit.secrets.md#клас-originallowlist) | dataclass (незмінний) | `jane_kit.secrets` |
| [`orphaned`](jane_kit.jobs.md#функція-orphaned) | функція | `jane_kit.jobs` |
| [`Page`](jane_kit.pagination.md#клас-page) | модель Pydantic | `jane_kit.pagination` |
| [`PageLimits`](jane_kit.pagination.md#клас-pagelimits) | клас | `jane_kit.pagination` |
| [`parse_host_allowlist`](jane_kit.content.md#функція-parse_host_allowlist) | функція | `jane_kit.content` |
| [`parse_host_port`](jane_kit.secrets.md#функція-parse_host_port) | функція | `jane_kit.secrets` |
| [`parse_traceparent`](jane_kit.tracing.md#функція-parse_traceparent) | функція | `jane_kit.tracing` |
| [`PgDatabase`](jane_kit.stores.postgres.md#клас-pgdatabase) | клас | `jane_kit.stores.postgres` |
| [`PgIdempotencyStore`](jane_kit.stores.postgres.md#клас-pgidempotencystore) | клас | `jane_kit.stores.postgres` |
| [`PgJobStore`](jane_kit.stores.postgres.md#клас-pgjobstore) | клас | `jane_kit.stores.postgres` |
| [`pool_tx`](jane_kit.stores.postgres.md#функція-pool_tx) | функція | `jane_kit.stores.postgres` |
| [`Principal`](jane_kit.auth.md#клас-principal) | dataclass (незмінний) | `jane_kit.auth` |
| [`principal_of`](jane_kit.auth.md#функція-principal_of) | функція | `jane_kit.auth` |
| [`Problem`](jane_kit.errors.md#клас-problem) | модель Pydantic | `jane_kit.errors` |
| [`problem_response`](jane_kit.errors.md#функція-problem_response) | функція | `jane_kit.errors` |
| [`RateLimited`](jane_kit.errors.md#клас-ratelimited) | виняток | `jane_kit.errors` |
| [`read_secret_file`](jane_kit.secrets.md#функція-read_secret_file) | функція | `jane_kit.secrets` |
| [`RemoteError`](jane_kit.clients.md#клас-remoteerror) | виняток | `jane_kit.clients` |
| [`require`](jane_kit.auth.md#функція-require) | функція | `jane_kit.auth` |
| [`resolve_limits`](jane_kit.config.md#функція-resolve_limits) | функція | `jane_kit.config` |
| [`resolve_secret_ref`](jane_kit.auth.md#функція-resolve_secret_ref) | функція | `jane_kit.auth` |
| [`ResolvedLimits`](jane_kit.config.md#клас-resolvedlimits) | dataclass (незмінний) | `jane_kit.config` |
| [`resumed`](jane_kit.jobs.md#функція-resumed) | функція | `jane_kit.jobs` |
| [`RetryPolicy`](jane_kit.clients.md#клас-retrypolicy) | клас | `jane_kit.clients` |
| [`RulesLoader`](jane_kit.rules.md#клас-rulesloader) | клас | `jane_kit.rules` |
| [`RulesReport`](jane_kit.rules.md#клас-rulesreport) | dataclass | `jane_kit.rules` |
| [`run`](jane_kit.service.md#функція-run) | функція | `jane_kit.service` |
| [`run_idempotent`](jane_kit.idempotency.md#функція-run_idempotent) | функція | `jane_kit.idempotency` |
| [`SecretPolicy`](jane_kit.secrets.md#клас-secretpolicy) | dataclass (незмінний) | `jane_kit.secrets` |
| [`SecretRefError`](jane_kit.auth.md#клас-secretreferror) | виняток | `jane_kit.auth` |
| [`ServiceClient`](jane_kit.clients.md#клас-serviceclient) | клас | `jane_kit.clients` |
| [`ServiceInfo`](jane_kit.health.md#клас-serviceinfo) | модель Pydantic | `jane_kit.health` |
| [`ServiceUnavailable`](jane_kit.errors.md#клас-serviceunavailable) | виняток | `jane_kit.errors` |
| [`sha256_hex`](jane_kit.auth.md#функція-sha256_hex) | функція | `jane_kit.auth` |
| [`SqliteDatabase`](jane_kit.stores.sqlite.md#клас-sqlitedatabase) | клас | `jane_kit.stores.sqlite` |
| [`SqliteIdempotencyStore`](jane_kit.stores.sqlite.md#клас-sqliteidempotencystore) | клас | `jane_kit.stores.sqlite` |
| [`SqliteJobStore`](jane_kit.stores.sqlite.md#клас-sqlitejobstore) | клас | `jane_kit.stores.sqlite` |
| [`SqliteTx`](jane_kit.stores.sqlite.md#клас-sqlitetx) | протокол | `jane_kit.stores.sqlite` |
| [`SqliteWorkJobStore`](jane_kit.stores.sqlite.md#клас-sqliteworkjobstore) | клас | `jane_kit.stores.sqlite` |
| [`StackInfo`](jane_kit.devstack.md#клас-stackinfo) | dataclass (незмінний) | `jane_kit.devstack` |
| [`StoredResponse`](jane_kit.idempotency.md#клас-storedresponse) | dataclass (незмінний) | `jane_kit.idempotency` |
| [`Timeout`](jane_kit.errors.md#клас-timeout) | виняток | `jane_kit.errors` |
| [`Unauthenticated`](jane_kit.errors.md#клас-unauthenticated) | виняток | `jane_kit.errors` |
| [`unmapped_routes`](jane_kit.auth.md#функція-unmapped_routes) | функція | `jane_kit.auth` |
| [`UpstreamUnavailable`](jane_kit.errors.md#клас-upstreamunavailable) | виняток | `jane_kit.errors` |
| [`ValidationFailed`](jane_kit.errors.md#клас-validationfailed) | виняток | `jane_kit.errors` |
| [`WorkRows`](jane_kit.stores.sqlite.md#клас-workrows) | протокол | `jane_kit.stores.sqlite` |
