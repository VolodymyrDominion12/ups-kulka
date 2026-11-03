import type { Metadata } from "next";

import { catalogApi } from "@/shared/api/storefront";
import { parsePage } from "@/shared/lib/paging";

import { CatalogPage } from "./CatalogPage";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ page?: string | string[] }>;

export async function generateMetadata({ searchParams }: { searchParams: SearchParams }): Promise<Metadata> {
  const page = parsePage((await searchParams).page);
  return {
    title: page > 1 ? `Каталог повітряних кульок — сторінка ${page}` : "Каталог повітряних кульок",
    description: "Композиції, фонтани, коробки-сюрпризи й фотозони з гелієвих кульок у Києві.",
    alternates: { canonical: page > 1 ? `/kulky?page=${page}` : "/kulky" },
  };
}

export default async function AllProductsPage({ searchParams }: { searchParams: SearchParams }) {
  const page = parsePage((await searchParams).page);
  const tags = await catalogApi.listTags();
  return <CatalogPage tags={tags} tag={null} page={page} />;
}
