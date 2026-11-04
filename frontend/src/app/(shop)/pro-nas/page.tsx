import type { Metadata } from "next";

import { SHOP } from "@/shared/config/shop";

export const metadata: Metadata = {
  title: "Про нас",
  description: `${SHOP.name} — повітряні кульки для свят, сюрпризів і настрою в ${SHOP.city}. Швидко, акуратно, красиво.`,
  alternates: { canonical: "/pro-nas" },
};

const VALUES = [
  ["Швидко", "Готові композиції часто збираємо день у день."],
  ["Акуратно", "Стежимо за якістю кульок і пакуванням."],
  ["Красиво", "Підбираємо палітру й композицію під ваш привід."],
] as const;

export default function ProNasPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 pb-16 pt-8 sm:px-6">
      <h1 className="font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">
        Про нас
      </h1>
      <p className="mt-4 max-w-[60ch] text-[15px] leading-relaxed text-[#3a3a3a]">
        {SHOP.name} — кульки для подій, сюрпризів і просто гарного настрою.
        Збираємо композиції, фонтани, цифри, коробки-сюрпризи та фотозони з
        гелієвих кульок у {SHOP.city}.
      </p>

      <ul className="mt-8 grid gap-4">
        {VALUES.map(([title, text]) => (
          <li key={title} className="rounded-3xl border border-line bg-white p-5">
            <h2 className="font-display text-lg font-bold text-ink">{title}</h2>
            <p className="mt-1.5 text-[15px] text-muted">{text}</p>
          </li>
        ))}
      </ul>

      <p className="mt-8 text-[15px] leading-relaxed text-[#3a3a3a]">
        Кольори й написи можна змінити — напишіть побажання в коментарі до
        замовлення або в Instagram, і ми підберемо композицію саме для вас.
      </p>
    </div>
  );
}
