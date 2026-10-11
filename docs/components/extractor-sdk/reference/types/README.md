# Типи й члени: jane-extractor-sdk

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk](../../../../../libs/extractor-sdk/src/jane_extractor_sdk). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_extractor_sdk`](jane_extractor_sdk.md) | 0 | 0 | SDK for Jane Python extractors. |
| [`jane_extractor_sdk.compare`](jane_extractor_sdk.compare.md) | 0 | 2 | Comparison of an expected test output with the actual one (``TestCase.compare``: ``exact`` \| ``subset``). |
| [`jane_extractor_sdk.context`](jane_extractor_sdk.context.md) | 2 | 0 | Execution context passed to the extractor callable as ``ctx``. |
| [`jane_extractor_sdk.entities`](jane_extractor_sdk.entities.md) | 0 | 3 | Turning extractor entities into ``EntityRecord`` documents (shared by the runtime and local test runs). |
| [`jane_extractor_sdk.package`](jane_extractor_sdk.package.md) | 2 | 9 | Package utilities: manifest, canonical archive and digest, safe unpacking, test-case inputs. |
| [`jane_extractor_sdk.result`](jane_extractor_sdk.result.md) | 0 | 4 | Helpers that build :class:`~jane_extractor_sdk.types.ExtractResult` values (the four states of TZ §9). |
| [`jane_extractor_sdk.runner`](jane_extractor_sdk.runner.md) | 0 | 2 | In-sandbox runner: ``python -I -m jane_extractor_sdk.runner <workdir>``. |
| [`jane_extractor_sdk.testing`](jane_extractor_sdk.testing.md) | 1 | 4 | Test utilities for extractor authors: run a package in-process, without the sandbox and without services. |
| [`jane_extractor_sdk.types`](jane_extractor_sdk.types.md) | 5 | 0 | Types of the extractor protocol (what the ``entry.callable`` of a package receives and returns). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`apply_param_defaults`](jane_extractor_sdk.testing.md#функція-apply_param_defaults) | функція | `jane_extractor_sdk.testing` |
| [`assert_package_tests_pass`](jane_extractor_sdk.testing.md#функція-assert_package_tests_pass) | функція | `jane_extractor_sdk.testing` |
| [`build_archive`](jane_extractor_sdk.package.md#функція-build_archive) | функція | `jane_extractor_sdk.package` |
| [`build_key`](jane_extractor_sdk.entities.md#функція-build_key) | функція | `jane_extractor_sdk.entities` |
| [`case_input`](jane_extractor_sdk.package.md#функція-case_input) | функція | `jane_extractor_sdk.package` |
| [`compare_output`](jane_extractor_sdk.compare.md#функція-compare_output) | функція | `jane_extractor_sdk.compare` |
| [`Context`](jane_extractor_sdk.context.md#клас-context) | клас | `jane_extractor_sdk.context` |
| [`Diagnostic`](jane_extractor_sdk.types.md#клас-diagnostic) | TypedDict | `jane_extractor_sdk.types` |
| [`DiagnosticsLog`](jane_extractor_sdk.context.md#клас-diagnosticslog) | клас | `jane_extractor_sdk.context` |
| [`digest_of`](jane_extractor_sdk.package.md#функція-digest_of) | функція | `jane_extractor_sdk.package` |
| [`empty`](jane_extractor_sdk.result.md#функція-empty) | функція | `jane_extractor_sdk.result` |
| [`entity`](jane_extractor_sdk.result.md#функція-entity) | функція | `jane_extractor_sdk.result` |
| [`EntityKey`](jane_extractor_sdk.types.md#клас-entitykey) | TypedDict | `jane_extractor_sdk.types` |
| [`EntityOut`](jane_extractor_sdk.types.md#клас-entityout) | TypedDict | `jane_extractor_sdk.types` |
| [`execute`](jane_extractor_sdk.runner.md#функція-execute) | функція | `jane_extractor_sdk.runner` |
| [`ExtractResult`](jane_extractor_sdk.types.md#клас-extractresult) | TypedDict | `jane_extractor_sdk.types` |
| [`iter_package_files`](jane_extractor_sdk.package.md#функція-iter_package_files) | функція | `jane_extractor_sdk.package` |
| [`load_manifest`](jane_extractor_sdk.package.md#функція-load_manifest) | функція | `jane_extractor_sdk.package` |
| [`LocalCaseResult`](jane_extractor_sdk.testing.md#клас-localcaseresult) | dataclass | `jane_extractor_sdk.testing` |
| [`main`](jane_extractor_sdk.runner.md#функція-main) | функція | `jane_extractor_sdk.runner` |
| [`material_from_bytes`](jane_extractor_sdk.package.md#функція-material_from_bytes) | функція | `jane_extractor_sdk.package` |
| [`material_from_file`](jane_extractor_sdk.package.md#функція-material_from_file) | функція | `jane_extractor_sdk.package` |
| [`observation_of`](jane_extractor_sdk.entities.md#функція-observation_of) | функція | `jane_extractor_sdk.entities` |
| [`PackageError`](jane_extractor_sdk.package.md#клас-packageerror) | виняток | `jane_extractor_sdk.package` |
| [`read_package_file`](jane_extractor_sdk.package.md#функція-read_package_file) | функція | `jane_extractor_sdk.package` |
| [`run_local`](jane_extractor_sdk.testing.md#функція-run_local) | функція | `jane_extractor_sdk.testing` |
| [`run_package_tests`](jane_extractor_sdk.testing.md#функція-run_package_tests) | функція | `jane_extractor_sdk.testing` |
| [`safe_unpack`](jane_extractor_sdk.package.md#функція-safe_unpack) | функція | `jane_extractor_sdk.package` |
| [`strip_runtime_metadata`](jane_extractor_sdk.compare.md#функція-strip_runtime_metadata) | функція | `jane_extractor_sdk.compare` |
| [`success`](jane_extractor_sdk.result.md#функція-success) | функція | `jane_extractor_sdk.result` |
| [`to_entity_record`](jane_extractor_sdk.entities.md#функція-to_entity_record) | функція | `jane_extractor_sdk.entities` |
| [`UnpackLimits`](jane_extractor_sdk.package.md#клас-unpacklimits) | dataclass (незмінний) | `jane_extractor_sdk.package` |
| [`unrecognized`](jane_extractor_sdk.result.md#функція-unrecognized) | функція | `jane_extractor_sdk.result` |
| [`Unrecognized`](jane_extractor_sdk.types.md#клас-unrecognized) | TypedDict | `jane_extractor_sdk.types` |
