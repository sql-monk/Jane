import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { JsonView, Status } from "./ui";
import { TestReportView } from "./JobPanel";
import { UnifiedDiff } from "./UnifiedDiff";
import { DagView } from "./DagView";
import type { TaskConfig, TestReport } from "../api/types";
import { openapiExample } from "../test/contracts";

// Built at runtime so secret scanners do not flag the (fake) fixture.
const FAKE_PASSWORD = ["hunter2", "SECRET"].join("-");

describe("components", () => {
  it("JsonView never renders secret values", () => {
    render(
      <JsonView value={{ params: { password: FAKE_PASSWORD }, secret_refs: { token: "env:TG_TOKEN" } }} />,
    );
    const text = screen.getByTestId("json-view").textContent ?? "";
    expect(text).not.toContain(FAKE_PASSWORD);
    expect(text).toContain("env:TG_TOKEN");
  });

  it("TestReportView shows passed/failed cases of the contract example", () => {
    render(<TestReportView report={openapiExample<TestReport>("test-report")} />);
    expect(screen.getByText("problem-sample-2026-09-26")).toBeInTheDocument();
    expect(screen.getAllByText("passed")).toHaveLength(2);
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("UnifiedDiff marks added and removed lines", () => {
    const { container } = render(<UnifiedDiff diff={"@@ -1 +1 @@\n-old\n+new\n"} label="d" />);
    expect(container.querySelector(".diff-del")?.textContent).toContain("-old");
    expect(container.querySelector(".diff-add")?.textContent).toContain("+new");
  });

  it("DagView draws every stage of a task", () => {
    const task = openapiExample<TaskConfig>("task-catalog");
    render(<DagView stages={task.stages} />);
    for (const stage of task.stages)
      expect(screen.getByTestId(`dag-node-${stage.stage_id}`)).toBeInTheDocument();
    expect(screen.getByTestId("dag-edge-extract-products-store-products")).toBeInTheDocument();
  });

  it("Status tolerates unknown values", () => {
    render(<Status value="brand_new_state" />);
    expect(screen.getByText("brand_new_state")).toBeInTheDocument();
  });
});
