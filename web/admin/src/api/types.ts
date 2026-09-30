// Convenience aliases over the generated contract types (src/api/generated/*). No hand-written shapes here:
// every alias points at a request/response of a contract operation.
import type { paths as Orch } from "./generated/orchestrator";
import type { paths as Reg } from "./generated/registry";
import type { paths as Sto } from "./generated/storage";
import type { paths as Llm } from "./generated/llm";
import type { paths as Hdl } from "./generated/handler";
import type { paths as Asst, components as AsstComponents } from "./generated/assistant";
import type { paths as Col } from "./generated/collector";

type Json<T> = T extends { content: { "application/json": infer B } } ? B : never;
type Ok<Op> = Op extends { responses: infer R }
  ? R extends { 200: infer X }
    ? Json<X>
    : R extends { 201: infer X }
      ? Json<X>
      : R extends { 202: infer X }
        ? Json<X>
        : never
  : never;
type Body<Op> = Op extends { requestBody?: infer B } ? Json<NonNullable<B>> : never;
type ItemOf<T> = T extends { items: Array<infer I> } ? I : never;

// orchestrator.v1
export type Source = Ok<Orch["/v1/sources/{source_id}"]["get"]>;
export type TaskConfig = Ok<Orch["/v1/tasks/{task_id}"]["get"]>;
export type TaskSummary = ItemOf<Ok<Orch["/v1/tasks"]["get"]>>;
export type Stage = TaskConfig["stages"][number];
export type Schedule = NonNullable<TaskConfig["schedule"]>;
export type TaskValidation = Ok<Orch["/v1/task-validations"]["post"]>;
export type RunRequest = Body<Orch["/v1/tasks/{task_id}/runs"]["post"]>;
export type Run = Ok<Orch["/v1/runs/{run_id}"]["get"]>;
export type StageItem = ItemOf<Ok<Orch["/v1/runs/{run_id}/items"]["get"]>>;
export type MaterialTrace = Ok<Orch["/v1/materials/{material_id}/trace"]["get"]>;
export type UnknownMaterial = ItemOf<Ok<Orch["/v1/unknown-materials"]["get"]>>;
export type ProblemGroup = ItemOf<Ok<Orch["/v1/problem-groups"]["get"]>>;
export type ProblemGroupStatus = ProblemGroup["status"];
export type ReprocessRequest = Body<Orch["/v1/reprocessing"]["post"]>;
export type PlatformConnection = Ok<Orch["/v1/connections/{connection_id}"]["get"]>;
export type Connection = PlatformConnection["connection"];
export type PlatformLimits = Ok<Orch["/v1/limits/platform"]["get"]>;
export type Limits = NonNullable<PlatformLimits["hard_caps"]>;
export type EffectiveLimits = Ok<Orch["/v1/limits/effective"]["get"]>;
export type Executor = ItemOf<Ok<Orch["/v1/executors"]["get"]>>;
export type AuditEvent = ItemOf<Ok<Orch["/v1/audit-events"]["get"]>>;
export type Activation = Ok<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
export type ActivationRequest = Body<Orch["/v1/tasks/{task_id}/stages/{stage_id}/activations"]["post"]>;
export type Job = Ok<Orch["/v1/jobs/{job_id}"]["get"]>;
export type JobStatus = Job["status"];
export type PackageRef = NonNullable<Source["collector_rules"]>;

// registry.v1
export type Package = Ok<Reg["/v1/packages/{package_id}"]["get"]>;
export type PackageVersion = Ok<Reg["/v1/packages/{package_id}/versions/{version}"]["get"]>;
export type PackageManifest = NonNullable<PackageVersion["manifest"]>;
export type PublishRequest = Extract<
  NonNullable<Reg["/v1/packages/{package_id}/versions"]["post"]["requestBody"]>["content"],
  { "application/json": unknown }
>["application/json"];
export type PackageDiff = Ok<Reg["/v1/packages/{package_id}/diff"]["get"]>;
export type UpstreamStatus = Ok<Reg["/v1/packages/{package_id}/upstream"]["get"]>;
export type ForkRequest = Body<Reg["/v1/packages/{package_id}/forks"]["post"]>;
export type StatusChange = Body<Reg["/v1/packages/{package_id}/versions/{version}/status"]["post"]>;
export type HandlerKind = Package["kind"];
export type VersionStatus = PackageVersion["status"];
export type TestResultsRecord = NonNullable<PackageVersion["test_reports"]>[number];
export type TestReport = TestResultsRecord["report"];

// storage.v1
export type StoredObject = ItemOf<Ok<Sto["/v1/objects"]["get"]>>;
export type StoredObjectDetail = Ok<Sto["/v1/objects/{object_id}"]["get"]>;
export type EntityState = ItemOf<Ok<Sto["/v1/entities"]["get"]>>;
export type EntityHistoryEntry = ItemOf<Ok<Sto["/v1/entity-history"]["get"]>>;

// llm.v1
export type Provider = Ok<Llm["/v1/providers/{provider_id}"]["get"]>;
export type ModelAlias = ItemOf<Ok<Llm["/v1/model-aliases"]["get"]>>;
export type BudgetDefinition = ItemOf<Ok<Llm["/v1/budgets"]["get"]>>;
export type UsageReport = Ok<Llm["/v1/usage"]["get"]>;
export type Money = NonNullable<Run["costs"]>["llm"];

// handler.v1
export type TestRunRequest = Body<Hdl["/v1/test-runs"]["post"]>;
export type ConnectionTestResult = Ok<Hdl["/v1/connections/{connection_id}/test"]["post"]>;

// assistant.v1
export type OnboardingRequest = Body<Asst["/v1/onboarding-sessions"]["post"]>;
export type OnboardingSession = Ok<Asst["/v1/onboarding-sessions/{session_id}"]["get"]>;
export type Proposal = NonNullable<OnboardingSession["proposals"]>[number];
export type ImprovementRequest = Body<Asst["/v1/improvement-runs"]["post"]>;
// Job.result shapes documented in assistant.v1 components.
export type ImprovementResult = AsstComponents["schemas"]["ImprovementResult"];
export type AcceptanceResult = AsstComponents["schemas"]["AcceptanceResult"];

// collector.v1
export type CollectionErrors = Ok<Col["/v1/collections/{collection_id}/errors"]["get"]>;
