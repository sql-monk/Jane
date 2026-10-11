import { useSearchParams } from "react-router-dom";
import { useConfig } from "../app/context";
import { modules } from "../lib/modules";
import { Page } from "../components/ui";
import { TelemetryCharts } from "../components/TelemetryCharts";
import { ModuleCard } from "./ModulesPage";

export function MonitoringPage() {
  const config = useConfig();
  const [params, setParams] = useSearchParams();
  const items = modules(config);
  const selected =
    items.find((module) => module.id === params.get("module")) ??
    items.find((module) => module.id === "orchestrator");
  return (
    <Page
      title="Моніторинг"
      description="Поточна робота модулів та історія вимірювань. Дані збираються і коли адмінку закрито."
    >
      <div className="monitoring-module-picker">
        <label>
          Модуль
          <select
            aria-label="Модуль моніторингу"
            value={selected?.id}
            onChange={(event) => setParams({ module: event.target.value })}
          >
            {items.map((module) => (
              <option value={module.id} key={module.id}>
                {module.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {selected ? <TelemetryCharts key={selected.id} module={selected} /> : null}
      <div className="modules-grid monitoring-status-grid">
        {items.map((module) => (
          <ModuleCard key={module.id} module={module} />
        ))}
      </div>
    </Page>
  );
}
