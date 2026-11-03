import type { ProductImageOut } from "@/shared/api/storefront";
import { responsiveImage } from "@/shared/lib/images";

const PLACEHOLDER_TONES = [
  ["#f5dede", "#e6b3b3", "#c06f6f"],
  ["#f6ead0", "#e2c27a", "#c06f6f"],
  ["#e3eef8", "#9cc3e6", "#e6b3b3"],
  ["#eee6f6", "#b9a0d6", "#e6b3b3"],
  ["#e6f4ec", "#9fd0b4", "#d99999"],
] as const;

function toneFor(seed: string) {
  let hash = 0;
  for (const char of seed) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return PLACEHOLDER_TONES[hash % PLACEHOLDER_TONES.length];
}

interface Props {
  image: ProductImageOut | undefined;
  alt: string;
  seed: string;
  sizes: string;
  priority?: boolean;
  className?: string;
}

/** Square product photo. Without a photo it draws a small balloon cluster instead. */
export function ProductImage({ image, alt, seed, sizes, priority = false, className = "" }: Props) {
  const picked = image ? responsiveImage(image) : null;
  if (image && picked) {
    return (
      <img
        src={picked.src}
        srcSet={picked.srcSet || undefined}
        sizes={sizes}
        alt={alt}
        width={image.width}
        height={image.height}
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
        decoding="async"
        className={`h-full w-full object-cover ${className}`}
        style={{
          backgroundImage: image.blur_data_url ? `url(${image.blur_data_url})` : undefined,
          backgroundSize: "cover",
        }}
      />
    );
  }

  const [bg, a, b] = toneFor(seed);
  return (
    <div
      role="img"
      aria-label={alt}
      className={`balloon-placeholder h-full w-full ${className}`}
      style={{ backgroundColor: bg }}
    >
      <i style={{ left: "24%", top: "16%", width: "36%", background: a }} />
      <i style={{ left: "50%", top: "28%", width: "30%", background: b }} />
      <i style={{ left: "10%", top: "40%", width: "24%", background: b }} />
    </div>
  );
}
