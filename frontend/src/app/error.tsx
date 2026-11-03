"use client";

import { SHOP } from "@/shared/config/shop";

/** Shown when a page fails, e.g. the catalogue API is unreachable. */
export default function ShopError({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="mx-auto max-w-xl px-4 py-20 text-center sm:px-6">
      <h1 className="font-display text-3xl font-bold">Каталог тимчасово не завантажився</h1>
      <p className="mt-3 text-[#3a3a3a]">
        Спробуйте ще раз за хвилину. Замовити можна й телефоном:{" "}
        <a href={`tel:${SHOP.phone}`} className="font-semibold text-ink">
          {SHOP.phoneLabel}
        </a>
        .
      </p>
      <button
        type="button"
        onClick={reset}
        className="mt-8 inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white"
      >
        Спробувати ще раз
      </button>
    </div>
  );
}
