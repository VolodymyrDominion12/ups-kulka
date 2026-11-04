import type { Metadata } from "next";

import { catalogApi } from "@/shared/api/storefront";
import { parseOnSale, parsePage, parseQuery, parseSort } from "@/shared/lib/paging";

import { CatalogPage } from "./CatalogPage";

export const dynamic = "force-dynamic";

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
  searchParams,
}: {
  searchParams: SearchParams;
}): Promise<Metadata> {
  const { page, q, sort, onSale } = await readParams(searchParams);
  const hasFilters = Boolean(q || sort !== "newest" || onSale);
  return {
    title: page > 1 ? `Каталог повітряних кульок — сторінка ${page}` : "Каталог повітряних кульок",
    description: "Композиції, фонтани, коробки-сюрпризи й фотозони з гелієвих кульок у Києві.",
    alternates: { canonical: hasFilters ? "/kulky" : page > 1 ? `/kulky?page=${page}` : "/kulky" },
    robots: hasFilters ? { index: false, follow: true } : undefined,
  };
}

export default async function AllProductsPage({ searchParams }: { searchParams: SearchParams }) {
  const { page, q, sort, onSale } = await readParams(searchParams);
  const tags = await catalogApi.listTags();
  return <CatalogPage tags={tags} detail={null} page={page} q={q} sort={sort} onSale={onSale} />;
}
