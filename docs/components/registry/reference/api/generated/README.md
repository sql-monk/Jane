# HTTP API — registry

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `GET` | `/v1/packages` | [listPackages](listPackages.md) |
| `POST` | `/v1/packages` | [createPackage](createPackage.md) |
| `GET` | `/v1/packages/{package_id}` | [getPackage](getPackage.md) |
| `PATCH` | `/v1/packages/{package_id}` | [updatePackage](updatePackage.md) |
| `GET` | `/v1/packages/{package_id}/diff` | [diffPackage](diffPackage.md) |
| `POST` | `/v1/packages/{package_id}/forks` | [forkPackage](forkPackage.md) |
| `GET` | `/v1/packages/{package_id}/upstream` | [getUpstreamStatus](getUpstreamStatus.md) |
| `POST` | `/v1/packages/{package_id}/upstream-ports` | [portUpstreamChanges](portUpstreamChanges.md) |
| `GET` | `/v1/packages/{package_id}/versions` | [listPackageVersions](listPackageVersions.md) |
| `POST` | `/v1/packages/{package_id}/versions` | [publishPackageVersion](publishPackageVersion.md) |
| `GET` | `/v1/packages/{package_id}/versions/{version}` | [getPackageVersion](getPackageVersion.md) |
| `GET` | `/v1/packages/{package_id}/versions/{version}/archive` | [downloadPackageArchive](downloadPackageArchive.md) |
| `GET` | `/v1/packages/{package_id}/versions/{version}/file` | [getPackageFile](getPackageFile.md) |
| `POST` | `/v1/packages/{package_id}/versions/{version}/status` | [setPackageVersionStatus](setPackageVersionStatus.md) |
| `POST` | `/v1/packages/{package_id}/versions/{version}/test-results` | [recordTestResults](recordTestResults.md) |
