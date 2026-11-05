import Link from "next/link";

import { bannerApi, catalogApi } from "@/shared/api/storefront";
import { PAGE_SIZE } from "@/shared/config/shop";
import { Hero } from "@/widgets/hero";
import { Faq, Perks } from "@/widgets/InfoSections";
import { ProductGrid } from "@/widgets/ProductGrid";
import { ShopShell } from "@/widgets/ShopShell";
import { TagChips } from "@/widgets/TagChips";

// The home page lives at app/page.tsx (outside the (shop) group), so it adds the shop frame itself.
// Rendered per request; catalogue data is cached by fetch (see shared/api/storefront.ts).
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [tags, page, banner] = await Promise.all([
    catalogApi.listTags(),
    catalogApi.listProducts({ limit: PAGE_SIZE, offset: 0 }),
    bannerApi.getHome(),
  ]);
  const showcase = page.items.filter((p) => p.images.length > 0);

  return (
    <ShopShell>
      <Hero banner={banner} showcase={showcase} />
      <section aria-labelledby="catalog-title" className="mx-auto max-w-6xl px-4 pt-12 sm:px-6">
        <div className="mb-5 flex items-end justify-between gap-4">
          <h2 id="catalog-title" className="font-display text-[clamp(28px,4vw,40px)] font-bold tracking-tight">
            Каталог
          </h2>
          <Link href="/kulky" className="font-semibold text-rose-deep hover:underline">
            Усі {page.total}
          </Link>
        </div>
        <TagChips tags={tags} active={null} />
        <div className="mt-6">
          <ProductGrid page={{ ...page, total: Math.min(page.total, PAGE_SIZE) }} basePath="/kulky" />
        </div>
        {page.total > PAGE_SIZE && (
          <div className="mt-8 flex justify-center">
            <Link
              href="/kulky?page=2"
              className="inline-flex h-12 items-center rounded-full bg-accent-soft px-6 font-bold text-rose-deep"
            >
              Показати ще композиції
            </Link>
          </div>
        )}
      </section>
      <Perks />
      <Faq />
    </ShopShell>
  );
}
