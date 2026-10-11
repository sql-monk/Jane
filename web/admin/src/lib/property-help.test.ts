import { describe, expect, it } from "vitest";
import type { Stage } from "../api/types";
import { describeSchemaPath, describeStageProperty } from "./property-help";

const collect: Stage = {
  stage_id: "collect",
  kind: "collect",
  collector: { collector: "web", mode: "full" },
};
const handler: Stage = {
  stage_id: "store",
  kind: "handler",
  handler: { package_id: "storage-files", version: "1.0.0" },
  params: { format: { raw: "original" } },
  inputs: [{ from: "collect", when: { all: [{ field: "result.status", op: "eq", value: "succeeded" }] } }],
  bindings: [{ url_patterns: [{ value: "example.test/**", type: "glob" }] }],
};

describe("stage property descriptions", () => {
  it("describes collector mode from contract metadata including enum and default", () => {
    expect(describeStageProperty(collect, "$.collector.mode")).toContain("продовжити від збереженого стану");
    expect(describeStageProperty(collect, "$.collector.mode")).toContain('"full", "incremental"');
    expect(describeStageProperty(collect, "$.collector.mode")).toContain('За замовчуванням: "full"');
    expect(describeStageProperty(collect, "$.collector.rules")).toContain("правила джерела");
    expect(
      describeSchemaPath({ properties: { mode: { enum: ["full", "incremental"] } } }, "$.mode", {
        value: { mode: "mistyped" },
      }),
    ).toContain("incremental");
  });
  it("follows cross-contract refs and arrays at any index", () => {
    expect(describeStageProperty(handler, "$.bindings[0].url_patterns[0].type")).toContain('"glob", "regex"');
    expect(describeStageProperty(handler, "$.bindings[9].url_patterns[23].value")).toContain(
      "вкладені шляхи",
    );
    expect(describeStageProperty(handler, "$.limits.concurrency.max_parallel_stage_items")).toContain(
      "одночасно",
    );
    expect(describeStageProperty(handler, "$.inputs[0].when.all[0].op")).toContain('"eq", "ne"');
  });
  it("uses only selected package metadata for nested params and preserves package namespace", () => {
    const schema = {
      type: "object",
      properties: {
        prefix: { type: "string", description: "Префікс ключів цього сховища." },
        format: {
          type: "object",
          properties: { raw: { type: "string", enum: ["original", "html", "json"] } },
        },
        steps: { type: "array", items: { $ref: "#/$defs/Step" } },
      },
      $defs: { Step: { type: "object", properties: { label: { type: "string", title: "Назва кроку" } } } },
    };
    expect(describeStageProperty(handler, "$.params.prefix", schema)).toBe("Префікс ключів цього сховища.");
    expect(describeStageProperty(handler, "$.params.format.raw", schema)).toBe(
      'Допустимі значення: "original", "html", "json".',
    );
    expect(describeStageProperty(handler, "$.params.steps[1].label", schema)).toBe("Назва кроку");
    expect(describeStageProperty(handler, "$.params.prefix")).toBeUndefined();
    expect(
      describeStageProperty(handler, "$.params.prefix", { properties: { another: { description: "Інше" } } }),
    ).toBeUndefined();
  });
  it("does not guess unknown fields or follow unavailable or cyclic refs", () => {
    expect(describeStageProperty(collect, "$.collector.mistyped")).toBeUndefined();
    expect(describeSchemaPath({ $ref: "missing.schema.json" }, "$.name")).toBeUndefined();
    expect(
      describeSchemaPath({ $ref: "#/$defs/Loop", $defs: { Loop: { $ref: "#/$defs/Loop" } } }, "$.name"),
    ).toBeUndefined();
    expect(
      describeSchemaPath({ properties: { name: { description: "Ім'я" } } }, "$.name[bad]"),
    ).toBeUndefined();
  });
  it("handles escaped local pointers and tuple array schemas", () => {
    const schema = {
      properties: { items: { type: "array", prefixItems: [{ $ref: "#/$defs/a~1b~0c" }] } },
      $defs: { "a/b~c": { description: "Перший елемент", default: false } },
    };
    expect(describeSchemaPath(schema, "$.items[0]")).toBe("Перший елемент За замовчуванням: false.");
  });
  it("uses actual field tokens for names containing dots or brackets", () => {
    const schema = {
      properties: {
        "a.b": { description: "Літеральна крапка" },
        a: { properties: { b: { description: "Вкладене поле" } } },
        "x[0]": { description: "Літеральні дужки" },
      },
    };
    expect(describeStageProperty(handler, "$.params.a.b", schema, ["params", "a.b"])).toBe(
      "Літеральна крапка",
    );
    expect(describeStageProperty(handler, "$.params.a.b", schema, ["params", "a", "b"])).toBe(
      "Вкладене поле",
    );
    expect(describeStageProperty(handler, "$.params.x[0]", schema, ["params", "x[0]"])).toBe(
      "Літеральні дужки",
    );
    expect(describeStageProperty(collect, "$.collector.mode", undefined, ["collector.mode"])).toBeUndefined();
  });
  it("uses verified file-storage fallback copy only for that package and existing schema fields", () => {
    const stage: Stage = { ...handler, handler: { package_id: "jane.storage-files", version: "1.0.0" } };
    const schema = {
      properties: {
        prefix: { description: "Підкаталог усередині base_path." },
        format: {
          properties: {
            raw: { enum: ["original", "html", "json"] },
            entities: { enum: ["json", "jsonl"] },
          },
        },
      },
    };
    expect(describeStageProperty(stage, "$.params.format", schema)).toContain("Формати збереження");
    expect(describeStageProperty(stage, "$.params.format.raw", schema)).toContain("original — байти як є");
    expect(describeStageProperty(stage, "$.params.format.entities", schema)).toContain(
      "історія як JSON Lines",
    );
    expect(describeStageProperty(stage, "$.params.prefix", schema)).toContain("той самий prefix");
    expect(describeStageProperty(handler, "$.params.prefix", schema)).toBe("Підкаталог усередині base_path.");
    expect(describeStageProperty(handler, "$.params.format.raw", schema)).not.toContain("байти як є");
    expect(
      describeStageProperty(stage, "$.params.format.raw", { properties: { something_else: {} } }),
    ).toBeUndefined();
    expect(
      describeStageProperty(stage, "$.params.format.raw", {
        properties: { format: { properties: { raw: { description: "Опис цієї версії пакета." } } } },
      }),
    ).toBe("Опис цієї версії пакета.");
  });
  it("does not pick an arbitrary description for ambiguous alternatives", () => {
    const schema = {
      oneOf: [
        { properties: { name: { description: "Перше" } } },
        { properties: { name: { description: "Друге" } } },
      ],
    };
    expect(describeSchemaPath(schema, "$.name")).toBeUndefined();
    expect(
      describeSchemaPath(
        { oneOf: [{ properties: { name: { description: "Перше" } } }, { properties: { name: {} } }] },
        "$.name",
      ),
    ).toBeUndefined();
    expect(
      describeSchemaPath(
        {
          oneOf: [
            { properties: { kind: { const: "one" }, name: { description: "Перше" } } },
            { properties: { kind: { const: "two" }, name: { description: "Друге" } } },
          ],
        },
        "$.name",
        { value: { kind: "two" } },
      ),
    ).toBe("Друге");
  });
});
