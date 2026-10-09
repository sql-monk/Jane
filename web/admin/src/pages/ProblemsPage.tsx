// Problem materials grouped by source and nature (ТЗ §9), including `unresolved`, and unknown materials (ТЗ §8).
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap, type ApiClients } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { ImprovementRequest, Job, ProblemGroup, ProblemGroupStatus } from "../api/types";
import { ConnectionPicker } from "../components/ConnectionPicker";
import { JobPanel } from "../components/JobPanel";
import { ImprovementResultView } from "../components/ImprovementResultView";
import {
  ErrorBox,
  Field,
  Loading,
  LoadMore,
  Notice,
  Page,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { formatDate, refLabel } from "../lib/format";

const GROUP_STATUSES: ProblemGroupStatus[] = ["open", "in_progress", "unresolved", "resolved", "ignored"];

type TabKey = "groups" | "unknown";

export function ProblemsPage() {
  const [params, setParams] = useSearchParams();
  const tab = (params.get("tab") as TabKey | null) ?? "groups";
  return (
    <Page title="Проблеми">
      <Tabs<TabKey>
        tabs={[
          ["groups", "Групи проблем"],
          ["unknown", "Невідомі матеріали"],
        ]}
        active={tab}
        onChange={(t) => setParams({ tab: t })}
      />
      {tab === "groups" ? <ProblemGroups /> : <UnknownMaterials />}
    </Page>
  );
}

function ProblemGroups() {
  const api = useApi();
  const [status, setStatus] = useState<ProblemGroupStatus | "">("");
  const [sourceId, setSourceId] = useState("");
  const [selected, setSelected] = useState<ProblemGroup | null>(null);
  const list = useCursorList(["problem-groups", status, sourceId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/problem-groups", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(status ? { status } : {}),
            ...(sourceId ? { source_id: sourceId } : {}),
          },
        },
      }),
    ),
  );
  return (
    <>
      <div className="filters">
        <Field label="Стан групи">
          <select value={status} onChange={(e) => setStatus(e.target.value as ProblemGroupStatus | "")}>
            <option value="">усі</option>
            {GROUP_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Джерело">
          <input value={sourceId} onChange={(e) => setSourceId(e.target.value)} />
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Групи проблем"
        rows={list.items}
        rowKey={(g) => g.group_id}
        columns={[
          { header: "Джерело", cell: (g) => g.source_id },
          { header: "Пакет", cell: (g) => refLabel(g.package) },
          { header: "Проблема", cell: (g) => <Status value={g.problem} /> },
          { header: "Сигнатура", cell: (g) => <code>{g.signature}</code> },
          { header: "Кількість", cell: (g) => g.count },
          { header: "Стан", cell: (g) => <Status value={g.status} /> },
          { header: "Остання", cell: (g) => formatDate(g.last_seen_at) },
          {
            header: "",
            cell: (g) => (
              <button type="button" className="btn btn-small" onClick={() => setSelected(g)}>
                Відкрити
              </button>
            ),
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      {selected ? (
        <ProblemGroupDetail key={selected.group_id} group={selected} onChanged={setSelected} />
      ) : null}
    </>
  );
}

function ProblemGroupDetail({
  group,
  onChanged,
}: {
  group: ProblemGroup;
  onChanged: (g: ProblemGroup) => void;
}) {
  const api = useApi();
  const queryClient = useQueryClient();
  const [storage, setStorage] = useState("");
  const [approval, setApproval] = useState<"manual" | "auto_after_checks">("manual");
  const [allowFork, setAllowFork] = useState(true);
  const [attempts, setAttempts] = useState("");
  const [jobId, setJobId] = useState<string | null>(group.assistant_job_id ?? null);

  const bindings = useQuery({
    queryKey: ["tasks", "bindings", group.package?.package_id],
    enabled: Boolean(group.package),
    queryFn: () =>
      unwrap(
        api.orchestrator.GET("/v1/tasks", {
          params: { query: { package_id: group.package?.package_id as string } },
        }),
      ),
  });

  const patch = useMutation({
    mutationFn: (body: { status?: ProblemGroupStatus; assistant_job_id?: string; note?: string }) =>
      unwrap(
        api.orchestrator.PATCH("/v1/problem-groups/{group_id}", {
          params: { path: { group_id: group.group_id } },
          headers: { "Content-Type": "application/merge-patch+json" },
          body,
        }),
      ),
    onSuccess: (updated) => {
      onChanged(updated);
      void queryClient.invalidateQueries({ queryKey: ["problem-groups"] });
    },
  });

  // A sample is usable when its stored RAW is known (stored_object_id) or can be found in the chosen storage
  // by material_id + observation_id (the orchestrator records only the material ids of a problem result).
  const samples = (group.samples ?? []).filter((s) => s.stored_object_id || s.material_id);
  const bindingList = (bindings.data?.items ?? []).flatMap((t) =>
    (t.package_stages ?? []).map((s) => ({ task_id: t.task_id, stage_id: s.stage_id })),
  );

  const improve = useMutation({
    mutationFn: async () => {
      if (!group.package) throw new Error("group has no package");
      const objectIds = await storedSampleObjects(api, storage, group.source_id, samples);
      if (objectIds.length === 0) throw new NoStoredSamples(storage);
      const body: ImprovementRequest = {
        package: group.package,
        source_id: group.source_id,
        problem_group_id: group.group_id,
        problem_samples: objectIds.map((objectId) => ({
          material_ref: { storage_connection_id: storage, object_id: objectId },
        })),
        ...(bindingList.length ? { bindings: bindingList } : {}),
        policy: { approval, allow_fork: allowFork },
        ...(attempts ? { limits: { max_improvement_attempts: Number.parseInt(attempts, 10) } } : {}),
      };
      const job = (await unwrap(
        api.assistant.POST("/v1/improvement-runs", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body,
        }),
      )) as Job;
      // Only link the job: the assistant moves the group itself (in_progress at the start, then unresolved /
      // resolved / in_progress at the end). A status here could overwrite its final status when the job is fast.
      await patch.mutateAsync({ assistant_job_id: job.job_id });
      return job;
    },
    onSuccess: (job) => setJobId(job.job_id),
  });

  return (
    <Section title={`Група ${group.group_id}`}>
      <p>
        <Status value={group.status} /> {group.problem}
        {group.failure_kind ? ` / ${group.failure_kind}` : ""}: <code>{group.signature}</code>, {group.count}{" "}
        матеріалів, пакет{" "}
        {group.package ? (
          <Link to={`/packages/${encodeURIComponent(group.package.package_id)}`}>
            {refLabel(group.package)}
          </Link>
        ) : (
          "—"
        )}
      </p>
      {group.status === "unresolved" ? (
        <Notice tone="warn">
          Автоматичне вдосконалення не впоралося в межах спроб і бюджету — потрібне рішення людини.
        </Notice>
      ) : null}
      <Table
        label="Приклади"
        rows={group.samples ?? []}
        rowKey={(s, i) => `${s.material_id ?? ""}-${i}`}
        columns={[
          {
            header: "Матеріал",
            cell: (s) =>
              s.material_id ? (
                <Link to={`/materials/${encodeURIComponent(s.material_id)}/trace`}>{s.material_id}</Link>
              ) : (
                "—"
              ),
          },
          { header: "Спостереження", cell: (s) => s.observation_id ?? "—" },
          { header: "Виклик", cell: (s) => s.invocation_id ?? "—" },
          { header: "Збережений об'єкт", cell: (s) => s.stored_object_id ?? "—" },
        ]}
      />
      <div className="button-row">
        <button
          type="button"
          className="btn"
          onClick={() => patch.mutate({ status: "ignored" })}
          disabled={patch.isPending}
        >
          Ігнорувати
        </button>
        <button
          type="button"
          className="btn"
          onClick={() => patch.mutate({ status: "resolved" })}
          disabled={patch.isPending}
        >
          Позначити вирішеною
        </button>
        <button
          type="button"
          className="btn"
          onClick={() => patch.mutate({ status: "open" })}
          disabled={patch.isPending}
        >
          Відкрити знову
        </button>
      </div>
      <ErrorBox error={patch.error} title="Не вдалося змінити групу" />
      <h3>Вдосконалити екстрактор через асистента</h3>
      <p className="muted">
        Нова версія перевіряється на нових і попередніх тестах на всіх прив'язках пакета ({bindingList.length}
        ) або оформлюється форком. Кількість спроб і витрати обмежені лімітами LLM.
      </p>
      <div className="grid-3">
        <ConnectionPicker label="Сховище RAW прикладів" value={storage} onChange={setStorage} />
        <Field label="Погодження">
          <select
            value={approval}
            onChange={(e) => setApproval(e.target.value as "manual" | "auto_after_checks")}
          >
            <option value="manual">ручне</option>
            <option value="auto_after_checks">автоматично після перевірок</option>
          </select>
        </Field>
        <Field label="Макс. спроб (необов'язково)">
          <input type="number" min={0} value={attempts} onChange={(e) => setAttempts(e.target.value)} />
        </Field>
        <label className="checkbox">
          <input type="checkbox" checked={allowFork} onChange={(e) => setAllowFork(e.target.checked)} />
          Дозволити форк
        </label>
      </div>
      <button
        type="button"
        className="btn btn-primary"
        disabled={!group.package || !storage || samples.length === 0 || improve.isPending}
        onClick={() => improve.mutate()}
      >
        Запустити вдосконалення
      </button>
      {samples.length === 0 ? (
        <p className="muted">У групи немає прикладів (material_id або stored_object_id).</p>
      ) : (
        <p className="muted">
          Збережений RAW прикладу береться з обраного сховища: за stored_object_id або за material_id і
          observation_id прикладу.
        </p>
      )}
      {improve.error instanceof NoStoredSamples ? (
        <Notice tone="warn">
          RAW прикладу недоступний у сховищі <code>{improve.error.connection}</code>: потрібен збережений
          object_id або рівно один RAW із observation_id прикладу.
        </Notice>
      ) : (
        <ErrorBox error={improve.error} title="Не вдалося запустити вдосконалення" />
      )}
      {jobId ? (
        <JobPanel
          service="assistant"
          client={api.assistant}
          jobId={jobId}
          title="Вдосконалення"
          renderResult={(result) => <ImprovementResultView result={result} />}
        />
      ) : null}
    </Section>
  );
}

type ProblemSample = NonNullable<ProblemGroup["samples"]>[number];

/** None of the problem samples has stored RAW in the chosen storage connection. */
class NoStoredSamples extends Error {
  constructor(readonly connection: string) {
    super(`no stored RAW of the problem samples in ${connection}`);
  }
}

/**
 * Object ids of the stored RAW of problem samples, in sample order. `stored_object_id` is used as is;
 * otherwise the RAW of the sample's observation is looked up in the storage connection by `material_id`
 * (storage.v1 listObjects). Missing observation ids and ambiguous RAW are skipped.
 */
async function storedSampleObjects(
  api: ApiClients,
  connectionId: string,
  sourceId: string,
  samples: ProblemSample[],
): Promise<string[]> {
  const ids: string[] = [];
  for (const sample of samples) {
    if (sample.stored_object_id) {
      ids.push(sample.stored_object_id);
      continue;
    }
    if (!sample.material_id || !sample.observation_id) continue;
    const matches = new Set<string>();
    let cursor: string | null = null;
    do {
      const page: Awaited<ReturnType<typeof listStored>> = await listStored(
        api,
        connectionId,
        sourceId,
        sample.material_id,
        cursor,
      );
      for (const object of page.items) {
        if (object.material?.observation_id === sample.observation_id) {
          matches.add(object.object.object_id);
        }
      }
      if (matches.size > 1) break;
      cursor = page.next_cursor ?? null;
    } while (cursor);
    if (matches.size === 1) ids.push(...matches);
  }
  return [...new Set(ids)];
}

function listStored(
  api: ApiClients,
  connectionId: string,
  sourceId: string,
  materialId: string,
  cursor: string | null,
) {
  return unwrap(
    api.storage.GET("/v1/objects", {
      params: {
        query: {
          connection_id: connectionId,
          source_id: sourceId,
          material_id: materialId,
          ...(cursor ? { cursor } : {}),
        },
      },
    }),
  );
}

function UnknownMaterials() {
  const api = useApi();
  const [forwarded, setForwarded] = useState<"" | "true" | "false">("");
  const [sourceId, setSourceId] = useState("");
  const list = useCursorList(["unknown-materials", forwarded, sourceId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/unknown-materials", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(forwarded ? { forwarded: forwarded === "true" } : {}),
            ...(sourceId ? { source_id: sourceId } : {}),
          },
        },
      }),
    ),
  );
  return (
    <>
      <p className="muted">
        Матеріали без відповідного обробника. LLM викликається лише якщо ввімкнено «Передавати в LLM невідомі
        сторінки» для джерела або завдання.
      </p>
      <div className="filters">
        <Field label="Передано в LLM">
          <select value={forwarded} onChange={(e) => setForwarded(e.target.value as "" | "true" | "false")}>
            <option value="">усі</option>
            <option value="true">так</option>
            <option value="false">ні</option>
          </select>
        </Field>
        <Field label="Джерело">
          <input value={sourceId} onChange={(e) => setSourceId(e.target.value)} />
        </Field>
      </div>
      <ErrorBox error={list.error} />
      <Table
        label="Невідомі матеріали"
        rows={list.items}
        rowKey={(m) => m.observation_id}
        columns={[
          { header: "URL", cell: (m) => m.url ?? m.material_id },
          {
            header: "Джерело",
            cell: (m) => <Link to={`/sources/${encodeURIComponent(m.source_id)}`}>{m.source_id}</Link>,
          },
          { header: "Передано в LLM", cell: (m) => (m.forwarded_to_llm ? "так" : "ні") },
          { header: "Причина", cell: (m) => m.reason ?? "—" },
          { header: "Зареєстровано", cell: (m) => formatDate(m.registered_at) },
          {
            header: "",
            cell: (m) => <Link to={`/materials/${encodeURIComponent(m.material_id)}/trace`}>Простежити</Link>,
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </>
  );
}
