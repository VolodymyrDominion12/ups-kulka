import type { HomeBannerOut, ProductOut } from "@/shared/api/storefront";

import { HeroBalloons } from "./HeroBalloons";
import { HeroImage } from "./HeroImage";

/**
 * Picks the hero by the active campaign's layout (specs/017-home-banners).
 * `split` and `collection` arrive in later stages and render the balloons hero until then.
 */
export function Hero({ banner, showcase }: { banner: HomeBannerOut; showcase: ProductOut[] }) {
  if (banner.layout === "image" && banner.image) {
    return <HeroImage banner={banner} />;
  }
  return <HeroBalloons banner={banner} showcase={showcase} />;
}
