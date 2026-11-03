/** First-touch marketing attribution sent with the order (specs/011-analytics). */

export interface MarketingAttribution {
  utm_source: string | null;
  utm_medium: string | null;
  utm_campaign: string | null;
  promo_code: string | null;
  landing_page: string | null;
}

const LIMITS = { utm_source: 120, utm_medium: 120, utm_campaign: 160, promo_code: 64 } as const;

function clip(value: string | null, max: number): string | null {
  const clean = value?.trim();
  return clean ? clean.slice(0, max) : null;
}

/** Reads attribution from a landing URL; returns null when the visit has no marks. */
export function attributionFromUrl(url: URL): MarketingAttribution | null {
  const q = url.searchParams;
  const result: MarketingAttribution = {
    utm_source: clip(q.get("utm_source"), LIMITS.utm_source),
    utm_medium: clip(q.get("utm_medium"), LIMITS.utm_medium),
    utm_campaign: clip(q.get("utm_campaign"), LIMITS.utm_campaign),
    promo_code: clip(q.get("promo") ?? q.get("promo_code"), LIMITS.promo_code),
    landing_page: clip(url.pathname, 300),
  };
  const hasMarks = result.utm_source || result.utm_medium || result.utm_campaign || result.promo_code;
  return hasMarks ? result : null;
}

export function parseStoredAttribution(raw: string | null): MarketingAttribution | null {
  if (!raw) return null;
  try {
    const data = JSON.parse(raw) as Partial<MarketingAttribution>;
    const pick = (v: unknown) => (typeof v === "string" ? v : null);
    return {
      utm_source: pick(data.utm_source),
      utm_medium: pick(data.utm_medium),
      utm_campaign: pick(data.utm_campaign),
      promo_code: pick(data.promo_code),
      landing_page: pick(data.landing_page),
    };
  } catch {
    return null;
  }
}
