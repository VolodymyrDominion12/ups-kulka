import { describe, expect, it } from "vitest";

import type { BannerTheme } from "@/shared/api/storefront";

import {
  BANNER_THEMES,
  fromDateTimeLocal,
  isExternalLink,
  themeClasses,
  toDateTimeLocal,
  withBannerAttribution,
} from "../banner";

describe("banner helpers", () => {
  it("has a preset for every theme", () => {
    const themes: BannerTheme[] = ["rose", "red", "gold", "dark"];
    for (const theme of themes) {
      expect(themeClasses(theme).section).toBeTruthy();
      expect(themeClasses(theme).ribbon).toBeTruthy();
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

  it("appends campaign attribution to internal links and leaves external or preview links untouched", () => {
    expect(withBannerAttribution("/kulky/8-bereznia", "camp-1", "image")).toBe(
      "/kulky/8-bereznia?utm_source=home_banner&utm_medium=image&utm_campaign=camp-1",
    );
    expect(withBannerAttribution("/kulky", "preview", "image")).toBe("/kulky");
    expect(withBannerAttribution("https://instagram.com/x", "camp-1", "image")).toBe(
      "https://instagram.com/x",
    );
  });
});
