# api/generated/assistant

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.assistant.paths](#adminapigeneratedassistantpaths)
- [admin.api.generated.assistant.paths./v1/health](#adminapigeneratedassistantpathsv1health)
- [admin.api.generated.assistant.paths./v1/info](#adminapigeneratedassistantpathsv1info)
- [admin.api.generated.assistant.paths./v1/onboarding-sessions](#adminapigeneratedassistantpathsv1onboarding-sessions)
- [admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}](#adminapigeneratedassistantpathsv1onboarding-sessionssession_id)
- [admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}/candidate-selection](#adminapigeneratedassistantpathsv1onboarding-sessionssession_idcandidate-selection)
- [admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance](#adminapigeneratedassistantpathsv1onboarding-sessionssession_idproposalsproposal_idacceptance)
- [admin.api.generated.assistant.paths./v1/improvement-runs](#adminapigeneratedassistantpathsv1improvement-runs)
- [admin.api.generated.assistant.paths./v1/unknown-materials](#adminapigeneratedassistantpathsv1unknown-materials)
- [admin.api.generated.assistant.paths./v1/jobs/{job_id}](#adminapigeneratedassistantpathsv1jobsjob_id)
- [admin.api.generated.assistant.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedassistantpathsv1jobsjob_idcancel)
- [admin.api.generated.assistant.webhooks](#adminapigeneratedassistantwebhooks)
- [admin.api.generated.assistant.components](#adminapigeneratedassistantcomponents)
- [admin.api.generated.assistant.components.schemas](#adminapigeneratedassistantcomponentsschemas)
- [admin.api.generated.assistant.components.responses](#adminapigeneratedassistantcomponentsresponses)
- [admin.api.generated.assistant.components.parameters](#adminapigeneratedassistantcomponentsparameters)
- [admin.api.generated.assistant.components.requestBodies](#adminapigeneratedassistantcomponentsrequestbodies)
- [admin.api.generated.assistant.components.headers](#adminapigeneratedassistantcomponentsheaders)
- [admin.api.generated.assistant.components.pathItems](#adminapigeneratedassistantcomponentspathitems)
- [admin.api.generated.assistant.$defs](#adminapigeneratedassistantdefs)
- [admin.api.generated.assistant.operations](#adminapigeneratedassistantoperations)
- [admin.api.generated.assistant.operations.getHealth](#adminapigeneratedassistantoperationsgethealth)
- [admin.api.generated.assistant.operations.getServiceInfo](#adminapigeneratedassistantoperationsgetserviceinfo)
- [admin.api.generated.assistant.operations.listOnboardingSessions](#adminapigeneratedassistantoperationslistonboardingsessions)
- [admin.api.generated.assistant.operations.startOnboarding](#adminapigeneratedassistantoperationsstartonboarding)
- [admin.api.generated.assistant.operations.getOnboardingSession](#adminapigeneratedassistantoperationsgetonboardingsession)
- [admin.api.generated.assistant.operations.selectCandidate](#adminapigeneratedassistantoperationsselectcandidate)
- [admin.api.generated.assistant.operations.acceptProposal](#adminapigeneratedassistantoperationsacceptproposal)
- [admin.api.generated.assistant.operations.listImprovementRuns](#adminapigeneratedassistantoperationslistimprovementruns)
- [admin.api.generated.assistant.operations.startImprovement](#adminapigeneratedassistantoperationsstartimprovement)
- [admin.api.generated.assistant.operations.analyzeUnknownMaterial](#adminapigeneratedassistantoperationsanalyzeunknownmaterial)
- [admin.api.generated.assistant.operations.getJob](#adminapigeneratedassistantoperationsgetjob)
- [admin.api.generated.assistant.operations.cancelJob](#adminapigeneratedassistantoperationscanceljob)

## admin.api.generated.assistant.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/assistant.ts:3](../../../../../../web/admin/src/api/generated/assistant.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.assistant.md#adminapigeneratedassistantpathsv1health) | Поле | ні |
| [/v1/info](api.generated.assistant.md#adminapigeneratedassistantpathsv1info) | Поле | ні |
| [/v1/onboarding-sessions](api.generated.assistant.md#adminapigeneratedassistantpathsv1onboarding-sessions) | Поле | ні |
| [/v1/onboarding-sessions/{session_id}](api.generated.assistant.md#adminapigeneratedassistantpathsv1onboarding-sessionssession_id) | Поле | ні |
| [/v1/onboarding-sessions/{session_id}/candidate-selection](api.generated.assistant.md#adminapigeneratedassistantpathsv1onboarding-sessionssession_idcandidate-selection) | Поле | ні |
| [/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance](api.generated.assistant.md#adminapigeneratedassistantpathsv1onboarding-sessionssession_idproposalsproposal_idacceptance) | Поле | ні |
| [/v1/improvement-runs](api.generated.assistant.md#adminapigeneratedassistantpathsv1improvement-runs) | Поле | ні |
| [/v1/unknown-materials](api.generated.assistant.md#adminapigeneratedassistantpathsv1unknown-materials) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.assistant.md#adminapigeneratedassistantpathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.assistant.md#adminapigeneratedassistantpathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.assistant.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:4](../../../../../../web/admin/src/api/generated/assistant.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:21](../../../../../../web/admin/src/api/generated/assistant.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/onboarding-sessions

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:38](../../../../../../web/admin/src/api/generated/assistant.ts#L38).

```typescript
/v1/onboarding-sessions: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listOnboardingSessions"]; put?: never; post: operations["startOnboarding"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:70](../../../../../../web/admin/src/api/generated/assistant.ts#L70).

```typescript
/v1/onboarding-sessions/{session_id}: { parameters: { query?: never; header?: never; path: { session_id: components["parameters"]["SessionId"]; }; cookie?: never; }; get: operations["getOnboardingSession"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}/candidate-selection

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:89](../../../../../../web/admin/src/api/generated/assistant.ts#L89).

```typescript
/v1/onboarding-sessions/{session_id}/candidate-selection: { parameters: { query?: never; header?: never; path: { session_id: components["parameters"]["SessionId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["selectCandidate"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:108](../../../../../../web/admin/src/api/generated/assistant.ts#L108).

```typescript
/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance: { parameters: { query?: never; header?: never; path: { session_id: components["parameters"]["SessionId"]; proposal_id: string; }; cookie?: never; }; get?: never; put?: never; post: operations["acceptProposal"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/improvement-runs

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:133](../../../../../../web/admin/src/api/generated/assistant.ts#L133).

```typescript
/v1/improvement-runs: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listImprovementRuns"]; put?: never; post: operations["startImprovement"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/unknown-materials

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:165](../../../../../../web/admin/src/api/generated/assistant.ts#L165).

```typescript
/v1/unknown-materials: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["analyzeUnknownMaterial"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:182](../../../../../../web/admin/src/api/generated/assistant.ts#L182).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:206](../../../../../../web/admin/src/api/generated/assistant.ts#L206).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.webhooks

**Тип.** Код: [web/admin/src/api/generated/assistant.ts:231](../../../../../../web/admin/src/api/generated/assistant.ts#L231).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.assistant.components

**Інтерфейс.** Код: [web/admin/src/api/generated/assistant.ts:232](../../../../../../web/admin/src/api/generated/assistant.ts#L232).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.assistant.md#adminapigeneratedassistantcomponentsschemas) | Поле | ні |
| [responses](api.generated.assistant.md#adminapigeneratedassistantcomponentsresponses) | Поле | ні |
| [parameters](api.generated.assistant.md#adminapigeneratedassistantcomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.assistant.md#adminapigeneratedassistantcomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.assistant.md#adminapigeneratedassistantcomponentsheaders) | Поле | ні |
| [pathItems](api.generated.assistant.md#adminapigeneratedassistantcomponentspathitems) | Поле | ні |

## admin.api.generated.assistant.components.schemas

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:233](../../../../../../web/admin/src/api/generated/assistant.ts#L233).

```typescript
schemas: { OnboardingRequest: { query: string; source_kind?: components["schemas"]["SourceKind"]; expected_entity_types?: string[]; crawl_hints?: Record<string, unknown>; limits?: components["schemas"]["llm"]; auto_activation?: boolean; }; SourceCandidate: { candidate_id: string; title: string; url?: string; telegram_username?: string; description?: string; confidence?: number; }; FieldInfo: { name: string; type?: string; examples?: unknown[]; coverage?: number; }; SourceAnalysis: { source_kind?: string; discovery_methods?: string[]; material_types?: { type: string; count: number; example_urls?: string[]; }[]; entities?: { entity_type: string; fields: components["schemas"]["FieldInfo"][]; }[]; }; ExtractorPlan: { entity_type: string; action: "bind_existing" | "fork" | "create"; package?: components["schemas"]["package-ref.schema"]; match_score?: number; tested_on_samples?: { passed?: number; failed?: number; }; }; Proposal: { proposal_id: string; title: string; summary?: string; recommended?: boolean; collector_rules: components["schemas"]["collector-rules.schema"]; extractors: components["schemas"]["ExtractorPlan"][]; coverage?: { estimated_materials?: number; entity_types?: string[]; notes?: string; }; cost?: { requests_per_run_estimate?: number; llm_setup_cost?: components["schemas"]["Money"]; llm_cost_per_run?: components["schemas"]["Money"]; }; risks?: string[]; }; OnboardingStatus: "resolving" | "needs_disambiguation" | "sampling" | "analyzing" | "proposals_ready" | "insufficient_sample" | "applying" | "completed" | "failed" | "cancelled"; OnboardingSessionSummary: { session_id: components["schemas"]["Id"]; status: components["schemas"]["OnboardingStatus"]; query: string; selected_candidate_id?: string; proposal_count?: number; costs?: components["schemas"]["Money"]; job_id?: string; created_at: components["schemas"]["Timestamp"]; error?: components["schemas"]["problem.schema"]; }; OnboardingSessionList: { items: components["schemas"]["OnboardingSessionSummary"][]; next_cursor: components["schemas"]["NextCursor"]; }; OnboardingSession: { session_id: components["schemas"]["Id"]; status: components["schemas"]["OnboardingStatus"]; query: string; candidates?: components["schemas"]["SourceCandidate"][]; selected_candidate_id?: string; sample?: { materials?: number; distinct_types?: number; confidence?: number; sufficient?: boolean; message?: string; }; analysis?: components["schemas"]["SourceAnalysis"]; proposals?: components["schemas"]["Proposal"][]; costs?: components["schemas"]["Money"]; job_id?: string; created_at: components["schemas"]["Timestamp"]; error?: components["schemas"]["problem.schema"]; }; AcceptanceResult: { collector_rules: components["schemas"]["package-ref.schema"]; extractors: { action: "bind_existing" | "fork" | "create"; package: components["schemas"]["package-ref.schema"]; test_report?: components["schemas"]["TestReport"]; }[]; source_draft?: components["schemas"]["source.schema"]; task_drafts?: components["schemas"]["task-config.schema"][]; activated?: boolean; }; MaterialRef: { storage_connection_id: string; object_id: string; }; ProblemSample: { material?: components["schemas"]["material.schema"]; material_ref?: components["schemas"]["MaterialRef"]; result?: components["schemas"]["handler-result.schema"]; diagnostics?: components["schemas"]["DiagnosticMessage"][]; } | unknown | unknown; ImprovementRequest: { package: components["schemas"]["package-ref.schema"]; source_id?: string; problem_group_id?: string; problem_samples: components["schemas"]["ProblemSample"][]; successful_examples?: components["schemas"]["ProblemSample"][]; bindings?: { task_id: string; stage_id: string; }[]; policy?: { approval?: "manual" | "auto_after_checks"; allow_fork?: boolean; }; limits?: components["schemas"]["llm"]; }; ImprovementResult: { outcome: "new_version" | "fork_created" | "proposal_only" | "unresolved"; version?: components["schemas"]["package-ref.schema"]; attempts?: number; test_reports?: { context?: string; report?: components["schemas"]["TestReport"]; }[]; activated?: boolean; unresolved_reason?: string; suggested_entity_types?: string[]; costs?: components["schemas"]["Money"]; proposal?: components["schemas"]["ImprovementProposal"]; }; ImprovementProposal: { based_on: components["schemas"]["package-ref.schema"]; version: string; schema_change?: "none" | "additive" | "breaking"; change_summary?: string; manifest: components["schemas"]["package-manifest.schema"]; files: { [key: string]: { encoding: "utf-8" | "base64"; data: string; }; }; omitted_files?: string[]; diff?: string; }; UnknownMaterialRequest: { source_id: string; task_id?: string; forward_unknown_to_llm: boolean; material: components["schemas"]["material.schema"]; limits?: components["schemas"]["llm"]; }; UnknownMaterialResult: { classification: { material_type?: string; confidence?: number; }; suggestion: { action: "none" | "new_extractor" | "extend_rules" | "expand_entity_types"; details?: string; onboarding_session_id?: string; }; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; Id: string; Money: { amount: number; currency: string; }; Timestamp: string; NextCursor: string | null; SourceKind: string; llm: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; MediaType: string; Sha256Hex: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; Labels: { [key: string]: string; }; UrlPattern: { type?: "glob" | "regex"; value: string; }; WebScope: { allowed_domains: string[]; include_subdomains?: boolean; allowed_schemes?: ("http" | "https")[]; path_prefixes?: string[]; include?: components["schemas"]["UrlPattern"][]; exclude?: components["schemas"]["UrlPattern"][]; }; Slug: string; StrategyCommon: { strategy_id?: components["schemas"]["Slug"]; priority?: number; section?: components["schemas"]["Slug"]; limits?: components["schemas"]["limits.schema"]; }; SeedListStrategy: { type: "seed_list"; urls: string[]; } & (components["schemas"]["StrategyCommon"] & { type: "seed_list"; }); RecursiveStrategy: { type: "recursive"; seeds?: string[]; follow?: components["schemas"]["UrlPattern"][]; link_sources?: ("a_href" | "link_rel" | "canonical" | "pagination_rel")[]; } & (components["schemas"]["StrategyCommon"] & { type: "recursive"; }); SitemapStrategy: { type: "sitemap"; urls?: string[]; use_robots_txt?: boolean; lastmod_since?: components["schemas"]["Timestamp"]; use_lastmod_for_revisit?: boolean; } & (components["schemas"]["StrategyCommon"] & { type: "sitemap"; }); FeedStrategy: { type: "feed"; urls?: string[]; autodiscover?: boolean; } & (components["schemas"]["StrategyCommon"] & { type: "feed"; }); Selector: { type?: "css" | "xpath" | "rel"; value: string; attribute?: string; }; ListingStrategy: { type: "listing"; start_urls: string[]; item_links?: components["schemas"]["Selector"]; next_page?: components["schemas"]["Selector"]; page_param?: { name: string; start?: number; step?: number; stop_when_empty?: boolean; }; search?: { url_template: string; queries: string[]; }; } & (components["schemas"]["StrategyCommon"] & { type: "listing"; }); UrlTemplateStrategy: { type: "url_template"; template: string; variables: { [key: string]: { range: { start: number; end: number; step?: number; }; } | { values: (string | number)[]; }; }; stop_after_consecutive_misses?: number; } & (components["schemas"]["StrategyCommon"] & { type: "url_template"; }); ApiFeedStrategy: { type: "api_feed"; url: string; method?: "GET" | "POST"; body?: unknown; items_path: string; url_path: string; lastmod_path?: string; emit_items_as_materials?: boolean; pagination?: { type?: "none" | "next_url" | "cursor" | "page"; next_url_path?: string; cursor_path?: string; cursor_param?: string; page_param?: string; }; } & (components["schemas"]["StrategyCommon"] & { type: "api_feed"; }); LlmExploreStrategy: { type: "llm_explore"; goal?: string; expected_entity_types?: string[]; } & (components["schemas"]["StrategyCommon"] & { type: "llm_explore"; }); Strategy: components["schemas"]["SeedListStrategy"] | components["schemas"]["RecursiveStrategy"] | components["schemas"]["SitemapStrategy"] | components["schemas"]["FeedStrategy"] | components["schemas"]["ListingStrategy"] | components["schemas"]["UrlTemplateStrategy"] | components["schemas"]["ApiFeedStrategy"] | components["schemas"]["LlmExploreStrategy"]; RobotsPolicy: { mode?: "respect" | "owner_policy"; user_agent_token?: string; owner_policy?: { confirmed_owner: true; justification: string; confirmed_by?: string; confirmed_at?: components["schemas"]["Timestamp"]; }; }; UrlNormalization: { remove_fragment?: boolean; lowercase_host?: boolean; sort_query?: boolean; strip_query_params?: string[]; trailing_slash?: "keep" | "add" | "remove"; }; WebRules: { collector: "web"; scope: components["schemas"]["WebScope"]; strategies: components["schemas"]["Strategy"][]; robots?: components["schemas"]["RobotsPolicy"]; normalization?: components["schemas"]["UrlNormalization"]; dedup?: { key?: "canonical_url" | "canonical_url_and_content"; use_link_rel_canonical?: boolean; }; priorities?: { pattern: components["schemas"]["UrlPattern"]; priority: number; }[]; sections?: { section_id: components["schemas"]["Slug"]; title?: string; patterns: components["schemas"]["UrlPattern"][]; }[]; fetch?: { user_agent?: string; headers?: { [key: string]: string; }; connection_id?: components["schemas"]["Slug"]; accept_media_types?: string[]; render_js?: boolean; }; revisit?: { mode?: "never" | "interval" | "if_changed"; }; limits?: components["schemas"]["limits.schema"]; }; TelegramRules: { collector: "telegram"; channels: ({ username?: string; channel_id?: string; } | unknown | unknown)[]; history?: { enabled?: boolean; since?: components["schemas"]["Timestamp"]; from_message_id?: number; }; updates?: { new_messages?: boolean; edits?: boolean; }; media?: { download?: boolean; kinds?: ("photo" | "document" | "video" | "audio")[]; }; account_connection_id?: components["schemas"]["Slug"]; limits?: components["schemas"]["limits.schema"]; }; "collector-rules.schema": {} & (components["schemas"]["WebRules"] | components["schemas"]["TelegramRules"]); SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; JobList: { items: components["schemas"]["job.schema"][]; next_cursor: components["schemas"]["NextCursor"]; }; DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; "material.schema": { material_id: components["schemas"]["Id"]; observation_id: components["schemas"]["Id"]; source: { source_id?: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; name?: string; }; locator: { url?: string; final_url?: string; canonical_url?: string; telegram?: { channel_id: string; channel_username?: string; message_id: number; grouped_id?: string; }; }; fetched_at: components["schemas"]["Timestamp"]; published_at?: components["schemas"]["Timestamp"]; edited_at?: components["schemas"]["Timestamp"]; format: { media_type: components["schemas"]["MediaType"]; charset?: string; language?: string; content_kind?: string; }; revision: { content_sha256: components["schemas"]["Sha256Hex"]; source_revision?: string; sequence?: number; is_edit?: boolean; }; content: components["schemas"]["content-ref.schema"]; attachments?: { name: string; role?: string; content: components["schemas"]["content-ref.schema"]; }[]; http?: { status?: number; headers?: { [key: string]: string; }; redirects?: string[]; }; discovery?: { strategy?: string; parent_url?: string; depth?: number; section?: string; priority?: number; }; collector: { name: string; version: string; rules?: components["schemas"]["package-ref.schema"]; collection_id?: components["schemas"]["Id"]; }; diagnostics?: components["schemas"]["DiagnosticMessage"][]; metadata?: Record<string, unknown>; }; EntityKey: { scope: string; natural: { [key: string]: string | number | boolean; }; }; ObservationOrder: { observation_id: components["schemas"]["Id"]; observed_at: components["schemas"]["Timestamp"]; sequence?: number; material_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; }; "entity.schema": { entity_type: string; schema?: string; key: components["schemas"]["EntityKey"]; fields: { [key: string]: unknown; }; cleared?: string[]; completeness?: "full" | "partial"; observation: components["schemas"]["ObservationOrder"]; provenance?: components["schemas"]["Provenance"]; confidence?: number; }; Provenance: { package?: components["schemas"]["package-ref.schema"]; invocation_id?: components["schemas"]["Id"]; run_id?: components["schemas"]["Id"]; stage_id?: components["schemas"]["Slug"]; }; StoredObjectRef: { object_id: components["schemas"]["Id"]; adapter: string; connection_id?: components["schemas"]["Slug"]; locator?: { [key: string]: string | number; }; media_type?: components["schemas"]["MediaType"]; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; content?: components["schemas"]["content-ref.schema"]; }; WriteAck: { status: "written" | "duplicate" | "stale" | "partially_stale" | "simulated"; target: { adapter: string; connection_id?: components["schemas"]["Slug"]; }; object?: components["schemas"]["StoredObjectRef"]; entity?: { entity_type?: string; canonical_key?: string; version?: number; }; applied_fields?: string[]; stale_fields?: string[]; delivery_key?: string; }; HandlerStatus: "success" | "empty" | "unrecognized" | "failed"; "handler-result.schema": { invocation_id: components["schemas"]["Id"]; handler: components["schemas"]["package-ref.schema"]; handler_kind: components["schemas"]["HandlerKind"]; status: components["schemas"]["HandlerStatus"]; inputs: components["schemas"]["InputRef"][]; output?: components["schemas"]["HandlerOutput"]; unrecognized?: { partial: boolean; reason?: string; signature?: string; }; failure?: { kind: "execution_error" | "schema_mismatch" | "timeout" | "resource_exceeded" | "sandbox_violation" | "dependency_error" | "connection_error" | "budget_exhausted" | "invalid_params"; message: string; retryable?: boolean; details?: Record<string, unknown>; }; diagnostics?: components["schemas"]["Diagnostics"]; usage?: components["schemas"]["Usage"]; delivery_key?: string; duplicate?: boolean; test_mode?: boolean; started_at: components["schemas"]["Timestamp"]; finished_at: components["schemas"]["Timestamp"]; } & (unknown & unknown); TestCaseResult: { name: string; passed: boolean; expected_status?: components["schemas"]["HandlerStatus"]; actual_status?: components["schemas"]["HandlerStatus"]; differences?: { pointer: string; expected?: unknown; actual?: unknown; }[]; result?: components["schemas"]["handler-result.schema"]; }; HandlerKind: "extractor" | "storage" | "llm" | "transform" | "collector-rules"; InputRef: { kind: "material" | "entities" | "data"; material_id?: components["schemas"]["Id"]; observation_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; from_invocation_id?: components["schemas"]["Id"]; }; HandlerOutput: { entities?: components["schemas"]["entity.schema"][]; entities_ref?: components["schemas"]["content-ref.schema"]; data?: unknown; data_ref?: components["schemas"]["content-ref.schema"]; writes?: components["schemas"]["WriteAck"][]; }; Diagnostics: { messages?: components["schemas"]["DiagnosticMessage"][]; validation_errors?: { pointer: string; message: string; schema_pointer?: string; }[]; metrics?: { duration_ms?: number; cpu_ms?: number; peak_memory_mb?: number; output_bytes?: number; }; logs_ref?: components["schemas"]["content-ref.schema"]; }; Usage: { llm?: { provider?: string; model?: string; input_tokens?: number; output_tokens?: number; cost?: components["schemas"]["Money"]; }; }; JobCancelRequest: { reason?: string; }; TestReport: { package: components["schemas"]["package-ref.schema"]; passed: number; failed: number; cases: components["schemas"]["TestCaseResult"][]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; }; "source.schema": { source_id: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; title: string; description?: string; locator: { url?: string; telegram_username?: string; telegram_channel_id?: string; }; collector_rules?: components["schemas"]["package-ref.schema"]; limits?: components["schemas"]["limits.schema"]; forward_unknown_to_llm?: boolean; expected_entity_types?: string[]; change_policy?: { llm_versions?: "manual_approval" | "auto_after_checks" | "forbidden"; }; connections?: { [key: string]: components["schemas"]["Slug"]; }; labels?: components["schemas"]["Labels"]; readonly created_at?: components["schemas"]["Timestamp"]; readonly updated_at?: components["schemas"]["Timestamp"]; }; CollectorStage: { collector: string; rules?: components["schemas"]["package-ref.schema"]; mode?: "full" | "incremental"; }; Condition: { all: components["schemas"]["Condition"][]; } | { any: components["schemas"]["Condition"][]; } | { not: components["schemas"]["Condition"]; } | components["schemas"]["Predicate"]; Predicate: { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; StageInput: { from: components["schemas"]["Slug"]; select?: "output" | "input_material" | "problems" | "unmatched_materials"; when?: components["schemas"]["Condition"]; }; Binding: { source_ids?: components["schemas"]["Slug"][]; sections?: components["schemas"]["Slug"][]; url_patterns?: components["schemas"]["UrlPattern"][]; media_types?: string[]; content_kinds?: string[]; }; TaskInput: { source_id: components["schemas"]["Slug"]; urls?: string[]; stored_materials?: { storage_connection_id?: components["schemas"]["Slug"]; since?: components["schemas"]["Timestamp"]; until?: components["schemas"]["Timestamp"]; material_ids?: components["schemas"]["Id"][]; object_ids?: components["schemas"]["Id"][]; observation_ids?: components["schemas"]["Id"][]; }; }; Stage: { stage_id: components["schemas"]["Slug"]; kind: "collect" | "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" | "fail_run"; } & (unknown & unknown); Schedule: { type: "manual" | "once" | "cron" | "interval"; at?: components["schemas"]["Timestamp"]; cron?: string; interval_seconds?: number; timezone?: string; start_at?: components["schemas"]["Timestamp"]; end_at?: components["schemas"]["Timestamp"]; enabled?: boolean; overlap?: "skip" | "queue" | "allow"; } & (unknown & unknown & unknown); "task-config.schema": { task_id: components["schemas"]["Slug"]; title: string; description?: string; enabled?: boolean; input: components["schemas"]["TaskInput"]; stages: components["schemas"]["Stage"][]; schedule?: components["schemas"]["Schedule"]; retries?: components["schemas"]["RetryPolicy"]; limits?: components["schemas"]["limits.schema"]; forward_unknown_to_llm?: boolean; labels?: components["schemas"]["Labels"]; }; PackagePath: string; PythonEntry: { runtime: "python"; module: string; callable: string; }; StorageEntry: { executor: "storage"; adapter: string; writes: "raw" | "entities" | "raw_and_entities" | "data"; format?: { raw?: "original" | "html" | "json"; entities?: "json" | "jsonl"; }; history?: boolean; }; LlmEntry: { executor: "llm"; instructions: components["schemas"]["PackagePath"]; input_template?: components["schemas"]["PackagePath"]; output_schema: components["schemas"]["PackagePath"]; model?: string; temperature?: number; max_output_tokens?: number; }; CollectorRulesEntry: { collector: string; rules: components["schemas"]["PackagePath"]; }; ExecutorEntry: { executor: string; operation?: string; }; InputContract: { accepts?: ("material" | "entities" | "data")[]; media_types?: string[]; content_kinds?: string[]; entity_types?: string[]; data_schema?: components["schemas"]["PackagePath"]; }; OutputContract: { entities?: { entity_type: string; schema: components["schemas"]["PackagePath"]; key_fields: string[]; description?: string; }[]; data_schema?: components["schemas"]["PackagePath"]; }; Dependencies: { runtime_profile?: string; python?: string[]; packages?: components["schemas"]["package-ref.schema"][]; }; ConnectionKind: string; ConnectionRequirement: { name: string; kind: components["schemas"]["ConnectionKind"]; purpose?: string; optional?: boolean; }; TestCase: { name: string; input: { material?: components["schemas"]["PackagePath"]; file?: components["schemas"]["PackagePath"]; media_type?: string; url?: string; entities?: components["schemas"]["PackagePath"]; data?: components["schemas"]["PackagePath"]; }; params?: Record<string, unknown>; expected_status: components["schemas"]["HandlerStatus"]; expected?: components["schemas"]["PackagePath"]; compare?: "exact" | "subset"; origin?: "human" | "llm" | "problem_sample"; }; "$defs-Provenance": { created_by: "human" | "llm" | "import"; authors?: string[]; created_at?: components["schemas"]["Timestamp"]; based_on?: components["schemas"]["package-ref.schema"]; change_summary?: string; llm?: { provider?: string; model?: string; assistant_job_id?: components["schemas"]["Id"]; reason?: "onboarding" | "improvement" | "unknown_material" | "upstream_port"; }; upstream_port?: { parent_version: components["schemas"]["SemVer"]; requested_by?: string; }; }; "package-manifest.schema": { schema_version: "1"; package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; tags?: string[]; entry: components["schemas"]["PythonEntry"] | components["schemas"]["StorageEntry"] | components["schemas"]["LlmEntry"] | components["schemas"]["CollectorRulesEntry"] | components["schemas"]["ExecutorEntry"]; input?: components["schemas"]["InputContract"]; params_schema?: components["schemas"]["PackagePath"]; output?: components["schemas"]["OutputContract"]; dependencies?: components["schemas"]["Dependencies"]; required_connections?: components["schemas"]["ConnectionRequirement"][]; access?: { network?: "none" | "allowlist"; hosts?: string[]; }; tests?: components["schemas"]["TestCase"][]; provenance: components["schemas"]["$defs-Provenance"]; fork_of?: components["schemas"]["package-ref.schema"]; bindings_hint?: { source_kinds?: components["schemas"]["SourceKind"][]; domains?: string[]; url_patterns?: string[]; }; } & unknown; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.components.responses

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:1941](../../../../../../web/admin/src/api/generated/assistant.ts#L1941).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; TooManyRequests: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.components.parameters

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2000](../../../../../../web/admin/src/api/generated/assistant.ts#L2000).

```typescript
parameters: { SessionId: components["schemas"]["Id"]; Cursor: string; Limit: number; IdempotencyKey: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2017](../../../../../../web/admin/src/api/generated/assistant.ts#L2017).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.components.headers

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2018](../../../../../../web/admin/src/api/generated/assistant.ts#L2018).

```typescript
headers: { Location: string; IdempotencyReplayed: boolean; RetryAfter: number; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2026](../../../../../../web/admin/src/api/generated/assistant.ts#L2026).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.$defs

**Тип.** Код: [web/admin/src/api/generated/assistant.ts:2028](../../../../../../web/admin/src/api/generated/assistant.ts#L2028).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.assistant.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/assistant.ts:2029](../../../../../../web/admin/src/api/generated/assistant.ts#L2029).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.assistant.md#adminapigeneratedassistantoperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.assistant.md#adminapigeneratedassistantoperationsgetserviceinfo) | Поле | ні |
| [listOnboardingSessions](api.generated.assistant.md#adminapigeneratedassistantoperationslistonboardingsessions) | Поле | ні |
| [startOnboarding](api.generated.assistant.md#adminapigeneratedassistantoperationsstartonboarding) | Поле | ні |
| [getOnboardingSession](api.generated.assistant.md#adminapigeneratedassistantoperationsgetonboardingsession) | Поле | ні |
| [selectCandidate](api.generated.assistant.md#adminapigeneratedassistantoperationsselectcandidate) | Поле | ні |
| [acceptProposal](api.generated.assistant.md#adminapigeneratedassistantoperationsacceptproposal) | Поле | ні |
| [listImprovementRuns](api.generated.assistant.md#adminapigeneratedassistantoperationslistimprovementruns) | Поле | ні |
| [startImprovement](api.generated.assistant.md#adminapigeneratedassistantoperationsstartimprovement) | Поле | ні |
| [analyzeUnknownMaterial](api.generated.assistant.md#adminapigeneratedassistantoperationsanalyzeunknownmaterial) | Поле | ні |
| [getJob](api.generated.assistant.md#adminapigeneratedassistantoperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.assistant.md#adminapigeneratedassistantoperationscanceljob) | Поле | ні |

## admin.api.generated.assistant.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2030](../../../../../../web/admin/src/api/generated/assistant.ts#L2030).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2059](../../../../../../web/admin/src/api/generated/assistant.ts#L2059).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.listOnboardingSessions

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2080](../../../../../../web/admin/src/api/generated/assistant.ts#L2080).

```typescript
listOnboardingSessions: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; status?: components["schemas"]["OnboardingStatus"][]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["OnboardingSessionList"]; }; }; 401: components["responses"]["Unauthenticated"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.startOnboarding

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2109](../../../../../../web/admin/src/api/generated/assistant.ts#L2109).

```typescript
startOnboarding: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["OnboardingRequest"]; }; }; responses: { 202: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 422: components["responses"]["UnprocessableEntity"]; 429: components["responses"]["TooManyRequests"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.getOnboardingSession

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2148](../../../../../../web/admin/src/api/generated/assistant.ts#L2148).

```typescript
getOnboardingSession: { parameters: { query?: never; header?: never; path: { session_id: components["parameters"]["SessionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["OnboardingSession"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.selectCandidate

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2172](../../../../../../web/admin/src/api/generated/assistant.ts#L2172).

```typescript
selectCandidate: { parameters: { query?: never; header?: never; path: { session_id: components["parameters"]["SessionId"]; }; cookie?: never; }; requestBody: { content: { "application/json": { candidate_id: string; }; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["OnboardingSession"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.acceptProposal

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2203](../../../../../../web/admin/src/api/generated/assistant.ts#L2203).

```typescript
acceptProposal: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { session_id: components["parameters"]["SessionId"]; proposal_id: string; }; cookie?: never; }; requestBody: { content: { "application/json": { activate?: boolean; source_id?: components["schemas"]["Slug"]; }; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.listImprovementRuns

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2239](../../../../../../web/admin/src/api/generated/assistant.ts#L2239).

```typescript
listImprovementRuns: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; package_id?: string; source_id?: string; problem_group_id?: string; status?: components["schemas"]["JobStatus"][]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["JobList"]; }; }; 401: components["responses"]["Unauthenticated"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.startImprovement

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2271](../../../../../../web/admin/src/api/generated/assistant.ts#L2271).

```typescript
startImprovement: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["ImprovementRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; 429: components["responses"]["TooManyRequests"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.analyzeUnknownMaterial

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2301](../../../../../../web/admin/src/api/generated/assistant.ts#L2301).

```typescript
analyzeUnknownMaterial: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["UnknownMaterialRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 403: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 422: components["responses"]["UnprocessableEntity"]; 429: components["responses"]["TooManyRequests"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2339](../../../../../../web/admin/src/api/generated/assistant.ts#L2339).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.assistant.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/assistant.ts:2363](../../../../../../web/admin/src/api/generated/assistant.ts#L2363).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
