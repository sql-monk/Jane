import { describe, expect, it } from "vitest";
import { formatDate, formatDuration, formatInstant, inputInstant } from "./format";

describe("human time diagnostics", () => {
  it("uses Kyiv time with an explicit timezone, including daylight saving", () => {
    expect(formatDate("2026-01-10T10:20:30Z")).toContain("12:20:30");
    expect(formatDate("2026-07-10T10:20:30Z")).toContain("13:20:30");
    expect(formatDate("2026-07-10T10:20:30Z")).toContain("Київ");
    expect(formatInstant("2026-01-10T10:20:30.123Z")).toContain("123 мс");
  });
  it("keeps missing or invalid durations unavailable and preserves precise input instants", () => {
    expect(formatDuration("2026-01-10T10:00:00Z", "2026-01-10T11:01:00Z")).toBe("1 год 1 хв");
    expect(formatDuration(undefined)).toBe("—");
    expect(formatDuration("invalid")).toBe("—");
    expect(formatDuration("2026-01-10T11:00:00Z", "2026-01-10T10:00:00Z")).toBe("—");
    expect(inputInstant("invalid")).toBeUndefined();
    expect(inputInstant("2026-01-10T10:00:00Z")).toBe("2026-01-10T10:00:00.000Z");
  });
});
