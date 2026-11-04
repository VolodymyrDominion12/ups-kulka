import Link from "next/link";

import {
  catalogApi,
  type ProductOut,
  type TagDetailOut,
  type TagSummaryOut,
} from "@/shared/api/storefront";
import { PAGE_SIZE, SHOP } from "@/shared/config/shop";
import type { ProductSort } from "@/shared/lib/paging";
import { CatalogControls } from "@/widgets/CatalogControls";
import { ProductGrid } from "@/widgets/ProductGrid";
import { TagChips } from "@/widgets/TagChips";

interface Props {
  tags: TagSummaryOut[];
  detail: TagDetailOut | null;
  page: number;
  q: string;
  sort: ProductSort;
  onSale: boolean;
}

function breadcrumbJsonLd(detail: TagDetailOut) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Головна", item: `${SHOP.siteUrl}/` },
      { "@type": "ListItem", position: 2, name: "Каталог", item: `${SHOP.siteUrl}/kulky` },
      {
        "@type": "ListItem",
        position: 3,
        name: detail.name,
        item: `${SHOP.siteUrl}/kulky/${detail.slug}`,
      },
    ],
  };
}

function faqJsonLd(detail: TagDetailOut) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: detail.faq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };
}

function itemListJsonLd(items: ProductOut[]) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: items.map((product, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: product.name,
      url: `${SHOP.siteUrl}/tovar/${product.slug}`,
    })),
  };
}

/** Shared body of /kulky and /kulky/[tag] (a collection landing page). */
export async function CatalogPage({ tags, detail, page, q, sort, onSale }: Props) {
  const data = await catalogApi.listProducts({
    tag: detail?.slug,
    limit: PAGE_SIZE,
    offset: (page - 1) * PAGE_SIZE,
    q: q || undefined,
    sort,
    on_sale: onSale,
  });
  const h1 = detail?.seo_title || detail?.name || "Усі композиції";
  const basePath = detail ? `/kulky/${detail.slug}` : "/kulky";

  // Related collections found on the products in this collection (for strong SEO internal linking)
  const relatedSlugs = new Set<string>();
  if (detail) {
    for (const product of data.items) {
      for (const t of product.tags) {
        if (t.slug !== detail.slug) {
          relatedSlugs.add(t.slug);
        }
      }
    }
  }
  const relatedTags = detail
    ? tags.filter((t) => relatedSlugs.has(t.slug) && t.product_count > 0).slice(0, 10)
    : [];

  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-6 sm:px-6">
      {detail && (
        <nav aria-label="Хлібні крихти" className="mb-3 text-sm text-muted">
          <Link href="/" className="hover:text-ink">
            Головна
          </Link>
          <span aria-hidden="true"> / </span>
          <Link href="/kulky" className="hover:text-ink">
            Каталог
          </Link>
          <span aria-hidden="true"> / </span>
          <span className="font-semibold text-ink">{detail.name}</span>
        </nav>
      )}

      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <h1 className="font-display text-[clamp(28px,5vw,42px)] font-bold leading-tight tracking-tight">
          {h1}
        </h1>
        <p className="text-muted tabular-nums">{data.total} шт.</p>
      </div>

      {detail?.intro_text && (
        <p className="mb-5 max-w-[72ch] text-[15px] leading-relaxed text-[#3a3a3a]">
          {detail.intro_text}
        </p>
      )}

      <CatalogControls q={q} sort={sort} onSale={onSale} />

      <TagChips tags={tags} active={detail?.slug ?? null} />

      <div className="mt-6">
        <ProductGrid page={data} basePath={basePath} />
      </div>

      {relatedTags.length > 0 && (
        <section className="mt-12 rounded-3xl border border-line bg-white p-5">
          <h2 className="font-display text-lg font-bold text-ink">
            Суміжні підбірки та кольори
          </h2>
          <p className="mt-1 text-xs text-muted">
            Перегляньте інші популярні категорії, що поєднуються з «{detail?.name}»:
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {relatedTags.map((tag) => (
              <Link
                key={tag.id}
                href={`/kulky/${tag.slug}`}
                className="inline-flex h-9 items-center gap-1.5 rounded-full bg-accent-soft/70 px-3.5 text-sm font-semibold text-rose-deep transition hover:bg-accent-soft"
              >
                {tag.name}
                <span className="text-xs opacity-70">({tag.product_count})</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {detail?.seo_text && (
        <section className="mt-10 rounded-3xl border border-line bg-white p-6">
          <h2 className="mb-3 font-display text-xl font-bold text-ink">
            Про підбірку «{detail.name}»
          </h2>
          <div className="max-w-[72ch] text-[15px] leading-relaxed text-[#3a3a3a]">
            {detail.seo_text
              .split(/\n+/)
              .filter(Boolean)
              .map((paragraph, index) => (
                <p key={index} className="mb-3 last:mb-0">
                  {paragraph}
                </p>
              ))}
          </div>
        </section>
      )}

      {detail && detail.faq.length > 0 && (
        <section className="mt-10">
          <h2 className="font-display text-xl font-bold">Часті питання</h2>
          <ul className="mt-4 grid gap-3">
            {detail.faq.map((item) => (
              <li key={item.question} className="rounded-2xl border border-line bg-white p-4">
                <p className="font-semibold">{item.question}</p>
                <p className="mt-1 text-[15px] text-muted">{item.answer}</p>
              </li>
            ))}
          </ul>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify(faqJsonLd(detail)).replace(/</g, "\\u003c"),
            }}
          />
        </section>
      )}

      {detail && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(itemListJsonLd(data.items)).replace(/</g, "\\u003c"),
          }}
        />
      )}

      {detail && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(breadcrumbJsonLd(detail)).replace(/</g, "\\u003c"),
          }}
        />
      )}
    </div>
  );
}
