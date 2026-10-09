// Handler packages and collector rules from the single registry (ТЗ §7): versions, tests, forks, diff, upstream.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { ifMatch, newIdempotencyKey, unwrap, unwrapWithEtag } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { HandlerKind, Job, Package, PackageVersion, StatusChange, TestReport } from "../api/types";
import { JobPanel, TestReportView } from "../components/JobPanel";
import { UnifiedDiff } from "../components/UnifiedDiff";
import {
  ErrorBox,
  Field,
  JsonView,
  KeyValue,
  Loading,
  LoadMore,
  Notice,
  Page,
  ReasonAction,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { SEMVER_PATTERN, SLUG_PATTERN, formatBytes, formatDate, refLabel } from "../lib/format";

const KINDS: HandlerKind[] = ["extractor", "storage", "llm", "transform", "collector-rules"];
const KIND_LABELS: Record<HandlerKind, string> = {
  extractor: "екстрактор",
  storage: "збереження",
  llm: "LLM",
  transform: "перетворення",
  "collector-rules": "правила колектора",
};

export function PackagesPage() {
  const api = useApi();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const kind = (params.get("kind") ?? "") as HandlerKind | "";
  const q = params.get("q") ?? "";
  const list = useCursorList(["packages", kind, q], (cursor, limit) =>
    unwrap(
      api.registry.GET("/v1/packages", {
        params: {
          query: { limit, ...(cursor ? { cursor } : {}), ...(kind ? { kind } : {}), ...(q ? { q } : {}) },
        },
      }),
    ),
  );
  const [creating, setCreating] = useState(false);
  const [draft, setDraft] = useState({
    package_id: "",
    kind: "extractor" as HandlerKind,
    title: "",
    auto_changes_allowed: true,
  });
  const create = useMutation({
    mutationFn: () =>
      unwrap(
        api.registry.POST("/v1/packages", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body: draft,
        }),
      ),
    onSuccess: (pkg) => navigate(`/packages/${encodeURIComponent(pkg.package_id)}`),
  });
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };
  return (
    <Page
      title="Пакети обробників і правила колекторів"
      actions={
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          Новий пакет
        </button>
      }
    >
      {creating ? (
        <Section title="Новий пакет (без версій)">
          <div className="grid-3">
            <Field label="package_id">
              <input
                value={draft.package_id}
                onChange={(e) => setDraft({ ...draft, package_id: e.target.value })}
              />
            </Field>
            <Field label="Тип">
              <select
                value={draft.kind}
                onChange={(e) => setDraft({ ...draft, kind: e.target.value as HandlerKind })}
              >
                {KINDS.map((k) => (
                  <option key={k} value={k}>
                    {KIND_LABELS[k]}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Назва">
              <input value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
            </Field>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={draft.auto_changes_allowed}
                onChange={(e) => setDraft({ ...draft, auto_changes_allowed: e.target.checked })}
              />
              Дозволити автоматичні зміни (версії від LLM)
            </label>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!SLUG_PATTERN.test(draft.package_id) || !draft.title || create.isPending}
            onClick={() => create.mutate()}
          >
            Створити
          </button>
          <ErrorBox error={create.error} />
        </Section>
      ) : null}
      <div className="filters">
        <Field label="Тип">
          <select value={kind} onChange={(e) => update("kind", e.target.value)}>
            <option value="">усі</option>
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {KIND_LABELS[k]}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Пошук">
          <input value={q} onChange={(e) => update("q", e.target.value)} />
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Пакети"
        rows={list.items}
        rowKey={(p) => p.package_id}
        columns={[
          {
            header: "Пакет",
            cell: (p) => <Link to={`/packages/${encodeURIComponent(p.package_id)}`}>{p.package_id}</Link>,
          },
          { header: "Тип", cell: (p) => KIND_LABELS[p.kind] ?? p.kind },
          { header: "Назва", cell: (p) => p.title },
          { header: "Остання версія", cell: (p) => p.latest_version ?? "—" },
          { header: "Форк від", cell: (p) => (p.fork_of ? refLabel(p.fork_of) : "—") },
          { header: "Автозміни", cell: (p) => (p.auto_changes_allowed ? "дозволено" : "заборонено") },
          { header: "Оновлено", cell: (p) => formatDate(p.updated_at) },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

type PackageTab = "overview" | "versions" | "diff" | "fork" | "upstream";

export function PackagePage() {
  const { packageId = "" } = useParams();
  const api = useApi();
  const [params] = useSearchParams();
  const [tab, setTab] = useState<PackageTab>(params.get("version") ? "versions" : "overview");
  const pkg = useQuery({
    queryKey: ["package", packageId],
    queryFn: () =>
      unwrapWithEtag(
        api.registry.GET("/v1/packages/{package_id}", { params: { path: { package_id: packageId } } }),
      ),
  });
  const data = pkg.data?.data;
  const tabs: Array<[PackageTab, string]> = [
    ["overview", "Огляд"],
    ["versions", "Версії й тести"],
    ["diff", "Відмінності"],
    ["fork", "Створити форк"],
  ];
  if (data?.fork_of) tabs.push(["upstream", "Оновлення батька"]);
  return (
    <Page title={`Пакет ${packageId}`}>
      {pkg.isLoading ? <Loading /> : null}
      <ErrorBox error={pkg.error} />
      {data ? (
        <>
          <Tabs<PackageTab> tabs={tabs} active={tab} onChange={setTab} />
          {tab === "overview" ? <Overview pkg={data} etag={pkg.data?.etag ?? null} /> : null}
          {tab === "versions" ? <Versions pkg={data} initialVersion={params.get("version")} /> : null}
          {tab === "diff" ? <DiffTab pkg={data} /> : null}
          {tab === "fork" ? <ForkTab pkg={data} /> : null}
          {tab === "upstream" && data.fork_of ? <UpstreamTab pkg={data} /> : null}
        </>
      ) : null}
    </Page>
  );
}

function Overview({ pkg, etag }: { pkg: Package; etag: string | null }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const forks = useQuery({
    queryKey: ["packages", "forks", pkg.package_id],
    queryFn: () =>
      unwrap(api.registry.GET("/v1/packages", { params: { query: { fork_of: pkg.package_id } } })),
  });
  const patch = useMutation({
    mutationFn: (body: { auto_changes_allowed?: boolean; deprecated?: boolean }) =>
      unwrapWithEtag(
        api.registry.PATCH("/v1/packages/{package_id}", {
          params: { path: { package_id: pkg.package_id }, header: ifMatch(etag) },
          headers: { "Content-Type": "application/merge-patch+json" },
          body,
        }),
      ),
    onSuccess: (result) => queryClient.setQueryData(["package", pkg.package_id], result),
  });
  return (
    <>
      <KeyValue
        rows={[
          ["Тип", KIND_LABELS[pkg.kind] ?? pkg.kind],
          ["Назва", pkg.title],
          ["Опис", pkg.description ?? "—"],
          ["Остання версія", pkg.latest_version ?? "—"],
          [
            "Форк від",
            pkg.fork_of ? (
              <Link to={`/packages/${encodeURIComponent(pkg.fork_of.package_id)}`}>
                {refLabel(pkg.fork_of)}
              </Link>
            ) : (
              "—"
            ),
          ],
          ["Форків", String(pkg.forks_count ?? 0)],
          ["Власник", pkg.owner ?? "—"],
          ["Застарілий", pkg.deprecated ? "так" : "ні"],
        ]}
      />
      <label className="checkbox">
        <input
          type="checkbox"
          checked={pkg.auto_changes_allowed}
          disabled={patch.isPending}
          onChange={(e) => patch.mutate({ auto_changes_allowed: e.target.checked })}
        />
        Дозволити автоматичні зміни цього пакета (версії від LLM)
      </label>
      <ErrorBox error={patch.error} title="Не вдалося змінити налаштування" />
      <p>
        <Link to={`/tasks?package_id=${encodeURIComponent(pkg.package_id)}`}>
          Завдання й етапи, що використовують пакет
        </Link>
      </p>
      <Section title="Форки цього пакета">
        <ErrorBox error={forks.error} />
        <Table
          label="Форки"
          rows={forks.data?.items ?? []}
          rowKey={(p) => p.package_id}
          empty="Форків немає"
          columns={[
            {
              header: "Форк",
              cell: (p) => <Link to={`/packages/${encodeURIComponent(p.package_id)}`}>{p.package_id}</Link>,
            },
            { header: "Від версії", cell: (p) => p.fork_of?.version ?? "—" },
            { header: "Остання версія", cell: (p) => p.latest_version ?? "—" },
          ]}
        />
      </Section>
    </>
  );
}

function Versions({ pkg, initialVersion }: { pkg: Package; initialVersion: string | null }) {
  const api = useApi();
  const list = useCursorList(["package-versions", pkg.package_id], (cursor, limit) =>
    unwrap(
      api.registry.GET("/v1/packages/{package_id}/versions", {
        params: { path: { package_id: pkg.package_id }, query: { limit, ...(cursor ? { cursor } : {}) } },
      }),
    ),
  );
  const [selected, setSelected] = useState<string | null>(initialVersion);
  return (
    <>
      <ErrorBox error={list.error} />
      <Table
        label="Версії"
        rows={list.items}
        rowKey={(v) => v.version}
        columns={[
          {
            header: "Версія",
            cell: (v) => (
              <button type="button" className="link" onClick={() => setSelected(v.version)}>
                {v.version}
              </button>
            ),
          },
          { header: "Статус", cell: (v) => <Status value={v.status} /> },
          { header: "Тести", cell: (v) => <Status value={v.test_status} /> },
          { header: "Автор", cell: (v) => v.created_by ?? "—" },
          { header: "Створено", cell: (v) => formatDate(v.created_at) },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      {selected ? <VersionDetail key={selected} pkg={pkg} version={selected} /> : null}
    </>
  );
}

function VersionDetail({ pkg, version }: { pkg: Package; version: string }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const [testJob, setTestJob] = useState<string | null>(null);
  const detail = useQuery({
    queryKey: ["package-version", pkg.package_id, version],
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
          params: { path: { package_id: pkg.package_id, version } },
        }),
      ),
  });
  const setStatus = useMutation({
    mutationFn: (body: StatusChange) =>
      unwrap(
        api.registry.POST("/v1/packages/{package_id}/versions/{version}/status", {
          params: {
            path: { package_id: pkg.package_id, version },
            header: { "Idempotency-Key": newIdempotencyKey() },
          },
          body,
        }),
      ),
    onSuccess: (updated) => {
      queryClient.setQueryData(["package-version", pkg.package_id, version], updated);
      void queryClient.invalidateQueries({ queryKey: ["package-versions", pkg.package_id] });
    },
  });
  const runTests = useMutation({
    mutationFn: () =>
      unwrap(
        api.handler.POST("/v1/test-runs", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body: {
            handler: {
              package_id: pkg.package_id,
              version,
              ...(detail.data?.digest ? { digest: detail.data.digest } : {}),
            },
            tests: "all",
          },
        }),
      ) as Promise<Job>,
    onSuccess: (job) => setTestJob(job.job_id),
  });
  const v: PackageVersion | undefined = detail.data;
  const status = (s: StatusChange["status"], reason: string) =>
    setStatus.mutate({ status: s, ...(reason ? { reason } : {}) });
  return (
    <Section title={`Версія ${version}`}>
      {detail.isLoading ? <Loading /> : null}
      <ErrorBox error={detail.error} />
      {v ? (
        <>
          <KeyValue
            rows={[
              ["Статус", <Status value={v.status} />],
              ["Тести (останній звіт)", <Status value={v.test_status} />],
              [
                "Тести на всіх контекстах",
                <span data-testid="test-summary-status">
                  <Status value={v.test_summary?.status ?? null} />
                </span>,
              ],
              ["Дайджест", <code>{v.digest}</code>],
              ["Розмір", formatBytes(v.size_bytes)],
              ["Автор", v.created_by ?? "—"],
              [
                "Походження",
                v.manifest?.provenance?.based_on
                  ? `на основі ${refLabel(v.manifest.provenance.based_on)}`
                  : "—",
              ],
              ["Опис змін", v.manifest?.provenance?.change_summary ?? "—"],
            ]}
          />
          <div className="button-row">
            <Link
              className="btn"
              to={`/packages/${encodeURIComponent(pkg.package_id)}/versions/${encodeURIComponent(version)}/edit`}
            >
              Редагувати код (нова версія)
            </Link>
            {pkg.kind === "collector-rules" ? (
              <Link
                className="btn"
                to={`/packages/${encodeURIComponent(pkg.package_id)}/versions/${encodeURIComponent(version)}/rules`}
              >
                Редагувати стратегії обходу
              </Link>
            ) : null}
            {pkg.kind !== "collector-rules" ? (
              <button
                type="button"
                className="btn"
                onClick={() => runTests.mutate()}
                disabled={runTests.isPending}
              >
                Запустити тести (без запису)
              </button>
            ) : null}
            <ReasonAction
              label="Погодити"
              confirmLabel="Погодити версію"
              busy={setStatus.isPending}
              onConfirm={(r) => status("approved", r)}
            />
            <ReasonAction
              label="Відхилити"
              confirmLabel="Відхилити версію"
              danger
              busy={setStatus.isPending}
              onConfirm={(r) => status("rejected", r)}
            />
            <ReasonAction
              label="Застаріла"
              confirmLabel="Позначити застарілою"
              busy={setStatus.isPending}
              onConfirm={(r) => status("deprecated", r)}
            />
            <ReasonAction
              label="Відкликати (yank)"
              confirmLabel="Відкликати"
              danger
              busy={setStatus.isPending}
              onConfirm={(r) => status("yanked", r)}
            />
          </div>
          <ErrorBox error={setStatus.error} title="Статус не змінено" />
          <ErrorBox error={runTests.error} title="Тести не запущено" />
          {testJob ? (
            <JobPanel
              service="handler"
              client={api.handler}
              jobId={testJob}
              title="Прогін тестів"
              renderResult={(result) => <TestReportView report={result as unknown as TestReport} />}
            />
          ) : null}
          {v.test_summary?.contexts.length ? (
            <Section title="Підсумок тестів за контекстами">
              <p className="muted">
                Для кожного контексту (власні тести, прогін на прив'язках етапу) діє останній звіт; версія
                пройшла всюди, лише якщо пройшов останній звіт кожного контексту.
              </p>
              <Table
                label="Тести за контекстами"
                rows={v.test_summary.contexts}
                rowKey={(c, i) => `${c.context ?? ""}-${i}`}
                columns={[
                  { header: "Контекст", cell: (c) => c.context ?? "без контексту" },
                  { header: "Стан", cell: (c) => <Status value={c.test_status} /> },
                  { header: "Звітів", cell: (c) => String(c.reports) },
                  { header: "Виконавець", cell: (c) => c.runner ?? "—" },
                  { header: "Останній звіт", cell: (c) => formatDate(c.recorded_at) },
                ]}
              />
            </Section>
          ) : null}
          {(v.test_reports ?? []).length ? (
            <Section title="Записані звіти тестів">
              {(v.test_reports ?? []).map((r, i) => (
                <div key={i}>
                  <p className="muted">
                    {r.runner ?? ""} {r.context ?? ""} {formatDate(r.recorded_at)}
                  </p>
                  <TestReportView report={r.report} />
                </div>
              ))}
            </Section>
          ) : null}
          <Section title="Файли">
            <Table
              label="Файли версії"
              rows={v.files ?? []}
              rowKey={(f) => f.path}
              columns={[
                { header: "Шлях", cell: (f) => <code>{f.path}</code> },
                { header: "Розмір", cell: (f) => formatBytes(f.size_bytes) },
                { header: "sha256", cell: (f) => <code className="muted">{f.sha256.slice(0, 12)}…</code> },
              ]}
            />
          </Section>
          <Section title="Історія статусів">
            <Table
              label="Історія статусів"
              rows={v.status_history ?? []}
              rowKey={(h, i) => `${h.at}-${i}`}
              columns={[
                { header: "Коли", cell: (h) => formatDate(h.at) },
                { header: "Статус", cell: (h) => <Status value={h.status} /> },
                { header: "Хто", cell: (h) => h.by ?? "—" },
                { header: "Причина", cell: (h) => h.reason ?? "—" },
              ]}
            />
          </Section>
          {v.manifest ? (
            <Section title="Маніфест (jane-package.json)">
              <JsonView value={v.manifest} />
            </Section>
          ) : null}
        </>
      ) : null}
    </Section>
  );
}

function DiffTab({ pkg }: { pkg: Package }) {
  const api = useApi();
  const [from, setFrom] = useState("");
  const [to, setTo] = useState(pkg.latest_version ?? "");
  const [request, setRequest] = useState<{ from: string; to: string } | null>(null);
  const diff = useQuery({
    queryKey: ["diff", pkg.package_id, request],
    enabled: Boolean(request?.to),
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/diff", {
          params: {
            path: { package_id: pkg.package_id },
            query: { to: request?.to as string, ...(request?.from ? { from: request.from } : {}) },
          },
        }),
      ),
  });
  return (
    <>
      <div className="filters">
        <Field label="Від (версія або parent:<версія>)">
          <input
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            placeholder={pkg.fork_of ? `parent:${pkg.fork_of.version}` : "1.1.0"}
          />
        </Field>
        <Field label="До версії">
          <input value={to} onChange={(e) => setTo(e.target.value)} />
        </Field>
        <button
          type="button"
          className="btn btn-primary"
          disabled={!to}
          onClick={() => setRequest({ from, to })}
        >
          Порівняти
        </button>
      </div>
      {diff.isLoading ? <Loading /> : null}
      <ErrorBox error={diff.error} />
      {diff.data ? <DiffView diff={diff.data} /> : null}
    </>
  );
}

export function DiffView({ diff }: { diff: import("../api/types").PackageDiff }) {
  return (
    <div aria-label="Відмінності версій">
      <p>
        {refLabel(diff.from)} → <strong>{refLabel(diff.to)}</strong>
      </p>
      {diff.manifest_changes?.length ? (
        <Table
          label="Зміни маніфесту"
          rows={diff.manifest_changes}
          rowKey={(c, i) => `${c.pointer}-${i}`}
          columns={[
            { header: "Поле", cell: (c) => <code>{c.pointer}</code> },
            { header: "Операція", cell: (c) => c.op },
            { header: "Було", cell: (c) => <JsonView value={c.old ?? null} compact /> },
            { header: "Стало", cell: (c) => <JsonView value={c.new ?? null} compact /> },
          ]}
        />
      ) : null}
      {diff.files.map((f) => (
        <div key={f.path} className="diff-file-block">
          <p>
            <code>{f.path}</code>{" "}
            <Status
              value={
                f.status === "added"
                  ? "success"
                  : f.status === "removed"
                    ? "failed"
                    : f.status === "modified"
                      ? "running"
                      : "skipped"
              }
            />{" "}
            {f.status}
            {f.binary ? " (бінарний)" : ""}
          </p>
          {f.unified_diff ? <UnifiedDiff diff={f.unified_diff} label={`diff ${f.path}`} /> : null}
        </div>
      ))}
    </div>
  );
}

function ForkTab({ pkg }: { pkg: Package }) {
  const api = useApi();
  const navigate = useNavigate();
  const [draft, setDraft] = useState({
    new_package_id: "",
    from_version: pkg.latest_version ?? "",
    initial_version: "",
    title: "",
    auto_changes_allowed: false,
  });
  const fork = useMutation({
    mutationFn: () =>
      unwrap(
        api.registry.POST("/v1/packages/{package_id}/forks", {
          params: {
            path: { package_id: pkg.package_id },
            header: { "Idempotency-Key": newIdempotencyKey() },
          },
          body: {
            new_package_id: draft.new_package_id,
            from_version: draft.from_version,
            ...(draft.initial_version ? { initial_version: draft.initial_version } : {}),
            ...(draft.title ? { title: draft.title } : {}),
            auto_changes_allowed: draft.auto_changes_allowed,
          },
        }),
      ),
    onSuccess: (created) => navigate(`/packages/${encodeURIComponent(created.package_id)}`),
  });
  return (
    <Section title="Незалежний форк">
      <Notice>
        Форк — незалежна копія з посиланням на батька й вихідну версію. Зміни батька на форк не впливають;
        перенесення — лише за явною командою. Підключення й секрети не копіюються.
      </Notice>
      <div className="grid-3">
        <Field label="Новий package_id">
          <input
            value={draft.new_package_id}
            onChange={(e) => setDraft({ ...draft, new_package_id: e.target.value })}
          />
        </Field>
        <Field label="Від версії">
          <input
            value={draft.from_version}
            onChange={(e) => setDraft({ ...draft, from_version: e.target.value })}
          />
        </Field>
        <Field label="Перша версія форку (необов'язково)">
          <input
            value={draft.initial_version}
            onChange={(e) => setDraft({ ...draft, initial_version: e.target.value })}
          />
        </Field>
        <Field label="Назва">
          <input value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
        </Field>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={draft.auto_changes_allowed}
            onChange={(e) => setDraft({ ...draft, auto_changes_allowed: e.target.checked })}
          />
          Дозволити автоматичні зміни форку
        </label>
      </div>
      <button
        type="button"
        className="btn btn-primary"
        disabled={
          !SLUG_PATTERN.test(draft.new_package_id) ||
          !SEMVER_PATTERN.test(draft.from_version) ||
          fork.isPending
        }
        onClick={() => fork.mutate()}
      >
        Створити форк
      </button>
      <ErrorBox error={fork.error} title="Форк не створено" />
    </Section>
  );
}

function UpstreamTab({ pkg }: { pkg: Package }) {
  const api = useApi();
  const upstream = useQuery({
    queryKey: ["upstream", pkg.package_id],
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/upstream", {
          params: { path: { package_id: pkg.package_id } },
        }),
      ),
  });
  const [parentVersion, setParentVersion] = useState("");
  const [newVersion, setNewVersion] = useState("");
  const [compare, setCompare] = useState<string | null>(null);
  const [portJob, setPortJob] = useState<string | null>(null);
  const diff = useQuery({
    queryKey: ["diff", pkg.package_id, "parent", compare],
    enabled: Boolean(compare && pkg.latest_version),
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/diff", {
          params: {
            path: { package_id: pkg.package_id },
            query: { from: `parent:${compare as string}`, to: pkg.latest_version as string },
          },
        }),
      ),
  });
  const port = useMutation({
    mutationFn: () =>
      unwrap(
        api.registry.POST("/v1/packages/{package_id}/upstream-ports", {
          params: {
            path: { package_id: pkg.package_id },
            header: { "Idempotency-Key": newIdempotencyKey() },
          },
          body: {
            parent_version: parentVersion,
            new_version: newVersion,
            ...(pkg.latest_version ? { base_version: pkg.latest_version } : {}),
          },
        }),
      ) as Promise<Job>,
    onSuccess: (job) => setPortJob(job.job_id),
  });
  const u = upstream.data;
  return (
    <>
      {upstream.isLoading ? <Loading /> : null}
      <ErrorBox error={upstream.error} />
      {u ? (
        <>
          <KeyValue
            rows={[
              ["Батько", refLabel(u.fork_of)],
              ["Останнє перенесення", u.last_ported_version ?? "—"],
              ["Остання версія батька", u.parent_latest_version],
            ]}
          />
          {u.newer_parent_versions.length ? (
            <Notice tone="warn">
              У батька є нові версії:{" "}
              <strong data-testid="newer-parent-versions">{u.newer_parent_versions.join(", ")}</strong>. Форк
              не змінюється, доки ви явно не перенесете зміни.
            </Notice>
          ) : (
            <Notice tone="ok">Форк актуальний відносно батька.</Notice>
          )}
          <div className="button-row">
            {u.newer_parent_versions.map((pv) => (
              <button key={pv} type="button" className="btn" onClick={() => setCompare(pv)}>
                Порівняти з батьком {pv}
              </button>
            ))}
          </div>
          <ErrorBox error={diff.error} />
          {diff.data ? <DiffView diff={diff.data} /> : null}
          <Section title="Перенести зміни батька (явна команда)">
            <div className="grid-3">
              <Field label="Версія батька">
                <select value={parentVersion} onChange={(e) => setParentVersion(e.target.value)}>
                  <option value="">—</option>
                  {u.newer_parent_versions.map((pv) => (
                    <option key={pv} value={pv}>
                      {pv}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Нова версія форку">
                <input value={newVersion} onChange={(e) => setNewVersion(e.target.value)} />
              </Field>
            </div>
            <ReasonAction
              label="Перенести зміни"
              confirmLabel="Так, перенести в нову версію"
              requireReason={false}
              busy={!parentVersion || !SEMVER_PATTERN.test(newVersion) || port.isPending}
              onConfirm={() => port.mutate()}
            />
            <ErrorBox error={port.error} title="Перенесення не запущено" />
            {portJob ? (
              <JobPanel
                service="registry"
                client={api.registry}
                jobId={portJob}
                title="Перенесення змін батька"
              />
            ) : null}
          </Section>
        </>
      ) : null}
    </>
  );
}
