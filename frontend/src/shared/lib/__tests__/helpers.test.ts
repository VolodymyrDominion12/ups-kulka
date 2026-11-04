import { describe, expect, it } from "vitest";

import { groupTagSections, sortTags } from "@/widgets/TagChips";
import { responsiveImage } from "../images";
import { discountPercent, formatUah } from "../money";
import { parseOnSale, parseOrderNumber, parsePage, parseQuery, parseSort } from "../paging";
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

  it("parses sort, sale and query filters", () => {
    expect(parseSort("price_asc")).toBe("price_asc");
    expect(parseSort("price_desc")).toBe("price_desc");
    expect(parseSort("bogus")).toBe("newest");
    expect(parseSort(undefined)).toBe("newest");

    expect(parseOnSale("true")).toBe(true);
    expect(parseOnSale("1")).toBe(true);
    expect(parseOnSale("false")).toBe(false);
    expect(parseOnSale(undefined)).toBe(false);

    expect(parseQuery("  єдиноріг  ")).toBe("  єдиноріг  ");
    expect(parseQuery(undefined)).toBe("");
    expect(parseQuery("x".repeat(200))).toHaveLength(120);
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

describe("TagChips grouping", () => {
  const sampleTags = [
    { id: "1", group: "color", slug: "pastelni", name: "Пастельні тони" },
    { id: "2", group: "recipient", slug: "dlia-mamy", name: "Для мами" },
    { id: "3", group: "occasion", slug: "den-narodzhennia", name: "День народження" },
    { id: "4", group: "type", slug: "fontany", name: "Фонтани та букети" },
  ];

  it("sorts tags by group priority and Ukrainian locale name", () => {
    const sorted = sortTags(sampleTags);
    expect(sorted.map((t) => t.slug)).toEqual([
      "dlia-mamy",
      "den-narodzhennia",
      "fontany",
      "pastelni",
    ]);
  });

  it("buckets tags into compact dropdown sections and omits empty ones", () => {
    const sections = groupTagSections(sampleTags);
    expect(sections.map((s) => ({ id: s.id, slugs: s.items.map((t) => t.slug) }))).toEqual([
      { id: "occasion", slugs: ["dlia-mamy", "den-narodzhennia"] },
      { id: "theme", slugs: ["fontany"] },
      { id: "color", slugs: ["pastelni"] },
    ]);

    const onlyColors = groupTagSections([sampleTags[0]]);
    expect(onlyColors.map((s) => s.id)).toEqual(["color"]);
  });
});

