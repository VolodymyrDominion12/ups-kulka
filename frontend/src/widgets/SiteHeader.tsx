import Link from "next/link";

import { CartLink } from "@/features/cart/CartLink";
import { SHOP } from "@/shared/config/shop";

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-2 font-display text-[22px] font-bold tracking-tight ${
        light ? "text-white" : "text-ink"
      }`}
    >
      <span className="logo-balloon" aria-hidden="true" />
      {SHOP.name}
    </Link>
  );
}

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-4 px-4 sm:px-6">
        <Logo />
        <nav aria-label="Розділи" className="ml-6 hidden gap-6 font-semibold text-muted md:flex">
          <Link href="/kulky" className="hover:text-ink">
            Каталог
          </Link>
          <Link href="/dostavka" className="hover:text-ink">
            Доставка
          </Link>
          <Link href="/kontakty" className="hover:text-ink">
            Контакти
          </Link>
          <Link href="/pro-nas" className="hover:text-ink">
            Про нас
          </Link>
        </nav>
        <div className="ml-auto flex items-center gap-4">
          <a href={`tel:${SHOP.phone}`} className="hidden font-bold sm:block">
            {SHOP.phoneLabel}
          </a>
          <CartLink />
        </div>
      </div>
    </header>
  );
}
