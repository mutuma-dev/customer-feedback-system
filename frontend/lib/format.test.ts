// Tests for the text helpers (time ago, source, verdict names).
import { describe, expect, it } from "vitest";
import { categoryLabel, kindLabel, sourceLabel, timeAgo } from "./format";

// A fixed "now" so the results never depend on the real clock.
const now = new Date("2026-11-13T12:00:00Z");

describe("timeAgo", () => {
  it("says 'just now' for under a minute (and for times in the future)", () => {
    expect(timeAgo("2026-11-13T11:59:30Z", now)).toBe("just now");
    expect(timeAgo("2026-11-13T12:05:00Z", now)).toBe("just now");
  });
  it("counts minutes, hours and days", () => {
    expect(timeAgo("2026-11-13T11:55:00Z", now)).toBe("5 min ago");
    expect(timeAgo("2026-11-13T09:00:00Z", now)).toBe("3 h ago");
    expect(timeAgo("2026-11-10T12:00:00Z", now)).toBe("3 d ago");
  });
  it("shows the date once it is older than a month", () => {
    expect(timeAgo("2026-09-01T12:00:00Z", now)).toBe("2026-09-01");
  });
});

describe("labels", () => {
  it("names where a response came from", () => {
    expect(sourceLabel("sms")).toBe("SMS reply");
    expect(sourceLabel("web")).toBe("Web form");
  });
  it("names the customer type", () => {
    expect(kindLabel("painter")).toBe("Painter");
    expect(kindLabel("buyer")).toBe("Paint buyer");
  });
  it("turns the brief's verdicts into plain words", () => {
    expect(categoryLabel("detractor")).toBe("Unhappy");
    expect(categoryLabel("passive")).toBe("Neutral");
    expect(categoryLabel("promoter")).toBe("Happy");
  });
});
