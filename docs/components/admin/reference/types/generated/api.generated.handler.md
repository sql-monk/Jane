# api/generated/handler

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.handler.paths](#adminapigeneratedhandlerpaths)
- [admin.api.generated.handler.paths./v1/health](#adminapigeneratedhandlerpathsv1health)
- [admin.api.generated.handler.paths./v1/info](#adminapigeneratedhandlerpathsv1info)
- [admin.api.generated.handler.paths./v1/invocations](#adminapigeneratedhandlerpathsv1invocations)
- [admin.api.generated.handler.paths./v1/invocations/{invocation_id}](#adminapigeneratedhandlerpathsv1invocationsinvocation_id)
- [admin.api.generated.handler.paths./v1/test-runs](#adminapigeneratedhandlerpathsv1test-runs)
- [admin.api.generated.handler.paths./v1/connections](#adminapigeneratedhandlerpathsv1connections)
- [admin.api.generated.handler.paths./v1/connections/{connection_id}](#adminapigeneratedhandlerpathsv1connectionsconnection_id)
- [admin.api.generated.handler.paths./v1/connections/{connection_id}/test](#adminapigeneratedhandlerpathsv1connectionsconnection_idtest)
- [admin.api.generated.handler.paths./v1/jobs/{job_id}](#adminapigeneratedhandlerpathsv1jobsjob_id)
- [admin.api.generated.handler.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedhandlerpathsv1jobsjob_idcancel)
- [admin.api.generated.handler.webhooks](#adminapigeneratedhandlerwebhooks)
- [admin.api.generated.handler.components](#adminapigeneratedhandlercomponents)
- [admin.api.generated.handler.components.schemas](#adminapigeneratedhandlercomponentsschemas)
- [admin.api.generated.handler.components.responses](#adminapigeneratedhandlercomponentsresponses)
- [admin.api.generated.handler.components.parameters](#adminapigeneratedhandlercomponentsparameters)
- [admin.api.generated.handler.components.requestBodies](#adminapigeneratedhandlercomponentsrequestbodies)
- [admin.api.generated.handler.components.headers](#adminapigeneratedhandlercomponentsheaders)
- [admin.api.generated.handler.components.pathItems](#adminapigeneratedhandlercomponentspathitems)
- [admin.api.generated.handler.$defs](#adminapigeneratedhandlerdefs)
- [admin.api.generated.handler.operations](#adminapigeneratedhandleroperations)
- [admin.api.generated.handler.operations.getHealth](#adminapigeneratedhandleroperationsgethealth)
- [admin.api.generated.handler.operations.getServiceInfo](#adminapigeneratedhandleroperationsgetserviceinfo)
- [admin.api.generated.handler.operations.invokeHandler](#adminapigeneratedhandleroperationsinvokehandler)
- [admin.api.generated.handler.operations.getInvocation](#adminapigeneratedhandleroperationsgetinvocation)
- [admin.api.generated.handler.operations.startTestRun](#adminapigeneratedhandleroperationsstarttestrun)
- [admin.api.generated.handler.operations.listConnections](#adminapigeneratedhandleroperationslistconnections)
- [admin.api.generated.handler.operations.getConnection](#adminapigeneratedhandleroperationsgetconnection)
- [admin.api.generated.handler.operations.putConnection](#adminapigeneratedhandleroperationsputconnection)
- [admin.api.generated.handler.operations.deleteConnection](#adminapigeneratedhandleroperationsdeleteconnection)
- [admin.api.generated.handler.operations.testConnection](#adminapigeneratedhandleroperationstestconnection)
- [admin.api.generated.handler.operations.getJob](#adminapigeneratedhandleroperationsgetjob)
- [admin.api.generated.handler.operations.cancelJob](#adminapigeneratedhandleroperationscanceljob)

## admin.api.generated.handler.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/handler.ts:3](../../../../../../web/admin/src/api/generated/handler.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.handler.md#adminapigeneratedhandlerpathsv1health) | Поле | ні |
| [/v1/info](api.generated.handler.md#adminapigeneratedhandlerpathsv1info) | Поле | ні |
| [/v1/invocations](api.generated.handler.md#adminapigeneratedhandlerpathsv1invocations) | Поле | ні |
| [/v1/invocations/{invocation_id}](api.generated.handler.md#adminapigeneratedhandlerpathsv1invocationsinvocation_id) | Поле | ні |
| [/v1/test-runs](api.generated.handler.md#adminapigeneratedhandlerpathsv1test-runs) | Поле | ні |
| [/v1/connections](api.generated.handler.md#adminapigeneratedhandlerpathsv1connections) | Поле | ні |
| [/v1/connections/{connection_id}](api.generated.handler.md#adminapigeneratedhandlerpathsv1connectionsconnection_id) | Поле | ні |
| [/v1/connections/{connection_id}/test](api.generated.handler.md#adminapigeneratedhandlerpathsv1connectionsconnection_idtest) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.handler.md#adminapigeneratedhandlerpathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.handler.md#adminapigeneratedhandlerpathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.handler.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/handler.ts:4](../../../../../../web/admin/src/api/generated/handler.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/handler.ts:21](../../../../../../web/admin/src/api/generated/handler.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/invocations

**Поле.** Код: [web/admin/src/api/generated/handler.ts:38](../../../../../../web/admin/src/api/generated/handler.ts#L38).

```typescript
/v1/invocations: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["invokeHandler"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/invocations/{invocation_id}

**Поле.** Код: [web/admin/src/api/generated/handler.ts:62](../../../../../../web/admin/src/api/generated/handler.ts#L62).

```typescript
/v1/invocations/{invocation_id}: { parameters: { query?: never; header?: never; path: { invocation_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getInvocation"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/test-runs

**Поле.** Код: [web/admin/src/api/generated/handler.ts:81](../../../../../../web/admin/src/api/generated/handler.ts#L81).

```typescript
/v1/test-runs: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["startTestRun"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/connections

**Поле.** Код: [web/admin/src/api/generated/handler.ts:103](../../../../../../web/admin/src/api/generated/handler.ts#L103).

```typescript
/v1/connections: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listConnections"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/connections/{connection_id}

**Поле.** Код: [web/admin/src/api/generated/handler.ts:123](../../../../../../web/admin/src/api/generated/handler.ts#L123).

```typescript
/v1/connections/{connection_id}: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get: operations["getConnection"]; put: operations["putConnection"]; post?: never; delete: operations["deleteConnection"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/connections/{connection_id}/test

**Поле.** Код: [web/admin/src/api/generated/handler.ts:150](../../../../../../web/admin/src/api/generated/handler.ts#L150).

```typescript
/v1/connections/{connection_id}/test: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["testConnection"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/handler.ts:169](../../../../../../web/admin/src/api/generated/handler.ts#L169).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/handler.ts:188](../../../../../../web/admin/src/api/generated/handler.ts#L188).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.webhooks

**Тип.** Код: [web/admin/src/api/generated/handler.ts:213](../../../../../../web/admin/src/api/generated/handler.ts#L213).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.handler.components

**Інтерфейс.** Код: [web/admin/src/api/generated/handler.ts:214](../../../../../../web/admin/src/api/generated/handler.ts#L214).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.handler.md#adminapigeneratedhandlercomponentsschemas) | Поле | ні |
| [responses](api.generated.handler.md#adminapigeneratedhandlercomponentsresponses) | Поле | ні |
| [parameters](api.generated.handler.md#adminapigeneratedhandlercomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.handler.md#adminapigeneratedhandlercomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.handler.md#adminapigeneratedhandlercomponentsheaders) | Поле | ні |
| [pathItems](api.generated.handler.md#adminapigeneratedhandlercomponentspathitems) | Поле | ні |

## admin.api.generated.handler.components.schemas

**Поле.** Код: [web/admin/src/api/generated/handler.ts:215](../../../../../../web/admin/src/api/generated/handler.ts#L215).

```typescript
schemas: { TestRunRequest: { handler: components["schemas"]["package-ref.schema"]; package_archive?: components["schemas"]["content-ref.schema"]; tests?: ("all" | "none") | string[]; extra_cases?: { name: string; input: components["schemas"]["HandlerInput"]; params?: Record<string, unknown>; expected_status: components["schemas"]["HandlerStatus"]; expected?: components["schemas"]["HandlerOutput"]; compare?: "exact" | "subset"; }[]; params?: Record<string, unknown>; limits?: components["schemas"]["limits.schema"]; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; Id: string; Slug: string; SourceKind: string; Timestamp: string; MediaType: string; Sha256Hex: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; "material.schema": { material_id: components["schemas"]["Id"]; observation_id: components["schemas"]["Id"]; source: { source_id?: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; name?: string; }; locator: { url?: string; final_url?: string; canonical_url?: string; telegram?: { channel_id: string; channel_username?: string; message_id: number; grouped_id?: string; }; }; fetched_at: components["schemas"]["Timestamp"]; published_at?: components["schemas"]["Timestamp"]; edited_at?: components["schemas"]["Timestamp"]; format: { media_type: components["schemas"]["MediaType"]; charset?: string; language?: string; content_kind?: string; }; revision: { content_sha256: components["schemas"]["Sha256Hex"]; source_revision?: string; sequence?: number; is_edit?: boolean; }; content: components["schemas"]["content-ref.schema"]; attachments?: { name: string; role?: string; content: components["schemas"]["content-ref.schema"]; }[]; http?: { status?: number; headers?: { [key: string]: string; }; redirects?: string[]; }; discovery?: { strategy?: string; parent_url?: string; depth?: number; section?: string; priority?: number; }; collector: { name: string; version: string; rules?: components["schemas"]["package-ref.schema"]; collection_id?: components["schemas"]["Id"]; }; diagnostics?: components["schemas"]["DiagnosticMessage"][]; metadata?: Record<string, unknown>; }; MaterialInput: { kind: "material"; material: components["schemas"]["material.schema"]; }; EntityKey: { scope: string; natural: { [key: string]: string | number | boolean; }; }; ObservationOrder: { observation_id: components["schemas"]["Id"]; observed_at: components["schemas"]["Timestamp"]; sequence?: number; material_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; }; "entity.schema": { entity_type: string; schema?: string; key: components["schemas"]["EntityKey"]; fields: { [key: string]: unknown; }; cleared?: string[]; completeness?: "full" | "partial"; observation: components["schemas"]["ObservationOrder"]; provenance?: components["schemas"]["Provenance"]; confidence?: number; }; Provenance: { package?: components["schemas"]["package-ref.schema"]; invocation_id?: components["schemas"]["Id"]; run_id?: components["schemas"]["Id"]; stage_id?: components["schemas"]["Slug"]; }; EntitiesInput: { kind: "entities"; entities?: components["schemas"]["entity.schema"][]; entities_ref?: components["schemas"]["content-ref.schema"]; from_invocation_id?: components["schemas"]["Id"]; material?: components["schemas"]["material.schema"]; } | unknown | unknown; DataInput: { kind: "data"; data?: unknown; data_ref?: components["schemas"]["content-ref.schema"]; from_invocation_id?: components["schemas"]["Id"]; } | unknown | unknown; unrecognized: { partial: boolean; reason?: string; signature?: string; }; failure: { kind: "execution_error" | "schema_mismatch" | "timeout" | "resource_exceeded" | "sandbox_violation" | "dependency_error" | "connection_error" | "budget_exhausted" | "invalid_params"; message: string; retryable?: boolean; details?: Record<string, unknown>; }; Diagnostics: { messages?: components["schemas"]["DiagnosticMessage"][]; validation_errors?: { pointer: string; message: string; schema_pointer?: string; }[]; metrics?: { duration_ms?: number; cpu_ms?: number; peak_memory_mb?: number; output_bytes?: number; }; logs_ref?: components["schemas"]["content-ref.schema"]; }; StoredObjectRef: { object_id: components["schemas"]["Id"]; adapter: string; connection_id?: components["schemas"]["Slug"]; locator?: { [key: string]: string | number; }; media_type?: components["schemas"]["MediaType"]; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; content?: components["schemas"]["content-ref.schema"]; }; WriteAck: { status: "written" | "duplicate" | "stale" | "partially_stale" | "simulated"; target: { adapter: string; connection_id?: components["schemas"]["Slug"]; }; object?: components["schemas"]["StoredObjectRef"]; entity?: { entity_type?: string; canonical_key?: string; version?: number; }; applied_fields?: string[]; stale_fields?: string[]; delivery_key?: string; }; TraceContext: { trace_id?: string; run_id?: components["schemas"]["Id"]; task_id?: components["schemas"]["Slug"]; stage_id?: components["schemas"]["Slug"]; source_id?: components["schemas"]["Slug"]; }; HandlerInput: components["schemas"]["MaterialInput"] | components["schemas"]["EntitiesInput"] | components["schemas"]["DataInput"]; InvocationContext: { trace?: components["schemas"]["TraceContext"]; attempt?: number; test_mode?: boolean; requested_by?: string; }; Delivery: { delivery_key: string; }; "handler-invocation.schema": { handler: components["schemas"]["package-ref.schema"]; package_archive?: components["schemas"]["content-ref.schema"]; params?: Record<string, unknown>; inputs: components["schemas"]["HandlerInput"][]; connections?: { [key: string]: components["schemas"]["Slug"]; }; context?: components["schemas"]["InvocationContext"]; delivery: components["schemas"]["Delivery"]; limits?: components["schemas"]["limits.schema"]; mode?: "sync" | "async"; }; Money: { amount: number; currency: string; }; HandlerStatus: "success" | "empty" | "unrecognized" | "failed"; "handler-result.schema": { invocation_id: components["schemas"]["Id"]; handler: components["schemas"]["package-ref.schema"]; handler_kind: components["schemas"]["HandlerKind"]; status: components["schemas"]["HandlerStatus"]; inputs: components["schemas"]["InputRef"][]; output?: components["schemas"]["HandlerOutput"]; unrecognized?: { partial: boolean; reason?: string; signature?: string; }; failure?: { kind: "execution_error" | "schema_mismatch" | "timeout" | "resource_exceeded" | "sandbox_violation" | "dependency_error" | "connection_error" | "budget_exhausted" | "invalid_params"; message: string; retryable?: boolean; details?: Record<string, unknown>; }; diagnostics?: components["schemas"]["Diagnostics"]; usage?: components["schemas"]["Usage"]; delivery_key?: string; duplicate?: boolean; test_mode?: boolean; started_at: components["schemas"]["Timestamp"]; finished_at: components["schemas"]["Timestamp"]; } & (unknown & unknown); TestCaseResult: { name: string; passed: boolean; expected_status?: components["schemas"]["HandlerStatus"]; actual_status?: components["schemas"]["HandlerStatus"]; differences?: { pointer: string; expected?: unknown; actual?: unknown; }[]; result?: components["schemas"]["handler-result.schema"]; }; HandlerKind: "extractor" | "storage" | "llm" | "transform" | "collector-rules"; InputRef: { kind: "material" | "entities" | "data"; material_id?: components["schemas"]["Id"]; observation_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; from_invocation_id?: components["schemas"]["Id"]; }; HandlerOutput: { entities?: components["schemas"]["entity.schema"][]; entities_ref?: components["schemas"]["content-ref.schema"]; data?: unknown; data_ref?: components["schemas"]["content-ref.schema"]; writes?: components["schemas"]["WriteAck"][]; }; Usage: { llm?: { provider?: string; model?: string; input_tokens?: number; output_tokens?: number; cost?: components["schemas"]["Money"]; }; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; NextCursor: string | null; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; Labels: { [key: string]: string; }; ConnectionKind: string; SecretRef: string; "connection.schema": { connection_id: components["schemas"]["Slug"]; kind: components["schemas"]["ConnectionKind"]; title?: string; params?: { [key: string]: string | number | boolean | unknown[] | Record<string, unknown>; }; secret_refs?: { [key: string]: components["schemas"]["SecretRef"]; }; labels?: components["schemas"]["Labels"]; }; ConnectionList: { items: components["schemas"]["connection.schema"][]; next_cursor: components["schemas"]["NextCursor"]; }; ConnectionTestResult: { ok: boolean; checked_at: components["schemas"]["Timestamp"]; latency_ms?: number; secrets_resolved?: { [key: string]: boolean; }; message?: string; }; JobCancelRequest: { reason?: string; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.components.responses

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1059](../../../../../../web/admin/src/api/generated/handler.ts#L1059).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; BadRequest: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PayloadTooLarge: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; TooManyRequests: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; ServiceUnavailable: { headers: { "Retry-After": components["headers"]["RetryAfter"]; [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.components.parameters

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1155](../../../../../../web/admin/src/api/generated/handler.ts#L1155).

```typescript
parameters: { IdempotencyKey: string; Traceparent: string; Cursor: string; Limit: number; ConnectionId: components["schemas"]["Slug"]; IfMatch: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1179](../../../../../../web/admin/src/api/generated/handler.ts#L1179).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.components.headers

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1180](../../../../../../web/admin/src/api/generated/handler.ts#L1180).

```typescript
headers: { IdempotencyReplayed: boolean; Location: string; RetryAfter: number; ETag: string; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1190](../../../../../../web/admin/src/api/generated/handler.ts#L1190).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.$defs

**Тип.** Код: [web/admin/src/api/generated/handler.ts:1192](../../../../../../web/admin/src/api/generated/handler.ts#L1192).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.handler.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/handler.ts:1193](../../../../../../web/admin/src/api/generated/handler.ts#L1193).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.handler.md#adminapigeneratedhandleroperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.handler.md#adminapigeneratedhandleroperationsgetserviceinfo) | Поле | ні |
| [invokeHandler](api.generated.handler.md#adminapigeneratedhandleroperationsinvokehandler) | Поле | ні |
| [getInvocation](api.generated.handler.md#adminapigeneratedhandleroperationsgetinvocation) | Поле | ні |
| [startTestRun](api.generated.handler.md#adminapigeneratedhandleroperationsstarttestrun) | Поле | ні |
| [listConnections](api.generated.handler.md#adminapigeneratedhandleroperationslistconnections) | Поле | ні |
| [getConnection](api.generated.handler.md#adminapigeneratedhandleroperationsgetconnection) | Поле | ні |
| [putConnection](api.generated.handler.md#adminapigeneratedhandleroperationsputconnection) | Поле | ні |
| [deleteConnection](api.generated.handler.md#adminapigeneratedhandleroperationsdeleteconnection) | Поле | ні |
| [testConnection](api.generated.handler.md#adminapigeneratedhandleroperationstestconnection) | Поле | ні |
| [getJob](api.generated.handler.md#adminapigeneratedhandleroperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.handler.md#adminapigeneratedhandleroperationscanceljob) | Поле | ні |

## admin.api.generated.handler.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1194](../../../../../../web/admin/src/api/generated/handler.ts#L1194).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1223](../../../../../../web/admin/src/api/generated/handler.ts#L1223).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.invokeHandler

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1244](../../../../../../web/admin/src/api/generated/handler.ts#L1244).

```typescript
invokeHandler: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; traceparent?: components["parameters"]["Traceparent"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["handler-invocation.schema"]; }; }; responses: { 200: { headers: { "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["handler-result.schema"]; }; }; 202: components["responses"]["JobAccepted"]; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 404: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 409: components["responses"]["Conflict"]; 413: components["responses"]["PayloadTooLarge"]; 422: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 429: components["responses"]["TooManyRequests"]; 502: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 503: components["responses"]["ServiceUnavailable"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.getInvocation

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1315](../../../../../../web/admin/src/api/generated/handler.ts#L1315).

```typescript
getInvocation: { parameters: { query?: never; header?: never; path: { invocation_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["handler-result.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.startTestRun

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1339](../../../../../../web/admin/src/api/generated/handler.ts#L1339).

```typescript
startTestRun: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["TestRunRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.listConnections

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1369](../../../../../../web/admin/src/api/generated/handler.ts#L1369).

```typescript
listConnections: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionList"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.getConnection

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1395](../../../../../../web/admin/src/api/generated/handler.ts#L1395).

```typescript
getConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.putConnection

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1420](../../../../../../web/admin/src/api/generated/handler.ts#L1420).

```typescript
putConnection: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["connection.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 201: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; 501: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.deleteConnection

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1475](../../../../../../web/admin/src/api/generated/handler.ts#L1475).

```typescript
deleteConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.testConnection

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1497](../../../../../../web/admin/src/api/generated/handler.ts#L1497).

```typescript
testConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionTestResult"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1521](../../../../../../web/admin/src/api/generated/handler.ts#L1521).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.handler.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/handler.ts:1545](../../../../../../web/admin/src/api/generated/handler.ts#L1545).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
