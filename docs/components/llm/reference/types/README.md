# Типи й члени: LLM gateway

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm](../../../../../services/llm/src/jane_llm). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_llm`](jane_llm.md) | 0 | 0 | Llm of the Jane platform. |
| [`jane_llm.__main__`](jane_llm.__main__.md) | 0 | 1 | Entry point: ``python -m jane_llm`` (host/port from ``JANE_LLM_HOST/PORT``). |
| [`jane_llm.app`](jane_llm.app.md) | 0 | 4 | HTTP API of the LLM service: ``llm.v1`` (gateway) + ``handler.v1`` (LLM handler). |
| [`jane_llm.connections`](jane_llm.connections.md) | 1 | 3 | Managed connections: secret reference policy and resolution, secret-like value detection (ADR-0006). |
| [`jane_llm.gateway`](jane_llm.gateway.md) | 4 | 3 | LLM gateway core: model resolution, prompt assembly, budgets and rates, provider call, schema validation. |
| [`jane_llm.handler`](jane_llm.handler.md) | 2 | 1 | LLM handler (``handler.v1``): executes ``kind: llm`` packages through the gateway. |
| [`jane_llm.models`](jane_llm.models.md) | 12 | 0 | Pydantic models of ``contracts/openapi/llm.v1.yaml`` and the shared ``Connection`` schema. |
| [`jane_llm.packages`](jane_llm.packages.md) | 3 | 8 | LLM packages (``kind: llm``): loading from an archive, the registry or a local directory. |
| [`jane_llm.prompt`](jane_llm.prompt.md) | 2 | 5 | Prompt assembly with a strict split between trusted instructions and untrusted data (TZ §11). |
| [`jane_llm.providers`](jane_llm.providers.md) | 0 | 0 | LLM provider adapters by ``Provider.kind``. |
| [`jane_llm.providers.anthropic`](jane_llm.providers.anthropic.md) | 1 | 1 | Anthropic Messages API adapter (``POST {api_base}/v1/messages`` over httpx). |
| [`jane_llm.providers.base`](jane_llm.providers.base.md) | 5 | 0 | Provider adapter interface. Adapters receive fully rendered prompts and resolved connections. |
| [`jane_llm.providers.fake`](jane_llm.providers.fake.md) | 1 | 3 | Deterministic fake provider ``fake`` for tests (this and other WPs). |
| [`jane_llm.settings`](jane_llm.settings.md) | 8 | 1 | Settings and limits of the LLM service. Every limit has a safe default documented in README.md. |
| [`jane_llm.store`](jane_llm.store.md) | 11 | 1 | Persistent state of the LLM service. |
| [`jane_llm.testing`](jane_llm.testing.md) | 0 | 2 | ``POST /v1/test-runs``: package tests without writing to working data (always ``test_mode``). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`AnthropicProvider`](jane_llm.providers.anthropic.md#клас-anthropicprovider) | клас | `jane_llm.providers.anthropic` |
| [`api_schema`](jane_llm.providers.anthropic.md#функція-api_schema) | функція | `jane_llm.providers.anthropic` |
| [`Budget`](jane_llm.models.md#клас-budget) | клас | `jane_llm.models` |
| [`budget_key`](jane_llm.gateway.md#функція-budget_key) | функція | `jane_llm.gateway` |
| [`BudgetCheck`](jane_llm.store.md#клас-budgetcheck) | dataclass (незмінний) | `jane_llm.store` |
| [`BudgetDefinition`](jane_llm.models.md#клас-budgetdefinition) | клас | `jane_llm.models` |
| [`BudgetExceeded`](jane_llm.store.md#клас-budgetexceeded) | виняток | `jane_llm.store` |
| [`BudgetExhausted`](jane_llm.gateway.md#клас-budgetexhausted) | виняток | `jane_llm.gateway` |
| [`build_app`](jane_llm.app.md#функція-build_app) | функція | `jane_llm.app` |
| [`build_archive`](jane_llm.packages.md#функція-build_archive) | функція | `jane_llm.packages` |
| [`build_prompt`](jane_llm.prompt.md#функція-build_prompt) | функція | `jane_llm.prompt` |
| [`check_llm_manifest`](jane_llm.packages.md#функція-check_llm_manifest) | функція | `jane_llm.packages` |
| [`CompletionRequest`](jane_llm.models.md#клас-completionrequest) | клас | `jane_llm.models` |
| [`CompletionScope`](jane_llm.models.md#клас-completionscope) | клас | `jane_llm.models` |
| [`Connection`](jane_llm.models.md#клас-connection) | клас | `jane_llm.models` |
| [`ConnectionPolicy`](jane_llm.connections.md#клас-connectionpolicy) | dataclass (незмінний) | `jane_llm.connections` |
| [`CounterKey`](jane_llm.store.md#клас-counterkey) | dataclass (незмінний) | `jane_llm.store` |
| [`DataBlock`](jane_llm.prompt.md#клас-datablock) | dataclass (незмінний) | `jane_llm.prompt` |
| [`DataPart`](jane_llm.models.md#клас-datapart) | клас | `jane_llm.models` |
| [`differences`](jane_llm.testing.md#функція-differences) | функція | `jane_llm.testing` |
| [`digest_of`](jane_llm.packages.md#функція-digest_of) | функція | `jane_llm.packages` |
| [`DigestMismatch`](jane_llm.packages.md#клас-digestmismatch) | виняток | `jane_llm.packages` |
| [`etag`](jane_llm.app.md#функція-etag) | функція | `jane_llm.app` |
| [`FakeProvider`](jane_llm.providers.fake.md#клас-fakeprovider) | клас | `jane_llm.providers.fake` |
| [`FakeProviderLimits`](jane_llm.settings.md#клас-fakeproviderlimits) | клас | `jane_llm.settings` |
| [`find_directive`](jane_llm.providers.fake.md#функція-find_directive) | функція | `jane_llm.providers.fake` |
| [`find_secret_like`](jane_llm.connections.md#функція-find_secret_like) | функція | `jane_llm.connections` |
| [`Gateway`](jane_llm.gateway.md#клас-gateway) | клас | `jane_llm.gateway` |
| [`GatewayLimits`](jane_llm.settings.md#клас-gatewaylimits) | клас | `jane_llm.settings` |
| [`HandlerFailure`](jane_llm.handler.md#клас-handlerfailure) | виняток | `jane_llm.handler` |
| [`iter_keys`](jane_llm.store.md#функція-iter_keys) | функція | `jane_llm.store` |
| [`LlmBudget`](jane_llm.settings.md#клас-llmbudget) | клас | `jane_llm.settings` |
| [`LlmHandler`](jane_llm.handler.md#клас-llmhandler) | клас | `jane_llm.handler` |
| [`LlmLimits`](jane_llm.settings.md#клас-llmlimits) | клас | `jane_llm.settings` |
| [`LlmLimitsIn`](jane_llm.models.md#клас-llmlimitsin) | клас | `jane_llm.models` |
| [`LoadedPackage`](jane_llm.packages.md#клас-loadedpackage) | dataclass (незмінний) | `jane_llm.packages` |
| [`main`](jane_llm.__main__.md#функція-main) | функція | `jane_llm.__main__` |
| [`main`](jane_llm.packages.md#функція-main) | функція | `jane_llm.packages` |
| [`make_store`](jane_llm.app.md#функція-make_store) | функція | `jane_llm.app` |
| [`MemoryStore`](jane_llm.store.md#клас-memorystore) | клас | `jane_llm.store` |
| [`minimal_instance`](jane_llm.providers.fake.md#функція-minimal_instance) | функція | `jane_llm.providers.fake` |
| [`ModelAlias`](jane_llm.models.md#клас-modelalias) | клас | `jane_llm.models` |
| [`ModelInfo`](jane_llm.models.md#клас-modelinfo) | клас | `jane_llm.models` |
| [`neutralise`](jane_llm.prompt.md#функція-neutralise) | функція | `jane_llm.prompt` |
| [`new_nonce`](jane_llm.prompt.md#функція-new_nonce) | функція | `jane_llm.prompt` |
| [`PackageLoader`](jane_llm.packages.md#клас-packageloader) | клас | `jane_llm.packages` |
| [`PostgresStore`](jane_llm.store.md#клас-postgresstore) | клас | `jane_llm.store` |
| [`preamble`](jane_llm.prompt.md#функція-preamble) | функція | `jane_llm.prompt` |
| [`Pricing`](jane_llm.models.md#клас-pricing) | клас | `jane_llm.models` |
| [`Prompt`](jane_llm.prompt.md#клас-prompt) | dataclass (незмінний) | `jane_llm.prompt` |
| [`Provider`](jane_llm.models.md#клас-provider) | клас | `jane_llm.models` |
| [`ProviderAdapter`](jane_llm.providers.base.md#клас-provideradapter) | протокол | `jane_llm.providers.base` |
| [`ProviderError`](jane_llm.providers.base.md#клас-providererror) | виняток | `jane_llm.providers.base` |
| [`ProviderLimits`](jane_llm.settings.md#клас-providerlimits) | клас | `jane_llm.settings` |
| [`ProviderRequest`](jane_llm.providers.base.md#клас-providerrequest) | dataclass (незмінний) | `jane_llm.providers.base` |
| [`ProviderResponse`](jane_llm.providers.base.md#клас-providerresponse) | dataclass (незмінний) | `jane_llm.providers.base` |
| [`publish`](jane_llm.packages.md#функція-publish) | функція | `jane_llm.packages` |
| [`publish_request`](jane_llm.packages.md#функція-publish_request) | функція | `jane_llm.packages` |
| [`RateCheck`](jane_llm.store.md#клас-ratecheck) | dataclass (незмінний) | `jane_llm.store` |
| [`RateExceeded`](jane_llm.store.md#клас-rateexceeded) | виняток | `jane_llm.store` |
| [`read_dir`](jane_llm.packages.md#функція-read_dir) | функція | `jane_llm.packages` |
| [`RegistryLimits`](jane_llm.settings.md#клас-registrylimits) | клас | `jane_llm.settings` |
| [`render_template`](jane_llm.handler.md#функція-render_template) | функція | `jane_llm.handler` |
| [`resolve_connection`](jane_llm.connections.md#функція-resolve_connection) | функція | `jane_llm.connections` |
| [`resolve_ref`](jane_llm.connections.md#функція-resolve_ref) | функція | `jane_llm.connections` |
| [`resolve_service_limits`](jane_llm.settings.md#функція-resolve_service_limits) | функція | `jane_llm.settings` |
| [`ResolvedConnection`](jane_llm.providers.base.md#клас-resolvedconnection) | dataclass (незмінний) | `jane_llm.providers.base` |
| [`ResolvedModel`](jane_llm.gateway.md#клас-resolvedmodel) | dataclass (незмінний) | `jane_llm.gateway` |
| [`retry_hint`](jane_llm.prompt.md#функція-retry_hint) | функція | `jane_llm.prompt` |
| [`run_tests`](jane_llm.testing.md#функція-run_tests) | функція | `jane_llm.testing` |
| [`Scope`](jane_llm.gateway.md#клас-scope) | dataclass (незмінний) | `jane_llm.gateway` |
| [`seed`](jane_llm.app.md#функція-seed) | функція | `jane_llm.app` |
| [`ServiceLimits`](jane_llm.settings.md#клас-servicelimits) | клас | `jane_llm.settings` |
| [`Settings`](jane_llm.settings.md#клас-settings) | модель Pydantic | `jane_llm.settings` |
| [`split_channels`](jane_llm.providers.fake.md#функція-split_channels) | функція | `jane_llm.providers.fake` |
| [`Store`](jane_llm.store.md#клас-store) | протокол | `jane_llm.store` |
| [`Strict`](jane_llm.models.md#клас-strict) | модель Pydantic | `jane_llm.models` |
| [`unpack`](jane_llm.packages.md#функція-unpack) | функція | `jane_llm.packages` |
| [`UsageQuery`](jane_llm.store.md#клас-usagequery) | dataclass | `jane_llm.store` |
| [`UsageRecord`](jane_llm.store.md#клас-usagerecord) | dataclass | `jane_llm.store` |
| [`UsageRow`](jane_llm.store.md#клас-usagerow) | dataclass | `jane_llm.store` |
| [`validate_output`](jane_llm.gateway.md#функція-validate_output) | функція | `jane_llm.gateway` |
| [`window`](jane_llm.gateway.md#функція-window) | функція | `jane_llm.gateway` |
