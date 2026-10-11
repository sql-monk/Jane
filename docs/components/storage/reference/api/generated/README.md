# HTTP API — storage

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/connections` | [listConnections](listConnections.md) |
| `DELETE` | `/v1/connections/{connection_id}` | [deleteConnection](deleteConnection.md) |
| `GET` | `/v1/connections/{connection_id}` | [getConnection](getConnection.md) |
| `PUT` | `/v1/connections/{connection_id}` | [putConnection](putConnection.md) |
| `POST` | `/v1/connections/{connection_id}/test` | [testConnection](testConnection.md) |
| `GET` | `/v1/entities` | [listEntities](listEntities.md) |
| `GET` | `/v1/entity-history` | [listEntityHistory](listEntityHistory.md) |
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `GET` | `/v1/objects` | [listObjects](listObjects.md) |
| `GET` | `/v1/objects/{object_id}` | [getObject](getObject.md) |
| `GET` | `/v1/objects/{object_id}/content` | [getObjectContent](getObjectContent.md) |
| `GET` | `/v1/storage-status` | [getStorageStatus](getStorageStatus.md) |
| `POST` | `/v1/storage-status/checks` | [checkStorageStatus](checkStorageStatus.md) |
