# api/generated/registry

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.registry.paths](#adminapigeneratedregistrypaths)
- [admin.api.generated.registry.paths./v1/health](#adminapigeneratedregistrypathsv1health)
- [admin.api.generated.registry.paths./v1/info](#adminapigeneratedregistrypathsv1info)
- [admin.api.generated.registry.paths./v1/packages](#adminapigeneratedregistrypathsv1packages)
- [admin.api.generated.registry.paths./v1/packages/{package_id}](#adminapigeneratedregistrypathsv1packagespackage_id)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions](#adminapigeneratedregistrypathsv1packagespackage_idversions)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}](#adminapigeneratedregistrypathsv1packagespackage_idversionsversion)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/archive](#adminapigeneratedregistrypathsv1packagespackage_idversionsversionarchive)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/file](#adminapigeneratedregistrypathsv1packagespackage_idversionsversionfile)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/status](#adminapigeneratedregistrypathsv1packagespackage_idversionsversionstatus)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/test-results](#adminapigeneratedregistrypathsv1packagespackage_idversionsversiontest-results)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/forks](#adminapigeneratedregistrypathsv1packagespackage_idforks)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/diff](#adminapigeneratedregistrypathsv1packagespackage_iddiff)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/upstream](#adminapigeneratedregistrypathsv1packagespackage_idupstream)
- [admin.api.generated.registry.paths./v1/packages/{package_id}/upstream-ports](#adminapigeneratedregistrypathsv1packagespackage_idupstream-ports)
- [admin.api.generated.registry.paths./v1/jobs/{job_id}](#adminapigeneratedregistrypathsv1jobsjob_id)
- [admin.api.generated.registry.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedregistrypathsv1jobsjob_idcancel)
- [admin.api.generated.registry.webhooks](#adminapigeneratedregistrywebhooks)
- [admin.api.generated.registry.components](#adminapigeneratedregistrycomponents)
- [admin.api.generated.registry.components.schemas](#adminapigeneratedregistrycomponentsschemas)
- [admin.api.generated.registry.components.responses](#adminapigeneratedregistrycomponentsresponses)
- [admin.api.generated.registry.components.parameters](#adminapigeneratedregistrycomponentsparameters)
- [admin.api.generated.registry.components.requestBodies](#adminapigeneratedregistrycomponentsrequestbodies)
- [admin.api.generated.registry.components.headers](#adminapigeneratedregistrycomponentsheaders)
- [admin.api.generated.registry.components.pathItems](#adminapigeneratedregistrycomponentspathitems)
- [admin.api.generated.registry.$defs](#adminapigeneratedregistrydefs)
- [admin.api.generated.registry.operations](#adminapigeneratedregistryoperations)
- [admin.api.generated.registry.operations.getHealth](#adminapigeneratedregistryoperationsgethealth)
- [admin.api.generated.registry.operations.getServiceInfo](#adminapigeneratedregistryoperationsgetserviceinfo)
- [admin.api.generated.registry.operations.listPackages](#adminapigeneratedregistryoperationslistpackages)
- [admin.api.generated.registry.operations.createPackage](#adminapigeneratedregistryoperationscreatepackage)
- [admin.api.generated.registry.operations.getPackage](#adminapigeneratedregistryoperationsgetpackage)
- [admin.api.generated.registry.operations.updatePackage](#adminapigeneratedregistryoperationsupdatepackage)
- [admin.api.generated.registry.operations.listPackageVersions](#adminapigeneratedregistryoperationslistpackageversions)
- [admin.api.generated.registry.operations.publishPackageVersion](#adminapigeneratedregistryoperationspublishpackageversion)
- [admin.api.generated.registry.operations.getPackageVersion](#adminapigeneratedregistryoperationsgetpackageversion)
- [admin.api.generated.registry.operations.downloadPackageArchive](#adminapigeneratedregistryoperationsdownloadpackagearchive)
- [admin.api.generated.registry.operations.getPackageFile](#adminapigeneratedregistryoperationsgetpackagefile)
- [admin.api.generated.registry.operations.setPackageVersionStatus](#adminapigeneratedregistryoperationssetpackageversionstatus)
- [admin.api.generated.registry.operations.recordTestResults](#adminapigeneratedregistryoperationsrecordtestresults)
- [admin.api.generated.registry.operations.forkPackage](#adminapigeneratedregistryoperationsforkpackage)
- [admin.api.generated.registry.operations.diffPackage](#adminapigeneratedregistryoperationsdiffpackage)
- [admin.api.generated.registry.operations.getUpstreamStatus](#adminapigeneratedregistryoperationsgetupstreamstatus)
- [admin.api.generated.registry.operations.portUpstreamChanges](#adminapigeneratedregistryoperationsportupstreamchanges)
- [admin.api.generated.registry.operations.getJob](#adminapigeneratedregistryoperationsgetjob)
- [admin.api.generated.registry.operations.cancelJob](#adminapigeneratedregistryoperationscanceljob)

## admin.api.generated.registry.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/registry.ts:3](../../../../../../web/admin/src/api/generated/registry.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.registry.md#adminapigeneratedregistrypathsv1health) | Поле | ні |
| [/v1/info](api.generated.registry.md#adminapigeneratedregistrypathsv1info) | Поле | ні |
| [/v1/packages](api.generated.registry.md#adminapigeneratedregistrypathsv1packages) | Поле | ні |
| [/v1/packages/{package_id}](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_id) | Поле | ні |
| [/v1/packages/{package_id}/versions](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversions) | Поле | ні |
| [/v1/packages/{package_id}/versions/{version}](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversionsversion) | Поле | ні |
| [/v1/packages/{package_id}/versions/{version}/archive](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversionsversionarchive) | Поле | ні |
| [/v1/packages/{package_id}/versions/{version}/file](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversionsversionfile) | Поле | ні |
| [/v1/packages/{package_id}/versions/{version}/status](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversionsversionstatus) | Поле | ні |
| [/v1/packages/{package_id}/versions/{version}/test-results](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idversionsversiontest-results) | Поле | ні |
| [/v1/packages/{package_id}/forks](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idforks) | Поле | ні |
| [/v1/packages/{package_id}/diff](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_iddiff) | Поле | ні |
| [/v1/packages/{package_id}/upstream](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idupstream) | Поле | ні |
| [/v1/packages/{package_id}/upstream-ports](api.generated.registry.md#adminapigeneratedregistrypathsv1packagespackage_idupstream-ports) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.registry.md#adminapigeneratedregistrypathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.registry.md#adminapigeneratedregistrypathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.registry.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/registry.ts:4](../../../../../../web/admin/src/api/generated/registry.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/registry.ts:21](../../../../../../web/admin/src/api/generated/registry.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages

**Поле.** Код: [web/admin/src/api/generated/registry.ts:38](../../../../../../web/admin/src/api/generated/registry.ts#L38).

```typescript
/v1/packages: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listPackages"]; put?: never; post: operations["createPackage"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}

**Поле.** Код: [web/admin/src/api/generated/registry.ts:56](../../../../../../web/admin/src/api/generated/registry.ts#L56).

```typescript
/v1/packages/{package_id}: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get: operations["getPackage"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch: operations["updatePackage"]; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions

**Поле.** Код: [web/admin/src/api/generated/registry.ts:76](../../../../../../web/admin/src/api/generated/registry.ts#L76).

```typescript
/v1/packages/{package_id}/versions: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get: operations["listPackageVersions"]; put?: never; post: operations["publishPackageVersion"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}

**Поле.** Код: [web/admin/src/api/generated/registry.ts:102](../../../../../../web/admin/src/api/generated/registry.ts#L102).

```typescript
/v1/packages/{package_id}/versions/{version}: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; get: operations["getPackageVersion"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/archive

**Поле.** Код: [web/admin/src/api/generated/registry.ts:122](../../../../../../web/admin/src/api/generated/registry.ts#L122).

```typescript
/v1/packages/{package_id}/versions/{version}/archive: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; get: operations["downloadPackageArchive"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/file

**Поле.** Код: [web/admin/src/api/generated/registry.ts:142](../../../../../../web/admin/src/api/generated/registry.ts#L142).

```typescript
/v1/packages/{package_id}/versions/{version}/file: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; get: operations["getPackageFile"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/status

**Поле.** Код: [web/admin/src/api/generated/registry.ts:162](../../../../../../web/admin/src/api/generated/registry.ts#L162).

```typescript
/v1/packages/{package_id}/versions/{version}/status: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; get?: never; put?: never; post: operations["setPackageVersionStatus"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/versions/{version}/test-results

**Поле.** Код: [web/admin/src/api/generated/registry.ts:182](../../../../../../web/admin/src/api/generated/registry.ts#L182).

```typescript
/v1/packages/{package_id}/versions/{version}/test-results: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; get?: never; put?: never; post: operations["recordTestResults"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/forks

**Поле.** Код: [web/admin/src/api/generated/registry.ts:202](../../../../../../web/admin/src/api/generated/registry.ts#L202).

```typescript
/v1/packages/{package_id}/forks: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["forkPackage"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/diff

**Поле.** Код: [web/admin/src/api/generated/registry.ts:226](../../../../../../web/admin/src/api/generated/registry.ts#L226).

```typescript
/v1/packages/{package_id}/diff: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get: operations["diffPackage"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/upstream

**Поле.** Код: [web/admin/src/api/generated/registry.ts:245](../../../../../../web/admin/src/api/generated/registry.ts#L245).

```typescript
/v1/packages/{package_id}/upstream: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get: operations["getUpstreamStatus"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/packages/{package_id}/upstream-ports

**Поле.** Код: [web/admin/src/api/generated/registry.ts:264](../../../../../../web/admin/src/api/generated/registry.ts#L264).

```typescript
/v1/packages/{package_id}/upstream-ports: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["portUpstreamChanges"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/registry.ts:289](../../../../../../web/admin/src/api/generated/registry.ts#L289).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/registry.ts:308](../../../../../../web/admin/src/api/generated/registry.ts#L308).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.webhooks

**Тип.** Код: [web/admin/src/api/generated/registry.ts:333](../../../../../../web/admin/src/api/generated/registry.ts#L333).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.registry.components

**Інтерфейс.** Код: [web/admin/src/api/generated/registry.ts:334](../../../../../../web/admin/src/api/generated/registry.ts#L334).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.registry.md#adminapigeneratedregistrycomponentsschemas) | Поле | ні |
| [responses](api.generated.registry.md#adminapigeneratedregistrycomponentsresponses) | Поле | ні |
| [parameters](api.generated.registry.md#adminapigeneratedregistrycomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.registry.md#adminapigeneratedregistrycomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.registry.md#adminapigeneratedregistrycomponentsheaders) | Поле | ні |
| [pathItems](api.generated.registry.md#adminapigeneratedregistrycomponentspathitems) | Поле | ні |

## admin.api.generated.registry.components.schemas

**Поле.** Код: [web/admin/src/api/generated/registry.ts:335](../../../../../../web/admin/src/api/generated/registry.ts#L335).

```typescript
schemas: { VersionStatus: "draft" | "approved" | "rejected" | "deprecated" | "yanked"; TestStatus: "unknown" | "passed" | "failed"; Package: { package_id: components["schemas"]["Slug"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; latest_version?: string | null; auto_changes_allowed: boolean; deprecated: boolean; fork_of?: components["schemas"]["package-ref.schema"]; forks_count?: number; owner?: string; labels?: components["schemas"]["Labels"]; created_at: components["schemas"]["Timestamp"]; updated_at: components["schemas"]["Timestamp"]; }; PackageList: { items: components["schemas"]["Package"][]; next_cursor: components["schemas"]["NextCursor"]; }; PackageCreate: { package_id: components["schemas"]["Slug"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; auto_changes_allowed?: boolean; labels?: components["schemas"]["Labels"]; }; PackagePatch: { title?: string; description?: string; auto_changes_allowed?: boolean; deprecated?: boolean; labels?: components["schemas"]["Labels"]; }; FileEntry: { path: components["schemas"]["PackagePath"]; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; }; PackageVersion: { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest: components["schemas"]["Digest"]; status: components["schemas"]["VersionStatus"]; test_status: components["schemas"]["TestStatus"]; manifest?: components["schemas"]["package-manifest.schema"]; files?: components["schemas"]["FileEntry"][]; size_bytes?: number; created_at: components["schemas"]["Timestamp"]; created_by?: string; published_by?: string; status_history?: { status: components["schemas"]["VersionStatus"]; at: components["schemas"]["Timestamp"]; by?: string; reason?: string; }[]; test_reports?: components["schemas"]["TestResultsRecord"][]; test_summary?: components["schemas"]["TestSummary"]; }; TestSummary: { status: components["schemas"]["TestStatus"]; contexts: { context?: string; test_status: components["schemas"]["TestStatus"]; recorded_at?: components["schemas"]["Timestamp"]; runner?: string; reports: number; }[]; }; PackageVersionList: { items: components["schemas"]["PackageVersion"][]; next_cursor: components["schemas"]["NextCursor"]; }; PublishRequest: { manifest: components["schemas"]["package-manifest.schema"]; files: { [key: string]: { encoding: "utf-8" | "base64"; data: string; }; }; }; StatusChange: { status: "approved" | "rejected" | "deprecated" | "yanked"; reason?: string; }; TestResultsRecord: { runner?: string; context?: string; report: components["schemas"]["TestReport"]; recorded_at?: components["schemas"]["Timestamp"]; }; ForkRequest: { new_package_id: components["schemas"]["Slug"]; from_version: components["schemas"]["SemVer"]; initial_version?: components["schemas"]["SemVer"]; title?: string; auto_changes_allowed?: boolean; }; PackageDiff: { from: components["schemas"]["package-ref.schema"]; to: components["schemas"]["package-ref.schema"]; manifest_changes?: { pointer: string; op: "add" | "remove" | "replace"; old?: unknown; new?: unknown; }[]; files: { path: string; status: "added" | "removed" | "modified" | "unchanged"; unified_diff?: string; binary?: boolean; }[]; }; UpstreamStatus: { fork_of: components["schemas"]["package-ref.schema"]; last_ported_version?: components["schemas"]["SemVer"]; parent_latest_version: components["schemas"]["SemVer"]; newer_parent_versions: components["schemas"]["SemVer"][]; }; UpstreamPortRequest: { parent_version: components["schemas"]["SemVer"]; base_version?: components["schemas"]["SemVer"]; new_version: components["schemas"]["SemVer"]; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; HandlerKind: "extractor" | "storage" | "llm" | "transform" | "collector-rules"; Slug: string; SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; Labels: { [key: string]: string; }; Timestamp: string; NextCursor: string | null; PackagePath: string; HandlerStatus: "success" | "empty" | "unrecognized" | "failed"; Id: string; PythonEntry: { runtime: "python"; module: string; callable: string; }; StorageEntry: { executor: "storage"; adapter: string; writes: "raw" | "entities" | "raw_and_entities" | "data"; format?: { raw?: "original" | "html" | "json"; entities?: "json" | "jsonl"; }; history?: boolean; }; LlmEntry: { executor: "llm"; instructions: components["schemas"]["PackagePath"]; input_template?: components["schemas"]["PackagePath"]; output_schema: components["schemas"]["PackagePath"]; model?: string; temperature?: number; max_output_tokens?: number; }; CollectorRulesEntry: { collector: string; rules: components["schemas"]["PackagePath"]; }; ExecutorEntry: { executor: string; operation?: string; }; InputContract: { accepts?: ("material" | "entities" | "data")[]; media_types?: string[]; content_kinds?: string[]; entity_types?: string[]; data_schema?: components["schemas"]["PackagePath"]; }; OutputContract: { entities?: { entity_type: string; schema: components["schemas"]["PackagePath"]; key_fields: string[]; description?: string; }[]; data_schema?: components["schemas"]["PackagePath"]; }; Dependencies: { runtime_profile?: string; python?: string[]; packages?: components["schemas"]["package-ref.schema"][]; }; ConnectionKind: string; ConnectionRequirement: { name: string; kind: components["schemas"]["ConnectionKind"]; purpose?: string; optional?: boolean; }; TestCase: { name: string; input: { material?: components["schemas"]["PackagePath"]; file?: components["schemas"]["PackagePath"]; media_type?: string; url?: string; entities?: components["schemas"]["PackagePath"]; data?: components["schemas"]["PackagePath"]; }; params?: Record<string, unknown>; expected_status: components["schemas"]["HandlerStatus"]; expected?: components["schemas"]["PackagePath"]; compare?: "exact" | "subset"; origin?: "human" | "llm" | "problem_sample"; }; Provenance: { created_by: "human" | "llm" | "import"; authors?: string[]; created_at?: components["schemas"]["Timestamp"]; based_on?: components["schemas"]["package-ref.schema"]; change_summary?: string; llm?: { provider?: string; model?: string; assistant_job_id?: components["schemas"]["Id"]; reason?: "onboarding" | "improvement" | "unknown_material" | "upstream_port"; }; upstream_port?: { parent_version: components["schemas"]["SemVer"]; requested_by?: string; }; }; SourceKind: string; "package-manifest.schema": { schema_version: "1"; package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; tags?: string[]; entry: components["schemas"]["PythonEntry"] | components["schemas"]["StorageEntry"] | components["schemas"]["LlmEntry"] | components["schemas"]["CollectorRulesEntry"] | components["schemas"]["ExecutorEntry"]; input?: components["schemas"]["InputContract"]; params_schema?: components["schemas"]["PackagePath"]; output?: components["schemas"]["OutputContract"]; dependencies?: components["schemas"]["Dependencies"]; required_connections?: components["schemas"]["ConnectionRequirement"][]; access?: { network?: "none" | "allowlist"; hosts?: string[]; }; tests?: components["schemas"]["TestCase"][]; provenance: components["schemas"]["Provenance"]; fork_of?: components["schemas"]["package-ref.schema"]; bindings_hint?: { source_kinds?: components["schemas"]["SourceKind"][]; domains?: string[]; url_patterns?: string[]; }; } & unknown; Sha256Hex: string; EntityKey: { scope: string; natural: { [key: string]: string | number | boolean; }; }; ObservationOrder: { observation_id: components["schemas"]["Id"]; observed_at: components["schemas"]["Timestamp"]; sequence?: number; material_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; }; "entity.schema": { entity_type: string; schema?: string; key: components["schemas"]["EntityKey"]; fields: { [key: string]: unknown; }; cleared?: string[]; completeness?: "full" | "partial"; observation: components["schemas"]["ObservationOrder"]; provenance?: components["schemas"]["$defs-Provenance"]; confidence?: number; }; "$defs-Provenance": { package?: components["schemas"]["package-ref.schema"]; invocation_id?: components["schemas"]["Id"]; run_id?: components["schemas"]["Id"]; stage_id?: components["schemas"]["Slug"]; }; MediaType: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); StoredObjectRef: { object_id: components["schemas"]["Id"]; adapter: string; connection_id?: components["schemas"]["Slug"]; locator?: { [key: string]: string | number; }; media_type?: components["schemas"]["MediaType"]; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; content?: components["schemas"]["content-ref.schema"]; }; WriteAck: { status: "written" | "duplicate" | "stale" | "partially_stale" | "simulated"; target: { adapter: string; connection_id?: components["schemas"]["Slug"]; }; object?: components["schemas"]["StoredObjectRef"]; entity?: { entity_type?: string; canonical_key?: string; version?: number; }; applied_fields?: string[]; stale_fields?: string[]; delivery_key?: string; }; DiagnosticMessage: { level: "debug" | "info" | "warning" | "error"; code?: string; message: string; pointer?: string; material_id?: components["schemas"]["Id"]; selector?: string; }; Money: { amount: number; currency: string; }; InputRef: { kind: "material" | "entities" | "data"; material_id?: components["schemas"]["Id"]; observation_id?: components["schemas"]["Id"]; content_sha256?: components["schemas"]["Sha256Hex"]; from_invocation_id?: components["schemas"]["Id"]; }; HandlerOutput: { entities?: components["schemas"]["entity.schema"][]; entities_ref?: components["schemas"]["content-ref.schema"]; data?: unknown; data_ref?: components["schemas"]["content-ref.schema"]; writes?: components["schemas"]["WriteAck"][]; }; Diagnostics: { messages?: components["schemas"]["DiagnosticMessage"][]; validation_errors?: { pointer: string; message: string; schema_pointer?: string; }[]; metrics?: { duration_ms?: number; cpu_ms?: number; peak_memory_mb?: number; output_bytes?: number; }; logs_ref?: components["schemas"]["content-ref.schema"]; }; Usage: { llm?: { provider?: string; model?: string; input_tokens?: number; output_tokens?: number; cost?: components["schemas"]["Money"]; }; }; "handler-result.schema": { invocation_id: components["schemas"]["Id"]; handler: components["schemas"]["package-ref.schema"]; handler_kind: components["schemas"]["HandlerKind"]; status: components["schemas"]["HandlerStatus"]; inputs: components["schemas"]["InputRef"][]; output?: components["schemas"]["HandlerOutput"]; unrecognized?: { partial: boolean; reason?: string; signature?: string; }; failure?: { kind: "execution_error" | "schema_mismatch" | "timeout" | "resource_exceeded" | "sandbox_violation" | "dependency_error" | "connection_error" | "budget_exhausted" | "invalid_params"; message: string; retryable?: boolean; details?: Record<string, unknown>; }; diagnostics?: components["schemas"]["Diagnostics"]; usage?: components["schemas"]["Usage"]; delivery_key?: string; duplicate?: boolean; test_mode?: boolean; started_at: components["schemas"]["Timestamp"]; finished_at: components["schemas"]["Timestamp"]; } & (unknown & unknown); TestCaseResult: { name: string; passed: boolean; expected_status?: components["schemas"]["HandlerStatus"]; actual_status?: components["schemas"]["HandlerStatus"]; differences?: { pointer: string; expected?: unknown; actual?: unknown; }[]; result?: components["schemas"]["handler-result.schema"]; }; TestReport: { package: components["schemas"]["package-ref.schema"]; passed: number; failed: number; cases: components["schemas"]["TestCaseResult"][]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; JobCancelRequest: { reason?: string; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.components.responses

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1269](../../../../../../web/admin/src/api/generated/registry.ts#L1269).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Forbidden: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; BadRequest: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PayloadTooLarge: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.components.parameters

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1354](../../../../../../web/admin/src/api/generated/registry.ts#L1354).

```typescript
parameters: { PackageId: components["schemas"]["Slug"]; Version: components["schemas"]["SemVer"]; Cursor: string; Limit: number; IdempotencyKey: string; IfMatch: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1377](../../../../../../web/admin/src/api/generated/registry.ts#L1377).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.components.headers

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1378](../../../../../../web/admin/src/api/generated/registry.ts#L1378).

```typescript
headers: { Location: string; ETag: string; IdempotencyReplayed: boolean; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1386](../../../../../../web/admin/src/api/generated/registry.ts#L1386).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.$defs

**Тип.** Код: [web/admin/src/api/generated/registry.ts:1388](../../../../../../web/admin/src/api/generated/registry.ts#L1388).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.registry.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/registry.ts:1389](../../../../../../web/admin/src/api/generated/registry.ts#L1389).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.registry.md#adminapigeneratedregistryoperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.registry.md#adminapigeneratedregistryoperationsgetserviceinfo) | Поле | ні |
| [listPackages](api.generated.registry.md#adminapigeneratedregistryoperationslistpackages) | Поле | ні |
| [createPackage](api.generated.registry.md#adminapigeneratedregistryoperationscreatepackage) | Поле | ні |
| [getPackage](api.generated.registry.md#adminapigeneratedregistryoperationsgetpackage) | Поле | ні |
| [updatePackage](api.generated.registry.md#adminapigeneratedregistryoperationsupdatepackage) | Поле | ні |
| [listPackageVersions](api.generated.registry.md#adminapigeneratedregistryoperationslistpackageversions) | Поле | ні |
| [publishPackageVersion](api.generated.registry.md#adminapigeneratedregistryoperationspublishpackageversion) | Поле | ні |
| [getPackageVersion](api.generated.registry.md#adminapigeneratedregistryoperationsgetpackageversion) | Поле | ні |
| [downloadPackageArchive](api.generated.registry.md#adminapigeneratedregistryoperationsdownloadpackagearchive) | Поле | ні |
| [getPackageFile](api.generated.registry.md#adminapigeneratedregistryoperationsgetpackagefile) | Поле | ні |
| [setPackageVersionStatus](api.generated.registry.md#adminapigeneratedregistryoperationssetpackageversionstatus) | Поле | ні |
| [recordTestResults](api.generated.registry.md#adminapigeneratedregistryoperationsrecordtestresults) | Поле | ні |
| [forkPackage](api.generated.registry.md#adminapigeneratedregistryoperationsforkpackage) | Поле | ні |
| [diffPackage](api.generated.registry.md#adminapigeneratedregistryoperationsdiffpackage) | Поле | ні |
| [getUpstreamStatus](api.generated.registry.md#adminapigeneratedregistryoperationsgetupstreamstatus) | Поле | ні |
| [portUpstreamChanges](api.generated.registry.md#adminapigeneratedregistryoperationsportupstreamchanges) | Поле | ні |
| [getJob](api.generated.registry.md#adminapigeneratedregistryoperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.registry.md#adminapigeneratedregistryoperationscanceljob) | Поле | ні |

## admin.api.generated.registry.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1390](../../../../../../web/admin/src/api/generated/registry.ts#L1390).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1419](../../../../../../web/admin/src/api/generated/registry.ts#L1419).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.listPackages

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1440](../../../../../../web/admin/src/api/generated/registry.ts#L1440).

```typescript
listPackages: { parameters: { query?: { kind?: components["schemas"]["HandlerKind"]; q?: string; tag?: string; entity_type?: string; media_type?: string; domain?: string; fork_of?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageList"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.createPackage

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1477](../../../../../../web/admin/src/api/generated/registry.ts#L1477).

```typescript
createPackage: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["PackageCreate"]; }; }; responses: { 201: { headers: { Location: components["headers"]["Location"]; ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["Package"]; }; }; 401: components["responses"]["Unauthenticated"]; 403: components["responses"]["Forbidden"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getPackage

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1517](../../../../../../web/admin/src/api/generated/registry.ts#L1517).

```typescript
getPackage: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["Package"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.updatePackage

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1542](../../../../../../web/admin/src/api/generated/registry.ts#L1542).

```typescript
updatePackage: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody: { content: { "application/merge-patch+json": components["schemas"]["PackagePatch"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["Package"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.listPackageVersions

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1579](../../../../../../web/admin/src/api/generated/registry.ts#L1579).

```typescript
listPackageVersions: { parameters: { query?: { status?: components["schemas"]["VersionStatus"]; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageVersionList"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.publishPackageVersion

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1609](../../../../../../web/admin/src/api/generated/registry.ts#L1609).

```typescript
publishPackageVersion: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody: { content: { "application/zip": string; "application/json": components["schemas"]["PublishRequest"]; }; }; responses: { 201: { headers: { Location: components["headers"]["Location"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageVersion"]; }; }; 400: components["responses"]["BadRequest"]; 401: components["responses"]["Unauthenticated"]; 403: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 404: components["responses"]["NotFound"]; 409: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 413: components["responses"]["PayloadTooLarge"]; 422: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getPackageVersion

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1678](../../../../../../web/admin/src/api/generated/registry.ts#L1678).

```typescript
getPackageVersion: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageVersion"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.downloadPackageArchive

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1703](../../../../../../web/admin/src/api/generated/registry.ts#L1703).

```typescript
downloadPackageArchive: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/zip": string; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getPackageFile

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1729](../../../../../../web/admin/src/api/generated/registry.ts#L1729).

```typescript
getPackageFile: { parameters: { query: { path: components["schemas"]["PackagePath"]; }; header?: never; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "text/plain": string; "application/octet-stream": string; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.setPackageVersionStatus

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1761](../../../../../../web/admin/src/api/generated/registry.ts#L1761).

```typescript
setPackageVersionStatus: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["StatusChange"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageVersion"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.recordTestResults

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1801](../../../../../../web/admin/src/api/generated/registry.ts#L1801).

```typescript
recordTestResults: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { package_id: components["parameters"]["PackageId"]; version: components["parameters"]["Version"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["TestResultsRecord"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageVersion"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.forkPackage

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1841](../../../../../../web/admin/src/api/generated/registry.ts#L1841).

```typescript
forkPackage: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["ForkRequest"]; }; }; responses: { 201: { headers: { Location: components["headers"]["Location"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["Package"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.diffPackage

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1881](../../../../../../web/admin/src/api/generated/registry.ts#L1881).

```typescript
diffPackage: { parameters: { query: { from?: string; to: string; context_lines?: number; }; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["PackageDiff"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getUpstreamStatus

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1910](../../../../../../web/admin/src/api/generated/registry.ts#L1910).

```typescript
getUpstreamStatus: { parameters: { query?: never; header?: never; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["UpstreamStatus"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.portUpstreamChanges

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1943](../../../../../../web/admin/src/api/generated/registry.ts#L1943).

```typescript
portUpstreamChanges: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { package_id: components["parameters"]["PackageId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["UpstreamPortRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1975](../../../../../../web/admin/src/api/generated/registry.ts#L1975).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.registry.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/registry.ts:1999](../../../../../../web/admin/src/api/generated/registry.ts#L1999).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
