import { Flower2, Heart, Snowflake, Sparkles } from "lucide-react";

import type { BannerTheme } from "@/shared/api/storefront";

/**
 * A light festive motif for a campaign hero: the themes double as holiday moods
 * (rose = spring, red = love, gold = winter, dark = new year). It sits behind the
 * content, is decorative only and never replaces the balloon photos.
 */
const MOTIF = {
  rose: Flower2,
  red: Heart,
  gold: Snowflake,
  dark: Sparkles,
} as const;

const COLOR: Record<BannerTheme, string> = {
  rose: "#c06f6f",
  red: "#a82828",
  gold: "#7a5a0a",
  dark: "#ffffff",
};

const SPOTS = [
  { top: "6%", left: "52%", size: 34, rotate: -12, opacity: 0.18 },
  { top: "17%", left: "88%", size: 20, rotate: 18, opacity: 0.16 },
  { top: "46%", left: "46%", size: 16, rotate: 8, opacity: 0.12 },
  { top: "63%", left: "79%", size: 38, rotate: -20, opacity: 0.14 },
  { top: "80%", left: "36%", size: 22, rotate: 24, opacity: 0.12 },
  { top: "33%", left: "68%", size: 13, rotate: 0, opacity: 0.2 },
] as const;

export function HeroDecor({ theme }: { theme: BannerTheme }) {
  const Motif = MOTIF[theme] ?? MOTIF.rose;
  const color = COLOR[theme] ?? COLOR.rose;

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
    >
      {SPOTS.map((spot, i) => (
        <Motif
          key={i}
          strokeWidth={1.4}
          className="absolute"
          style={{
            top: spot.top,
            left: spot.left,
            width: spot.size,
            height: spot.size,
            color,
            opacity: spot.opacity,
            transform: `rotate(${spot.rotate}deg)`,
          }}
        />
      ))}
    </div>
  );
}
