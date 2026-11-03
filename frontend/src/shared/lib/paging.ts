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
