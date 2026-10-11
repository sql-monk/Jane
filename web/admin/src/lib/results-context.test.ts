import { describe, it, expect } from "vitest";
import { resultsHref, entityTypeLabel } from "./results-context";

describe("honest storage result links", () => {
  it("preserves actual key and scope without inferring provenance", () => {
    const url = new URL(
      resultsHref({
        connectionId: "results-pg",
        entityType: "offer",
        scope: "магазин",
        key: 'shop|{"url":"https://example/a?x=1&y=2"}',
      }),
      "https://jane.test",
    );
    expect(url.searchParams.get("scope")).toBe("магазин");
    expect(url.searchParams.get("key")).toContain("x=1&y=2");
    expect(url.searchParams.has("run_id")).toBe(false);
    expect(url.searchParams.has("source_id")).toBe(false);
    expect(resultsHref()).toBe("/results");
  });
  it("labels common business entities and preserves unknown codes", () => {
    expect(entityTypeLabel("offer")).toBe("Пропозиції магазинів");
    expect(entityTypeLabel("product_book")).toBe("Товари: книжки");
    expect(entityTypeLabel("ad_realty")).toBe("Оголошення: нерухомість");
    expect(entityTypeLabel("event_custom")).toBe("event_custom");
  });
});
