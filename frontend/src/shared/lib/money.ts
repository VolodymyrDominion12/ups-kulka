/** Prices come from the API in kopecks (integers). Display only: the server computes totals. */
export function formatUah(kopecks: number): string {
  const hryvnias = Math.trunc(kopecks / 100);
  const rest = Math.abs(kopecks % 100);
  const whole = hryvnias.toLocaleString("uk-UA");
  return rest ? `${whole},${String(rest).padStart(2, "0")} грн` : `${whole} грн`;
}

/** Discount in whole percent, or 0 when there is no real discount. */
export function discountPercent(priceKopecks: number, oldPriceKopecks?: number | null): number {
  if (!oldPriceKopecks || oldPriceKopecks <= priceKopecks) return 0;
  return Math.round(((oldPriceKopecks - priceKopecks) * 100) / oldPriceKopecks);
}
