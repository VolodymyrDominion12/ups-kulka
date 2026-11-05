"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Search } from "lucide-react";

import type { ProductSort } from "@/shared/lib/paging";

interface Props {
  q: string;
  sort: ProductSort;
  onSale: boolean;
}

/** Search + sort + sale filter. Updates the URL so results stay shareable and server-rendered. */
export function CatalogControls({ q, sort, onSale }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const [value, setValue] = useState(q);

  useEffect(() => {
    setValue(q);
  }, [q]);

  function navigate(next: { q?: string; sort?: ProductSort; onSale?: boolean }) {
    const params = new URLSearchParams();
    const nextQ = next.q ?? q;
    const nextSort = next.sort ?? sort;
    const nextSale = next.onSale ?? onSale;
    if (nextQ) params.set("q", nextQ);
    if (nextSort && nextSort !== "newest") params.set("sort", nextSort);
    if (nextSale) params.set("sale", "1");
    const qs = params.toString();
    router.push(qs ? `${pathname}?${qs}` : pathname);
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    navigate({ q: value.trim() });
  }

  return (
    <div className="mb-3 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
      <form onSubmit={submit} className="relative">
        <Search className="pointer-events-none absolute left-3.5 top-3 h-4 w-4 text-muted" />
        <input
          type="search"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Пошук: єдиноріг, цифра 5..."
          aria-label="Пошук по каталогу"
          className="min-h-[44px] w-full rounded-full border border-line bg-white pl-10 pr-4 text-sm text-ink focus:border-rose focus:outline-none"
        />
      </form>

      <select
        value={sort}
        onChange={(event) => navigate({ sort: event.target.value as ProductSort })}
        aria-label="Сортування"
        className="min-h-[44px] rounded-full border border-line bg-white px-4 text-sm font-semibold text-ink focus:border-rose focus:outline-none"
      >
        <option value="newest">Новіші</option>
        <option value="price_asc">Ціна ↑</option>
        <option value="price_desc">Ціна ↓</option>
      </select>

      <button
        type="button"
        onClick={() => navigate({ onSale: !onSale })}
        aria-pressed={onSale}
        className={`min-h-[44px] rounded-full border px-4 text-sm font-semibold transition ${
          onSale ? "border-ink bg-ink text-white" : "border-line bg-white text-ink hover:border-accent-dark"
        }`}
      >
        Акції
      </button>
    </div>
  );
}
