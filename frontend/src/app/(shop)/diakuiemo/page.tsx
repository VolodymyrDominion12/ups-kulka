import type { Metadata } from "next";
import Link from "next/link";

import { SHOP } from "@/shared/config/shop";
import { parseOrderNumber } from "@/shared/lib/paging";

export const metadata: Metadata = {
  title: "Дякуємо за замовлення",
  robots: { index: false, follow: false },
};

type SearchParams = Promise<{ order?: string | string[] }>;

export default async function ThankYouPage({ searchParams }: { searchParams: SearchParams }) {
  const number = parseOrderNumber((await searchParams).order);

  return (
    <div className="mx-auto max-w-xl px-4 pb-20 pt-14 text-center sm:px-6">
      <span className="balloon-icon mx-auto h-[84px] w-[72px] text-4xl" aria-hidden="true">
        🎈
      </span>
      <h1 className="mt-5 font-display text-[clamp(28px,5vw,40px)] font-bold tracking-tight">
        {number ? `Замовлення №${number} прийнято` : "Замовлення прийнято"}
      </h1>
      <p className="mt-3 text-lg text-[#3a3a3a]">
        Менеджер зателефонує найближчим часом, щоб підтвердити деталі. Якщо ви оплатили онлайн,
        підтвердження оплати ми отримаємо автоматично.
      </p>
      <p className="mt-3 text-muted">
        Питання? Телефонуйте{" "}
        <a href={`tel:${SHOP.phone}`} className="font-semibold text-ink">
          {SHOP.phoneLabel}
        </a>
      </p>
      <Link href="/kulky" className="mt-8 inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white">
        Повернутися до каталогу
      </Link>
    </div>
  );
}
