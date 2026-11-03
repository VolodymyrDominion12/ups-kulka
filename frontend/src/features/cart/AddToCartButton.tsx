"use client";

import type { CartProduct } from "@/shared/lib/cart";
import { formatUah } from "@/shared/lib/money";

import { useCart } from "./CartProvider";
import { QuantityStepper } from "./QuantityStepper";

interface Props {
  product: CartProduct;
  /** Card version: round "+" on desktop, full-width "+ Додати" on phones. */
  compact?: boolean;
}

export function AddToCartButton({ product, compact = false }: Props) {
  const { quantityOf, add, ready } = useCart();
  const quantity = ready ? quantityOf(product.id) : 0;

  if (quantity > 0) {
    return (
      <div className={compact ? "w-full shrink-0 sm:w-auto" : "w-full"}>
        <QuantityStepper productId={product.id} productName={product.name} wide={!compact} />
      </div>
    );
  }

  if (compact) {
    return (
      <button
        type="button"
        onClick={() => add(product)}
        aria-label={`Додати «${product.name}» в кошик`}
        className="inline-flex h-11 w-full shrink-0 items-center justify-center gap-1.5 rounded-full bg-ink px-4 text-[15px] font-bold text-white transition hover:bg-rose-deep active:scale-95 sm:w-11 sm:px-0 sm:text-xl"
      >
        <span aria-hidden="true">+</span>
        <span className="sm:hidden">Додати</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={() => add(product)}
      className="inline-flex h-12 w-full items-center justify-center rounded-full bg-ink px-6 font-bold text-white transition hover:bg-rose-deep active:scale-[0.98]"
    >
      Додати в кошик за {formatUah(product.priceKopecks)}
    </button>
  );
}
