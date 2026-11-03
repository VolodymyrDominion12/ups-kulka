"""Adapters from orders ports to other modules' public facades (AGENTS.md, section 3)."""

import uuid
from collections.abc import Mapping, Sequence

from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade
from ups_kulka.modules.catalog.application.public import CatalogFacade
from ups_kulka.modules.notifications.application.public import (
    NoticeLine,
    NotificationsFacade,
    OrderPlacedNotice,
)
from ups_kulka.modules.orders.application.dto import (
    CatalogProduct,
    CatalogProductAnalytics,
    CatalogProductTag,
)
from ups_kulka.modules.orders.domain.entities import Order
from ups_kulka.modules.payments.application.public import PaymentsFacade, StartPaymentCommand


class OrdersAdminAuthAdapter:
    def __init__(self, auth: AdminAuthFacade) -> None:
        self._auth = auth

    def require_admin(self, token: str | None) -> None:
        self._auth.verify_token(token)


class CatalogProductCatalog:
    def __init__(self, catalog: CatalogFacade) -> None:
        self._catalog = catalog

    async def products_for_order(
        self, ids: Sequence[uuid.UUID]
    ) -> Mapping[uuid.UUID, CatalogProduct]:
        found = await self._catalog.products_for_order(ids)
        return {
            product_id: CatalogProduct(
                id=p.id, name=p.name, price_kopecks=p.price_kopecks, is_active=p.is_active
            )
            for product_id, p in found.items()
        }

    async def products_for_analytics(self) -> list[CatalogProductAnalytics]:
        found = await self._catalog.products_for_analytics()
        return [
            CatalogProductAnalytics(
                id=p.id,
                slug=p.slug,
                name=p.name,
                price_kopecks=p.price_kopecks,
                is_active=p.is_active,
                created_at=p.created_at,
                tags=tuple(
                    CatalogProductTag(group=t.group, slug=t.slug, name=t.name) for t in p.tags
                ),
            )
            for p in found
        ]


class FacadePaymentStarter:
    def __init__(self, payments: PaymentsFacade) -> None:
        self._payments = payments

    @property
    def is_enabled(self) -> bool:
        return self._payments.is_enabled

    async def start(self, order: Order) -> str:
        if order.number is None:
            raise ValueError("order must be saved before payment")
        link = await self._payments.start(
            StartPaymentCommand(
                order_id=order.id,
                order_number=order.number,
                amount_kopecks=order.total.kopecks,
                description=f"Замовлення №{order.number} — УПС! Кулька",
            )
        )
        return link.page_url


class NotificationsOrderNotifier:
    def __init__(self, notifications: NotificationsFacade) -> None:
        self._notifications = notifications

    async def order_placed(self, order: Order, payment_url: str | None) -> None:
        if order.number is None:
            raise ValueError("order must be saved before notification")
        await self._notifications.order_placed(
            OrderPlacedNotice(
                number=order.number,
                lines=tuple(
                    NoticeLine(
                        name=item.product_name,
                        quantity=item.quantity,
                        total_kopecks=item.total.kopecks,
                    )
                    for item in order.items
                ),
                total_kopecks=order.total.kopecks,
                customer_name=order.customer.name,
                customer_phone=order.customer.phone.value,
                delivery_method=order.delivery.method.value,
                payment_method=order.payment_method.value,
                address=order.delivery.address,
                delivery_date=order.delivery.date,
                time_slot=order.delivery.time_slot,
                comment=order.customer.comment,
                payment_url=payment_url,
            )
        )
