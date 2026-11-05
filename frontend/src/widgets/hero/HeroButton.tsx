"use client";

import Link from "next/link";

import type { BannerLayout } from "@/shared/api/storefront";
import { isExternalLink, recordBannerClick, withBannerAttribution } from "@/shared/lib/banner";

const BASE = "inline-flex h-12 items-center rounded-full px-6 font-bold transition";

export function HeroButton({
  href,
  className,
  campaignId,
  layout,
  children,
}: {
  href: string;
  className: string;
  campaignId?: string | null;
  layout?: BannerLayout;
  children: React.ReactNode;
}) {
  const classes = `${BASE} ${className}`;
  const trackedHref = withBannerAttribution(href, campaignId, layout);
  const handleClick = () => {
    recordBannerClick(campaignId, layout, href);
  };

  if (isExternalLink(href)) {
    return (
      <a href={href} target="_blank" rel="noreferrer" onClick={handleClick} className={classes}>
        {children}
      </a>
    );
  }
  return (
    <Link href={trackedHref} onClick={handleClick} className={classes}>
      {children}
    </Link>
  );
}
