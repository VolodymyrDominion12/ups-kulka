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
from ups_kulka.modules.catalog.application.dto import UpdateProductCommand, UpdateTagSeoCommand
from ups_kulka.modules.catalog.application.legacy_import import (
    LegacyCatalog,
    plan_legacy_import,
)
from ups_kulka.modules.catalog.application.use_cases.admin_products import UpdateProduct
from ups_kulka.modules.catalog.application.use_cases.update_tag_seo import UpdateTagSeo
from ups_kulka.modules.catalog.domain.errors import SlugAlreadyTaken, TagSlugAlreadyTaken

DEFAULT_SEED = Path(__file__).resolve().parents[1] / "seed" / "old_site_catalog.json"


async def run(catalog: LegacyCatalog, *, photos: bool) -> int:
    plan = plan_legacy_import(catalog)
    container = Container()
    uow_factory = container.catalog.uow
    create_tag = container.catalog.create_tag()
    get_tag_detail = container.catalog.get_tag_detail()
    update_tag_seo = UpdateTagSeo(uow_factory)
    create_product = container.catalog.create_product()
    get_product = container.catalog.get_product()
    update_product = UpdateProduct(uow_factory)
    out = sys.stdout

    created_tags = updated_tags = created_products = updated_products = 0
    try:
        for tag_cmd in plan.tags:
            try:
                await create_tag(tag_cmd)
                created_tags += 1
            except TagSlugAlreadyTaken:
                if tag_cmd.seo_text:
                    detail = await get_tag_detail(tag_cmd.slug)
                    if not detail.seo_text:
                        await update_tag_seo(
                            UpdateTagSeoCommand(
                                tag_id=detail.id,
                                seo_title=tag_cmd.seo_title,
                                seo_description=tag_cmd.seo_description,
                                intro_text=tag_cmd.intro_text,
                                seo_text=tag_cmd.seo_text,
                                faq=tag_cmd.faq,
                            )
                        )
                        updated_tags += 1
        for product_cmd in plan.products:
            try:
                await create_product(product_cmd)
                created_products += 1
            except SlugAlreadyTaken:
                existing = await get_product(product_cmd.slug)
                existing_slugs = {t.slug for t in existing.tags}
                merged = tuple(
                    dict.fromkeys([*(t.slug for t in existing.tags), *product_cmd.tag_slugs])
                )
                if set(merged) != existing_slugs:
                    await update_product(
                        UpdateProductCommand(product_id=existing.id, tag_slugs=merged)
                    )
                    updated_products += 1
        out.write(
            f"tags: {created_tags} new, {updated_tags} SEO updated of {len(plan.tags)}; "
            f"products: {created_products} new, {updated_products} retagged "
            f"of {len(plan.products)}\n"
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
