import type { Metadata } from "next";

import { CartView } from "@/features/cart/CartView";

export const metadata: Metadata = {
  title: "Кошик",
  robots: { index: false, follow: true },
};

export default function CartPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-8 sm:px-6">
      <h1 className="mb-6 font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">Кошик</h1>
      <CartView />
    </div>
  );
}
