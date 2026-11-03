"""Sales, marketing attribution, and customer CRM analytics use cases (specs/011-analytics)."""

from collections import defaultdict
from collections.abc import Callable
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from ups_kulka.modules.orders.application.dto import (
    AnalyticsDashboardDTO,
    AnalyticsDashboardQuery,
    BreakdownItemDTO,
    CustomerCrmDTO,
    DailySalesPointDTO,
    HourlyBucketDTO,
    ListCustomersCrmQuery,
    OrderAnniversaryDTO,
    ProductPerformanceDTO,
    PromoPerformanceDTO,
    SalesKpiDTO,
    TagGroupPerformanceDTO,
)
from ups_kulka.modules.orders.application.ports import (
    OrdersAdminGuard,
    OrdersUnitOfWorkFactory,
    ProductCatalog,
)
from ups_kulka.modules.orders.application.use_cases.place_order import kyiv_today
from ups_kulka.modules.orders.domain.analytics import (
    check_anniversary_window,
    classify_customer_segment,
    percentage_change,
)
from ups_kulka.modules.orders.domain.entities import Order, OrderStatus
from ups_kulka.shared.application.pagination import Page, PageRequest

KYIV = ZoneInfo("Europe/Kyiv")

_STATUS_LABELS: dict[str, str] = {
    "new": "Нові",
    "confirmed": "Прийнято",
    "assembled": "Зібрано",
    "shipped": "Відправлено",
    "completed": "Виконано",
    "cancelled": "Скасовано",
}
_DELIVERY_LABELS: dict[str, str] = {
    "pickup": "Самовивіз із салону",
    "taxi": "Доставка таксі",
}
_PAYMENT_LABELS: dict[str, str] = {
    "on_delivery": "При отриманні",
    "online": "Онлайн (Monobank)",
}
_SOURCE_LABELS: dict[str, str] = {
    "storefront": "Сайт (кошик)",
    "instagram": "Instagram Direct",
    "telegram": "Telegram",
    "phone": "Дзвінок у салон",
    "walk_in": "Візит у салон",
}


class GetAnalyticsDashboard:
    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        catalog: ProductCatalog,
        auth: OrdersAdminGuard | None = None,
        today: Callable[[], date] = kyiv_today,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog = catalog
        self._auth = auth
        self._today = today

    async def __call__(self, query: AnalyticsDashboardQuery) -> AnalyticsDashboardDTO:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)

        today = self._today()
        date_to = query.date_to or today
        date_from = query.date_from or (date_to - timedelta(days=29))
        if date_from > date_to:
            date_from, date_to = date_to, date_from

        span_days = max(1, (date_to - date_from).days + 1)
        prev_to = date_from - timedelta(days=1)
        prev_from = prev_to - timedelta(days=span_days - 1)

        async with self._uow_factory() as uow:
            all_orders = await uow.orders.list_all_for_analytics()
        catalog_products = await self._catalog.products_for_analytics()
        product_map = {p.id: p for p in catalog_products}

        period_orders: list[Order] = []
        prev_orders: list[Order] = []
        orders_per_phone_all_time: dict[str, int] = defaultdict(int)

        for o in all_orders:
            if o.status is not OrderStatus.CANCELLED:
                orders_per_phone_all_time[o.customer.phone.value] += 1
            order_day = o.created_at.astimezone(KYIV).date()
            if date_from <= order_day <= date_to:
                period_orders.append(o)
            elif prev_from <= order_day <= prev_to:
                prev_orders.append(o)

        active_period = [o for o in period_orders if o.status is not OrderStatus.CANCELLED]
        active_prev = [o for o in prev_orders if o.status is not OrderStatus.CANCELLED]
        cancelled_count = sum(1 for o in period_orders if o.status is OrderStatus.CANCELLED)

        rev = sum(o.total.kopecks for o in active_period)
        prev_rev = sum(o.total.kopecks for o in active_prev)
        cnt = len(active_period)
        prev_cnt = len(active_prev)
        aov = round(rev / cnt) if cnt > 0 else 0
        prev_aov = round(prev_rev / prev_cnt) if prev_cnt > 0 else 0
        units = sum(item.quantity for o in active_period for item in o.items)

        period_phones = {o.customer.phone.value for o in active_period}
        unique_cust = len(period_phones)
        repeat_cust = sum(1 for ph in period_phones if orders_per_phone_all_time.get(ph, 0) >= 2)
        repeat_rate = round((repeat_cust / unique_cust) * 100.0, 1) if unique_cust > 0 else 0.0

        kpi = SalesKpiDTO(
            revenue_kopecks=rev,
            previous_revenue_kopecks=prev_rev,
            revenue_change_percent=percentage_change(rev, prev_rev),
            orders_count=cnt,
            previous_orders_count=prev_cnt,
            orders_change_percent=percentage_change(cnt, prev_cnt),
            cancelled_orders_count=cancelled_count,
            avg_order_value_kopecks=aov,
            previous_avg_order_value_kopecks=prev_aov,
            avg_order_change_percent=percentage_change(aov, prev_aov),
            units_sold=units,
            unique_customers_count=unique_cust,
            repeat_customers_count=repeat_cust,
            repeat_customers_rate_percent=repeat_rate,
        )

        # Daily series
        daily_rev: dict[date, int] = defaultdict(int)
        daily_cnt: dict[date, int] = defaultdict(int)
        for o in active_period:
            d = o.created_at.astimezone(KYIV).date()
            daily_rev[d] += o.total.kopecks
            daily_cnt[d] += 1

        daily_series = tuple(
            DailySalesPointDTO(
                date=date_from + timedelta(days=i),
                revenue_kopecks=daily_rev[date_from + timedelta(days=i)],
                orders_count=daily_cnt[date_from + timedelta(days=i)],
            )
            for i in range(span_days)
        )

        by_status = _build_breakdown(
            period_orders,
            key_fn=lambda o: o.status.value,
            label_map=_STATUS_LABELS,
        )
        by_delivery = _build_breakdown(
            active_period,
            key_fn=lambda o: o.delivery.method.value,
            label_map=_DELIVERY_LABELS,
        )
        by_payment = _build_breakdown(
            active_period,
            key_fn=lambda o: o.payment_method.value,
            label_map=_PAYMENT_LABELS,
        )
        by_source = _build_breakdown(
            active_period,
            key_fn=lambda o: o.marketing.order_source.value,
            label_map=_SOURCE_LABELS,
        )
        by_utm_source = _build_breakdown(
            active_period,
            key_fn=lambda o: o.marketing.utm_source or "direct / органіка",
            label_map={},
        )
        by_utm_campaign = _build_breakdown(
            [o for o in active_period if o.marketing.utm_campaign],
            key_fn=lambda o: o.marketing.utm_campaign or "",
            label_map={},
        )
        by_landing = _build_breakdown(
            [o for o in active_period if o.marketing.landing_page],
            key_fn=lambda o: o.marketing.landing_page or "/",
            label_map={},
        )

        # Promo codes
        promo_cnt: dict[str, int] = defaultdict(int)
        promo_rev: dict[str, int] = defaultdict(int)
        promo_disc: dict[str, int] = defaultdict(int)
        for o in active_period:
            if o.marketing.promo_code:
                code = o.marketing.promo_code.upper()
                promo_cnt[code] += 1
                promo_rev[code] += o.total.kopecks
                promo_disc[code] += o.marketing.discount_kopecks
        promo_codes = tuple(
            PromoPerformanceDTO(
                promo_code=code,
                orders_count=promo_cnt[code],
                revenue_kopecks=promo_rev[code],
                discount_kopecks=promo_disc[code],
            )
            for code in sorted(promo_rev, key=lambda k: promo_rev[k], reverse=True)
        )

        # Product performance & tag group performance
        prod_units: dict[object, int] = defaultdict(int)
        prod_orders: dict[object, int] = defaultdict(int)
        prod_rev: dict[object, int] = defaultdict(int)
        prod_name: dict[object, str] = {}

        tag_units: dict[tuple[str, str, str], int] = defaultdict(int)
        tag_rev: dict[tuple[str, str, str], int] = defaultdict(int)

        for o in active_period:
            for item in o.items:
                pid = item.product_id
                item_rev = item.total.kopecks
                prod_units[pid] += item.quantity
                prod_orders[pid] += 1
                prod_rev[pid] += item_rev
                prod_name[pid] = item.product_name

                cat_prod = product_map.get(pid)
                if cat_prod:
                    for tag in cat_prod.tags:
                        tkey = (tag.group, tag.slug, tag.name)
                        tag_units[tkey] += item.quantity
                        tag_rev[tkey] += item_rev

        top_products = tuple(
            ProductPerformanceDTO(
                product_id=pid,  # type: ignore[arg-type]
                product_name=prod_name[pid],
                slug=product_map[pid].slug if pid in product_map else None,  # type: ignore[index]
                units_sold=prod_units[pid],
                orders_count=prod_orders[pid],
                revenue_kopecks=prod_rev[pid],
            )
            for pid in sorted(prod_rev, key=lambda k: prod_rev[k], reverse=True)[:20]
        )

        zero_sales_products = tuple(
            ProductPerformanceDTO(
                product_id=p.id,
                product_name=p.name,
                slug=p.slug,
                units_sold=0,
                orders_count=0,
                revenue_kopecks=0,
            )
            for p in catalog_products
            if p.is_active and p.id not in prod_units
        )[:20]

        by_tag_group = tuple(
            TagGroupPerformanceDTO(
                group=grp,
                tag_slug=tslug,
                tag_name=tname,
                units_sold=tag_units[(grp, tslug, tname)],
                revenue_kopecks=tag_rev[(grp, tslug, tname)],
            )
            for (grp, tslug, tname) in sorted(tag_rev, key=lambda k: tag_rev[k], reverse=True)
        )

        # Hourly heatmap
        heatmap_counts: dict[tuple[int, int], int] = defaultdict(int)
        for o in active_period:
            local_dt = o.created_at.astimezone(KYIV)
            heatmap_counts[(local_dt.weekday(), local_dt.hour)] += 1

        hourly_heatmap = tuple(
            HourlyBucketDTO(day_of_week=dow, hour=hr, orders_count=cnt_val)
            for (dow, hr), cnt_val in sorted(heatmap_counts.items())
        )

        return AnalyticsDashboardDTO(
            date_from=date_from,
            date_to=date_to,
            kpi=kpi,
            daily_series=daily_series,
            by_status=by_status,
            by_delivery_method=by_delivery,
            by_payment_method=by_payment,
            by_order_source=by_source,
            by_utm_source=by_utm_source,
            by_utm_campaign=by_utm_campaign,
            by_landing_page=by_landing,
            promo_codes=promo_codes,
            top_products=top_products,
            zero_sales_products=zero_sales_products,
            by_tag_group=by_tag_group,
            hourly_heatmap=hourly_heatmap,
        )


def _build_breakdown(
    orders: list[Order],
    *,
    key_fn: Callable[[Order], str],
    label_map: dict[str, str],
) -> tuple[BreakdownItemDTO, ...]:
    if not orders:
        return ()
    counts: dict[str, int] = defaultdict(int)
    revs: dict[str, int] = defaultdict(int)
    total_orders = len(orders)
    for o in orders:
        k = key_fn(o)
        counts[k] += 1
        revs[k] += o.total.kopecks
    return tuple(
        BreakdownItemDTO(
            key=k,
            label=label_map.get(k, k),
            orders_count=counts[k],
            revenue_kopecks=revs[k],
            share_percent=round((counts[k] / total_orders) * 100.0, 1),
        )
        for k in sorted(revs, key=lambda x: (revs[x], counts[x]), reverse=True)
    )


class ListCustomersCrm:
    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        auth: OrdersAdminGuard | None = None,
        today: Callable[[], date] = kyiv_today,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth
        self._today = today

    async def __call__(self, query: ListCustomersCrmQuery) -> Page[CustomerCrmDTO]:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)

        page_req = PageRequest(limit=query.limit, offset=query.offset)
        async with self._uow_factory() as uow:
            orders = await uow.orders.list_all_for_analytics()

        customers = _aggregate_customers(orders, today=self._today())
        if query.segment:
            customers = [c for c in customers if c.segment == query.segment]
        if query.q and query.q.strip():
            needle = query.q.strip().lower()
            customers = [
                c for c in customers if needle in c.phone.lower() or needle in c.name.lower()
            ]

        total = len(customers)
        sliced = customers[page_req.offset : page_req.offset + page_req.limit]
        return Page(
            items=tuple(sliced),
            total=total,
            limit=page_req.limit,
            offset=page_req.offset,
        )


def _aggregate_customers(orders: list[Order], *, today: date) -> list[CustomerCrmDTO]:
    grouped: dict[str, list[Order]] = defaultdict(list)
    for o in orders:
        if o.status is not OrderStatus.CANCELLED:
            grouped[o.customer.phone.value].append(o)

    result: list[CustomerCrmDTO] = []
    for phone, cust_orders in grouped.items():
        cust_orders.sort(key=lambda x: x.created_at)
        latest = cust_orders[-1]
        first = cust_orders[0]
        ltv = sum(o.total.kopecks for o in cust_orders)
        cnt = len(cust_orders)
        aov = round(ltv / cnt)
        days_since = max(0, (today - latest.created_at.astimezone(KYIV).date()).days)
        seg = classify_customer_segment(
            orders_count=cnt,
            ltv_kopecks=ltv,
            days_since_last_order=days_since,
        )
        item_names = list(
            dict.fromkeys(item.product_name for o in reversed(cust_orders) for item in o.items)
        )[:4]
        result.append(
            CustomerCrmDTO(
                phone=phone,
                name=latest.customer.name,
                orders_count=cnt,
                ltv_kopecks=ltv,
                avg_order_value_kopecks=aov,
                first_order_at=first.created_at,
                last_order_at=latest.created_at,
                days_since_last_order=days_since,
                segment=seg,
                favorite_items=tuple(item_names),
            )
        )
    result.sort(key=lambda c: (c.ltv_kopecks, c.orders_count), reverse=True)
    return result


class GetOrderAnniversaries:
    """Finds customers whose past-year balloon orders have an anniversary coming up."""

    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        auth: OrdersAdminGuard | None = None,
        today: Callable[[], date] = kyiv_today,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth
        self._today = today

    async def __call__(
        self,
        *,
        days_ahead: int = 14,
        auth_token: str | None = None,
    ) -> list[OrderAnniversaryDTO]:
        if self._auth is not None:
            self._auth.require_admin(auth_token)

        today = self._today()
        async with self._uow_factory() as uow:
            orders = await uow.orders.list_all_for_analytics()

        matches: list[OrderAnniversaryDTO] = []
        for o in orders:
            if o.status is OrderStatus.CANCELLED or o.number is None:
                continue
            target_date = o.delivery.date or o.created_at.astimezone(KYIV).date()
            win = check_anniversary_window(target_date, today=today, days_ahead=days_ahead)
            if win is not None:
                summary = ", ".join(f"{it.product_name} ×{it.quantity}" for it in o.items[:3])
                matches.append(
                    OrderAnniversaryDTO(
                        order_number=o.number,
                        customer_name=o.customer.name,
                        customer_phone=o.customer.phone.value,
                        original_date=target_date,
                        anniversary_date=win.anniversary_date,
                        days_until=win.days_until,
                        years_ago=win.years_ago,
                        total_kopecks=o.total.kopecks,
                        items_summary=summary,
                    )
                )
        matches.sort(key=lambda m: (m.days_until, -m.total_kopecks))
        return matches
