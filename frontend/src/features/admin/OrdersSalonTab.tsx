"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  Camera,
  CheckCircle2,
  Clock,
  Copy,
  Loader2,
  MapPin,
  MessageCircle,
  Phone,
  Plus,
  Search,
  Send,
  Truck,
  X,
} from "lucide-react";
import {
  adminApi,
  AdminOrderOut,
  formatMoneyUah,
  OrderSource,
  OrderStatus,
  ProductOut,
} from "@/shared/api/admin";

const STATUS_META: Record<
  OrderStatus,
  { label: string; badgeClass: string; next?: OrderStatus; nextLabel?: string }
> = {
  new: {
    label: "Нове",
    badgeClass: "bg-amber-100 text-amber-900",
    next: "confirmed",
    nextLabel: "✓ Підтвердити",
  },
  confirmed: {
    label: "В роботі",
    badgeClass: "bg-blue-100 text-blue-900",
    next: "assembled",
    nextLabel: "🎈 Зібрано (готово)",
  },
  assembled: {
    label: "Зібрано",
    badgeClass: "bg-purple-100 text-purple-900",
    next: "shipped",
    nextLabel: "🚕 Відправлено",
  },
  shipped: {
    label: "В дорозі",
    badgeClass: "bg-indigo-100 text-indigo-900",
    next: "completed",
    nextLabel: "🎉 Виконано",
  },
  completed: {
    label: "Виконано",
    badgeClass: "bg-emerald-100 text-emerald-900",
  },
  cancelled: {
    label: "Скасовано",
    badgeClass: "bg-neutral-200 text-neutral-600",
  },
};

const SOURCE_LABELS: Record<OrderSource, string> = {
  storefront: "🌐 Сайт",
  instagram: "📸 Instagram",
  telegram: "✈️ Telegram",
  phone: "📞 Дзвінок",
  walk_in: "🏪 Салон",
};

interface OrdersSalonTabProps {
  products: ProductOut[];
  onShootFromOrder: (prefill: { name: string; priceUah: number }) => void;
}

export function OrdersSalonTab({
  products,
  onShootFromOrder,
}: OrdersSalonTabProps) {
  const [orders, setOrders] = useState<AdminOrderOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [updatingNumber, setUpdatingNumber] = useState<number | null>(null);
  const [copiedAddressId, setCopiedAddressId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Manual salon order form state
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("+380");
  const [orderSource, setOrderSource] = useState<OrderSource>("instagram");
  const [deliveryMethod, setDeliveryMethod] = useState<"pickup" | "taxi">(
    "pickup"
  );
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [deliveryDate, setDeliveryDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [deliverySlot, setDeliverySlot] = useState("12:00-14:00");
  const [selectedProductId, setSelectedProductId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [internalNote, setInternalNote] = useState("");
  const [creatingOrder, setCreatingOrder] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadOrders = useCallback(async () => {
    setLoading(true);
    try {
      const page = await adminApi.listAdminOrders({
        status: statusFilter || undefined,
        q: searchQuery.trim() || undefined,
        limit: 50,
      });
      setOrders(page.items);
    } catch {
      // handled globally on 401
    } finally {
      setLoading(false);
    }
  }, [statusFilter, searchQuery]);

  useEffect(() => {
    void loadOrders();
  }, [loadOrders]);

  const handleStatusChange = async (
    orderNumber: number,
    nextStatus: OrderStatus
  ) => {
    setUpdatingNumber(orderNumber);
    try {
      const updated = await adminApi.updateAdminOrder(orderNumber, {
        status: nextStatus,
      });
      setOrders((prev) =>
        prev.map((o) => (o.number === orderNumber ? updated : o))
      );
    } finally {
      setUpdatingNumber(null);
    }
  };

  const handleCreateManualOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    const targetProductId = selectedProductId || products[0]?.id;
    if (!targetProductId) {
      setFormError("Спочатку додайте хоча б один товар у каталог");
      return;
    }
    setCreatingOrder(true);
    try {
      const created = await adminApi.createAdminOrder({
        customer: {
          name: customerName.trim() || "Клієнт салону",
          phone: customerPhone.trim(),
        },
        delivery: {
          method: deliveryMethod,
          address:
            deliveryMethod === "taxi"
              ? deliveryAddress.trim() || "За адресою"
              : undefined,
          date: deliveryDate || undefined,
          time_slot: deliverySlot || undefined,
        },
        payment_method: "on_delivery",
        order_source: orderSource,
        items: [{ product_id: targetProductId, quantity }],
        internal_note: internalNote.trim(),
      });
      setOrders((prev) => [created, ...prev]);
      setShowCreateModal(false);
      setCustomerName("");
      setCustomerPhone("+380");
      setInternalNote("");
    } catch (err) {
      setFormError(
        err instanceof Error ? err.message : "Не вдалося створити замовлення"
      );
    } finally {
      setCreatingOrder(false);
    }
  };

  const cleanPhoneDigits = (phone: string) => phone.replace(/[^\d]/g, "");

  return (
    <div className="space-y-4 pb-24">
      {/* Top Action & Search Bar */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-muted" />
          <input
            type="search"
            placeholder="Ім'я, телефон або №..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="min-h-[44px] w-full rounded-full border border-line bg-white pl-10 pr-4 text-sm text-ink focus:border-rose focus:outline-none"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowCreateModal(true)}
          className="inline-flex min-h-[44px] shrink-0 items-center gap-1.5 rounded-full bg-ink px-4 text-xs font-bold text-white shadow-sm active:scale-95"
        >
          <Plus className="h-4 w-4" /> Замовлення
        </button>
      </div>

      {/* Status filter pills */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {[
          { key: "", label: "Усі" },
          { key: "new", label: "🔥 Нові" },
          { key: "confirmed", label: "В роботі" },
          { key: "assembled", label: "🎈 Зібрані" },
          { key: "shipped", label: "🚕 В дорозі" },
          { key: "completed", label: "Виконані" },
        ].map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setStatusFilter(tab.key)}
            className={`min-h-[38px] shrink-0 rounded-full px-3.5 text-xs font-bold transition ${
              statusFilter === tab.key
                ? "bg-rose-deep text-white"
                : "border border-line bg-white text-ink"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12 text-muted">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : orders.length === 0 ? (
        <div className="rounded-3xl border border-line bg-white p-8 text-center">
          <p className="font-display text-base font-bold text-ink">
            Замовлень за цим фільтром немає
          </p>
          <p className="mt-1 text-xs text-muted">
            Додайте замовлення з Instagram або телефону кнопкою зверху
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => {
            const meta = STATUS_META[order.status];
            const firstItem = order.items[0];
            return (
              <article
                key={order.id}
                className="rounded-3xl border border-line bg-white p-4 shadow-sm"
              >
                {/* Header: Number, source, status, total */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="font-display text-base font-bold text-ink">
                        №{order.number}
                      </span>
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${meta.badgeClass}`}
                      >
                        {meta.label}
                      </span>
                      <span className="rounded-full bg-surface px-2 py-0.5 text-[11px] font-semibold text-muted">
                        {SOURCE_LABELS[order.order_source] ||
                          order.order_source}
                      </span>
                    </div>
                    <div className="mt-1 text-sm font-bold text-ink">
                      {order.customer_name} ·{" "}
                      <span className="text-muted">{order.customer_phone}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-display text-lg font-extrabold text-ink">
                      {formatMoneyUah(order.total_kopecks)}
                    </div>
                    {order.promo_code && (
                      <span className="text-[10px] font-bold text-emerald-700">
                        Промо: {order.promo_code}
                      </span>
                    )}
                  </div>
                </div>

                {/* Delivery slot & address */}
                <div className="mt-2.5 flex flex-wrap items-center gap-2 rounded-2xl bg-surface px-3 py-2 text-xs text-ink">
                  <span className="inline-flex items-center gap-1 font-semibold">
                    {order.delivery_method === "taxi" ? (
                      <>
                        <Truck className="h-3.5 w-3.5 text-rose-deep" /> Таксі
                      </>
                    ) : (
                      <>
                        <MapPin className="h-3.5 w-3.5 text-emerald-700" />{" "}
                        Самовивіз
                      </>
                    )}
                  </span>
                  {order.delivery_date && (
                    <span className="inline-flex items-center gap-1 text-muted">
                      <Clock className="h-3.5 w-3.5" />
                      {order.delivery_date}{" "}
                      {order.delivery_slot ? `(${order.delivery_slot})` : ""}
                    </span>
                  )}
                  {order.delivery_address && (
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          order.delivery_address || ""
                        );
                        setCopiedAddressId(order.id);
                        setTimeout(() => setCopiedAddressId(null), 1800);
                      }}
                      className="ml-auto inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1 text-[11px] font-semibold text-ink shadow-sm"
                    >
                      <Copy className="h-3 w-3" />
                      {copiedAddressId === order.id
                        ? "Скопійовано!"
                        : order.delivery_address}
                    </button>
                  )}
                </div>

                {/* Order items */}
                <ul className="mt-2.5 space-y-1 text-xs text-ink">
                  {order.items.map((item, idx) => (
                    <li
                      key={`${item.product_id}-${idx}`}
                      className="flex items-center justify-between"
                    >
                      <span className="font-medium">
                        🎈 {item.product_name}{" "}
                        <strong className="text-muted">×{item.quantity}</strong>
                      </span>
                      <span className="font-semibold">
                        {formatMoneyUah(item.total_kopecks)}
                      </span>
                    </li>
                  ))}
                </ul>

                {(order.comment || order.internal_note) && (
                  <div className="mt-2 rounded-xl border border-amber-200/80 bg-amber-50/70 px-3 py-1.5 text-xs text-amber-950">
                    {order.comment && <div>💬 Клієнт: {order.comment}</div>}
                    {order.internal_note && (
                      <div>📝 Флорист: {order.internal_note}</div>
                    )}
                  </div>
                )}

                {/* Quick Contact & Salon Actions */}
                <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-line pt-3">
                  <a
                    href={`tel:${order.customer_phone}`}
                    className="inline-flex min-h-[40px] items-center gap-1 rounded-full border border-line bg-surface px-3 text-xs font-bold text-ink"
                  >
                    <Phone className="h-3.5 w-3.5 text-emerald-700" /> Дзвінок
                  </a>
                  <a
                    href={`viber://chat?number=%2B${cleanPhoneDigits(
                      order.customer_phone
                    )}`}
                    className="inline-flex min-h-[40px] items-center gap-1 rounded-full border border-line bg-surface px-3 text-xs font-bold text-purple-800"
                  >
                    <MessageCircle className="h-3.5 w-3.5" /> Viber
                  </a>
                  <a
                    href={`https://t.me/+${cleanPhoneDigits(
                      order.customer_phone
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex min-h-[40px] items-center gap-1 rounded-full border border-line bg-surface px-3 text-xs font-bold text-sky-800"
                  >
                    <Send className="h-3.5 w-3.5" /> TG
                  </a>

                  {/* Shoot composition directly from order */}
                  <button
                    type="button"
                    onClick={() =>
                      onShootFromOrder({
                        name: firstItem?.product_name || "Композиція на замовлення",
                        priceUah: Math.round(order.total_kopecks / 100),
                      })
                    }
                    className="inline-flex min-h-[40px] items-center gap-1 rounded-full bg-accent-soft px-3 text-xs font-bold text-rose-deep"
                  >
                    <Camera className="h-3.5 w-3.5" /> На сайт
                  </button>

                  {meta.next && (
                    <button
                      type="button"
                      disabled={updatingNumber === order.number}
                      onClick={() =>
                        handleStatusChange(order.number, meta.next!)
                      }
                      className="ml-auto inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-ink px-4 text-xs font-bold text-white shadow-sm active:scale-95 disabled:opacity-50"
                    >
                      {updatingNumber === order.number ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <CheckCircle2 className="h-3.5 w-3.5" />
                      )}
                      {meta.nextLabel}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}

      {/* Quick Manual Salon Order Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-0 sm:items-center sm:p-4">
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-t-3xl bg-white p-5 shadow-xl sm:rounded-3xl">
            <div className="flex items-center justify-between">
              <h3 className="font-display text-lg font-bold text-ink">
                Швидке замовлення (Instagram / Телефон)
              </h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="rounded-full p-1.5 text-muted hover:bg-surface"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateManualOrder} className="mt-4 space-y-3">
              <div>
                <label className="text-xs font-bold text-muted">
                  Джерело звернення
                </label>
                <div className="mt-1 grid grid-cols-4 gap-1.5">
                  {(
                    [
                      ["instagram", "Instagram"],
                      ["telegram", "Telegram"],
                      ["phone", "Дзвінок"],
                      ["walk_in", "В салоні"],
                    ] as [OrderSource, string][]
                  ).map(([src, label]) => (
                    <button
                      key={src}
                      type="button"
                      onClick={() => setOrderSource(src)}
                      className={`min-h-[38px] rounded-xl text-xs font-bold ${
                        orderSource === src
                          ? "bg-rose-deep text-white"
                          : "border border-line bg-surface text-ink"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="text-xs font-bold text-muted">
                    Ім&apos;я клієнта
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Олена"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-muted">
                    Телефон (+380...)
                  </label>
                  <input
                    type="tel"
                    required
                    value={customerPhone}
                    onChange={(e) => setCustomerPhone(e.target.value)}
                    className="mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div className="col-span-2">
                  <label className="text-xs font-bold text-muted">
                    Композиція з каталогу
                  </label>
                  <select
                    value={selectedProductId || products[0]?.id || ""}
                    onChange={(e) => setSelectedProductId(e.target.value)}
                    className="mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-xs font-semibold"
                  >
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({formatMoneyUah(p.price_kopecks)})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-muted">К-сть</label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={quantity}
                    onChange={(e) =>
                      setQuantity(Math.max(1, Number(e.target.value)))
                    }
                    className="mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm font-bold"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setDeliveryMethod("pickup")}
                  className={`min-h-[40px] rounded-xl text-xs font-bold ${
                    deliveryMethod === "pickup"
                      ? "bg-ink text-white"
                      : "border border-line bg-surface text-ink"
                  }`}
                >
                  📍 Самовивіз із салону
                </button>
                <button
                  type="button"
                  onClick={() => setDeliveryMethod("taxi")}
                  className={`min-h-[40px] rounded-xl text-xs font-bold ${
                    deliveryMethod === "taxi"
                      ? "bg-ink text-white"
                      : "border border-line bg-surface text-ink"
                  }`}
                >
                  🚕 Доставка на таксі
                </button>
              </div>

              {deliveryMethod === "taxi" && (
                <input
                  type="text"
                  required
                  placeholder="Вулиця, будинок, під'їзд..."
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  className="min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm"
                />
              )}

              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={deliveryDate}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                  className="min-h-[42px] rounded-xl border border-line bg-surface px-3 text-xs"
                />
                <input
                  type="text"
                  placeholder="12:00-14:00"
                  value={deliverySlot}
                  onChange={(e) => setDeliverySlot(e.target.value)}
                  className="min-h-[42px] rounded-xl border border-line bg-surface px-3 text-xs"
                />
              </div>

              <input
                type="text"
                placeholder="Нотатка для флориста (напис на кульці, стрічка...)"
                value={internalNote}
                onChange={(e) => setInternalNote(e.target.value)}
                className="min-h-[42px] w-full rounded-xl border border-line bg-surface px-3 text-xs"
              />

              {formError && (
                <div className="rounded-xl bg-red-50 p-2.5 text-xs font-semibold text-red-700">
                  {formError}
                </div>
              )}

              <button
                type="submit"
                disabled={creatingOrder}
                className="flex min-h-[48px] w-full items-center justify-center rounded-full bg-rose-deep text-sm font-bold text-white shadow-pop"
              >
                {creatingOrder ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Створити замовлення"
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
