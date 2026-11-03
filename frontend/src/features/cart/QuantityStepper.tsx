"use client";

import { MAX_QUANTITY } from "@/shared/lib/cart";

import { useCart } from "./CartProvider";

interface Props {
  productId: string;
  productName: string;
  wide?: boolean;
}

export function QuantityStepper({ productId, productName, wide = false }: Props) {
  const { quantityOf, setQuantity } = useCart();
  const quantity = quantityOf(productId);
  return (
    <div
      className={`inline-flex h-11 items-center rounded-full bg-accent-soft ${
        wide ? "h-12 w-full justify-between" : ""
      }`}
      role="group"
      aria-label={`Кількість: ${productName}`}
    >
      <button
        type="button"
        className="h-full w-11 rounded-full text-xl text-rose-deep"
        onClick={() => setQuantity(productId, quantity - 1)}
        aria-label="Менше"
      >
        −
      </button>
      <output className="min-w-6 text-center font-bold tabular-nums" aria-live="polite">
        {quantity}
      </output>
      <button
        type="button"
        className="h-full w-11 rounded-full text-xl text-rose-deep disabled:opacity-40"
        onClick={() => setQuantity(productId, quantity + 1)}
        disabled={quantity >= MAX_QUANTITY}
        aria-label="Більше"
      >
        +
      </button>
    </div>
  );
}
