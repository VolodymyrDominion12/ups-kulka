/**
 * Typed API client for the UPS! Kulka mobile admin panel and storefront.
 * Mirrors contracts/openapi.json.
 */

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

export interface MediaAssetOut {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  width: number;
  height: number;
  url_prefix: string;
  blur_data_url: string;
  variants: Record<string, string>;
  created_at: string;
}

export type OrderStatus =
  | "new"
  | "confirmed"
  | "assembled"
  | "shipped"
  | "completed"
  | "cancelled";

export type OrderSource =
  | "storefront"
  | "instagram"
  | "telegram"
  | "phone"
  | "walk_in";

export interface PlacedOrderItemOut {
  product_id: string;
  product_name: string;
  unit_price_kopecks: number;
  quantity: number;
  total_kopecks: number;
}

export interface OrderStatusEntryOut {
  id: string;
  from_status: string | null;
  to_status: string;
  note: string;
  changed_at: string;
}

export interface AdminOrderOut {
  id: string;
  number: number;
  status: OrderStatus;
  customer_name: string;
  customer_phone: string;
  comment: string;
  delivery_method: "pickup" | "taxi";
  delivery_address: string | null;
  delivery_date: string | null;
  delivery_slot: string | null;
  payment_method: "on_delivery" | "online";
  subtotal_kopecks: number;
  discount_kopecks: number;
  total_kopecks: number;
  order_source: OrderSource;
  utm_source: string | null;
  utm_medium: string | null;
  utm_campaign: string | null;
  landing_page: string | null;
  promo_code: string | null;
  internal_note: string;
  created_at: string;
  updated_at: string;
  items: PlacedOrderItemOut[];
  status_history: OrderStatusEntryOut[];
}

export interface AdminOrderPageOut {
  items: AdminOrderOut[];
  total: number;
  limit: number;
  offset: number;
}

export interface SalesKpiOut {
  revenue_kopecks: number;
  previous_revenue_kopecks: number;
  revenue_change_percent: number | null;
  orders_count: number;
  previous_orders_count: number;
  orders_change_percent: number | null;
  cancelled_orders_count: number;
  avg_order_value_kopecks: number;
  previous_avg_order_value_kopecks: number;
  avg_order_change_percent: number | null;
  units_sold: number;
  unique_customers_count: number;
  repeat_customers_count: number;
  repeat_customers_rate_percent: number;
}

export interface DailySalesPointOut {
  date: string;
  revenue_kopecks: number;
  orders_count: number;
}

export interface BreakdownItemOut {
  key: string;
  label: string;
  orders_count: number;
  revenue_kopecks: number;
  share_percent: number;
}

export interface PromoPerformanceOut {
  promo_code: string;
  orders_count: number;
  revenue_kopecks: number;
  discount_kopecks: number;
}

export interface ProductPerformanceOut {
  product_id: string;
  product_name: string;
  slug: string | null;
  units_sold: number;
  orders_count: number;
  revenue_kopecks: number;
}

export interface TagGroupPerformanceOut {
  group: string;
  tag_slug: string;
  tag_name: string;
  units_sold: number;
  revenue_kopecks: number;
}

export interface HourlyBucketOut {
  day_of_week: number;
  hour: number;
  orders_count: number;
}

export interface AnalyticsDashboardOut {
  date_from: string;
  date_to: string;
  kpi: SalesKpiOut;
  daily_series: DailySalesPointOut[];
  by_status: BreakdownItemOut[];
  by_delivery_method: BreakdownItemOut[];
  by_payment_method: BreakdownItemOut[];
  by_order_source: BreakdownItemOut[];
  by_utm_source: BreakdownItemOut[];
  by_utm_campaign: BreakdownItemOut[];
  by_landing_page: BreakdownItemOut[];
  promo_codes: PromoPerformanceOut[];
  top_products: ProductPerformanceOut[];
  zero_sales_products: ProductPerformanceOut[];
  by_tag_group: TagGroupPerformanceOut[];
  hourly_heatmap: HourlyBucketOut[];
}

export interface CustomerCrmOut {
  phone: string;
  name: string;
  orders_count: number;
  ltv_kopecks: number;
  avg_order_value_kopecks: number;
  first_order_at: string;
  last_order_at: string;
  days_since_last_order: number;
  segment: "vip" | "repeat" | "new" | "sleeping";
  favorite_items: string[];
}

export interface CustomerCrmPageOut {
  items: CustomerCrmOut[];
  total: number;
  limit: number;
  offset: number;
}

export interface OrderAnniversaryOut {
  order_number: number;
  customer_name: string;
  customer_phone: string;
  original_date: string;
  anniversary_date: string;
  days_until: number;
  years_ago: number;
  total_kopecks: number;
  items_summary: string;
}

const TOKEN_STORAGE_KEY = "ups_kulka_admin_token";

export function getStoredAdminToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredAdminToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

export function formatMoneyUah(kopecks: number): string {
  const hryvnias = Math.round(kopecks / 100);
  return `${hryvnias.toLocaleString("uk-UA")} ₴`;
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredAdminToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    setStoredAdminToken(null);
    throw new Error("UNAUTHORIZED");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.message || `Помилка запиту (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export const adminApi = {
  login: async (password: string) => {
    const res = await apiRequest<{
      role: string;
      token: string;
      expires_at: string;
    }>("/api/v1/admin/auth/login", {
      method: "POST",
      body: JSON.stringify({ password }),
    });
    setStoredAdminToken(res.token);
    return res;
  },

  me: () =>
    apiRequest<{ role: string; token: string; expires_at: string }>(
      "/api/v1/admin/auth/me"
    ),

  uploadMedia: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return apiRequest<MediaAssetOut>("/api/v1/admin/media", {
      method: "POST",
      body: form,
    });
  },

  listTags: () => apiRequest<TagSummaryOut[]>("/api/v1/catalog/tags"),

  getTagSeo: (slug: string) =>
    apiRequest<TagDetailOut>(`/api/v1/catalog/tags/${encodeURIComponent(slug)}`),

  updateTagSeo: (
    tagId: string,
    payload: {
      seo_title?: string;
      seo_description?: string;
      intro_text?: string;
      seo_text?: string;
      faq?: { question: string; answer: string }[];
    }
  ) =>
    apiRequest<TagDetailOut>(`/api/v1/admin/catalog/tags/${tagId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  createTag: (payload: {
    group: string;
    slug: string;
    name: string;
  }) =>
    apiRequest<TagOut>("/api/v1/catalog/tags", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  quickCreateProduct: (payload: {
    name: string;
    price_kopecks: number;
    old_price_kopecks?: number | null;
    description?: string;
    is_active?: boolean;
    tag_slugs: string[];
    media_ids: string[];
  }) =>
    apiRequest<ProductOut>("/api/v1/admin/catalog/products", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateProduct: (
    productId: string,
    payload: {
      name?: string;
      description?: string;
      price_kopecks?: number;
      old_price_kopecks?: number | null;
      clear_old_price?: boolean;
      is_active?: boolean;
      tag_slugs?: string[];
      media_ids?: string[];
    }
  ) =>
    apiRequest<ProductOut>(`/api/v1/admin/catalog/products/${productId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listAdminProducts: (params: {
    q?: string;
    tag?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  } = {}) => {
    const search = new URLSearchParams();
    if (params.q) search.set("q", params.q);
    if (params.tag) search.set("tag", params.tag);
    if (params.is_active !== undefined)
      search.set("is_active", String(params.is_active));
    if (params.limit) search.set("limit", String(params.limit));
    if (params.offset) search.set("offset", String(params.offset));
    const qs = search.toString();
    return apiRequest<ProductPageOut>(
      `/api/v1/admin/catalog/products${qs ? `?${qs}` : ""}`
    );
  },

  listAdminOrders: (params: {
    status?: string;
    delivery_date?: string;
    delivery_method?: string;
    order_source?: string;
    q?: string;
    limit?: number;
  } = {}) => {
    const search = new URLSearchParams();
    if (params.status) search.set("status", params.status);
    if (params.delivery_date) search.set("delivery_date", params.delivery_date);
    if (params.delivery_method)
      search.set("delivery_method", params.delivery_method);
    if (params.order_source) search.set("order_source", params.order_source);
    if (params.q) search.set("q", params.q);
    if (params.limit) search.set("limit", String(params.limit));
    const qs = search.toString();
    return apiRequest<AdminOrderPageOut>(
      `/api/v1/admin/orders${qs ? `?${qs}` : ""}`
    );
  },

  updateAdminOrder: (
    number: number,
    payload: {
      status?: OrderStatus;
      status_note?: string;
      internal_note?: string;
      delivery_date?: string | null;
      time_slot?: string | null;
      address?: string | null;
    }
  ) =>
    apiRequest<AdminOrderOut>(`/api/v1/admin/orders/${number}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  createAdminOrder: (payload: {
    customer: { name: string; phone: string; comment?: string };
    delivery: {
      method: "pickup" | "taxi";
      address?: string;
      date?: string;
      time_slot?: string;
    };
    payment_method: "on_delivery" | "online";
    order_source: OrderSource;
    items: { product_id: string; quantity: number }[];
    promo_code?: string;
    discount_kopecks?: number;
    internal_note?: string;
  }) =>
    apiRequest<AdminOrderOut>("/api/v1/admin/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getAnalyticsDashboard: (params: {
    date_from?: string;
    date_to?: string;
  } = {}) => {
    const search = new URLSearchParams();
    if (params.date_from) search.set("date_from", params.date_from);
    if (params.date_to) search.set("date_to", params.date_to);
    const qs = search.toString();
    return apiRequest<AnalyticsDashboardOut>(
      `/api/v1/admin/analytics/dashboard${qs ? `?${qs}` : ""}`
    );
  },

  listCustomersCrm: (params: { q?: string; segment?: string } = {}) => {
    const search = new URLSearchParams();
    if (params.q) search.set("q", params.q);
    if (params.segment) search.set("segment", params.segment);
    const qs = search.toString();
    return apiRequest<CustomerCrmPageOut>(
      `/api/v1/admin/analytics/customers${qs ? `?${qs}` : ""}`
    );
  },

  getAnniversaries: (daysAhead = 14) =>
    apiRequest<OrderAnniversaryOut[]>(
      `/api/v1/admin/analytics/anniversaries?days_ahead=${daysAhead}`
    ),
};
