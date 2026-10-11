import { describe, expect, it } from "vitest";
import { emptyValue, jsonType, moveItem, removeStage, renameField, renameStage } from "./property";
import { buildDag } from "./dag";
import type { Stage } from "../api/types";

describe("lossless properties and graph mutations", () => {
  it("distinguishes all falsy JSON values and preserves hostile own keys", () => {
    const value = JSON.parse('{"__proto__":{"safe":[null,false,0,""]},"constructor":4}');
    const next = renameField(value, "constructor", "count");
    expect(JSON.parse(JSON.stringify(next))).toEqual({
      ["__proto__"]: { safe: [null, false, 0, ""] },
      count: 4,
    });
    expect([null, false, 0, "", [], {}].map((v) => jsonType(v))).toEqual([
      "null",
      "boolean",
      "number",
      "string",
      "array",
      "object",
    ]);
    expect(emptyValue("boolean")).toBe(false);
  });
  it("rejects rename collisions and keeps array item types/order", () => {
    expect(() => renameField({ a: 1, b: false }, "a", "b")).toThrow();
    expect(moveItem([null, { nested: [false, 0] }, ""], 1, -1)).toEqual([{ nested: [false, 0] }, null, ""]);
  });
  const stages: Stage[] = [
    { stage_id: "collect", kind: "collect", collector: { collector: "web" } },
    {
      stage_id: "extract",
      kind: "handler",
      handler: { package_id: "pkg", version: "1.0.0" },
      inputs: [
        { from: "collect", select: "problems", when: { field: "result.status", op: "eq", value: "failed" } },
      ],
    },
  ];
  it("renames incoming refs while retaining conditions; delete removes refs", () => {
    const next = renameStage(stages, "collect", "raw");
    expect(next[1]?.inputs?.[0]).toEqual({ ...stages[1]?.inputs?.[0], from: "raw" });
    expect(removeStage(next, "raw")[0]?.inputs).toEqual([]);
    expect(() => renameStage(stages, "extract", "collect")).toThrow();
  });
  it("detects cycles, dangling links and duplicate collectors", () => {
    expect(
      buildDag([...stages, { ...stages[1]!, stage_id: "loop", inputs: [{ from: "loop" }] }]).issues.join(),
    ).toContain("цикл");
    expect(buildDag([{ ...stages[1]!, inputs: [{ from: "missing" }] }]).issues.join()).toContain(
      "невідомого",
    );
    expect(buildDag([stages[0]!, { ...stages[0]!, stage_id: "other" }]).issues.join()).toContain(
      "рівно один",
    );
  });
  it("matches orchestrator select restrictions for collect and handler sources", () => {
    for (const select of ["input_material", "problems"] as const)
      expect(
        buildDag([stages[0]!, { ...stages[1]!, inputs: [{ from: "collect", select }] }]).issues.join(),
      ).toContain("недопустимий вихід");
    expect(
      buildDag([
        ...stages,
        { ...stages[1]!, stage_id: "store", inputs: [{ from: "extract", select: "unmatched_materials" }] },
      ]).issues.join(),
    ).toContain("недопустимий вихід");
    const valid = [
      { ...stages[1]!, inputs: [{ from: "collect", select: "unmatched_materials" as const }] },
      { ...stages[1]!, stage_id: "store", inputs: [{ from: "extract", select: "input_material" as const }] },
    ];
    expect(buildDag([stages[0]!, ...valid]).issues).toEqual([]);
  });
});
