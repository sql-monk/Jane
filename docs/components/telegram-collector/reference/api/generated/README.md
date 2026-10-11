# HTTP API — telegram-collector

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `POST` | `/v1/collections` | [startCollection](startCollection.md) |
| `GET` | `/v1/collections/{collection_id}` | [getCollection](getCollection.md) |
| `GET` | `/v1/collections/{collection_id}/errors` | [listCollectionErrors](listCollectionErrors.md) |
| `GET` | `/v1/collections/{collection_id}/materials` | [listCollectionMaterials](listCollectionMaterials.md) |
| `GET` | `/v1/connections` | [listConnections](listConnections.md) |
| `DELETE` | `/v1/connections/{connection_id}` | [deleteConnection](deleteConnection.md) |
| `GET` | `/v1/connections/{connection_id}` | [getConnection](getConnection.md) |
| `PUT` | `/v1/connections/{connection_id}` | [putConnection](putConnection.md) |
| `POST` | `/v1/connections/{connection_id}/test` | [testConnection](testConnection.md) |
| `POST` | `/v1/fetches` | [fetchMaterial](fetchMaterial.md) |
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `POST` | `/v1/rules/validations` | [validateRules](validateRules.md) |
| `DELETE` | `/v1/states/{state_key}` | [resetCollectorState](resetCollectorState.md) |
| `GET` | `/v1/states/{state_key}` | [getCollectorState](getCollectorState.md) |
