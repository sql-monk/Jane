import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { ifMatch, unwrap, unwrapWithEtag } from "../api/client";
import { modules, type ModuleDefinition, type ModuleConfiguration } from "../lib/modules";
import { ErrorBox, Loading, Notice, Page, Section, Status, Tabs } from "../components/ui";
import { TelemetryCharts } from "../components/TelemetryCharts";
import { ModuleSettingsForm } from "../components/ModuleSettingsForm";

function useModuleState(module: ModuleDefinition) {
  const api = useApi();
  const config = useConfig();
  const health = useQuery({
    queryKey: ["module-health", module.executor],
    queryFn: () => unwrap(api.executor(module.executor).GET("/v1/health")),
    refetchInterval: config.monitoring.refresh_interval_ms,
  });
  const info = useQuery({
    queryKey: ["module-info", module.executor],
    queryFn: () => unwrap(api.executor(module.executor).GET("/v1/info")),
    refetchInterval: config.monitoring.refresh_interval_ms,
  });
  return { health, info };
}

export function ModuleCard({ module }: { module: ModuleDefinition }) {
  const { health, info } = useModuleState(module);
  return (
    <article className="module-card">
      <div className="module-card-head">
        <h2>
          <Link to={`/modules/${module.id}`}>{module.name}</Link>
        </h2>
        <Status value={health.isError ? "unknown" : (health.data?.status ?? "unknown")} />
      </div>
      <p>{module.description}</p>
      <small className="muted">{info.data ? `Версія ${info.data.version}` : "Версія недоступна"}</small>
      {health.isError ? <p className="telemetry-stale">Не вдалося перевірити доступність</p> : null}
      <div className="module-card-links">
        <Link to={`/modules/${module.id}?tab=monitoring`}>Моніторинг</Link>
        <Link to={`/modules/${module.id}?tab=settings`}>Налаштування</Link>
      </div>
    </article>
  );
}

export function ModulesPage() {
  const config = useConfig();
  return (
    <Page title="Модулі" description="Стан, моніторинг і налаштування кожного компонента платформи.">
      <div className="modules-grid">
        {modules(config).map((module) => (
          <ModuleCard key={module.id} module={module} />
        ))}
      </div>
    </Page>
  );
}

type Tab = "state" | "monitoring" | "settings" | "diagnostics";
export function ModulePage() {
  const config = useConfig();
  const { moduleId } = useParams();
  const module = modules(config).find((item) => item.id === moduleId);
  return module ? (
    <ModuleDetail key={module.id} module={module} />
  ) : (
    <Page title="Модуль не знайдено">
      <Link to="/modules">До всіх модулів</Link>
    </Page>
  );
}

function ModuleDetail({ module }: { module: ModuleDefinition }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const [params, setParams] = useSearchParams();
  const rawTab = params.get("tab");
  const tab: Tab =
    rawTab === "monitoring" || rawTab === "settings" || rawTab === "diagnostics" ? rawTab : "state";
  const { health, info } = useModuleState(module);
  const configuration = useQuery({
    queryKey: ["module-configuration", module.executor],
    queryFn: () => unwrapWithEtag(api.module(module.executor).GET("/v1/configuration")),
    enabled: tab === "settings",
    staleTime: Infinity,
  });
  const save = useMutation({
    mutationFn: (values: ModuleConfiguration["overrides"]) =>
      unwrapWithEtag(
        api
          .module(module.executor)
          .PUT("/v1/configuration", {
            params: { header: ifMatch(configuration.data?.etag) },
            body: { values },
          }),
      ),
    onSuccess: (result) => queryClient.setQueryData(["module-configuration", module.executor], result),
  });
  return (
    <Page
      title={module.name}
      description={module.description}
      actions={
        <Link className="btn" to="/modules">
          Усі модулі
        </Link>
      }
    >
      <Tabs<Tab>
        tabs={[
          ["state", "Стан"],
          ["monitoring", "Моніторинг"],
          ["settings", "Налаштування"],
          ["diagnostics", "Діагностика"],
        ]}
        active={tab}
        onChange={(next) => setParams({ tab: next })}
      />
      {tab === "monitoring" ? <TelemetryCharts module={module} /> : null}
      {tab === "settings" ? (
        <>
          <ErrorBox error={configuration.error} title="Конфігурація недоступна" />
          {configuration.isLoading ? <Loading /> : null}
          {configuration.data ? (
            <ModuleSettingsForm
              key={configuration.data.etag}
              configuration={configuration.data.data}
              save={(values) => save.mutate(values)}
              pending={save.isPending}
              error={save.error}
            />
          ) : null}
          {save.isSuccess ? (
            <Notice tone="ok">Налаштування збережено. Момент застосування показано біля параметрів.</Notice>
          ) : null}
          {module.links.length ? (
            <Section title="Пов’язані налаштування та дії">
              <div className="module-related">
                {module.links.map((link) => (
                  <Link className="btn" key={link.to} to={link.to}>
                    {link.label}
                  </Link>
                ))}
              </div>
            </Section>
          ) : null}
        </>
      ) : null}
      {tab === "state" || tab === "diagnostics" ? (
        <>
          <Section title="Доступність">
            <ErrorBox error={health.error} />
            <ErrorBox error={info.error} />
            {health.isLoading ? <Loading /> : null}
            <Status value={health.isError ? "unknown" : (health.data?.status ?? "unknown")} />
            {info.data ? (
              <p>
                Версія: {info.data.version} ·{" "}
                {health.dataUpdatedAt
                  ? `Перевірено ${new Date(health.dataUpdatedAt).toLocaleTimeString("uk-UA")}`
                  : ""}
              </p>
            ) : null}
            {Object.entries(health.data?.checks ?? {}).map(([name, check]) => (
              <div className="module-check" key={name}>
                <strong>{name}</strong>
                <Status value={check.status} />
                {check.message ? <span>{check.message}</span> : null}
              </div>
            ))}
          </Section>
          <Section title="Дії та пов’язані дані">
            <div className="module-related">
              {module.links.map((link) => (
                <Link className="btn" key={link.to} to={link.to}>
                  {link.label}
                </Link>
              ))}
              <Link className="btn" to="/audit">
                Аудит змін
              </Link>
            </div>
          </Section>
          {tab === "diagnostics" && info.data ? (
            <Section title="Можливості модуля">
              <dl className="module-capabilities">
                {Object.entries(info.data.capabilities ?? {}).map(([name, value]) => (
                  <div key={name}>
                    <dt>{name}</dt>
                    <dd>{typeof value === "object" ? JSON.stringify(value) : String(value)}</dd>
                  </div>
                ))}
              </dl>
            </Section>
          ) : null}
        </>
      ) : null}
    </Page>
  );
}
