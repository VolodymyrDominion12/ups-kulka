import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

// Admin PWA settings moved here from the root layout, so the storefront has its own.
export const metadata: Metadata = {
  title: { absolute: "УПС! Кулька — Адмін Салону" },
  description: "Мобільна адмін-панель салону повітряних кульок УПС! Кулька (Київ)",
  manifest: "/manifest.json",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#8a4f4f",
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return children;
}
