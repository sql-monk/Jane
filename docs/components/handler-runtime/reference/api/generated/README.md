# HTTP API — handler-runtime

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/connections` | [listConnections](listConnections.md) |
| `DELETE` | `/v1/connections/{connection_id}` | [deleteConnection](deleteConnection.md) |
| `GET` | `/v1/connections/{connection_id}` | [getConnection](getConnection.md) |
| `PUT` | `/v1/connections/{connection_id}` | [putConnection](putConnection.md) |
| `POST` | `/v1/connections/{connection_id}/test` | [testConnection](testConnection.md) |
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `POST` | `/v1/invocations` | [invokeHandler](invokeHandler.md) |
| `GET` | `/v1/invocations/{invocation_id}` | [getInvocation](getInvocation.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `POST` | `/v1/test-runs` | [startTestRun](startTestRun.md) |
