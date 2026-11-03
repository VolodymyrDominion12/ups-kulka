import type { Metadata } from "next";

import { CheckoutForm } from "@/features/checkout/CheckoutForm";

export const metadata: Metadata = {
  title: "Оформлення замовлення",
  robots: { index: false, follow: false },
};

export default function CheckoutPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-8 sm:px-6">
      <h1 className="mb-6 font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">
        Оформлення
      </h1>
      <CheckoutForm />
    </div>
  );
}
