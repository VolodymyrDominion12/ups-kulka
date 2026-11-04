import type { Metadata } from "next";
import { CreditCard, Store, CarTaxiFront, Clock } from "lucide-react";

import { SHOP } from "@/shared/config/shop";
import { Faq } from "@/widgets/InfoSections";

export const metadata: Metadata = {
  title: "Доставка і оплата",
  description:
    "Доставка кульок по Києву таксі або самовивіз. Оплата при отриманні готівкою чи карткою.",
  alternates: { canonical: "/dostavka" },
};

const METHODS = [
  {
    Icon: CarTaxiFront,
    title: "Доставка таксі",
    text: `Відправляємо замовлення таксі по Києву в зручний для вас час. Поїздку оплачуєте за тарифом служби таксі.`,
  },
  {
    Icon: Store,
    title: "Самовивіз",
    text: "Безкоштовно. Менеджер підкаже адресу й час, коли замовлення буде готове.",
  },
  {
    Icon: CreditCard,
    title: "Оплата",
    text: "При отриманні — готівкою або карткою. Онлайн-оплата доступна, коли її вмикають на касі.",
  },
  {
    Icon: Clock,
    title: "Коли замовляти",
    text: "Готові композиції часто збираємо день у день. Фотозони й великі набори краще бронювати за 1–2 дні.",
  },
] as const;

export default function DostavkaPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 pb-16 pt-8 sm:px-6">
      <h1 className="font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">
        Доставка і оплата
      </h1>
      <p className="mt-4 max-w-[60ch] text-[15px] leading-relaxed text-[#3a3a3a]">
        Працюємо в {SHOP.city}. Доставляємо таксі або віддаємо замовлення на
        самовивозі — обирайте, як зручніше.
      </p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        {METHODS.map(({ Icon, title, text }) => (
          <div key={title} className="rounded-3xl border border-line bg-white p-5">
            <span className="balloon-icon" aria-hidden="true">
              <Icon size={24} />
            </span>
            <h2 className="mt-3 font-display text-lg font-bold">{title}</h2>
            <p className="mt-1.5 text-[15px] text-muted">{text}</p>
          </div>
        ))}
      </div>

      <div className="mt-12">
        <Faq />
      </div>
    </div>
  );
}
