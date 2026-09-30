import { describe, expect, it } from "vitest";
import { SCHEMAS, validateAgainst } from "./schema";
import { openapiExample } from "../test/contracts";

describe("contract schema validation", () => {
  it.each([
    ["task-catalog", SCHEMAS.task],
    ["task-price-check", SCHEMAS.task],
    ["task-telegram", SCHEMAS.task],
    ["source-shop", SCHEMAS.source],
    ["source-telegram", SCHEMAS.source],
    ["rules-web-shop", SCHEMAS.collectorRules],
    ["rules-web-news", SCHEMAS.collectorRules],
    ["rules-telegram", SCHEMAS.collectorRules],
    ["platform-limits-dev", SCHEMAS.platformLimits],
    ["connection-pg", SCHEMAS.connection],
    ["manifest-extractor", SCHEMAS.manifest],
    ["manifest-rules", SCHEMAS.manifest],
  ])("accepts contract example %s", (name, schema) => {
    expect(validateAgainst(schema, openapiExample(name))).toEqual([]);
  });

  it("rejects unknown fields in strict configuration documents", () => {
    const task = { ...openapiExample<Record<string, unknown>>("task-catalog"), unexpected: 1 };
    const issues = validateAgainst(SCHEMAS.task, task);
    expect(issues.map((i) => i.message).join(" ")).toContain("unexpected");
  });

  it("rejects a raw secret value in secret_refs", () => {
    const issues = validateAgainst(SCHEMAS.connection, {
      connection_id: "pg",
      kind: "postgresql",
      secret_refs: { password: "hunter2" },
    });
    expect(issues.length).toBeGreaterThan(0);
  });

  it("validates each strategy type template", async () => {
    const { STRATEGY_TEMPLATES } = await import("../pages/RulesEditorPage");
    for (const template of Object.values(STRATEGY_TEMPLATES)) {
      expect(validateAgainst(SCHEMAS.strategy, template)).toEqual([]);
    }
  });
});
