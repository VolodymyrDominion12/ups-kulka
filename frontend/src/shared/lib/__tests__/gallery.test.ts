import { describe, expect, it } from "vitest";

import {
  appendMediaIds,
  cycleIndex,
  largestImageSrc,
  moveMediaToFront,
  removeMediaId,
  reorderMediaIds,
} from "../gallery";

describe("cycleIndex", () => {
  it("wraps forward and backward", () => {
    expect(cycleIndex(0, 5, 1)).toBe(1);
    expect(cycleIndex(4, 5, 1)).toBe(0);
    expect(cycleIndex(0, 5, -1)).toBe(4);
  });

  it("stays at 0 for a single item", () => {
    expect(cycleIndex(0, 1, 1)).toBe(0);
    expect(cycleIndex(0, 0, -1)).toBe(0);
  });
});

describe("reorderMediaIds", () => {
  const ids = ["a", "b", "c", "d"];

  it("moves an item forward", () => {
    expect(reorderMediaIds(ids, 0, 2)).toEqual(["b", "c", "a", "d"]);
  });

  it("moves an item backward", () => {
    expect(reorderMediaIds(ids, 3, 1)).toEqual(["a", "d", "b", "c"]);
  });

  it("keeps order on a no-op or out-of-range move", () => {
    expect(reorderMediaIds(ids, 1, 1)).toEqual(ids);
    expect(reorderMediaIds(ids, -1, 2)).toEqual(ids);
    expect(reorderMediaIds(ids, 2, 99)).toEqual(ids);
  });

  it("does not mutate the input", () => {
    reorderMediaIds(ids, 0, 3);
    expect(ids).toEqual(["a", "b", "c", "d"]);
  });
});

describe("moveMediaToFront", () => {
  it("promotes a photo to the cover position", () => {
    expect(moveMediaToFront(["a", "b", "c"], 2)).toEqual(["c", "a", "b"]);
    expect(moveMediaToFront(["a", "b", "c"], 0)).toEqual(["a", "b", "c"]);
  });
});

describe("removeMediaId", () => {
  it("removes the photo at the given index", () => {
    expect(removeMediaId(["a", "b", "c"], 1)).toEqual(["a", "c"]);
    expect(removeMediaId(["a"], 0)).toEqual([]);
  });

  it("leaves the list unchanged for a bad index", () => {
    expect(removeMediaId(["a", "b"], 5)).toEqual(["a", "b"]);
  });
});

describe("appendMediaIds", () => {
  it("appends new ids without duplicating existing ones", () => {
    expect(appendMediaIds(["a", "b"], ["c", "a"])).toEqual(["a", "b", "c"]);
  });

  it("caps the total at the limit", () => {
    expect(appendMediaIds(["1", "2", "3"], ["4", "5", "6", "7", "8", "9", "10", "11"])).toEqual([
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
    ]);
  });
});

describe("largestImageSrc", () => {
  it("prefers the largest variant", () => {
    const variants = { "320w": "/320", "640w": "/640", "1280w": "/1280", original: "/orig" };
    expect(largestImageSrc(variants)).toBe("/1280");
  });

  it("falls back to original when no sized variants exist", () => {
    expect(largestImageSrc({ original: "/orig" })).toBe("/orig");
  });

  it("returns null for an empty map", () => {
    expect(largestImageSrc({})).toBeNull();
  });
});
