import type { Metadata, Viewport } from "next";
import { Comfortaa, Manrope } from "next/font/google";
import type { ReactNode } from "react";

import { SHOP } from "@/shared/config/shop";

import "./globals.css";

const comfortaa = Comfortaa({
  subsets: ["cyrillic", "latin"],
  variable: "--font-comfortaa",
  weight: ["600", "700"],
});

const manrope = Manrope({
  subsets: ["cyrillic", "latin"],
  variable: "--font-manrope",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SHOP.siteUrl),
  title: {
    default: "УПС! Кулька — повітряні кульки в Києві",
    template: "%s | УПС! Кулька",
  },
  description:
    "Композиції, фонтани й фотозони з гелієвих кульок у Києві. Самовивіз або доставка таксі.",
  openGraph: { siteName: SHOP.name, locale: "uk_UA", type: "website" },
};

// No maximumScale here: customers must be able to zoom (accessibility).
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#ffffff",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="uk" className={`${comfortaa.variable} ${manrope.variable}`}>
      <body className="min-h-screen bg-surface text-ink antialiased">{children}</body>
    </html>
  );
}
