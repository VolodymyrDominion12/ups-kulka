/** Picks pre-generated WebP variants (specs/009-media-pipeline) for <img srcset>. */

export interface ImageVariants {
  variants: Record<string, string>;
}

export interface ResponsiveImage {
  src: string;
  srcSet: string;
}

export function responsiveImage(image: ImageVariants, fallbackWidth = 640): ResponsiveImage | null {
  const widths = Object.keys(image.variants)
    .map((key) => /^(\d+)w$/.exec(key))
    .filter((m): m is RegExpExecArray => m !== null)
    .map((m) => Number(m[1]))
    .sort((a, b) => a - b);
  if (widths.length === 0) {
    const original = image.variants.original;
    return original ? { src: original, srcSet: "" } : null;
  }
  const srcSet = widths.map((w) => `${image.variants[`${w}w`]} ${w}w`).join(", ");
  const best = widths.find((w) => w >= fallbackWidth) ?? widths[widths.length - 1];
  return { src: image.variants[`${best}w`], srcSet };
}
