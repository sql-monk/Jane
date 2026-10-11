# api/generated/storage

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.storage.paths](#adminapigeneratedstoragepaths)
- [admin.api.generated.storage.paths./v1/health](#adminapigeneratedstoragepathsv1health)
- [admin.api.generated.storage.paths./v1/info](#adminapigeneratedstoragepathsv1info)
- [admin.api.generated.storage.paths./v1/connections](#adminapigeneratedstoragepathsv1connections)
- [admin.api.generated.storage.paths./v1/connections/{connection_id}](#adminapigeneratedstoragepathsv1connectionsconnection_id)
- [admin.api.generated.storage.paths./v1/connections/{connection_id}/test](#adminapigeneratedstoragepathsv1connectionsconnection_idtest)
- [admin.api.generated.storage.paths./v1/storage-status/checks](#adminapigeneratedstoragepathsv1storage-statuschecks)
- [admin.api.generated.storage.paths./v1/jobs/{job_id}](#adminapigeneratedstoragepathsv1jobsjob_id)
- [admin.api.generated.storage.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedstoragepathsv1jobsjob_idcancel)
- [admin.api.generated.storage.paths./v1/storage-status](#adminapigeneratedstoragepathsv1storage-status)
- [admin.api.generated.storage.paths./v1/entities](#adminapigeneratedstoragepathsv1entities)
- [admin.api.generated.storage.paths./v1/entity-history](#adminapigeneratedstoragepathsv1entity-history)
- [admin.api.generated.storage.paths./v1/objects](#adminapigeneratedstoragepathsv1objects)
- [admin.api.generated.storage.paths./v1/objects/{object_id}](#adminapigeneratedstoragepathsv1objectsobject_id)
- [admin.api.generated.storage.paths./v1/objects/{object_id}/content](#adminapigeneratedstoragepathsv1objectsobject_idcontent)
- [admin.api.generated.storage.webhooks](#adminapigeneratedstoragewebhooks)
- [admin.api.generated.storage.components](#adminapigeneratedstoragecomponents)
- [admin.api.generated.storage.components.schemas](#adminapigeneratedstoragecomponentsschemas)
- [admin.api.generated.storage.components.responses](#adminapigeneratedstoragecomponentsresponses)
- [admin.api.generated.storage.components.parameters](#adminapigeneratedstoragecomponentsparameters)
- [admin.api.generated.storage.components.requestBodies](#adminapigeneratedstoragecomponentsrequestbodies)
- [admin.api.generated.storage.components.headers](#adminapigeneratedstoragecomponentsheaders)
- [admin.api.generated.storage.components.pathItems](#adminapigeneratedstoragecomponentspathitems)
- [admin.api.generated.storage.$defs](#adminapigeneratedstoragedefs)
- [admin.api.generated.storage.operations](#adminapigeneratedstorageoperations)
- [admin.api.generated.storage.operations.getHealth](#adminapigeneratedstorageoperationsgethealth)
- [admin.api.generated.storage.operations.getServiceInfo](#adminapigeneratedstorageoperationsgetserviceinfo)
- [admin.api.generated.storage.operations.listConnections](#adminapigeneratedstorageoperationslistconnections)
- [admin.api.generated.storage.operations.getConnection](#adminapigeneratedstorageoperationsgetconnection)
- [admin.api.generated.storage.operations.putConnection](#adminapigeneratedstorageoperationsputconnection)
- [admin.api.generated.storage.operations.deleteConnection](#adminapigeneratedstorageoperationsdeleteconnection)
- [admin.api.generated.storage.operations.testConnection](#adminapigeneratedstorageoperationstestconnection)
- [admin.api.generated.storage.operations.checkStorageStatus](#adminapigeneratedstorageoperationscheckstoragestatus)
- [admin.api.generated.storage.operations.getJob](#adminapigeneratedstorageoperationsgetjob)
- [admin.api.generated.storage.operations.cancelJob](#adminapigeneratedstorageoperationscanceljob)
- [admin.api.generated.storage.operations.getStorageStatus](#adminapigeneratedstorageoperationsgetstoragestatus)
- [admin.api.generated.storage.operations.listEntities](#adminapigeneratedstorageoperationslistentities)
- [admin.api.generated.storage.operations.listEntityHistory](#adminapigeneratedstorageoperationslistentityhistory)
- [admin.api.generated.storage.operations.listObjects](#adminapigeneratedstorageoperationslistobjects)
- [admin.api.generated.storage.operations.getObject](#adminapigeneratedstorageoperationsgetobject)
- [admin.api.generated.storage.operations.getObjectContent](#adminapigeneratedstorageoperationsgetobjectcontent)

## admin.api.generated.storage.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/storage.ts:3](../../../../../../web/admin/src/api/generated/storage.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.storage.md#adminapigeneratedstoragepathsv1health) | Поле | ні |
| [/v1/info](api.generated.storage.md#adminapigeneratedstoragepathsv1info) | Поле | ні |
| [/v1/connections](api.generated.storage.md#adminapigeneratedstoragepathsv1connections) | Поле | ні |
| [/v1/connections/{connection_id}](api.generated.storage.md#adminapigeneratedstoragepathsv1connectionsconnection_id) | Поле | ні |
| [/v1/connections/{connection_id}/test](api.generated.storage.md#adminapigeneratedstoragepathsv1connectionsconnection_idtest) | Поле | ні |
| [/v1/storage-status/checks](api.generated.storage.md#adminapigeneratedstoragepathsv1storage-statuschecks) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.storage.md#adminapigeneratedstoragepathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.storage.md#adminapigeneratedstoragepathsv1jobsjob_idcancel) | Поле | ні |
| [/v1/storage-status](api.generated.storage.md#adminapigeneratedstoragepathsv1storage-status) | Поле | ні |
| [/v1/entities](api.generated.storage.md#adminapigeneratedstoragepathsv1entities) | Поле | ні |
| [/v1/entity-history](api.generated.storage.md#adminapigeneratedstoragepathsv1entity-history) | Поле | ні |
| [/v1/objects](api.generated.storage.md#adminapigeneratedstoragepathsv1objects) | Поле | ні |
| [/v1/objects/{object_id}](api.generated.storage.md#adminapigeneratedstoragepathsv1objectsobject_id) | Поле | ні |
| [/v1/objects/{object_id}/content](api.generated.storage.md#adminapigeneratedstoragepathsv1objectsobject_idcontent) | Поле | ні |

## admin.api.generated.storage.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/storage.ts:4](../../../../../../web/admin/src/api/generated/storage.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/storage.ts:21](../../../../../../web/admin/src/api/generated/storage.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/connections

**Поле.** Код: [web/admin/src/api/generated/storage.ts:38](../../../../../../web/admin/src/api/generated/storage.ts#L38).

```typescript
/v1/connections: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listConnections"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/connections/{connection_id}

**Поле.** Код: [web/admin/src/api/generated/storage.ts:58](../../../../../../web/admin/src/api/generated/storage.ts#L58).

```typescript
/v1/connections/{connection_id}: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get: operations["getConnection"]; put: operations["putConnection"]; post?: never; delete: operations["deleteConnection"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/connections/{connection_id}/test

**Поле.** Код: [web/admin/src/api/generated/storage.ts:85](../../../../../../web/admin/src/api/generated/storage.ts#L85).

```typescript
/v1/connections/{connection_id}/test: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["testConnection"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/storage-status/checks

**Поле.** Код: [web/admin/src/api/generated/storage.ts:104](../../../../../../web/admin/src/api/generated/storage.ts#L104).

```typescript
/v1/storage-status/checks: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["checkStorageStatus"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/storage.ts:121](../../../../../../web/admin/src/api/generated/storage.ts#L121).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/storage.ts:140](../../../../../../web/admin/src/api/generated/storage.ts#L140).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/storage-status

**Поле.** Код: [web/admin/src/api/generated/storage.ts:164](../../../../../../web/admin/src/api/generated/storage.ts#L164).

```typescript
/v1/storage-status: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getStorageStatus"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/entities

**Поле.** Код: [web/admin/src/api/generated/storage.ts:184](../../../../../../web/admin/src/api/generated/storage.ts#L184).

```typescript
/v1/entities: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listEntities"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/entity-history

**Поле.** Код: [web/admin/src/api/generated/storage.ts:201](../../../../../../web/admin/src/api/generated/storage.ts#L201).

```typescript
/v1/entity-history: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listEntityHistory"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects

**Поле.** Код: [web/admin/src/api/generated/storage.ts:218](../../../../../../web/admin/src/api/generated/storage.ts#L218).

```typescript
/v1/objects: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listObjects"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects/{object_id}

**Поле.** Код: [web/admin/src/api/generated/storage.ts:235](../../../../../../web/admin/src/api/generated/storage.ts#L235).

```typescript
/v1/objects/{object_id}: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getObject"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects/{object_id}/content

**Поле.** Код: [web/admin/src/api/generated/storage.ts:267](../../../../../../web/admin/src/api/generated/storage.ts#L267).

```typescript
/v1/objects/{object_id}/content: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getObjectContent"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.webhooks

**Тип.** Код: [web/admin/src/api/generated/storage.ts:289](../../../../../../web/admin/src/api/generated/storage.ts#L289).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.storage.components

**Інтерфейс.** Код: [web/admin/src/api/generated/storage.ts:290](../../../../../../web/admin/src/api/generated/storage.ts#L290).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.storage.md#adminapigeneratedstoragecomponentsschemas) | Поле | ні |
| [responses](api.generated.storage.md#adminapigeneratedstoragecomponentsresponses) | Поле | ні |
| [parameters](api.generated.storage.md#adminapigeneratedstoragecomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.storage.md#adminapigeneratedstoragecomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.storage.md#adminapigeneratedstoragecomponentsheaders) | Поле | ні |
| [pathItems](api.generated.storage.md#adminapigeneratedstoragecomponentspathitems) | Поле | ні |

## admin.api.generated.storage.components.schemas

**Поле.** Код: [web/admin/src/api/generated/storage.ts:291](../../../../../../web/admin/src/api/generated/storage.ts#L291).

```typescript
schemas: { StoredObject: { object: components["schemas"]["StoredObjectRef"]; material?: { material_id?: string; observation_id?: string; source_id?: string; url?: string; fetched_at?: string; }; stored_at: components["schemas"]["Timestamp"]; }; StoredObjectDetail: { object: components["schemas"]["StoredObjectRef"]; stored_at: components["schemas"]["Timestamp"]; material?: components["schemas"]["material.schema"]; }; StorageStatus: { connection_id: string; kind: string; availability: "unknown" | "available" | "unavailable"; checked_at: string | null; message: string | null; statistics: { object_count: number | null; total_size_bytes: number | null; checked_at: string | null; scope: "connection_objects"; unavailable_reason: string | null; }; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; ConnectionKind: string; Timestamp: string; Slug: string; SecretRef: string; Labels: { [key: string]: string; }; "connection.schema": { connection_id: components["schemas"]["Slug"]; kind: components["schemas"]["ConnectionKind"]; title?: string; params?: { [key: string]: string | number | boolean | unknown[] | Record<string, unknown>; }; secret_refs?: { [key: string]: components["schemas"]["SecretRef"]; }; labels?: components["schemas"]["Labels"]; }; NextCursor: string | null; ConnectionList: { items: components["schemas"]["connection.schema"][]; next_cursor: components["schemas"]["NextCursor"]; }; ConnectionTestResult: { ok: boolean; checked_at: components["schemas"]["Timestamp"]; latency_ms?: number; secrets_resolved?: { [key: string]: boolean; }; message?: string; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; Id: string; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; MediaType: string; Sha256Hex: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; JobCancelRequest: { reason?: string; }; EntityKey: { scope: string; natural: { [key: string]: string | number | boolean; }; }; ObservationOrder: { observation_id: components["schemas"]["Id"]; observed_at: components["schemas"]["Timestamp"]; sequence?: number; material_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; }; EntityState: { entity_type: string; key: components["schemas"]["EntityKey"]; canonical_key?: string; fields: Record<string, unknown>; field_orders?: { [key: string]: components["schemas"]["ObservationOrder"]; }; cleared_fields?: string[]; version?: number; updated_at: components["schemas"]["Timestamp"]; }; SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; Provenance: { package?: components["schemas"]["package-ref.schema"]; invocation_id?: components["schemas"]["Id"]; run_id?: components["schemas"]["Id"]; stage_id?: components["schemas"]["Slug"]; }; "entity.schema": { entity_type: string; schema?: string; key: components["schemas"]["EntityKey"]; fields: { [key: string]: unknown; }; cleared?: string[]; completeness?: "full" | "partial"; observation: components["schemas"]["ObservationOrder"]; provenance?: components["schemas"]["Provenance"]; confidence?: number; }; EntityHistoryEntry: { record: components["schemas"]["entity.schema"]; received_at: components["schemas"]["Timestamp"]; delivery_key?: string; applied_fields: string[]; stale_fields: string[]; }; StoredObjectRef: { object_id: components["schemas"]["Id"]; adapter: string; connection_id?: components["schemas"]["Slug"]; locator?: { [key: string]: string | number; }; media_type?: components["schemas"]["MediaType"]; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; content?: components["schemas"]["content-ref.schema"]; }; SourceKind: string; DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; "material.schema": { material_id: components["schemas"]["Id"]; observation_id: components["schemas"]["Id"]; source: { source_id?: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; name?: string; }; locator: { url?: string; final_url?: string; canonical_url?: string; telegram?: { channel_id: string; channel_username?: string; message_id: number; grouped_id?: string; }; }; fetched_at: components["schemas"]["Timestamp"]; published_at?: components["schemas"]["Timestamp"]; edited_at?: components["schemas"]["Timestamp"]; format: { media_type: components["schemas"]["MediaType"]; charset?: string; language?: string; content_kind?: string; }; revision: { content_sha256: components["schemas"]["Sha256Hex"]; source_revision?: string; sequence?: number; is_edit?: boolean; }; content: components["schemas"]["content-ref.schema"]; attachments?: { name: string; role?: string; content: components["schemas"]["content-ref.schema"]; }[]; http?: { status?: number; headers?: { [key: string]: string; }; redirects?: string[]; }; discovery?: { strategy?: string; parent_url?: string; depth?: number; section?: string; priority?: number; }; collector: { name: string; version: string; rules?: components["schemas"]["package-ref.schema"]; collection_id?: components["schemas"]["Id"]; }; diagnostics?: components["schemas"]["DiagnosticMessage"][]; metadata?: Record<string, unknown>; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.responses

**Поле.** Код: [web/admin/src/api/generated/storage.ts:930](../../../../../../web/admin/src/api/generated/storage.ts#L930).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.parameters

**Поле.** Код: [web/admin/src/api/generated/storage.ts:968](../../../../../../web/admin/src/api/generated/storage.ts#L968).

```typescript
parameters: { ConnectionIdQuery: components["schemas"]["Slug"]; Cursor: string; Limit: number; ConnectionId: components["schemas"]["Slug"]; IfMatch: string; IdempotencyKey: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/storage.ts:991](../../../../../../web/admin/src/api/generated/storage.ts#L991).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.headers

**Поле.** Код: [web/admin/src/api/generated/storage.ts:992](../../../../../../web/admin/src/api/generated/storage.ts#L992).

```typescript
headers: { ETag: string; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/storage.ts:996](../../../../../../web/admin/src/api/generated/storage.ts#L996).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.$defs

**Тип.** Код: [web/admin/src/api/generated/storage.ts:998](../../../../../../web/admin/src/api/generated/storage.ts#L998).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.storage.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/storage.ts:999](../../../../../../web/admin/src/api/generated/storage.ts#L999).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.storage.md#adminapigeneratedstorageoperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.storage.md#adminapigeneratedstorageoperationsgetserviceinfo) | Поле | ні |
| [listConnections](api.generated.storage.md#adminapigeneratedstorageoperationslistconnections) | Поле | ні |
| [getConnection](api.generated.storage.md#adminapigeneratedstorageoperationsgetconnection) | Поле | ні |
| [putConnection](api.generated.storage.md#adminapigeneratedstorageoperationsputconnection) | Поле | ні |
| [deleteConnection](api.generated.storage.md#adminapigeneratedstorageoperationsdeleteconnection) | Поле | ні |
| [testConnection](api.generated.storage.md#adminapigeneratedstorageoperationstestconnection) | Поле | ні |
| [checkStorageStatus](api.generated.storage.md#adminapigeneratedstorageoperationscheckstoragestatus) | Поле | ні |
| [getJob](api.generated.storage.md#adminapigeneratedstorageoperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.storage.md#adminapigeneratedstorageoperationscanceljob) | Поле | ні |
| [getStorageStatus](api.generated.storage.md#adminapigeneratedstorageoperationsgetstoragestatus) | Поле | ні |
| [listEntities](api.generated.storage.md#adminapigeneratedstorageoperationslistentities) | Поле | ні |
| [listEntityHistory](api.generated.storage.md#adminapigeneratedstorageoperationslistentityhistory) | Поле | ні |
| [listObjects](api.generated.storage.md#adminapigeneratedstorageoperationslistobjects) | Поле | ні |
| [getObject](api.generated.storage.md#adminapigeneratedstorageoperationsgetobject) | Поле | ні |
| [getObjectContent](api.generated.storage.md#adminapigeneratedstorageoperationsgetobjectcontent) | Поле | ні |

## admin.api.generated.storage.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1000](../../../../../../web/admin/src/api/generated/storage.ts#L1000).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1029](../../../../../../web/admin/src/api/generated/storage.ts#L1029).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listConnections

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1050](../../../../../../web/admin/src/api/generated/storage.ts#L1050).

```typescript
listConnections: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionList"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getConnection

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1076](../../../../../../web/admin/src/api/generated/storage.ts#L1076).

```typescript
getConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.putConnection

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1101](../../../../../../web/admin/src/api/generated/storage.ts#L1101).

```typescript
putConnection: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["connection.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 201: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["connection.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; 501: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.deleteConnection

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1156](../../../../../../web/admin/src/api/generated/storage.ts#L1156).

```typescript
deleteConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.testConnection

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1178](../../../../../../web/admin/src/api/generated/storage.ts#L1178).

```typescript
testConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["parameters"]["ConnectionId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ConnectionTestResult"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.checkStorageStatus

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1202](../../../../../../web/admin/src/api/generated/storage.ts#L1202).

```typescript
checkStorageStatus: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": { connection_id: components["schemas"]["Slug"]; }; }; }; responses: { 202: { headers: { Location?: string; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1255](../../../../../../web/admin/src/api/generated/storage.ts#L1255).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1279](../../../../../../web/admin/src/api/generated/storage.ts#L1279).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getStorageStatus

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1316](../../../../../../web/admin/src/api/generated/storage.ts#L1316).

```typescript
getStorageStatus: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["StorageStatus"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listEntities

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1340](../../../../../../web/admin/src/api/generated/storage.ts#L1340).

```typescript
listEntities: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; entity_type: string; scope?: string; key?: string; updated_since?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["EntityState"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listEntityHistory

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1377](../../../../../../web/admin/src/api/generated/storage.ts#L1377).

```typescript
listEntityHistory: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; entity_type: string; key: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["EntityHistoryEntry"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listObjects

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1410](../../../../../../web/admin/src/api/generated/storage.ts#L1410).

```typescript
listObjects: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; source_id?: string; material_id?: string; material_ids?: string[]; since?: string; until?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["StoredObject"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getObject

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1455](../../../../../../web/admin/src/api/generated/storage.ts#L1455).

```typescript
getObject: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["StoredObjectDetail"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getObjectContent

**Поле.** Код: [web/admin/src/api/generated/storage.ts:1481](../../../../../../web/admin/src/api/generated/storage.ts#L1481).

```typescript
getObjectContent: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/octet-stream": string; "text/html": string; "text/plain": string; "application/json": unknown; "*/*": string; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
