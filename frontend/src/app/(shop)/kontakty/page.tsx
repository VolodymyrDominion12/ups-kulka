import type { Metadata } from "next";
import { Instagram, Phone } from "lucide-react";

import { SHOP } from "@/shared/config/shop";

export const metadata: Metadata = {
  title: "Контакти",
  description: `Телефон ${SHOP.phoneLabel} та Instagram ${SHOP.instagramHandle}. Пишіть — підберемо композицію з кульок.`,
  alternates: { canonical: "/kontakty" },
};

export default function KontaktyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 pb-16 pt-8 sm:px-6">
      <h1 className="font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">
        Контакти
      </h1>
      <p className="mt-4 max-w-[60ch] text-[15px] leading-relaxed text-[#3a3a3a]">
        Зателефонуйте або напишіть — відповімо швидко, допоможемо обрати
        композицію та оформити замовлення.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <a
          href={`tel:${SHOP.phone}`}
          className="flex items-center gap-4 rounded-3xl border border-line bg-white p-5 transition hover:border-accent-dark"
        >
          <span className="balloon-icon" aria-hidden="true">
            <Phone size={24} />
          </span>
          <span>
            <span className="block text-sm font-semibold text-muted">Телефон</span>
            <span className="font-display text-lg font-bold text-ink">{SHOP.phoneLabel}</span>
          </span>
        </a>

        <a
          href={SHOP.instagramUrl}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-4 rounded-3xl border border-line bg-white p-5 transition hover:border-accent-dark"
        >
          <span className="balloon-icon" aria-hidden="true">
            <Instagram size={24} />
          </span>
          <span>
            <span className="block text-sm font-semibold text-muted">Instagram</span>
            <span className="font-display text-lg font-bold text-ink">{SHOP.instagramHandle}</span>
          </span>
        </a>
      </div>

      <div className="mt-8 rounded-3xl bg-accent-soft p-6">
        <h2 className="font-display text-lg font-bold text-rose-deep">Наші роботи в Instagram</h2>
        <p className="mt-1.5 max-w-[52ch] text-[15px] text-[#3a3a3a]">
          Свіжі композиції, кольори й ідеї публікуємо в Instagram — зазирніть
          перед замовленням.
        </p>
        <a
          href={SHOP.instagramUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white transition hover:bg-rose-deep"
        >
          Подивитись {SHOP.instagramHandle}
        </a>
      </div>
    </div>
  );
}
