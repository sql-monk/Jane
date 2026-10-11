# api/generated/collector

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.collector.paths](#adminapigeneratedcollectorpaths)
- [admin.api.generated.collector.paths./v1/health](#adminapigeneratedcollectorpathsv1health)
- [admin.api.generated.collector.paths./v1/info](#adminapigeneratedcollectorpathsv1info)
- [admin.api.generated.collector.paths./v1/fetches](#adminapigeneratedcollectorpathsv1fetches)
- [admin.api.generated.collector.paths./v1/collections](#adminapigeneratedcollectorpathsv1collections)
- [admin.api.generated.collector.paths./v1/collections/{collection_id}](#adminapigeneratedcollectorpathsv1collectionscollection_id)
- [admin.api.generated.collector.paths./v1/collections/{collection_id}/materials](#adminapigeneratedcollectorpathsv1collectionscollection_idmaterials)
- [admin.api.generated.collector.paths./v1/collections/{collection_id}/errors](#adminapigeneratedcollectorpathsv1collectionscollection_iderrors)
- [admin.api.generated.collector.paths./v1/rules/validations](#adminapigeneratedcollectorpathsv1rulesvalidations)
- [admin.api.generated.collector.paths./v1/states/{state_key}](#adminapigeneratedcollectorpathsv1statesstate_key)
- [admin.api.generated.collector.paths./v1/connections](#adminapigeneratedcollectorpathsv1connections)
- [admin.api.generated.collector.paths./v1/connections/{connection_id}](#adminapigeneratedcollectorpathsv1connectionsconnection_id)
- [admin.api.generated.collector.paths./v1/connections/{connection_id}/test](#adminapigeneratedcollectorpathsv1connectionsconnection_idtest)
- [admin.api.generated.collector.paths./v1/jobs/{job_id}](#adminapigeneratedcollectorpathsv1jobsjob_id)
- [admin.api.generated.collector.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedcollectorpathsv1jobsjob_idcancel)
- [admin.api.generated.collector.webhooks](#adminapigeneratedcollectorwebhooks)
- [admin.api.generated.collector.components](#adminapigeneratedcollectorcomponents)
- [admin.api.generated.collector.components.schemas](#adminapigeneratedcollectorcomponentsschemas)
- [admin.api.generated.collector.components.responses](#adminapigeneratedcollectorcomponentsresponses)
- [admin.api.generated.collector.components.parameters](#adminapigeneratedcollectorcomponentsparameters)
- [admin.api.generated.collector.components.requestBodies](#adminapigeneratedcollectorcomponentsrequestbodies)
- [admin.api.generated.collector.components.headers](#adminapigeneratedcollectorcomponentsheaders)
- [admin.api.generated.collector.components.pathItems](#adminapigeneratedcollectorcomponentspathitems)
- [admin.api.generated.collector.$defs](#adminapigeneratedcollectordefs)
- [admin.api.generated.collector.operations](#adminapigeneratedcollectoroperations)
- [admin.api.generated.collector.operations.getHealth](#adminapigeneratedcollectoroperationsgethealth)
- [admin.api.generated.collector.operations.getServiceInfo](#adminapigeneratedcollectoroperationsgetserviceinfo)
- [admin.api.generated.collector.operations.fetchMaterial](#adminapigeneratedcollectoroperationsfetchmaterial)
- [admin.api.generated.collector.operations.startCollection](#adminapigeneratedcollectoroperationsstartcollection)
- [admin.api.generated.collector.operations.getCollection](#adminapigeneratedcollectoroperationsgetcollection)
- [admin.api.generated.collector.operations.listCollectionMaterials](#adminapigeneratedcollectoroperationslistcollectionmaterials)
- [admin.api.generated.collector.operations.listCollectionErrors](#adminapigeneratedcollectoroperationslistcollectionerrors)
- [admin.api.generated.collector.operations.validateRules](#adminapigeneratedcollectoroperationsvalidaterules)
- [admin.api.generated.collector.operations.getCollectorState](#adminapigeneratedcollectoroperationsgetcollectorstate)
- [admin.api.generated.collector.operations.resetCollectorState](#adminapigeneratedcollectoroperationsresetcollectorstate)
- [admin.api.generated.collector.operations.listConnections](#adminapigeneratedcollectoroperationslistconnections)
- [admin.api.generated.collector.operations.getConnection](#adminapigeneratedcollectoroperationsgetconnection)
- [admin.api.generated.collector.operations.putConnection](#adminapigeneratedcollectoroperationsputconnection)
- [admin.api.generated.collector.operations.deleteConnection](#adminapigeneratedcollectoroperationsdeleteconnection)
- [admin.api.generated.collector.operations.testConnection](#adminapigeneratedcollectoroperationstestconnection)
- [admin.api.generated.collector.operations.getJob](#adminapigeneratedcollectoroperationsgetjob)
- [admin.api.generated.collector.operations.cancelJob](#adminapigeneratedcollectoroperationscanceljob)

## admin.api.generated.collector.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/collector.ts:3](../../../../../../web/admin/src/api/generated/collector.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.collector.md#adminapigeneratedcollectorpathsv1health) | Поле | ні |
| [/v1/info](api.generated.collector.md#adminapigeneratedcollectorpathsv1info) | Поле | ні |
| [/v1/fetches](api.generated.collector.md#adminapigeneratedcollectorpathsv1fetches) | Поле | ні |
| [/v1/collections](api.generated.collector.md#adminapigeneratedcollectorpathsv1collections) | Поле | ні |
| [/v1/collections/{collection_id}](api.generated.collector.md#adminapigeneratedcollectorpathsv1collectionscollection_id) | Поле | ні |
| [/v1/collections/{collection_id}/materials](api.generated.collector.md#adminapigeneratedcollectorpathsv1collectionscollection_idmaterials) | Поле | ні |
| [/v1/collections/{collection_id}/errors](api.generated.collector.md#adminapigeneratedcollectorpathsv1collectionscollection_iderrors) | Поле | ні |
| [/v1/rules/validations](api.generated.collector.md#adminapigeneratedcollectorpathsv1rulesvalidations) | Поле | ні |
| [/v1/states/{state_key}](api.generated.collector.md#adminapigeneratedcollectorpathsv1statesstate_key) | Поле | ні |
| [/v1/connections](api.generated.collector.md#adminapigeneratedcollectorpathsv1connections) | Поле | ні |
| [/v1/connections/{connection_id}](api.generated.collector.md#adminapigeneratedcollectorpathsv1connectionsconnection_id) | Поле | ні |
| [/v1/connections/{connection_id}/test](api.generated.collector.md#adminapigeneratedcollectorpathsv1connectionsconnection_idtest) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.collector.md#adminapigeneratedcollectorpathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.collector.md#adminapigeneratedcollectorpathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.collector.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/collector.ts:4](../../../../../../web/admin/src/api/generated/collector.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/collector.ts:21](../../../../../../web/admin/src/api/generated/collector.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/fetches

**Поле.** Код: [web/admin/src/api/generated/collector.ts:38](../../../../../../web/admin/src/api/generated/collector.ts#L38).

```typescript
/v1/fetches: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["fetchMaterial"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/collections

**Поле.** Код: [web/admin/src/api/generated/collector.ts:62](../../../../../../web/admin/src/api/generated/collector.ts#L62).

```typescript
/v1/collections: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["startCollection"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/collections/{collection_id}

**Поле.** Код: [web/admin/src/api/generated/collector.ts:79](../../../../../../web/admin/src/api/generated/collector.ts#L79).

```typescript
/v1/collections/{collection_id}: { parameters: { query?: never; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; get: operations["getCollection"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/collections/{collection_id}/materials

**Поле.** Код: [web/admin/src/api/generated/collector.ts:99](../../../../../../web/admin/src/api/generated/collector.ts#L99).

```typescript
/v1/collections/{collection_id}/materials: { parameters: { query?: never; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; get: operations["listCollectionMaterials"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/collections/{collection_id}/errors

**Поле.** Код: [web/admin/src/api/generated/collector.ts:125](../../../../../../web/admin/src/api/generated/collector.ts#L125).

```typescript
/v1/collections/{collection_id}/errors: { parameters: { query?: never; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; get: operations["listCollectionErrors"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/rules/validations

**Поле.** Код: [web/admin/src/api/generated/collector.ts:145](../../../../../../web/admin/src/api/generated/collector.ts#L145).

```typescript
/v1/rules/validations: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["validateRules"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/states/{state_key}

**Поле.** Код: [web/admin/src/api/generated/collector.ts:162](../../../../../../web/admin/src/api/generated/collector.ts#L162).

```typescript
/v1/states/{state_key}: { parameters: { query?: never; header?: never; path: { state_key: components["schemas"]["Slug"]; }; cookie?: never; }; get: operations["getCollectorState"]; put?: never; post?: never; delete: operations["resetCollectorState"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/connections

**Поле.** Код: [web/admin/src/api/generated/collector.ts:182](../../../../../../web/admin/src/api/generated/collector.ts#L182).

```typescript
/v1/connections: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listConnections"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/connections/{connection_id}

**Поле.** Код: [web/admin/src/api/generated/collector.ts:199](../../../../../../web/admin/src/api/generated/collector.ts#L199).

```typescript
/v1/connections/{connection_id}: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get: operations["getConnection"]; put: operations["putConnection"]; post?: never; delete: operations["deleteConnection"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/connections/{connection_id}/test

**Поле.** Код: [web/admin/src/api/generated/collector.ts:224](../../../../../../web/admin/src/api/generated/collector.ts#L224).

```typescript
/v1/connections/{connection_id}/test: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["testConnection"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/collector.ts:243](../../../../../../web/admin/src/api/generated/collector.ts#L243).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/collector.ts:262](../../../../../../web/admin/src/api/generated/collector.ts#L262).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.webhooks

**Тип.** Код: [web/admin/src/api/generated/collector.ts:287](../../../../../../web/admin/src/api/generated/collector.ts#L287).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.collector.components

**Інтерфейс.** Код: [web/admin/src/api/generated/collector.ts:288](../../../../../../web/admin/src/api/generated/collector.ts#L288).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.collector.md#adminapigeneratedcollectorcomponentsschemas) | Поле | ні |
| [responses](api.generated.collector.md#adminapigeneratedcollectorcomponentsresponses) | Поле | ні |
| [parameters](api.generated.collector.md#adminapigeneratedcollectorcomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.collector.md#adminapigeneratedcollectorcomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.collector.md#adminapigeneratedcollectorcomponentsheaders) | Поле | ні |
| [pathItems](api.generated.collector.md#adminapigeneratedcollectorcomponentspathitems) | Поле | ні |

## admin.api.generated.collector.components.schemas

**Поле.** Код: [web/admin/src/api/generated/collector.ts:289](../../../../../../web/admin/src/api/generated/collector.ts#L289).

```typescript
schemas: { ContentDelivery: "auto" | "inline" | "blob"; FetchRequest: { source_kind: components["schemas"]["SourceKind"]; source_id?: components["schemas"]["Slug"]; url?: string; telegram?: { channel_username?: string; channel_id?: string; message_id: number; }; rules?: components["schemas"]["collector-rules.schema"]; rules_ref?: components["schemas"]["package-ref.schema"]; content_delivery?: components["schemas"]["ContentDelivery"]; limits?: components["schemas"]["limits.schema"]; }; CollectionRequest: { source_kind: components["schemas"]["SourceKind"]; source_id?: components["schemas"]["Slug"]; rules?: components["schemas"]["collector-rules.schema"]; rules_ref?: components["schemas"]["package-ref.schema"]; urls?: string[]; mode?: "full" | "incremental"; state_key?: components["schemas"]["Slug"]; content_delivery?: components["schemas"]["ContentDelivery"]; limits?: components["schemas"]["limits.schema"]; trace?: components["schemas"]["TraceContext"]; labels?: components["schemas"]["Labels"]; } | unknown | unknown; CollectionStats: { discovered?: number; fetched?: number; emitted?: number; acknowledged?: number; unacked?: number; duplicates?: number; skipped_out_of_scope?: number; skipped_robots?: number; not_modified?: number; errors?: number; frontier_size?: number; bytes_fetched?: number; by_strategy?: { [key: string]: number; }; }; Collection: { collection_id: components["schemas"]["Id"]; status: components["schemas"]["JobStatus"]; paused_by_backpressure?: boolean; source_kind: components["schemas"]["SourceKind"]; source_id?: components["schemas"]["Slug"]; rules?: components["schemas"]["package-ref.schema"]; mode?: "full" | "incremental"; state_key?: string; created_at: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; stats: components["schemas"]["CollectionStats"]; effective_limits?: components["schemas"]["limits.schema"]; }; MaterialPage: { items: components["schemas"]["material.schema"][]; next_cursor: components["schemas"]["NextCursor"]; end_of_stream: boolean; collection_status: components["schemas"]["JobStatus"]; }; FetchError: { url?: string; telegram_message?: string; code: string; http_status?: number; attempts?: number; message: string; at: components["schemas"]["Timestamp"]; }; FetchErrorPage: { items: components["schemas"]["FetchError"][]; next_cursor: components["schemas"]["NextCursor"]; }; RulesValidation: { valid: boolean; supported?: boolean; errors: components["schemas"]["FieldError"][]; warnings?: components["schemas"]["FieldError"][]; }; CollectorState: { state_key: string; collector: string; updated_at: components["schemas"]["Timestamp"]; known_urls?: number; frontier_size?: number; cursors?: { [key: string]: Record<string, unknown>; }; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; SourceKind: string; Slug: string; UrlPattern: { type?: "glob" | "regex"; value: string; }; WebScope: { allowed_domains: string[]; include_subdomains?: boolean; allowed_schemes?: ("http" | "https")[]; path_prefixes?: string[]; include?: components["schemas"]["UrlPattern"][]; exclude?: components["schemas"]["UrlPattern"][]; }; StrategyCommon: { strategy_id?: components["schemas"]["Slug"]; priority?: number; section?: components["schemas"]["Slug"]; limits?: components["schemas"]["limits.schema"]; }; SeedListStrategy: { type: "seed_list"; urls: string[]; } & (components["schemas"]["StrategyCommon"] & { type: "seed_list"; }); RecursiveStrategy: { type: "recursive"; seeds?: string[]; follow?: components["schemas"]["UrlPattern"][]; link_sources?: ("a_href" | "link_rel" | "canonical" | "pagination_rel")[]; } & (components["schemas"]["StrategyCommon"] & { type: "recursive"; }); Timestamp: string; SitemapStrategy: { type: "sitemap"; urls?: string[]; use_robots_txt?: boolean; lastmod_since?: components["schemas"]["Timestamp"]; use_lastmod_for_revisit?: boolean; } & (components["schemas"]["StrategyCommon"] & { type: "sitemap"; }); FeedStrategy: { type: "feed"; urls?: string[]; autodiscover?: boolean; } & (components["schemas"]["StrategyCommon"] & { type: "feed"; }); Selector: { type?: "css" | "xpath" | "rel"; value: string; attribute?: string; }; ListingStrategy: { type: "listing"; start_urls: string[]; item_links?: components["schemas"]["Selector"]; next_page?: components["schemas"]["Selector"]; page_param?: { name: string; start?: number; step?: number; stop_when_empty?: boolean; }; search?: { url_template: string; queries: string[]; }; } & (components["schemas"]["StrategyCommon"] & { type: "listing"; }); UrlTemplateStrategy: { type: "url_template"; template: string; variables: { [key: string]: { range: { start: number; end: number; step?: number; }; } | { values: (string | number)[]; }; }; stop_after_consecutive_misses?: number; } & (components["schemas"]["StrategyCommon"] & { type: "url_template"; }); ApiFeedStrategy: { type: "api_feed"; url: string; method?: "GET" | "POST"; body?: unknown; items_path: string; url_path: string; lastmod_path?: string; emit_items_as_materials?: boolean; pagination?: { type?: "none" | "next_url" | "cursor" | "page"; next_url_path?: string; cursor_path?: string; cursor_param?: string; page_param?: string; }; } & (components["schemas"]["StrategyCommon"] & { type: "api_feed"; }); LlmExploreStrategy: { type: "llm_explore"; goal?: string; expected_entity_types?: string[]; } & (components["schemas"]["StrategyCommon"] & { type: "llm_explore"; }); Strategy: components["schemas"]["SeedListStrategy"] | components["schemas"]["RecursiveStrategy"] | components["schemas"]["SitemapStrategy"] | components["schemas"]["FeedStrategy"] | components["schemas"]["ListingStrategy"] | components["schemas"]["UrlTemplateStrategy"] | components["schemas"]["ApiFeedStrategy"] | components["schemas"]["LlmExploreStrategy"]; RobotsPolicy: { mode?: "respect" | "owner_policy"; user_agent_token?: string; owner_policy?: { confirmed_owner: true; justification: string; confirmed_by?: string; confirmed_at?: components["schemas"]["Timestamp"]; }; }; UrlNormalization: { remove_fragment?: boolean; lowercase_host?: boolean; sort_query?: boolean; strip_query_params?: string[]; trailing_slash?: "keep" | "add" | "remove"; }; WebRules: { collector: "web"; scope: components["schemas"]["WebScope"]; strategies: components["schemas"]["Strategy"][]; robots?: components["schemas"]["RobotsPolicy"]; normalization?: components["schemas"]["UrlNormalization"]; dedup?: { key?: "canonical_url" | "canonical_url_and_content"; use_link_rel_canonical?: boolean; }; priorities?: { pattern: components["schemas"]["UrlPattern"]; priority: number; }[]; sections?: { section_id: components["schemas"]["Slug"]; title?: string; patterns: components["schemas"]["UrlPattern"][]; }[]; fetch?: { user_agent?: string; headers?: { [key: string]: string; }; connection_id?: components["schemas"]["Slug"]; accept_media_types?: string[]; render_js?: boolean; }; revisit?: { mode?: "never" | "interval" | "if_changed"; }; limits?: components["schemas"]["limits.schema"]; }; TelegramRules: { collector: "telegram"; channels: ({ username?: string; channel_id?: string; } | unknown | unknown)[]; history?: { enabled?: boolean; since?: components["schemas"]["Timestamp"]; from_message_id?: number; }; updates?: { new_messages?: boolean; edits?: boolean; }; media?: { download?: boolean; kinds?: ("photo" | "document" | "video" | "audio")[]; }; account_connection_id?: components["schemas"]["Slug"]; limits?: components["schemas"]["limits.schema"]; }; "collector-rules.schema": {} & (components["schemas"]["WebRules"] | components["schemas"]["TelegramRules"]); SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; Id: string; MediaType: string; Sha256Hex: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; "material.schema": { material_id: components["schemas"]["Id"]; observation_id: components["schemas"]["Id"]; source: { source_id?: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; name?: string; }; locator: { url?: string; final_url?: string; canonical_url?: string; telegram?: { channel_id: string; channel_username?: string; message_id: number; grouped_id?: string; }; }; fetched_at: components["schemas"]["Timestamp"]; published_at?: components["schemas"]["Timestamp"]; edited_at?: components["schemas"]["Timestamp"]; format: { media_type: components["schemas"]["MediaType"]; charset?: string; language?: string; content_kind?: string; }; revision: { content_sha256: components["schemas"]["Sha256Hex"]; source_revision?: string; sequence?: number; is_edit?: boolean; }; content: components["schemas"]["content-ref.schema"]; attachments?: { name: string; role?: string; content: components["schemas"]["content-ref.schema"]; }[]; http?: { status?: number; headers?: { [key: string]: string; }; redirects?: string[]; }; discovery?: { strategy?: string; parent_url?: string; depth?: number; section?: string; priority?: number; }; collector: { name: string; version: string; rules?: components["schemas"]["package-ref.schema"]; collection_id?: components["schemas"]["Id"]; }; diagnostics?: components["schemas"]["DiagnosticMessage"][]; metadata?: Record<string, unknown>; }; TraceContext: { trace_id?: string; run_id?: components["schemas"]["Id"]; task_id?: components["schemas"]["Slug"]; stage_id?: components["schemas"]["Slug"]; source_id?: components["schemas"]["Slug"]; }; Labels: { [key: string]: string; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; NextCursor: string | null; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; ConnectionKind: string; SecretRef: string; "connection.schema": { connection_id: components["schemas"]["Slug"]; kind: components["schemas"]["ConnectionKind"]; title?: string; params?: { [key: string]: string | number | boolean | unknown[] | Record<string, unknown>; }; secret_refs?: { [key: string]: components["schemas"]["SecretRef"]; }; labels?: components["schemas"]["Labels"]; }; ConnectionList: { items: components["schemas"]["connection.schema"][]; next_cursor: components["schemas"]["NextCursor"]; }; ConnectionTestResult: { ok: boolean; checked_at: components["schemas"]["Timestamp"]; latency_ms?: number; secrets_resolved?: { [key: string]: boolean; }; message?: string; }; JobCancelRequest: { reason?: string; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.components.responses

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1291](../../../../../../web/admin/src/api/generated/collector.ts#L1291).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; BadRequest: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; TooManyRequests: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; InternalError: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; ServiceUnavailable: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.components.parameters

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1387](../../../../../../web/admin/src/api/generated/collector.ts#L1387).

```typescript
parameters: { CollectionId: components["schemas"]["Id"]; IdempotencyKey: string; Limit: number; Cursor: string; ConnectionId: components["schemas"]["Slug"]; IfMatch: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1411](../../../../../../web/admin/src/api/generated/collector.ts#L1411).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.components.headers

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1412](../../../../../../web/admin/src/api/generated/collector.ts#L1412).

```typescript
headers: { RetryAfter: number; Location: string; IdempotencyReplayed: boolean; ETag: string; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1422](../../../../../../web/admin/src/api/generated/collector.ts#L1422).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.$defs

**Тип.** Код: [web/admin/src/api/generated/collector.ts:1424](../../../../../../web/admin/src/api/generated/collector.ts#L1424).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.collector.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/collector.ts:1425](../../../../../../web/admin/src/api/generated/collector.ts#L1425).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.collector.md#adminapigeneratedcollectoroperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.collector.md#adminapigeneratedcollectoroperationsgetserviceinfo) | Поле | ні |
| [fetchMaterial](api.generated.collector.md#adminapigeneratedcollectoroperationsfetchmaterial) | Поле | ні |
| [startCollection](api.generated.collector.md#adminapigeneratedcollectoroperationsstartcollection) | Поле | ні |
| [getCollection](api.generated.collector.md#adminapigeneratedcollectoroperationsgetcollection) | Поле | ні |
| [listCollectionMaterials](api.generated.collector.md#adminapigeneratedcollectoroperationslistcollectionmaterials) | Поле | ні |
| [listCollectionErrors](api.generated.collector.md#adminapigeneratedcollectoroperationslistcollectionerrors) | Поле | ні |
| [validateRules](api.generated.collector.md#adminapigeneratedcollectoroperationsvalidaterules) | Поле | ні |
| [getCollectorState](api.generated.collector.md#adminapigeneratedcollectoroperationsgetcollectorstate) | Поле | ні |
| [resetCollectorState](api.generated.collector.md#adminapigeneratedcollectoroperationsresetcollectorstate) | Поле | ні |
| [listConnections](api.generated.collector.md#adminapigeneratedcollectoroperationslistconnections) | Поле | ні |
| [getConnection](api.generated.collector.md#adminapigeneratedcollectoroperationsgetconnection) | Поле | ні |
| [putConnection](api.generated.collector.md#adminapigeneratedcollectoroperationsputconnection) | Поле | ні |
| [deleteConnection](api.generated.collector.md#adminapigeneratedcollectoroperationsdeleteconnection) | Поле | ні |
| [testConnection](api.generated.collector.md#adminapigeneratedcollectoroperationstestconnection) | Поле | ні |
| [getJob](api.generated.collector.md#adminapigeneratedcollectoroperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.collector.md#adminapigeneratedcollectoroperationscanceljob) | Поле | ні |

## admin.api.generated.collector.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1426](../../../../../../web/admin/src/api/generated/collector.ts#L1426).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1455](../../../../../../web/admin/src/api/generated/collector.ts#L1455).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.fetchMaterial

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1476](../../../../../../web/admin/src/api/generated/collector.ts#L1476).

```typescript
fetchMaterial: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["FetchRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["material.schema"]; }; }; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 403: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 404: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 422: components["responses"]["UnprocessableEntity"]; 429: components["responses"]["TooManyRequests"]; 500: components["responses"]["InternalError"]; 501: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 502: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 503: components["responses"]["ServiceUnavailable"]; 504: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.startCollection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1567](../../../../../../web/admin/src/api/generated/collector.ts#L1567).

```typescript
startCollection: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["CollectionRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.getCollection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1598](../../../../../../web/admin/src/api/generated/collector.ts#L1598).

```typescript
getCollection: { parameters: { query?: never; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Collection"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.listCollectionMaterials

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1624](../../../../../../web/admin/src/api/generated/collector.ts#L1624).

```typescript
listCollectionMaterials: { parameters: { query?: { after?: string; limit?: components["parameters"]["Limit"]; wait_ms?: number; }; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["MaterialPage"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 410: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.listCollectionErrors

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1665](../../../../../../web/admin/src/api/generated/collector.ts#L1665).

```typescript
listCollectionErrors: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path: { collection_id: components["parameters"]["CollectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["FetchErrorPage"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.validateRules

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1696](../../../../../../web/admin/src/api/generated/collector.ts#L1696).

```typescript
validateRules: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["collector-rules.schema"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["RulesValidation"]; }; }; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.getCollectorState

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1722](../../../../../../web/admin/src/api/generated/collector.ts#L1722).

```typescript
getCollectorState: { parameters: { query?: never; header?: never; path: { state_key: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["CollectorState"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.resetCollectorState

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1747](../../../../../../web/admin/src/api/generated/collector.ts#L1747).

```typescript
resetCollectorState: { parameters: { query?: never; header?: never; path: { state_key: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.listConnections

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1770](../../../../../../web/admin/src/api/generated/collector.ts#L1770).

```typescript
listConnections: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionList"]; }; }; 401: components["responses"]["Unauthenticated"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.getConnection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1797](../../../../../../web/admin/src/api/generated/collector.ts#L1797).

```typescript
getConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.putConnection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1823](../../../../../../web/admin/src/api/generated/collector.ts#L1823).

```typescript
putConnection: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["connection.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 201: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; 501: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.deleteConnection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1879](../../../../../../web/admin/src/api/generated/collector.ts#L1879).

```typescript
deleteConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.testConnection

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1902](../../../../../../web/admin/src/api/generated/collector.ts#L1902).

```typescript
testConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionTestResult"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1927](../../../../../../web/admin/src/api/generated/collector.ts#L1927).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.collector.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/collector.ts:1952](../../../../../../web/admin/src/api/generated/collector.ts#L1952).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.
