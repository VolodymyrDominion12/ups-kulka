"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useState,
  type ReactNode,
} from "react";

import {
  cartCount,
  cartLines,
  cartReducer,
  cartTotalKopecks,
  parseStoredCart,
  type CartLine,
  type CartProduct,
  type CartState,
} from "@/shared/lib/cart";

const STORAGE_KEY = "ups_kulka_cart_v1";

interface CartContextValue {
  state: CartState;
  lines: CartLine[];
  count: number;
  totalKopecks: number;
  /** False until the saved cart is read, so the server HTML and first render match. */
  ready: boolean;
  quantityOf: (productId: string) => number;
  add: (product: CartProduct) => void;
  setQuantity: (productId: string, quantity: number) => void;
  remove: (productId: string) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, {});
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let saved: CartState = {};
    try {
      saved = parseStoredCart(window.localStorage.getItem(STORAGE_KEY));
    } catch {
      saved = {};
    }
    dispatch({ type: "restore", state: saved });
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // Private mode or full storage: the cart still works for this visit.
    }
  }, [state, ready]);

  const value = useMemo<CartContextValue>(
    () => ({
      state,
      lines: cartLines(state),
      count: cartCount(state),
      totalKopecks: cartTotalKopecks(state),
      ready,
      quantityOf: (id) => state[id]?.quantity ?? 0,
      add: (product) => dispatch({ type: "add", product }),
      setQuantity: (productId, quantity) => dispatch({ type: "setQuantity", productId, quantity }),
      remove: (productId) => dispatch({ type: "remove", productId }),
      clear: () => dispatch({ type: "clear" }),
    }),
    [state, ready],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const value = useContext(CartContext);
  if (!value) throw new Error("useCart must be used inside <CartProvider>");
  return value;
}
