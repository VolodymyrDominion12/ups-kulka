import { ATTRIBUTION_STORAGE_KEY } from "@/features/marketing/UtmCapture";
import type { BannerLayout, BannerTheme } from "@/shared/api/storefront";
import type { MarketingAttribution } from "@/shared/lib/utm";

export interface ThemeClasses {
  section: string;
  heading: string;
  body: string;
  primaryButton: string;
  secondaryButton: string;
  ribbon: string;
}

/** Fixed colour presets (no free-form CSS from the admin): rose is the default look. */
export const BANNER_THEMES: Record<BannerTheme, ThemeClasses> = {
  rose: {
    section: "bg-gradient-to-b from-accent-soft to-white",
    heading: "text-rose-deep",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-ink text-white hover:bg-rose-deep",
    secondaryButton: "bg-accent-soft text-rose-deep hover:bg-accent",
    ribbon: "bg-rose-deep text-white",
  },
  red: {
    section: "bg-gradient-to-b from-[#f9c9c9] to-white",
    heading: "text-[#a82828]",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-[#a82828] text-white hover:bg-ink",
    secondaryButton: "bg-white text-[#a82828] hover:bg-accent-soft",
    ribbon: "bg-[#a82828] text-white",
  },
  gold: {
    section: "bg-gradient-to-b from-[#f6e7b8] to-white",
    heading: "text-[#7a5a0a]",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-ink text-white hover:bg-[#7a5a0a]",
    secondaryButton: "bg-white text-[#7a5a0a] hover:bg-[#f6e7b8]",
    ribbon: "bg-[#7a5a0a] text-white",
  },
  dark: {
    section: "bg-ink",
    heading: "text-white",
    body: "text-white/85",
    primaryButton: "bg-white text-ink hover:bg-accent",
    secondaryButton: "bg-white/15 text-white hover:bg-white/25",
    ribbon: "bg-ink text-white border-b border-white/15",
  },
};

export function themeClasses(theme: BannerTheme): ThemeClasses {
  return BANNER_THEMES[theme] ?? BANNER_THEMES.rose;
}

const ABSOLUTE_URL = /^https?:\/\//i;

/** Links to other sites open in a new tab; internal ones use the router. */
export function isExternalLink(url: string): boolean {
  return ABSOLUTE_URL.test(url);
}

/**
 * Appends campaign attribution marks (`utm_source=home_banner&utm_medium=<layout>&utm_campaign=<id>`)
 * to internal links when a real campaign is active, without overwriting existing UTM query params.
 */
export function withBannerAttribution(
  href: string,
  campaignId: string | null | undefined,
  layout?: BannerLayout,
): string {
  if (!href || !campaignId || campaignId === "preview" || isExternalLink(href)) {
    return href;
  }
  const [pathWithQuery, hash = ""] = href.split("#", 2);
  const [pathname, rawQuery = ""] = pathWithQuery.split("?", 2);
  const params = new URLSearchParams(rawQuery);
  if (!params.has("utm_source")) params.set("utm_source", "home_banner");
  if (layout && !params.has("utm_medium")) params.set("utm_medium", layout);
  if (!params.has("utm_campaign")) params.set("utm_campaign", campaignId);
  const query = params.toString();
  const suffix = hash ? `#${hash}` : "";
  return query ? `${pathname}?${query}${suffix}` : `${pathname}${suffix}`;
}

/**
 * Records a banner CTA click in sessionStorage for checkout attribution (specs/011 & 017),
 * so orders placed in this session are attributed to the holiday banner campaign.
 */
export function recordBannerClick(
  campaignId: string | null | undefined,
  layout: BannerLayout | undefined,
  targetHref: string,
): void {
  if (!campaignId || campaignId === "preview" || typeof window === "undefined") {
    return;
  }
  try {
    const attribution: MarketingAttribution = {
      utm_source: "home_banner",
      utm_medium: layout ?? "banner",
      utm_campaign: campaignId.slice(0, 160),
      promo_code: null,
      landing_page: targetHref.split("?")[0]?.slice(0, 300) || "/",
    };
    window.sessionStorage.setItem(ATTRIBUTION_STORAGE_KEY, JSON.stringify(attribution));
  } catch {
    // Storage unavailable: ignore silently.
  }
}

const pad = (n: number) => String(n).padStart(2, "0");

/** ISO instant → value for <input type="datetime-local"> in the browser's local time. */
export function toDateTimeLocal(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** <input type="datetime-local"> value (local time) → ISO instant with an offset. */
export function fromDateTimeLocal(value: string): string {
  return new Date(value).toISOString();
}
