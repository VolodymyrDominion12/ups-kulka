import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Price } from "@/entities/product/Price";
import { ProductGallery } from "@/entities/product/ProductGallery";
import { toCartProduct } from "@/entities/product/toCartProduct";
import { AddToCartButton } from "@/features/cart/AddToCartButton";
import { catalogApi, type ProductOut } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";
import { responsiveImage } from "@/shared/lib/images";

export const dynamic = "force-dynamic";

type Params = Promise<{ slug: string }>;

function productJsonLd(product: ProductOut) {
  const cover = product.images[0] ? responsiveImage(product.images[0], 960) : null;
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: product.description || undefined,
    image: cover ? [`${SHOP.siteUrl}${cover.src}`] : undefined,
    url: `${SHOP.siteUrl}/tovar/${product.slug}`,
    offers: {
      "@type": "Offer",
      priceCurrency: "UAH",
      price: (product.price_kopecks / 100).toFixed(2),
      availability: "https://schema.org/InStock",
    },
  };
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const product = await catalogApi.getProduct((await params).slug);
  if (!product) return { title: "Товар не знайдено" };
  const cover = product.images[0] ? responsiveImage(product.images[0], 960) : null;
  return {
    title: `${product.name} — повітряні кульки`,
    description:
      product.description.slice(0, 160) ||
      `${product.name}: композиція з гелієвих кульок. Самовивіз або доставка таксі по Києву.`,
    alternates: { canonical: `/tovar/${product.slug}` },
    openGraph: cover ? { images: [{ url: cover.src }] } : undefined,
  };
}

export default async function ProductPage({ params }: { params: Params }) {
  const product = await catalogApi.getProduct((await params).slug);
  if (!product) notFound();

  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-6 sm:px-6">
      <nav aria-label="Навігація" className="mb-4 text-sm text-muted">
        <Link href="/kulky" className="hover:text-ink">
          Каталог
        </Link>
        {product.tags[0] && (
          <>
            <span aria-hidden="true"> / </span>
            <Link href={`/kulky/${product.tags[0].slug}`} className="hover:text-ink">
              {product.tags[0].name}
            </Link>
          </>
        )}
      </nav>

      <div className="grid gap-8 md:grid-cols-2">
        <ProductGallery images={product.images} name={product.name} seed={product.slug} />

        <div className="flex flex-col gap-5">
          <h1 className="font-display text-[clamp(28px,4vw,40px)] font-bold leading-tight tracking-tight">
            {product.name}
          </h1>
          <Price
            priceKopecks={product.price_kopecks}
            oldPriceKopecks={product.old_price_kopecks}
            className="text-2xl"
          />
          {product.description && (
            <p className="max-w-[60ch] whitespace-pre-line text-[#3a3a3a]">{product.description}</p>
          )}
          <div className="max-w-sm">
            <AddToCartButton product={toCartProduct(product)} />
          </div>
          <ul className="grid gap-1.5 text-[15px] text-muted">
            <li>Самовивіз або доставка таксі по Києву (поїздку оплачуєте ви).</li>
            <li>Кольори й напис можна змінити: напишіть у коментарі до замовлення.</li>
          </ul>
          {product.tags.length > 0 && (
            <ul className="flex flex-wrap gap-2" aria-label="Категорії товару">
              {product.tags.map((tag) => (
                <li key={tag.id}>
                  <Link
                    href={`/kulky/${tag.slug}`}
                    className="inline-flex h-9 items-center rounded-full bg-accent-soft px-3.5 text-sm font-semibold text-rose-deep"
                  >
                    {tag.name}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <script
        type="application/ld+json"
        // JSON from our own API; escaping "<" keeps it from closing the script tag.
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(productJsonLd(product)).replace(/</g, "\\u003c"),
        }}
      />
    </div>
  );
}
