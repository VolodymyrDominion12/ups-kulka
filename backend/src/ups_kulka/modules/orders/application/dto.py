import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from ups_kulka.modules.orders.domain.entities import Order, OrderStatusEntry


@dataclass(frozen=True, slots=True)
class OrderLineInput:
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class PlaceOrderCommand:
    customer_name: str
    phone: str
    delivery_method: str
    payment_method: str
    lines: tuple[OrderLineInput, ...]
    address: str | None = None
    delivery_date: date | None = None
    time_slot: str | None = None
    comment: str = ""
    order_source: str = "storefront"
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    landing_page: str | None = None
    promo_code: str | None = None
    discount_kopecks: int = 0
    internal_note: str = ""


@dataclass(frozen=True, slots=True)
class CreateAdminOrderCommand:
    customer_name: str
    phone: str
    delivery_method: str
    payment_method: str
    lines: tuple[OrderLineInput, ...]
    order_source: str = "walk_in"
    address: str | None = None
    delivery_date: date | None = None
    time_slot: str | None = None
    comment: str = ""
    promo_code: str | None = None
    discount_kopecks: int = 0
    internal_note: str = ""
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class ListAdminOrdersQuery:
    status: str | None = None
    delivery_date: date | None = None
    delivery_method: str | None = None
    order_source: str | None = None
    q: str | None = None
    limit: int = 24
    offset: int = 0
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class GetAdminOrderQuery:
    number: int
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateAdminOrderCommand:
    number: int
    status: str | None = None
    status_note: str = ""
    internal_note: str | None = None
    delivery_date: date | None = None
    time_slot: str | None = None
    address: str | None = None
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class CatalogProduct:
    """What orders needs to know about a product (filled by the catalog facade adapter)."""

    id: uuid.UUID
    name: str
    price_kopecks: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class CatalogProductTag:
    group: str
    slug: str
    name: str


@dataclass(frozen=True, slots=True)
class CatalogProductAnalytics:
    id: uuid.UUID
    slug: str
    name: str
    price_kopecks: int
    is_active: bool
    created_at: datetime
    tags: tuple[CatalogProductTag, ...]


@dataclass(frozen=True, slots=True)
class PlacedOrderItemDTO:
    product_id: uuid.UUID
    product_name: str
    unit_price_kopecks: int
    quantity: int
    total_kopecks: int


@dataclass(frozen=True, slots=True)
class PlacedOrderDTO:
    id: uuid.UUID
    number: int
    total_kopecks: int
    delivery_method: str
    payment_method: str
    payment_url: str | None
    items: tuple[PlacedOrderItemDTO, ...]

    @classmethod
    def from_entity(cls, order: Order, payment_url: str | None) -> "PlacedOrderDTO":
        if order.number is None:
            raise ValueError("order must be saved before it is returned")
        return cls(
            id=order.id,
            number=order.number,
            total_kopecks=order.total.kopecks,
            delivery_method=order.delivery.method.value,
            payment_method=order.payment_method.value,
            payment_url=payment_url,
            items=tuple(
                PlacedOrderItemDTO(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price_kopecks=item.unit_price.kopecks,
                    quantity=item.quantity,
                    total_kopecks=item.total.kopecks,
                )
                for item in order.items
            ),
        )


@dataclass(frozen=True, slots=True)
class OrderStatusEntryDTO:
    id: uuid.UUID
    from_status: str | None
    to_status: str
    note: str
    changed_at: datetime

    @classmethod
    def from_entity(cls, entry: OrderStatusEntry) -> "OrderStatusEntryDTO":
        return cls(
            id=entry.id,
            from_status=entry.from_status.value if entry.from_status else None,
            to_status=entry.to_status.value,
            note=entry.note,
            changed_at=entry.changed_at,
        )


@dataclass(frozen=True, slots=True)
class AdminOrderDTO:
    id: uuid.UUID
    number: int
    status: str
    customer_name: str
    customer_phone: str
    comment: str
    delivery_method: str
    delivery_address: str | None
    delivery_date: date | None
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
    created_at: datetime
    updated_at: datetime
    items: tuple[PlacedOrderItemDTO, ...]
    status_history: tuple[OrderStatusEntryDTO, ...] = field(default_factory=tuple)

    @classmethod
    def from_entity(cls, order: Order) -> "AdminOrderDTO":
        if order.number is None:
            raise ValueError("order must have a number")
        return cls(
            id=order.id,
            number=order.number,
            status=order.status.value,
            customer_name=order.customer.name,
            customer_phone=order.customer.phone.value,
            comment=order.customer.comment,
            delivery_method=order.delivery.method.value,
            delivery_address=order.delivery.address,
            delivery_date=order.delivery.date,
            delivery_slot=order.delivery.time_slot,
            payment_method=order.payment_method.value,
            subtotal_kopecks=order.subtotal.kopecks,
            discount_kopecks=order.marketing.discount_kopecks,
            total_kopecks=order.total.kopecks,
            order_source=order.marketing.order_source.value,
            utm_source=order.marketing.utm_source,
            utm_medium=order.marketing.utm_medium,
            utm_campaign=order.marketing.utm_campaign,
            landing_page=order.marketing.landing_page,
            promo_code=order.marketing.promo_code,
            internal_note=order.internal_note,
            created_at=order.created_at,
            updated_at=order.updated_at or order.created_at,
            items=tuple(
                PlacedOrderItemDTO(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price_kopecks=item.unit_price.kopecks,
                    quantity=item.quantity,
                    total_kopecks=item.total.kopecks,
                )
                for item in order.items
            ),
            status_history=tuple(OrderStatusEntryDTO.from_entity(e) for e in order.status_history),
        )


@dataclass(frozen=True, slots=True)
class CheckoutOptionsDTO:
    delivery_methods: tuple[str, ...]
    payment_methods: tuple[str, ...]


# --- Analytics & Marketing DTOs (specs/011-analytics) ---


@dataclass(frozen=True, slots=True)
class AnalyticsDashboardQuery:
    date_from: date | None = None
    date_to: date | None = None
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class DailySalesPointDTO:
    date: date
    revenue_kopecks: int
    orders_count: int


@dataclass(frozen=True, slots=True)
class BreakdownItemDTO:
    key: str
    label: str
    orders_count: int
    revenue_kopecks: int
    share_percent: float


@dataclass(frozen=True, slots=True)
class PromoPerformanceDTO:
    promo_code: str
    orders_count: int
    revenue_kopecks: int
    discount_kopecks: int


@dataclass(frozen=True, slots=True)
class ProductPerformanceDTO:
    product_id: uuid.UUID
    product_name: str
    slug: str | None
    units_sold: int
    orders_count: int
    revenue_kopecks: int


@dataclass(frozen=True, slots=True)
class TagGroupPerformanceDTO:
    group: str
    tag_slug: str
    tag_name: str
    units_sold: int
    revenue_kopecks: int


@dataclass(frozen=True, slots=True)
class HourlyBucketDTO:
    day_of_week: int  # 0=Mon .. 6=Sun (ISO weekday - 1)
    hour: int  # 0..23
    orders_count: int


@dataclass(frozen=True, slots=True)
class SalesKpiDTO:
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


@dataclass(frozen=True, slots=True)
class AnalyticsDashboardDTO:
    date_from: date
    date_to: date
    kpi: SalesKpiDTO
    daily_series: tuple[DailySalesPointDTO, ...]
    by_status: tuple[BreakdownItemDTO, ...]
    by_delivery_method: tuple[BreakdownItemDTO, ...]
    by_payment_method: tuple[BreakdownItemDTO, ...]
    by_order_source: tuple[BreakdownItemDTO, ...]
    by_utm_source: tuple[BreakdownItemDTO, ...]
    by_utm_campaign: tuple[BreakdownItemDTO, ...]
    by_landing_page: tuple[BreakdownItemDTO, ...]
    promo_codes: tuple[PromoPerformanceDTO, ...]
    top_products: tuple[ProductPerformanceDTO, ...]
    zero_sales_products: tuple[ProductPerformanceDTO, ...]
    by_tag_group: tuple[TagGroupPerformanceDTO, ...]
    hourly_heatmap: tuple[HourlyBucketDTO, ...]


@dataclass(frozen=True, slots=True)
class ListCustomersCrmQuery:
    q: str | None = None
    segment: str | None = None
    limit: int = 24
    offset: int = 0
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class CustomerCrmDTO:
    phone: str
    name: str
    orders_count: int
    ltv_kopecks: int
    avg_order_value_kopecks: int
    first_order_at: datetime
    last_order_at: datetime
    days_since_last_order: int
    segment: str
    favorite_items: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class OrderAnniversaryDTO:
    order_number: int
    customer_name: str
    customer_phone: str
    original_date: date
    anniversary_date: date
    days_until: int
    years_ago: int
    total_kopecks: int
    items_summary: str
