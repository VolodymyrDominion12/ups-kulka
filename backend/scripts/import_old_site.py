"""Import the catalogue and photos captured from oops.kylka.shop (specs/010-import-old-site).

Idempotent: existing tags and products (same slug) are skipped, products that
already have photos keep them. Safe to run again after a partial failure.

Usage:
    uv run python scripts/import_old_site.py [path/to/old_site_catalog.json] [--no-photos]
"""

import asyncio
import json
import sys
from pathlib import Path

from ups_kulka.container import Container
from ups_kulka.modules.catalog.application.legacy_import import (
    LegacyCatalog,
    plan_legacy_import,
)
from ups_kulka.modules.catalog.domain.errors import SlugAlreadyTaken, TagSlugAlreadyTaken

DEFAULT_SEED = Path(__file__).resolve().parents[1] / "seed" / "old_site_catalog.json"


async def run(catalog: LegacyCatalog, *, photos: bool) -> int:
    plan = plan_legacy_import(catalog)
    container = Container()
    create_tag = container.catalog.create_tag()
    create_product = container.catalog.create_product()
    out = sys.stdout

    created_tags = created_products = 0
    try:
        for tag_cmd in plan.tags:
            try:
                await create_tag(tag_cmd)
                created_tags += 1
            except TagSlugAlreadyTaken:
                pass
        for product_cmd in plan.products:
            try:
                await create_product(product_cmd)
                created_products += 1
            except SlugAlreadyTaken:
                pass
        out.write(
            f"tags: {created_tags} new of {len(plan.tags)}; "
            f"products: {created_products} new of {len(plan.products)}\n"
        )

        if not photos:
            return 0
        out.write(f"photos: importing {len(plan.photos)}, this takes a few minutes...\n")
        report = await container.catalog.import_legacy_photos()(plan.photos)
        out.write(
            f"photos: {len(report.imported)} imported, {len(report.skipped)} already had photos, "
            f"{len(report.failed)} failed\n"
        )
        for slug, reason in sorted(report.failed.items()):
            out.write(f"  failed {slug}: {reason}\n")
        return 1 if report.failed else 0
    finally:
        await container.engine().dispose()


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    seed = Path(args[0]) if args else DEFAULT_SEED
    catalog: LegacyCatalog = json.loads(seed.read_text(encoding="utf-8"))
    raise SystemExit(asyncio.run(run(catalog, photos="--no-photos" not in sys.argv)))


if __name__ == "__main__":
    main()
