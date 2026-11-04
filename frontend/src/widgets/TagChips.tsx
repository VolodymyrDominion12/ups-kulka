"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronDown, X } from "lucide-react";

import type { TagOut } from "@/shared/api/storefront";

const ORDER = ["recipient", "occasion", "age", "type", "theme", "color"];

export const COLOR_SWATCH: Record<string, string> = {
  pastelni: "bg-gradient-to-tr from-pink-200 via-amber-100 to-teal-200 border-pink-300",
  rozhevi: "bg-pink-400 border-pink-500",
  "zoloto-chorni": "bg-gradient-to-tr from-neutral-900 to-amber-400 border-neutral-800",
  "blakytni-syni": "bg-sky-400 border-sky-500",
  "buzkovi-fioletovi": "bg-purple-400 border-purple-500",
  "zeleni-smarahdovi": "bg-emerald-500 border-emerald-600",
  chervoni: "bg-red-500 border-red-600",
  "sriblo-bili": "bg-gradient-to-tr from-neutral-100 to-slate-300 border-neutral-300",
};

export interface TagGroupSection<T extends TagOut = TagOut> {
  id: string;
  shortLabel: string;
  label: string;
  groups: string[];
  items: T[];
}

const GROUP_DEFS: Omit<TagGroupSection, "items">[] = [
  {
    id: "occasion",
    shortLabel: "Кому та свято",
    label: "Кому та на яке свято",
    groups: ["recipient", "occasion", "age"],
  },
  {
    id: "theme",
    shortLabel: "Формат і тематика",
    label: "Формат та тематика",
    groups: ["type", "theme"],
  },
  {
    id: "color",
    shortLabel: "Колір кульок",
    label: "Колір кульок",
    groups: ["color"],
  },
];

export function sortTags<T extends TagOut>(tags: readonly T[]): T[] {
  return [...tags].sort(
    (a, b) => ORDER.indexOf(a.group) - ORDER.indexOf(b.group) || a.name.localeCompare(b.name, "uk"),
  );
}

export function groupTagSections<T extends TagOut>(tags: readonly T[]): TagGroupSection<T>[] {
  const sorted = sortTags(tags);
  return GROUP_DEFS.map((def) => ({
    ...def,
    items: sorted.filter((t) => def.groups.includes(t.group)),
  })).filter((section) => section.items.length > 0);
}

export function TagChips({
  tags,
  active,
  compact = false,
}: {
  tags: TagOut[];
  active: string | null;
  compact?: boolean;
}) {
  const [openSectionId, setOpenSectionId] = useState<string | null>(null);
  const containerRef = useRef<HTMLElement | null>(null);

  const sorted = sortTags(tags);
  const sections = groupTagSections(tags);
  const activeTag = active ? sorted.find((t) => t.slug === active) ?? null : null;
  const activeSectionId = activeTag
    ? sections.find((s) => s.groups.includes(activeTag.group))?.id ?? null
    : null;

  useEffect(() => {
    setOpenSectionId(null);
  }, [active]);

  useEffect(() => {
    if (!openSectionId) return;

    function handlePointerDown(event: PointerEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpenSectionId(null);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpenSectionId(null);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [openSectionId]);

  const chip =
    "inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 text-sm font-semibold transition";
  const on = "border-ink bg-ink text-white";
  const off = "border-line bg-white text-ink hover:border-accent-dark";

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

  function toggleSection(id: string) {
    setOpenSectionId((prev) => (prev === id ? null : id));
  }

  const activeSwatch = activeTag ? COLOR_SWATCH[activeTag.slug] : undefined;

  return (
    <nav ref={containerRef} aria-label="Категорії та теги" className="relative">
      <div className="-mx-4 flex items-center gap-2 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:flex-wrap sm:px-0">
        <Link
          href="/kulky"
          aria-current={active === null ? "page" : undefined}
          onClick={() => setOpenSectionId(null)}
          className={`inline-flex h-10 shrink-0 items-center whitespace-nowrap rounded-full border px-4 text-sm font-semibold transition ${
            active === null ? on : off
          }`}
        >
          Усі композиції
        </Link>

        {sections.map((section) => {
          const isOpen = openSectionId === section.id;
          const hasActive = activeSectionId === section.id;
          return (
            <button
              key={section.id}
              type="button"
              aria-expanded={isOpen}
              aria-controls={`tag-panel-${section.id}`}
              onClick={() => toggleSection(section.id)}
              className={`inline-flex h-10 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-4 text-sm font-semibold transition ${
                isOpen
                  ? "border-rose bg-accent-soft/80 text-rose-deep shadow-sm"
                  : hasActive
                    ? "border-rose/60 bg-accent-soft/40 text-rose-deep hover:border-rose"
                    : "border-line bg-white text-ink hover:border-accent-dark"
              }`}
            >
              {section.id === "color" && (
                <span
                  aria-hidden="true"
                  className="h-3 w-3 shrink-0 rounded-full border border-pink-300 bg-gradient-to-tr from-pink-300 via-amber-200 to-sky-300"
                />
              )}
              <span>{section.shortLabel}</span>
              <span className="text-xs opacity-60 tabular-nums">({section.items.length})</span>
              <ChevronDown
                aria-hidden="true"
                className={`h-4 w-4 shrink-0 opacity-75 transition-transform duration-200 ${
                  isOpen ? "rotate-180" : ""
                }`}
              />
            </button>
          );
        })}

        {activeTag && (
          <>
            <span aria-hidden="true" className="mx-0.5 hidden h-5 w-px shrink-0 bg-line sm:inline-block" />
            <div className="inline-flex h-10 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border border-ink bg-ink pl-3.5 pr-1.5 text-sm font-semibold text-white">
              <button
                type="button"
                onClick={() => activeSectionId && toggleSection(activeSectionId)}
                className="inline-flex items-center gap-1.5 text-left"
                title="Натисніть, щоб змінити категорію"
              >
                {activeSwatch && (
                  <span
                    aria-hidden="true"
                    className={`h-3 w-3 shrink-0 rounded-full border ${activeSwatch}`}
                  />
                )}
                <span>{activeTag.name}</span>
              </button>
              <Link
                href="/kulky"
                aria-label={`Скинути фільтр ${activeTag.name}`}
                title="Скинути фільтр"
                className="ml-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/15 text-white transition hover:bg-white/30"
              >
                <X aria-hidden="true" className="h-3.5 w-3.5" />
              </Link>
            </div>
          </>
        )}
      </div>

      {sections.map((section) => {
        const isOpen = openSectionId === section.id;
        return (
          <div
            key={section.id}
            id={`tag-panel-${section.id}`}
            className={
              isOpen
                ? "mt-2.5 rounded-2xl border border-line bg-white p-3.5 shadow-sm sm:p-4"
                : "hidden"
            }
          >
            <div className="mb-2.5 flex items-center justify-between gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-muted">
                {section.label}
              </span>
              <button
                type="button"
                onClick={() => setOpenSectionId(null)}
                aria-label="Закрити панель категорій"
                className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold text-muted transition hover:bg-surface hover:text-ink"
              >
                <span>Згорнути</span>
                <X aria-hidden="true" className="h-3.5 w-3.5" />
              </button>
            </div>
            <ul className="flex flex-wrap gap-2">
              {section.items.map((tag) => {
                const swatch = COLOR_SWATCH[tag.slug];
                const isCurrent = active === tag.slug;
                return (
                  <li key={tag.id}>
                    <Link
                      href={isCurrent ? "/kulky" : `/kulky/${tag.slug}`}
                      aria-current={isCurrent ? "page" : undefined}
                      onClick={() => setOpenSectionId(null)}
                      className={`${chip} ${isCurrent ? on : off}`}
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
        );
      })}
    </nav>
  );
}
