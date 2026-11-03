import Link from "next/link";

import type { TagOut } from "@/shared/api/storefront";

const ORDER = ["occasion", "recipient", "type", "theme", "color", "age"];

export function TagChips({ tags, active }: { tags: TagOut[]; active: string | null }) {
  const sorted = [...tags].sort(
    (a, b) => ORDER.indexOf(a.group) - ORDER.indexOf(b.group) || a.name.localeCompare(b.name, "uk"),
  );
  const chip =
    "inline-flex h-10 shrink-0 items-center whitespace-nowrap rounded-full border px-4 font-semibold transition";
  const on = "border-ink bg-ink text-white";
  const off = "border-line bg-white hover:border-accent-dark";
  return (
    <nav aria-label="Категорії" className="-mx-4 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:px-0">
      <ul className="flex gap-2">
        <li>
          <Link href="/kulky" aria-current={active === null ? "page" : undefined} className={`${chip} ${active === null ? on : off}`}>
            Усе
          </Link>
        </li>
        {sorted.map((tag) => (
          <li key={tag.id}>
            <Link
              href={`/kulky/${tag.slug}`}
              aria-current={active === tag.slug ? "page" : undefined}
              className={`${chip} ${active === tag.slug ? on : off}`}
            >
              {tag.name}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
