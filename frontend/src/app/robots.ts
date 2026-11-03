import type { MetadataRoute } from "next";

import { SHOP } from "@/shared/config/shop";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin", "/koshyk", "/oformlennia", "/diakuiemo", "/api/"],
    },
    sitemap: `${SHOP.siteUrl}/sitemap.xml`,
  };
}
