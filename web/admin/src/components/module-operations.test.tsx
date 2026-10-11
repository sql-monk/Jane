import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ModuleSettingsForm } from "./ModuleSettingsForm";
import { TimeSeriesChart } from "./TelemetryCharts";
import type { ModuleConfiguration, ModuleTelemetry } from "../lib/modules";

const configuration: ModuleConfiguration = {
  service: "orchestrator",
  instance_id: "a",
  revision: 1,
  overrides: { "limits.engine.workers": 3 },
  pending_restart: false,
  fields: [
    {
      path: "limits.engine.workers",
      type: "number",
      integer: true,
      value: 3,
      inherited_value: 2,
      minimum: 0,
      maximum: 8,
      requires_restart: true,
      origin: "module",
    },
  ],
};

describe("module operations", () => {
  it("reset shows inherited value and submits removal instead of copying active value", () => {
    const save = vi.fn();
    render(
      <MemoryRouter>
        <ModuleSettingsForm configuration={configuration} save={save} pending={false} error={null} />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText("Кількість воркерів")).toHaveValue(3);
    fireEvent.click(screen.getByRole("button", { name: "Успадкувати" }));
    expect(screen.getByLabelText("Кількість воркерів")).toHaveValue(2);
    fireEvent.click(screen.getByRole("button", { name: "Зберегти налаштування" }));
    expect(save).toHaveBeenCalledWith({});
  });

  it("does not render unavailable measurements as zero", () => {
    const history: ModuleTelemetry = {
      service: "storage",
      instance_id: "a",
      sample_interval_seconds: 5,
      retention_seconds: 86400,
      metrics: [{ key: "value", label: "Вимірювання", unit: "мс" }],
      samples: [{ at: "2026-10-11T01:00:00Z", instance_id: "a", values: { value: null } }],
    };
    render(<TimeSeriesChart history={history} metric={history.metrics[0]!} />);
    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("breaks the graph at a process restart and at missing samples", () => {
    const history: ModuleTelemetry = {
      service: "storage",
      instance_id: "b",
      sample_interval_seconds: 5,
      retention_seconds: 86400,
      metrics: [{ key: "value", label: "Вимірювання", unit: "мс" }],
      samples: [
        { at: "2026-10-11T01:00:00Z", instance_id: "a", values: { value: 1 } },
        { at: "2026-10-11T01:00:05Z", instance_id: "a", values: { value: 2 } },
        { at: "2026-10-11T01:00:10Z", instance_id: "b", values: { value: 3 } },
        { at: "2026-10-11T01:00:15Z", instance_id: "b", values: { value: null } },
        { at: "2026-10-11T01:00:20Z", instance_id: "b", values: { value: 4 } },
      ],
    };
    const { container } = render(<TimeSeriesChart history={history} metric={history.metrics[0]!} />);
    expect(container.querySelectorAll("path.telemetry-line")).toHaveLength(3);
  });
});
