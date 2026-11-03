import { CreditCard, Store, CarTaxiFront } from "lucide-react";

const PERKS = [
  {
    Icon: CarTaxiFront,
    title: "Доставка таксі",
    text: "Відправимо замовлення таксі в зручний час. Поїздку ви оплачуєте за тарифом таксі.",
  },
  {
    Icon: Store,
    title: "Самовивіз",
    text: "Заберіть замовлення самі: менеджер підкаже, коли воно буде готове.",
  },
  {
    Icon: CreditCard,
    title: "Оплата при отриманні",
    text: "Готівкою або карткою, коли забираєте кульки.",
  },
] as const;

export function Perks() {
  return (
    <section id="dostavka" aria-labelledby="perks-title" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-14 sm:px-6">
      <h2 id="perks-title" className="sr-only">
        Доставка та оплата
      </h2>
      <div className="grid gap-8 sm:grid-cols-3">
        {PERKS.map(({ Icon, title, text }) => (
          <div key={title}>
            <span className="balloon-icon" aria-hidden="true">
              <Icon size={24} />
            </span>
            <h3 className="mt-3 font-display text-xl font-bold">{title}</h3>
            <p className="mt-1.5 max-w-[34ch] text-muted">{text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export const FAQ = [
  [
    "Скільки коштує доставка?",
    "Ми відправляємо замовлення таксі, а ви оплачуєте лише поїздку за тарифом служби таксі. Самовивіз безкоштовний.",
  ],
  [
    "Як оплатити замовлення?",
    "При отриманні: готівкою або карткою. Онлайн-оплату підключаємо найближчим часом.",
  ],
  [
    "Можна змінити кольори композиції?",
    "Так. Напишіть побажання в коментарі до замовлення або в Instagram, і ми підберемо палітру.",
  ],
  [
    "За скільки часу треба замовляти?",
    "Готові композиції часто можемо зібрати день у день. Фотозони й великі набори краще бронювати за 1–2 дні.",
  ],
] as const;

export function Faq() {
  return (
    <section id="pytannia" aria-labelledby="faq-title" className="mx-auto max-w-6xl scroll-mt-20 px-4 pb-16 sm:px-6">
      <h2 id="faq-title" className="font-display text-[clamp(28px,4vw,40px)] font-bold tracking-tight">
        Часті питання
      </h2>
      <div className="mt-4 max-w-3xl">
        {FAQ.map(([q, a]) => (
          <details key={q} className="faq border-b border-line">
            <summary className="flex cursor-pointer list-none justify-between gap-4 py-5 text-[17px] font-bold">
              {q}
            </summary>
            <p className="mb-5 max-w-[64ch] text-[#3a3a3a]">{a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
