"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { formatUah } from "@/shared/lib/money";

import { useCart } from "./CartProvider";

const HIDDEN_ON = ["/koshyk", "/oformlennia", "/diakuiemo"];

/** Bottom bar on phones: the cart is one tap away from any page. */
export function MobileCartBar() {
  const { count, totalKopecks, ready } = useCart();
  const pathname = usePathname();
  if (!ready || count === 0 || HIDDEN_ON.includes(pathname)) return null;
  return (
    <div className="fixed inset-x-3 bottom-3 z-30 flex items-center justify-between rounded-full bg-ink py-1.5 pl-5 pr-1.5 text-white shadow-pop sm:hidden">
      <span className="text-sm">
        <strong className="tabular-nums">{count}</strong> шт. на{" "}
        <strong className="tabular-nums">{formatUah(totalKopecks)}</strong>
      </span>
      <Link
        href="/koshyk"
        className="inline-flex h-11 items-center rounded-full bg-accent px-5 font-bold text-ink"
      >
        До кошика
      </Link>
    </div>
  );
}
