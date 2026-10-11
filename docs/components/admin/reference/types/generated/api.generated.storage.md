# api/generated/storage

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.storage.paths](#adminapigeneratedstoragepaths)
- [admin.api.generated.storage.paths./v1/health](#adminapigeneratedstoragepathsv1health)
- [admin.api.generated.storage.paths./v1/info](#adminapigeneratedstoragepathsv1info)
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

## admin.api.generated.storage.paths./v1/entities

**Поле.** Код: [web/admin/src/api/generated/storage.ts:38](../../../../../../web/admin/src/api/generated/storage.ts#L38).

```typescript
/v1/entities: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listEntities"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/entity-history

**Поле.** Код: [web/admin/src/api/generated/storage.ts:55](../../../../../../web/admin/src/api/generated/storage.ts#L55).

```typescript
/v1/entity-history: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listEntityHistory"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects

**Поле.** Код: [web/admin/src/api/generated/storage.ts:72](../../../../../../web/admin/src/api/generated/storage.ts#L72).

```typescript
/v1/objects: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listObjects"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects/{object_id}

**Поле.** Код: [web/admin/src/api/generated/storage.ts:89](../../../../../../web/admin/src/api/generated/storage.ts#L89).

```typescript
/v1/objects/{object_id}: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getObject"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.paths./v1/objects/{object_id}/content

**Поле.** Код: [web/admin/src/api/generated/storage.ts:121](../../../../../../web/admin/src/api/generated/storage.ts#L121).

```typescript
/v1/objects/{object_id}/content: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getObjectContent"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.webhooks

**Тип.** Код: [web/admin/src/api/generated/storage.ts:143](../../../../../../web/admin/src/api/generated/storage.ts#L143).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.storage.components

**Інтерфейс.** Код: [web/admin/src/api/generated/storage.ts:144](../../../../../../web/admin/src/api/generated/storage.ts#L144).

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

**Поле.** Код: [web/admin/src/api/generated/storage.ts:145](../../../../../../web/admin/src/api/generated/storage.ts#L145).

```typescript
schemas: { StoredObject: { object: components["schemas"]["StoredObjectRef"]; material?: { material_id?: string; observation_id?: string; source_id?: string; url?: string; fetched_at?: string; }; stored_at: components["schemas"]["Timestamp"]; }; StoredObjectDetail: { object: components["schemas"]["StoredObjectRef"]; stored_at: components["schemas"]["Timestamp"]; material?: components["schemas"]["material.schema"]; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; Slug: string; EntityKey: { scope: string; natural: { [key: string]: string | number | boolean; }; }; Id: string; Timestamp: string; Sha256Hex: string; ObservationOrder: { observation_id: components["schemas"]["Id"]; observed_at: components["schemas"]["Timestamp"]; sequence?: number; material_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; }; EntityState: { entity_type: string; key: components["schemas"]["EntityKey"]; canonical_key?: string; fields: Record<string, unknown>; field_orders?: { [key: string]: components["schemas"]["ObservationOrder"]; }; cleared_fields?: string[]; version?: number; updated_at: components["schemas"]["Timestamp"]; }; NextCursor: string | null; SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; Provenance: { package?: components["schemas"]["package-ref.schema"]; invocation_id?: components["schemas"]["Id"]; run_id?: components["schemas"]["Id"]; stage_id?: components["schemas"]["Slug"]; }; "entity.schema": { entity_type: string; schema?: string; key: components["schemas"]["EntityKey"]; fields: { [key: string]: unknown; }; cleared?: string[]; completeness?: "full" | "partial"; observation: components["schemas"]["ObservationOrder"]; provenance?: components["schemas"]["Provenance"]; confidence?: number; }; EntityHistoryEntry: { record: components["schemas"]["entity.schema"]; received_at: components["schemas"]["Timestamp"]; delivery_key?: string; applied_fields: string[]; stale_fields: string[]; }; MediaType: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); StoredObjectRef: { object_id: components["schemas"]["Id"]; adapter: string; connection_id?: components["schemas"]["Slug"]; locator?: { [key: string]: string | number; }; media_type?: components["schemas"]["MediaType"]; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; content?: components["schemas"]["content-ref.schema"]; }; SourceKind: string; DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; "material.schema": { material_id: components["schemas"]["Id"]; observation_id: components["schemas"]["Id"]; source: { source_id?: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; name?: string; }; locator: { url?: string; final_url?: string; canonical_url?: string; telegram?: { channel_id: string; channel_username?: string; message_id: number; grouped_id?: string; }; }; fetched_at: components["schemas"]["Timestamp"]; published_at?: components["schemas"]["Timestamp"]; edited_at?: components["schemas"]["Timestamp"]; format: { media_type: components["schemas"]["MediaType"]; charset?: string; language?: string; content_kind?: string; }; revision: { content_sha256: components["schemas"]["Sha256Hex"]; source_revision?: string; sequence?: number; is_edit?: boolean; }; content: components["schemas"]["content-ref.schema"]; attachments?: { name: string; role?: string; content: components["schemas"]["content-ref.schema"]; }[]; http?: { status?: number; headers?: { [key: string]: string; }; redirects?: string[]; }; discovery?: { strategy?: string; parent_url?: string; depth?: number; section?: string; priority?: number; }; collector: { name: string; version: string; rules?: components["schemas"]["package-ref.schema"]; collection_id?: components["schemas"]["Id"]; }; diagnostics?: components["schemas"]["DiagnosticMessage"][]; metadata?: Record<string, unknown>; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.responses

**Поле.** Код: [web/admin/src/api/generated/storage.ts:661](../../../../../../web/admin/src/api/generated/storage.ts#L661).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.parameters

**Поле.** Код: [web/admin/src/api/generated/storage.ts:690](../../../../../../web/admin/src/api/generated/storage.ts#L690).

```typescript
parameters: { ConnectionIdQuery: components["schemas"]["Slug"]; Cursor: string; Limit: number; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/storage.ts:697](../../../../../../web/admin/src/api/generated/storage.ts#L697).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.headers

**Поле.** Код: [web/admin/src/api/generated/storage.ts:698](../../../../../../web/admin/src/api/generated/storage.ts#L698).

```typescript
headers: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/storage.ts:699](../../../../../../web/admin/src/api/generated/storage.ts#L699).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.$defs

**Тип.** Код: [web/admin/src/api/generated/storage.ts:701](../../../../../../web/admin/src/api/generated/storage.ts#L701).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.storage.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/storage.ts:702](../../../../../../web/admin/src/api/generated/storage.ts#L702).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.storage.md#adminapigeneratedstorageoperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.storage.md#adminapigeneratedstorageoperationsgetserviceinfo) | Поле | ні |
| [listEntities](api.generated.storage.md#adminapigeneratedstorageoperationslistentities) | Поле | ні |
| [listEntityHistory](api.generated.storage.md#adminapigeneratedstorageoperationslistentityhistory) | Поле | ні |
| [listObjects](api.generated.storage.md#adminapigeneratedstorageoperationslistobjects) | Поле | ні |
| [getObject](api.generated.storage.md#adminapigeneratedstorageoperationsgetobject) | Поле | ні |
| [getObjectContent](api.generated.storage.md#adminapigeneratedstorageoperationsgetobjectcontent) | Поле | ні |

## admin.api.generated.storage.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/storage.ts:703](../../../../../../web/admin/src/api/generated/storage.ts#L703).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/storage.ts:732](../../../../../../web/admin/src/api/generated/storage.ts#L732).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listEntities

**Поле.** Код: [web/admin/src/api/generated/storage.ts:753](../../../../../../web/admin/src/api/generated/storage.ts#L753).

```typescript
listEntities: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; entity_type: string; scope?: string; key?: string; updated_since?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["EntityState"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listEntityHistory

**Поле.** Код: [web/admin/src/api/generated/storage.ts:790](../../../../../../web/admin/src/api/generated/storage.ts#L790).

```typescript
listEntityHistory: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; entity_type: string; key: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["EntityHistoryEntry"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.listObjects

**Поле.** Код: [web/admin/src/api/generated/storage.ts:823](../../../../../../web/admin/src/api/generated/storage.ts#L823).

```typescript
listObjects: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; source_id?: string; material_id?: string; material_ids?: string[]; since?: string; until?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["StoredObject"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getObject

**Поле.** Код: [web/admin/src/api/generated/storage.ts:868](../../../../../../web/admin/src/api/generated/storage.ts#L868).

```typescript
getObject: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["StoredObjectDetail"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.storage.operations.getObjectContent

**Поле.** Код: [web/admin/src/api/generated/storage.ts:894](../../../../../../web/admin/src/api/generated/storage.ts#L894).

```typescript
getObjectContent: { parameters: { query: { connection_id: components["parameters"]["ConnectionIdQuery"]; }; header?: never; path: { object_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/octet-stream": string; "text/html": string; "text/plain": string; "application/json": unknown; "*/*": string; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
