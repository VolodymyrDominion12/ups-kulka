import Link from "next/link";
import type { CSSProperties } from "react";

import type { ProductOut } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";
import { responsiveImage } from "@/shared/lib/images";

/** Balloon positions in the cluster: three photos, two plain balloons. */
const SLOTS = [
  { x: "34%", y: "2%", w: "40%", d: "0s", s: "190px", r: "4deg", c: "#e6b3b3" },
  { x: "2%", y: "22%", w: "34%", d: ".15s", s: "160px", r: "-14deg", c: "#c06f6f" },
  { x: "64%", y: "26%", w: "33%", d: ".3s", s: "150px", r: "16deg", c: "#f5dede" },
  { x: "20%", y: "58%", w: "16%", d: ".45s", s: "90px", r: "-6deg", c: "#d99999" },
  { x: "58%", y: "66%", w: "13%", d: ".55s", s: "70px", r: "8deg", c: "#8a4f4f" },
] as const;

export function Hero({ showcase }: { showcase: ProductOut[] }) {
  const photos = showcase
    .map((p) => (p.images[0] ? responsiveImage(p.images[0], 320) : null))
    .filter((img): img is NonNullable<typeof img> => img !== null)
    .slice(0, 3);

  return (
    <section className="bg-gradient-to-b from-accent-soft to-white">
      <div className="mx-auto grid max-w-6xl items-center gap-6 px-4 pb-12 pt-8 sm:px-6 md:min-h-[540px] md:grid-cols-[1.05fr_1fr] md:pb-16">
        <div className="order-2 md:order-1">
          <h1 className="font-display text-[clamp(48px,9vw,92px)] font-bold leading-[0.95] tracking-[-0.035em] text-rose-deep">
            Упс!
            <span className="mt-3 block text-[0.42em] leading-[1.15] tracking-[-0.02em] text-ink">
              Кульки, що роблять свято з будь-якого дня
            </span>
          </h1>
          <p className="mt-5 max-w-[46ch] text-lg text-[#3a3a3a]">
            Композиції, фонтани й фотозони з гелієвих кульок у Києві. Заберіть самі або
            відправимо таксі в зручний час.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/kulky"
              className="inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white transition hover:bg-rose-deep"
            >
              Обрати кульки
            </Link>
            <a
              href={SHOP.instagramUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-12 items-center rounded-full bg-accent-soft px-6 font-bold text-rose-deep transition hover:bg-accent"
            >
              Більше робіт в Instagram
            </a>
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
