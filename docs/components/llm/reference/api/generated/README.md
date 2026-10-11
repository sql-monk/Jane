# HTTP API — llm

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/budgets` | [listBudgets](listBudgets.md) |
| `DELETE` | `/v1/budgets/{scope_type}/{scope_id}` | [deleteBudget](deleteBudget.md) |
| `PUT` | `/v1/budgets/{scope_type}/{scope_id}` | [putBudget](putBudget.md) |
| `POST` | `/v1/completions` | [createCompletion](createCompletion.md) |
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `GET` | `/v1/model-aliases` | [listModelAliases](listModelAliases.md) |
| `PUT` | `/v1/model-aliases/{alias}` | [putModelAlias](putModelAlias.md) |
| `GET` | `/v1/providers` | [listProviders](listProviders.md) |
| `DELETE` | `/v1/providers/{provider_id}` | [deleteProvider](deleteProvider.md) |
| `GET` | `/v1/providers/{provider_id}` | [getProvider](getProvider.md) |
| `PUT` | `/v1/providers/{provider_id}` | [putProvider](putProvider.md) |
| `GET` | `/v1/usage` | [getUsage](getUsage.md) |
