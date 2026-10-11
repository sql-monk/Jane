# Модуль `api.types`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/api/types.ts](../../../../../web/admin/src/api/types.ts). Не редагуйте вручну.

## Типи

### Тип `Source`

```typescript
type Source = Ok<Orch["/v1/sources/{source_id}"]["get"]>;
```

Код: [types.ts:25](../../../../../web/admin/src/api/types.ts#L25).

### Тип `TaskConfig`

```typescript
type TaskConfig = Ok<Orch["/v1/tasks/{task_id}"]["get"]>;
```

Код: [types.ts:26](../../../../../web/admin/src/api/types.ts#L26).

### Тип `TaskSummary`

```typescript
type TaskSummary = ItemOf<Ok<Orch["/v1/tasks"]["get"]>>;
```

Код: [types.ts:27](../../../../../web/admin/src/api/types.ts#L27).

### Тип `Stage`

```typescript
type Stage = TaskConfig["stages"][number];
```

Код: [types.ts:28](../../../../../web/admin/src/api/types.ts#L28).

### Тип `Schedule`

```typescript
type Schedule = NonNullable<TaskConfig["schedule"]>;
```

Код: [types.ts:29](../../../../../web/admin/src/api/types.ts#L29).

### Тип `TaskValidation`

```typescript
type TaskValidation = Ok<Orch["/v1/task-validations"]["post"]>;
```

Код: [types.ts:30](../../../../../web/admin/src/api/types.ts#L30).

### Тип `RunRequest`

```typescript
type RunRequest = Body<Orch["/v1/tasks/{task_id}/runs"]["post"]>;
```

Код: [types.ts:31](../../../../../web/admin/src/api/types.ts#L31).

### Тип `Run`

```typescript
type Run = Ok<Orch["/v1/runs/{run_id}"]["get"]>;
```

Код: [types.ts:32](../../../../../web/admin/src/api/types.ts#L32).

### Тип `StageItem`

```typescript
type StageItem = ItemOf<Ok<Orch["/v1/runs/{run_id}/items"]["get"]>>;
```

Код: [types.ts:33](../../../../../web/admin/src/api/types.ts#L33).

### Тип `AttemptEvent`

```typescript
type AttemptEvent = NonNullable<StageItem["attempt_history"]>[number];
```

Код: [types.ts:34](../../../../../web/admin/src/api/types.ts#L34).

### Тип `MaterialTrace`

```typescript
type MaterialTrace = Ok<Orch["/v1/materials/{material_id}/trace"]["get"]>;
```

Код: [types.ts:35](../../../../../web/admin/src/api/types.ts#L35).

### Тип `UnknownMaterial`

```typescript
type UnknownMaterial = ItemOf<Ok<Orch["/v1/unknown-materials"]["get"]>>;
```

Код: [types.ts:36](../../../../../web/admin/src/api/types.ts#L36).

### Тип `ProblemGroup`

```typescript
type ProblemGroup = ItemOf<Ok<Orch["/v1/problem-groups"]["get"]>>;
```

Код: [types.ts:37](../../../../../web/admin/src/api/types.ts#L37).

### Тип `ProblemGroupStatus`

```typescript
type ProblemGroupStatus = ProblemGroup["status"];
```

Код: [types.ts:38](../../../../../web/admin/src/api/types.ts#L38).

### Тип `ReprocessRequest`

```typescript
type ReprocessRequest = Body<Orch["/v1/reprocessing"]["post"]>;
```

Код: [types.ts:39](../../../../../web/admin/src/api/types.ts#L39).

### Тип `PlatformConnection`

```typescript
type PlatformConnection = Ok<Orch["/v1/connections/{connection_id}"]["get"]>;
```

Код: [types.ts:40](../../../../../web/admin/src/api/types.ts#L40).

### Тип `Connection`

```typescript
type Connection = PlatformConnection["connection"];
```

Код: [types.ts:41](../../../../../web/admin/src/api/types.ts#L41).

### Тип `PlatformLimits`

```typescript
type PlatformLimits = Ok<Orch["/v1/limits/platform"]["get"]>;
```

Код: [types.ts:42](../../../../../web/admin/src/api/types.ts#L42).

### Тип `Limits`

```typescript
type Limits = NonNullable<PlatformLimits["hard_caps"]>;
```

Код: [types.ts:43](../../../../../web/admin/src/api/types.ts#L43).

### Тип `EffectiveLimits`

```typescript
type EffectiveLimits = Ok<Orch["/v1/limits/effective"]["get"]>;
```

Код: [types.ts:44](../../../../../web/admin/src/api/types.ts#L44).

### Тип `Executor`

```typescript
type Executor = ItemOf<Ok<Orch["/v1/executors"]["get"]>>;
```

Код: [types.ts:45](../../../../../web/admin/src/api/types.ts#L45).

### Тип `AuditEvent`

```typescript
type AuditEvent = ItemOf<Ok<Orch["/v1/audit-events"]["get"]>>;
```

Код: [types.ts:46](../../../../../web/admin/src/api/types.ts#L46).

### Тип `Activation`

```typescript
type Activation = Ok<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
```

Код: [types.ts:47](../../../../../web/admin/src/api/types.ts#L47).

### Тип `ActivationRequest`

```typescript
type ActivationRequest = Body<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
```

Код: [types.ts:48](../../../../../web/admin/src/api/types.ts#L48).

### Тип `Job`

```typescript
type Job = Ok<Orch["/v1/jobs/{job_id}"]["get"]>;
```

Код: [types.ts:49](../../../../../web/admin/src/api/types.ts#L49).

### Тип `JobStatus`

```typescript
type JobStatus = Job["status"];
```

Код: [types.ts:50](../../../../../web/admin/src/api/types.ts#L50).

### Тип `PackageRef`

```typescript
type PackageRef = NonNullable<Source["collector_rules"]>;
```

Код: [types.ts:51](../../../../../web/admin/src/api/types.ts#L51).

### Тип `Package`

```typescript
type Package = Ok<Reg["/v1/packages/{package_id}"]["get"]>;
```

Код: [types.ts:54](../../../../../web/admin/src/api/types.ts#L54).

### Тип `PackageVersion`

```typescript
type PackageVersion = Ok<Reg["/v1/packages/{package_id}/versions/{version}"]["get"]>;
```

Код: [types.ts:55](../../../../../web/admin/src/api/types.ts#L55).

### Тип `PackageManifest`

```typescript
type PackageManifest = NonNullable<PackageVersion["manifest"]>;
```

Код: [types.ts:56](../../../../../web/admin/src/api/types.ts#L56).

### Тип `PublishRequest`

```typescript
type PublishRequest = Extract<
  NonNullable<Reg["/v1/packages/{package_id}/versions"]["post"]["requestBody"]>["content"],
  { "application/json": unknown }
>["application/json"];
```

Код: [types.ts:57](../../../../../web/admin/src/api/types.ts#L57).

### Тип `PackageDiff`

```typescript
type PackageDiff = Ok<Reg["/v1/packages/{package_id}/diff"]["get"]>;
```

Код: [types.ts:61](../../../../../web/admin/src/api/types.ts#L61).

### Тип `UpstreamStatus`

```typescript
type UpstreamStatus = Ok<Reg["/v1/packages/{package_id}/upstream"]["get"]>;
```

Код: [types.ts:62](../../../../../web/admin/src/api/types.ts#L62).

### Тип `ForkRequest`

```typescript
type ForkRequest = Body<Reg["/v1/packages/{package_id}/forks"]["post"]>;
```

Код: [types.ts:63](../../../../../web/admin/src/api/types.ts#L63).

### Тип `StatusChange`

```typescript
type StatusChange = Body<Reg["/v1/packages/{package_id}/versions/{version}/status"]["post"]>;
```

Код: [types.ts:64](../../../../../web/admin/src/api/types.ts#L64).

### Тип `HandlerKind`

```typescript
type HandlerKind = Package["kind"];
```

Код: [types.ts:65](../../../../../web/admin/src/api/types.ts#L65).

### Тип `VersionStatus`

```typescript
type VersionStatus = PackageVersion["status"];
```

Код: [types.ts:66](../../../../../web/admin/src/api/types.ts#L66).

### Тип `TestResultsRecord`

```typescript
type TestResultsRecord = NonNullable<PackageVersion["test_reports"]>[number];
```

Код: [types.ts:67](../../../../../web/admin/src/api/types.ts#L67).

### Тип `TestReport`

```typescript
type TestReport = TestResultsRecord["report"];
```

Код: [types.ts:68](../../../../../web/admin/src/api/types.ts#L68).

### Тип `TestSummary`

```typescript
type TestSummary = NonNullable<PackageVersion["test_summary"]>;
```

Код: [types.ts:69](../../../../../web/admin/src/api/types.ts#L69).

### Тип `StoredObject`

```typescript
type StoredObject = ItemOf<Ok<Sto["/v1/objects"]["get"]>>;
```

Код: [types.ts:72](../../../../../web/admin/src/api/types.ts#L72).

### Тип `StoredObjectDetail`

```typescript
type StoredObjectDetail = Ok<Sto["/v1/objects/{object_id}"]["get"]>;
```

Код: [types.ts:73](../../../../../web/admin/src/api/types.ts#L73).

### Тип `EntityState`

```typescript
type EntityState = ItemOf<Ok<Sto["/v1/entities"]["get"]>>;
```

Код: [types.ts:74](../../../../../web/admin/src/api/types.ts#L74).

### Тип `EntityHistoryEntry`

```typescript
type EntityHistoryEntry = ItemOf<Ok<Sto["/v1/entity-history"]["get"]>>;
```

Код: [types.ts:75](../../../../../web/admin/src/api/types.ts#L75).

### Тип `Provider`

```typescript
type Provider = Ok<Llm["/v1/providers/{provider_id}"]["get"]>;
```

Код: [types.ts:78](../../../../../web/admin/src/api/types.ts#L78).

### Тип `ModelAlias`

```typescript
type ModelAlias = ItemOf<Ok<Llm["/v1/model-aliases"]["get"]>>;
```

Код: [types.ts:79](../../../../../web/admin/src/api/types.ts#L79).

### Тип `BudgetDefinition`

```typescript
type BudgetDefinition = ItemOf<Ok<Llm["/v1/budgets"]["get"]>>;
```

Код: [types.ts:80](../../../../../web/admin/src/api/types.ts#L80).

### Тип `UsageReport`

```typescript
type UsageReport = Ok<Llm["/v1/usage"]["get"]>;
```

Код: [types.ts:81](../../../../../web/admin/src/api/types.ts#L81).

### Тип `Money`

```typescript
type Money = NonNullable<Run["costs"]>["llm"];
```

Код: [types.ts:82](../../../../../web/admin/src/api/types.ts#L82).

### Тип `TestRunRequest`

```typescript
type TestRunRequest = Body<Hdl["/v1/test-runs"]["post"]>;
```

Код: [types.ts:85](../../../../../web/admin/src/api/types.ts#L85).

### Тип `ConnectionTestResult`

```typescript
type ConnectionTestResult = Ok<Hdl["/v1/connections/{connection_id}/test"]["post"]>;
```

Код: [types.ts:86](../../../../../web/admin/src/api/types.ts#L86).

### Тип `OnboardingRequest`

```typescript
type OnboardingRequest = Body<Asst["/v1/onboarding-sessions"]["post"]>;
```

Код: [types.ts:89](../../../../../web/admin/src/api/types.ts#L89).

### Тип `OnboardingSession`

```typescript
type OnboardingSession = Ok<Asst["/v1/onboarding-sessions/{session_id}"]["get"]>;
```

Код: [types.ts:90](../../../../../web/admin/src/api/types.ts#L90).

### Тип `OnboardingSessionSummary`

```typescript
type OnboardingSessionSummary = ItemOf<Ok<Asst["/v1/onboarding-sessions"]["get"]>>;
```

Код: [types.ts:91](../../../../../web/admin/src/api/types.ts#L91).

### Тип `OnboardingStatus`

```typescript
type OnboardingStatus = OnboardingSession["status"];
```

Код: [types.ts:92](../../../../../web/admin/src/api/types.ts#L92).

### Тип `Proposal`

```typescript
type Proposal = NonNullable<OnboardingSession["proposals"]>[number];
```

Код: [types.ts:93](../../../../../web/admin/src/api/types.ts#L93).

### Тип `ImprovementRequest`

```typescript
type ImprovementRequest = Body<Asst["/v1/improvement-runs"]["post"]>;
```

Код: [types.ts:94](../../../../../web/admin/src/api/types.ts#L94).

### Тип `ImprovementRun`

```typescript
type ImprovementRun = ItemOf<Ok<Asst["/v1/improvement-runs"]["get"]>>;
```

Код: [types.ts:95](../../../../../web/admin/src/api/types.ts#L95).

### Тип `AssistantInfo`

```typescript
type AssistantInfo = Ok<Asst["/v1/info"]["get"]>;
```

Код: [types.ts:96](../../../../../web/admin/src/api/types.ts#L96).

### Тип `ImprovementResult`

```typescript
type ImprovementResult = AsstComponents["schemas"]["ImprovementResult"];
```

Код: [types.ts:98](../../../../../web/admin/src/api/types.ts#L98).

### Тип `ImprovementProposal`

```typescript
type ImprovementProposal = AsstComponents["schemas"]["ImprovementProposal"];
```

Код: [types.ts:99](../../../../../web/admin/src/api/types.ts#L99).

### Тип `AcceptanceResult`

```typescript
type AcceptanceResult = AsstComponents["schemas"]["AcceptanceResult"];
```

Код: [types.ts:100](../../../../../web/admin/src/api/types.ts#L100).

### Тип `CollectionErrors`

```typescript
type CollectionErrors = Ok<Col["/v1/collections/{collection_id}/errors"]["get"]>;
```

Код: [types.ts:103](../../../../../web/admin/src/api/types.ts#L103).
