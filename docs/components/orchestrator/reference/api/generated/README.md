# HTTP API — orchestrator

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/audit-events` | [listAuditEvents](listAuditEvents.md) |
| `GET` | `/v1/connections` | [listPlatformConnections](listPlatformConnections.md) |
| `DELETE` | `/v1/connections/{connection_id}` | [deletePlatformConnection](deletePlatformConnection.md) |
| `GET` | `/v1/connections/{connection_id}` | [getPlatformConnection](getPlatformConnection.md) |
| `PUT` | `/v1/connections/{connection_id}` | [putPlatformConnection](putPlatformConnection.md) |
| `GET` | `/v1/executors` | [listExecutors](listExecutors.md) |
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `GET` | `/v1/limits/effective` | [getEffectiveLimits](getEffectiveLimits.md) |
| `GET` | `/v1/limits/platform` | [getPlatformLimits](getPlatformLimits.md) |
| `PUT` | `/v1/limits/platform` | [putPlatformLimits](putPlatformLimits.md) |
| `GET` | `/v1/materials/{material_id}/trace` | [getMaterialTrace](getMaterialTrace.md) |
| `GET` | `/v1/problem-groups` | [listProblemGroups](listProblemGroups.md) |
| `PATCH` | `/v1/problem-groups/{group_id}` | [updateProblemGroup](updateProblemGroup.md) |
| `POST` | `/v1/reprocessing` | [startReprocessing](startReprocessing.md) |
| `GET` | `/v1/runs` | [listRuns](listRuns.md) |
| `GET` | `/v1/runs/{run_id}` | [getRun](getRun.md) |
| `POST` | `/v1/runs/{run_id}/cancel` | [cancelRun](cancelRun.md) |
| `GET` | `/v1/runs/{run_id}/items` | [listRunItems](listRunItems.md) |
| `GET` | `/v1/sources` | [listSources](listSources.md) |
| `POST` | `/v1/sources` | [createSource](createSource.md) |
| `DELETE` | `/v1/sources/{source_id}` | [deleteSource](deleteSource.md) |
| `GET` | `/v1/sources/{source_id}` | [getSource](getSource.md) |
| `PUT` | `/v1/sources/{source_id}` | [replaceSource](replaceSource.md) |
| `POST` | `/v1/task-validations` | [validateTask](validateTask.md) |
| `GET` | `/v1/tasks` | [listTasks](listTasks.md) |
| `POST` | `/v1/tasks` | [createTask](createTask.md) |
| `DELETE` | `/v1/tasks/{task_id}` | [deleteTask](deleteTask.md) |
| `GET` | `/v1/tasks/{task_id}` | [getTask](getTask.md) |
| `PUT` | `/v1/tasks/{task_id}` | [replaceTask](replaceTask.md) |
| `POST` | `/v1/tasks/{task_id}/runs` | [startRun](startRun.md) |
| `GET` | `/v1/tasks/{task_id}/stages/{stage_id}/activations` | [listStageActivations](listStageActivations.md) |
| `POST` | `/v1/tasks/{task_id}/stages/{stage_id}/activations` | [activateStageVersion](activateStageVersion.md) |
| `GET` | `/v1/unknown-materials` | [listUnknownMaterials](listUnknownMaterials.md) |
