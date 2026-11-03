/**
 * Cart state, kept in the browser. Prices here are a snapshot for display;
 * the order total is always computed by the server from the catalogue.
 */

export const MAX_QUANTITY = 99;
export const MAX_LINES = 50;

export interface CartProduct {
  id: string;
  slug: string;
  name: string;
  priceKopecks: number;
  imageUrl: string | null;
}

export interface CartLine {
  product: CartProduct;
  quantity: number;
}

export type CartState = Record<string, CartLine>;

export type CartAction =
  | { type: "add"; product: CartProduct }
  | { type: "setQuantity"; productId: string; quantity: number }
  | { type: "remove"; productId: string }
  | { type: "clear" }
  | { type: "restore"; state: CartState };

export function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case "add": {
      const current = state[action.product.id];
      if (!current && Object.keys(state).length >= MAX_LINES) return state;
      const quantity = Math.min(MAX_QUANTITY, (current?.quantity ?? 0) + 1);
      return { ...state, [action.product.id]: { product: action.product, quantity } };
    }
    case "setQuantity": {
      const current = state[action.productId];
      if (!current) return state;
      if (action.quantity <= 0) return omit(state, action.productId);
      const quantity = Math.min(MAX_QUANTITY, Math.floor(action.quantity));
      return { ...state, [action.productId]: { ...current, quantity } };
    }
    case "remove":
      return omit(state, action.productId);
    case "clear":
      return {};
    case "restore":
      return action.state;
  }
}

function omit(state: CartState, productId: string): CartState {
  const next = { ...state };
  delete next[productId];
  return next;
}

export function cartLines(state: CartState): CartLine[] {
  return Object.values(state);
}

export function cartCount(state: CartState): number {
  return cartLines(state).reduce((sum, line) => sum + line.quantity, 0);
}

export function cartTotalKopecks(state: CartState): number {
  return cartLines(state).reduce((sum, l) => sum + l.quantity * l.product.priceKopecks, 0);
}

/** Restores a saved cart, dropping anything malformed (old versions, manual edits). */
export function parseStoredCart(raw: string | null): CartState {
  if (!raw) return {};
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return {};
  }
  if (!data || typeof data !== "object") return {};
  const result: CartState = {};
  for (const value of Object.values(data as Record<string, unknown>)) {
    const line = value as Partial<CartLine> | null;
    const p = line?.product as Partial<CartProduct> | undefined;
    if (
      p &&
      typeof p.id === "string" &&
      typeof p.slug === "string" &&
      typeof p.name === "string" &&
      typeof p.priceKopecks === "number" &&
      typeof line?.quantity === "number" &&
      line.quantity >= 1
    ) {
      result[p.id] = {
        product: {
          id: p.id,
          slug: p.slug,
          name: p.name,
          priceKopecks: p.priceKopecks,
          imageUrl: typeof p.imageUrl === "string" ? p.imageUrl : null,
        },
        quantity: Math.min(MAX_QUANTITY, Math.floor(line.quantity)),
      };
    }
  }
  return result;
}
