"""Texts sent to the shop (Ukrainian, plain text: works in Telegram, logs and SMS)."""

from ups_kulka.modules.notifications.application.dto import (
    OrderPlacedNotice,
    PaymentReceivedNotice,
)


def format_uah(kopecks: int) -> str:
    hryvnias, rest = divmod(kopecks, 100)
    amount = f"{hryvnias:,}".replace(",", " ")
    return f"{amount},{rest:02d} грн" if rest else f"{amount} грн"


def order_placed_text(notice: OrderPlacedNotice) -> str:
    lines = [f"🎈 Нове замовлення №{notice.number}", ""]
    lines += [
        f"• {line.name} × {line.quantity} = {format_uah(line.total_kopecks)}"
        for line in notice.lines
    ]
    lines += [
        "",
        f"Разом: {format_uah(notice.total_kopecks)}",
        f"👤 {notice.customer_name}, {notice.customer_phone}",
    ]
    if notice.delivery_method == "taxi":
        lines.append(f"🚕 Таксі на адресу: {notice.address}")
        lines.append("   Поїздку оплачує клієнт за тарифом таксі")
    else:
        lines.append("🏬 Самовивіз")
    if notice.delivery_date is not None:
        when = notice.delivery_date.strftime("%d.%m.%Y")
        lines.append(f"📅 {when} {notice.time_slot or ''}".rstrip())
    if notice.payment_method == "online":
        lines.append(
            "💳 Онлайн-оплата: очікуємо"
            if notice.payment_url
            else "💳 Онлайн-оплата не створилась — домовтеся про оплату з клієнтом"
        )
    else:
        lines.append("💵 Оплата при отриманні")
    if notice.comment:
        lines.append(f"💬 {notice.comment}")
    return "\n".join(lines)


def payment_received_text(notice: PaymentReceivedNotice) -> str:
    return (
        f"✅ Замовлення №{notice.order_number} оплачено онлайн: {format_uah(notice.amount_kopecks)}"
    )
