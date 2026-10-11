# api/types

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.types.Source](#adminapitypessource)
- [admin.api.types.TaskConfig](#adminapitypestaskconfig)
- [admin.api.types.TaskSummary](#adminapitypestasksummary)
- [admin.api.types.Stage](#adminapitypesstage)
- [admin.api.types.Schedule](#adminapitypesschedule)
- [admin.api.types.TaskValidation](#adminapitypestaskvalidation)
- [admin.api.types.RunRequest](#adminapitypesrunrequest)
- [admin.api.types.Run](#adminapitypesrun)
- [admin.api.types.StageItem](#adminapitypesstageitem)
- [admin.api.types.AttemptEvent](#adminapitypesattemptevent)
- [admin.api.types.MaterialTrace](#adminapitypesmaterialtrace)
- [admin.api.types.UnknownMaterial](#adminapitypesunknownmaterial)
- [admin.api.types.ProblemGroup](#adminapitypesproblemgroup)
- [admin.api.types.ProblemGroupStatus](#adminapitypesproblemgroupstatus)
- [admin.api.types.ReprocessRequest](#adminapitypesreprocessrequest)
- [admin.api.types.PlatformConnection](#adminapitypesplatformconnection)
- [admin.api.types.Connection](#adminapitypesconnection)
- [admin.api.types.PlatformLimits](#adminapitypesplatformlimits)
- [admin.api.types.Limits](#adminapitypeslimits)
- [admin.api.types.EffectiveLimits](#adminapitypeseffectivelimits)
- [admin.api.types.Executor](#adminapitypesexecutor)
- [admin.api.types.AuditEvent](#adminapitypesauditevent)
- [admin.api.types.Activation](#adminapitypesactivation)
- [admin.api.types.ActivationRequest](#adminapitypesactivationrequest)
- [admin.api.types.Job](#adminapitypesjob)
- [admin.api.types.JobStatus](#adminapitypesjobstatus)
- [admin.api.types.PackageRef](#adminapitypespackageref)
- [admin.api.types.Package](#adminapitypespackage)
- [admin.api.types.PackageVersion](#adminapitypespackageversion)
- [admin.api.types.PackageManifest](#adminapitypespackagemanifest)
- [admin.api.types.PublishRequest](#adminapitypespublishrequest)
- [admin.api.types.PackageDiff](#adminapitypespackagediff)
- [admin.api.types.UpstreamStatus](#adminapitypesupstreamstatus)
- [admin.api.types.ForkRequest](#adminapitypesforkrequest)
- [admin.api.types.StatusChange](#adminapitypesstatuschange)
- [admin.api.types.HandlerKind](#adminapitypeshandlerkind)
- [admin.api.types.VersionStatus](#adminapitypesversionstatus)
- [admin.api.types.TestResultsRecord](#adminapitypestestresultsrecord)
- [admin.api.types.TestReport](#adminapitypestestreport)
- [admin.api.types.TestSummary](#adminapitypestestsummary)
- [admin.api.types.StoredObject](#adminapitypesstoredobject)
- [admin.api.types.StoredObjectDetail](#adminapitypesstoredobjectdetail)
- [admin.api.types.EntityState](#adminapitypesentitystate)
- [admin.api.types.EntityHistoryEntry](#adminapitypesentityhistoryentry)
- [admin.api.types.Provider](#adminapitypesprovider)
- [admin.api.types.ModelAlias](#adminapitypesmodelalias)
- [admin.api.types.BudgetDefinition](#adminapitypesbudgetdefinition)
- [admin.api.types.UsageReport](#adminapitypesusagereport)
- [admin.api.types.Money](#adminapitypesmoney)
- [admin.api.types.TestRunRequest](#adminapitypestestrunrequest)
- [admin.api.types.ConnectionTestResult](#adminapitypesconnectiontestresult)
- [admin.api.types.OnboardingRequest](#adminapitypesonboardingrequest)
- [admin.api.types.OnboardingSession](#adminapitypesonboardingsession)
- [admin.api.types.OnboardingSessionSummary](#adminapitypesonboardingsessionsummary)
- [admin.api.types.OnboardingStatus](#adminapitypesonboardingstatus)
- [admin.api.types.Proposal](#adminapitypesproposal)
- [admin.api.types.ImprovementRequest](#adminapitypesimprovementrequest)
- [admin.api.types.ImprovementRun](#adminapitypesimprovementrun)
- [admin.api.types.AssistantInfo](#adminapitypesassistantinfo)
- [admin.api.types.ImprovementResult](#adminapitypesimprovementresult)
- [admin.api.types.ImprovementProposal](#adminapitypesimprovementproposal)
- [admin.api.types.AcceptanceResult](#adminapitypesacceptanceresult)
- [admin.api.types.CollectionErrors](#adminapitypescollectionerrors)

## admin.api.types.Source

**Тип.** Код: [web/admin/src/api/types.ts:25](../../../../../../web/admin/src/api/types.ts#L25).

```typescript
export type Source = Ok<Orch["/v1/sources/{source_id}"]["get"]>;
```

## admin.api.types.TaskConfig

**Тип.** Код: [web/admin/src/api/types.ts:26](../../../../../../web/admin/src/api/types.ts#L26).

```typescript
export type TaskConfig = Ok<Orch["/v1/tasks/{task_id}"]["get"]>;
```

## admin.api.types.TaskSummary

**Тип.** Код: [web/admin/src/api/types.ts:27](../../../../../../web/admin/src/api/types.ts#L27).

```typescript
export type TaskSummary = ItemOf<Ok<Orch["/v1/tasks"]["get"]>>;
```

## admin.api.types.Stage

**Тип.** Код: [web/admin/src/api/types.ts:28](../../../../../../web/admin/src/api/types.ts#L28).

```typescript
export type Stage = TaskConfig["stages"][number];
```

## admin.api.types.Schedule

**Тип.** Код: [web/admin/src/api/types.ts:29](../../../../../../web/admin/src/api/types.ts#L29).

```typescript
export type Schedule = NonNullable<TaskConfig["schedule"]>;
```

## admin.api.types.TaskValidation

**Тип.** Код: [web/admin/src/api/types.ts:30](../../../../../../web/admin/src/api/types.ts#L30).

```typescript
export type TaskValidation = Ok<Orch["/v1/task-validations"]["post"]>;
```

## admin.api.types.RunRequest

**Тип.** Код: [web/admin/src/api/types.ts:31](../../../../../../web/admin/src/api/types.ts#L31).

```typescript
export type RunRequest = Body<Orch["/v1/tasks/{task_id}/runs"]["post"]>;
```

## admin.api.types.Run

**Тип.** Код: [web/admin/src/api/types.ts:32](../../../../../../web/admin/src/api/types.ts#L32).

```typescript
export type Run = Ok<Orch["/v1/runs/{run_id}"]["get"]>;
```

## admin.api.types.StageItem

**Тип.** Код: [web/admin/src/api/types.ts:33](../../../../../../web/admin/src/api/types.ts#L33).

```typescript
export type StageItem = ItemOf<Ok<Orch["/v1/runs/{run_id}/items"]["get"]>>;
```

## admin.api.types.AttemptEvent

**Тип.** Код: [web/admin/src/api/types.ts:34](../../../../../../web/admin/src/api/types.ts#L34).

```typescript
export type AttemptEvent = NonNullable<StageItem["attempt_history"]>[number];
```

## admin.api.types.MaterialTrace

**Тип.** Код: [web/admin/src/api/types.ts:35](../../../../../../web/admin/src/api/types.ts#L35).

```typescript
export type MaterialTrace = Ok<Orch["/v1/materials/{material_id}/trace"]["get"]>;
```

## admin.api.types.UnknownMaterial

**Тип.** Код: [web/admin/src/api/types.ts:36](../../../../../../web/admin/src/api/types.ts#L36).

```typescript
export type UnknownMaterial = ItemOf<Ok<Orch["/v1/unknown-materials"]["get"]>>;
```

## admin.api.types.ProblemGroup

**Тип.** Код: [web/admin/src/api/types.ts:37](../../../../../../web/admin/src/api/types.ts#L37).

```typescript
export type ProblemGroup = ItemOf<Ok<Orch["/v1/problem-groups"]["get"]>>;
```

## admin.api.types.ProblemGroupStatus

**Тип.** Код: [web/admin/src/api/types.ts:38](../../../../../../web/admin/src/api/types.ts#L38).

```typescript
export type ProblemGroupStatus = ProblemGroup["status"];
```

## admin.api.types.ReprocessRequest

**Тип.** Код: [web/admin/src/api/types.ts:39](../../../../../../web/admin/src/api/types.ts#L39).

```typescript
export type ReprocessRequest = Body<Orch["/v1/reprocessing"]["post"]>;
```

## admin.api.types.PlatformConnection

**Тип.** Код: [web/admin/src/api/types.ts:40](../../../../../../web/admin/src/api/types.ts#L40).

```typescript
export type PlatformConnection = Ok<Orch["/v1/connections/{connection_id}"]["get"]>;
```

## admin.api.types.Connection

**Тип.** Код: [web/admin/src/api/types.ts:41](../../../../../../web/admin/src/api/types.ts#L41).

```typescript
export type Connection = PlatformConnection["connection"];
```

## admin.api.types.PlatformLimits

**Тип.** Код: [web/admin/src/api/types.ts:42](../../../../../../web/admin/src/api/types.ts#L42).

```typescript
export type PlatformLimits = Ok<Orch["/v1/limits/platform"]["get"]>;
```

## admin.api.types.Limits

**Тип.** Код: [web/admin/src/api/types.ts:43](../../../../../../web/admin/src/api/types.ts#L43).

```typescript
export type Limits = NonNullable<PlatformLimits["hard_caps"]>;
```

## admin.api.types.EffectiveLimits

**Тип.** Код: [web/admin/src/api/types.ts:44](../../../../../../web/admin/src/api/types.ts#L44).

```typescript
export type EffectiveLimits = Ok<Orch["/v1/limits/effective"]["get"]>;
```

## admin.api.types.Executor

**Тип.** Код: [web/admin/src/api/types.ts:45](../../../../../../web/admin/src/api/types.ts#L45).

```typescript
export type Executor = ItemOf<Ok<Orch["/v1/executors"]["get"]>>;
```

## admin.api.types.AuditEvent

**Тип.** Код: [web/admin/src/api/types.ts:46](../../../../../../web/admin/src/api/types.ts#L46).

```typescript
export type AuditEvent = ItemOf<Ok<Orch["/v1/audit-events"]["get"]>>;
```

## admin.api.types.Activation

**Тип.** Код: [web/admin/src/api/types.ts:47](../../../../../../web/admin/src/api/types.ts#L47).

```typescript
export type Activation = Ok<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
```

## admin.api.types.ActivationRequest

**Тип.** Код: [web/admin/src/api/types.ts:48](../../../../../../web/admin/src/api/types.ts#L48).

```typescript
export type ActivationRequest = Body<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
```

## admin.api.types.Job

**Тип.** Код: [web/admin/src/api/types.ts:49](../../../../../../web/admin/src/api/types.ts#L49).

```typescript
export type Job = Ok<Orch["/v1/jobs/{job_id}"]["get"]>;
```

## admin.api.types.JobStatus

**Тип.** Код: [web/admin/src/api/types.ts:50](../../../../../../web/admin/src/api/types.ts#L50).

```typescript
export type JobStatus = Job["status"];
```

## admin.api.types.PackageRef

**Тип.** Код: [web/admin/src/api/types.ts:51](../../../../../../web/admin/src/api/types.ts#L51).

```typescript
export type PackageRef = NonNullable<Source["collector_rules"]>;
```

## admin.api.types.Package

**Тип.** Код: [web/admin/src/api/types.ts:54](../../../../../../web/admin/src/api/types.ts#L54).

```typescript
export type Package = Ok<Reg["/v1/packages/{package_id}"]["get"]>;
```

## admin.api.types.PackageVersion

**Тип.** Код: [web/admin/src/api/types.ts:55](../../../../../../web/admin/src/api/types.ts#L55).

```typescript
export type PackageVersion = Ok<Reg["/v1/packages/{package_id}/versions/{version}"]["get"]>;
```

## admin.api.types.PackageManifest

**Тип.** Код: [web/admin/src/api/types.ts:56](../../../../../../web/admin/src/api/types.ts#L56).

```typescript
export type PackageManifest = NonNullable<PackageVersion["manifest"]>;
```

## admin.api.types.PublishRequest

**Тип.** Код: [web/admin/src/api/types.ts:57](../../../../../../web/admin/src/api/types.ts#L57).

```typescript
export type PublishRequest = Extract<
  NonNullable<Reg["/v1/packages/{package_id}/versions"]["post"]["requestBody"]>["content"],
  { "application/json": unknown }
>["application/json"];
```

## admin.api.types.PackageDiff

**Тип.** Код: [web/admin/src/api/types.ts:61](../../../../../../web/admin/src/api/types.ts#L61).

```typescript
export type PackageDiff = Ok<Reg["/v1/packages/{package_id}/diff"]["get"]>;
```

## admin.api.types.UpstreamStatus

**Тип.** Код: [web/admin/src/api/types.ts:62](../../../../../../web/admin/src/api/types.ts#L62).

```typescript
export type UpstreamStatus = Ok<Reg["/v1/packages/{package_id}/upstream"]["get"]>;
```

## admin.api.types.ForkRequest

**Тип.** Код: [web/admin/src/api/types.ts:63](../../../../../../web/admin/src/api/types.ts#L63).

```typescript
export type ForkRequest = Body<Reg["/v1/packages/{package_id}/forks"]["post"]>;
```

## admin.api.types.StatusChange

**Тип.** Код: [web/admin/src/api/types.ts:64](../../../../../../web/admin/src/api/types.ts#L64).

```typescript
export type StatusChange = Body<Reg["/v1/packages/{package_id}/versions/{version}/status"]["post"]>;
```

## admin.api.types.HandlerKind

**Тип.** Код: [web/admin/src/api/types.ts:65](../../../../../../web/admin/src/api/types.ts#L65).

```typescript
export type HandlerKind = Package["kind"];
```

## admin.api.types.VersionStatus

**Тип.** Код: [web/admin/src/api/types.ts:66](../../../../../../web/admin/src/api/types.ts#L66).

```typescript
export type VersionStatus = PackageVersion["status"];
```

## admin.api.types.TestResultsRecord

**Тип.** Код: [web/admin/src/api/types.ts:67](../../../../../../web/admin/src/api/types.ts#L67).

```typescript
export type TestResultsRecord = NonNullable<PackageVersion["test_reports"]>[number];
```

## admin.api.types.TestReport

**Тип.** Код: [web/admin/src/api/types.ts:68](../../../../../../web/admin/src/api/types.ts#L68).

```typescript
export type TestReport = TestResultsRecord["report"];
```

## admin.api.types.TestSummary

**Тип.** Код: [web/admin/src/api/types.ts:69](../../../../../../web/admin/src/api/types.ts#L69).

```typescript
export type TestSummary = NonNullable<PackageVersion["test_summary"]>;
```

## admin.api.types.StoredObject

**Тип.** Код: [web/admin/src/api/types.ts:72](../../../../../../web/admin/src/api/types.ts#L72).

```typescript
export type StoredObject = ItemOf<Ok<Sto["/v1/objects"]["get"]>>;
```

## admin.api.types.StoredObjectDetail

**Тип.** Код: [web/admin/src/api/types.ts:73](../../../../../../web/admin/src/api/types.ts#L73).

```typescript
export type StoredObjectDetail = Ok<Sto["/v1/objects/{object_id}"]["get"]>;
```

## admin.api.types.EntityState

**Тип.** Код: [web/admin/src/api/types.ts:74](../../../../../../web/admin/src/api/types.ts#L74).

```typescript
export type EntityState = ItemOf<Ok<Sto["/v1/entities"]["get"]>>;
```

## admin.api.types.EntityHistoryEntry

**Тип.** Код: [web/admin/src/api/types.ts:75](../../../../../../web/admin/src/api/types.ts#L75).

```typescript
export type EntityHistoryEntry = ItemOf<Ok<Sto["/v1/entity-history"]["get"]>>;
```

## admin.api.types.Provider

**Тип.** Код: [web/admin/src/api/types.ts:78](../../../../../../web/admin/src/api/types.ts#L78).

```typescript
export type Provider = Ok<Llm["/v1/providers/{provider_id}"]["get"]>;
```

## admin.api.types.ModelAlias

**Тип.** Код: [web/admin/src/api/types.ts:79](../../../../../../web/admin/src/api/types.ts#L79).

```typescript
export type ModelAlias = ItemOf<Ok<Llm["/v1/model-aliases"]["get"]>>;
```

## admin.api.types.BudgetDefinition

**Тип.** Код: [web/admin/src/api/types.ts:80](../../../../../../web/admin/src/api/types.ts#L80).

```typescript
export type BudgetDefinition = ItemOf<Ok<Llm["/v1/budgets"]["get"]>>;
```

## admin.api.types.UsageReport

**Тип.** Код: [web/admin/src/api/types.ts:81](../../../../../../web/admin/src/api/types.ts#L81).

```typescript
export type UsageReport = Ok<Llm["/v1/usage"]["get"]>;
```

## admin.api.types.Money

**Тип.** Код: [web/admin/src/api/types.ts:82](../../../../../../web/admin/src/api/types.ts#L82).

```typescript
export type Money = NonNullable<Run["costs"]>["llm"];
```

## admin.api.types.TestRunRequest

**Тип.** Код: [web/admin/src/api/types.ts:85](../../../../../../web/admin/src/api/types.ts#L85).

```typescript
export type TestRunRequest = Body<Hdl["/v1/test-runs"]["post"]>;
```

## admin.api.types.ConnectionTestResult

**Тип.** Код: [web/admin/src/api/types.ts:86](../../../../../../web/admin/src/api/types.ts#L86).

```typescript
export type ConnectionTestResult = Ok<Hdl["/v1/connections/{connection_id}/test"]["post"]>;
```

## admin.api.types.OnboardingRequest

**Тип.** Код: [web/admin/src/api/types.ts:89](../../../../../../web/admin/src/api/types.ts#L89).

```typescript
export type OnboardingRequest = Body<Asst["/v1/onboarding-sessions"]["post"]>;
```

## admin.api.types.OnboardingSession

**Тип.** Код: [web/admin/src/api/types.ts:90](../../../../../../web/admin/src/api/types.ts#L90).

```typescript
export type OnboardingSession = Ok<Asst["/v1/onboarding-sessions/{session_id}"]["get"]>;
```

## admin.api.types.OnboardingSessionSummary

**Тип.** Код: [web/admin/src/api/types.ts:91](../../../../../../web/admin/src/api/types.ts#L91).

```typescript
export type OnboardingSessionSummary = ItemOf<Ok<Asst["/v1/onboarding-sessions"]["get"]>>;
```

## admin.api.types.OnboardingStatus

**Тип.** Код: [web/admin/src/api/types.ts:92](../../../../../../web/admin/src/api/types.ts#L92).

```typescript
export type OnboardingStatus = OnboardingSession["status"];
```

## admin.api.types.Proposal

**Тип.** Код: [web/admin/src/api/types.ts:93](../../../../../../web/admin/src/api/types.ts#L93).

```typescript
export type Proposal = NonNullable<OnboardingSession["proposals"]>[number];
```

## admin.api.types.ImprovementRequest

**Тип.** Код: [web/admin/src/api/types.ts:94](../../../../../../web/admin/src/api/types.ts#L94).

```typescript
export type ImprovementRequest = Body<Asst["/v1/improvement-runs"]["post"]>;
```

## admin.api.types.ImprovementRun

**Тип.** Код: [web/admin/src/api/types.ts:95](../../../../../../web/admin/src/api/types.ts#L95).

```typescript
export type ImprovementRun = ItemOf<Ok<Asst["/v1/improvement-runs"]["get"]>>;
```

## admin.api.types.AssistantInfo

**Тип.** Код: [web/admin/src/api/types.ts:96](../../../../../../web/admin/src/api/types.ts#L96).

```typescript
export type AssistantInfo = Ok<Asst["/v1/info"]["get"]>;
```

## admin.api.types.ImprovementResult

**Тип.** Код: [web/admin/src/api/types.ts:98](../../../../../../web/admin/src/api/types.ts#L98).

```typescript
export type ImprovementResult = AsstComponents["schemas"]["ImprovementResult"];
```

## admin.api.types.ImprovementProposal

**Тип.** Код: [web/admin/src/api/types.ts:99](../../../../../../web/admin/src/api/types.ts#L99).

```typescript
export type ImprovementProposal = AsstComponents["schemas"]["ImprovementProposal"];
```

## admin.api.types.AcceptanceResult

**Тип.** Код: [web/admin/src/api/types.ts:100](../../../../../../web/admin/src/api/types.ts#L100).

```typescript
export type AcceptanceResult = AsstComponents["schemas"]["AcceptanceResult"];
```

## admin.api.types.CollectionErrors

**Тип.** Код: [web/admin/src/api/types.ts:103](../../../../../../web/admin/src/api/types.ts#L103).

```typescript
export type CollectionErrors = Ok<Col["/v1/collections/{collection_id}/errors"]["get"]>;
```
