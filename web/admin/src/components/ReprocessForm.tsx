// Re-processing of stored RAW materials by task stages (orchestrator POST /v1/reprocessing -> 202 Job).
// `stored_materials` (task-config.schema.json TaskInput): `material_ids` takes every stored observation of these
// materials in the since/until window; the exact choice is `object_ids` (these stored RAW) or `observation_ids`.
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import type { Job, ReprocessRequest } from "../api/types";
import { ErrorBox, Field, Notice } from "./ui";
import { ConnectionPicker } from "./ConnectionPicker";
import { useCursorList } from "../api/hooks";

/** One stored RAW object (storage.v1 StoredObject) the user picked, e.g. a row of the materials page. */
export interface StoredSelection {
  object_id: string;
  material_id?: string | undefined;
  observation_id?: string | undefined;
}

type SelectionMode = "material" | "object" | "observation";

const MODE_LABELS: Record<SelectionMode, string> = {
  material: "усі збережені спостереження матеріалу (material_ids)",
  object: "лише цей збережений RAW (object_ids)",
  observation: "лише це спостереження матеріалу (observation_ids)",
};

function idList(text: string): string[] {
  return text
    .split(/[\s,]+/)
    .map((id) => id.trim())
    .filter(Boolean);
}

export function ReprocessForm({
  taskId = "",
  storageConnectionId = "",
  materialIds,
  objectIds,
  stored,
}: {
  taskId?: string;
  storageConnectionId?: string;
  /** Every stored observation of these materials. */
  materialIds?: string[];
  /** Exactly these stored RAW objects (e.g. the RAW of problem samples). */
  objectIds?: string[];
  /** A stored object: the user chooses the material, this RAW only or its observation only. */
  stored?: StoredSelection;
}) {
  const api = useApi();
  const navigate = useNavigate();
  const [task, setTask] = useState(taskId);
  const [taskSearch, setTaskSearch] = useState("");
  const [connection, setConnection] = useState(storageConnectionId);
  const [fromStage, setFromStage] = useState("");
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const [exactObjects, setExactObjects] = useState("");
  const [exactObservations, setExactObservations] = useState("");
  const [testMode, setTestMode] = useState(false);
  const [reason, setReason] = useState("");
  const modes: SelectionMode[] = stored
    ? [
        ...(stored.material_id ? (["material"] as const) : []),
        "object",
        ...(stored.material_id && stored.observation_id ? (["observation"] as const) : []),
      ]
    : [];
  // A row action selects exactly the RAW the user clicked. A wider scope is an explicit choice.
  const [mode, setMode] = useState<SelectionMode>("object");
  const [confirmAll, setConfirmAll] = useState(false);
  const tasks = useCursorList(["tasks", "reprocess-picker"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/tasks", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
  const selectedTask = useQuery({
    queryKey: ["task", task],
    enabled: Boolean(task),
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/tasks/{task_id}", { params: { path: { task_id: task } } })),
  });
  const stages = selectedTask.data?.stages.filter((stage) => stage.kind === "handler") ?? [];

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

  const fixed = Boolean(stored || materialIds?.length || objectIds?.length);
  const selectedCount = stored && mode === "object" ? 1 : objectIds?.length || idList(exactObjects).length;
  const broadSelection = Boolean(
    (stored && mode === "material") ||
    materialIds?.length ||
    (!fixed && !idList(exactObjects).length && !idList(exactObservations).length),
  );
  const datesValid = !since || !until || new Date(since) < new Date(until);
  const ready = Boolean(
    task && selectedTask.data && connection && datesValid && (!broadSelection || confirmAll),
  );

  const submit = () => {
    if (!ready) return;
    const selection: ReprocessRequest["stored_materials"] = {};
    if (connection) selection.storage_connection_id = connection;
    if (stored) {
      if (mode === "object") selection.object_ids = [stored.object_id];
      else if (stored.material_id) selection.material_ids = [stored.material_id];
      if (mode === "observation" && stored.observation_id)
        selection.observation_ids = [stored.observation_id];
    } else if (objectIds?.length) {
      selection.object_ids = objectIds;
    } else if (materialIds?.length) {
      selection.material_ids = materialIds;
    } else {
      if (since) selection.since = new Date(since).toISOString();
      if (until) selection.until = new Date(until).toISOString();
      if (idList(exactObjects).length) selection.object_ids = idList(exactObjects);
      if (idList(exactObservations).length) selection.observation_ids = idList(exactObservations);
    }
    start.mutate({
      task_id: task,
      stored_materials: selection,
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
        <Field label="Пошук завдання">
          <input
            aria-label="Пошук завдання"
            value={taskSearch}
            onChange={(e) => setTaskSearch(e.target.value)}
            placeholder="Пошук за назвою або ідентифікатором"
          />
        </Field>
        <Field label="Завдання" hint="Виберіть наявний ланцюжок для повторної обробки">
          <select
            value={task}
            onChange={(e) => {
              setTask(e.target.value);
              setFromStage("");
            }}
            required
          >
            <option value="">Оберіть завдання</option>
            {task && !tasks.items.some((item) => item.task_id === task) ? (
              <option value={task}>{task}</option>
            ) : null}
            {tasks.items
              .filter(
                (item) =>
                  item.task_id === task ||
                  `${item.title} ${item.task_id}`
                    .toLocaleLowerCase()
                    .includes(taskSearch.toLocaleLowerCase()),
              )
              .map((item) => (
                <option key={item.task_id} value={item.task_id}>
                  {item.title} ({item.task_id})
                </option>
              ))}
          </select>
          {tasks.hasMore ? (
            <button
              type="button"
              className="btn btn-small"
              onClick={tasks.loadMore}
              disabled={tasks.loadingMore}
            >
              Більше завдань
            </button>
          ) : null}
        </Field>
        <ConnectionPicker label="Сховище RAW" value={connection} onChange={setConnection} />
        <Field label="Почати з етапу">
          <select value={fromStage} onChange={(e) => setFromStage(e.target.value)}>
            <option value="">За ланцюжком завдання</option>
            {stages.map((stage) => (
              <option key={stage.stage_id} value={stage.stage_id}>
                {stage.stage_id}
              </option>
            ))}
          </select>
        </Field>
        {stored ? (
          <>
            <p>
              Об'єкт RAW: <code>{stored.object_id}</code>
              {stored.material_id ? (
                <>
                  , матеріал <code>{stored.material_id}</code>
                </>
              ) : null}
              {stored.observation_id ? (
                <>
                  , спостереження <code>{stored.observation_id}</code>
                </>
              ) : null}
            </p>
            <Field label="Що обробити">
              <select
                value={mode}
                onChange={(e) => {
                  setMode(e.target.value as SelectionMode);
                  setConfirmAll(false);
                }}
              >
                {modes.map((m) => (
                  <option key={m} value={m}>
                    {MODE_LABELS[m]}
                  </option>
                ))}
              </select>
            </Field>
          </>
        ) : objectIds?.length ? (
          <p>
            Збережені RAW (object_ids): <code>{objectIds.join(", ")}</code>
          </p>
        ) : materialIds?.length ? (
          <p>
            Матеріали: <code>{materialIds.join(", ")}</code>
          </p>
        ) : null}
        {!fixed ? (
          <>
            <Field label="Збережені з" hint="Час у часовій зоні вашого браузера">
              <input type="datetime-local" value={since} onChange={(e) => setSince(e.target.value)} />
            </Field>
            <Field label="Збережені до (не включно)">
              <input type="datetime-local" value={until} onChange={(e) => setUntil(e.target.value)} />
            </Field>
            <Field label="Точний вибір: RAW object_ids" hint="через кому або пробіл; необов'язково">
              <input value={exactObjects} onChange={(e) => setExactObjects(e.target.value)} />
            </Field>
            <Field label="Точний вибір: observation_ids" hint="через кому або пробіл; необов'язково">
              <input value={exactObservations} onChange={(e) => setExactObservations(e.target.value)} />
            </Field>
          </>
        ) : null}
        <Field label="Причина">
          <input value={reason} onChange={(e) => setReason(e.target.value)} />
        </Field>
        <label className="checkbox">
          <input type="checkbox" checked={testMode} onChange={(e) => setTestMode(e.target.checked)} />
          Тестовий режим (без запису в робочі дані)
        </label>
      </div>
      <Notice>
        {selectedCount
          ? `Точна вибірка: ${selectedCount} збережених RAW.`
          : stored && mode === "observation"
            ? "Одне спостереження вибраного матеріалу."
            : idList(exactObservations).length
              ? `Вибрано спостережень: ${idList(exactObservations).length}.`
              : "Широка вибірка: усі відповідні збережені спостереження. Кількість до виконання невідома."}
        {broadSelection ? " Один матеріал може мати багато збережених версій." : null}
        {testMode ? " Тестовий режим без запису результатів." : " Результати буде записано в робочі сховища."}
      </Notice>
      {broadSelection ? (
        <label className="checkbox">
          <input type="checkbox" checked={confirmAll} onChange={(e) => setConfirmAll(e.target.checked)} />
          Підтверджую обробку всієї цієї вибірки
        </label>
      ) : null}
      {!datesValid ? <p role="alert">Початок періоду має бути раніше його кінця.</p> : null}
      <ErrorBox error={tasks.error ?? selectedTask.error} title="Завдання недоступні" />
      <button type="submit" className="btn btn-primary" disabled={!ready || start.isPending}>
        Обробити повторно
      </button>
      <ErrorBox error={start.error} title="Не вдалося запустити повторну обробку" />
    </form>
  );
}
