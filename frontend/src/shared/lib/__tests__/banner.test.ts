import { describe, expect, it } from "vitest";

import type { BannerTheme } from "@/shared/api/storefront";

import {
  BANNER_THEMES,
  fromDateTimeLocal,
  isExternalLink,
  themeClasses,
  toDateTimeLocal,
} from "../banner";

describe("banner helpers", () => {
  it("has a preset for every theme", () => {
    const themes: BannerTheme[] = ["rose", "red", "gold", "dark"];
    for (const theme of themes) {
      expect(themeClasses(theme).section).toBeTruthy();
    }
  });

  it("falls back to rose for an unknown theme", () => {
    expect(themeClasses("unknown" as BannerTheme)).toBe(BANNER_THEMES.rose);
  });

  it("detects external links", () => {
    expect(isExternalLink("https://instagram.com/x")).toBe(true);
    expect(isExternalLink("/kulky")).toBe(false);
  });

  it("round-trips a datetime-local value through an ISO instant", () => {
    const local = "2027-03-08T09:30";
    const iso = fromDateTimeLocal(local);
    expect(iso).toMatch(/Z$/);
    expect(toDateTimeLocal(iso)).toBe(local);
  });
});
