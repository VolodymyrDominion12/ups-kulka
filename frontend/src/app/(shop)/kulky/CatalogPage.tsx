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

  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-8 sm:px-6">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <h1 className="font-display text-[clamp(30px,5vw,44px)] font-bold leading-tight tracking-tight">
          {h1}
        </h1>
        <p className="text-muted tabular-nums">{data.total} шт.</p>
      </div>

      {detail?.intro_text && (
        <p className="mb-5 max-w-[70ch] text-[15px] leading-relaxed text-[#3a3a3a]">
          {detail.intro_text}
        </p>
      )}

      <CatalogControls q={q} sort={sort} onSale={onSale} />

      <TagChips tags={tags} active={detail?.slug ?? null} />

      <div className="mt-6">
        <ProductGrid page={data} basePath={basePath} />
      </div>

      {detail?.seo_text && (
        <section className="mt-10 max-w-[70ch] text-[15px] leading-relaxed text-[#3a3a3a]">
          {detail.seo_text
            .split(/\n+/)
            .filter(Boolean)
            .map((paragraph, index) => (
              <p key={index} className="mb-3">
                {paragraph}
              </p>
            ))}
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
