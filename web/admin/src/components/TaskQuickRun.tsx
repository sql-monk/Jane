import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import { ActionDialog, ErrorBox, Field } from "./ui";
import { Icon } from "./Icon";

export function TaskQuickRun({ taskId }: { taskId: string }) {
  const api = useApi();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [testMode, setTestMode] = useState(true);
  const [reason, setReason] = useState("");
  const task = useQuery({
    queryKey: ["task", taskId],
    enabled: open,
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/tasks/{task_id}", { params: { path: { task_id: taskId } } })),
  });
  const start = useMutation({
    mutationFn: () =>
      unwrap(
        api.orchestrator.POST("/v1/tasks/{task_id}/runs", {
          params: { path: { task_id: taskId }, header: { "Idempotency-Key": newIdempotencyKey() } },
          body: { test_mode: testMode, ...(reason.trim() ? { reason: reason.trim() } : {}) },
        }),
      ),
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["runs"] });
      navigate(`/runs/${encodeURIComponent(job.job_id)}`);
    },
  });
  const trigger = (
    <button
      className="btn btn-small"
      type="button"
      aria-label={`Запустити ${taskId}`}
      onClick={() => {
        setTestMode(true);
        setReason("");
        setOpen(true);
      }}
    >
      <Icon name="runs" size={14} />
      Запустити
    </button>
  );
  if (!open) return trigger;
  return (
    <>
      {trigger}
      <ActionDialog
        title={`Запуск ${taskId}`}
        onClose={() => {
          if (!start.isPending) {
            setOpen(false);
            start.reset();
          }
        }}
      >
        <form
          className="quick-run"
          aria-label={`Запуск ${taskId}`}
          onSubmit={(event) => {
            event.preventDefault();
            if (!start.isPending) start.mutate();
          }}
        >
          {task.data ? (
            <p>
              Завдання: <strong>{task.data.title}</strong>. Джерело: {task.data.input?.source_id}. Етапів:{" "}
              {task.data.stages?.length ?? "Недоступно"}.
            </p>
          ) : null}
          <ErrorBox error={task.error} title="Налаштування завдання недоступні" />
          <Field label="Режим запуску">
            <select
              value={testMode ? "test" : "live"}
              onChange={(event) => setTestMode(event.target.value === "test")}
              disabled={start.isPending}
            >
              <option value="test">Тестовий — без запису в робочі дані</option>
              <option value="live">Робочий — зі збереженням результатів</option>
            </select>
          </Field>
          <Field label="Причина запуску">
            <input
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              maxLength={1000}
              disabled={start.isPending}
              placeholder="Необов’язково"
            />
          </Field>
          {!testMode ? (
            <p className="warn-inline">Етапи збереження запишуть результати в робочі сховища.</p>
          ) : null}
          <div className="button-row">
            <button className="btn btn-primary btn-small" type="submit" disabled={start.isPending}>
              {start.isPending ? "Запускаємо…" : "Підтвердити запуск"}
            </button>
            <button
              className="btn btn-small"
              type="button"
              disabled={start.isPending}
              onClick={() => {
                setOpen(false);
                start.reset();
              }}
            >
              Скасувати
            </button>
          </div>
          <ErrorBox error={start.error} title="Не вдалося запустити" />
        </form>
      </ActionDialog>
    </>
  );
}
