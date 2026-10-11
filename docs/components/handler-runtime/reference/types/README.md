# Типи й члени: Handler Runtime

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime](../../../../../services/handler-runtime/src/jane_handler_runtime). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_handler_runtime`](jane_handler_runtime.md) | 0 | 0 | Handler Runtime of the Jane platform. |
| [`jane_handler_runtime.__main__`](jane_handler_runtime.__main__.md) | 0 | 1 | Entry point: ``python -m jane_handler_runtime`` (host/port from ``JANE_HANDLER_RUNTIME_HOST/PORT``). |
| [`jane_handler_runtime.app`](jane_handler_runtime.app.md) | 0 | 2 | HTTP API: handler protocol ``contracts/openapi/handler.v1.yaml`` for Python extractors. |
| [`jane_handler_runtime.cli`](jane_handler_runtime.cli.md) | 0 | 1 | Command line: run a package on a local file or run its tests without any other Jane service. |
| [`jane_handler_runtime.docker_sandbox`](jane_handler_runtime.docker_sandbox.md) | 1 | 0 | Docker/Podman backend (ADR-0003): one fresh container per invocation through the Engine API. |
| [`jane_handler_runtime.executor`](jane_handler_runtime.executor.md) | 2 | 2 | Executing a ``HandlerInvocation``: prepare (package, dependencies, params, inputs, limits), run in the sandbox, turn the runner output into a ``HandlerResult``  |
| [`jane_handler_runtime.packages`](jane_handler_runtime.packages.md) | 3 | 1 | Getting a package: a local directory or zip (CLI), ``package_archive`` (ContentRef) or the registry. |
| [`jane_handler_runtime.profiles`](jane_handler_runtime.profiles.md) | 2 | 2 | Runtime profiles: which Python and libraries a sandbox image provides (``dependencies.runtime_profile``). |
| [`jane_handler_runtime.runtime`](jane_handler_runtime.runtime.md) | 1 | 2 | Wiring shared by the HTTP service and the CLI. |
| [`jane_handler_runtime.sandbox`](jane_handler_runtime.sandbox.md) | 5 | 2 | Sandbox backends (ADR-0003): ``SandboxBackend`` protocol, the workdir bundle, the ``subprocess`` backend. |
| [`jane_handler_runtime.schemas`](jane_handler_runtime.schemas.md) | 2 | 2 | JSON Schema validation against the WP-00 contracts (``contracts/schemas``) and package schemas. |
| [`jane_handler_runtime.settings`](jane_handler_runtime.settings.md) | 7 | 2 | Settings and limits of the service. Every limit has a safe default documented in README.md. |
| [`jane_handler_runtime.state`](jane_handler_runtime.state.md) | 4 | 0 | Service state shared by instances: idempotency keys, jobs and invocation results. |
| [`jane_handler_runtime.testrun`](jane_handler_runtime.testrun.md) | 0 | 2 | Package test runs without writing to working data (``POST /v1/test-runs``, CLI ``test``). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`build_app`](jane_handler_runtime.app.md#функція-build_app) | функція | `jane_handler_runtime.app` |
| [`build_backend`](jane_handler_runtime.runtime.md#функція-build_backend) | функція | `jane_handler_runtime.runtime` |
| [`build_runtime`](jane_handler_runtime.runtime.md#функція-build_runtime) | функція | `jane_handler_runtime.runtime` |
| [`build_state`](jane_handler_runtime.app.md#функція-build_state) | функція | `jane_handler_runtime.app` |
| [`Bundle`](jane_handler_runtime.sandbox.md#клас-bundle) | dataclass | `jane_handler_runtime.sandbox` |
| [`check_dependencies`](jane_handler_runtime.profiles.md#функція-check_dependencies) | функція | `jane_handler_runtime.profiles` |
| [`ConcurrencyLimits`](jane_handler_runtime.settings.md#клас-concurrencylimits) | клас | `jane_handler_runtime.settings` |
| [`ContentFetcher`](jane_handler_runtime.packages.md#клас-contentfetcher) | клас | `jane_handler_runtime.packages` |
| [`ContractSchemas`](jane_handler_runtime.schemas.md#клас-contractschemas) | клас | `jane_handler_runtime.schemas` |
| [`DependencyProblem`](jane_handler_runtime.profiles.md#клас-dependencyproblem) | dataclass (незмінний) | `jane_handler_runtime.profiles` |
| [`digest_mismatch`](jane_handler_runtime.packages.md#функція-digest_mismatch) | функція | `jane_handler_runtime.packages` |
| [`DockerSandbox`](jane_handler_runtime.docker_sandbox.md#клас-dockersandbox) | клас | `jane_handler_runtime.docker_sandbox` |
| [`Executor`](jane_handler_runtime.executor.md#клас-executor) | клас | `jane_handler_runtime.executor` |
| [`find_contracts_dir`](jane_handler_runtime.schemas.md#функція-find_contracts_dir) | функція | `jane_handler_runtime.schemas` |
| [`InMemoryState`](jane_handler_runtime.state.md#клас-inmemorystate) | клас | `jane_handler_runtime.state` |
| [`killed_by_sigkill`](jane_handler_runtime.sandbox.md#функція-killed_by_sigkill) | функція | `jane_handler_runtime.sandbox` |
| [`load_profiles`](jane_handler_runtime.profiles.md#функція-load_profiles) | функція | `jane_handler_runtime.profiles` |
| [`LoadedPackage`](jane_handler_runtime.packages.md#клас-loadedpackage) | dataclass (незмінний) | `jane_handler_runtime.packages` |
| [`main`](jane_handler_runtime.__main__.md#функція-main) | функція | `jane_handler_runtime.__main__` |
| [`main`](jane_handler_runtime.cli.md#функція-main) | функція | `jane_handler_runtime.cli` |
| [`new_invocation_id`](jane_handler_runtime.executor.md#функція-new_invocation_id) | функція | `jane_handler_runtime.executor` |
| [`now_rfc3339`](jane_handler_runtime.executor.md#функція-now_rfc3339) | функція | `jane_handler_runtime.executor` |
| [`PackageLimits`](jane_handler_runtime.settings.md#клас-packagelimits) | клас | `jane_handler_runtime.settings` |
| [`PackageStore`](jane_handler_runtime.packages.md#клас-packagestore) | клас | `jane_handler_runtime.packages` |
| [`PostgresState`](jane_handler_runtime.state.md#клас-postgresstate) | клас | `jane_handler_runtime.state` |
| [`PreparedInvocation`](jane_handler_runtime.executor.md#клас-preparedinvocation) | dataclass | `jane_handler_runtime.executor` |
| [`read_limited`](jane_handler_runtime.sandbox.md#функція-read_limited) | функція | `jane_handler_runtime.sandbox` |
| [`request_layer`](jane_handler_runtime.settings.md#функція-request_layer) | функція | `jane_handler_runtime.settings` |
| [`resolve_service_limits`](jane_handler_runtime.settings.md#функція-resolve_service_limits) | функція | `jane_handler_runtime.settings` |
| [`ResultStore`](jane_handler_runtime.state.md#клас-resultstore) | протокол | `jane_handler_runtime.state` |
| [`run_tests`](jane_handler_runtime.testrun.md#функція-run_tests) | функція | `jane_handler_runtime.testrun` |
| [`Runtime`](jane_handler_runtime.runtime.md#клас-runtime) | dataclass | `jane_handler_runtime.runtime` |
| [`RuntimeProfile`](jane_handler_runtime.profiles.md#клас-runtimeprofile) | dataclass (незмінний) | `jane_handler_runtime.profiles` |
| [`SandboxBackend`](jane_handler_runtime.sandbox.md#клас-sandboxbackend) | протокол | `jane_handler_runtime.sandbox` |
| [`SandboxLimits`](jane_handler_runtime.settings.md#клас-sandboxlimits) | клас | `jane_handler_runtime.settings` |
| [`SandboxOutcome`](jane_handler_runtime.sandbox.md#клас-sandboxoutcome) | dataclass | `jane_handler_runtime.sandbox` |
| [`SandboxUnavailable`](jane_handler_runtime.sandbox.md#клас-sandboxunavailable) | виняток | `jane_handler_runtime.sandbox` |
| [`SchemaError`](jane_handler_runtime.schemas.md#клас-schemaerror) | клас | `jane_handler_runtime.schemas` |
| [`select_cases`](jane_handler_runtime.testrun.md#функція-select_cases) | функція | `jane_handler_runtime.testrun` |
| [`ServiceLimits`](jane_handler_runtime.settings.md#клас-servicelimits) | клас | `jane_handler_runtime.settings` |
| [`ServiceState`](jane_handler_runtime.state.md#клас-servicestate) | протокол | `jane_handler_runtime.state` |
| [`Settings`](jane_handler_runtime.settings.md#клас-settings) | модель Pydantic | `jane_handler_runtime.settings` |
| [`StateLimits`](jane_handler_runtime.settings.md#клас-statelimits) | клас | `jane_handler_runtime.settings` |
| [`SubprocessSandbox`](jane_handler_runtime.sandbox.md#клас-subprocesssandbox) | клас | `jane_handler_runtime.sandbox` |
| [`TimeoutLimits`](jane_handler_runtime.settings.md#клас-timeoutlimits) | клас | `jane_handler_runtime.settings` |
| [`validate_instance`](jane_handler_runtime.schemas.md#функція-validate_instance) | функція | `jane_handler_runtime.schemas` |
