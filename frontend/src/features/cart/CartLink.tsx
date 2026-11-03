"use client";

import { ShoppingBag } from "lucide-react";
import Link from "next/link";

import { useCart } from "./CartProvider";

/** Cart button in the header with the item count. */
export function CartLink() {
  const { count, ready } = useCart();
  const shown = ready ? count : 0;
  return (
    <Link
      href="/koshyk"
      className="relative grid h-11 w-11 place-items-center rounded-full bg-accent-soft text-rose-deep"
      aria-label={`Кошик, товарів: ${shown}`}
    >
      <ShoppingBag size={21} aria-hidden="true" />
      {shown > 0 && (
        <span className="absolute -right-1 -top-1 min-w-5 rounded-full bg-rose px-1.5 text-center text-xs font-bold leading-5 text-white">
          {shown}
        </span>
      )}
    </Link>
  );
}
