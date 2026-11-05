import type { BannerImageOut, HomeBannerOut } from "@/shared/api/storefront";
import { themeClasses } from "@/shared/lib/banner";
import { responsiveImage } from "@/shared/lib/images";

import { HeroButton } from "./HeroButton";

function pictureSources(image: BannerImageOut) {
  return responsiveImage(image, 960);
}

/**
 * Split hero: headline and CTAs on the left, framed holiday photo on the right.
 */
export function HeroSplit({ banner }: { banner: HomeBannerOut }) {
  const image = banner.image;
  if (!image) return null;
  const desktop = pictureSources(image);
  const mobile = banner.image_mobile ? pictureSources(banner.image_mobile) : null;
  if (!desktop) return null;
  const theme = themeClasses(banner.theme);

  return (
    <section className={theme.section}>
      <div className="mx-auto grid max-w-6xl items-center gap-8 px-4 pb-12 pt-8 sm:px-6 md:min-h-[540px] md:grid-cols-[1.05fr_1fr] md:pb-16">
        <div className="order-2 md:order-1">
          <h1
            className={`font-display text-[clamp(40px,7vw,76px)] font-bold leading-[0.98] tracking-[-0.03em] ${theme.heading}`}
          >
            {banner.headline}
          </h1>
          {banner.subtitle && (
            <p className={`mt-5 max-w-[46ch] text-lg ${theme.body}`}>{banner.subtitle}</p>
          )}
          {(banner.cta_label || banner.cta2_label) && (
            <div className="mt-7 flex flex-wrap gap-3">
              {banner.cta_label && (
                <HeroButton
                  href={banner.cta_url}
                  campaignId={banner.campaign_id}
                  layout={banner.layout}
                  className={theme.primaryButton}
                >
                  {banner.cta_label}
                </HeroButton>
              )}
              {banner.cta2_label && (
                <HeroButton
                  href={banner.cta2_url}
                  campaignId={banner.campaign_id}
                  layout={banner.layout}
                  className={theme.secondaryButton}
                >
                  {banner.cta2_label}
                </HeroButton>
              )}
            </div>
          )}
        </div>

        <div className="order-1 overflow-hidden rounded-3xl shadow-card md:order-2">
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
              sizes="(min-width: 768px) 50vw, 100vw"
              alt={banner.image_alt}
              width={image.width}
              height={image.height}
              loading="eager"
              fetchPriority="high"
              decoding="async"
              style={{ backgroundImage: `url(${image.blur_data_url})`, backgroundSize: "cover" }}
              className="aspect-[4/5] max-h-[480px] w-full object-cover md:aspect-[5/4]"
            />
          </picture>
        </div>
      </div>
    </section>
  );
}

