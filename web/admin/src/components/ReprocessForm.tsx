// Re-processing of stored RAW materials by task stages (orchestrator POST /v1/reprocessing -> 202 Job).
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import type { Job, ReprocessRequest } from "../api/types";
import { ErrorBox, Field } from "./ui";

export function ReprocessForm({
  taskId = "",
  storageConnectionId = "",
  materialIds,
}: {
  taskId?: string;
  storageConnectionId?: string;
  materialIds?: string[];
}) {
  const api = useApi();
  const navigate = useNavigate();
  const [task, setTask] = useState(taskId);
  const [connection, setConnection] = useState(storageConnectionId);
  const [fromStage, setFromStage] = useState("");
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const [testMode, setTestMode] = useState(false);
  const [reason, setReason] = useState("");

  const start = useMutation({
    mutationFn: (body: ReprocessRequest) =>
      unwrap(
        api.orchestrator.POST("/v1/reprocessing", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body,
        }),
      ) as Promise<Job>,
    onSuccess: (job) => navigate(`/runs/${encodeURIComponent(job.job_id)}`),
  });

  const submit = () => {
    const stored: ReprocessRequest["stored_materials"] = {};
    if (connection) stored.storage_connection_id = connection;
    if (since) stored.since = since;
    if (until) stored.until = until;
    if (materialIds?.length) stored.material_ids = materialIds;
    start.mutate({
      task_id: task,
      stored_materials: stored,
      ...(fromStage ? { from_stage: fromStage } : {}),
      ...(testMode ? { test_mode: true } : {}),
      ...(reason ? { reason } : {}),
    });
  };

  return (
    <form
      className="form"
      aria-label="Повторна обробка"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <div className="grid-3">
        <Field label="Завдання">
          <input value={task} onChange={(e) => setTask(e.target.value)} required />
        </Field>
        <Field label="Сховище RAW (connection_id)">
          <input value={connection} onChange={(e) => setConnection(e.target.value)} />
        </Field>
        <Field label="Почати з етапу">
          <input
            value={fromStage}
            onChange={(e) => setFromStage(e.target.value)}
            placeholder="extract-products"
          />
        </Field>
        {materialIds?.length ? (
          <p>
            Матеріали: <code>{materialIds.join(", ")}</code>
          </p>
        ) : (
          <>
            <Field label="Збережені з (RFC 3339)">
              <input
                value={since}
                onChange={(e) => setSince(e.target.value)}
                placeholder="2026-09-20T00:00:00Z"
              />
            </Field>
            <Field label="Збережені до (RFC 3339)">
              <input value={until} onChange={(e) => setUntil(e.target.value)} />
            </Field>
          </>
        )}
        <Field label="Причина">
          <input value={reason} onChange={(e) => setReason(e.target.value)} />
        </Field>
        <label className="checkbox">
          <input type="checkbox" checked={testMode} onChange={(e) => setTestMode(e.target.checked)} />
          Тестовий режим (без запису в робочі дані)
        </label>
      </div>
      <button type="submit" className="btn btn-primary" disabled={!task || start.isPending}>
        Обробити повторно
      </button>
      <ErrorBox error={start.error} title="Не вдалося запустити повторну обробку" />
    </form>
  );
}
