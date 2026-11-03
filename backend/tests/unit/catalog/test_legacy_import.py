import json
from pathlib import Path

from ups_kulka.modules.catalog.application.legacy_import import (
    LegacyCatalog,
    plan_legacy_import,
)
from ups_kulka.modules.catalog.domain.entities import Slug

SEED = Path(__file__).resolve().parents[3] / "seed" / "old_site_catalog.json"


def _catalog() -> LegacyCatalog:
    data: LegacyCatalog = json.loads(SEED.read_text(encoding="utf-8"))
    return data


def test_seed_imports_every_product_with_unique_valid_slugs() -> None:
    plan = plan_legacy_import(_catalog())

    slugs = [cmd.slug for cmd in plan.products]
    assert len(plan.products) == 211
    assert len(set(slugs)) == len(slugs)
    for slug in slugs:
        Slug(slug)  # raises if not a valid slug


def test_all_tags_created_even_empty_ones() -> None:
    plan = plan_legacy_import(_catalog())
    tag_slugs = {cmd.slug for cmd in plan.tags}
    used = {tag for cmd in plan.products for tag in cmd.tag_slugs}

    assert "dlia-noho" in tag_slugs  # owner decision: keep "Для нього" even when empty
    assert used <= tag_slugs


def test_owner_kept_product_is_imported() -> None:
    plan = plan_legacy_import(_catalog())
    assert any(cmd.name == "Сучка" for cmd in plan.products)


def test_prices_in_kopecks_and_order_by_old_id() -> None:
    catalog: LegacyCatalog = {
        "tags": [
            {"old_category": "Для неї", "group": "recipient", "slug": "dlia-nei", "name": "Для неї"}
        ],
        "products": [
            {"old_id": 20, "name": "Дракон", "price_uah": 550, "old_price_uah": None,
             "image_url": "", "tag": "dlia-nei"},
            {"old_id": 10, "name": "Дракон", "price_uah": 500, "old_price_uah": None,
             "image_url": "", "tag": "dlia-nei"},
            {"old_id": 30, "name": "Лев", "price_uah": 350, "old_price_uah": None,
             "image_url": "", "tag": "dlia-nei"},
        ],
    }  # fmt: skip
    plan = plan_legacy_import(catalog)

    assert [c.slug for c in plan.products] == ["drakon-10", "drakon-20", "lev"]
    assert [c.price_kopecks for c in plan.products] == [50000, 55000, 35000]


def test_plan_has_a_photo_per_product_with_matching_slugs() -> None:
    plan = plan_legacy_import(_catalog())
    product_slugs = {cmd.slug for cmd in plan.products}
    assert len(plan.photos) == 211
    assert {p.product_slug for p in plan.photos} == product_slugs
    assert all(p.image_url.startswith("https://oops.kylka.shop/img/p/") for p in plan.photos)


def test_only_real_discounts_become_old_prices() -> None:
    plan = plan_legacy_import(_catalog())
    on_sale = {cmd.name: (cmd.price_kopecks, cmd.old_price_kopecks) for cmd in plan.products
               if cmd.old_price_kopecks is not None}  # fmt: skip
    # Old site: two real discounts; "Happy" and "Зебра" had old price == price.
    assert on_sale == {
        "Набір повітряних кульок «Сяйво»": (390000, 430000),
        "Композиція «Love you»": (690100, 695000),
    }
