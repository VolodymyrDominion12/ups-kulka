import type { BannerImageOut, HomeBannerOut } from "@/shared/api/storefront";
import { themeClasses } from "@/shared/lib/banner";
import { responsiveImage } from "@/shared/lib/images";

import { HeroButton } from "./HeroButton";

function pictureSources(image: BannerImageOut) {
  return responsiveImage(image, 1280);
}

/**
 * Full-width photo hero. The photo is the LCP element, so it is eager with high priority;
 * the text stays real HTML (<h1>) on top of it for SEO and accessibility.
 */
export function HeroImage({ banner }: { banner: HomeBannerOut }) {
  const image = banner.image;
  if (!image) return null;
  const desktop = pictureSources(image);
  const mobile = banner.image_mobile ? pictureSources(banner.image_mobile) : null;
  if (!desktop) return null;
  const theme = themeClasses(banner.theme);

  return (
    <section className={`relative isolate overflow-hidden ${theme.section}`}>
      <picture>
        {mobile && (
          <source
            media="(max-width: 767px)"
            srcSet={mobile.srcSet || mobile.src}
            sizes="100vw"
          />
        )}
        <img
          src={desktop.src}
          srcSet={desktop.srcSet || undefined}
          sizes="100vw"
          alt={banner.image_alt}
          width={image.width}
          height={image.height}
          loading="eager"
          fetchPriority="high"
          decoding="async"
          style={{ backgroundImage: `url(${image.blur_data_url})`, backgroundSize: "cover" }}
          className="absolute inset-0 -z-10 h-full w-full object-cover"
        />
      </picture>
      <div className="absolute inset-0 -z-10 bg-gradient-to-r from-black/55 via-black/25 to-transparent" />

      <div className="mx-auto flex max-w-6xl flex-col justify-center px-4 py-16 sm:px-6 md:min-h-[540px]">
        <h1 className="max-w-[18ch] font-display text-[clamp(40px,7vw,80px)] font-bold leading-[1] tracking-[-0.03em] text-white">
          {banner.headline}
        </h1>
        {banner.subtitle && (
          <p className="mt-5 max-w-[46ch] text-lg text-white/90">{banner.subtitle}</p>
        )}
        {(banner.cta_label || banner.cta2_label) && (
          <div className="mt-7 flex flex-wrap gap-3">
            {banner.cta_label && (
              <HeroButton
                href={banner.cta_url}
                campaignId={banner.campaign_id}
                layout={banner.layout}
                className="bg-white text-ink hover:bg-accent"
              >
                {banner.cta_label}
              </HeroButton>
            )}
            {banner.cta2_label && (
              <HeroButton
                href={banner.cta2_url}
                campaignId={banner.campaign_id}
                layout={banner.layout}
                className="bg-white/20 text-white hover:bg-white/30"
              >
                {banner.cta2_label}
              </HeroButton>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
