import Link from "next/link";
import type { ReactNode } from "react";

import type { ProductOut } from "@/shared/api/storefront";
import { discountPercent } from "@/shared/lib/money";

import { Price } from "./Price";
import { ProductImage } from "./ProductImage";

interface Props {
  product: ProductOut;
  priority?: boolean;
  /** Slot for a feature (the add-to-cart button): entities do not import features. */
  action?: ReactNode;
}

export function ProductCard({ product, priority = false, action }: Props) {
  const discount = discountPercent(product.price_kopecks, product.old_price_kopecks);
  const href = `/tovar/${product.slug}`;
  return (
    <li className="flex flex-col">
      <Link
        href={href}
        tabIndex={-1}
        aria-hidden="true"
        className="relative block aspect-square overflow-hidden rounded-photo bg-accent-soft"
      >
        <ProductImage
          image={product.images[0]}
          alt=""
          seed={product.slug}
          sizes="(min-width: 1024px) 280px, (min-width: 640px) 33vw, 50vw"
          priority={priority}
          className="transition-transform duration-500 hover:scale-[1.04]"
        />
        {discount > 0 && (
          <span className="absolute left-3 top-3 rounded-full bg-rose px-2.5 py-1 text-[13px] font-bold text-white">
            −{discount}%
          </span>
        )}
      </Link>
      <div className="flex flex-1 flex-col gap-2 pt-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="text-[15px] font-semibold leading-snug">
            <Link href={href} className="hover:text-rose-deep">
              {product.name}
            </Link>
          </h3>
          <Price
            priceKopecks={product.price_kopecks}
            oldPriceKopecks={product.old_price_kopecks}
            className="mt-1 text-[17px]"
          />
        </div>
        {/* mt-auto keeps buttons on one line across a row when titles wrap */}
        <div className="mt-auto sm:mt-0">{action}</div>
      </div>
    </li>
  );
}
