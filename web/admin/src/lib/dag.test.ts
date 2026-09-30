import { describe, expect, it } from "vitest";
import { buildDag } from "./dag";
import type { Stage, TaskConfig } from "../api/types";
import { openapiExample } from "../test/contracts";

describe("buildDag", () => {
  it("lays out the branching catalog task from the contract example", () => {
    const task = openapiExample<TaskConfig>("task-catalog");
    const dag = buildDag(task.stages);
    expect(dag.issues).toEqual([]);
    const layer = Object.fromEntries(dag.nodes.map((n) => [n.id, n.layer]));
    expect(layer).toMatchObject({
      collect: 0,
      "store-raw": 1,
      "extract-products": 1,
      "store-products": 2,
      "analyze-problems": 2,
    });
    expect(dag.edges).toContainEqual({
      from: "extract-products",
      to: "analyze-problems",
      select: "problems",
      conditional: false,
    });
    expect(dag.edges).toContainEqual({
      from: "collect",
      to: "extract-products",
      select: "output",
      conditional: true,
    });
    expect(dag.edges).toContainEqual({
      from: "collect",
      to: "unknown-pages",
      select: "unmatched_materials",
      conditional: false,
    });
  });

  it("reports cycles, unknown inputs and a missing collect stage", () => {
    const stages: Stage[] = [
      {
        stage_id: "a",
        kind: "handler",
        handler: { package_id: "p", version: "1.0.0" },
        inputs: [{ from: "b" }],
      },
      {
        stage_id: "b",
        kind: "handler",
        handler: { package_id: "p", version: "1.0.0" },
        inputs: [{ from: "a" }],
      },
      {
        stage_id: "c",
        kind: "handler",
        handler: { package_id: "p", version: "1.0.0" },
        inputs: [{ from: "zzz" }],
      },
    ];
    const issues = buildDag(stages).issues.join("\n");
    expect(issues).toContain("zzz");
    expect(issues).toContain("цикл");
    expect(issues).toContain("kind=collect");
  });
});
