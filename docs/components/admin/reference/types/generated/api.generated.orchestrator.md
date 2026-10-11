# api/generated/orchestrator

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.generated.orchestrator.paths](#adminapigeneratedorchestratorpaths)
- [admin.api.generated.orchestrator.paths./v1/health](#adminapigeneratedorchestratorpathsv1health)
- [admin.api.generated.orchestrator.paths./v1/info](#adminapigeneratedorchestratorpathsv1info)
- [admin.api.generated.orchestrator.paths./v1/sources](#adminapigeneratedorchestratorpathsv1sources)
- [admin.api.generated.orchestrator.paths./v1/sources/{source_id}](#adminapigeneratedorchestratorpathsv1sourcessource_id)
- [admin.api.generated.orchestrator.paths./v1/tasks](#adminapigeneratedorchestratorpathsv1tasks)
- [admin.api.generated.orchestrator.paths./v1/tasks/{task_id}](#adminapigeneratedorchestratorpathsv1taskstask_id)
- [admin.api.generated.orchestrator.paths./v1/task-validations](#adminapigeneratedorchestratorpathsv1task-validations)
- [admin.api.generated.orchestrator.paths./v1/tasks/{task_id}/runs](#adminapigeneratedorchestratorpathsv1taskstask_idruns)
- [admin.api.generated.orchestrator.paths./v1/tasks/{task_id}/stages/{stage_id}/activations](#adminapigeneratedorchestratorpathsv1taskstask_idstagesstage_idactivations)
- [admin.api.generated.orchestrator.paths./v1/runs](#adminapigeneratedorchestratorpathsv1runs)
- [admin.api.generated.orchestrator.paths./v1/runs/{run_id}](#adminapigeneratedorchestratorpathsv1runsrun_id)
- [admin.api.generated.orchestrator.paths./v1/runs/{run_id}/cancel](#adminapigeneratedorchestratorpathsv1runsrun_idcancel)
- [admin.api.generated.orchestrator.paths./v1/runs/{run_id}/items](#adminapigeneratedorchestratorpathsv1runsrun_iditems)
- [admin.api.generated.orchestrator.paths./v1/materials/{material_id}/trace](#adminapigeneratedorchestratorpathsv1materialsmaterial_idtrace)
- [admin.api.generated.orchestrator.paths./v1/unknown-materials](#adminapigeneratedorchestratorpathsv1unknown-materials)
- [admin.api.generated.orchestrator.paths./v1/problem-groups](#adminapigeneratedorchestratorpathsv1problem-groups)
- [admin.api.generated.orchestrator.paths./v1/problem-groups/{group_id}](#adminapigeneratedorchestratorpathsv1problem-groupsgroup_id)
- [admin.api.generated.orchestrator.paths./v1/reprocessing](#adminapigeneratedorchestratorpathsv1reprocessing)
- [admin.api.generated.orchestrator.paths./v1/connections](#adminapigeneratedorchestratorpathsv1connections)
- [admin.api.generated.orchestrator.paths./v1/connections/{connection_id}](#adminapigeneratedorchestratorpathsv1connectionsconnection_id)
- [admin.api.generated.orchestrator.paths./v1/limits/platform](#adminapigeneratedorchestratorpathsv1limitsplatform)
- [admin.api.generated.orchestrator.paths./v1/limits/effective](#adminapigeneratedorchestratorpathsv1limitseffective)
- [admin.api.generated.orchestrator.paths./v1/executors](#adminapigeneratedorchestratorpathsv1executors)
- [admin.api.generated.orchestrator.paths./v1/audit-events](#adminapigeneratedorchestratorpathsv1audit-events)
- [admin.api.generated.orchestrator.paths./v1/jobs/{job_id}](#adminapigeneratedorchestratorpathsv1jobsjob_id)
- [admin.api.generated.orchestrator.paths./v1/jobs/{job_id}/cancel](#adminapigeneratedorchestratorpathsv1jobsjob_idcancel)
- [admin.api.generated.orchestrator.webhooks](#adminapigeneratedorchestratorwebhooks)
- [admin.api.generated.orchestrator.components](#adminapigeneratedorchestratorcomponents)
- [admin.api.generated.orchestrator.components.schemas](#adminapigeneratedorchestratorcomponentsschemas)
- [admin.api.generated.orchestrator.components.responses](#adminapigeneratedorchestratorcomponentsresponses)
- [admin.api.generated.orchestrator.components.parameters](#adminapigeneratedorchestratorcomponentsparameters)
- [admin.api.generated.orchestrator.components.requestBodies](#adminapigeneratedorchestratorcomponentsrequestbodies)
- [admin.api.generated.orchestrator.components.headers](#adminapigeneratedorchestratorcomponentsheaders)
- [admin.api.generated.orchestrator.components.pathItems](#adminapigeneratedorchestratorcomponentspathitems)
- [admin.api.generated.orchestrator.$defs](#adminapigeneratedorchestratordefs)
- [admin.api.generated.orchestrator.operations](#adminapigeneratedorchestratoroperations)
- [admin.api.generated.orchestrator.operations.getHealth](#adminapigeneratedorchestratoroperationsgethealth)
- [admin.api.generated.orchestrator.operations.getServiceInfo](#adminapigeneratedorchestratoroperationsgetserviceinfo)
- [admin.api.generated.orchestrator.operations.listSources](#adminapigeneratedorchestratoroperationslistsources)
- [admin.api.generated.orchestrator.operations.createSource](#adminapigeneratedorchestratoroperationscreatesource)
- [admin.api.generated.orchestrator.operations.getSource](#adminapigeneratedorchestratoroperationsgetsource)
- [admin.api.generated.orchestrator.operations.replaceSource](#adminapigeneratedorchestratoroperationsreplacesource)
- [admin.api.generated.orchestrator.operations.deleteSource](#adminapigeneratedorchestratoroperationsdeletesource)
- [admin.api.generated.orchestrator.operations.listTasks](#adminapigeneratedorchestratoroperationslisttasks)
- [admin.api.generated.orchestrator.operations.createTask](#adminapigeneratedorchestratoroperationscreatetask)
- [admin.api.generated.orchestrator.operations.getTask](#adminapigeneratedorchestratoroperationsgettask)
- [admin.api.generated.orchestrator.operations.replaceTask](#adminapigeneratedorchestratoroperationsreplacetask)
- [admin.api.generated.orchestrator.operations.deleteTask](#adminapigeneratedorchestratoroperationsdeletetask)
- [admin.api.generated.orchestrator.operations.validateTask](#adminapigeneratedorchestratoroperationsvalidatetask)
- [admin.api.generated.orchestrator.operations.startRun](#adminapigeneratedorchestratoroperationsstartrun)
- [admin.api.generated.orchestrator.operations.listStageActivations](#adminapigeneratedorchestratoroperationsliststageactivations)
- [admin.api.generated.orchestrator.operations.activateStageVersion](#adminapigeneratedorchestratoroperationsactivatestageversion)
- [admin.api.generated.orchestrator.operations.listRuns](#adminapigeneratedorchestratoroperationslistruns)
- [admin.api.generated.orchestrator.operations.getRun](#adminapigeneratedorchestratoroperationsgetrun)
- [admin.api.generated.orchestrator.operations.cancelRun](#adminapigeneratedorchestratoroperationscancelrun)
- [admin.api.generated.orchestrator.operations.listRunItems](#adminapigeneratedorchestratoroperationslistrunitems)
- [admin.api.generated.orchestrator.operations.getMaterialTrace](#adminapigeneratedorchestratoroperationsgetmaterialtrace)
- [admin.api.generated.orchestrator.operations.listUnknownMaterials](#adminapigeneratedorchestratoroperationslistunknownmaterials)
- [admin.api.generated.orchestrator.operations.listProblemGroups](#adminapigeneratedorchestratoroperationslistproblemgroups)
- [admin.api.generated.orchestrator.operations.updateProblemGroup](#adminapigeneratedorchestratoroperationsupdateproblemgroup)
- [admin.api.generated.orchestrator.operations.startReprocessing](#adminapigeneratedorchestratoroperationsstartreprocessing)
- [admin.api.generated.orchestrator.operations.listPlatformConnections](#adminapigeneratedorchestratoroperationslistplatformconnections)
- [admin.api.generated.orchestrator.operations.getPlatformConnection](#adminapigeneratedorchestratoroperationsgetplatformconnection)
- [admin.api.generated.orchestrator.operations.putPlatformConnection](#adminapigeneratedorchestratoroperationsputplatformconnection)
- [admin.api.generated.orchestrator.operations.deletePlatformConnection](#adminapigeneratedorchestratoroperationsdeleteplatformconnection)
- [admin.api.generated.orchestrator.operations.getPlatformLimits](#adminapigeneratedorchestratoroperationsgetplatformlimits)
- [admin.api.generated.orchestrator.operations.putPlatformLimits](#adminapigeneratedorchestratoroperationsputplatformlimits)
- [admin.api.generated.orchestrator.operations.getEffectiveLimits](#adminapigeneratedorchestratoroperationsgeteffectivelimits)
- [admin.api.generated.orchestrator.operations.listExecutors](#adminapigeneratedorchestratoroperationslistexecutors)
- [admin.api.generated.orchestrator.operations.listAuditEvents](#adminapigeneratedorchestratoroperationslistauditevents)
- [admin.api.generated.orchestrator.operations.getJob](#adminapigeneratedorchestratoroperationsgetjob)
- [admin.api.generated.orchestrator.operations.cancelJob](#adminapigeneratedorchestratoroperationscanceljob)

## admin.api.generated.orchestrator.paths

**Інтерфейс.** Код: [web/admin/src/api/generated/orchestrator.ts:3](../../../../../../web/admin/src/api/generated/orchestrator.ts#L3).

```typescript
interface paths {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [/v1/health](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1health) | Поле | ні |
| [/v1/info](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1info) | Поле | ні |
| [/v1/sources](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1sources) | Поле | ні |
| [/v1/sources/{source_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1sourcessource_id) | Поле | ні |
| [/v1/tasks](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1tasks) | Поле | ні |
| [/v1/tasks/{task_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1taskstask_id) | Поле | ні |
| [/v1/task-validations](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1task-validations) | Поле | ні |
| [/v1/tasks/{task_id}/runs](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1taskstask_idruns) | Поле | ні |
| [/v1/tasks/{task_id}/stages/{stage_id}/activations](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1taskstask_idstagesstage_idactivations) | Поле | ні |
| [/v1/runs](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1runs) | Поле | ні |
| [/v1/runs/{run_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1runsrun_id) | Поле | ні |
| [/v1/runs/{run_id}/cancel](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1runsrun_idcancel) | Поле | ні |
| [/v1/runs/{run_id}/items](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1runsrun_iditems) | Поле | ні |
| [/v1/materials/{material_id}/trace](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1materialsmaterial_idtrace) | Поле | ні |
| [/v1/unknown-materials](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1unknown-materials) | Поле | ні |
| [/v1/problem-groups](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1problem-groups) | Поле | ні |
| [/v1/problem-groups/{group_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1problem-groupsgroup_id) | Поле | ні |
| [/v1/reprocessing](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1reprocessing) | Поле | ні |
| [/v1/connections](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1connections) | Поле | ні |
| [/v1/connections/{connection_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1connectionsconnection_id) | Поле | ні |
| [/v1/limits/platform](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1limitsplatform) | Поле | ні |
| [/v1/limits/effective](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1limitseffective) | Поле | ні |
| [/v1/executors](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1executors) | Поле | ні |
| [/v1/audit-events](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1audit-events) | Поле | ні |
| [/v1/jobs/{job_id}](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1jobsjob_id) | Поле | ні |
| [/v1/jobs/{job_id}/cancel](api.generated.orchestrator.md#adminapigeneratedorchestratorpathsv1jobsjob_idcancel) | Поле | ні |

## admin.api.generated.orchestrator.paths./v1/health

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:4](../../../../../../web/admin/src/api/generated/orchestrator.ts#L4).

```typescript
/v1/health: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getHealth"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/info

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:21](../../../../../../web/admin/src/api/generated/orchestrator.ts#L21).

```typescript
/v1/info: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getServiceInfo"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/sources

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:38](../../../../../../web/admin/src/api/generated/orchestrator.ts#L38).

```typescript
/v1/sources: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listSources"]; put?: never; post: operations["createSource"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/sources/{source_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:56](../../../../../../web/admin/src/api/generated/orchestrator.ts#L56).

```typescript
/v1/sources/{source_id}: { parameters: { query?: never; header?: never; path: { source_id: components["parameters"]["SourceId"]; }; cookie?: never; }; get: operations["getSource"]; put: operations["replaceSource"]; post?: never; delete: operations["deleteSource"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/tasks

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:77](../../../../../../web/admin/src/api/generated/orchestrator.ts#L77).

```typescript
/v1/tasks: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listTasks"]; put?: never; post: operations["createTask"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/tasks/{task_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:101](../../../../../../web/admin/src/api/generated/orchestrator.ts#L101).

```typescript
/v1/tasks/{task_id}: { parameters: { query?: never; header?: never; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; get: operations["getTask"]; put: operations["replaceTask"]; post?: never; delete: operations["deleteTask"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/task-validations

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:122](../../../../../../web/admin/src/api/generated/orchestrator.ts#L122).

```typescript
/v1/task-validations: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["validateTask"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/tasks/{task_id}/runs

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:139](../../../../../../web/admin/src/api/generated/orchestrator.ts#L139).

```typescript
/v1/tasks/{task_id}/runs: { parameters: { query?: never; header?: never; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["startRun"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/tasks/{task_id}/stages/{stage_id}/activations

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:158](../../../../../../web/admin/src/api/generated/orchestrator.ts#L158).

```typescript
/v1/tasks/{task_id}/stages/{stage_id}/activations: { parameters: { query?: never; header?: never; path: { task_id: components["parameters"]["TaskId"]; stage_id: components["schemas"]["Slug"]; }; cookie?: never; }; get: operations["listStageActivations"]; put?: never; post: operations["activateStageVersion"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/runs

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:194](../../../../../../web/admin/src/api/generated/orchestrator.ts#L194).

```typescript
/v1/runs: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listRuns"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/runs/{run_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:211](../../../../../../web/admin/src/api/generated/orchestrator.ts#L211).

```typescript
/v1/runs/{run_id}: { parameters: { query?: never; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; get: operations["getRun"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/runs/{run_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:230](../../../../../../web/admin/src/api/generated/orchestrator.ts#L230).

```typescript
/v1/runs/{run_id}/cancel: { parameters: { query?: never; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelRun"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/runs/{run_id}/items

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:249](../../../../../../web/admin/src/api/generated/orchestrator.ts#L249).

```typescript
/v1/runs/{run_id}/items: { parameters: { query?: never; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; get: operations["listRunItems"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/materials/{material_id}/trace

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:268](../../../../../../web/admin/src/api/generated/orchestrator.ts#L268).

```typescript
/v1/materials/{material_id}/trace: { parameters: { query?: never; header?: never; path: { material_id: components["schemas"]["Id"]; }; cookie?: never; }; get: operations["getMaterialTrace"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/unknown-materials

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:287](../../../../../../web/admin/src/api/generated/orchestrator.ts#L287).

```typescript
/v1/unknown-materials: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listUnknownMaterials"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/problem-groups

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:304](../../../../../../web/admin/src/api/generated/orchestrator.ts#L304).

```typescript
/v1/problem-groups: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listProblemGroups"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/problem-groups/{group_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:321](../../../../../../web/admin/src/api/generated/orchestrator.ts#L321).

```typescript
/v1/problem-groups/{group_id}: { parameters: { query?: never; header?: never; path: { group_id: components["schemas"]["Id"]; }; cookie?: never; }; get?: never; put?: never; post?: never; delete?: never; options?: never; head?: never; patch: operations["updateProblemGroup"]; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/reprocessing

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:340](../../../../../../web/admin/src/api/generated/orchestrator.ts#L340).

```typescript
/v1/reprocessing: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get?: never; put?: never; post: operations["startReprocessing"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/connections

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:357](../../../../../../web/admin/src/api/generated/orchestrator.ts#L357).

```typescript
/v1/connections: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listPlatformConnections"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/connections/{connection_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:374](../../../../../../web/admin/src/api/generated/orchestrator.ts#L374).

```typescript
/v1/connections/{connection_id}: { parameters: { query?: never; header?: never; path: { connection_id: components["schemas"]["Slug"]; }; cookie?: never; }; get: operations["getPlatformConnection"]; put: operations["putPlatformConnection"]; post?: never; delete: operations["deletePlatformConnection"]; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/limits/platform

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:395](../../../../../../web/admin/src/api/generated/orchestrator.ts#L395).

```typescript
/v1/limits/platform: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getPlatformLimits"]; put: operations["putPlatformLimits"]; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/limits/effective

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:413](../../../../../../web/admin/src/api/generated/orchestrator.ts#L413).

```typescript
/v1/limits/effective: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["getEffectiveLimits"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/executors

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:430](../../../../../../web/admin/src/api/generated/orchestrator.ts#L430).

```typescript
/v1/executors: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listExecutors"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/audit-events

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:447](../../../../../../web/admin/src/api/generated/orchestrator.ts#L447).

```typescript
/v1/audit-events: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; get: operations["listAuditEvents"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/jobs/{job_id}

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:464](../../../../../../web/admin/src/api/generated/orchestrator.ts#L464).

```typescript
/v1/jobs/{job_id}: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get: operations["getJob"]; put?: never; post?: never; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.paths./v1/jobs/{job_id}/cancel

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:483](../../../../../../web/admin/src/api/generated/orchestrator.ts#L483).

```typescript
/v1/jobs/{job_id}/cancel: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; get?: never; put?: never; post: operations["cancelJob"]; delete?: never; options?: never; head?: never; patch?: never; trace?: never; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.webhooks

**Тип.** Код: [web/admin/src/api/generated/orchestrator.ts:508](../../../../../../web/admin/src/api/generated/orchestrator.ts#L508).

```typescript
export type webhooks = Record<string, never>;
```

## admin.api.generated.orchestrator.components

**Інтерфейс.** Код: [web/admin/src/api/generated/orchestrator.ts:509](../../../../../../web/admin/src/api/generated/orchestrator.ts#L509).

```typescript
interface components {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [schemas](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentsschemas) | Поле | ні |
| [responses](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentsresponses) | Поле | ні |
| [parameters](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentsparameters) | Поле | ні |
| [requestBodies](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentsrequestbodies) | Поле | ні |
| [headers](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentsheaders) | Поле | ні |
| [pathItems](api.generated.orchestrator.md#adminapigeneratedorchestratorcomponentspathitems) | Поле | ні |

## admin.api.generated.orchestrator.components.schemas

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:510](../../../../../../web/admin/src/api/generated/orchestrator.ts#L510).

```typescript
schemas: { TaskSummary: { task_id: string; title: string; source_id: string; enabled: boolean; schedule?: components["schemas"]["Schedule"]; next_run_at?: string; package_stages?: { stage_id: string; package: components["schemas"]["package-ref.schema"]; }[]; last_run?: { run_id?: string; status?: components["schemas"]["JobStatus"]; finished_at?: string; }; }; TaskValidation: { valid: boolean; errors: components["schemas"]["FieldError"][]; warnings?: components["schemas"]["FieldError"][]; effective_forward_unknown_to_llm?: boolean; }; RunRequest: { reason?: string; test_mode?: boolean; input_override?: { urls?: string[]; stored_materials?: components["schemas"]["stored_materials"]; }; limits?: components["schemas"]["limits.schema"]; }; ItemStatus: "queued" | "leased" | "running" | "completed" | "retrying" | "failed" | "skipped" | "cancelled"; StageProgress: { stage_id: string; handler?: components["schemas"]["package-ref.schema"]; counts?: { [key: string]: number; }; }; Run: { run_id: components["schemas"]["Id"]; task_id: components["schemas"]["Slug"]; task_etag?: string; status: components["schemas"]["JobStatus"]; trigger: "manual" | "schedule" | "reprocess" | "assistant" | "api"; test_mode?: boolean; created_at: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; collection_id?: string; stages?: components["schemas"]["StageProgress"][]; counters?: { [key: string]: number; }; backpressure?: boolean; costs?: { llm?: components["schemas"]["Money"]; }; error?: components["schemas"]["problem.schema"]; }; StageItem: { item_id: components["schemas"]["Id"]; stage_id: string; material_id?: string; observation_id?: string; status: components["schemas"]["ItemStatus"]; result_status?: components["schemas"]["HandlerStatus"]; attempts: number; handler?: components["schemas"]["package-ref.schema"]; invocation_id?: string; delivery_key?: string; error?: components["schemas"]["problem.schema"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; available_at?: components["schemas"]["Timestamp"]; attempt_history?: components["schemas"]["AttemptHistory"]; }; AttemptHistory: components["schemas"]["AttemptEvent"][]; AttemptEvent: { event: string; at: components["schemas"]["Timestamp"]; attempt?: number; available_at?: components["schemas"]["Timestamp"]; delay_ms?: number; code?: string; }; MaterialTrace: { material_id: string; source_id?: string; url?: string; observations: { observation_id: string; run_id?: string; task_id?: string; fetched_at?: components["schemas"]["Timestamp"]; content_sha256?: string; stages: { stage_id: string; handler?: components["schemas"]["package-ref.schema"]; invocation_id?: string; result_status?: components["schemas"]["HandlerStatus"]; item_id?: string; status?: components["schemas"]["ItemStatus"]; attempts?: number; available_at?: components["schemas"]["Timestamp"]; attempt_history?: components["schemas"]["AttemptHistory"]; outputs?: { kind: "entity" | "stored_object" | "data"; entity_type?: string; canonical_key?: string; object_id?: string; connection_id?: string; }[]; }[]; }[]; }; UnknownMaterial: { material_id: string; observation_id: string; source_id: string; run_id?: string; url?: string; registered_at: components["schemas"]["Timestamp"]; forwarded_to_llm: boolean; reason?: string; stored_object_id?: string; }; ProblemGroupStatus: "open" | "in_progress" | "resolved" | "ignored" | "unresolved"; ProblemGroup: { group_id: components["schemas"]["Id"]; source_id: string; package?: components["schemas"]["package-ref.schema"]; problem: "unrecognized" | "failed"; failure_kind?: string; signature: string; count: number; first_seen_at?: components["schemas"]["Timestamp"]; last_seen_at?: components["schemas"]["Timestamp"]; status: components["schemas"]["ProblemGroupStatus"]; assistant_job_id?: string; note?: string; samples?: { material_id?: string; observation_id?: string; invocation_id?: string; stored_object_id?: string; }[]; }; ReprocessRequest: { task_id: components["schemas"]["Slug"]; stored_materials: components["schemas"]["stored_materials"]; from_stage?: components["schemas"]["Slug"]; test_mode?: boolean; reason?: string; }; PlatformConnection: { connection: components["schemas"]["connection.schema"]; executors?: { executor: string; sync_status: "pending" | "synced" | "failed"; synced_at?: components["schemas"]["Timestamp"]; message?: string; }[]; }; ActivationRequest: { kind: "activate" | "rollback" | "auto_activate"; package?: components["schemas"]["package-ref.schema"]; reason?: string; }; Activation: { activation_id: components["schemas"]["Id"]; task_id: string; stage_id: string; package: components["schemas"]["package-ref.schema"]; previous?: components["schemas"]["package-ref.schema"]; kind: "activate" | "rollback" | "auto_activate"; reason?: string; activated_by?: string; activated_at: components["schemas"]["Timestamp"]; }; Executor: { executor: string; role: "collector" | "handler" | "storage_read" | "registry" | "llm" | "assistant"; base_url: string; status: "ok" | "degraded" | "down" | "unknown"; capabilities?: Record<string, unknown>; }; AuditEvent: { event_id: string; at: components["schemas"]["Timestamp"]; actor: string; action: string; subject_type: string; subject_id: string; details?: Record<string, unknown>; }; Health: { status: "ok" | "degraded" | "down"; checks?: { [key: string]: { status: "ok" | "degraded" | "down"; message?: string; }; }; }; "limits.schema": { concurrency?: { max_parallel_fetches?: number; max_parallel_fetches_per_host?: number; max_parallel_invocations?: number; max_parallel_runs_per_task?: number; max_parallel_stage_items?: number; }; rate?: { requests_per_second_per_host?: number; min_delay_ms_per_host?: number; burst_per_host?: number; respect_crawl_delay?: boolean; }; crawl?: { max_depth?: number; max_pages_per_run?: number; max_bytes_per_run?: number; max_material_bytes?: number; max_redirects?: number; max_links_per_page?: number; max_seed_urls?: number; max_frontier_size?: number; revisit_interval_seconds?: number; }; timeouts?: { connect_timeout_ms?: number; request_timeout_ms?: number; invocation_timeout_ms?: number; stage_timeout_ms?: number; run_timeout_ms?: number; sync_response_max_ms?: number; }; retries?: components["schemas"]["RetryPolicy"]; queue?: { max_queue_depth?: number; max_inflight_materials?: number; max_unacked_materials?: number; }; sandbox?: { cpu_cores?: number; memory_mb?: number; wall_time_ms?: number; max_output_bytes?: number; max_processes?: number; tmpfs_mb?: number; }; llm?: { max_requests_per_minute?: number; max_input_tokens_per_request?: number; max_output_tokens_per_request?: number; budget?: components["schemas"]["Budget"]; max_improvement_attempts?: number; max_onboarding_samples?: number; min_onboarding_confidence?: number; }; transfer?: { inline_max_bytes?: number; max_request_body_bytes?: number; transit_ttl_seconds?: number; download_url_ttl_seconds?: number; job_retention_seconds?: number; idempotency_ttl_seconds?: number; }; telegram?: { max_messages_per_run?: number; max_media_bytes?: number; max_flood_wait_seconds?: number; }; }; LimitLevel: "platform" | "source" | "task" | "stage" | "request" | "hard_cap" | "runtime"; RetryPolicy: { max_attempts?: number; initial_backoff_ms?: number; max_backoff_ms?: number; backoff_multiplier?: number; jitter?: boolean; }; Budget: { amount: number; currency: string; period: "run" | "day" | "week" | "month" | "total"; }; PlatformLimits: { profile?: string; defaults: components["schemas"]["limits.schema"]; hard_caps?: components["schemas"]["limits.schema"]; }; ServiceInfo: { service: string; version: string; api_versions: string[]; capabilities?: { [key: string]: unknown; }; auth_mode?: "none" | "api_key" | "jwt"; limits?: components["schemas"]["PlatformLimits"]; }; FieldError: { pointer?: string; parameter?: string; code?: string; message: string; }; "problem.schema": { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }; Slug: string; SourceKind: string; SemVer: string; Digest: string; "package-ref.schema": { package_id: components["schemas"]["Slug"]; version: components["schemas"]["SemVer"]; digest?: components["schemas"]["Digest"]; }; Labels: { [key: string]: string; }; Timestamp: string; "source.schema": { source_id: components["schemas"]["Slug"]; kind: components["schemas"]["SourceKind"]; title: string; description?: string; locator: { url?: string; telegram_username?: string; telegram_channel_id?: string; }; collector_rules?: components["schemas"]["package-ref.schema"]; limits?: components["schemas"]["limits.schema"]; forward_unknown_to_llm?: boolean; expected_entity_types?: string[]; change_policy?: { llm_versions?: "manual_approval" | "auto_after_checks" | "forbidden"; }; connections?: { [key: string]: components["schemas"]["Slug"]; }; labels?: components["schemas"]["Labels"]; readonly created_at?: components["schemas"]["Timestamp"]; readonly updated_at?: components["schemas"]["Timestamp"]; }; NextCursor: string | null; Schedule: { type: "manual" | "once" | "cron" | "interval"; at?: components["schemas"]["Timestamp"]; cron?: string; interval_seconds?: number; timezone?: string; start_at?: components["schemas"]["Timestamp"]; end_at?: components["schemas"]["Timestamp"]; enabled?: boolean; overlap?: "skip" | "queue" | "allow"; } & (unknown & unknown & unknown); JobStatus: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; Id: string; CollectorStage: { collector: string; rules?: components["schemas"]["package-ref.schema"]; mode?: "full" | "incremental"; }; Condition: { all: components["schemas"]["Condition"][]; } | { any: components["schemas"]["Condition"][]; } | { not: components["schemas"]["Condition"]; } | components["schemas"]["Predicate"]; Predicate: { field: string; op: "eq" | "ne" | "in" | "not_in" | "exists" | "not_exists" | "gt" | "gte" | "lt" | "lte" | "matches_glob" | "matches_regex"; value?: unknown; }; StageInput: { from: components["schemas"]["Slug"]; select?: "output" | "input_material" | "problems" | "unmatched_materials"; when?: components["schemas"]["Condition"]; }; UrlPattern: { type?: "glob" | "regex"; value: string; }; Binding: { source_ids?: components["schemas"]["Slug"][]; sections?: components["schemas"]["Slug"][]; url_patterns?: components["schemas"]["UrlPattern"][]; media_types?: string[]; content_kinds?: string[]; }; TaskInput: { source_id: components["schemas"]["Slug"]; urls?: string[]; stored_materials?: { storage_connection_id?: components["schemas"]["Slug"]; since?: components["schemas"]["Timestamp"]; until?: components["schemas"]["Timestamp"]; material_ids?: components["schemas"]["Id"][]; object_ids?: components["schemas"]["Id"][]; observation_ids?: components["schemas"]["Id"][]; }; }; Stage: { stage_id: components["schemas"]["Slug"]; kind: "collect" | "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" | "fail_run"; } & (unknown & unknown); "task-config.schema": { task_id: components["schemas"]["Slug"]; title: string; description?: string; enabled?: boolean; input: components["schemas"]["TaskInput"]; stages: components["schemas"]["Stage"][]; schedule?: components["schemas"]["Schedule"]; retries?: components["schemas"]["RetryPolicy"]; limits?: components["schemas"]["limits.schema"]; forward_unknown_to_llm?: boolean; labels?: components["schemas"]["Labels"]; }; stored_materials: { storage_connection_id?: components["schemas"]["Slug"]; since?: components["schemas"]["Timestamp"]; until?: components["schemas"]["Timestamp"]; material_ids?: components["schemas"]["Id"][]; object_ids?: components["schemas"]["Id"][]; observation_ids?: components["schemas"]["Id"][]; }; "job.schema": { job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }; JobProgress: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: components["schemas"]["Timestamp"]; }; MediaType: string; Sha256Hex: string; InlineContent: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: components["schemas"]["Sha256Hex"]; }; BlobContent: { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: components["schemas"]["Timestamp"]; media_type: components["schemas"]["MediaType"]; charset?: string; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent"; expires_at?: string | null; }; "content-ref.schema": {} & (components["schemas"]["InlineContent"] | components["schemas"]["BlobContent"]); JobCancellation: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string; reason?: string; }; Money: { amount: number; currency: string; }; JobCancelRequest: { reason?: string; }; HandlerStatus: "success" | "empty" | "unrecognized" | "failed"; ConnectionKind: string; "connection.schema": { connection_id: components["schemas"]["Slug"]; kind: components["schemas"]["ConnectionKind"]; title?: string; params?: { [key: string]: string | number | boolean | unknown[] | Record<string, unknown>; }; secret_refs?: { [key: string]: components["schemas"]["SecretRef"]; }; labels?: components["schemas"]["Labels"]; }; SecretRef: string; EffectiveLimits: { limits: components["schemas"]["limits.schema"]; provenance: { [key: string]: components["schemas"]["LimitLevel"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.components.responses

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1375](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1375).

```typescript
responses: { Unauthenticated: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; Conflict: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; UnprocessableEntity: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; NotFound: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; PreconditionFailed: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; JobAccepted: { headers: { Location: components["headers"]["Location"]; "Idempotency-Replayed": components["headers"]["IdempotencyReplayed"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; Forbidden: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.components.parameters

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1442](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1442).

```typescript
parameters: { SourceId: components["schemas"]["Slug"]; TaskId: components["schemas"]["Slug"]; RunId: components["schemas"]["Id"]; Cursor: string; Limit: number; IdempotencyKey: string; IfMatch: string; JobId: components["schemas"]["Id"]; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.components.requestBodies

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1466](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1466).

```typescript
requestBodies: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.components.headers

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1467](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1467).

```typescript
headers: { Location: string; ETag: string; IdempotencyReplayed: boolean; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.components.pathItems

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1475](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1475).

```typescript
pathItems: never
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.$defs

**Тип.** Код: [web/admin/src/api/generated/orchestrator.ts:1477](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1477).

```typescript
export type $defs = Record<string, never>;
```

## admin.api.generated.orchestrator.operations

**Інтерфейс.** Код: [web/admin/src/api/generated/orchestrator.ts:1478](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1478).

```typescript
interface operations {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getHealth](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgethealth) | Поле | ні |
| [getServiceInfo](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetserviceinfo) | Поле | ні |
| [listSources](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistsources) | Поле | ні |
| [createSource](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationscreatesource) | Поле | ні |
| [getSource](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetsource) | Поле | ні |
| [replaceSource](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsreplacesource) | Поле | ні |
| [deleteSource](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsdeletesource) | Поле | ні |
| [listTasks](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslisttasks) | Поле | ні |
| [createTask](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationscreatetask) | Поле | ні |
| [getTask](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgettask) | Поле | ні |
| [replaceTask](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsreplacetask) | Поле | ні |
| [deleteTask](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsdeletetask) | Поле | ні |
| [validateTask](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsvalidatetask) | Поле | ні |
| [startRun](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsstartrun) | Поле | ні |
| [listStageActivations](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsliststageactivations) | Поле | ні |
| [activateStageVersion](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsactivatestageversion) | Поле | ні |
| [listRuns](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistruns) | Поле | ні |
| [getRun](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetrun) | Поле | ні |
| [cancelRun](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationscancelrun) | Поле | ні |
| [listRunItems](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistrunitems) | Поле | ні |
| [getMaterialTrace](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetmaterialtrace) | Поле | ні |
| [listUnknownMaterials](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistunknownmaterials) | Поле | ні |
| [listProblemGroups](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistproblemgroups) | Поле | ні |
| [updateProblemGroup](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsupdateproblemgroup) | Поле | ні |
| [startReprocessing](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsstartreprocessing) | Поле | ні |
| [listPlatformConnections](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistplatformconnections) | Поле | ні |
| [getPlatformConnection](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetplatformconnection) | Поле | ні |
| [putPlatformConnection](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsputplatformconnection) | Поле | ні |
| [deletePlatformConnection](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsdeleteplatformconnection) | Поле | ні |
| [getPlatformLimits](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetplatformlimits) | Поле | ні |
| [putPlatformLimits](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsputplatformlimits) | Поле | ні |
| [getEffectiveLimits](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgeteffectivelimits) | Поле | ні |
| [listExecutors](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistexecutors) | Поле | ні |
| [listAuditEvents](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationslistauditevents) | Поле | ні |
| [getJob](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationsgetjob) | Поле | ні |
| [cancelJob](api.generated.orchestrator.md#adminapigeneratedorchestratoroperationscanceljob) | Поле | ні |

## admin.api.generated.orchestrator.operations.getHealth

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1479](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1479).

```typescript
getHealth: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; 503: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Health"]; }; }; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getServiceInfo

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1508](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1508).

```typescript
getServiceInfo: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ServiceInfo"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listSources

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1529](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1529).

```typescript
listSources: { parameters: { query?: { kind?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["source.schema"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.createSource

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1559](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1559).

```typescript
createSource: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["source.schema"]; }; }; responses: { 201: { headers: { Location: components["headers"]["Location"]; ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["source.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getSource

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1598](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1598).

```typescript
getSource: { parameters: { query?: never; header?: never; path: { source_id: components["parameters"]["SourceId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["source.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.replaceSource

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1623](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1623).

```typescript
replaceSource: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { source_id: components["parameters"]["SourceId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["source.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["source.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.deleteSource

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1660](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1660).

```typescript
deleteSource: { parameters: { query?: never; header?: never; path: { source_id: components["parameters"]["SourceId"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listTasks

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1683](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1683).

```typescript
listTasks: { parameters: { query?: { source_id?: string; package_id?: components["schemas"]["Slug"]; package_version?: components["schemas"]["SemVer"]; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["TaskSummary"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.createTask

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1716](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1716).

```typescript
createTask: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["task-config.schema"]; }; }; responses: { 201: { headers: { Location: components["headers"]["Location"]; ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["task-config.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getTask

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1755](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1755).

```typescript
getTask: { parameters: { query?: never; header?: never; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["task-config.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.replaceTask

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1780](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1780).

```typescript
replaceTask: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["task-config.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["task-config.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.deleteTask

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1817](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1817).

```typescript
deleteTask: { parameters: { query?: never; header?: never; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.validateTask

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1840](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1840).

```typescript
validateTask: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["task-config.schema"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["TaskValidation"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.startRun

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1865](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1865).

```typescript
startRun: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { task_id: components["parameters"]["TaskId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["RunRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 409: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listStageActivations

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1905](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1905).

```typescript
listStageActivations: { parameters: { query?: { cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path: { task_id: components["parameters"]["TaskId"]; stage_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["Activation"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.activateStageVersion

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1938](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1938).

```typescript
activateStageVersion: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path: { task_id: components["parameters"]["TaskId"]; stage_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["ActivationRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Activation"]; }; }; 401: components["responses"]["Unauthenticated"]; 403: { headers: { [name: string]: unknown; }; content: { "application/problem+json": components["schemas"]["problem.schema"]; }; }; 404: components["responses"]["NotFound"]; 409: components["responses"]["Conflict"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listRuns

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:1988](../../../../../../web/admin/src/api/generated/orchestrator.ts#L1988).

```typescript
listRuns: { parameters: { query?: { task_id?: string; status?: components["schemas"]["JobStatus"]; since?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["Run"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getRun

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2020](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2020).

```typescript
getRun: { parameters: { query?: never; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["Run"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.cancelRun

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2044](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2044).

```typescript
cancelRun: { parameters: { query?: never; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listRunItems

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2081](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2081).

```typescript
listRunItems: { parameters: { query?: { stage_id?: string; status?: components["schemas"]["ItemStatus"]; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path: { run_id: components["parameters"]["RunId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["StageItem"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getMaterialTrace

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2115](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2115).

```typescript
getMaterialTrace: { parameters: { query?: never; header?: never; path: { material_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["MaterialTrace"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listUnknownMaterials

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2139](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2139).

```typescript
listUnknownMaterials: { parameters: { query?: { source_id?: string; forwarded?: boolean; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["UnknownMaterial"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listProblemGroups

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2170](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2170).

```typescript
listProblemGroups: { parameters: { query?: { source_id?: string; status?: components["schemas"]["ProblemGroupStatus"]; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["ProblemGroup"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.updateProblemGroup

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2201](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2201).

```typescript
updateProblemGroup: { parameters: { query?: never; header?: never; path: { group_id: components["schemas"]["Id"]; }; cookie?: never; }; requestBody: { content: { "application/merge-patch+json": { status?: components["schemas"]["ProblemGroupStatus"]; assistant_job_id?: components["schemas"]["Id"]; note?: string; }; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["ProblemGroup"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.startReprocessing

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2234](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2234).

```typescript
startReprocessing: { parameters: { query?: never; header: { "Idempotency-Key": components["parameters"]["IdempotencyKey"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["ReprocessRequest"]; }; }; responses: { 202: components["responses"]["JobAccepted"]; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listPlatformConnections

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2263](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2263).

```typescript
listPlatformConnections: { parameters: { query?: { kind?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["PlatformConnection"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getPlatformConnection

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2293](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2293).

```typescript
getPlatformConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["PlatformConnection"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.putPlatformConnection

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2318](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2318).

```typescript
putPlatformConnection: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path: { connection_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["connection.schema"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["PlatformConnection"]; }; }; 401: components["responses"]["Unauthenticated"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.deletePlatformConnection

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2354](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2354).

```typescript
deletePlatformConnection: { parameters: { query?: never; header?: never; path: { connection_id: components["schemas"]["Slug"]; }; cookie?: never; }; requestBody?: never; responses: { 204: { headers: { [name: string]: unknown; }; content?: never; }; 401: components["responses"]["Unauthenticated"]; 409: components["responses"]["Conflict"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getPlatformLimits

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2376](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2376).

```typescript
getPlatformLimits: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["PlatformLimits"]; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.putPlatformLimits

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2398](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2398).

```typescript
putPlatformLimits: { parameters: { query?: never; header?: { "If-Match"?: components["parameters"]["IfMatch"]; }; path?: never; cookie?: never; }; requestBody: { content: { "application/json": components["schemas"]["PlatformLimits"]; }; }; responses: { 200: { headers: { ETag: components["headers"]["ETag"]; [name: string]: unknown; }; content: { "application/json": components["schemas"]["PlatformLimits"]; }; }; 401: components["responses"]["Unauthenticated"]; 403: components["responses"]["Forbidden"]; 412: components["responses"]["PreconditionFailed"]; 422: components["responses"]["UnprocessableEntity"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getEffectiveLimits

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2433](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2433).

```typescript
getEffectiveLimits: { parameters: { query?: { source_id?: string; task_id?: string; stage_id?: string; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["EffectiveLimits"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listExecutors

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2459](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2459).

```typescript
listExecutors: { parameters: { query?: never; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["Executor"][]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.listAuditEvents

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2482](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2482).

```typescript
listAuditEvents: { parameters: { query?: { subject_type?: "source" | "task" | "stage" | "connection" | "limits" | "problem_group"; subject_id?: string; cursor?: components["parameters"]["Cursor"]; limit?: components["parameters"]["Limit"]; }; header?: never; path?: never; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": { items: components["schemas"]["AuditEvent"][]; next_cursor: components["schemas"]["NextCursor"]; }; }; }; 401: components["responses"]["Unauthenticated"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.getJob

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2513](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2513).

```typescript
getJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: never; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.

## admin.api.generated.orchestrator.operations.cancelJob

**Поле.** Код: [web/admin/src/api/generated/orchestrator.ts:2537](../../../../../../web/admin/src/api/generated/orchestrator.ts#L2537).

```typescript
cancelJob: { parameters: { query?: never; header?: never; path: { job_id: components["parameters"]["JobId"]; }; cookie?: never; }; requestBody?: { content: { "application/json": components["schemas"]["JobCancelRequest"]; }; }; responses: { 200: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 202: { headers: { [name: string]: unknown; }; content: { "application/json": components["schemas"]["job.schema"]; }; }; 401: components["responses"]["Unauthenticated"]; 404: components["responses"]["NotFound"]; }; }
```

Доступ: читання — так; запис — так.
