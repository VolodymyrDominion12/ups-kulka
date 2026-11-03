"""Import the catalogue captured from oops.kylka.shop (specs/010-import-old-site).

Idempotent: tags and products that already exist (same slug) are skipped.

Usage:
    uv run python scripts/import_old_site.py [path/to/old_site_catalog.json]
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


async def run(catalog: LegacyCatalog) -> None:
    plan = plan_legacy_import(catalog)
    container = Container()
    create_tag = container.catalog.create_tag()
    create_product = container.catalog.create_product()

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
    finally:
        await container.engine().dispose()

    sys.stdout.write(
        f"tags: {created_tags} new of {len(plan.tags)}; "
        f"products: {created_products} new of {len(plan.products)}\n"
    )


def main() -> None:
    seed = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SEED
    catalog: LegacyCatalog = json.loads(seed.read_text(encoding="utf-8"))
    asyncio.run(run(catalog))


if __name__ == "__main__":
    main()
