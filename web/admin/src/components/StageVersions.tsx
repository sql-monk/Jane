// Activation and rollback of package versions in task stages, with audit (orchestrator activations API).
// Handler stages switch `stages[].handler`; collect stages switch the collector rules (`stages[].collector.rules`,
// a `collector-rules` package) - the stage's own rules or, when it has none, `Source.collector_rules`.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import type { Activation, ActivationRequest, PackageRef, Stage, TaskConfig } from "../api/types";
import { formatDate, refLabel } from "../lib/format";
import { ErrorBox, Field, Notice, ReasonAction, Section, Table } from "./ui";

export function StageVersions({ task }: { task: TaskConfig }) {
  const api = useApi();
  const stages = task.stages.filter((s) => (s.kind === "handler" && s.handler) || s.kind === "collect");
  const sourceId = task.input.source_id;
  // A collect stage without its own rules uses the rules of the task's source.
  const needsSource = stages.some((s) => s.kind === "collect" && !s.collector?.rules);
  const source = useQuery({
    queryKey: ["source", sourceId],
    enabled: needsSource && Boolean(sourceId),
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/sources/{source_id}", { params: { path: { source_id: sourceId } } })),
  });
  return (
    <>
      <Notice>
        Активувати можна лише погоджену (approved) версію. Відкат повертає попередню активацію. Кожна дія
        потрапляє в журнал аудиту. Для етапу збору (collect) активується версія правил колектора.
      </Notice>
      <ErrorBox error={source.error} title="Правила джерела недоступні" />
      {stages.map((stage) =>
        stage.kind === "collect" ? (
          <StageVersionCard
            key={stage.stage_id}
            taskId={task.task_id}
            stage={stage}
            current={stage.collector?.rules ?? source.data?.collector_rules}
            inherited={!stage.collector?.rules}
          />
        ) : (
          <StageVersionCard
            key={stage.stage_id}
            taskId={task.task_id}
            stage={stage}
            current={stage.handler}
          />
        ),
      )}
    </>
  );
}

function StageVersionCard({
  taskId,
  stage,
  current,
  inherited = false,
}: {
  taskId: string;
  stage: Stage;
  current: PackageRef | undefined;
  inherited?: boolean;
}) {
  const api = useApi();
  const queryClient = useQueryClient();
  const isCollect = stage.kind === "collect";
  const currentPackage = current?.package_id ?? "";
  // The stage may be switched to an independent fork of its package (ТЗ §7, §10): pick the package, then its version.
  const [picked, setPicked] = useState<string | null>(null);
  const packageId = picked ?? currentPackage;
  const [version, setVersion] = useState("");
  const [last, setLast] = useState<Activation | null>(null);

  const forks = useQuery({
    queryKey: ["packages", "forks", currentPackage],
    enabled: Boolean(currentPackage),
    queryFn: () =>
      unwrap(api.registry.GET("/v1/packages", { params: { query: { fork_of: currentPackage } } })),
  });
  const candidates = [
    ...new Set([currentPackage, ...(forks.data?.items ?? []).map((p) => p.package_id)].filter(Boolean)),
  ];

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
      actions={
        currentPackage && !isCollect ? (
          <Link to={`/tasks?package_id=${encodeURIComponent(currentPackage)}`}>Усі прив'язки пакета</Link>
        ) : null
      }
    >
      <p>
        {isCollect ? "Поточні правила колектора" : "Поточна версія"}:{" "}
        <strong data-testid={`current-${stage.stage_id}`}>{refLabel(current)}</strong>{" "}
        {isCollect && inherited && current ? <span className="muted">(правила джерела) </span> : null}
        {currentPackage ? <Link to={`/packages/${encodeURIComponent(currentPackage)}`}>пакет</Link> : null}
      </p>
      {isCollect && !current ? (
        <p className="muted">Правила ще не прив'язано: оберіть пакет правил колектора (collector-rules).</p>
      ) : null}
      <div className="inline-form">
        <Field label={isCollect ? "Пакет правил (поточний або його форк)" : "Пакет (поточний або його форк)"}>
          {isCollect && !currentPackage ? (
            <input
              aria-label={`Пакет для ${stage.stage_id}`}
              value={packageId}
              onChange={(e) => {
                setPicked(e.target.value.trim());
                setVersion("");
              }}
              placeholder="package_id (collector-rules)"
            />
          ) : (
            <select
              aria-label={`Пакет для ${stage.stage_id}`}
              value={packageId}
              onChange={(e) => {
                setPicked(e.target.value);
                setVersion("");
              }}
            >
              {candidates.map((id) => (
                <option key={id} value={id}>
                  {id === currentPackage ? `${id} (поточний)` : `${id} (форк)`}
                </option>
              ))}
            </select>
          )}
        </Field>
        <Field label="Погоджена версія">
          <select
            aria-label={`Версія для ${stage.stage_id}`}
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          >
            <option value="">—</option>
            {approved.map((v) => (
              <option key={v.version} value={v.version}>
                {v.version} ({v.test_summary?.status ?? v.test_status})
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
                package_id: packageId,
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
