"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X } from "lucide-react";

import type { HomeBannerOut } from "@/shared/api/storefront";
import {
  isExternalLink,
  recordBannerClick,
  themeClasses,
  withBannerAttribution,
} from "@/shared/lib/banner";

function storageKey(banner: HomeBannerOut): string {
  return `ups_kulka_ribbon_dismissed:${banner.campaign_id ?? "default"}:${banner.ribbon_text}`;
}

export function HeroRibbon({ banner }: { banner: HomeBannerOut }) {
  const text = banner.ribbon_text.trim();
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (!text || banner.campaign_id === "preview") {
      setDismissed(false);
      return;
    }
    try {
      setDismissed(window.sessionStorage.getItem(storageKey(banner)) === "1");
    } catch {
      setDismissed(false);
    }
  }, [banner, text]);

  if (!text || dismissed) return null;

  const theme = themeClasses(banner.theme);
  const url = banner.ribbon_url.trim();
  const trackedHref = url ? withBannerAttribution(url, banner.campaign_id, banner.layout) : "";

  const handleDismiss = () => {
    setDismissed(true);
    if (banner.campaign_id === "preview") return;
    try {
      window.sessionStorage.setItem(storageKey(banner), "1");
    } catch {
      // Storage blocked: dismiss for current render only.
    }
  };

  const handleClick = () => {
    if (url) recordBannerClick(banner.campaign_id, banner.layout, url);
  };

  return (
    <div className={`relative px-4 py-2.5 text-center text-xs font-bold sm:text-sm ${theme.ribbon}`}>
      <div className="mx-auto flex max-w-6xl items-center justify-center gap-2 pr-7">
        {url ? (
          isExternalLink(url) ? (
            <a
              href={url}
              target="_blank"
              rel="noreferrer"
              onClick={handleClick}
              className="underline decoration-white/60 underline-offset-4 hover:decoration-white"
            >
              {text}
            </a>
          ) : (
            <Link
              href={trackedHref}
              onClick={handleClick}
              className="underline decoration-white/60 underline-offset-4 hover:decoration-white"
            >
              {text}
            </Link>
          )
        ) : (
          <span>{text}</span>
        )}
      </div>
      <button
        type="button"
        onClick={handleDismiss}
        aria-label="Закрити повідомлення"
        className="absolute right-2 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full opacity-80 transition hover:bg-black/15 hover:opacity-100"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

