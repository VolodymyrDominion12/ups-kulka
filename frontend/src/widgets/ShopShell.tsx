import type { ReactNode } from "react";

import { CartProvider } from "@/features/cart/CartProvider";
import { MobileCartBar } from "@/features/cart/MobileCartBar";
import { UtmCapture } from "@/features/marketing/UtmCapture";

import { SiteFooter } from "./SiteFooter";
import { SiteHeader } from "./SiteHeader";

/** Storefront frame: cart state, header, footer, mobile cart bar, ad-mark capture. */
export function ShopShell({ children }: { children: ReactNode }) {
  return (
    <CartProvider>
      <UtmCapture />
      <SiteHeader />
      <main className="bg-white">{children}</main>
      <SiteFooter />
      <MobileCartBar />
    </CartProvider>
  );
}
