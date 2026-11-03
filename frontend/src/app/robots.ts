import type { MetadataRoute } from "next";

import { SHOP } from "@/shared/config/shop";

// Read SITE_URL and SITE_NOINDEX when the server runs, not at build time.
export const dynamic = "force-dynamic";

export default function robots(): MetadataRoute.Robots {
  if (process.env.SITE_NOINDEX === "1") {
    // Staging: keep search engines out entirely.
    return { rules: { userAgent: "*", disallow: "/" } };
  }
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin", "/koshyk", "/oformlennia", "/diakuiemo", "/api/"],
    },
    sitemap: `${SHOP.siteUrl}/sitemap.xml`,
  };
}
