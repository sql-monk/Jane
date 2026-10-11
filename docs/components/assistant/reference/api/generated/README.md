# HTTP API — assistant

Усі операції чинного OpenAPI, включно зі спільними pathItems.

| Метод | Шлях | Операція |
|---|---|---|
| `GET` | `/v1/health` | [getHealth](getHealth.md) |
| `GET` | `/v1/improvement-runs` | [listImprovementRuns](listImprovementRuns.md) |
| `POST` | `/v1/improvement-runs` | [startImprovement](startImprovement.md) |
| `GET` | `/v1/info` | [getServiceInfo](getServiceInfo.md) |
| `GET` | `/v1/jobs/{job_id}` | [getJob](getJob.md) |
| `POST` | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) |
| `GET` | `/v1/onboarding-sessions` | [listOnboardingSessions](listOnboardingSessions.md) |
| `POST` | `/v1/onboarding-sessions` | [startOnboarding](startOnboarding.md) |
| `GET` | `/v1/onboarding-sessions/{session_id}` | [getOnboardingSession](getOnboardingSession.md) |
| `POST` | `/v1/onboarding-sessions/{session_id}/candidate-selection` | [selectCandidate](selectCandidate.md) |
| `POST` | `/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance` | [acceptProposal](acceptProposal.md) |
| `POST` | `/v1/unknown-materials` | [analyzeUnknownMaterial](analyzeUnknownMaterial.md) |
