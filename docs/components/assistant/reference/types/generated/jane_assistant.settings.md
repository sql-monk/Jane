# jane_assistant.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.settings.ENV_PREFIX](#jane_assistantsettingsenv_prefix)
- [jane_assistant.settings.Settings](#jane_assistantsettingssettings)
- [jane_assistant.settings.Settings.model_config](#jane_assistantsettingssettingsmodel_config)
- [jane_assistant.settings.Settings.service_name](#jane_assistantsettingssettingsservice_name)
- [jane_assistant.settings.Settings.state_dsn](#jane_assistantsettingssettingsstate_dsn)
- [jane_assistant.settings.Settings.state_schema](#jane_assistantsettingssettingsstate_schema)
- [jane_assistant.settings.Settings.llm_url](#jane_assistantsettingssettingsllm_url)
- [jane_assistant.settings.Settings.registry_url](#jane_assistantsettingssettingsregistry_url)
- [jane_assistant.settings.Settings.collector_web_url](#jane_assistantsettingssettingscollector_web_url)
- [jane_assistant.settings.Settings.collector_telegram_url](#jane_assistantsettingssettingscollector_telegram_url)
- [jane_assistant.settings.Settings.handler_runtime_url](#jane_assistantsettingssettingshandler_runtime_url)
- [jane_assistant.settings.Settings.orchestrator_url](#jane_assistantsettingssettingsorchestrator_url)
- [jane_assistant.settings.Settings.storage_url](#jane_assistantsettingssettingsstorage_url)
- [jane_assistant.settings.Settings.service_token_ref](#jane_assistantsettingssettingsservice_token_ref)
- [jane_assistant.settings.Settings.llm_token_ref](#jane_assistantsettingssettingsllm_token_ref)
- [jane_assistant.settings.Settings.registry_token_ref](#jane_assistantsettingssettingsregistry_token_ref)
- [jane_assistant.settings.Settings.collector_web_token_ref](#jane_assistantsettingssettingscollector_web_token_ref)
- [jane_assistant.settings.Settings.collector_telegram_token_ref](#jane_assistantsettingssettingscollector_telegram_token_ref)
- [jane_assistant.settings.Settings.handler_runtime_token_ref](#jane_assistantsettingssettingshandler_runtime_token_ref)
- [jane_assistant.settings.Settings.orchestrator_token_ref](#jane_assistantsettingssettingsorchestrator_token_ref)
- [jane_assistant.settings.Settings.storage_token_ref](#jane_assistantsettingssettingsstorage_token_ref)
- [jane_assistant.settings.Settings.service_token_env](#jane_assistantsettingssettingsservice_token_env)
- [jane_assistant.settings.Settings.search_provider](#jane_assistantsettingssettingssearch_provider)
- [jane_assistant.settings.Settings.search_static_file](#jane_assistantsettingssettingssearch_static_file)
- [jane_assistant.settings.Settings.search_url_template](#jane_assistantsettingssettingssearch_url_template)
- [jane_assistant.settings.Settings.search_items_path](#jane_assistantsettingssettingssearch_items_path)
- [jane_assistant.settings.Settings.search_title_field](#jane_assistantsettingssettingssearch_title_field)
- [jane_assistant.settings.Settings.search_url_field](#jane_assistantsettingssettingssearch_url_field)
- [jane_assistant.settings.Settings.search_description_field](#jane_assistantsettingssettingssearch_description_field)
- [jane_assistant.settings.Settings.blob_roots](#jane_assistantsettingssettingsblob_roots)
- [jane_assistant.settings.Settings.download_host_allowlist](#jane_assistantsettingssettingsdownload_host_allowlist)
- [jane_assistant.settings.Settings.contracts_dir](#jane_assistantsettingssettingscontracts_dir)
- [jane_assistant.settings.Settings.default_storage_package](#jane_assistantsettingssettingsdefault_storage_package)
- [jane_assistant.settings.Settings.default_storage_connection](#jane_assistantsettingssettingsdefault_storage_connection)
- [jane_assistant.settings.Settings.llm_model_cheap](#jane_assistantsettingssettingsllm_model_cheap)
- [jane_assistant.settings.Settings.llm_model_strong](#jane_assistantsettingssettingsllm_model_strong)
- [jane_assistant.settings.Settings.llm_completion_mode](#jane_assistantsettingssettingsllm_completion_mode)
- [jane_assistant.settings.Settings.generated_code_allowed_modules](#jane_assistantsettingssettingsgenerated_code_allowed_modules)
- [jane_assistant.settings.Settings.onboarding_allow_activation](#jane_assistantsettingssettingsonboarding_allow_activation)
- [jane_assistant.settings.Budget](#jane_assistantsettingsbudget)
- [jane_assistant.settings.Budget.amount](#jane_assistantsettingsbudgetamount)
- [jane_assistant.settings.Budget.currency](#jane_assistantsettingsbudgetcurrency)
- [jane_assistant.settings.Budget.period](#jane_assistantsettingsbudgetperiod)
- [jane_assistant.settings.LlmLimits](#jane_assistantsettingsllmlimits)
- [jane_assistant.settings.LlmLimits.max_requests_per_minute](#jane_assistantsettingsllmlimitsmax_requests_per_minute)
- [jane_assistant.settings.LlmLimits.max_input_tokens_per_request](#jane_assistantsettingsllmlimitsmax_input_tokens_per_request)
- [jane_assistant.settings.LlmLimits.max_output_tokens_per_request](#jane_assistantsettingsllmlimitsmax_output_tokens_per_request)
- [jane_assistant.settings.LlmLimits.budget](#jane_assistantsettingsllmlimitsbudget)
- [jane_assistant.settings.LlmLimits.max_improvement_attempts](#jane_assistantsettingsllmlimitsmax_improvement_attempts)
- [jane_assistant.settings.LlmLimits.max_onboarding_samples](#jane_assistantsettingsllmlimitsmax_onboarding_samples)
- [jane_assistant.settings.LlmLimits.min_onboarding_confidence](#jane_assistantsettingsllmlimitsmin_onboarding_confidence)
- [jane_assistant.settings.OnboardingLimits](#jane_assistantsettingsonboardinglimits)
- [jane_assistant.settings.OnboardingLimits.min_distinct_types](#jane_assistantsettingsonboardinglimitsmin_distinct_types)
- [jane_assistant.settings.OnboardingLimits.sample_batch_size](#jane_assistantsettingsonboardinglimitssample_batch_size)
- [jane_assistant.settings.OnboardingLimits.max_sample_chars](#jane_assistantsettingsonboardinglimitsmax_sample_chars)
- [jane_assistant.settings.OnboardingLimits.max_example_chars](#jane_assistantsettingsonboardinglimitsmax_example_chars)
- [jane_assistant.settings.OnboardingLimits.min_examples_per_type](#jane_assistantsettingsonboardinglimitsmin_examples_per_type)
- [jane_assistant.settings.OnboardingLimits.max_examples_per_type](#jane_assistantsettingsonboardinglimitsmax_examples_per_type)
- [jane_assistant.settings.OnboardingLimits.max_negative_examples](#jane_assistantsettingsonboardinglimitsmax_negative_examples)
- [jane_assistant.settings.OnboardingLimits.poll_page_factor](#jane_assistantsettingsonboardinglimitspoll_page_factor)
- [jane_assistant.settings.OnboardingLimits.max_candidates](#jane_assistantsettingsonboardinglimitsmax_candidates)
- [jane_assistant.settings.OnboardingLimits.auto_select_confidence](#jane_assistantsettingsonboardinglimitsauto_select_confidence)
- [jane_assistant.settings.OnboardingLimits.auto_select_margin](#jane_assistantsettingsonboardinglimitsauto_select_margin)
- [jane_assistant.settings.OnboardingLimits.max_candidate_packages](#jane_assistantsettingsonboardinglimitsmax_candidate_packages)
- [jane_assistant.settings.OnboardingLimits.bind_threshold](#jane_assistantsettingsonboardinglimitsbind_threshold)
- [jane_assistant.settings.OnboardingLimits.fork_threshold](#jane_assistantsettingsonboardinglimitsfork_threshold)
- [jane_assistant.settings.OnboardingLimits.max_generation_attempts](#jane_assistantsettingsonboardinglimitsmax_generation_attempts)
- [jane_assistant.settings.OnboardingLimits.max_proposals](#jane_assistantsettingsonboardinglimitsmax_proposals)
- [jane_assistant.settings.OnboardingLimits.fetch_ratio](#jane_assistantsettingsonboardinglimitsfetch_ratio)
- [jane_assistant.settings.OnboardingLimits.collection_poll_wait_ms](#jane_assistantsettingsonboardinglimitscollection_poll_wait_ms)
- [jane_assistant.settings.OnboardingLimits.max_empty_polls](#jane_assistantsettingsonboardinglimitsmax_empty_polls)
- [jane_assistant.settings.OnboardingLimits.requests_overhead_ratio](#jane_assistantsettingsonboardinglimitsrequests_overhead_ratio)
- [jane_assistant.settings.OnboardingLimits.max_link_patterns](#jane_assistantsettingsonboardinglimitsmax_link_patterns)
- [jane_assistant.settings.OnboardingLimits.link_pattern_examples](#jane_assistantsettingsonboardinglimitslink_pattern_examples)
- [jane_assistant.settings.OnboardingLimits.max_pages_listed](#jane_assistantsettingsonboardinglimitsmax_pages_listed)
- [jane_assistant.settings.OnboardingLimits.max_evidence_examples](#jane_assistantsettingsonboardinglimitsmax_evidence_examples)
- [jane_assistant.settings.OnboardingLimits.max_risk_url_chars](#jane_assistantsettingsonboardinglimitsmax_risk_url_chars)
- [jane_assistant.settings.MaterialLimits](#jane_assistantsettingsmateriallimits)
- [jane_assistant.settings.MaterialLimits.max_fixture_bytes](#jane_assistantsettingsmateriallimitsmax_fixture_bytes)
- [jane_assistant.settings.MaterialLimits.head_share](#jane_assistantsettingsmateriallimitshead_share)
- [jane_assistant.settings.MaterialLimits.structured_share](#jane_assistantsettingsmateriallimitsstructured_share)
- [jane_assistant.settings.MaterialLimits.text_share](#jane_assistantsettingsmateriallimitstext_share)
- [jane_assistant.settings.MaterialLimits.max_list_items](#jane_assistantsettingsmateriallimitsmax_list_items)
- [jane_assistant.settings.MaterialLimits.max_string_chars](#jane_assistantsettingsmateriallimitsmax_string_chars)
- [jane_assistant.settings.MaterialLimits.short_string_chars](#jane_assistantsettingsmateriallimitsshort_string_chars)
- [jane_assistant.settings.MaterialLimits.max_head_tags](#jane_assistantsettingsmateriallimitsmax_head_tags)
- [jane_assistant.settings.MaterialLimits.max_microdata_types](#jane_assistantsettingsmateriallimitsmax_microdata_types)
- [jane_assistant.settings.MaterialLimits.max_microdata_props](#jane_assistantsettingsmateriallimitsmax_microdata_props)
- [jane_assistant.settings.ImprovementLimits](#jane_assistantsettingsimprovementlimits)
- [jane_assistant.settings.ImprovementLimits.max_sample_chars](#jane_assistantsettingsimprovementlimitsmax_sample_chars)
- [jane_assistant.settings.ImprovementLimits.max_problem_samples](#jane_assistantsettingsimprovementlimitsmax_problem_samples)
- [jane_assistant.settings.ImprovementLimits.max_successful_examples](#jane_assistantsettingsimprovementlimitsmax_successful_examples)
- [jane_assistant.settings.ImprovementLimits.max_file_chars](#jane_assistantsettingsimprovementlimitsmax_file_chars)
- [jane_assistant.settings.ImprovementLimits.max_proposal_bytes](#jane_assistantsettingsimprovementlimitsmax_proposal_bytes)
- [jane_assistant.settings.UnknownLimits](#jane_assistantsettingsunknownlimits)
- [jane_assistant.settings.UnknownLimits.max_sample_chars](#jane_assistantsettingsunknownlimitsmax_sample_chars)
- [jane_assistant.settings.UnknownLimits.min_confidence](#jane_assistantsettingsunknownlimitsmin_confidence)
- [jane_assistant.settings.TransferLimits](#jane_assistantsettingstransferlimits)
- [jane_assistant.settings.TransferLimits.inline_max_bytes](#jane_assistantsettingstransferlimitsinline_max_bytes)
- [jane_assistant.settings.ContentLimits](#jane_assistantsettingscontentlimits)
- [jane_assistant.settings.ContentLimits.max_material_bytes](#jane_assistantsettingscontentlimitsmax_material_bytes)
- [jane_assistant.settings.ContentLimits.fetch_timeout_ms](#jane_assistantsettingscontentlimitsfetch_timeout_ms)
- [jane_assistant.settings.ContentLimits.connect_timeout_ms](#jane_assistantsettingscontentlimitsconnect_timeout_ms)
- [jane_assistant.settings.SearchLimits](#jane_assistantsettingssearchlimits)
- [jane_assistant.settings.SearchLimits.request_timeout_ms](#jane_assistantsettingssearchlimitsrequest_timeout_ms)
- [jane_assistant.settings.SearchLimits.connect_timeout_ms](#jane_assistantsettingssearchlimitsconnect_timeout_ms)
- [jane_assistant.settings.LlmCallLimits](#jane_assistantsettingsllmcalllimits)
- [jane_assistant.settings.LlmCallLimits.request_timeout_ms](#jane_assistantsettingsllmcalllimitsrequest_timeout_ms)
- [jane_assistant.settings.LlmCallLimits.chars_per_token](#jane_assistantsettingsllmcalllimitschars_per_token)
- [jane_assistant.settings.LlmCallLimits.prompt_overhead_chars](#jane_assistantsettingsllmcalllimitsprompt_overhead_chars)
- [jane_assistant.settings.LlmCallLimits.part_overhead_chars](#jane_assistantsettingsllmcalllimitspart_overhead_chars)
- [jane_assistant.settings.LlmCallLimits.client_limits](#jane_assistantsettingsllmcalllimitsclient_limits)
- [jane_assistant.settings.StateLimits](#jane_assistantsettingsstatelimits)
- [jane_assistant.settings.StateLimits.pool_max_size](#jane_assistantsettingsstatelimitspool_max_size)
- [jane_assistant.settings.StateLimits.connect_timeout_ms](#jane_assistantsettingsstatelimitsconnect_timeout_ms)
- [jane_assistant.settings.StateLimits.in_progress_lease_ms](#jane_assistantsettingsstatelimitsin_progress_lease_ms)
- [jane_assistant.settings.StateLimits.job_lease_ms](#jane_assistantsettingsstatelimitsjob_lease_ms)
- [jane_assistant.settings.StateLimits.heartbeat_interval_ms](#jane_assistantsettingsstatelimitsheartbeat_interval_ms)
- [jane_assistant.settings.StateLimits.session_retention_seconds](#jane_assistantsettingsstatelimitssession_retention_seconds)
- [jane_assistant.settings.ServiceLimits](#jane_assistantsettingsservicelimits)
- [jane_assistant.settings.ServiceLimits.state](#jane_assistantsettingsservicelimitsstate)
- [jane_assistant.settings.ServiceLimits.llm](#jane_assistantsettingsservicelimitsllm)
- [jane_assistant.settings.ServiceLimits.transfer](#jane_assistantsettingsservicelimitstransfer)
- [jane_assistant.settings.ServiceLimits.onboarding](#jane_assistantsettingsservicelimitsonboarding)
- [jane_assistant.settings.ServiceLimits.material](#jane_assistantsettingsservicelimitsmaterial)
- [jane_assistant.settings.ServiceLimits.improvement](#jane_assistantsettingsservicelimitsimprovement)
- [jane_assistant.settings.ServiceLimits.unknown](#jane_assistantsettingsservicelimitsunknown)
- [jane_assistant.settings.ServiceLimits.content](#jane_assistantsettingsservicelimitscontent)
- [jane_assistant.settings.ServiceLimits.search](#jane_assistantsettingsservicelimitssearch)
- [jane_assistant.settings.ServiceLimits.clients](#jane_assistantsettingsservicelimitsclients)
- [jane_assistant.settings.ServiceLimits.llm_call](#jane_assistantsettingsservicelimitsllm_call)
- [jane_assistant.settings.ServiceLimits.pages](#jane_assistantsettingsservicelimitspages)
- [jane_assistant.settings.ServiceLimits.jobs](#jane_assistantsettingsservicelimitsjobs)
- [jane_assistant.settings.ServiceLimits.idempotency](#jane_assistantsettingsservicelimitsidempotency)
- [jane_assistant.settings.resolve_service_limits](#jane_assistantsettingsresolve_service_limits)
- [jane_assistant.settings.request_layer](#jane_assistantsettingsrequest_layer)

## jane_assistant.settings.ENV_PREFIX

**Константа.** Код: [services/assistant/src/jane_assistant/settings.py:35](../../../../../../services/assistant/src/jane_assistant/settings.py#L35).

```python
ENV_PREFIX = 'JANE_ASSISTANT_'
```

## jane_assistant.settings.Settings

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:38](../../../../../../services/assistant/src/jane_assistant/settings.py#L38).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_assistant.settings.md#jane_assistantsettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_assistant.settings.md#jane_assistantsettingssettingsservice_name) | Поле | ні |
| [state_dsn](jane_assistant.settings.md#jane_assistantsettingssettingsstate_dsn) | Поле | ні |
| [state_schema](jane_assistant.settings.md#jane_assistantsettingssettingsstate_schema) | Поле | ні |
| [llm_url](jane_assistant.settings.md#jane_assistantsettingssettingsllm_url) | Поле | ні |
| [registry_url](jane_assistant.settings.md#jane_assistantsettingssettingsregistry_url) | Поле | ні |
| [collector_web_url](jane_assistant.settings.md#jane_assistantsettingssettingscollector_web_url) | Поле | ні |
| [collector_telegram_url](jane_assistant.settings.md#jane_assistantsettingssettingscollector_telegram_url) | Поле | ні |
| [handler_runtime_url](jane_assistant.settings.md#jane_assistantsettingssettingshandler_runtime_url) | Поле | ні |
| [orchestrator_url](jane_assistant.settings.md#jane_assistantsettingssettingsorchestrator_url) | Поле | ні |
| [storage_url](jane_assistant.settings.md#jane_assistantsettingssettingsstorage_url) | Поле | ні |
| [service_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingsservice_token_ref) | Поле | ні |
| [llm_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingsllm_token_ref) | Поле | ні |
| [registry_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingsregistry_token_ref) | Поле | ні |
| [collector_web_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingscollector_web_token_ref) | Поле | ні |
| [collector_telegram_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingscollector_telegram_token_ref) | Поле | ні |
| [handler_runtime_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingshandler_runtime_token_ref) | Поле | ні |
| [orchestrator_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingsorchestrator_token_ref) | Поле | ні |
| [storage_token_ref](jane_assistant.settings.md#jane_assistantsettingssettingsstorage_token_ref) | Поле | ні |
| [service_token_env](jane_assistant.settings.md#jane_assistantsettingssettingsservice_token_env) | Поле | ні |
| [search_provider](jane_assistant.settings.md#jane_assistantsettingssettingssearch_provider) | Поле | ні |
| [search_static_file](jane_assistant.settings.md#jane_assistantsettingssettingssearch_static_file) | Поле | ні |
| [search_url_template](jane_assistant.settings.md#jane_assistantsettingssettingssearch_url_template) | Поле | ні |
| [search_items_path](jane_assistant.settings.md#jane_assistantsettingssettingssearch_items_path) | Поле | ні |
| [search_title_field](jane_assistant.settings.md#jane_assistantsettingssettingssearch_title_field) | Поле | ні |
| [search_url_field](jane_assistant.settings.md#jane_assistantsettingssettingssearch_url_field) | Поле | ні |
| [search_description_field](jane_assistant.settings.md#jane_assistantsettingssettingssearch_description_field) | Поле | ні |
| [blob_roots](jane_assistant.settings.md#jane_assistantsettingssettingsblob_roots) | Поле | ні |
| [download_host_allowlist](jane_assistant.settings.md#jane_assistantsettingssettingsdownload_host_allowlist) | Поле | ні |
| [contracts_dir](jane_assistant.settings.md#jane_assistantsettingssettingscontracts_dir) | Поле | ні |
| [default_storage_package](jane_assistant.settings.md#jane_assistantsettingssettingsdefault_storage_package) | Поле | ні |
| [default_storage_connection](jane_assistant.settings.md#jane_assistantsettingssettingsdefault_storage_connection) | Поле | ні |
| [llm_model_cheap](jane_assistant.settings.md#jane_assistantsettingssettingsllm_model_cheap) | Поле | ні |
| [llm_model_strong](jane_assistant.settings.md#jane_assistantsettingssettingsllm_model_strong) | Поле | ні |
| [llm_completion_mode](jane_assistant.settings.md#jane_assistantsettingssettingsllm_completion_mode) | Поле | ні |
| [generated_code_allowed_modules](jane_assistant.settings.md#jane_assistantsettingssettingsgenerated_code_allowed_modules) | Поле | ні |
| [onboarding_allow_activation](jane_assistant.settings.md#jane_assistantsettingssettingsonboarding_allow_activation) | Поле | ні |
| [instance_id](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsinstance_id) | Поле | так |
| [host](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshost) | Поле | так |
| [port](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsport) | Поле | так |
| [log_level](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_level) | Поле | так |
| [log_format](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_format) | Поле | так |
| [metrics_enabled](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsmetrics_enabled) | Поле | так |
| [health_check_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshealth_check_timeout_ms) | Поле | так |
| [limits_file](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslimits_file) | Поле | так |
| [platform_layers](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsplatform_layers) | Метод | так |
| [with_overrides](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingswith_overrides) | Метод | так |
| [auth_mode](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_mode) | Поле | так |
| [auth_none_allow_remote](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_none_allow_remote) | Поле | так |
| [api_keys](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys) | Поле | так |
| [api_keys_file](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys_file) | Поле | так |
| [jwt_jwks_url](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_url) | Поле | так |
| [jwt_issuer](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_issuer) | Поле | так |
| [jwt_audience](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_audience) | Поле | так |
| [jwt_algorithms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_algorithms) | Поле | так |
| [jwt_scope_claim](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_scope_claim) | Поле | так |
| [jwt_leeway_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_leeway_seconds) | Поле | так |
| [jwt_jwks_cache_ttl_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds) | Поле | так |
| [jwt_jwks_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_timeout_ms) | Поле | так |
| [jwt_jwks_refresh_cooldown_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds) | Поле | так |
| [jwt_jwks_max_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_max_bytes) | Поле | так |
| [auth_max_token_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_max_token_bytes) | Поле | так |
| [metrics_public](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsmetrics_public) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:136](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L136).

```python
settings = settings or Settings(log_format="console", contracts_dir=contracts)
```

Контекст і передумови: [services/assistant/tests/test_app.py:50](../../../../../../services/assistant/tests/test_app.py#L50).

```python
app = build_app(Settings(log_format="console"))
```

## jane_assistant.settings.Settings.model_config

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:39](../../../../../../services/assistant/src/jane_assistant/settings.py#L39).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.service_name

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:41](../../../../../../services/assistant/src/jane_assistant/settings.py#L41).

```python
service_name: str = 'assistant'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.state_dsn

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:43](../../../../../../services/assistant/src/jane_assistant/settings.py#L43).

```python
state_dsn: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
PostgreSQL DSN of the service's own state (sessions, jobs, idempotency keys) shared by instances.
    Unset: in-memory state - only for a single standalone instance and tests (lost on restart).
```

## jane_assistant.settings.Settings.state_schema

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:46](../../../../../../services/assistant/src/jane_assistant/settings.py#L46).

```python
state_schema: str = Field(default='jane_assistant', pattern='^[a-z_][a-z0-9_]{0,62}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'jane_assistant'",
  "pattern": "'^[a-z_][a-z0-9_]{0,62}$'"
}
```

### Опис із вихідного коду

```text
Schema of the state tables (created if missing).
```

## jane_assistant.settings.Settings.llm_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:51](../../../../../../services/assistant/src/jane_assistant/settings.py#L51).

```python
llm_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.registry_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:52](../../../../../../services/assistant/src/jane_assistant/settings.py#L52).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.collector_web_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:53](../../../../../../services/assistant/src/jane_assistant/settings.py#L53).

```python
collector_web_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.collector_telegram_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:54](../../../../../../services/assistant/src/jane_assistant/settings.py#L54).

```python
collector_telegram_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.handler_runtime_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:55](../../../../../../services/assistant/src/jane_assistant/settings.py#L55).

```python
handler_runtime_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.orchestrator_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:56](../../../../../../services/assistant/src/jane_assistant/settings.py#L56).

```python
orchestrator_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.storage_url

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:57](../../../../../../services/assistant/src/jane_assistant/settings.py#L57).

```python
storage_url: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.service_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:60](../../../../../../services/assistant/src/jane_assistant/settings.py#L60).

```python
service_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Token for every neighbour that has no reference of its own below.
```

## jane_assistant.settings.Settings.llm_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:62](../../../../../../services/assistant/src/jane_assistant/settings.py#L62).

```python
llm_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.registry_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:63](../../../../../../services/assistant/src/jane_assistant/settings.py#L63).

```python
registry_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.collector_web_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:64](../../../../../../services/assistant/src/jane_assistant/settings.py#L64).

```python
collector_web_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.collector_telegram_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:65](../../../../../../services/assistant/src/jane_assistant/settings.py#L65).

```python
collector_telegram_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.handler_runtime_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:66](../../../../../../services/assistant/src/jane_assistant/settings.py#L66).

```python
handler_runtime_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.orchestrator_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:67](../../../../../../services/assistant/src/jane_assistant/settings.py#L67).

```python
orchestrator_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.storage_token_ref

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:68](../../../../../../services/assistant/src/jane_assistant/settings.py#L68).

```python
storage_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.service_token_env

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:69](../../../../../../services/assistant/src/jane_assistant/settings.py#L69).

```python
service_token_env: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Deprecated: name of an environment variable with the token for all neighbours; use
    ``service_token_ref=env:<name>``.
```

## jane_assistant.settings.Settings.search_provider

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:74](../../../../../../services/assistant/src/jane_assistant/settings.py#L74).

```python
search_provider: Literal['none', 'static', 'http_json'] = 'none'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.search_static_file

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:75](../../../../../../services/assistant/src/jane_assistant/settings.py#L75).

```python
search_static_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``static``: JSON file ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?}]``.
```

## jane_assistant.settings.Settings.search_url_template

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:77](../../../../../../services/assistant/src/jane_assistant/settings.py#L77).

```python
search_url_template: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``http_json``: URL with ``{query}``, e.g. an internal search gateway.
```

## jane_assistant.settings.Settings.search_items_path

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:79](../../../../../../services/assistant/src/jane_assistant/settings.py#L79).

```python
search_items_path: str = 'results'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.search_title_field

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:80](../../../../../../services/assistant/src/jane_assistant/settings.py#L80).

```python
search_title_field: str = 'title'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.search_url_field

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:81](../../../../../../services/assistant/src/jane_assistant/settings.py#L81).

```python
search_url_field: str = 'url'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.search_description_field

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:82](../../../../../../services/assistant/src/jane_assistant/settings.py#L82).

```python
search_description_field: str = 'description'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.Settings.blob_roots

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:86](../../../../../../services/assistant/src/jane_assistant/settings.py#L86).

```python
blob_roots: list[Path] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
Directories from which ``file://`` material content may be read (JSON list). Empty (default): ``file://``
    content is refused - a request must not read arbitrary files of this container.
```

## jane_assistant.settings.Settings.download_host_allowlist

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:89](../../../../../../services/assistant/src/jane_assistant/settings.py#L89).

```python
download_host_allowlist: list[str] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
``hostname`` (any port) or ``hostname:port`` a material ``download_url`` may point to (JSON list).
    Empty (default): downloads are refused. Redirects are never followed.
```

## jane_assistant.settings.Settings.contracts_dir

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:93](../../../../../../services/assistant/src/jane_assistant/settings.py#L93).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Where ``contracts/schemas`` live (local validation of generated rules and manifests).
    Empty -> found upwards from the package (dev checkout) or ``/app/contracts`` (Docker).
```

## jane_assistant.settings.Settings.default_storage_package

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:97](../../../../../../services/assistant/src/jane_assistant/settings.py#L97).

```python
default_storage_package: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``package_id@version`` of a storage package added to task drafts (optional).
```

## jane_assistant.settings.Settings.default_storage_connection

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:99](../../../../../../services/assistant/src/jane_assistant/settings.py#L99).

```python
default_storage_connection: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``connection_id`` for that storage stage.
```

## jane_assistant.settings.Settings.llm_model_cheap

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:101](../../../../../../services/assistant/src/jane_assistant/settings.py#L101).

```python
llm_model_cheap: str = 'cheap'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Model alias of the LLM gateway for classification (sampling, unknown materials).
```

## jane_assistant.settings.Settings.llm_model_strong

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:103](../../../../../../services/assistant/src/jane_assistant/settings.py#L103).

```python
llm_model_strong: str = 'strong'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Model alias for analysis, proposals and code generation.
```

## jane_assistant.settings.Settings.llm_completion_mode

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:105](../../../../../../services/assistant/src/jane_assistant/settings.py#L105).

```python
llm_completion_mode: Literal['sync', 'async'] = 'sync'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
How the assistant waits for a model call (``llm.v1`` ``CompletionRequest.mode``): ``sync`` - one HTTP
    request with its own timeout ``limits.llm_call.request_timeout_ms``; ``async`` - 202 + job of the gateway,
    polled every ``clients.job_poll_interval_ms`` within ``clients.job_wait_timeout_ms`` (no long connection).
```

## jane_assistant.settings.Settings.generated_code_allowed_modules

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:109](../../../../../../services/assistant/src/jane_assistant/settings.py#L109).

```python
generated_code_allowed_modules: list[str] = Field(default_factory=lambda: ['re', 'html', 'json', 'math', 'datetime', 'decimal', 'string', 'unicodedata', 'itertools', 'functools', 'collections', 'typing', 'dataclasses'])
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: ['re', 'html', 'json', 'math', 'datetime', 'decimal', 'string', 'unicodedata', 'itertools', 'functools', 'collections', 'typing', 'dataclasses']"
}
```

### Опис із вихідного коду

```text
Policy (not a limit): modules generated extractor code may import. The runtime sandbox
    (WP-06) is the real barrier; this list rejects obviously unsuitable code early.
```

## jane_assistant.settings.Settings.onboarding_allow_activation

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:128](../../../../../../services/assistant/src/jane_assistant/settings.py#L128).

```python
onboarding_allow_activation: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Allow ``acceptProposal`` with ``activate: true`` to create the source and task in the
    orchestrator (only when every extractor passed its tests).
```

## jane_assistant.settings.Budget

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:139](../../../../../../services/assistant/src/jane_assistant/settings.py#L139).

```python
class Budget(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [amount](jane_assistant.settings.md#jane_assistantsettingsbudgetamount) | Поле | ні |
| [currency](jane_assistant.settings.md#jane_assistantsettingsbudgetcurrency) | Поле | ні |
| [period](jane_assistant.settings.md#jane_assistantsettingsbudgetperiod) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Contract ``limits.llm.budget`` (``Budget``).
```

## jane_assistant.settings.Budget.amount

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:142](../../../../../../services/assistant/src/jane_assistant/settings.py#L142).

```python
amount: float = Field(default=2.0, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2.0",
  "ge": "0"
}
```

## jane_assistant.settings.Budget.currency

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:143](../../../../../../services/assistant/src/jane_assistant/settings.py#L143).

```python
currency: str = Field(default='USD', pattern='^[A-Z]{3}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'USD'",
  "pattern": "'^[A-Z]{3}$'"
}
```

## jane_assistant.settings.Budget.period

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:144](../../../../../../services/assistant/src/jane_assistant/settings.py#L144).

```python
period: Literal['run', 'day', 'week', 'month', 'total'] = 'run'
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.LlmLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:147](../../../../../../services/assistant/src/jane_assistant/settings.py#L147).

```python
class LlmLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_requests_per_minute](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmax_requests_per_minute) | Поле | ні |
| [max_input_tokens_per_request](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmax_input_tokens_per_request) | Поле | ні |
| [max_output_tokens_per_request](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmax_output_tokens_per_request) | Поле | ні |
| [budget](jane_assistant.settings.md#jane_assistantsettingsllmlimitsbudget) | Поле | ні |
| [max_improvement_attempts](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmax_improvement_attempts) | Поле | ні |
| [max_onboarding_samples](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmax_onboarding_samples) | Поле | ні |
| [min_onboarding_confidence](jane_assistant.settings.md#jane_assistantsettingsllmlimitsmin_onboarding_confidence) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Contract ``limits.llm``. ``budget`` follows the contract's ``Budget`` semantics: with ``period: run`` it is
the limit of one assistant run (onboarding session, improvement or unknown-material job) - every call sends
it with ``scope.run_id`` and the gateway counts the run; ``amount: 0`` allows no LLM call. The assistant
also stops by itself once its run spent ``budget.amount``.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:147](../../../../../../services/assistant/tests/test_large_sites.py#L147).

```python
budget = int(LlmLimits().max_input_tokens_per_request * LlmCallLimits().chars_per_token)
```

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:103](../../../../../../services/assistant/tests/test_llm_budget.py#L103).

```python
limits = LlmLimits(max_output_tokens_per_request=50, budget=budget(amount))
```

## jane_assistant.settings.LlmLimits.max_requests_per_minute

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:153](../../../../../../services/assistant/src/jane_assistant/settings.py#L153).

```python
max_requests_per_minute: int = Field(default=30, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30",
  "ge": "1"
}
```

## jane_assistant.settings.LlmLimits.max_input_tokens_per_request

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:154](../../../../../../services/assistant/src/jane_assistant/settings.py#L154).

```python
max_input_tokens_per_request: int = Field(default=16000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "16000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Data sent to the model is fitted to this limit as the gateway counts it (``llm_call.chars_per_token``).
```

## jane_assistant.settings.LlmLimits.max_output_tokens_per_request

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:156](../../../../../../services/assistant/src/jane_assistant/settings.py#L156).

```python
max_output_tokens_per_request: int = Field(default=8000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "8000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Room for the model's answer. Code generation answers with a module, a schema and expectations; 4000 cut
    such answers on real pages (the gateway then reports invalid output). Keep the answer within the gateway's
    provider timeout (about 130 tokens/s of a strong model: 8000 tokens ~ 1 min).
```

## jane_assistant.settings.LlmLimits.budget

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:160](../../../../../../services/assistant/src/jane_assistant/settings.py#L160).

```python
budget: Budget = Budget()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.LlmLimits.max_improvement_attempts

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:161](../../../../../../services/assistant/src/jane_assistant/settings.py#L161).

```python
max_improvement_attempts: int = Field(default=3, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "0"
}
```

## jane_assistant.settings.LlmLimits.max_onboarding_samples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:162](../../../../../../services/assistant/src/jane_assistant/settings.py#L162).

```python
max_onboarding_samples: int = Field(default=60, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60",
  "ge": "1"
}
```

## jane_assistant.settings.LlmLimits.min_onboarding_confidence

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:163](../../../../../../services/assistant/src/jane_assistant/settings.py#L163).

```python
min_onboarding_confidence: float = Field(default=0.8, gt=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.8",
  "gt": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Contract ``llm.min_onboarding_confidence`` (WP-15): sampling stops once the sample-coverage confidence
    reaches it; below it within the budget the session is ``insufficient_sample``. Before WP-15 it was the
    internal ``onboarding.min_confidence``.
```

## jane_assistant.settings.OnboardingLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:169](../../../../../../services/assistant/src/jane_assistant/settings.py#L169).

```python
class OnboardingLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [min_distinct_types](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmin_distinct_types) | Поле | ні |
| [sample_batch_size](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitssample_batch_size) | Поле | ні |
| [max_sample_chars](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_sample_chars) | Поле | ні |
| [max_example_chars](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_example_chars) | Поле | ні |
| [min_examples_per_type](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmin_examples_per_type) | Поле | ні |
| [max_examples_per_type](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_examples_per_type) | Поле | ні |
| [max_negative_examples](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_negative_examples) | Поле | ні |
| [poll_page_factor](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitspoll_page_factor) | Поле | ні |
| [max_candidates](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_candidates) | Поле | ні |
| [auto_select_confidence](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsauto_select_confidence) | Поле | ні |
| [auto_select_margin](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsauto_select_margin) | Поле | ні |
| [max_candidate_packages](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_candidate_packages) | Поле | ні |
| [bind_threshold](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsbind_threshold) | Поле | ні |
| [fork_threshold](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsfork_threshold) | Поле | ні |
| [max_generation_attempts](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_generation_attempts) | Поле | ні |
| [max_proposals](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_proposals) | Поле | ні |
| [fetch_ratio](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsfetch_ratio) | Поле | ні |
| [collection_poll_wait_ms](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitscollection_poll_wait_ms) | Поле | ні |
| [max_empty_polls](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_empty_polls) | Поле | ні |
| [requests_overhead_ratio](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsrequests_overhead_ratio) | Поле | ні |
| [max_link_patterns](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_link_patterns) | Поле | ні |
| [link_pattern_examples](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitslink_pattern_examples) | Поле | ні |
| [max_pages_listed](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_pages_listed) | Поле | ні |
| [max_evidence_examples](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_evidence_examples) | Поле | ні |
| [max_risk_url_chars](jane_assistant.settings.md#jane_assistantsettingsonboardinglimitsmax_risk_url_chars) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:146](../../../../../../services/assistant/tests/test_large_sites.py#L146).

```python
assert raw.index("application/ld+json") > OnboardingLimits().max_sample_chars
```

Контекст і передумови: [services/assistant/tests/test_material.py:32](../../../../../../services/assistant/tests/test_material.py#L32).

```python
URL = OnboardingLimits().max_risk_url_chars
```

## jane_assistant.settings.OnboardingLimits.min_distinct_types

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:170](../../../../../../services/assistant/src/jane_assistant/settings.py#L170).

```python
min_distinct_types: int = Field(default=2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Do not trust coverage of a single material type while collection is still running.
```

## jane_assistant.settings.OnboardingLimits.sample_batch_size

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:172](../../../../../../services/assistant/src/jane_assistant/settings.py#L172).

```python
sample_batch_size: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Materials classified per LLM request during adaptive sampling.
```

## jane_assistant.settings.OnboardingLimits.max_sample_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:174](../../../../../../services/assistant/src/jane_assistant/settings.py#L174).

```python
max_sample_chars: int = Field(default=6000, ge=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "6000",
  "ge": "200"
}
```

### Опис із вихідного коду

```text
Text of one material passed to the classifying model. A larger HTML page is shown as a digest of that
    size (see ``material``); a batch shrinks it further to fit ``llm.max_input_tokens_per_request``.
```

## jane_assistant.settings.OnboardingLimits.max_example_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:177](../../../../../../services/assistant/src/jane_assistant/settings.py#L177).

```python
max_example_chars: int = Field(default=12000, ge=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "12000",
  "ge": "200"
}
```

### Опис із вихідного коду

```text
Text of one example material in analysis and extractor generation (a digest for larger HTML; shrunk to
    fit ``llm.max_input_tokens_per_request`` with the other parts of the request).
```

## jane_assistant.settings.OnboardingLimits.min_examples_per_type

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:180](../../../../../../services/assistant/src/jane_assistant/settings.py#L180).

```python
min_examples_per_type: int = Field(default=2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
A material type counts as distinguished after this many examples.
```

## jane_assistant.settings.OnboardingLimits.max_examples_per_type

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:182](../../../../../../services/assistant/src/jane_assistant/settings.py#L182).

```python
max_examples_per_type: int = Field(default=3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Examples of one type sent to analysis and code generation.
```

## jane_assistant.settings.OnboardingLimits.max_negative_examples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:184](../../../../../../services/assistant/src/jane_assistant/settings.py#L184).

```python
max_negative_examples: int = Field(default=1, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Materials of other types used as ``empty`` cases when testing/generating an extractor.
```

## jane_assistant.settings.OnboardingLimits.poll_page_factor

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:186](../../../../../../services/assistant/src/jane_assistant/settings.py#L186).

```python
poll_page_factor: int = Field(default=3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Materials pulled per poll of the sampling collection = ``sample_batch_size x poll_page_factor``
    (the surplus is the pool the diversity selection picks from).
```

## jane_assistant.settings.OnboardingLimits.max_candidates

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:189](../../../../../../services/assistant/src/jane_assistant/settings.py#L189).

```python
max_candidates: int = Field(default=5, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Search results kept for disambiguation.
```

## jane_assistant.settings.OnboardingLimits.auto_select_confidence

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:191](../../../../../../services/assistant/src/jane_assistant/settings.py#L191).

```python
auto_select_confidence: float = Field(default=0.8, gt=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.8",
  "gt": "0",
  "le": "1"
}
```

## jane_assistant.settings.OnboardingLimits.auto_select_margin

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:192](../../../../../../services/assistant/src/jane_assistant/settings.py#L192).

```python
auto_select_margin: float = Field(default=0.2, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.2",
  "ge": "0",
  "le": "1"
}
```

## jane_assistant.settings.OnboardingLimits.max_candidate_packages

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:193](../../../../../../services/assistant/src/jane_assistant/settings.py#L193).

```python
max_candidate_packages: int = Field(default=5, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Existing extractors tested per entity type.
```

## jane_assistant.settings.OnboardingLimits.bind_threshold

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:195](../../../../../../services/assistant/src/jane_assistant/settings.py#L195).

```python
bind_threshold: float = Field(default=0.9, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.9",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Share of samples an existing extractor must pass to be bound as is.
```

## jane_assistant.settings.OnboardingLimits.fork_threshold

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:197](../../../../../../services/assistant/src/jane_assistant/settings.py#L197).

```python
fork_threshold: float = Field(default=0.5, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.5",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Share of samples above which an existing extractor is forked and adapted.
```

## jane_assistant.settings.OnboardingLimits.max_generation_attempts

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:199](../../../../../../services/assistant/src/jane_assistant/settings.py#L199).

```python
max_generation_attempts: int = Field(default=2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
LLM attempts to produce a new extractor that passes its tests.
```

## jane_assistant.settings.OnboardingLimits.max_proposals

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:201](../../../../../../services/assistant/src/jane_assistant/settings.py#L201).

```python
max_proposals: int = Field(default=4, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4",
  "ge": "1"
}
```

## jane_assistant.settings.OnboardingLimits.fetch_ratio

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:202](../../../../../../services/assistant/src/jane_assistant/settings.py#L202).

```python
fetch_ratio: int = Field(default=3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
The sampling collection may fetch up to ``max_onboarding_samples x fetch_ratio`` materials
    (``limits.crawl.max_pages_per_run`` / ``telegram.max_messages_per_run`` of that collection); only
    the most diverse ones are classified.
```

## jane_assistant.settings.OnboardingLimits.collection_poll_wait_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:206](../../../../../../services/assistant/src/jane_assistant/settings.py#L206).

```python
collection_poll_wait_ms: int = Field(default=1000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Long-poll of ``listCollectionMaterials`` while sampling.
```

## jane_assistant.settings.OnboardingLimits.max_empty_polls

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:208](../../../../../../services/assistant/src/jane_assistant/settings.py#L208).

```python
max_empty_polls: int = Field(default=30, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Consecutive empty polls of a running collection before sampling gives up.
```

## jane_assistant.settings.OnboardingLimits.requests_overhead_ratio

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:210](../../../../../../services/assistant/src/jane_assistant/settings.py#L210).

```python
requests_overhead_ratio: float = Field(default=0.05, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.05",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Added to estimated materials for the ``requests_per_run_estimate`` of a proposal.
```

## jane_assistant.settings.OnboardingLimits.max_link_patterns

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:212](../../../../../../services/assistant/src/jane_assistant/settings.py#L212).

```python
max_link_patterns: int = Field(default=20, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
In-page link patterns (and pagination URL templates) of sampled pages kept as evidence for analysis
    and proposals, most frequent first.
```

## jane_assistant.settings.OnboardingLimits.link_pattern_examples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:215](../../../../../../services/assistant/src/jane_assistant/settings.py#L215).

```python
link_pattern_examples: int = Field(default=2, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Example links kept per link pattern.
```

## jane_assistant.settings.OnboardingLimits.max_pages_listed

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:217](../../../../../../services/assistant/src/jane_assistant/settings.py#L217).

```python
max_pages_listed: int = Field(default=20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Page numbers listed per pagination template (the largest seen is always given).
```

## jane_assistant.settings.OnboardingLimits.max_evidence_examples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:219](../../../../../../services/assistant/src/jane_assistant/settings.py#L219).

```python
max_evidence_examples: int = Field(default=5, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Examples kept of other evidence (pages declaring another canonical) and of URL shapes in messages.
```

## jane_assistant.settings.OnboardingLimits.max_risk_url_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:221](../../../../../../services/assistant/src/jane_assistant/settings.py#L221).

```python
max_risk_url_chars: int = Field(default=200, ge=20)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200",
  "ge": "20"
}
```

### Опис із вихідного коду

```text
A page URL quoted in a proposal risk is cut to this many characters.
```

## jane_assistant.settings.MaterialLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:225](../../../../../../services/assistant/src/jane_assistant/settings.py#L225).

```python
class MaterialLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_fixture_bytes](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_fixture_bytes) | Поле | ні |
| [head_share](jane_assistant.settings.md#jane_assistantsettingsmateriallimitshead_share) | Поле | ні |
| [structured_share](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsstructured_share) | Поле | ні |
| [text_share](jane_assistant.settings.md#jane_assistantsettingsmateriallimitstext_share) | Поле | ні |
| [max_list_items](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_list_items) | Поле | ні |
| [max_string_chars](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_string_chars) | Поле | ні |
| [short_string_chars](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsshort_string_chars) | Поле | ні |
| [max_head_tags](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_head_tags) | Поле | ні |
| [max_microdata_types](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_microdata_types) | Поле | ні |
| [max_microdata_props](jane_assistant.settings.md#jane_assistantsettingsmateriallimitsmax_microdata_props) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
How a large HTML material is shown to the model and kept as a test fixture (``material.py``).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:212](../../../../../../services/assistant/tests/test_large_sites.py#L212).

```python
assert content["size_bytes"] == len(content["data"].encode()) <= MaterialLimits().max_fixture_bytes
```

Контекст і передумови: [services/assistant/tests/test_material.py:73](../../../../../../services/assistant/tests/test_material.py#L73).

```python
limits = MaterialLimits()
```

## jane_assistant.settings.MaterialLimits.max_fixture_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:228](../../../../../../services/assistant/src/jane_assistant/settings.py#L228).

```python
max_fixture_bytes: int = Field(default=131072, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "131072",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
HTML content above this size is reduced once it is read (executable scripts, styles, SVG and comments
    removed, then data scripts other than JSON-LD, then the end of the body): the reduced page is what the
    model sees, what extractors are tested on and what a package keeps as its test fixture, so generated
    packages stay within ``transfer.inline_max_bytes``. JSON-LD is kept whole while it fits.
```

## jane_assistant.settings.MaterialLimits.head_share

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:233](../../../../../../services/assistant/src/jane_assistant/settings.py#L233).

```python
head_share: float = Field(default=0.1, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.1",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Share of a digest's characters for head tags (title, meta, canonical / next / prev links).
```

## jane_assistant.settings.MaterialLimits.structured_share

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:235](../../../../../../services/assistant/src/jane_assistant/settings.py#L235).

```python
structured_share: float = Field(default=0.6, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.6",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Share of a digest's characters for structured data (JSON-LD, microdata).
```

## jane_assistant.settings.MaterialLimits.text_share

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:237](../../../../../../services/assistant/src/jane_assistant/settings.py#L237).

```python
text_share: float = Field(default=0.15, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.15",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Share of a digest's characters for the visible text; the start of the body markup gets the rest (and
    whatever the other parts do not use).
```

## jane_assistant.settings.MaterialLimits.max_list_items

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:240](../../../../../../services/assistant/src/jane_assistant/settings.py#L240).

```python
max_list_items: int = Field(default=3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Items kept from every long list of structured data in a digest (the count of the rest is stated).
```

## jane_assistant.settings.MaterialLimits.max_string_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:242](../../../../../../services/assistant/src/jane_assistant/settings.py#L242).

```python
max_string_chars: int = Field(default=1000, ge=20)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "20"
}
```

### Опис із вихідного коду

```text
Longer strings of structured data are shortened in a digest (marked with the number of cut characters).
```

## jane_assistant.settings.MaterialLimits.short_string_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:244](../../../../../../services/assistant/src/jane_assistant/settings.py#L244).

```python
short_string_chars: int = Field(default=200, ge=20)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200",
  "ge": "20"
}
```

### Опис із вихідного коду

```text
Strings of structured data when even its first list items do not fit the structured share: lists then
    keep one item and strings this many characters.
```

## jane_assistant.settings.MaterialLimits.max_head_tags

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:247](../../../../../../services/assistant/src/jane_assistant/settings.py#L247).

```python
max_head_tags: int = Field(default=60, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Head tags (title, informative meta, canonical / next / prev links) in a digest.
```

## jane_assistant.settings.MaterialLimits.max_microdata_types

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:249](../../../../../../services/assistant/src/jane_assistant/settings.py#L249).

```python
max_microdata_types: int = Field(default=20, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "0"
}
```

## jane_assistant.settings.MaterialLimits.max_microdata_props

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:250](../../../../../../services/assistant/src/jane_assistant/settings.py#L250).

```python
max_microdata_props: int = Field(default=30, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Microdata item types and property names (most frequent first, with counts) in a digest.
```

## jane_assistant.settings.ImprovementLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:260](../../../../../../services/assistant/src/jane_assistant/settings.py#L260).

```python
class ImprovementLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_sample_chars](jane_assistant.settings.md#jane_assistantsettingsimprovementlimitsmax_sample_chars) | Поле | ні |
| [max_problem_samples](jane_assistant.settings.md#jane_assistantsettingsimprovementlimitsmax_problem_samples) | Поле | ні |
| [max_successful_examples](jane_assistant.settings.md#jane_assistantsettingsimprovementlimitsmax_successful_examples) | Поле | ні |
| [max_file_chars](jane_assistant.settings.md#jane_assistantsettingsimprovementlimitsmax_file_chars) | Поле | ні |
| [max_proposal_bytes](jane_assistant.settings.md#jane_assistantsettingsimprovementlimitsmax_proposal_bytes) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_assistant.settings.ImprovementLimits.max_sample_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:261](../../../../../../services/assistant/src/jane_assistant/settings.py#L261).

```python
max_sample_chars: int = Field(default=6000, ge=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "6000",
  "ge": "200"
}
```

## jane_assistant.settings.ImprovementLimits.max_problem_samples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:262](../../../../../../services/assistant/src/jane_assistant/settings.py#L262).

```python
max_problem_samples: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

## jane_assistant.settings.ImprovementLimits.max_successful_examples

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:263](../../../../../../services/assistant/src/jane_assistant/settings.py#L263).

```python
max_successful_examples: int = Field(default=5, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "0"
}
```

## jane_assistant.settings.ImprovementLimits.max_file_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:264](../../../../../../services/assistant/src/jane_assistant/settings.py#L264).

```python
max_file_chars: int = Field(default=20000, ge=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20000",
  "ge": "200"
}
```

### Опис із вихідного коду

```text
Package source file passed to the model (longer files are cut).
```

## jane_assistant.settings.ImprovementLimits.max_proposal_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:266](../../../../../../services/assistant/src/jane_assistant/settings.py#L266).

```python
max_proposal_bytes: int = Field(default=1048576, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1048576",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
``proposal_only``: size of the whole ``ImprovementResult.proposal`` as compact UTF-8 JSON (whenever its
    required part fits): code and schema files, then the diff (cut with a marker), then test fixtures; files that do
    not fit are named in ``omitted_files``.
```

## jane_assistant.settings.UnknownLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:272](../../../../../../services/assistant/src/jane_assistant/settings.py#L272).

```python
class UnknownLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_sample_chars](jane_assistant.settings.md#jane_assistantsettingsunknownlimitsmax_sample_chars) | Поле | ні |
| [min_confidence](jane_assistant.settings.md#jane_assistantsettingsunknownlimitsmin_confidence) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_assistant.settings.UnknownLimits.max_sample_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:273](../../../../../../services/assistant/src/jane_assistant/settings.py#L273).

```python
max_sample_chars: int = Field(default=6000, ge=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "6000",
  "ge": "200"
}
```

## jane_assistant.settings.UnknownLimits.min_confidence

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:274](../../../../../../services/assistant/src/jane_assistant/settings.py#L274).

```python
min_confidence: float = Field(default=0.6, ge=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0.6",
  "ge": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
Below this, the suggestion for an unknown material is ``none``.
```

## jane_assistant.settings.TransferLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:278](../../../../../../services/assistant/src/jane_assistant/settings.py#L278).

```python
class TransferLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [inline_max_bytes](jane_assistant.settings.md#jane_assistantsettingstransferlimitsinline_max_bytes) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_assistant.settings.TransferLimits.inline_max_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:279](../../../../../../services/assistant/src/jane_assistant/settings.py#L279).

```python
inline_max_bytes: int = contract_field('transfer.inline_max_bytes', 262144, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.inline_max_bytes'",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Package archives up to this size are sent to the runtime inline (base64).
```

## jane_assistant.settings.ContentLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:283](../../../../../../services/assistant/src/jane_assistant/settings.py#L283).

```python
class ContentLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_material_bytes](jane_assistant.settings.md#jane_assistantsettingscontentlimitsmax_material_bytes) | Поле | ні |
| [fetch_timeout_ms](jane_assistant.settings.md#jane_assistantsettingscontentlimitsfetch_timeout_ms) | Поле | ні |
| [connect_timeout_ms](jane_assistant.settings.md#jane_assistantsettingscontentlimitsconnect_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Reading material content (``ContentRef``) under ``blob_roots`` / ``download_host_allowlist``.
```

## jane_assistant.settings.ContentLimits.max_material_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:286](../../../../../../services/assistant/src/jane_assistant/settings.py#L286).

```python
max_material_bytes: int = Field(default=16777216, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "16777216",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Largest material content read (inline, file or download); larger is ``limit_exceeded``.
```

## jane_assistant.settings.ContentLimits.fetch_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:288](../../../../../../services/assistant/src/jane_assistant/settings.py#L288).

```python
fetch_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
The whole ``download_url`` download, connection included.
```

## jane_assistant.settings.ContentLimits.connect_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:290](../../../../../../services/assistant/src/jane_assistant/settings.py#L290).

```python
connect_timeout_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Establishing the connection of a ``download_url`` download.
```

## jane_assistant.settings.SearchLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:294](../../../../../../services/assistant/src/jane_assistant/settings.py#L294).

```python
class SearchLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [request_timeout_ms](jane_assistant.settings.md#jane_assistantsettingssearchlimitsrequest_timeout_ms) | Поле | ні |
| [connect_timeout_ms](jane_assistant.settings.md#jane_assistantsettingssearchlimitsconnect_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Calls of the ``http_json`` search provider.
```

## jane_assistant.settings.SearchLimits.request_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:297](../../../../../../services/assistant/src/jane_assistant/settings.py#L297).

```python
request_timeout_ms: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

## jane_assistant.settings.SearchLimits.connect_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:298](../../../../../../services/assistant/src/jane_assistant/settings.py#L298).

```python
connect_timeout_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

## jane_assistant.settings.LlmCallLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:301](../../../../../../services/assistant/src/jane_assistant/settings.py#L301).

```python
class LlmCallLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [request_timeout_ms](jane_assistant.settings.md#jane_assistantsettingsllmcalllimitsrequest_timeout_ms) | Поле | ні |
| [chars_per_token](jane_assistant.settings.md#jane_assistantsettingsllmcalllimitschars_per_token) | Поле | ні |
| [prompt_overhead_chars](jane_assistant.settings.md#jane_assistantsettingsllmcalllimitsprompt_overhead_chars) | Поле | ні |
| [part_overhead_chars](jane_assistant.settings.md#jane_assistantsettingsllmcalllimitspart_overhead_chars) | Поле | ні |
| [client_limits](jane_assistant.settings.md#jane_assistantsettingsllmcalllimitsclient_limits) | Метод | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Calls of the LLM gateway (internal). Other neighbours use ``clients.*`` - the platform's general
``timeouts.*`` / ``retries``, sized for short service calls; one model call can take minutes.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:82](../../../../../../services/assistant/tests/test_large_sites.py#L82).

```python
call = LlmCallLimits()
```

Контекст і передумови: [services/assistant/tests/test_large_sites.py:147](../../../../../../services/assistant/tests/test_large_sites.py#L147).

```python
budget = int(LlmLimits().max_input_tokens_per_request * LlmCallLimits().chars_per_token)
```

## jane_assistant.settings.LlmCallLimits.request_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:305](../../../../../../services/assistant/src/jane_assistant/settings.py#L305).

```python
request_timeout_ms: int = Field(default=900000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Timeout of one synchronous ``createCompletion``. It must cover the gateway's worst case: (schema retries
    + 1) x provider attempts x provider timeout + backoff - with the llm defaults 2 x 2 x 120 s = 8 min, with a
    platform profile's 3 attempts 12 min; 15 min is also the gateway's ``reservation_ttl_seconds`` (a call
    older than that is treated as crashed). Connection and retries come from ``clients.*``.
```

## jane_assistant.settings.LlmCallLimits.chars_per_token

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:311](../../../../../../services/assistant/src/jane_assistant/settings.py#L311).

```python
chars_per_token: float = Field(default=2.0, gt=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2.0",
  "gt": "0"
}
```

### Опис із вихідного коду

```text
Characters per token used to fit data into ``llm.max_input_tokens_per_request``. Keep it no larger than
    the gateway's own estimate (``gateway.chars_per_token_estimate``, 2.0 by default), otherwise the gateway
    refuses a full request with ``limit_exceeded``.
```

## jane_assistant.settings.LlmCallLimits.prompt_overhead_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:315](../../../../../../services/assistant/src/jane_assistant/settings.py#L315).

```python
prompt_overhead_chars: int = Field(default=2000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Characters reserved for the gateway's preamble around the instructions (the instructions are counted).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:87](../../../../../../services/assistant/tests/test_large_sites.py#L87).

```python
return len(request["instructions"]) + call.prompt_overhead_chars + parts
```

## jane_assistant.settings.LlmCallLimits.part_overhead_chars

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:317](../../../../../../services/assistant/src/jane_assistant/settings.py#L317).

```python
part_overhead_chars: int = Field(default=150, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "150",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Characters reserved for the delimiters of every data part (its name and media type are counted).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_large_sites.py:83](../../../../../../services/assistant/tests/test_large_sites.py#L83).

```python
parts = sum(
        len(p["text"]) + call.part_overhead_chars + len(p["name"]) + len(p.get("media_type", ""))
        for p in request["data"]
    )
```

## jane_assistant.settings.LlmCallLimits.client_limits

**Метод.** Код: [services/assistant/src/jane_assistant/settings.py:320](../../../../../../services/assistant/src/jane_assistant/settings.py#L320).

```python
def client_limits(self, clients: ClientLimits) -> ClientLimits:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `clients` | `ClientLimits` | `—` | positional-or-keyword |

Результат: `ClientLimits`.

## jane_assistant.settings.StateLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:324](../../../../../../services/assistant/src/jane_assistant/settings.py#L324).

```python
class StateLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pool_max_size](jane_assistant.settings.md#jane_assistantsettingsstatelimitspool_max_size) | Поле | ні |
| [connect_timeout_ms](jane_assistant.settings.md#jane_assistantsettingsstatelimitsconnect_timeout_ms) | Поле | ні |
| [in_progress_lease_ms](jane_assistant.settings.md#jane_assistantsettingsstatelimitsin_progress_lease_ms) | Поле | ні |
| [job_lease_ms](jane_assistant.settings.md#jane_assistantsettingsstatelimitsjob_lease_ms) | Поле | ні |
| [heartbeat_interval_ms](jane_assistant.settings.md#jane_assistantsettingsstatelimitsheartbeat_interval_ms) | Поле | ні |
| [session_retention_seconds](jane_assistant.settings.md#jane_assistantsettingsstatelimitssession_retention_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Shared PostgreSQL state (``state_dsn``).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_state.py:301](../../../../../../services/assistant/tests/test_state.py#L301).

```python
short = ServiceLimits(state=StateLimits(job_lease_ms=1))
```

Контекст і передумови: [services/assistant/tests/test_state.py:410](../../../../../../services/assistant/tests/test_state.py#L410).

```python
dead = PostgresState(own[0], own[1], ServiceLimits(state=StateLimits(job_lease_ms=1)), "dead")
```

## jane_assistant.settings.StateLimits.pool_max_size

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:327](../../../../../../services/assistant/src/jane_assistant/settings.py#L327).

```python
pool_max_size: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

## jane_assistant.settings.StateLimits.connect_timeout_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:328](../../../../../../services/assistant/src/jane_assistant/settings.py#L328).

```python
connect_timeout_ms: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

## jane_assistant.settings.StateLimits.in_progress_lease_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:329](../../../../../../services/assistant/src/jane_assistant/settings.py#L329).

```python
in_progress_lease_ms: int = Field(default=900000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
An in-progress idempotency claim of a crashed instance can be taken over after this.
```

## jane_assistant.settings.StateLimits.job_lease_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:331](../../../../../../services/assistant/src/jane_assistant/settings.py#L331).

```python
job_lease_ms: int = Field(default=60000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
A running job whose instance did not renew the lease for this long is marked ``failed``.
```

## jane_assistant.settings.StateLimits.heartbeat_interval_ms

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:333](../../../../../../services/assistant/src/jane_assistant/settings.py#L333).

```python
heartbeat_interval_ms: int = Field(default=15000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "15000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How often an instance renews the leases of its running jobs (keep well below job_lease_ms).
```

## jane_assistant.settings.StateLimits.session_retention_seconds

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:335](../../../../../../services/assistant/src/jane_assistant/settings.py#L335).

```python
session_retention_seconds: int = Field(default=2592000, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2592000",
  "ge": "60"
}
```

### Опис із вихідного коду

```text
Onboarding sessions not updated for this long are deleted (default 30 days).
```

## jane_assistant.settings.ServiceLimits

**Клас.** Код: [services/assistant/src/jane_assistant/settings.py:339](../../../../../../services/assistant/src/jane_assistant/settings.py#L339).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [state](jane_assistant.settings.md#jane_assistantsettingsservicelimitsstate) | Поле | ні |
| [llm](jane_assistant.settings.md#jane_assistantsettingsservicelimitsllm) | Поле | ні |
| [transfer](jane_assistant.settings.md#jane_assistantsettingsservicelimitstransfer) | Поле | ні |
| [onboarding](jane_assistant.settings.md#jane_assistantsettingsservicelimitsonboarding) | Поле | ні |
| [material](jane_assistant.settings.md#jane_assistantsettingsservicelimitsmaterial) | Поле | ні |
| [improvement](jane_assistant.settings.md#jane_assistantsettingsservicelimitsimprovement) | Поле | ні |
| [unknown](jane_assistant.settings.md#jane_assistantsettingsservicelimitsunknown) | Поле | ні |
| [content](jane_assistant.settings.md#jane_assistantsettingsservicelimitscontent) | Поле | ні |
| [search](jane_assistant.settings.md#jane_assistantsettingsservicelimitssearch) | Поле | ні |
| [clients](jane_assistant.settings.md#jane_assistantsettingsservicelimitsclients) | Поле | ні |
| [llm_call](jane_assistant.settings.md#jane_assistantsettingsservicelimitsllm_call) | Поле | ні |
| [pages](jane_assistant.settings.md#jane_assistantsettingsservicelimitspages) | Поле | ні |
| [jobs](jane_assistant.settings.md#jane_assistantsettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_assistant.settings.md#jane_assistantsettingsservicelimitsidempotency) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_lists.py:219](../../../../../../services/assistant/tests/test_lists.py#L219).

```python
state = InMemoryState(ServiceLimits())
```

Контекст і передумови: [services/assistant/tests/test_state.py:301](../../../../../../services/assistant/tests/test_state.py#L301).

```python
short = ServiceLimits(state=StateLimits(job_lease_ms=1))
```

## jane_assistant.settings.ServiceLimits.state

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:340](../../../../../../services/assistant/src/jane_assistant/settings.py#L340).

```python
state: StateLimits = StateLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.llm

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:341](../../../../../../services/assistant/src/jane_assistant/settings.py#L341).

```python
llm: LlmLimits = contract_field('llm', LlmLimits())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'llm'"
}
```

## jane_assistant.settings.ServiceLimits.transfer

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:342](../../../../../../services/assistant/src/jane_assistant/settings.py#L342).

```python
transfer: TransferLimits = TransferLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.onboarding

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:343](../../../../../../services/assistant/src/jane_assistant/settings.py#L343).

```python
onboarding: OnboardingLimits = OnboardingLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.material

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:344](../../../../../../services/assistant/src/jane_assistant/settings.py#L344).

```python
material: MaterialLimits = MaterialLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.improvement

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:345](../../../../../../services/assistant/src/jane_assistant/settings.py#L345).

```python
improvement: ImprovementLimits = ImprovementLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.unknown

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:346](../../../../../../services/assistant/src/jane_assistant/settings.py#L346).

```python
unknown: UnknownLimits = UnknownLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.content

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:347](../../../../../../services/assistant/src/jane_assistant/settings.py#L347).

```python
content: ContentLimits = ContentLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.search

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:348](../../../../../../services/assistant/src/jane_assistant/settings.py#L348).

```python
search: SearchLimits = SearchLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.clients

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:349](../../../../../../services/assistant/src/jane_assistant/settings.py#L349).

```python
clients: ClientLimits = ClientLimits()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Calls of the neighbours: contract ``timeouts.connect_timeout_ms`` / ``request_timeout_ms`` and ``retries``
    (a platform profile sets them); the LLM gateway's request timeout is ``llm_call`` instead.
```

## jane_assistant.settings.ServiceLimits.llm_call

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:352](../../../../../../services/assistant/src/jane_assistant/settings.py#L352).

```python
llm_call: LlmCallLimits = LlmCallLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.pages

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:353](../../../../../../services/assistant/src/jane_assistant/settings.py#L353).

```python
pages: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Cursor pages of ``listOnboardingSessions`` / ``listImprovementRuns``: default and largest ``limit``.
```

## jane_assistant.settings.ServiceLimits.jobs

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:355](../../../../../../services/assistant/src/jane_assistant/settings.py#L355).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.ServiceLimits.idempotency

**Поле.** Код: [services/assistant/src/jane_assistant/settings.py:356](../../../../../../services/assistant/src/jane_assistant/settings.py#L356).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_assistant.settings.resolve_service_limits

**Функція.** Код: [services/assistant/src/jane_assistant/settings.py:359](../../../../../../services/assistant/src/jane_assistant/settings.py#L359).

```python
def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `extra` | `LimitLayer` | `—` | var-positional |

Результат: `ResolvedLimits[ServiceLimits]`.

### Опис із вихідного коду

```text
Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_ASSISTANT_LIMITS__*`` <- ``extra``.

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
the assistant does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_content_policy.py:214](../../../../../../services/assistant/tests/test_content_policy.py#L214).

```python
provider = build_search(s, resolve_service_limits(s).limits)
```

Контекст і передумови: [services/assistant/tests/test_limits_profile.py:47](../../../../../../services/assistant/tests/test_limits_profile.py#L47).

```python
resolved = resolve_service_limits(settings)
```

## jane_assistant.settings.request_layer

**Функція.** Код: [services/assistant/src/jane_assistant/settings.py:367](../../../../../../services/assistant/src/jane_assistant/settings.py#L367).

```python
def request_layer(llm_limits: dict[str, Any] | None) -> list[LimitLayer]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `llm_limits` | `dict[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `list[LimitLayer]`.

### Опис із вихідного коду

```text
Contract ``limits.llm`` from a request as a ``request`` layer (empty list if absent).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_limits_profile.py:72](../../../../../../services/assistant/tests/test_limits_profile.py#L72).

```python
lim = resolve_service_limits(settings, *request_layer({"max_output_tokens_per_request": 100_000})).limits
```

Контекст і передумови: [services/assistant/tests/test_limits_profile.py:80](../../../../../../services/assistant/tests/test_limits_profile.py#L80).

```python
resolve_service_limits(settings, *request_layer({"max_onboarding_sample": 4}))
```
