import Link from "next/link";

import { ProductCard } from "@/entities/product/ProductCard";
import { toCartProduct } from "@/entities/product/toCartProduct";
import { AddToCartButton } from "@/features/cart/AddToCartButton";
import type { ProductPageOut } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";

interface Props {
  page: ProductPageOut;
  /** Base path for page links: "/kulky" or "/kulky/<tag>". */
  basePath: string;
  emptyText?: string;
}

export function ProductGrid({ page, basePath, emptyText }: Props) {
  if (page.items.length === 0) {
    return (
      <div className="rounded-panel bg-white px-6 py-14 text-center">
        <p className="font-display text-xl font-bold">Тут скоро зʼявляться композиції</p>
        <p className="mx-auto mt-2 max-w-[44ch] text-muted">
          {emptyText ?? "Напишіть нам в Instagram, і ми зберемо подарунок під ваш запит."}
        </p>
        <a
          href={SHOP.instagramUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-6 inline-flex h-12 items-center rounded-full bg-accent-soft px-6 font-bold text-rose-deep"
        >
          Написати в Instagram
        </a>
      </div>
    );
  }

  const current = Math.floor(page.offset / page.limit) + 1;
  const pages = Math.max(1, Math.ceil(page.total / page.limit));
  const href = (n: number) => (n === 1 ? basePath : `${basePath}?page=${n}`);

  return (
    <>
      <ul className="grid grid-cols-2 gap-x-3 gap-y-7 sm:grid-cols-3 sm:gap-x-5 lg:grid-cols-4">
        {page.items.map((product, i) => (
          <ProductCard
            key={product.id}
            product={product}
            priority={i < 2}
            action={<AddToCartButton product={toCartProduct(product)} compact />}
          />
        ))}
      </ul>
      {pages > 1 && (
        <nav aria-label="Сторінки каталогу" className="mt-10 flex items-center justify-center gap-3">
          {current > 1 && (
            <Link
              href={href(current - 1)}
              rel="prev"
              className="inline-flex h-12 items-center rounded-full bg-accent-soft px-5 font-bold text-rose-deep"
            >
              Попередні
            </Link>
          )}
          <span className="tabular-nums text-muted">
            {current} з {pages}
          </span>
          {current < pages && (
            <Link
              href={href(current + 1)}
              rel="next"
              className="inline-flex h-12 items-center rounded-full bg-ink px-5 font-bold text-white"
            >
              Наступні
            </Link>
          )}
        </nav>
      )}
    </>
  );
}
