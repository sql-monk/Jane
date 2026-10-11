# Типи й члени Handler Runtime

[Повний каталог](generated/README.md) містить декларації кожного публічного символу, parameters/defaults, properties access, inheritance і code links. Ручні пояснення нижче описують поведінку, errors і приклади.

## Модулі

| Модуль | Призначення членів |
|---|---|
| [runtime](generated/jane_handler_runtime.runtime.md) | Runtime/build_runtime/build_backend складають Settings, backend, store, schemas, Executor; close прибирає store |
| [executor](generated/jane_handler_runtime.executor.md) | PreparedInvocation/Executor: validate, prepare, bundle, run, interpret, result diagnostics |
| [packages](generated/jane_handler_runtime.packages.md) | LoadedPackage, PackageStore, ContentFetcher: archive/digest/cache/ContentRef |
| [sandbox](generated/jane_handler_runtime.sandbox.md) | Bundle/SandboxOutcome/SandboxBackend/SubprocessSandbox: execution protocol і локальний backend |
| [docker_sandbox](generated/jane_handler_runtime.docker_sandbox.md) | DockerSandbox run/kill/ping і container resource policy |
| [schemas](generated/jane_handler_runtime.schemas.md) | ContractSchemas/errors і пошук contracts |
| [state](generated/jane_handler_runtime.state.md) | ResultStore/ServiceState, memory/Postgres adapters, heartbeat/results |
| [testrun](generated/jane_handler_runtime.testrun.md) | Select cases/run_tests/comparison/report зі справжнім Executor |
| [profiles](generated/jane_handler_runtime.profiles.md) | RuntimeProfile, allowed dependencies, profile loading |
| [app](generated/jane_handler_runtime.app.md) | Build_app, idempotent invoke/test/job/cancel та власний state |
| [cli](generated/jane_handler_runtime.cli.md) | Main/repo_root/build_context та command dispatch |
| [settings](generated/jane_handler_runtime.settings.md) | Settings/limit models/request_layer/resolve_service_limits/caps |
| [__main__](generated/jane_handler_runtime.__main__.md) | HTTP process entry point |

## Executor і PackageStore

Check_package повертає image для profile; unsupported kind/runtime/network → ValidationFailed, невідомий profile/library → dependency_not_allowed. Check_params і check_input перевіряють схеми до sandbox. Prepare(invocation, package=...) повертає PreparedInvocation; package аргумент дозволяє локальну інтеграцію без Registry.

Run(prep) повертає HandlerResult після container outcome. Docker недоступний → ServiceUnavailable; outcome timeout/OOM/output/violation/invalid result → HandlerResult.failed. Interpret не кидає HTTP error за помилку самого пакета. SandboxBackend.run повертає SandboxOutcome; kill повертає кількість/ознаку backend-зупинки за його декларацією, ping перевіряє engine.

PackageStore.load_local приймає directory/ZIP; invalid archive/schema → ValidationFailed, filesystem error може поширюватися. Load(handler,archive_ref) читає exact archive або Registry і перевіряє identity; wrong digest → digest_mismatch, not found → NotFound, registry failure → UpstreamUnavailable. ContentFetcher.read застосовує byte cap і ContentRef policy; root/host/digest порушення відхиляються до execution.

LoadedPackage — frozen dataclass. Root/manifest/digest/source поля не переприсвоюються; вкладений manifest залишається Python mapping. Ref — read-only property з package_id/version/digest; звертайтеся package.ref, не викликайте її як функцію.

## Lifecycle й state

Runtime.close закриває package store, не є cancel усіх HTTP job. HTTP lifespan окремо відкриває/закриває ServiceState і runner. ResultStore.put/get зберігає завершений Result; get повертає None, коли result відсутній/витіснений. InMemoryResultStore має configured maximum; PostgresState зберігає own schema і leases.

Settings Pydantic fields RW за деклараціями; validated створення застосовує type/constraint checks. Model_copy(update=...) не замінює validation для untrusted API input. Request_layer бере sandbox/timeouts, resolve_service_limits обрізає hard caps. JSON/схема input належать до prepare, container failure — до Result.

## Приклади

[Python приклад](../../integration.md#python-із-локальним-пакетом) виконує build_runtime → load_local → prepare → run → close та перевіряє status/entities. [CLI tests](../../quickstart.md#2-тести-пакета) перевіряє expected status/output кожного кейсу, а не тільки exit запуску.

Огляд профілю без Docker:

```powershell
uv run --all-packages jane-handler-runtime profile --json
```

[Configuration](../../configuration.md) дає defaults/constraints; [operations](../../operations.md) пояснює crash/replay.
