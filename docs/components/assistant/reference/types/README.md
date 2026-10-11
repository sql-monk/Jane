# Типи й члени: Assistant

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant](../../../../../services/assistant/src/jane_assistant). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_assistant`](jane_assistant.md) | 0 | 0 | Assistant of the Jane platform. |
| [`jane_assistant.__main__`](jane_assistant.__main__.md) | 0 | 1 | Entry point: ``python -m jane_assistant`` (host/port from ``JANE_ASSISTANT_HOST/PORT``). |
| [`jane_assistant.app`](jane_assistant.app.md) | 11 | 3 | HTTP API of the source assistant (``contracts/openapi/assistant.v1.yaml``). |
| [`jane_assistant.clients`](jane_assistant.clients.md) | 1 | 1 | Clients of neighbour services, strictly by their contracts (``contracts/openapi/*.v1.yaml``). |
| [`jane_assistant.content`](jane_assistant.content.md) | 2 | 6 | Material content helpers: read ``ContentRef`` (inline / blob) under the ContentRef policy, URL shapes, truncation. |
| [`jane_assistant.guards`](jane_assistant.guards.md) | 3 | 2 | Guards against untrusted model output (ТЗ §11: source content is data, not instructions). |
| [`jane_assistant.improvement`](jane_assistant.improvement.md) | 2 | 4 | Improvement of an extractor on problem samples (ТЗ §9, plan.md WP-11 «Вдосконалення»). |
| [`jane_assistant.listing`](jane_assistant.listing.md) | 0 | 4 | Positions and cursors of the list operations (``listOnboardingSessions``, ``listImprovementRuns``). |
| [`jane_assistant.llm`](jane_assistant.llm.md) | 3 | 1 | LLM calls of one assistant job: trusted instructions, untrusted data, budget and size limits. |
| [`jane_assistant.material`](jane_assistant.material.md) | 0 | 15 | Large HTML materials: what the model sees and what tests run on. |
| [`jane_assistant.onboarding`](jane_assistant.onboarding.md) | 4 | 0 | Onboarding of a new source (ТЗ §8, §13.1 п.2, plan.md WP-11 «Підключення»). |
| [`jane_assistant.packages`](jane_assistant.packages.md) | 1 | 5 | Package drafts built by the assistant (``jane-handler-package`` skill, ``package-manifest.schema.json``). |
| [`jane_assistant.prompts`](jane_assistant.prompts.md) | 0 | 0 | Trusted instructions and output schemas of every LLM step of the assistant. |
| [`jane_assistant.sampling`](jane_assistant.sampling.md) | 3 | 3 | Adaptive sampling of a source (ТЗ §8: no fixed sample size; stop at sufficient confidence or report an insufficient sample within the budget). |
| [`jane_assistant.search`](jane_assistant.search.md) | 5 | 2 | Source search: turn a site/channel name into candidates (plan.md WP-11, ТЗ §8, §13.1 п.2). |
| [`jane_assistant.settings`](jane_assistant.settings.md) | 13 | 2 | Settings and limits of the assistant. Every limit has a safe default documented in README.md. |
| [`jane_assistant.state`](jane_assistant.state.md) | 3 | 0 | State of the assistant shared by instances: onboarding sessions, jobs and idempotency keys. |
| [`jane_assistant.testing`](jane_assistant.testing.md) | 1 | 2 | Running package tests through handler-runtime (``handler.v1`` ``POST /v1/test-runs``). |
| [`jane_assistant.unknown`](jane_assistant.unknown.md) | 1 | 1 | Analysis of an unknown material (ТЗ §8, criterion 11). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`AcceptanceRequest`](jane_assistant.app.md#клас-acceptancerequest) | клас | `jane_assistant.app` |
| [`BindingRef`](jane_assistant.app.md#клас-bindingref) | клас | `jane_assistant.app` |
| [`Budget`](jane_assistant.settings.md#клас-budget) | клас | `jane_assistant.settings` |
| [`BudgetExhausted`](jane_assistant.llm.md#клас-budgetexhausted) | виняток | `jane_assistant.llm` |
| [`build_app`](jane_assistant.app.md#функція-build_app) | функція | `jane_assistant.app` |
| [`build_search`](jane_assistant.app.md#функція-build_search) | функція | `jane_assistant.app` |
| [`build_state`](jane_assistant.app.md#функція-build_state) | функція | `jane_assistant.app` |
| [`bump`](jane_assistant.packages.md#функція-bump) | функція | `jane_assistant.packages` |
| [`Candidate`](jane_assistant.search.md#клас-candidate) | dataclass (незмінний) | `jane_assistant.search` |
| [`CandidateSelection`](jane_assistant.app.md#клас-candidateselection) | клас | `jane_assistant.app` |
| [`case_name`](jane_assistant.packages.md#функція-case_name) | функція | `jane_assistant.packages` |
| [`check_code`](jane_assistant.guards.md#функція-check_code) | функція | `jane_assistant.guards` |
| [`CodeCheck`](jane_assistant.guards.md#клас-codecheck) | dataclass | `jane_assistant.guards` |
| [`collector_rules_draft`](jane_assistant.packages.md#функція-collector_rules_draft) | функція | `jane_assistant.packages` |
| [`ContentLimits`](jane_assistant.settings.md#клас-contentlimits) | клас | `jane_assistant.settings` |
| [`coverage`](jane_assistant.sampling.md#функція-coverage) | функція | `jane_assistant.sampling` |
| [`declared_canonical`](jane_assistant.material.md#функція-declared_canonical) | функція | `jane_assistant.material` |
| [`decode_position`](jane_assistant.listing.md#функція-decode_position) | функція | `jane_assistant.listing` |
| [`decode_text`](jane_assistant.content.md#функція-decode_text) | функція | `jane_assistant.content` |
| [`Dependencies`](jane_assistant.app.md#клас-dependencies) | dataclass | `jane_assistant.app` |
| [`direct_candidate`](jane_assistant.search.md#функція-direct_candidate) | функція | `jane_assistant.search` |
| [`empty_shell`](jane_assistant.material.md#функція-empty_shell) | функція | `jane_assistant.material` |
| [`encode_position`](jane_assistant.listing.md#функція-encode_position) | функція | `jane_assistant.listing` |
| [`Evidence`](jane_assistant.sampling.md#клас-evidence) | dataclass | `jane_assistant.sampling` |
| [`extra_case`](jane_assistant.testing.md#функція-extra_case) | функція | `jane_assistant.testing` |
| [`extractor_draft`](jane_assistant.packages.md#функція-extractor_draft) | функція | `jane_assistant.packages` |
| [`FlagOff`](jane_assistant.unknown.md#клас-flagoff) | виняток | `jane_assistant.unknown` |
| [`group_problems`](jane_assistant.improvement.md#функція-group_problems) | функція | `jane_assistant.improvement` |
| [`host_of`](jane_assistant.content.md#функція-host_of) | функція | `jane_assistant.content` |
| [`html_digest`](jane_assistant.material.md#функція-html_digest) | функція | `jane_assistant.material` |
| [`HttpJsonSearchProvider`](jane_assistant.search.md#клас-httpjsonsearchprovider) | клас | `jane_assistant.search` |
| [`idem_key`](jane_assistant.clients.md#функція-idem_key) | функція | `jane_assistant.clients` |
| [`improve_draft`](jane_assistant.improvement.md#функція-improve_draft) | функція | `jane_assistant.improvement` |
| [`ImprovementLimits`](jane_assistant.settings.md#клас-improvementlimits) | клас | `jane_assistant.settings` |
| [`ImprovementRequest`](jane_assistant.app.md#клас-improvementrequest) | клас | `jane_assistant.app` |
| [`ImproveOutcome`](jane_assistant.improvement.md#клас-improveoutcome) | dataclass | `jane_assistant.improvement` |
| [`inline_bytes`](jane_assistant.material.md#функція-inline_bytes) | функція | `jane_assistant.material` |
| [`inline_text`](jane_assistant.material.md#функція-inline_text) | функція | `jane_assistant.material` |
| [`InMemorySessionStore`](jane_assistant.onboarding.md#клас-inmemorysessionstore) | клас | `jane_assistant.onboarding` |
| [`InMemoryState`](jane_assistant.state.md#клас-inmemorystate) | клас | `jane_assistant.state` |
| [`InvalidModelOutput`](jane_assistant.llm.md#клас-invalidmodeloutput) | виняток | `jane_assistant.llm` |
| [`is_html`](jane_assistant.material.md#функція-is_html) | функція | `jane_assistant.material` |
| [`lean_html`](jane_assistant.material.md#функція-lean_html) | функція | `jane_assistant.material` |
| [`link_pattern`](jane_assistant.material.md#функція-link_pattern) | функція | `jane_assistant.material` |
| [`LlmCallLimits`](jane_assistant.settings.md#клас-llmcalllimits) | клас | `jane_assistant.settings` |
| [`LlmLimits`](jane_assistant.settings.md#клас-llmlimits) | клас | `jane_assistant.settings` |
| [`LlmSession`](jane_assistant.llm.md#клас-llmsession) | dataclass | `jane_assistant.llm` |
| [`main`](jane_assistant.__main__.md#функція-main) | функція | `jane_assistant.__main__` |
| [`material_bytes`](jane_assistant.content.md#функція-material_bytes) | функція | `jane_assistant.content` |
| [`material_label`](jane_assistant.content.md#функція-material_label) | функція | `jane_assistant.content` |
| [`material_text`](jane_assistant.material.md#функція-material_text) | функція | `jane_assistant.material` |
| [`MaterialContent`](jane_assistant.content.md#клас-materialcontent) | dataclass (незмінний) | `jane_assistant.content` |
| [`MaterialContentScope`](jane_assistant.content.md#клас-materialcontentscope) | клас | `jane_assistant.content` |
| [`MaterialLimits`](jane_assistant.settings.md#клас-materiallimits) | клас | `jane_assistant.settings` |
| [`MaterialRef`](jane_assistant.app.md#клас-materialref) | клас | `jane_assistant.app` |
| [`Neighbours`](jane_assistant.clients.md#клас-neighbours) | dataclass | `jane_assistant.clients` |
| [`NoSearchProvider`](jane_assistant.search.md#клас-nosearchprovider) | клас | `jane_assistant.search` |
| [`now_text`](jane_assistant.listing.md#функція-now_text) | функція | `jane_assistant.listing` |
| [`OnboardingLimits`](jane_assistant.settings.md#клас-onboardinglimits) | клас | `jane_assistant.settings` |
| [`OnboardingRequest`](jane_assistant.app.md#клас-onboardingrequest) | клас | `jane_assistant.app` |
| [`OnboardingService`](jane_assistant.onboarding.md#клас-onboardingservice) | клас | `jane_assistant.onboarding` |
| [`outside_blocks`](jane_assistant.material.md#функція-outside_blocks) | функція | `jane_assistant.material` |
| [`PackageDraft`](jane_assistant.packages.md#клас-packagedraft) | dataclass | `jane_assistant.packages` |
| [`PackageRef`](jane_assistant.app.md#клас-packageref) | клас | `jane_assistant.app` |
| [`page_links`](jane_assistant.material.md#функція-page_links) | функція | `jane_assistant.material` |
| [`pagination_templates`](jane_assistant.material.md#функція-pagination_templates) | функція | `jane_assistant.material` |
| [`parse_time`](jane_assistant.listing.md#функція-parse_time) | функція | `jane_assistant.listing` |
| [`part`](jane_assistant.llm.md#функція-part) | функція | `jane_assistant.llm` |
| [`Policy`](jane_assistant.app.md#клас-policy) | клас | `jane_assistant.app` |
| [`PostgresState`](jane_assistant.state.md#клас-postgresstate) | клас | `jane_assistant.state` |
| [`ProblemCase`](jane_assistant.improvement.md#клас-problemcase) | dataclass | `jane_assistant.improvement` |
| [`ProblemSample`](jane_assistant.app.md#клас-problemsample) | клас | `jane_assistant.app` |
| [`reduce_material`](jane_assistant.material.md#функція-reduce_material) | функція | `jane_assistant.material` |
| [`request_layer`](jane_assistant.settings.md#функція-request_layer) | функція | `jane_assistant.settings` |
| [`resolve_service_limits`](jane_assistant.settings.md#функція-resolve_service_limits) | функція | `jane_assistant.settings` |
| [`RulesCheck`](jane_assistant.guards.md#клас-rulescheck) | dataclass | `jane_assistant.guards` |
| [`run_improvement`](jane_assistant.improvement.md#функція-run_improvement) | функція | `jane_assistant.improvement` |
| [`run_tests`](jane_assistant.testing.md#функція-run_tests) | функція | `jane_assistant.testing` |
| [`run_unknown`](jane_assistant.unknown.md#функція-run_unknown) | функція | `jane_assistant.unknown` |
| [`same_url`](jane_assistant.material.md#функція-same_url) | функція | `jane_assistant.material` |
| [`Sample`](jane_assistant.sampling.md#клас-sample) | dataclass | `jane_assistant.sampling` |
| [`sample_source`](jane_assistant.sampling.md#функція-sample_source) | функція | `jane_assistant.sampling` |
| [`SampleResult`](jane_assistant.sampling.md#клас-sampleresult) | dataclass | `jane_assistant.sampling` |
| [`sampling_rules`](jane_assistant.sampling.md#функція-sampling_rules) | функція | `jane_assistant.sampling` |
| [`sanitize_web_rules`](jane_assistant.guards.md#функція-sanitize_web_rules) | функція | `jane_assistant.guards` |
| [`SchemaValidator`](jane_assistant.guards.md#клас-schemavalidator) | клас | `jane_assistant.guards` |
| [`score`](jane_assistant.search.md#функція-score) | функція | `jane_assistant.search` |
| [`SearchLimits`](jane_assistant.settings.md#клас-searchlimits) | клас | `jane_assistant.settings` |
| [`SearchProvider`](jane_assistant.search.md#клас-searchprovider) | протокол | `jane_assistant.search` |
| [`ServiceLimits`](jane_assistant.settings.md#клас-servicelimits) | клас | `jane_assistant.settings` |
| [`ServiceState`](jane_assistant.state.md#клас-servicestate) | протокол | `jane_assistant.state` |
| [`Session`](jane_assistant.onboarding.md#клас-session) | dataclass | `jane_assistant.onboarding` |
| [`SessionStore`](jane_assistant.onboarding.md#клас-sessionstore) | протокол | `jane_assistant.onboarding` |
| [`Settings`](jane_assistant.settings.md#клас-settings) | модель Pydantic | `jane_assistant.settings` |
| [`signature_of`](jane_assistant.improvement.md#функція-signature_of) | функція | `jane_assistant.improvement` |
| [`slug`](jane_assistant.packages.md#функція-slug) | функція | `jane_assistant.packages` |
| [`StateLimits`](jane_assistant.settings.md#клас-statelimits) | клас | `jane_assistant.settings` |
| [`StaticSearchProvider`](jane_assistant.search.md#клас-staticsearchprovider) | клас | `jane_assistant.search` |
| [`TestOutcome`](jane_assistant.testing.md#клас-testoutcome) | dataclass | `jane_assistant.testing` |
| [`TransferLimits`](jane_assistant.settings.md#клас-transferlimits) | клас | `jane_assistant.settings` |
| [`truncate`](jane_assistant.content.md#функція-truncate) | функція | `jane_assistant.content` |
| [`UnknownLimits`](jane_assistant.settings.md#клас-unknownlimits) | клас | `jane_assistant.settings` |
| [`UnknownMaterialRequest`](jane_assistant.app.md#клас-unknownmaterialrequest) | клас | `jane_assistant.app` |
| [`url_shape`](jane_assistant.content.md#функція-url_shape) | функція | `jane_assistant.content` |
| [`with_content`](jane_assistant.material.md#функція-with_content) | функція | `jane_assistant.material` |
