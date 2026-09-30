import { describe, expect, it } from "vitest";
import { fixGenerated } from "../../scripts/gen-api.mjs";

describe("gen-api fixGenerated", () => {
  it("drops nested $defs properties and restores discriminator constants", () => {
    const input = [
      "    WebRules: {",
      "      /**",
      "       * @description discriminator enum property added by openapi-typescript",
      "       * @enum {string}",
      "       */",
      '      collector: "WebRules";',
      "      scope: string;",
      "      $defs: {",
      "        Inner: {",
      "          a?: string;",
      "        };",
      "      };",
      "    };",
    ].join("\n");
    const out = fixGenerated(input, new Map([["WebRules.collector", "web"]]));
    expect(out).toContain('collector: "web";');
    expect(out).not.toContain("$defs");
    expect(out).not.toContain('"WebRules"');
    expect(out).toContain("scope: string;");
  });
});
