import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import { pollDelay } from "../api/hooks";
import { ErrorBox, Loading, Page, Section, Status, Table } from "../components/ui";
import { Icon, type IconName } from "../components/Icon";
import { TaskQuickRun } from "../components/TaskQuickRun";
import { formatDate, formatMoney, formatDuration, statusLabel } from "../lib/format";
import { modules } from "../lib/modules";
import { TelemetryCharts } from "../components/TelemetryCharts";

function Metric({
  label,
  value,
  note,
  to,
  icon,
  tone = "neutral",
}: {
  label: string;
  value: string;
  note: string;
  to: string;
  icon: IconName;
  tone?: string;
}) {
  return (
    <Link className={`metric metric-${tone}`} to={to}>
      <div className="metric-head">
        <span>{label}</span>
        <Icon name={icon} />
      </div>
      <strong className="metric-value">{value}</strong>
      <span className="metric-note">
        {note}
        <Icon name="arrow" size={14} />
      </span>
    </Link>
  );
}

function countLabel(items: unknown[] | undefined, nextCursor: string | null | undefined, failed: boolean) {
  return !items || failed ? "—" : `${items.length}${nextCursor ? "+" : ""}`;
}

export function DashboardPage() {
  const api = useApi();
  const config = useConfig();
  const [days, setDays] = useState(1);
  const executors = useQuery({
    queryKey: ["executors"],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/executors")),
  });
  const sources = useQuery({
    queryKey: ["sources", "dashboard", config.page_size],
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/sources", { params: { query: { limit: config.page_size } } })),
  });
  const tasks = useQuery({
    queryKey: ["tasks", "dashboard", config.page_size],
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/tasks", { params: { query: { limit: config.page_size } } })),
  });
  const runs = useQuery({
    queryKey: ["runs", "recent", config.page_size],
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/runs", { params: { query: { limit: config.page_size } } })),
    refetchInterval: (query) =>
      !query.state.error &&
      query.state.data?.items.some((run) => ["queued", "running", "cancelling"].includes(run.status))
        ? pollDelay(query.state.dataUpdateCount, config.polling)
        : false,
  });
  const problems = useQuery({
    queryKey: ["problem-groups", "open", config.page_size],
    queryFn: () =>
      unwrap(
        api.orchestrator.GET("/v1/problem-groups", {
          params: { query: { status: "open", limit: config.page_size } },
        }),
      ),
  });
  const usage = useQuery({
    queryKey: ["llm-usage", "dashboard", days],
    queryFn: () => {
      const until = new Date();
      return unwrap(
        api.llm.GET("/v1/usage", {
          params: {
            query: {
              group_by: "day",
              since: new Date(until.getTime() - days * 86400000).toISOString(),
              until: until.toISOString(),
            },
          },
        }),
      );
    },
  });
  const unknown = useQuery({
    queryKey: ["unknown-materials", "dashboard", config.page_size],
    queryFn: () =>
      unwrap(
        api.orchestrator.GET("/v1/unknown-materials", { params: { query: { limit: config.page_size } } }),
      ),
  });
  const queries = [executors, sources, tasks, runs, problems, usage, unknown];
  const fetching = queries.some((query) => query.isFetching);
  const refresh = () => {
    void Promise.all(queries.map((query) => query.refetch()));
  };
  const recent = runs.isError ? [] : (runs.data?.items ?? []);
  const activeRuns = recent.filter((run) => ["queued", "running", "cancelling"].includes(run.status));
  const failedRuns = recent.filter((run) => run.status === "failed");
  const successful = recent.filter((run) => run.status === "succeeded").length;
  const workerItems = executors.isError ? [] : (executors.data?.items ?? []);
  const healthy = workerItems.filter((executor) => executor.status === "ok").length;
  const unavailable = workerItems.filter((executor) => executor.status !== "ok");
  const taskItems = tasks.isError ? [] : (tasks.data?.items ?? []);
  const groups = problems.isError ? [] : (problems.data?.items ?? []);
  const refreshedAt = queries.every((query) => query.isSuccess)
    ? Math.min(...queries.map((query) => query.dataUpdatedAt))
    : null;

  return (
    <Page
      title="Огляд"
      actions={
        <>
          <button className="btn" type="button" onClick={refresh} disabled={fetching}>
            <Icon name="refresh" />
            {fetching ? "Оновлення…" : "Оновити"}
          </button>
          <Link className="btn btn-primary" to="/assistant">
            <Icon name="plus" />
            Підключити джерело
          </Link>
        </>
      }
    >
      <div className="overview-intro">
        <div>
          <span className="eyebrow">Центр керування</span>
          <h2>Ваші дані. Усе під контролем.</h2>
          <p>Від джерела до результату — спостерігайте, перевіряйте та керуйте.</p>
        </div>
        <div className="overview-updated">
          <span className={`status-dot ${refreshedAt ? "dot-ok" : "dot-warn"}`} />
          {refreshedAt
            ? `Оновлено ${formatDate(new Date(refreshedAt).toISOString())}`
            : queries.some((query) => query.isError)
              ? "Частина даних недоступна"
              : "Очікуємо дані сервісів"}
        </div>
      </div>
      <Section title="Моніторинг платформи" actions={<Link to="/monitoring">Усі графіки →</Link>}>
        <TelemetryCharts module={modules(config).find((module) => module.id === "orchestrator")!} compact />
      </Section>
      <div className="metrics-grid">
        <Metric
          label="Джерела"
          value={countLabel(sources.data?.items, sources.data?.next_cursor, sources.isError)}
          note="Підключені сайти й канали"
          to="/sources"
          icon="sources"
        />
        <Metric
          label="Увімкнені завдання"
          value={
            tasks.data && !tasks.isError
              ? `${taskItems.filter((task) => task.enabled).length}${tasks.data.next_cursor ? "+" : ""}`
              : "—"
          }
          note="У завантаженій вибірці"
          to="/tasks"
          icon="tasks"
        />
        <Metric
          label="У роботі"
          value={runs.data && !runs.isError ? `${activeRuns.length}${runs.data.next_cursor ? "+" : ""}` : "—"}
          note="Серед останніх запусків"
          to="/runs"
          icon="runs"
          tone="info"
        />
        <Metric
          label="Відкриті групи проблем матеріалів"
          value={countLabel(problems.data?.items, problems.data?.next_cursor, problems.isError)}
          note="Групи схожих помилок або нерозпізнаних форматів"
          to="/problems?status=open"
          icon="problems"
          tone={groups.length ? "warn" : "neutral"}
        />
        <Metric
          label="Невдалі запуски"
          value={runs.isSuccess ? `${failedRuns.length}${runs.data.next_cursor ? "+" : ""}` : "—"}
          note="Серед останніх запусків; окремо від груп матеріалів"
          to="/runs?status=failed"
          icon="runs"
          tone={failedRuns.length ? "warn" : "neutral"}
        />
        <Metric
          label="Невідомі матеріали"
          value={countLabel(unknown.data?.items, unknown.data?.next_cursor, unknown.isError)}
          note="Зареєстровані спостереження; це не завжди збій запуску"
          to="/problems?tab=unknown"
          icon="materials"
        />
      </div>
      <p className="sample-note">
        Списки: до {config.page_size} записів на розділ. «+» означає, що є наступні сторінки; показники
        запусків і завдань стосуються цієї вибірки.
      </p>
      <div className="overview-columns">
        <div>
          <Section
            title="Потребує уваги"
            actions={
              <Link to="/problems?status=open">
                Переглянути проблеми <Icon name="arrow" size={14} />
              </Link>
            }
          >
            <ErrorBox error={problems.error} />
            <ErrorBox error={executors.error} />
            <ErrorBox error={runs.error} />
            {problems.isLoading || executors.isLoading || runs.isLoading ? <Loading /> : null}
            {unavailable.map((executor) => (
              <a className="attention-row" key={executor.executor} href="#executors">
                <span className="attention-icon">
                  <Icon name="problems" />
                </span>
                <span>
                  <strong>{executor.executor}</strong>
                  <small>
                    Виконавець{" "}
                    {executor.status === "down"
                      ? "недоступний"
                      : executor.status === "degraded"
                        ? "працює з обмеженнями"
                        : "має невідомий стан"}
                    . Перевірте підключення та конфігурацію.
                  </small>
                </span>
                <Status value={executor.status} />
              </a>
            ))}
            {failedRuns.slice(0, 3).map((run) => (
              <Link className="attention-row" key={run.run_id} to={`/runs/${encodeURIComponent(run.run_id)}`}>
                <span className="attention-icon">
                  <Icon name="runs" />
                </span>
                <span>
                  <strong>Збій завдання {run.task_id}</strong>
                  <small>Відкрийте запуск, щоб перевірити помилки етапів і повтори.</small>
                </span>
                <Icon name="arrow" />
              </Link>
            ))}
            {groups.slice(0, 3).map((group) => (
              <Link
                className="attention-row"
                key={group.group_id}
                to={`/problems?status=open&source_id=${encodeURIComponent(group.source_id)}`}
              >
                <span className="attention-icon">
                  <Icon name="materials" />
                </span>
                <span>
                  <strong>{group.source_id}</strong>
                  <small>
                    {group.count} проблемних матеріалів · {group.signature}
                  </small>
                </span>
                <Status value={group.problem} />
              </Link>
            ))}
            {queries.slice(0, 5).every((query) => query.isSuccess) &&
            !unavailable.length &&
            !failedRuns.length &&
            !groups.length ? (
              <div className="empty-state">
                <span className="empty-icon">
                  <Icon name="check" size={26} />
                </span>
                <strong>У цій вибірці проблем немає</strong>
                <p>Відкритих груп і невдалих запусків не знайдено. Відомі виконавці доступні.</p>
              </div>
            ) : null}
          </Section>
          <Section
            title="Останні запуски"
            actions={
              <Link to="/runs">
                Усі запуски <Icon name="arrow" size={14} />
              </Link>
            }
          >
            {runs.data && !runs.isError ? (
              <div className="run-summary" aria-label="Розподіл останніх запусків">
                <span>
                  <i className="status-dot dot-ok" />
                  Успішні <strong>{successful}</strong>
                </span>
                <span>
                  <i className="status-dot dot-info" />У роботі <strong>{activeRuns.length}</strong>
                </span>
                <span>
                  <i className="status-dot dot-bad" />З помилками <strong>{failedRuns.length}</strong>
                </span>
              </div>
            ) : null}
            {runs.isLoading ? <Loading /> : null}
            <ErrorBox error={runs.error} />
            <Table
              label="Останні запуски"
              rows={recent.slice(0, 8)}
              rowKey={(run) => run.run_id}
              empty={
                runs.isLoading
                  ? "Завантаження запусків…"
                  : runs.isError
                    ? "Дані запусків недоступні"
                    : "Запусків ще немає. Відкрийте завдання та запустіть перший збір."
              }
              columns={[
                {
                  header: "Запуск / завдання",
                  cell: (run) => (
                    <div className="cell-stack">
                      <Link to={`/runs/${encodeURIComponent(run.run_id)}`}>{run.task_id}</Link>
                      <small className="muted">{run.run_id}</small>
                    </div>
                  ),
                },
                { header: "Стан", cell: (run) => <Status value={run.status} /> },
                {
                  header: "Етапи",
                  cell: (run) =>
                    run.stages?.length ? (
                      <div className="stage-chips">
                        {run.stages.map((stage) => (
                          <span
                            key={stage.stage_id}
                            title={Object.entries(stage.counts ?? {})
                              .map(([status, count]) => `${statusLabel(status)}: ${count}`)
                              .join(" · ")}
                          >
                            {stage.stage_id}
                            {stage.counts?.["completed"] !== undefined ? (
                              <small>{stage.counts["completed"]} завершено</small>
                            ) : null}
                          </span>
                        ))}
                      </div>
                    ) : (
                      "—"
                    ),
                },
                { header: "Створено", cell: (run) => formatDate(run.created_at) },
                { header: "Тривалість", cell: (run) => formatDuration(run.started_at, run.finished_at) },
                { header: "Останній прогрес", cell: (run) => formatDate(run.updated_at) },
              ]}
            />
          </Section>
          <Section
            title="Завдання під рукою"
            actions={
              <Link to="/tasks">
                Керувати завданнями <Icon name="arrow" size={14} />
              </Link>
            }
          >
            <ErrorBox error={tasks.error} />
            {tasks.isLoading ? <Loading /> : null}
            {taskItems.slice(0, 5).map((task) => (
              <div className="task-shortcut" key={task.task_id}>
                <div>
                  <Link to={`/tasks/${encodeURIComponent(task.task_id)}`}>
                    <strong>{task.title}</strong>
                  </Link>
                  <small>
                    {task.source_id} · {task.enabled ? "увімкнено" : "призупинено"}
                  </small>
                </div>
                <TaskQuickRun taskId={task.task_id} />
              </div>
            ))}
            {tasks.isSuccess && !taskItems.length ? (
              <div className="empty-state">
                <strong>Підготуйте перший ланцюжок</strong>
                <p>Оберіть джерело, додайте етапи збору й обробки, задайте розклад.</p>
                <Link className="btn btn-primary" to="/tasks/new">
                  Створити завдання
                </Link>
              </div>
            ) : null}
          </Section>
        </div>
        <aside className="overview-aside">
          <Section
            title="Витрати LLM"
            actions={
              <select
                aria-label="Період витрат LLM"
                value={days}
                onChange={(event) => setDays(Number(event.target.value))}
              >
                <option value={1}>24 години</option>
                <option value={7}>7 днів</option>
                <option value={30}>30 днів</option>
              </select>
            }
          >
            {usage.isLoading ? <Loading /> : null}
            <ErrorBox error={usage.error} />
            <strong className="cost-value" data-testid="usage-total">
              {usage.isError ? "—" : formatMoney(usage.data?.totals?.cost)}
            </strong>
            <p className="muted">За обраний період до останнього оновлення</p>
            <div className="usage-stats">
              <div>
                <strong>{usage.isError ? "—" : (usage.data?.totals?.requests ?? "—")}</strong>
                <span>запитів</span>
              </div>
              <div>
                <strong>
                  {usage.isError
                    ? "—"
                    : usage.data?.totals
                      ? (usage.data.totals.input_tokens + usage.data.totals.output_tokens).toLocaleString(
                          "uk-UA",
                        )
                      : "—"}
                </strong>
                <span>токенів</span>
              </div>
            </div>
            <Link className="section-link" to="/llm">
              Деталі витрат і бюджети <Icon name="arrow" size={14} />
            </Link>
          </Section>
          <div id="executors">
            <Section
              title="Виконавці"
              actions={
                <span className="muted">
                  {executors.isError || !executors.data ? "—" : `${healthy}/${workerItems.length}`} доступні
                </span>
              }
            >
              {executors.isLoading ? <Loading /> : null}
              <ErrorBox error={executors.error} />
              {workerItems.length ? (
                <table className="executor-table" aria-label="Виконавці">
                  <thead className="sr-only">
                    <tr>
                      <th>Виконавець / роль</th>
                      <th>Стан</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workerItems.map((executor) => (
                      <tr key={executor.executor}>
                        <td>
                          <div className="executor-row">
                            <span
                              className={`status-dot ${executor.status === "ok" ? "dot-ok" : executor.status === "down" ? "dot-bad" : "dot-warn"}`}
                            />
                            <div>
                              <strong>{executor.executor}</strong>
                              <small>
                                {(
                                  {
                                    collector: "Колектор",
                                    handler: "Обробник",
                                    storage_read: "Читання сховищ",
                                    registry: "Репозиторій пакетів",
                                    llm: "LLM-шлюз",
                                    assistant: "Асистент",
                                  } as Record<string, string>
                                )[executor.role] ?? executor.role}
                              </small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <Status value={executor.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : null}
              {executors.isSuccess && !workerItems.length ? (
                <p className="muted">Виконавці ще не зареєстровані.</p>
              ) : null}
              <p className="sample-note">Останній відомий оркестратору стан.</p>
            </Section>
          </div>
          <Section title="Швидкі дії">
            <div className="quick-links">
              {[
                ["/sources/new", "Нове джерело", "Додати сайт або Telegram-канал", "sources"],
                ["/tasks/new", "Нове завдання", "Зібрати ланцюжок і розклад", "tasks"],
                ["/packages", "Редагувати обробник", "Код, тести, активація й відкат", "packages"],
                ["/materials", "Перевірити матеріали", "Оригінали та історія обробки", "materials"],
              ].map(([to, title, note, icon]) => (
                <Link className="quick-link" key={to} to={to!}>
                  <Icon name={icon as IconName} />
                  <span>
                    <strong>{title}</strong>
                    <small>{note}</small>
                  </span>
                  <Icon name="arrow" size={14} />
                </Link>
              ))}
            </div>
          </Section>
        </aside>
      </div>
      <ErrorBox error={sources.error} title="Джерела недоступні" />
      <ErrorBox error={unknown.error} title="Невідомі матеріали недоступні" />
    </Page>
  );
}
