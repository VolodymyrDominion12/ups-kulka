import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { catalogApi } from "@/shared/api/storefront";
import { parsePage } from "@/shared/lib/paging";

import { CatalogPage } from "../CatalogPage";

export const dynamic = "force-dynamic";

type Params = Promise<{ tag: string }>;
type SearchParams = Promise<{ page?: string | string[] }>;

async function findTag(slug: string) {
  const tags = await catalogApi.listTags();
  return { tags, tag: tags.find((t) => t.slug === slug) ?? null };
}

export async function generateMetadata({
  params,
  searchParams,
}: {
  params: Params;
  searchParams: SearchParams;
}): Promise<Metadata> {
  const { tag } = await findTag((await params).tag);
  if (!tag) return { title: "Категорію не знайдено" };
  const page = parsePage((await searchParams).page);
  const base = `/kulky/${tag.slug}`;
  return {
    title: `${tag.name} — повітряні кульки в Києві${page > 1 ? `, сторінка ${page}` : ""}`,
    description: `${tag.name}: композиції з гелієвих кульок. Самовивіз або доставка таксі по Києву.`,
    alternates: { canonical: page > 1 ? `${base}?page=${page}` : base },
  };
}

export default async function TagPage({ params, searchParams }: { params: Params; searchParams: SearchParams }) {
  const { tags, tag } = await findTag((await params).tag);
  if (!tag) notFound();
  const page = parsePage((await searchParams).page);
  return <CatalogPage tags={tags} tag={tag} page={page} />;
}
