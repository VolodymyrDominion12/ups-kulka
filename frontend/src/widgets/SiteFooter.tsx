import Link from "next/link";

import { SHOP } from "@/shared/config/shop";

import { Logo } from "./SiteHeader";

export function SiteFooter() {
  return (
    <footer className="bg-ink pb-24 pt-14 text-[#e8e8e8] sm:pb-14">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 sm:grid-cols-[1.4fr_1fr_1fr] sm:px-6">
        <div>
          <Logo light />
          <p className="mt-3 max-w-[36ch]">
            Повітряні кульки для свят, сюрпризів і просто гарного настрою. {SHOP.city}.
          </p>
        </div>
        <div className="grid content-start gap-2">
          <h2 className="mb-1 text-[15px] font-bold text-accent">Контакти</h2>
          <a href={`tel:${SHOP.phone}`} className="hover:text-white hover:underline">
            {SHOP.phoneLabel}
          </a>
          <a href={SHOP.instagramUrl} target="_blank" rel="noreferrer" className="hover:text-white hover:underline">
            Instagram {SHOP.instagramHandle}
          </a>
        </div>
        <div className="grid content-start gap-2">
          <h2 className="mb-1 text-[15px] font-bold text-accent">Покупцям</h2>
          <Link href="/kulky" className="hover:text-white hover:underline">
            Каталог
          </Link>
          <Link href="/#dostavka" className="hover:text-white hover:underline">
            Доставка й оплата
          </Link>
          <Link href="/#pytannia" className="hover:text-white hover:underline">
            Часті питання
          </Link>
        </div>
      </div>
    </footer>
  );
}
