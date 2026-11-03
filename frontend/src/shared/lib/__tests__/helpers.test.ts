import { describe, expect, it } from "vitest";

import { responsiveImage } from "../images";
import { discountPercent, formatUah } from "../money";
import { parseOrderNumber, parsePage } from "../paging";
import { normalizeUaPhone } from "../phone";
import { attributionFromUrl, parseStoredAttribution } from "../utm";

describe("normalizeUaPhone (same rule as the backend)", () => {
  it.each(["093 111 22 33", "0931112233", "+380931112233", "38 (093) 111-22-33"])("%s", (raw) => {
    expect(normalizeUaPhone(raw)).toBe("+380931112233");
  });

  it.each(["12345", "+44 20 7946 0958", "", "093111223"])("rejects %s", (raw) => {
    expect(normalizeUaPhone(raw)).toBeNull();
  });
});

describe("money", () => {
  it("formats kopecks", () => {
    expect(formatUah(288500).replace(/\s/g, " ")).toBe("2 885 грн");
    expect(formatUah(15550)).toBe("155,50 грн");
  });

  it("computes discount only for a real old price", () => {
    expect(discountPercent(390000, 430000)).toBe(9);
    expect(discountPercent(25000, 25000)).toBe(0);
    expect(discountPercent(25000, null)).toBe(0);
  });
});

describe("responsiveImage", () => {
  const variants = {
    "320w": "/media/a/320w.webp",
    "960w": "/media/a/960w.webp",
    "640w": "/media/a/640w.webp",
    original: "/media/a/original.webp",
  };

  it("builds a sorted srcset and picks the first variant at least as wide as needed", () => {
    expect(responsiveImage({ variants })).toEqual({
      src: "/media/a/640w.webp",
      srcSet: "/media/a/320w.webp 320w, /media/a/640w.webp 640w, /media/a/960w.webp 960w",
    });
    expect(responsiveImage({ variants }, 2000)?.src).toBe("/media/a/960w.webp");
  });

  it("falls back to the original or nothing", () => {
    expect(responsiveImage({ variants: { original: "/o.webp" } })).toEqual({ src: "/o.webp", srcSet: "" });
    expect(responsiveImage({ variants: {} })).toBeNull();
  });
});

describe("paging", () => {
  const pages: [string | string[] | undefined, number][] = [
    [undefined, 1],
    ["3", 3],
    ["0", 1],
    ["-2", 1],
    ["2.5", 1],
    ["abc", 1],
    [["4", "5"], 4],
  ];
  it.each(pages)("parsePage(%j) = %i", (value, page) => {
    expect(parsePage(value)).toBe(page);
  });

  it("parses order numbers strictly", () => {
    expect(parseOrderNumber("1001")).toBe(1001);
    expect(parseOrderNumber("0")).toBeNull();
    expect(parseOrderNumber("10a")).toBeNull();
    expect(parseOrderNumber(undefined)).toBeNull();
  });
});

describe("utm", () => {
  it("reads marks and the landing path", () => {
    const url = new URL("https://shop.example/kulky/dlia-nei?utm_source=instagram&utm_campaign=8-bereznia&promo=VESNA");
    expect(attributionFromUrl(url)).toEqual({
      utm_source: "instagram",
      utm_medium: null,
      utm_campaign: "8-bereznia",
      promo_code: "VESNA",
      landing_page: "/kulky/dlia-nei",
    });
  });

  it("ignores visits without marks", () => {
    expect(attributionFromUrl(new URL("https://shop.example/?page=2"))).toBeNull();
  });

  it("clips overlong values to API limits", () => {
    const url = new URL(`https://shop.example/?utm_source=${"x".repeat(500)}`);
    expect(attributionFromUrl(url)?.utm_source).toHaveLength(120);
  });

  it("parses stored attribution defensively", () => {
    expect(parseStoredAttribution("{bad")).toBeNull();
    expect(parseStoredAttribution(JSON.stringify({ utm_source: "tg", promo_code: 5 }))).toEqual({
      utm_source: "tg",
      utm_medium: null,
      utm_campaign: null,
      promo_code: null,
      landing_page: null,
    });
  });
});
