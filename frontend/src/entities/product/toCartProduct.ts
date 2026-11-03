import type { ProductOut } from "@/shared/api/storefront";
import type { CartProduct } from "@/shared/lib/cart";
import { responsiveImage } from "@/shared/lib/images";

export function toCartProduct(product: ProductOut): CartProduct {
  const cover = product.images[0];
  return {
    id: product.id,
    slug: product.slug,
    name: product.name,
    priceKopecks: product.price_kopecks,
    imageUrl: cover ? (responsiveImage(cover, 320)?.src ?? null) : null,
  };
}
