/**
 * Storefront API client. Types mirror contracts/openapi.json.
 *
 * Catalogue reads run on the server (Server Components) and are cached;
 * the order is sent from the browser through the `/api` rewrite.
 */

import { CATALOG_REVALIDATE_SECONDS } from "@/shared/config/shop";
import type { PlaceOrderBody } from "@/shared/lib/checkout";

export interface TagOut {
  id: string;
  group: string;
  slug: string;
  name: string;
}

export interface TagSummaryOut extends TagOut {
  product_count: number;
  is_indexable: boolean;
}

export interface FaqItemOut {
  question: string;
  answer: string;
}

export interface TagDetailOut extends TagSummaryOut {
  seo_title: string;
  seo_description: string;
  intro_text: string;
  seo_text: string;
  faq: FaqItemOut[];
}

export interface ProductImageOut {
  media_id: string;
  position: number;
  url_prefix: string;
  blur_data_url: string;
  width: number;
  height: number;
  variants: Record<string, string>;
}

export interface ProductOut {
  id: string;
  slug: string;
  name: string;
  description: string;
  price_kopecks: number;
  old_price_kopecks?: number | null;
  is_active: boolean;
  created_at: string;
  tags: TagOut[];
  images: ProductImageOut[];
}

export interface ProductPageOut {
  items: ProductOut[];
  total: number;
  limit: number;
  offset: number;
}

export interface CheckoutOptionsOut {
  delivery_methods: string[];
  payment_methods: string[];
}

export interface PlacedOrderOut {
  id: string;
  number: number;
  total_kopecks: number;
  delivery_method: string;
  payment_method: string;
  payment_url: string | null;
}

export type BannerLayout = "balloons" | "image" | "split" | "collection";
export type BannerTheme = "rose" | "red" | "gold" | "dark";

export interface BannerImageOut {
  url_prefix: string;
  blur_data_url: string;
  width: number;
  height: number;
  variants: Record<string, string>;
}

/** Home hero for "now" (specs/017-home-banners). `campaign_id === null` = default balloons. */
export interface HomeBannerOut {
  layout: BannerLayout;
  campaign_id: string | null;
  theme: BannerTheme;
  headline: string;
  subtitle: string;
  cta_label: string;
  cta_url: string;
  cta2_label: string;
  cta2_url: string;
  image: BannerImageOut | null;
  image_mobile: BannerImageOut | null;
  image_alt: string;
  tag_slug: string | null;
  ribbon_text: string;
  ribbon_url: string;
}

export const DEFAULT_HOME_BANNER: HomeBannerOut = {
  layout: "balloons",
  campaign_id: null,
  theme: "rose",
  headline: "",
  subtitle: "",
  cta_label: "",
  cta_url: "",
  cta2_label: "",
  cta2_url: "",
  image: null,
  image_mobile: null,
  image_alt: "",
  tag_slug: null,
  ribbon_text: "",
  ribbon_url: "",
};

export class ApiUnavailableError extends Error {}

/** Server-side base URL: the internal Docker address in production. */
function serverBase(): string {
  return (
    process.env.API_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

async function getJson<T>(path: string): Promise<T | null> {
  let response: Response;
  try {
    response = await fetch(`${serverBase()}${path}`, {
      next: { revalidate: CATALOG_REVALIDATE_SECONDS, tags: ["catalog"] },
      headers: { Accept: "application/json" },
    });
  } catch (error) {
    throw new ApiUnavailableError(`API is not reachable: ${String(error)}`);
  }
  if (response.status === 404) return null;
  if (!response.ok) throw new ApiUnavailableError(`API ${path} answered ${response.status}`);
  return (await response.json()) as T;
}

export const catalogApi = {
  async listProducts(params: {
    tag?: string;
    limit: number;
    offset: number;
    q?: string;
    sort?: string;
    on_sale?: boolean;
  }) {
    const q = new URLSearchParams({ limit: String(params.limit), offset: String(params.offset) });
    if (params.tag) q.set("tag", params.tag);
    if (params.q) q.set("q", params.q);
    if (params.sort && params.sort !== "newest") q.set("sort", params.sort);
    if (params.on_sale) q.set("on_sale", "true");
    const page = await getJson<ProductPageOut>(`/api/v1/catalog/products?${q}`);
    return page ?? { items: [], total: 0, limit: params.limit, offset: params.offset };
  },

  getProduct(slug: string) {
    return getJson<ProductOut>(`/api/v1/catalog/products/${encodeURIComponent(slug)}`);
  },

  listRelated(slug: string) {
    return getJson<ProductOut[]>(`/api/v1/catalog/products/${encodeURIComponent(slug)}/related`);
  },

  async listTags() {
    return (await getJson<TagSummaryOut[]>("/api/v1/catalog/tags")) ?? [];
  },

  getTag(slug: string) {
    return getJson<TagDetailOut>(`/api/v1/catalog/tags/${encodeURIComponent(slug)}`);
  },
};

/** A campaign switch must show up fast, so the banner is cached much shorter than the catalogue. */
const BANNER_REVALIDATE_SECONDS = 60;

export const bannerApi = {
  /** Never throws: a banner problem must not take the home page down, so it falls back to the default hero. */
  async getHome(): Promise<HomeBannerOut> {
    try {
      const response = await fetch(`${serverBase()}/api/v1/storefront/home-banner`, {
        next: { revalidate: BANNER_REVALIDATE_SECONDS, tags: ["banner"] },
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return DEFAULT_HOME_BANNER;
      return (await response.json()) as HomeBannerOut;
    } catch {
      return DEFAULT_HOME_BANNER;
    }
  },
};

/** Browser-side calls (relative URLs, proxied to the API by next.config.ts). */
export const checkoutApi = {
  async options(): Promise<CheckoutOptionsOut> {
    const response = await fetch("/api/v1/orders/checkout-options");
    if (!response.ok) return { delivery_methods: ["pickup", "taxi"], payment_methods: ["on_delivery"] };
    return (await response.json()) as CheckoutOptionsOut;
  },

  async placeOrder(
    body: PlaceOrderBody,
  ): Promise<{ ok: true; order: PlacedOrderOut } | { ok: false; status: number; body: unknown }> {
    let response: Response;
    try {
      response = await fetch("/api/v1/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch {
      return { ok: false, status: 0, body: { message: "Немає звʼязку. Перевірте інтернет і спробуйте ще раз." } };
    }
    const data: unknown = await response.json().catch(() => null);
    if (!response.ok) return { ok: false, status: response.status, body: data };
    return { ok: true, order: data as PlacedOrderOut };
  },
};
