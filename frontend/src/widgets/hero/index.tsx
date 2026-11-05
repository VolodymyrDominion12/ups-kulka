import type { HomeBannerOut, ProductOut } from "@/shared/api/storefront";

import { HeroBalloons } from "./HeroBalloons";
import { HeroImage } from "./HeroImage";
import { HeroRibbon } from "./HeroRibbon";
import { HeroSplit } from "./HeroSplit";

/**
 * Picks the hero by the active campaign's layout and renders the optional promo ribbon above it
 * (specs/017-home-banners).
 */
export function Hero({ banner, showcase }: { banner: HomeBannerOut; showcase: ProductOut[] }) {
  let content: React.ReactNode;
  if (banner.layout === "image" && banner.image) {
    content = <HeroImage banner={banner} />;
  } else if (banner.layout === "split" && banner.image) {
    content = <HeroSplit banner={banner} />;
  } else {
    content = <HeroBalloons banner={banner} showcase={showcase} />;
  }

  return (
    <>
      <HeroRibbon banner={banner} />
      {content}
    </>
  );
}
