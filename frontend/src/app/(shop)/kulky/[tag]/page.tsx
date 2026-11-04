import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { catalogApi } from "@/shared/api/storefront";
import { parseOnSale, parsePage, parseQuery, parseSort } from "@/shared/lib/paging";

import { CatalogPage } from "../CatalogPage";

export const dynamic = "force-dynamic";

type Params = Promise<{ tag: string }>;
type SearchParams = Promise<{
  page?: string | string[];
  q?: string | string[];
  sort?: string | string[];
  sale?: string | string[];
}>;

async function readParams(searchParams: SearchParams) {
  const sp = await searchParams;
  return {
    page: parsePage(sp.page),
    q: parseQuery(sp.q),
    sort: parseSort(sp.sort),
    onSale: parseOnSale(sp.sale),
  };
}

export async function generateMetadata({
  params,
  searchParams,
}: {
  params: Params;
  searchParams: SearchParams;
}): Promise<Metadata> {
  const slug = (await params).tag;
  const { page, q, sort, onSale } = await readParams(searchParams);
  const detail = await catalogApi.getTag(slug);
  if (!detail) return { title: "Категорію не знайдено" };
  const base = `/kulky/${detail.slug}`;
  const hasFilters = Boolean(q || sort !== "newest" || onSale);
  const title = detail.seo_title || `${detail.name} — повітряні кульки в Києві`;
  const canonical = hasFilters
    ? base
    : detail.is_indexable
      ? page > 1
        ? `${base}?page=${page}`
        : base
      : "/kulky";
  return {
    title: page > 1 ? `${title}, сторінка ${page}` : title,
    description:
      detail.seo_description ||
      `${detail.name}: композиції з гелієвих кульок. Самовивіз або доставка таксі по Києву.`,
    alternates: { canonical },
    robots: detail.is_indexable && !hasFilters ? undefined : { index: false, follow: true },
  };
}

export default async function TagPage({
  params,
  searchParams,
}: {
  params: Params;
  searchParams: SearchParams;
}) {
  const slug = (await params).tag;
  const { page, q, sort, onSale } = await readParams(searchParams);
  const [tags, detail] = await Promise.all([catalogApi.listTags(), catalogApi.getTag(slug)]);
  if (!detail) notFound();
  return <CatalogPage tags={tags} detail={detail} page={page} q={q} sort={sort} onSale={onSale} />;
}
