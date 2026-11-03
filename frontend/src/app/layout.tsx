import type { Metadata, Viewport } from "next";
import { Comfortaa, Manrope } from "next/font/google";
import "./globals.css";

const comfortaa = Comfortaa({
  subsets: ["cyrillic", "latin"],
  variable: "--font-comfortaa",
  weight: ["600", "700"],
});

const manrope = Manrope({
  subsets: ["cyrillic", "latin"],
  variable: "--font-manrope",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "УПС! Кулька — Адмін Салону",
  description:
    "Мобільна адмін-панель салону повітряних кульок УПС! Кулька (Київ)",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#8a4f4f",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk" className={`${comfortaa.variable} ${manrope.variable}`}>
      <body className="min-h-screen bg-surface text-ink antialiased">
        {children}
      </body>
    </html>
  );
}
