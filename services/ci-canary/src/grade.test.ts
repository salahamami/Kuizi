import { describe, expect, it } from "vitest";
import { passes } from "./grade.js";

describe("passes", () => {
  it("needs an average of 10 out of 20", () => {
    expect(passes(10)).toBe(true);
    expect(passes(9.75)).toBe(false);
  });
});
