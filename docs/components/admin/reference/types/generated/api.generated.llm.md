# api/generated/llm

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.llm.paths](#adminapigeneratedllmpaths)
- [admin.api.generated.llm.paths./v1/health](#adminapigeneratedllmpathsv1health)
- [admin.api.generated.llm.paths./v1/info](#adminapigeneratedllmpathsv1info)
- [admin.api.generated.llm.paths./v1/providers](#adminapigeneratedllmpathsv1providers)
- [admin.api.generated.llm.paths./v1/providers/{provider_id}](#adminapigeneratedllmpathsv1providersprovider_id)
- [admin.api.generated.llm.paths./v1/model-aliases](#adminapigeneratedllmpathsv1model-aliases)
- [admin.api.generated.llm.paths./v1/model-aliases/{alias}](#adminapigeneratedllmpathsv1model-aliasesalias)
- [admin.api.generated.llm.paths./v1/completions](#adminapigeneratedllmpathsv1completions)
- [admin.api.generated.llm.paths./v1/budgets](#adminapigeneratedllmpathsv1budgets)
- [admin.api.generated.llm.paths./v1/budgets/{scope_type}/{scope_id}](#adminapigeneratedllmpathsv1budgetsscope_typescope_id)
- [admin.api.generated.llm.paths./v1/usage](#adminapigeneratedllmpathsv1usage)
- [admin.api.generated.llm.paths./v1/jobs/{job_id}](#adminapigeneratedllmpathsv1jobsjob_id)
- [admin.api.generated.llm.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedllmpathsv1jobsjob_idcancel)
- [admin.api.generated.llm.webhooks](#adminapigeneratedllmwebhooks)
- [admin.api.generated.llm.components](#adminapigeneratedllmcomponents)
- [admin.api.generated.llm.components.schemas](#adminapigeneratedllmcomponentsschemas)
- [admin.api.generated.llm.components.responses](#adminapigeneratedllmcomponentsresponses)
- [admin.api.generated.llm.components.parameters](#adminapigeneratedllmcomponentsparameters)
- [admin.api.generated.llm.components.requestBodies](#adminapigeneratedllmcomponentsrequestbodies)
- [admin.api.generated.llm.components.headers](#adminapigeneratedllmcomponentsheaders)
- [admin.api.generated.llm.components.pathItems](#adminapigeneratedllmcomponentspathitems)
- [admin.api.generated.llm.$defs](#adminapigeneratedllmdefs)
- [admin.api.generated.llm.operations](#adminapigeneratedllmoperations)
- [admin.api.generated.llm.operations.getHealth](#adminapigeneratedllmoperationsgethealth)
- [admin.api.generated.llm.operations.getServiceInfo](#adminapigeneratedllmoperationsgetserviceinfo)
- [admin.api.generated.llm.operations.listProviders](#adminapigeneratedllmoperationslistproviders)
- [admin.api.generated.llm.operations.getProvider](#adminapigeneratedllmoperationsgetprovider)
- [admin.api.generated.llm.operations.putProvider](#adminapigeneratedllmoperationsputprovider)
- [admin.api.generated.llm.operations.deleteProvider](#adminapigeneratedllmoperationsdeleteprovider)
- [admin.api.generated.llm.operations.listModelAliases](#adminapigeneratedllmoperationslistmodelaliases)
- [admin.api.generated.llm.operations.putModelAlias](#adminapigeneratedllmoperationsputmodelalias)
- [admin.api.generated.llm.operations.createCompletion](#adminapigeneratedllmoperationscreatecompletion)
- [admin.api.generated.llm.operations.listBudgets](#adminapigeneratedllmoperationslistbudgets)
- [admin.api.generated.llm.operations.putBudget](#adminapigeneratedllmoperationsputbudget)
- [admin.api.generated.llm.operations.deleteBudget](#adminapigeneratedllmoperationsdeletebudget)
- [admin.api.generated.llm.operations.getUsage](#adminapigeneratedllmoperationsgetusage)
- [admin.api.generated.llm.operations.getJob](#adminapigeneratedllmoperationsgetjob)
- [admin.api.generated.llm.operations.cancelJob](#adminapigeneratedllmoperationscanceljob)

## admin.api.generated.llm.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/llm.ts:3](../../../../../../web/admin/src/api/generated/llm.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.llm.md#adminapigeneratedllmpathsv1health) | Поле | ні |
| [/v1/info](api.generated.llm.md#adminapigeneratedllmpathsv1info) | Поле | ні |
| [/v1/providers](api.generated.llm.md#adminapigeneratedllmpathsv1providers) | Поле | ні |
| [/v1/providers/{provider_id}](api.generated.llm.md#adminapigeneratedllmpathsv1providersprovider_id) | Поле | ні |
| [/v1/model-aliases](api.generated.llm.md#adminapigeneratedllmpathsv1model-aliases) | Поле | ні |
| [/v1/model-aliases/{alias}](api.generated.llm.md#adminapigeneratedllmpathsv1model-aliasesalias) | Поле | ні |
| [/v1/completions](api.generated.llm.md#adminapigeneratedllmpathsv1completions) | Поле | ні |
| [/v1/budgets](api.generated.llm.md#adminapigeneratedllmpathsv1budgets) | Поле | ні |
| [/v1/budgets/{scope_type}/{scope_id}](api.generated.llm.md#adminapigeneratedllmpathsv1budgetsscope_typescope_id) | Поле | ні |
| [/v1/usage](api.generated.llm.md#adminapigeneratedllmpathsv1usage) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.llm.md#adminapigeneratedllmpathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.llm.md#adminapigeneratedllmpathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.llm.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/llm.ts:4](../../../../../../web/admin/src/api/generated/llm.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/llm.ts:21](../../../../../../web/admin/src/api/generated/llm.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/providers

**Поле.** Код: [web/admin/src/api/generated/llm.ts:38](../../../../../../web/admin/src/api/generated/llm.ts#L38).

```typescript
/v1/providers: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listProviders"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/providers/{provider_id}

**Поле.** Код: [web/admin/src/api/generated/llm.ts:55](../../../../../../web/admin/src/api/generated/llm.ts#L55).

```typescript
/v1/providers/{provider_id}: { parameters: { query?: never; header?: never; path: { provider_id: components["schemas"]["Slug"]; }; cookie?: never; }; get: operations["getProvider"]; put: operations["putProvider"]; post?: never; delete: operations["deleteProvider"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/model-aliases

**Поле.** Код: [web/admin/src/api/generated/llm.ts:76](../../../../../../web/admin/src/api/generated/llm.ts#L76).

```typescript
/v1/model-aliases: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listModelAliases"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/model-aliases/{alias}

**Поле.** Код: [web/admin/src/api/generated/llm.ts:93](../../../../../../web/admin/src/api/generated/llm.ts#L93).

```typescript
/v1/model-aliases/{alias}: { parameters: { query?: never; header?: never; path: { alias: string; }; cookie?: never; }; get?: never; put: operations["putModelAlias"]; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/completions

**Поле.** Код: [web/admin/src/api/generated/llm.ts:112](../../../../../../web/admin/src/api/generated/llm.ts#L112).

```typescript
/v1/completions: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["createCompletion"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/budgets

**Поле.** Код: [web/admin/src/api/generated/llm.ts:129](../../../../../../web/admin/src/api/generated/llm.ts#L129).

```typescript
/v1/budgets: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listBudgets"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/budgets/{scope_type}/{scope_id}

**Поле.** Код: [web/admin/src/api/generated/llm.ts:146](../../../../../../web/admin/src/api/generated/llm.ts#L146).

```typescript
/v1/budgets/{scope_type}/{scope_id}: { parameters: { query?: never; header?: never; path: { scope_type: components["schemas"]["ScopeType"]; scope_id: string; }; cookie?: never; }; get?: never; put: operations["putBudget"]; post?: never; delete: operations["deleteBudget"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/usage

**Поле.** Код: [web/admin/src/api/generated/llm.ts:167](../../../../../../web/admin/src/api/generated/llm.ts#L167).

```typescript
/v1/usage: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getUsage"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/llm.ts:184](../../../../../../web/admin/src/api/generated/llm.ts#L184).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/llm.ts:203](../../../../../../web/admin/src/api/generated/llm.ts#L203).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.webhooks

**Тип.** Код: [web/admin/src/api/generated/llm.ts:228](../../../../../../web/admin/src/api/generated/llm.ts#L228).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.llm.components

**Інтерфейс.** Код: [web/admin/src/api/generated/llm.ts:229](../../../../../../web/admin/src/api/generated/llm.ts#L229).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.llm.md#adminapigeneratedllmcomponentsschemas) | Поле | ні |
| [responses](api.generated.llm.md#adminapigeneratedllmcomponentsresponses) | Поле | ні |
| [parameters](api.generated.llm.md#adminapigeneratedllmcomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.llm.md#adminapigeneratedllmcomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.llm.md#adminapigeneratedllmcomponentsheaders) | Поле | ні |
| [pathItems](api.generated.llm.md#adminapigeneratedllmcomponentspathitems) | Поле | ні |

## admin.api.generated.llm.components.schemas

**Поле.** Код: [web/admin/src/api/generated/llm.ts:230](../../../../../../web/admin/src/api/generated/llm.ts#L230).

```typescript
schemas: { ScopeType: "platform" | "source" | "task"; Provider: { provider_id: components["schemas"]["Slug"]; kind: string; connection_id?: components["schemas"]["Slug"]; enabled: boolean; models: { model_id: string; max_context_tokens?: number; supports_structured_output?: boolean; pricing?: { input_per_mtok: number; output_per_mtok: number; currency: string; }; }[]; limits?: components["schemas"]["llm"]; }; ModelAlias: { alias: string; provider_id: string; model_id: string; }; DataPart: { name: string; media_type?: string; text?: string; content?: components["schemas"]["content-ref.schema"]; }; CompletionRequest: { model?: string; instructions: string; data?: components["schemas"]["DataPart"][]; output_schema?: Record<string, unknown>; max_output_tokens?: number; temperature?: number; max_schema_retries?: number; scope: { source_id?: string; task_id?: string; run_id?: string; purpose: "handler" | "onboarding" | "improvement" | "unknown_material" | "other"; }; limits?: components["schemas"]["llm"]; test_mode?: boolean; mode?: "sync" | "async"; }; BudgetStatus: { scope_type: components["schemas"]["ScopeType"]; scope_id: string; spent: components["schemas"]["Money"]; limit?: components["schemas"]["Budget"]; resets_at?: components["schemas"]["Timestamp"]; exhausted: boolean; }; CompletionResult: { completion_id: components["schemas"]["Id"]; model: { provider_id: string; model_id: string; }; output?: unknown; output_text?: string; valid: boolean; validation_errors?: { pointer?: string; message?: string; }[]; finish_reason?: string; usage: { input_tokens: number; output_tokens: number; cost?: components["schemas"]["Money"]; }; budget?: components["schemas"]["BudgetStatus"][]; }; BudgetDefinition: { scope_type: components["schemas"]["ScopeType"]; scope_id: string; budget?: components["schemas"]["Budget"]; max_requests_per_minute?: number; status?: components["schemas"]["BudgetStatus"]; }; UsageRow: { period_start?: components["schemas"]["Timestamp"]; scope_type?: components["schemas"]["ScopeType"]; scope_id?: string; model?: string; purpose?: string; requests: number; input_tokens: number; output_tokens: number; cost: components["schemas"]["Money"]; test_mode?: boolean; }; UsageReport: { items: components["schemas"]["UsageRow"][]; totals: components["schemas"]["UsageRow"]; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; Slug: string; llm: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; MediaType: string; Sha256Hex: string; Timestamp: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); Id: string; Money: { amount: number; currency: string; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; NextCursor: string | null; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; Labels: { [key: string]: string; }; JobCancelRequest: { reason?: string; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.components.responses

**Поле.** Код: [web/admin/src/api/generated/llm.ts:709](../../../../../../web/admin/src/api/generated/llm.ts#L709).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; BadRequest: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PayloadTooLarge: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.components.parameters

**Поле.** Код: [web/admin/src/api/generated/llm.ts:785](../../../../../../web/admin/src/api/generated/llm.ts#L785).

```typescript
parameters: { IfMatch: string; IdempotencyKey: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/llm.ts:802](../../../../../../web/admin/src/api/generated/llm.ts#L802).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.components.headers

**Поле.** Код: [web/admin/src/api/generated/llm.ts:803](../../../../../../web/admin/src/api/generated/llm.ts#L803).

```typescript
headers: { IdempotencyReplayed: boolean; Location: string; RetryAfter: number; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/llm.ts:811](../../../../../../web/admin/src/api/generated/llm.ts#L811).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.$defs

**Тип.** Код: [web/admin/src/api/generated/llm.ts:813](../../../../../../web/admin/src/api/generated/llm.ts#L813).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.llm.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/llm.ts:814](../../../../../../web/admin/src/api/generated/llm.ts#L814).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.llm.md#adminapigeneratedllmoperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.llm.md#adminapigeneratedllmoperationsgetserviceinfo) | Поле | ні |
| [listProviders](api.generated.llm.md#adminapigeneratedllmoperationslistproviders) | Поле | ні |
| [getProvider](api.generated.llm.md#adminapigeneratedllmoperationsgetprovider) | Поле | ні |
| [putProvider](api.generated.llm.md#adminapigeneratedllmoperationsputprovider) | Поле | ні |
| [deleteProvider](api.generated.llm.md#adminapigeneratedllmoperationsdeleteprovider) | Поле | ні |
| [listModelAliases](api.generated.llm.md#adminapigeneratedllmoperationslistmodelaliases) | Поле | ні |
| [putModelAlias](api.generated.llm.md#adminapigeneratedllmoperationsputmodelalias) | Поле | ні |
| [createCompletion](api.generated.llm.md#adminapigeneratedllmoperationscreatecompletion) | Поле | ні |
| [listBudgets](api.generated.llm.md#adminapigeneratedllmoperationslistbudgets) | Поле | ні |
| [putBudget](api.generated.llm.md#adminapigeneratedllmoperationsputbudget) | Поле | ні |
| [deleteBudget](api.generated.llm.md#adminapigeneratedllmoperationsdeletebudget) | Поле | ні |
| [getUsage](api.generated.llm.md#adminapigeneratedllmoperationsgetusage) | Поле | ні |
| [getJob](api.generated.llm.md#adminapigeneratedllmoperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.llm.md#adminapigeneratedllmoperationscanceljob) | Поле | ні |

## admin.api.generated.llm.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/llm.ts:815](../../../../../../web/admin/src/api/generated/llm.ts#L815).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/llm.ts:844](../../../../../../web/admin/src/api/generated/llm.ts#L844).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.listProviders

**Поле.** Код: [web/admin/src/api/generated/llm.ts:865](../../../../../../web/admin/src/api/generated/llm.ts#L865).

```typescript
listProviders: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["Provider"][]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.getProvider

**Поле.** Код: [web/admin/src/api/generated/llm.ts:888](../../../../../../web/admin/src/api/generated/llm.ts#L888).

```typescript
getProvider: { parameters: { query?: never; header?: never; path: { provider_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Provider"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.putProvider

**Поле.** Код: [web/admin/src/api/generated/llm.ts:912](../../../../../../web/admin/src/api/generated/llm.ts#L912).

```typescript
putProvider: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { provider_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["Provider"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Provider"]; }; }; 401: components["responses"]["Unauthenticated"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.deleteProvider

**Поле.** Код: [web/admin/src/api/generated/llm.ts:947](../../../../../../web/admin/src/api/generated/llm.ts#L947).

```typescript
deleteProvider: { parameters: { query?: never; header?: never; path: { provider_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.listModelAliases

**Поле.** Код: [web/admin/src/api/generated/llm.ts:969](../../../../../../web/admin/src/api/generated/llm.ts#L969).

```typescript
listModelAliases: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["ModelAlias"][]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.putModelAlias

**Поле.** Код: [web/admin/src/api/generated/llm.ts:992](../../../../../../web/admin/src/api/generated/llm.ts#L992).

```typescript
putModelAlias: { parameters: { query?: never; header?: never; path: { alias: string; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["ModelAlias"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ModelAlias"]; }; }; 401: components["responses"]["Unauthenticated"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.createCompletion

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1020](../../../../../../web/admin/src/api/generated/llm.ts#L1020).

```typescript
createCompletion: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["CompletionRequest"]; }; }; responses: { 200: { headers: { "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["CompletionResult"]; }; }; 202: components["responses"]["JobAccepted"]; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; 413: components["responses"]["PayloadTooLarge"]; 422: components["responses"]["UnprocessableEntity"]; 429: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 502: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.listBudgets

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1085](../../../../../../web/admin/src/api/generated/llm.ts#L1085).

```typescript
listBudgets: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["BudgetDefinition"][]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.putBudget

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1108](../../../../../../web/admin/src/api/generated/llm.ts#L1108).

```typescript
putBudget: { parameters: { query?: never; header?: never; path: { scope_type: components["schemas"]["ScopeType"]; scope_id: string; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["BudgetDefinition"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["BudgetDefinition"]; }; }; 401: components["responses"]["Unauthenticated"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.deleteBudget

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1137](../../../../../../web/admin/src/api/generated/llm.ts#L1137).

```typescript
deleteBudget: { parameters: { query?: never; header?: never; path: { scope_type: components["schemas"]["ScopeType"]; scope_id: string; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.getUsage

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1160](../../../../../../web/admin/src/api/generated/llm.ts#L1160).

```typescript
getUsage: { parameters: { query?: { scope_type?: components["schemas"]["ScopeType"]; scope_id?: string; since?: string; until?: string; group_by?: "day" | "model" | "purpose" | "scope"; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["UsageReport"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1187](../../../../../../web/admin/src/api/generated/llm.ts#L1187).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.llm.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/llm.ts:1211](../../../../../../web/admin/src/api/generated/llm.ts#L1211).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
