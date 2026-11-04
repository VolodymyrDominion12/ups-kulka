/** `?page=N` from the URL: a positive integer, anything else is page 1. */
export function parsePage(value: string | string[] | undefined): number {
  const raw = Array.isArray(value) ? value[0] : value;
  const page = Number(raw);
  return Number.isInteger(page) && page >= 1 && page <= 1000 ? page : 1;
}

/** `?order=N` on the thank-you page: a positive order number or null. */
export function parseOrderNumber(value: string | string[] | undefined): number | null {
  const raw = Array.isArray(value) ? value[0] : value;
  if (!raw || !/^\d{1,9}$/.test(raw)) return null;
  const number = Number(raw);
  return number >= 1 ? number : null;
}

export type ProductSort = "newest" | "price_asc" | "price_desc";

/** `?sort=` from the URL: one of the supported values, otherwise "newest". */
export function parseSort(value: string | string[] | undefined): ProductSort {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw === "price_asc" || raw === "price_desc" ? raw : "newest";
}

/** `?sale=1` / `?sale=true`: whether the "on sale" filter is active. */
export function parseOnSale(value: string | string[] | undefined): boolean {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw === "true" || raw === "1";
}

/** `?q=` search query, capped at 120 chars (matches the API limit). */
export function parseQuery(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return (raw ?? "").slice(0, 120);
}
