"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { TouchEvent as ReactTouchEvent } from "react";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

import type { ProductImageOut } from "@/shared/api/storefront";
import { cycleIndex, largestImageSrc } from "@/shared/lib/gallery";
import { responsiveImage } from "@/shared/lib/images";

import { ProductImage } from "./ProductImage";

interface Props {
  images: ProductImageOut[];
  name: string;
  seed: string;
}

/** Client-side product photo gallery: cover, clickable thumbnails, fullscreen lightbox. */
export function ProductGallery({ images, name, seed }: Props) {
  const [active, setActive] = useState(0);
  const [open, setOpen] = useState(false);
  const openerRef = useRef<HTMLButtonElement | null>(null);
  const touchStart = useRef<number | null>(null);

  const count = images.length;
  const current = images[Math.min(active, count - 1)];

  const step = useCallback(
    (delta: 1 | -1) => setActive((a) => cycleIndex(a, count, delta)),
    [count],
  );

  const close = useCallback(() => {
    setOpen(false);
    openerRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
      else if (event.key === "ArrowLeft") step(-1);
      else if (event.key === "ArrowRight") step(1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close, step]);

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [open]);

  const onTouchStart = (event: ReactTouchEvent<HTMLDivElement>) => {
    touchStart.current = event.touches[0].clientX;
  };

  const onTouchEnd = (event: ReactTouchEvent<HTMLDivElement>) => {
    if (touchStart.current === null) return;
    const dx = event.changedTouches[0].clientX - touchStart.current;
    if (Math.abs(dx) > 40) step(dx > 0 ? -1 : 1);
    touchStart.current = null;
  };

  if (count === 0) {
    return (
      <div className="aspect-[4/5] overflow-hidden rounded-panel bg-accent-soft">
        <ProductImage image={undefined} alt={name} seed={seed} sizes="50vw" priority />
      </div>
    );
  }

  const cover = responsiveImage(current, 960);
  const lightboxSrc = largestImageSrc(current.variants);

  return (
    <>
      <div className="grid gap-3">
        <button
          type="button"
          ref={openerRef}
          onClick={() => setOpen(true)}
          aria-label="Відкрити фото на весь екран"
          className="relative block aspect-[4/5] overflow-hidden rounded-panel bg-accent-soft focus-visible:outline-offset-4"
        >
          {cover && (
            <img
              src={cover.src}
              srcSet={cover.srcSet || undefined}
              sizes="(min-width: 768px) 50vw, 100vw"
              alt={name}
              width={current.width}
              height={current.height}
              loading={active === 0 ? "eager" : "lazy"}
              fetchPriority={active === 0 ? "high" : "auto"}
              decoding="async"
              className="h-full w-full object-cover"
              style={{
                backgroundImage: current.blur_data_url
                  ? `url(${current.blur_data_url})`
                  : undefined,
                backgroundSize: "cover",
              }}
            />
          )}
        </button>

        {count > 1 && (
          <ul className="grid grid-cols-4 gap-2" aria-label="Фотографії товару">
            {images.map((image, index) => {
              const thumb = responsiveImage(image, 320);
              const isActive = index === active;
              return (
                <li key={image.media_id}>
                  <button
                    type="button"
                    onClick={() => setActive(index)}
                    aria-label={`Показати фото ${index + 1} з ${count}`}
                    aria-current={isActive}
                    className={`aspect-[4/5] w-full overflow-hidden rounded-2xl bg-accent-soft transition ${
                      isActive ? "ring-2 ring-rose ring-offset-2" : "opacity-75 hover:opacity-100"
                    }`}
                  >
                    {thumb && (
                      <img
                        src={thumb.src}
                        alt=""
                        loading="lazy"
                        decoding="async"
                        className="h-full w-full object-cover"
                        style={{
                          backgroundImage: image.blur_data_url
                            ? `url(${image.blur_data_url})`
                            : undefined,
                          backgroundSize: "cover",
                        }}
                      />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={`Фото ${name}`}
          className="fixed inset-0 z-50 flex flex-col bg-black/90"
          onTouchStart={onTouchStart}
          onTouchEnd={onTouchEnd}
        >
          <div className="flex items-center justify-between px-4 py-3 text-white">
            <span className="text-sm font-semibold tabular-nums">
              {active + 1} / {count}
            </span>
            <button
              type="button"
              onClick={close}
              autoFocus
              aria-label="Закрити перегляд"
              className="flex h-11 w-11 items-center justify-center rounded-full bg-white/10 text-white transition hover:bg-white/20"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="relative flex flex-1 items-center justify-center px-12">
            {lightboxSrc && (
              <img
                src={lightboxSrc}
                alt={name}
                className="max-h-full max-w-full rounded-2xl object-contain"
              />
            )}
            <button
              type="button"
              onClick={() => step(-1)}
              aria-label="Попереднє фото"
              className="absolute left-2 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-white/10 text-white transition hover:bg-white/20"
            >
              <ChevronLeft className="h-6 w-6" />
            </button>
            <button
              type="button"
              onClick={() => step(1)}
              aria-label="Наступне фото"
              className="absolute right-2 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-white/10 text-white transition hover:bg-white/20"
            >
              <ChevronRight className="h-6 w-6" />
            </button>
          </div>

          {count > 1 && (
            <div className="flex justify-center gap-1.5 pb-5">
              {images.map((_, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setActive(index)}
                  aria-label={`Фото ${index + 1}`}
                  className={`h-1.5 rounded-full transition-all ${
                    index === active ? "w-6 bg-white" : "w-1.5 bg-white/40"
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
}
