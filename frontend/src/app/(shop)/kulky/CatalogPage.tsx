import { catalogApi, type TagOut } from "@/shared/api/storefront";
import { PAGE_SIZE } from "@/shared/config/shop";
import { ProductGrid } from "@/widgets/ProductGrid";
import { TagChips } from "@/widgets/TagChips";

interface Props {
  tags: TagOut[];
  tag: TagOut | null;
  page: number;
}

/** Shared body of /kulky and /kulky/[tag]. */
export async function CatalogPage({ tags, tag, page }: Props) {
  const data = await catalogApi.listProducts({
    tag: tag?.slug,
    limit: PAGE_SIZE,
    offset: (page - 1) * PAGE_SIZE,
  });
  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-8 sm:px-6">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-2">
        <h1 className="font-display text-[clamp(30px,5vw,44px)] font-bold tracking-tight">
          {tag ? tag.name : "Усі композиції"}
        </h1>
        <p className="text-muted tabular-nums">{data.total} шт.</p>
      </div>
      <TagChips tags={tags} active={tag?.slug ?? null} />
      <div className="mt-6">
        <ProductGrid page={data} basePath={tag ? `/kulky/${tag.slug}` : "/kulky"} />
      </div>
    </div>
  );
}
