import type { MetadataRoute } from "next";

import { catalogApi, type ProductOut } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";

export const dynamic = "force-dynamic";

const API_PAGE = 100; // API maximum

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = SHOP.siteUrl;
  const entries: MetadataRoute.Sitemap = [
    { url: `${base}/`, changeFrequency: "daily", priority: 1 },
    { url: `${base}/kulky`, changeFrequency: "daily", priority: 0.9 },
  ];
  try {
    const tags = await catalogApi.listTags();
    entries.push(
      ...tags
        .filter((tag) => tag.is_indexable)
        .map((tag) => ({
          url: `${base}/kulky/${tag.slug}`,
          changeFrequency: "weekly" as const,
          priority: 0.8,
        })),
    );
    const products: ProductOut[] = [];
    for (let offset = 0; ; offset += API_PAGE) {
      const page = await catalogApi.listProducts({ limit: API_PAGE, offset });
      products.push(...page.items);
      if (page.items.length < API_PAGE || products.length >= page.total) break;
    }
    entries.push(
      ...products.map((p) => ({
        url: `${base}/tovar/${p.slug}`,
        lastModified: p.created_at,
        changeFrequency: "weekly" as const,
        priority: 0.7,
      })),
    );
  } catch {
    // API is down: serve the static part rather than failing the whole sitemap.
  }
  return entries;
}
