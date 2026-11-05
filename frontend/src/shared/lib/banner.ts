import type { BannerTheme } from "@/shared/api/storefront";

export interface ThemeClasses {
  section: string;
  heading: string;
  body: string;
  primaryButton: string;
  secondaryButton: string;
}

/** Fixed colour presets (no free-form CSS from the admin): rose is the default look. */
export const BANNER_THEMES: Record<BannerTheme, ThemeClasses> = {
  rose: {
    section: "bg-gradient-to-b from-accent-soft to-white",
    heading: "text-rose-deep",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-ink text-white hover:bg-rose-deep",
    secondaryButton: "bg-accent-soft text-rose-deep hover:bg-accent",
  },
  red: {
    section: "bg-gradient-to-b from-[#f9c9c9] to-white",
    heading: "text-[#a82828]",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-[#a82828] text-white hover:bg-ink",
    secondaryButton: "bg-white text-[#a82828] hover:bg-accent-soft",
  },
  gold: {
    section: "bg-gradient-to-b from-[#f6e7b8] to-white",
    heading: "text-[#7a5a0a]",
    body: "text-[#3a3a3a]",
    primaryButton: "bg-ink text-white hover:bg-[#7a5a0a]",
    secondaryButton: "bg-white text-[#7a5a0a] hover:bg-[#f6e7b8]",
  },
  dark: {
    section: "bg-ink",
    heading: "text-white",
    body: "text-white/85",
    primaryButton: "bg-white text-ink hover:bg-accent",
    secondaryButton: "bg-white/15 text-white hover:bg-white/25",
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
