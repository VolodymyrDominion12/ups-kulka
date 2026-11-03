import { afterEach, describe, expect, it, vi } from "vitest";

async function loadRobots() {
  vi.resetModules(); // SHOP reads SITE_URL when the module loads
  return (await import("../robots")).default();
}

describe("robots.txt", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("points to the sitemap of the runtime SITE_URL", async () => {
    vi.stubEnv("SITE_URL", "https://example.ua/");
    vi.stubEnv("SITE_NOINDEX", "");
    const robots = await loadRobots();
    expect(robots.sitemap).toBe("https://example.ua/sitemap.xml");
    expect(robots.rules).toMatchObject({ allow: "/" });
  });

  it("closes the whole site on staging", async () => {
    vi.stubEnv("SITE_NOINDEX", "1");
    const robots = await loadRobots();
    expect(robots.rules).toEqual({ userAgent: "*", disallow: "/" });
    expect(robots.sitemap).toBeUndefined();
  });
});
