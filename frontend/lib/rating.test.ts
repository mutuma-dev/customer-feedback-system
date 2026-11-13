import { describe, expect, it } from "vitest";
import { labelFor } from "./rating";

describe("labelFor", () => {
  it("labels ratings 1-5", () => {
    expect(labelFor(1)).toBe("Poor");
    expect(labelFor(3)).toBe("Good");
    expect(labelFor(5)).toBe("Excellent");
  });
  it("prompts when nothing is chosen or the value is invalid", () => {
    expect(labelFor(null)).toBe("Select a rating");
    expect(labelFor(0)).toBe("Select a rating");
    expect(labelFor(6)).toBe("Select a rating");
  });
});
