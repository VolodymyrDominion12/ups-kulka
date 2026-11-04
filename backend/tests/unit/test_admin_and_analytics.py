import uuid
from datetime import UTC, date, datetime

import pytest

from tests.fakes.catalog import FakeCatalogUnitOfWork, FakeMediaLookup
from tests.fakes.orders import FakeOrdersUnitOfWork, FakeProductCatalog
from ups_kulka.modules.catalog.application.dto import (
    CreateTagCommand,
    ListAdminProductsQuery,
    QuickCreateProductCommand,
    UpdateProductCommand,
)
from ups_kulka.modules.catalog.application.use_cases.admin_products import (
    ListAdminProducts,
    QuickCreateProduct,
    UpdateProduct,
)
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.list_tags import ListTags
from ups_kulka.modules.catalog.domain.errors import InvalidProduct, UnknownMediaAssets
from ups_kulka.modules.orders.application.dto import (
    AnalyticsDashboardQuery,
    CatalogProduct,
    CatalogProductAnalytics,
    CatalogProductTag,
    CreateAdminOrderCommand,
    GetAdminOrderQuery,
    ListAdminOrdersQuery,
    ListCustomersCrmQuery,
    OrderLineInput,
    UpdateAdminOrderCommand,
)
from ups_kulka.modules.orders.application.use_cases.admin_orders import (
    CreateAdminOrder,
    GetAdminOrder,
    ListAdminOrders,
    UpdateAdminOrder,
)
from ups_kulka.modules.orders.application.use_cases.analytics import (
    GetAnalyticsDashboard,
    GetOrderAnniversaries,
    ListCustomersCrm,
)


async def test_salon_quick_create_auto_slug_and_update() -> None:
    uow = FakeCatalogUnitOfWork()
    media_id_1 = uuid.uuid4()
    media_id_2 = uuid.uuid4()
    media_lookup = FakeMediaLookup(media_id_1, media_id_2)

    create_tag = CreateTag(uow)
    await create_tag(CreateTagCommand(group="occasion", slug="vypyska", name="Виписка"))
    await create_tag(CreateTagCommand(group="color", slug="pastelni", name="Пастельні"))

    tags = await ListTags(uow)()
    assert len(tags) == 2

    quick_create = QuickCreateProduct(uow, media_lookup=media_lookup)
    first = await quick_create(
        QuickCreateProductCommand(
            name="Ніжна виписка з ведмедиком",
            price_kopecks=165000,
            old_price_kopecks=190000,
            tag_slugs=("vypyska", "pastelni"),
            media_ids=(media_id_1,),
        )
    )
    assert first.slug == "nizhna-vypyska-z-vedmedykom"
    assert first.old_price_kopecks == 190000
    assert len(first.images) == 1
    assert first.images[0].media_id == media_id_1

    # Second composition with the same Ukrainian name gets automatic "-2" suffix!
    second = await quick_create(
        QuickCreateProductCommand(
            name="Ніжна виписка з ведмедиком",
            price_kopecks=175000,
            tag_slugs=("vypyska",),
            media_ids=(media_id_2,),
        )
    )
    assert second.slug == "nizhna-vypyska-z-vedmedykom-2"

    # Update product in 1 tap (price, deactivate, clear old price)
    update_uc = UpdateProduct(uow, media_lookup=media_lookup)
    updated = await update_uc(
        UpdateProductCommand(
            product_id=first.id,
            price_kopecks=155000,
            clear_old_price=True,
            is_active=False,
        )
    )
    assert updated.price_kopecks == 155000
    assert updated.old_price_kopecks is None
    assert updated.is_active is False

    admin_page = await ListAdminProducts(uow)(
        ListAdminProductsQuery(q="ведмедиком", is_active=False)
    )
    assert admin_page.total == 1
    assert admin_page.items[0].id == first.id

    with pytest.raises(InvalidProduct):
        await quick_create(
            QuickCreateProductCommand(
                name="Помилкова знижка",
                price_kopecks=150000,
                old_price_kopecks=120000,
            )
        )

    with pytest.raises(UnknownMediaAssets):
        await quick_create(
            QuickCreateProductCommand(
                name="Невідоме фото",
                price_kopecks=150000,
                media_ids=(uuid.uuid4(),),
            )
        )


async def test_admin_orders_and_marketing_analytics() -> None:
    today = date(2026, 11, 3)
    uow = FakeOrdersUnitOfWork()
    prod_id_1 = uuid.uuid4()
    prod_id_2 = uuid.uuid4()
    catalog = FakeProductCatalog(
        CatalogProduct(id=prod_id_1, name="Рожевий шик", price_kopecks=150000, is_active=True),
        CatalogProduct(id=prod_id_2, name="Космос 5 років", price_kopecks=200000, is_active=True),
        analytics_products=[
            CatalogProductAnalytics(
                id=prod_id_1,
                slug="rozhevyi-shyk",
                name="Рожевий шик",
                price_kopecks=150000,
                is_active=True,
                created_at=datetime(2026, 10, 1, tzinfo=UTC),
                tags=(
                    CatalogProductTag(
                        group="recipient", slug="dlia-divchynky", name="Для дівчинки"
                    ),
                    CatalogProductTag(group="color", slug="rozhevi", name="Рожеві"),
                ),
            ),
            CatalogProductAnalytics(
                id=prod_id_2,
                slug="kosmos-5",
                name="Космос 5 років",
                price_kopecks=200000,
                is_active=True,
                created_at=datetime(2026, 10, 1, tzinfo=UTC),
                tags=(CatalogProductTag(group="theme", slug="kosmos", name="Космос"),),
            ),
        ],
    )

    create_order = CreateAdminOrder(uow, catalog=catalog, today=lambda: today)
    order1 = await create_order(
        CreateAdminOrderCommand(
            customer_name="Марія",
            phone="093 111 22 33",
            delivery_method="taxi",
            address="вул. Оноре де Бальзака, 12",
            delivery_date=today,
            time_slot="12:00-14:00",
            payment_method="on_delivery",
            order_source="instagram",
            promo_code="INSTA10",
            discount_kopecks=15000,
            internal_note="Додати золоті грузики",
            lines=(OrderLineInput(product_id=prod_id_1, quantity=2),),
        )
    )
    assert order1.number == 1001
    assert order1.subtotal_kopecks == 300000
    assert order1.total_kopecks == 285000
    assert order1.order_source == "instagram"

    # Change status in salon: new -> confirmed -> assembled
    update_order = UpdateAdminOrder(uow)
    updated = await update_order(
        UpdateAdminOrderCommand(
            number=1001,
            status="assembled",
            status_note="Зібрано та сфотографовано в салоні",
            internal_note="Готово до відправки",
        )
    )
    assert updated.status == "assembled"
    assert len(updated.status_history) == 2
    assert updated.status_history[-1].to_status == "assembled"

    fetched = await GetAdminOrder(uow)(GetAdminOrderQuery(number=1001))
    assert fetched.internal_note == "Готово до відправки"

    listed = await ListAdminOrders(uow)(
        ListAdminOrdersQuery(status="assembled", delivery_date=today, q="Марія")
    )
    assert listed.total == 1

    # Pin order1's created_at to the tested period
    uow.orders.saved[0].created_at = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)

    # Place a past-year order to test Anniversary Radar & Repeat Customer CRM
    await create_order(
        CreateAdminOrderCommand(
            customer_name="Марія",
            phone="093 111 22 33",
            delivery_method="pickup",
            payment_method="on_delivery",
            order_source="walk_in",
            lines=(OrderLineInput(product_id=prod_id_1, quantity=1),),
        )
    )
    # Set the second order's date to ~1 year ago (2025-11-10, 7 days ahead of 2026-11-03)
    uow.orders.saved[1].created_at = datetime(2025, 11, 10, 10, 0, tzinfo=UTC)

    dashboard = await GetAnalyticsDashboard(uow, catalog=catalog, today=lambda: today)(
        AnalyticsDashboardQuery(date_from=date(2026, 11, 1), date_to=today)
    )
    assert dashboard.kpi.revenue_kopecks == 285000
    assert dashboard.kpi.orders_count == 1
    assert dashboard.kpi.units_sold == 2
    assert dashboard.kpi.repeat_customers_count == 1
    assert dashboard.by_order_source[0].key == "instagram"
    assert dashboard.promo_codes[0].promo_code == "INSTA10"
    assert dashboard.top_products[0].product_id == prod_id_1
    assert len(dashboard.zero_sales_products) == 1
    assert dashboard.zero_sales_products[0].product_id == prod_id_2
    assert len(dashboard.by_tag_group) == 2

    crm_page = await ListCustomersCrm(uow, today=lambda: today)(ListCustomersCrmQuery())
    assert crm_page.total == 1
    assert crm_page.items[0].orders_count == 2
    assert crm_page.items[0].segment in ("repeat", "vip")

    anniversaries = await GetOrderAnniversaries(uow, today=lambda: today)(days_ahead=14)
    assert len(anniversaries) == 1
    assert anniversaries[0].days_until == 7
    assert anniversaries[0].years_ago == 1


def test_domain_analytics_helpers() -> None:
    from ups_kulka.modules.orders.domain.analytics import (
        check_anniversary_window,
        classify_customer_segment,
        percentage_change,
    )

    assert percentage_change(150, 100) == 50.0
    assert percentage_change(50, 100) == -50.0
    assert percentage_change(0, 0) == 0.0
    assert percentage_change(100, 0) == 100.0

    assert (
        classify_customer_segment(orders_count=3, ltv_kopecks=100_000, days_since_last_order=10)
        == "vip"
    )
    assert (
        classify_customer_segment(orders_count=1, ltv_kopecks=450_000, days_since_last_order=10)
        == "vip"
    )
    assert (
        classify_customer_segment(orders_count=1, ltv_kopecks=100_000, days_since_last_order=400)
        == "sleeping"
    )
    assert (
        classify_customer_segment(orders_count=2, ltv_kopecks=200_000, days_since_last_order=30)
        == "repeat"
    )
    assert (
        classify_customer_segment(orders_count=1, ltv_kopecks=100_000, days_since_last_order=10)
        == "new"
    )

    today = date(2026, 2, 25)
    # Leap year Feb 29 -> Feb 28 in non-leap year
    leap_win = check_anniversary_window(date(2024, 2, 29), today=today, days_ahead=14)
    assert leap_win is not None
    assert leap_win.anniversary_date == date(2026, 2, 28)
    assert leap_win.years_ago == 2
    assert check_anniversary_window(date(2026, 2, 20), today=today) is None
    assert check_anniversary_window(date(2025, 8, 15), today=today) is None
