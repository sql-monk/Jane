# api/packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.packages.MANIFEST_FILE](#adminapipackagesmanifest_file)
- [admin.api.packages.PackageFile](#adminapipackagespackagefile)
- [admin.api.packages.PackageFile.encoding](#adminapipackagespackagefileencoding)
- [admin.api.packages.PackageFile.data](#adminapipackagespackagefiledata)
- [admin.api.packages.decodeFile](#adminapipackagesdecodefile)
- [admin.api.packages.fetchPackageFile](#adminapipackagesfetchpackagefile)
- [admin.api.packages.fetchAllFiles](#adminapipackagesfetchallfiles)
- [admin.api.packages.nextManifest](#adminapipackagesnextmanifest)
- [admin.api.packages.publishVersion](#adminapipackagespublishversion)

## admin.api.packages.MANIFEST_FILE

**Константа.** Код: [web/admin/src/api/packages.ts:7](../../../../../../web/admin/src/api/packages.ts#L7).

```typescript
MANIFEST_FILE: "jane-package.json" = "jane-package.json"
```

Доступ: читання — так; запис — так.

## admin.api.packages.PackageFile

**Інтерфейс.** Код: [web/admin/src/api/packages.ts:9](../../../../../../web/admin/src/api/packages.ts#L9).

```typescript
interface PackageFile {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [encoding](api.packages.md#adminapipackagespackagefileencoding) | Поле | ні |
| [data](api.packages.md#adminapipackagespackagefiledata) | Поле | ні |

## admin.api.packages.PackageFile.encoding

**Поле.** Код: [web/admin/src/api/packages.ts:10](../../../../../../web/admin/src/api/packages.ts#L10).

```typescript
encoding: "utf-8" | "base64"
```

Доступ: читання — так; запис — так.

## admin.api.packages.PackageFile.data

**Поле.** Код: [web/admin/src/api/packages.ts:11](../../../../../../web/admin/src/api/packages.ts#L11).

```typescript
data: string
```

Доступ: читання — так; запис — так.

## admin.api.packages.decodeFile

**Функція.** Код: [web/admin/src/api/packages.ts:23](../../../../../../web/admin/src/api/packages.ts#L23).

```typescript
function decodeFile(bytes: ArrayBuffer): PackageFile
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `bytes` | `ArrayBuffer` | `—` | required |

Результат: `PackageFile`.

### Опис із вихідного коду

```text
Decodes as UTF-8 text when possible, otherwise keeps the bytes as base64.
```

## admin.api.packages.fetchPackageFile

**Функція.** Код: [web/admin/src/api/packages.ts:31](../../../../../../web/admin/src/api/packages.ts#L31).

```typescript
function fetchPackageFile(api: ApiClients, packageId: string, version: string, path: string): Promise<PackageFile>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `api` | `ApiClients` | `—` | required |
| `packageId` | `string` | `—` | required |
| `version` | `string` | `—` | required |
| `path` | `string` | `—` | required |

Результат: `Promise<PackageFile>`.

## admin.api.packages.fetchAllFiles

**Функція.** Код: [web/admin/src/api/packages.ts:53](../../../../../../web/admin/src/api/packages.ts#L53).

```typescript
function fetchAllFiles(api: ApiClients, version: PackageVersion): Promise<Record<string, PackageFile>>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `api` | `ApiClients` | `—` | required |
| `version` | `{ package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest: components["schemas"]["Digest"]; status: components["schemas"]["VersionStatus"]; test_status: components["schemas"]["TestStatus"]; manifest?: components["schemas"]["package-manifest.schema"]; files?: components["schemas"]["FileEntry"][]; size_bytes?: number; created_at: components["schemas"]["Timestamp"]; created_by?: string; published_by?: string; status_history?: { status: components["schemas"]["VersionStatus"]; at: components["schemas"]["Timestamp"]; by?: string; reason?: string; }[]; test_reports?: components["schemas"]["TestResultsRecord"][]; test_summary?: components["schemas"]["TestSummary"]; }` | `—` | required |

Результат: `Promise<Record<string, PackageFile>>`.

### Опис із вихідного коду

```text
All files of a version except the manifest (the registry builds jane-package.json from `manifest`).
```

## admin.api.packages.nextManifest

**Функція.** Код: [web/admin/src/api/packages.ts:65](../../../../../../web/admin/src/api/packages.ts#L65).

```typescript
function nextManifest(base: PackageManifest, newVersion: string, changeSummary: string): PackageManifest
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `{ schema_version: "1"; package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; tags?: string[]; entry: components["schemas"]["PythonEntry"] \| components["schemas"]["StorageEntry"] \| components["schemas"]["LlmEntry"] \| components["schemas"]["CollectorRulesEntry"] \| components["schemas"]["ExecutorEntry"]; input?: components["schemas"]["InputContract"]; params_schema?: components["schemas"]["PackagePath"]; output?: components["schemas"]["OutputContract"]; dependencies?: components["schemas"]["Dependencies"]; required_connections?: components["schemas"]["ConnectionRequirement"][]; access?: { network?: "none" \| "allowlist"; hosts?: string[]; }; tests?: components["schemas"]["TestCase"][]; provenance: components["schemas"]["Provenance"]; fork_of?: components["schemas"]["package-ref.schema"]; bindings_hint?: { source_kinds?: components["schemas"]["SourceKind"][]; domains?: string[]; url_patterns?: string[]; }; }` | `—` | required |
| `newVersion` | `string` | `—` | required |
| `changeSummary` | `string` | `—` | required |

Результат: `{ schema_version: "1"; package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; tags?: string[]; entry: components["schemas"]["PythonEntry"] | components["schemas"]["StorageEntry"] | components["schemas"]["LlmEntry"] | components["schemas"]["CollectorRulesEntry"] | components["schemas"]["ExecutorEntry"]; input?: components["schemas"]["InputContract"]; params_schema?: components["schemas"]["PackagePath"]; output?: components["schemas"]["OutputContract"]; dependencies?: components["schemas"]["Dependencies"]; required_connections?: components["schemas"]["ConnectionRequirement"][]; access?: { network?: "none" | "allowlist"; hosts?: string[]; }; tests?: components["schemas"]["TestCase"][]; provenance: components["schemas"]["Provenance"]; fork_of?: components["schemas"]["package-ref.schema"]; bindings_hint?: { source_kinds?: components["schemas"]["SourceKind"][]; domains?: string[]; url_patterns?: string[]; }; }`.

## admin.api.packages.publishVersion

**Функція.** Код: [web/admin/src/api/packages.ts:82](../../../../../../web/admin/src/api/packages.ts#L82).

```typescript
function publishVersion(api: ApiClients, packageId: string, manifest: PackageManifest, files: Record<string, PackageFile>): Promise<PackageVersion>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `api` | `ApiClients` | `—` | required |
| `packageId` | `string` | `—` | required |
| `manifest` | `{ schema_version: "1"; package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; kind: components["schemas"]["HandlerKind"]; title: string; description?: string; tags?: string[]; entry: components["schemas"]["PythonEntry"] \| components["schemas"]["StorageEntry"] \| components["schemas"]["LlmEntry"] \| components["schemas"]["CollectorRulesEntry"] \| components["schemas"]["ExecutorEntry"]; input?: components["schemas"]["InputContract"]; params_schema?: components["schemas"]["PackagePath"]; output?: components["schemas"]["OutputContract"]; dependencies?: components["schemas"]["Dependencies"]; required_connections?: components["schemas"]["ConnectionRequirement"][]; access?: { network?: "none" \| "allowlist"; hosts?: string[]; }; tests?: components["schemas"]["TestCase"][]; provenance: components["schemas"]["Provenance"]; fork_of?: components["schemas"]["package-ref.schema"]; bindings_hint?: { source_kinds?: components["schemas"]["SourceKind"][]; domains?: string[]; url_patterns?: string[]; }; }` | `—` | required |
| `files` | `Record<string, PackageFile>` | `—` | required |

Результат: `Promise<{ package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest: components["schemas"]["Digest"]; status: components["schemas"]["VersionStatus"]; test_status: components["schemas"]["TestStatus"]; manifest?: components["schemas"]["package-manifest.schema"]; files?: components["schemas"]["FileEntry"][]; size_bytes?: number; created_at: components["schemas"]["Timestamp"]; created_by?: string; published_by?: string; status_history?: { status: components["schemas"]["VersionStatus"]; at: components["schemas"]["Timestamp"]; by?: string; reason?: string; }[]; test_reports?: components["schemas"]["TestResultsRecord"][]; test_summary?: components["schemas"]["TestSummary"]; }>`.

### Опис із вихідного коду

```text
Publishes a new draft version (JSON form of publishPackageVersion).
```
