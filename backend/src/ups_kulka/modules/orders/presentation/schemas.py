"""HTTP schemas of orders. They define the OpenAPI contract for the storefront and admin."""

import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from ups_kulka.modules.orders.application.dto import (
    AdminOrderDTO,
    AnalyticsDashboardDTO,
    BreakdownItemDTO,
    CheckoutOptionsDTO,
    CreateAdminOrderCommand,
    CustomerCrmDTO,
    DailySalesPointDTO,
    HourlyBucketDTO,
    OrderAnniversaryDTO,
    OrderLineInput,
    OrderStatusEntryDTO,
    PlacedOrderDTO,
    PlaceOrderCommand,
    ProductPerformanceDTO,
    PromoPerformanceDTO,
    SalesKpiDTO,
    TagGroupPerformanceDTO,
    UpdateAdminOrderCommand,
)
from ups_kulka.shared.application.pagination import Page

OrderStatusLiteral = Literal[
    "new",
    "confirmed",
    "assembled",
    "shipped",
    "completed",
    "cancelled",
]
OrderSourceLiteral = Literal[
    "storefront",
    "instagram",
    "telegram",
    "phone",
    "walk_in",
]


class CustomerIn(BaseModel):
    name: str = Field(min_length=1, max_length=120, examples=["Олена"])
    phone: str = Field(min_length=10, max_length=20, examples=["093 111 22 33"])
    comment: str = Field(default="", max_length=1000, examples=["Напис «З днем народження, Соня»"])


class DeliveryIn(BaseModel):
    method: Literal["pickup", "taxi"] = Field(
        description="taxi: the shop sends a taxi, the customer pays the fare separately"
    )
    address: str | None = Field(default=None, max_length=300, examples=["вул. Хрещатик, 1, кв. 5"])
    date: dt.date | None = None
    time_slot: str | None = Field(default=None, max_length=20, examples=["14–16"])


class OrderLineIn(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1, le=99)


class MarketingAttributionIn(BaseModel):
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=160)
    landing_page: str | None = Field(default=None, max_length=300)
    promo_code: str | None = Field(default=None, max_length=64)


class PlaceOrderIn(BaseModel):
    customer: CustomerIn
    delivery: DeliveryIn
    payment_method: Literal["on_delivery", "online"] = "on_delivery"
    items: list[OrderLineIn] = Field(min_length=1, max_length=50)
    marketing: MarketingAttributionIn | None = None

    def to_command(self) -> PlaceOrderCommand:
        mkt = self.marketing
        return PlaceOrderCommand(
            customer_name=self.customer.name,
            phone=self.customer.phone,
            comment=self.customer.comment,
            delivery_method=self.delivery.method,
            address=self.delivery.address,
            delivery_date=self.delivery.date,
            time_slot=self.delivery.time_slot,
            payment_method=self.payment_method,
            lines=tuple(OrderLineInput(i.product_id, i.quantity) for i in self.items),
            utm_source=mkt.utm_source if mkt else None,
            utm_medium=mkt.utm_medium if mkt else None,
            utm_campaign=mkt.utm_campaign if mkt else None,
            landing_page=mkt.landing_page if mkt else None,
            promo_code=mkt.promo_code if mkt else None,
        )


class CreateAdminOrderIn(BaseModel):
    customer: CustomerIn
    delivery: DeliveryIn
    payment_method: Literal["on_delivery", "online"] = "on_delivery"
    order_source: OrderSourceLiteral = "walk_in"
    items: list[OrderLineIn] = Field(min_length=1, max_length=50)
    promo_code: str | None = Field(default=None, max_length=64)
    discount_kopecks: int = Field(default=0, ge=0)
    internal_note: str = Field(default="", max_length=1000)

    def to_command(self, auth_token: str | None) -> CreateAdminOrderCommand:
        return CreateAdminOrderCommand(
            customer_name=self.customer.name,
            phone=self.customer.phone,
            comment=self.customer.comment,
            delivery_method=self.delivery.method,
            address=self.delivery.address,
            delivery_date=self.delivery.date,
            time_slot=self.delivery.time_slot,
            payment_method=self.payment_method,
            order_source=self.order_source,
            lines=tuple(OrderLineInput(i.product_id, i.quantity) for i in self.items),
            promo_code=self.promo_code,
            discount_kopecks=self.discount_kopecks,
            internal_note=self.internal_note,
            auth_token=auth_token,
        )


class UpdateAdminOrderIn(BaseModel):
    status: OrderStatusLiteral | None = None
    status_note: str = Field(default="", max_length=300)
    internal_note: str | None = Field(default=None, max_length=1000)
    delivery_date: dt.date | None = None
    time_slot: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=300)

    def to_command(self, number: int, auth_token: str | None) -> UpdateAdminOrderCommand:
        return UpdateAdminOrderCommand(
            number=number,
            status=self.status,
            status_note=self.status_note,
            internal_note=self.internal_note,
            delivery_date=self.delivery_date,
            time_slot=self.time_slot,
            address=self.address,
            auth_token=auth_token,
        )


class PlacedOrderItemOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    unit_price_kopecks: int
    quantity: int
    total_kopecks: int


class PlacedOrderOut(BaseModel):
    id: uuid.UUID
    number: int
    total_kopecks: int = Field(description="Goods only; the taxi fare is paid separately")
    delivery_method: str
    payment_method: str
    payment_url: str | None = Field(description="Payment page when payment_method is online")
    items: list[PlacedOrderItemOut]

    @classmethod
    def from_dto(cls, dto: PlacedOrderDTO) -> "PlacedOrderOut":
        return cls(
            id=dto.id,
            number=dto.number,
            total_kopecks=dto.total_kopecks,
            delivery_method=dto.delivery_method,
            payment_method=dto.payment_method,
            payment_url=dto.payment_url,
            items=[
                PlacedOrderItemOut(
                    product_id=i.product_id,
                    product_name=i.product_name,
                    unit_price_kopecks=i.unit_price_kopecks,
                    quantity=i.quantity,
                    total_kopecks=i.total_kopecks,
                )
                for i in dto.items
            ],
        )


class OrderStatusEntryOut(BaseModel):
    id: uuid.UUID
    from_status: str | None
    to_status: str
    note: str
    changed_at: dt.datetime

    @classmethod
    def from_dto(cls, dto: OrderStatusEntryDTO) -> "OrderStatusEntryOut":
        return cls(
            id=dto.id,
            from_status=dto.from_status,
            to_status=dto.to_status,
            note=dto.note,
            changed_at=dto.changed_at,
        )


class AdminOrderOut(BaseModel):
    id: uuid.UUID
    number: int
    status: str
    customer_name: str
    customer_phone: str
    comment: str
    delivery_method: str
    delivery_address: str | None
    delivery_date: dt.date | None
    delivery_slot: str | None
    payment_method: str
    subtotal_kopecks: int
    discount_kopecks: int
    total_kopecks: int
    order_source: str
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    landing_page: str | None
    promo_code: str | None
    internal_note: str
    created_at: dt.datetime
    updated_at: dt.datetime
    items: list[PlacedOrderItemOut]
    status_history: list[OrderStatusEntryOut]

    @classmethod
    def from_dto(cls, dto: AdminOrderDTO) -> "AdminOrderOut":
        return cls(
            id=dto.id,
            number=dto.number,
            status=dto.status,
            customer_name=dto.customer_name,
            customer_phone=dto.customer_phone,
            comment=dto.comment,
            delivery_method=dto.delivery_method,
            delivery_address=dto.delivery_address,
            delivery_date=dto.delivery_date,
            delivery_slot=dto.delivery_slot,
            payment_method=dto.payment_method,
            subtotal_kopecks=dto.subtotal_kopecks,
            discount_kopecks=dto.discount_kopecks,
            total_kopecks=dto.total_kopecks,
            order_source=dto.order_source,
            utm_source=dto.utm_source,
            utm_medium=dto.utm_medium,
            utm_campaign=dto.utm_campaign,
            landing_page=dto.landing_page,
            promo_code=dto.promo_code,
            internal_note=dto.internal_note,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            items=[
                PlacedOrderItemOut(
                    product_id=i.product_id,
                    product_name=i.product_name,
                    unit_price_kopecks=i.unit_price_kopecks,
                    quantity=i.quantity,
                    total_kopecks=i.total_kopecks,
                )
                for i in dto.items
            ],
            status_history=[OrderStatusEntryOut.from_dto(e) for e in dto.status_history],
        )


class AdminOrderPageOut(BaseModel):
    items: list[AdminOrderOut]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: Page[AdminOrderDTO]) -> "AdminOrderPageOut":
        return cls(
            items=[AdminOrderOut.from_dto(o) for o in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )


class CheckoutOptionsOut(BaseModel):
    delivery_methods: list[str]
    payment_methods: list[str]

    @classmethod
    def from_dto(cls, dto: CheckoutOptionsDTO) -> "CheckoutOptionsOut":
        return cls(
            delivery_methods=list(dto.delivery_methods),
            payment_methods=list(dto.payment_methods),
        )


# --- Analytics Out Schemas ---


class DailySalesPointOut(BaseModel):
    date: dt.date
    revenue_kopecks: int
    orders_count: int

    @classmethod
    def from_dto(cls, dto: DailySalesPointDTO) -> "DailySalesPointOut":
        return cls(
            date=dto.date,
            revenue_kopecks=dto.revenue_kopecks,
            orders_count=dto.orders_count,
        )


class BreakdownItemOut(BaseModel):
    key: str
    label: str
    orders_count: int
    revenue_kopecks: int
    share_percent: float

    @classmethod
    def from_dto(cls, dto: BreakdownItemDTO) -> "BreakdownItemOut":
        return cls(
            key=dto.key,
            label=dto.label,
            orders_count=dto.orders_count,
            revenue_kopecks=dto.revenue_kopecks,
            share_percent=dto.share_percent,
        )


class PromoPerformanceOut(BaseModel):
    promo_code: str
    orders_count: int
    revenue_kopecks: int
    discount_kopecks: int

    @classmethod
    def from_dto(cls, dto: PromoPerformanceDTO) -> "PromoPerformanceOut":
        return cls(
            promo_code=dto.promo_code,
            orders_count=dto.orders_count,
            revenue_kopecks=dto.revenue_kopecks,
            discount_kopecks=dto.discount_kopecks,
        )


class ProductPerformanceOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    slug: str | None
    units_sold: int
    orders_count: int
    revenue_kopecks: int

    @classmethod
    def from_dto(cls, dto: ProductPerformanceDTO) -> "ProductPerformanceOut":
        return cls(
            product_id=dto.product_id,
            product_name=dto.product_name,
            slug=dto.slug,
            units_sold=dto.units_sold,
            orders_count=dto.orders_count,
            revenue_kopecks=dto.revenue_kopecks,
        )


class TagGroupPerformanceOut(BaseModel):
    group: str
    tag_slug: str
    tag_name: str
    units_sold: int
    revenue_kopecks: int

    @classmethod
    def from_dto(cls, dto: TagGroupPerformanceDTO) -> "TagGroupPerformanceOut":
        return cls(
            group=dto.group,
            tag_slug=dto.tag_slug,
            tag_name=dto.tag_name,
            units_sold=dto.units_sold,
            revenue_kopecks=dto.revenue_kopecks,
        )


class HourlyBucketOut(BaseModel):
    day_of_week: int
    hour: int
    orders_count: int

    @classmethod
    def from_dto(cls, dto: HourlyBucketDTO) -> "HourlyBucketOut":
        return cls(
            day_of_week=dto.day_of_week,
            hour=dto.hour,
            orders_count=dto.orders_count,
        )


class SalesKpiOut(BaseModel):
    revenue_kopecks: int
    previous_revenue_kopecks: int
    revenue_change_percent: float | None
    orders_count: int
    previous_orders_count: int
    orders_change_percent: float | None
    cancelled_orders_count: int
    avg_order_value_kopecks: int
    previous_avg_order_value_kopecks: int
    avg_order_change_percent: float | None
    units_sold: int
    unique_customers_count: int
    repeat_customers_count: int
    repeat_customers_rate_percent: float

    @classmethod
    def from_dto(cls, dto: SalesKpiDTO) -> "SalesKpiOut":
        return cls(
            revenue_kopecks=dto.revenue_kopecks,
            previous_revenue_kopecks=dto.previous_revenue_kopecks,
            revenue_change_percent=dto.revenue_change_percent,
            orders_count=dto.orders_count,
            previous_orders_count=dto.previous_orders_count,
            orders_change_percent=dto.orders_change_percent,
            cancelled_orders_count=dto.cancelled_orders_count,
            avg_order_value_kopecks=dto.avg_order_value_kopecks,
            previous_avg_order_value_kopecks=dto.previous_avg_order_value_kopecks,
            avg_order_change_percent=dto.avg_order_change_percent,
            units_sold=dto.units_sold,
            unique_customers_count=dto.unique_customers_count,
            repeat_customers_count=dto.repeat_customers_count,
            repeat_customers_rate_percent=dto.repeat_customers_rate_percent,
        )


class AnalyticsDashboardOut(BaseModel):
    date_from: dt.date
    date_to: dt.date
    kpi: SalesKpiOut
    daily_series: list[DailySalesPointOut]
    by_status: list[BreakdownItemOut]
    by_delivery_method: list[BreakdownItemOut]
    by_payment_method: list[BreakdownItemOut]
    by_order_source: list[BreakdownItemOut]
    by_utm_source: list[BreakdownItemOut]
    by_utm_campaign: list[BreakdownItemOut]
    by_landing_page: list[BreakdownItemOut]
    promo_codes: list[PromoPerformanceOut]
    top_products: list[ProductPerformanceOut]
    zero_sales_products: list[ProductPerformanceOut]
    by_tag_group: list[TagGroupPerformanceOut]
    hourly_heatmap: list[HourlyBucketOut]

    @classmethod
    def from_dto(cls, dto: AnalyticsDashboardDTO) -> "AnalyticsDashboardOut":
        return cls(
            date_from=dto.date_from,
            date_to=dto.date_to,
            kpi=SalesKpiOut.from_dto(dto.kpi),
            daily_series=[DailySalesPointOut.from_dto(x) for x in dto.daily_series],
            by_status=[BreakdownItemOut.from_dto(x) for x in dto.by_status],
            by_delivery_method=[BreakdownItemOut.from_dto(x) for x in dto.by_delivery_method],
            by_payment_method=[BreakdownItemOut.from_dto(x) for x in dto.by_payment_method],
            by_order_source=[BreakdownItemOut.from_dto(x) for x in dto.by_order_source],
            by_utm_source=[BreakdownItemOut.from_dto(x) for x in dto.by_utm_source],
            by_utm_campaign=[BreakdownItemOut.from_dto(x) for x in dto.by_utm_campaign],
            by_landing_page=[BreakdownItemOut.from_dto(x) for x in dto.by_landing_page],
            promo_codes=[PromoPerformanceOut.from_dto(x) for x in dto.promo_codes],
            top_products=[ProductPerformanceOut.from_dto(x) for x in dto.top_products],
            zero_sales_products=[
                ProductPerformanceOut.from_dto(x) for x in dto.zero_sales_products
            ],
            by_tag_group=[TagGroupPerformanceOut.from_dto(x) for x in dto.by_tag_group],
            hourly_heatmap=[HourlyBucketOut.from_dto(x) for x in dto.hourly_heatmap],
        )


class CustomerCrmOut(BaseModel):
    phone: str
    name: str
    orders_count: int
    ltv_kopecks: int
    avg_order_value_kopecks: int
    first_order_at: dt.datetime
    last_order_at: dt.datetime
    days_since_last_order: int
    segment: str
    favorite_items: list[str]

    @classmethod
    def from_dto(cls, dto: CustomerCrmDTO) -> "CustomerCrmOut":
        return cls(
            phone=dto.phone,
            name=dto.name,
            orders_count=dto.orders_count,
            ltv_kopecks=dto.ltv_kopecks,
            avg_order_value_kopecks=dto.avg_order_value_kopecks,
            first_order_at=dto.first_order_at,
            last_order_at=dto.last_order_at,
            days_since_last_order=dto.days_since_last_order,
            segment=dto.segment,
            favorite_items=list(dto.favorite_items),
        )


class CustomerCrmPageOut(BaseModel):
    items: list[CustomerCrmOut]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: Page[CustomerCrmDTO]) -> "CustomerCrmPageOut":
        return cls(
            items=[CustomerCrmOut.from_dto(x) for x in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )


class OrderAnniversaryOut(BaseModel):
    order_number: int
    customer_name: str
    customer_phone: str
    original_date: dt.date
    anniversary_date: dt.date
    days_until: int
    years_ago: int
    total_kopecks: int
    items_summary: str

    @classmethod
    def from_dto(cls, dto: OrderAnniversaryDTO) -> "OrderAnniversaryOut":
        return cls(
            order_number=dto.order_number,
            customer_name=dto.customer_name,
            customer_phone=dto.customer_phone,
            original_date=dto.original_date,
            anniversary_date=dto.anniversary_date,
            days_until=dto.days_until,
            years_ago=dto.years_ago,
            total_kopecks=dto.total_kopecks,
            items_summary=dto.items_summary,
        )
