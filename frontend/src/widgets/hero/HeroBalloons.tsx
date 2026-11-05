import type { CSSProperties } from "react";

import type { HomeBannerOut, ProductOut } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";
import { themeClasses } from "@/shared/lib/banner";
import { responsiveImage } from "@/shared/lib/images";

import { HeroButton } from "./HeroButton";
import { HeroDecor } from "./HeroDecor";

/** Balloon positions in the cluster: three photos, two plain balloons. */
const SLOTS = [
  { x: "34%", y: "2%", w: "40%", d: "0s", s: "190px", r: "4deg", c: "#e6b3b3" },
  { x: "2%", y: "22%", w: "34%", d: ".15s", s: "160px", r: "-14deg", c: "#c06f6f" },
  { x: "64%", y: "26%", w: "33%", d: ".3s", s: "150px", r: "16deg", c: "#f5dede" },
  { x: "20%", y: "58%", w: "16%", d: ".45s", s: "90px", r: "-6deg", c: "#d99999" },
  { x: "58%", y: "66%", w: "13%", d: ".55s", s: "70px", r: "8deg", c: "#8a4f4f" },
] as const;

const DEFAULT_TITLE = "Кульки, що роблять свято з будь-якого дня";
const DEFAULT_TEXT =
  "Композиції, фонтани й фотозони з гелієвих кульок у Києві. Заберіть самі або відправимо таксі в зручний час.";

/**
 * The brand hero: text + a bunch of balloons with product photos. It is the default
 * (no active campaign) and also a campaign layout, which may override texts, buttons and colours.
 */
export function HeroBalloons({
  showcase,
  banner,
}: {
  showcase: ProductOut[];
  banner?: HomeBannerOut;
}) {
  const campaign = banner && banner.campaign_id !== null ? banner : null;
  const theme = themeClasses(campaign?.theme ?? "rose");
  const title = campaign?.headline || null;
  const text = campaign?.subtitle || DEFAULT_TEXT;
  const defaultCollectionHref =
    campaign?.layout === "collection" && campaign.tag_slug
      ? `/kulky/${campaign.tag_slug}`
      : "/kulky";

  const photos = showcase
    .map((p) => (p.images[0] ? responsiveImage(p.images[0], 320) : null))
    .filter((img): img is NonNullable<typeof img> => img !== null)
    .slice(0, 3);

  return (
    <section className={`relative isolate overflow-hidden ${theme.section}`}>
      {campaign && <HeroDecor theme={campaign.theme} />}
      <div className="mx-auto grid max-w-6xl items-center gap-6 px-4 pb-12 pt-8 sm:px-6 md:min-h-[540px] md:grid-cols-[1.05fr_1fr] md:pb-16">
        <div className="order-2 md:order-1">
          <h1
            className={`font-display text-[clamp(48px,9vw,92px)] font-bold leading-[0.95] tracking-[-0.035em] ${theme.heading}`}
          >
            {title ?? "Упс!"}
            {!title && (
              <span className="mt-3 block text-[0.42em] leading-[1.15] tracking-[-0.02em] text-ink">
                {DEFAULT_TITLE}
              </span>
            )}
          </h1>
          <p className={`mt-5 max-w-[46ch] text-lg ${theme.body}`}>{text}</p>
          <div className="mt-7 flex flex-wrap gap-3">
            {campaign?.cta_label ? (
              <HeroButton
                href={campaign.cta_url}
                campaignId={campaign.campaign_id}
                layout={campaign.layout}
                className={theme.primaryButton}
              >
                {campaign.cta_label}
              </HeroButton>
            ) : (
              <HeroButton
                href={defaultCollectionHref}
                campaignId={campaign?.campaign_id}
                layout={campaign?.layout}
                className={theme.primaryButton}
              >
                Обрати кульки
              </HeroButton>
            )}
            {campaign?.cta2_label ? (
              <HeroButton
                href={campaign.cta2_url}
                campaignId={campaign.campaign_id}
                layout={campaign.layout}
                className={theme.secondaryButton}
              >
                {campaign.cta2_label}
              </HeroButton>
            ) : (
              <HeroButton
                href={SHOP.instagramUrl}
                campaignId={campaign?.campaign_id}
                layout={campaign?.layout}
                className={theme.secondaryButton}
              >
                Більше робіт в Instagram
              </HeroButton>
            )}
          </div>
        </div>

        <div className="balloon-bunch order-1 md:order-2" aria-hidden="true">
          {SLOTS.map((slot, i) => {
            const photo = i < 3 ? photos[i] : undefined;
            const style = {
              "--x": slot.x,
              "--y": slot.y,
              "--w": slot.w,
              "--d": slot.d,
              "--s": slot.s,
              "--r": slot.r,
              "--c": slot.c,
            } as CSSProperties;
            return (
              <div key={i} className="balloon" style={style}>
                <div className="balloon-skin">
                  {photo && <img src={photo.src} alt="" loading="eager" decoding="async" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
