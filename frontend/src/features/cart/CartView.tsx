"use client";

import Link from "next/link";

import { formatUah } from "@/shared/lib/money";

import { useCart } from "./CartProvider";
import { QuantityStepper } from "./QuantityStepper";

export function CartView() {
  const { lines, totalKopecks, ready, remove } = useCart();

  if (!ready) {
    return <div className="h-40 animate-pulse rounded-panel bg-accent-soft" aria-label="Завантажуємо кошик" />;
  }

  if (lines.length === 0) {
    return (
      <div className="rounded-panel bg-white p-8 text-center">
        <p className="font-display text-xl font-bold">Кошик порожній</p>
        <p className="mt-2 text-muted">Додайте композицію з каталогу, і вона зʼявиться тут.</p>
        <Link href="/kulky" className="mt-6 inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white">
          До каталогу
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_340px] lg:items-start">
      <ul className="divide-y divide-line rounded-panel bg-white px-5 sm:px-7">
        {lines.map(({ product, quantity }) => (
          <li key={product.id} className="grid grid-cols-[72px_1fr] items-center gap-4 py-4 sm:grid-cols-[88px_1fr_auto]">
            <Link href={`/tovar/${product.slug}`} className="block aspect-square overflow-hidden rounded-2xl bg-accent-soft">
              {product.imageUrl && (
                <img src={product.imageUrl} alt="" width={88} height={88} className="h-full w-full object-cover" />
              )}
            </Link>
            <div className="min-w-0">
              <Link href={`/tovar/${product.slug}`} className="font-semibold hover:text-rose-deep">
                {product.name}
              </Link>
              <p className="mt-1 font-bold tabular-nums text-rose-deep">
                {formatUah(product.priceKopecks * quantity)}
              </p>
            </div>
            <div className="col-span-2 flex items-center justify-between gap-3 sm:col-span-1 sm:flex-col sm:items-end">
              <QuantityStepper productId={product.id} productName={product.name} />
              <button type="button" onClick={() => remove(product.id)} className="text-sm text-muted underline">
                Видалити
              </button>
            </div>
          </li>
        ))}
      </ul>
      <aside className="grid gap-4 rounded-panel bg-white p-5 sm:p-7 lg:sticky lg:top-24">
        <div className="flex justify-between text-lg font-extrabold">
          <span>За товари</span>
          <span className="tabular-nums">{formatUah(totalKopecks)}</span>
        </div>
        <p className="-mt-2 text-sm text-muted">Остаточну суму підтвердимо під час оформлення.</p>
        <Link
          href="/oformlennia"
          className="inline-flex h-12 items-center justify-center rounded-full bg-ink font-bold text-white transition hover:bg-rose-deep"
        >
          Оформити замовлення
        </Link>
        <Link href="/kulky" className="text-center text-sm font-semibold text-rose-deep">
          Продовжити покупки
        </Link>
      </aside>
    </div>
  );
}
