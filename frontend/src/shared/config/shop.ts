export const SHOP = {
  name: "УПС! Кулька",
  city: "Київ",
  phone: "+380936424049",
  phoneLabel: "093 642 40 49",
  instagramUrl: "https://www.instagram.com/oops_kulka",
  instagramHandle: "@oops_kulka",
  /** Absolute site URL for canonical links, sitemap and schema.org. */
  siteUrl: (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, ""),
} as const;

export const PAGE_SIZE = 24;
/** Seconds the storefront may reuse catalogue data before asking the API again. */
export const CATALOG_REVALIDATE_SECONDS = 300;
