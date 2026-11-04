import Link from "next/link";

import type { TagOut } from "@/shared/api/storefront";

const ORDER = ["recipient", "occasion", "age", "type", "theme", "color"];

const COLOR_SWATCH: Record<string, string> = {
  pastelni: "bg-gradient-to-tr from-pink-200 via-amber-100 to-teal-200 border-pink-300",
  rozhevi: "bg-pink-400 border-pink-500",
  "zoloto-chorni": "bg-gradient-to-tr from-neutral-900 to-amber-400 border-neutral-800",
  "blakytni-syni": "bg-sky-400 border-sky-500",
  "buzkovi-fioletovi": "bg-purple-400 border-purple-500",
  "zeleni-smarahdovi": "bg-emerald-500 border-emerald-600",
  chervoni: "bg-red-500 border-red-600",
  "sriblo-bili": "bg-gradient-to-tr from-neutral-100 to-slate-300 border-neutral-300",
};

const GROUP_SECTIONS: { label: string; groups: string[] }[] = [
  { label: "Кому та на яке свято", groups: ["recipient", "occasion", "age"] },
  { label: "Формат та тематика", groups: ["type", "theme"] },
  { label: "Колір кульок", groups: ["color"] },
];

export function TagChips({
  tags,
  active,
  compact = false,
}: {
  tags: TagOut[];
  active: string | null;
  compact?: boolean;
}) {
  const sorted = [...tags].sort(
    (a, b) => ORDER.indexOf(a.group) - ORDER.indexOf(b.group) || a.name.localeCompare(b.name, "uk"),
  );
  const chip =
    "inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 text-sm font-semibold transition";
  const on = "border-ink bg-ink text-white";
  const off = "border-line bg-white hover:border-accent-dark";

  if (compact || tags.length <= 10) {
    return (
      <nav
        aria-label="Категорії"
        className="-mx-4 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:px-0"
      >
        <ul className="flex gap-2">
          <li>
            <Link
              href="/kulky"
              aria-current={active === null ? "page" : undefined}
              className={`${chip} ${active === null ? on : off}`}
            >
              Усе
            </Link>
          </li>
          {sorted.map((tag) => {
            const swatch = COLOR_SWATCH[tag.slug];
            return (
              <li key={tag.id}>
                <Link
                  href={`/kulky/${tag.slug}`}
                  aria-current={active === tag.slug ? "page" : undefined}
                  className={`${chip} ${active === tag.slug ? on : off}`}
                >
                  {swatch && (
                    <span
                      aria-hidden="true"
                      className={`h-3 w-3 shrink-0 rounded-full border ${swatch}`}
                    />
                  )}
                  {tag.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    );
  }

  return (
    <nav aria-label="Категорії та теги" className="space-y-3">
      {GROUP_SECTIONS.map((section, idx) => {
        const items = sorted.filter((t) => section.groups.includes(t.group));
        if (items.length === 0) return null;
        return (
          <div key={section.label}>
            <div className="mb-1.5 text-xs font-bold uppercase tracking-wider text-muted">
              {section.label}
            </div>
            <div className="-mx-4 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:px-0">
              <ul className="flex gap-2 sm:flex-wrap">
                {idx === 0 && (
                  <li>
                    <Link
                      href="/kulky"
                      aria-current={active === null ? "page" : undefined}
                      className={`${chip} ${active === null ? on : off}`}
                    >
                      Усі композиції
                    </Link>
                  </li>
                )}
                {items.map((tag) => {
                  const swatch = COLOR_SWATCH[tag.slug];
                  return (
                    <li key={tag.id}>
                      <Link
                        href={`/kulky/${tag.slug}`}
                        aria-current={active === tag.slug ? "page" : undefined}
                        className={`${chip} ${active === tag.slug ? on : off}`}
                      >
                        {swatch && (
                          <span
                            aria-hidden="true"
                            className={`h-3 w-3 shrink-0 rounded-full border ${swatch}`}
                          />
                        )}
                        {tag.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        );
      })}
    </nav>
  );
}
