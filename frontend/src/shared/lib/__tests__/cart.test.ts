import { describe, expect, it } from "vitest";

import {
  MAX_LINES,
  cartCount,
  cartReducer,
  cartTotalKopecks,
  parseStoredCart,
  type CartProduct,
  type CartState,
} from "../cart";

const heart: CartProduct = { id: "h", slug: "sertse", name: "Серце", priceKopecks: 15500, imageUrl: null };
const box: CartProduct = { id: "b", slug: "korobka", name: "Коробка", priceKopecks: 200000, imageUrl: "/m/1.webp" };

describe("cartReducer", () => {
  it("adds and increments, totals use kopecks", () => {
    let s: CartState = {};
    s = cartReducer(s, { type: "add", product: heart });
    s = cartReducer(s, { type: "add", product: heart });
    s = cartReducer(s, { type: "add", product: box });
    expect(cartCount(s)).toBe(3);
    expect(cartTotalKopecks(s)).toBe(15500 * 2 + 200000);
  });

  it("caps quantity at 99 and removes at zero", () => {
    let s = cartReducer({}, { type: "add", product: heart });
    s = cartReducer(s, { type: "setQuantity", productId: "h", quantity: 500 });
    expect(s.h.quantity).toBe(99);
    s = cartReducer(s, { type: "add", product: heart });
    expect(s.h.quantity).toBe(99);
    s = cartReducer(s, { type: "setQuantity", productId: "h", quantity: 0 });
    expect(s).toEqual({});
  });

  it("ignores quantity changes for unknown products", () => {
    const s = cartReducer({}, { type: "setQuantity", productId: "x", quantity: 3 });
    expect(s).toEqual({});
  });

  it("does not exceed the server limit of different products", () => {
    let s: CartState = {};
    for (let i = 0; i < MAX_LINES + 5; i++) {
      s = cartReducer(s, { type: "add", product: { ...heart, id: `p${i}` } });
    }
    expect(Object.keys(s)).toHaveLength(MAX_LINES);
  });

  it("removes, clears and restores", () => {
    let s = cartReducer({}, { type: "add", product: heart });
    s = cartReducer(s, { type: "add", product: box });
    s = cartReducer(s, { type: "remove", productId: "h" });
    expect(Object.keys(s)).toEqual(["b"]);
    const saved = s;
    s = cartReducer(s, { type: "clear" });
    expect(s).toEqual({});
    expect(cartReducer(s, { type: "restore", state: saved })).toBe(saved);
  });
});

describe("parseStoredCart", () => {
  it("restores a valid cart", () => {
    const raw = JSON.stringify({ h: { product: heart, quantity: 2 } });
    expect(parseStoredCart(raw)).toEqual({ h: { product: heart, quantity: 2 } });
  });

  it.each([null, "", "not json", "[1,2]", "42"])("returns empty for %s", (raw) => {
    expect(parseStoredCart(raw)).toEqual({});
  });

  it("drops malformed lines and clamps quantity", () => {
    const raw = JSON.stringify({
      ok: { product: box, quantity: 250.7 },
      noPrice: { product: { ...heart, priceKopecks: "1" }, quantity: 1 },
      zero: { product: heart, quantity: 0 },
    });
    expect(parseStoredCart(raw)).toEqual({ b: { product: box, quantity: 99 } });
  });
});
