// Activation and rollback of package versions in task stages, with audit (orchestrator activations API).
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import type { Activation, ActivationRequest, Stage, TaskConfig } from "../api/types";
import { formatDate, refLabel } from "../lib/format";
import { ErrorBox, Field, Notice, ReasonAction, Section, Table } from "./ui";

export function StageVersions({ task }: { task: TaskConfig }) {
  const stages = task.stages.filter((s) => s.kind === "handler" && s.handler);
  return (
    <>
      <Notice>
        Активувати можна лише погоджену (approved) версію. Відкат повертає попередню активацію. Кожна дія
        потрапляє в журнал аудиту.
      </Notice>
      {stages.map((stage) => (
        <StageVersionCard key={stage.stage_id} taskId={task.task_id} stage={stage} />
      ))}
    </>
  );
}

function StageVersionCard({ taskId, stage }: { taskId: string; stage: Stage }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const handler = stage.handler;
  const packageId = handler?.package_id ?? "";
  const [version, setVersion] = useState("");
  const [last, setLast] = useState<Activation | null>(null);

  const history = useQuery({
    queryKey: ["activations", taskId, stage.stage_id],
    queryFn: () =>
      unwrap(
        api.orchestrator.GET("/v1/tasks/{task_id}/stages/{stage_id}/activations", {
          params: { path: { task_id: taskId, stage_id: stage.stage_id } },
        }),
      ),
  });
  const versions = useQuery({
    queryKey: ["package-versions", packageId, "approved"],
    enabled: Boolean(packageId),
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions", {
          params: { path: { package_id: packageId }, query: { status: "approved" } },
        }),
      ),
  });

  const activate = useMutation({
    mutationFn: (body: ActivationRequest) =>
      unwrap(
        api.orchestrator.POST("/v1/tasks/{task_id}/stages/{stage_id}/activations", {
          params: {
            path: { task_id: taskId, stage_id: stage.stage_id },
            header: { "Idempotency-Key": newIdempotencyKey() },
          },
          body,
        }),
      ),
    onSuccess: (activation) => {
      setLast(activation);
      void queryClient.invalidateQueries({ queryKey: ["activations", taskId, stage.stage_id] });
      void queryClient.invalidateQueries({ queryKey: ["task", taskId] });
    },
  });

  const approved = versions.data?.items ?? [];
  const selected = approved.find((v) => v.version === version);

  return (
    <Section
      title={`Етап ${stage.stage_id}`}
      actions={<Link to={`/tasks?package_id=${encodeURIComponent(packageId)}`}>Усі прив'язки пакета</Link>}
    >
      <p>
        Поточна версія: <strong data-testid={`current-${stage.stage_id}`}>{refLabel(handler)}</strong>{" "}
        <Link to={`/packages/${encodeURIComponent(packageId)}`}>пакет</Link>
      </p>
      <div className="inline-form">
        <Field label="Погоджена версія">
          <select
            aria-label={`Версія для ${stage.stage_id}`}
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          >
            <option value="">—</option>
            {approved.map((v) => (
              <option key={v.version} value={v.version}>
                {v.version} ({v.test_status})
              </option>
            ))}
          </select>
        </Field>
        <ReasonAction
          label="Активувати"
          confirmLabel="Активувати версію"
          busy={activate.isPending || !selected}
          onConfirm={(reason) =>
            selected &&
            activate.mutate({
              kind: "activate",
              package: {
                package_id: selected.package_id,
                version: selected.version,
                digest: selected.digest,
              },
              ...(reason ? { reason } : {}),
            })
          }
        />
        <ReasonAction
          label="Відкотити"
          confirmLabel="Відкотити до попередньої"
          danger
          busy={activate.isPending}
          onConfirm={(reason) => activate.mutate({ kind: "rollback", ...(reason ? { reason } : {}) })}
        />
      </div>
      <ErrorBox error={versions.error} />
      <ErrorBox error={activate.error} title="Активацію не виконано" />
      {last ? (
        <Notice tone="ok">
          {last.kind === "rollback" ? "Відкат" : "Активація"}: {refLabel(last.previous)} →{" "}
          <strong>{refLabel(last.package)}</strong>
        </Notice>
      ) : null}
      <ErrorBox error={history.error} />
      <Table
        label={`Історія активацій ${stage.stage_id}`}
        rows={history.data?.items ?? []}
        rowKey={(a) => a.activation_id}
        empty="Активацій ще не було"
        columns={[
          { header: "Коли", cell: (a) => formatDate(a.activated_at) },
          { header: "Тип", cell: (a) => a.kind },
          { header: "Версія", cell: (a) => refLabel(a.package) },
          { header: "Попередня", cell: (a) => refLabel(a.previous) },
          { header: "Хто", cell: (a) => a.activated_by ?? "—" },
          { header: "Причина", cell: (a) => a.reason ?? "—" },
        ]}
      />
    </Section>
  );
}
