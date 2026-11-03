"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  CalendarHeart,
  Flame,
  Loader2,
  Megaphone,
  MessageCircle,
  Send,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  adminApi,
  AnalyticsDashboardOut,
  CustomerCrmOut,
  formatMoneyUah,
  OrderAnniversaryOut,
} from "@/shared/api/admin";

type SubView = "sales" | "marketing" | "products" | "crm" | "anniversaries";

const SEGMENT_BADGES: Record<
  CustomerCrmOut["segment"],
  { label: string; className: string }
> = {
  vip: { label: "👑 VIP", className: "bg-amber-100 text-amber-900" },
  repeat: { label: "🔁 Постійний", className: "bg-emerald-100 text-emerald-900" },
  new: { label: "✨ Новий", className: "bg-sky-100 text-sky-900" },
  sleeping: {
    label: "💤 Давно не замовляв",
    className: "bg-neutral-200 text-neutral-700",
  },
};

export function AnalyticsMarketingTab() {
  const [subView, setSubView] = useState<SubView>("sales");
  const [daysPreset, setDaysPreset] = useState<number>(30);
  const [dashboard, setDashboard] = useState<AnalyticsDashboardOut | null>(
    null
  );
  const [customers, setCustomers] = useState<CustomerCrmOut[]>([]);
  const [segmentFilter, setSegmentFilter] = useState<string>("");
  const [anniversaries, setAnniversaries] = useState<OrderAnniversaryOut[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      const today = new Date();
      const fromDate = new Date();
      fromDate.setDate(today.getDate() - (daysPreset - 1));
      const dateTo = today.toISOString().slice(0, 10);
      const dateFrom = fromDate.toISOString().slice(0, 10);

      const [dashRes, crmRes, annivRes] = await Promise.all([
        adminApi.getAnalyticsDashboard({ date_from: dateFrom, date_to: dateTo }),
        adminApi.listCustomersCrm({ segment: segmentFilter || undefined }),
        adminApi.getAnniversaries(21),
      ]);
      setDashboard(dashRes);
      setCustomers(crmRes.items);
      setAnniversaries(annivRes);
    } catch {
      // handled on 401
    } finally {
      setLoading(false);
    }
  }, [daysPreset, segmentFilter]);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  const cleanPhoneDigits = (phone: string) => phone.replace(/[^\d]/g, "");

  const renderDeltaBadge = (delta: number | null) => {
    if (delta === null || delta === undefined) return null;
    const positive = delta >= 0;
    return (
      <span
        className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[11px] font-bold ${
          positive
            ? "bg-emerald-100 text-emerald-800"
            : "bg-red-100 text-red-700"
        }`}
      >
        {positive ? (
          <ArrowUpRight className="h-3 w-3" />
        ) : (
          <ArrowDownRight className="h-3 w-3" />
        )}
        {positive ? `+${delta}%` : `${delta}%`}
      </span>
    );
  };

  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center py-16 text-muted">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (!dashboard) return null;

  const maxDailyRevenue = Math.max(
    1,
    ...dashboard.daily_series.map((d) => d.revenue_kopecks)
  );

  return (
    <div className="space-y-4 pb-24">
      {/* Period Selector */}
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-bold text-muted">
          Період: {dashboard.date_from} — {dashboard.date_to}
        </span>
        <div className="flex gap-1">
          {[
            { days: 7, label: "7 дн" },
            { days: 30, label: "30 дн" },
            { days: 90, label: "90 дн" },
          ].map((p) => (
            <button
              key={p.days}
              type="button"
              onClick={() => setDaysPreset(p.days)}
              className={`min-h-[34px] rounded-full px-3 text-xs font-bold ${
                daysPreset === p.days
                  ? "bg-ink text-white"
                  : "border border-line bg-white text-ink"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sub-navigation pills */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {[
          { key: "sales", label: "💰 Продажі", icon: TrendingUp },
          { key: "marketing", label: "📣 Канали & UTM", icon: Megaphone },
          { key: "products", label: "🎈 Хіти & Теги", icon: Flame },
          { key: "crm", label: "👥 Клієнти (LTV)", icon: Users },
          {
            key: "anniversaries",
            label: `🎂 Радар свят (${anniversaries.length})`,
            icon: CalendarHeart,
          },
        ].map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setSubView(tab.key as SubView)}
            className={`min-h-[40px] shrink-0 rounded-full px-3.5 text-xs font-bold transition ${
              subView === tab.key
                ? "bg-rose-deep text-white shadow-sm"
                : "border border-line bg-white text-ink"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 1. SALES & KPI OVERVIEW */}
      {subView === "sales" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted">Виручка</span>
                {renderDeltaBadge(dashboard.kpi.revenue_change_percent)}
              </div>
              <div className="mt-1.5 font-display text-2xl font-extrabold text-ink">
                {formatMoneyUah(dashboard.kpi.revenue_kopecks)}
              </div>
              <div className="mt-1 text-[11px] text-muted">
                Попер. період:{" "}
                {formatMoneyUah(dashboard.kpi.previous_revenue_kopecks)}
              </div>
            </div>

            <div className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted">
                  Середній чек (AOV)
                </span>
                {renderDeltaBadge(dashboard.kpi.avg_order_change_percent)}
              </div>
              <div className="mt-1.5 font-display text-2xl font-extrabold text-ink">
                {formatMoneyUah(dashboard.kpi.avg_order_value_kopecks)}
              </div>
              <div className="mt-1 text-[11px] text-muted">
                Попер. період:{" "}
                {formatMoneyUah(dashboard.kpi.previous_avg_order_value_kopecks)}
              </div>
            </div>

            <div className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted">
                  Замовлень
                </span>
                {renderDeltaBadge(dashboard.kpi.orders_change_percent)}
              </div>
              <div className="mt-1.5 font-display text-2xl font-extrabold text-ink">
                {dashboard.kpi.orders_count}
              </div>
              <div className="mt-1 text-[11px] text-muted">
                Одиниць товару: {dashboard.kpi.units_sold} шт.
              </div>
            </div>

            <div className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted">
                  Повторні клієнти
                </span>
                <span className="rounded-full bg-accent-soft px-2 py-0.5 text-[11px] font-bold text-rose-deep">
                  {dashboard.kpi.repeat_customers_rate_percent}%
                </span>
              </div>
              <div className="mt-1.5 font-display text-2xl font-extrabold text-ink">
                {dashboard.kpi.repeat_customers_count} /{" "}
                {dashboard.kpi.unique_customers_count}
              </div>
              <div className="mt-1 text-[11px] text-muted">
                Унікальних покупців за період
              </div>
            </div>
          </div>

          {/* Daily Revenue Mini Bar Chart */}
          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              Динаміка виручки по днях
            </h3>
            <div className="mt-3 flex h-32 items-end gap-1 overflow-x-auto pb-1">
              {dashboard.daily_series.slice(-14).map((point) => {
                const heightPct = Math.max(
                  6,
                  Math.round((point.revenue_kopecks / maxDailyRevenue) * 100)
                );
                return (
                  <div
                    key={point.date}
                    className="flex min-w-[20px] flex-1 flex-col items-center gap-1"
                  >
                    <div
                      title={`${point.date}: ${formatMoneyUah(
                        point.revenue_kopecks
                      )} (${point.orders_count} зам.)`}
                      style={{ height: `${heightPct}%` }}
                      className={`w-full rounded-t-lg transition ${
                        point.revenue_kopecks > 0
                          ? "bg-rose-deep"
                          : "bg-surface"
                      }`}
                    />
                    <span className="text-[9px] text-muted">
                      {point.date.slice(8, 10)}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Delivery & Payment Split */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <h3 className="font-display text-sm font-bold text-ink">
                Доставка vs Самовивіз
              </h3>
              <div className="mt-2.5 space-y-2">
                {dashboard.by_delivery_method.map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-ink">{item.label}</span>
                    <span className="text-muted">
                      {item.orders_count} зам. ·{" "}
                      <strong className="text-ink">
                        {formatMoneyUah(item.revenue_kopecks)}
                      </strong>{" "}
                      ({item.share_percent}%)
                    </span>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
              <h3 className="font-display text-sm font-bold text-ink">
                Спосіб оплати
              </h3>
              <div className="mt-2.5 space-y-2">
                {dashboard.by_payment_method.map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-ink">{item.label}</span>
                    <span className="text-muted">
                      {item.orders_count} зам. ·{" "}
                      <strong className="text-ink">
                        {formatMoneyUah(item.revenue_kopecks)}
                      </strong>{" "}
                      ({item.share_percent}%)
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      )}

      {/* 2. MARKETING CHANNELS, UTM & PROMO CODES */}
      {subView === "marketing" && (
        <div className="space-y-4">
          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              Джерела замовлень (Order Source)
            </h3>
            <p className="text-xs text-muted">
              Звідки приходять реальні гроші: сайт, Instagram Direct, Telegram чи
              дзвінки
            </p>
            <div className="mt-3 space-y-2.5">
              {dashboard.by_order_source.map((src) => (
                <div key={src.key}>
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-ink">{src.label}</span>
                    <span>
                      <strong>{formatMoneyUah(src.revenue_kopecks)}</strong> ·{" "}
                      {src.orders_count} зам. ({src.share_percent}%)
                    </span>
                  </div>
                  <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-surface">
                    <div
                      className="h-full rounded-full bg-rose-deep"
                      style={{ width: `${Math.max(4, src.share_percent)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              UTM Джерела та Рекламні Кампанії
            </h3>
            <div className="mt-3 space-y-2">
              {dashboard.by_utm_source.map((utm) => (
                <div
                  key={utm.key}
                  className="flex items-center justify-between rounded-2xl bg-surface px-3 py-2 text-xs"
                >
                  <span className="font-bold text-ink">utm_source: {utm.label}</span>
                  <span>
                    {utm.orders_count} зам. ·{" "}
                    <strong>{formatMoneyUah(utm.revenue_kopecks)}</strong>
                  </span>
                </div>
              ))}
              {dashboard.by_utm_campaign.map((camp) => (
                <div
                  key={camp.key}
                  className="flex items-center justify-between rounded-2xl border border-line px-3 py-2 text-xs"
                >
                  <span className="font-semibold text-muted">
                    Кампанія: <strong className="text-ink">{camp.label}</strong>
                  </span>
                  <span>
                    {camp.orders_count} зам. ·{" "}
                    <strong>{formatMoneyUah(camp.revenue_kopecks)}</strong>
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              Ефективність промокодів (блогери / таргет)
            </h3>
            {dashboard.promo_codes.length === 0 ? (
              <p className="mt-2 text-xs text-muted">
                За обраний період замовлень із промокодами ще не було.
              </p>
            ) : (
              <div className="mt-3 space-y-2">
                {dashboard.promo_codes.map((p) => (
                  <div
                    key={p.promo_code}
                    className="flex items-center justify-between rounded-2xl bg-emerald-50/80 px-3.5 py-2.5 text-xs"
                  >
                    <div>
                      <span className="rounded-full bg-emerald-700 px-2.5 py-0.5 font-bold text-white">
                        {p.promo_code}
                      </span>
                      <span className="ml-2 text-muted">
                        Знижок на {formatMoneyUah(p.discount_kopecks)}
                      </span>
                    </div>
                    <div className="font-bold text-ink">
                      {p.orders_count} зам. ·{" "}
                      {formatMoneyUah(p.revenue_kopecks)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}

      {/* 3. TOP PRODUCTS, ZERO SALES & TAG GROUPS */}
      {subView === "products" && (
        <div className="space-y-4">
          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              🔥 Топ композицій за виручкою
            </h3>
            <div className="mt-3 space-y-2.5">
              {dashboard.top_products.map((prod, idx) => (
                <div
                  key={prod.product_id}
                  className="flex items-center justify-between rounded-2xl bg-surface px-3.5 py-2.5 text-xs"
                >
                  <div className="min-w-0 pr-2">
                    <span className="font-bold text-rose-deep">#{idx + 1}</span>{" "}
                    <span className="font-bold text-ink">
                      {prod.product_name}
                    </span>
                    <div className="text-[11px] text-muted">
                      Продано: {prod.units_sold} шт. у {prod.orders_count} зам.
                    </div>
                  </div>
                  <div className="shrink-0 font-display text-sm font-extrabold text-ink">
                    {formatMoneyUah(prod.revenue_kopecks)}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
            <h3 className="font-display text-sm font-bold text-ink">
              🎯 Які приводи, кольори та отримувачі продають найкраще
            </h3>
            <div className="mt-3 space-y-2">
              {dashboard.by_tag_group.map((tg) => (
                <div
                  key={`${tg.group}:${tg.tag_slug}`}
                  className="flex items-center justify-between rounded-2xl border border-line px-3 py-2 text-xs"
                >
                  <div>
                    <span className="rounded-full bg-accent-soft px-2 py-0.5 text-[10px] font-bold uppercase text-rose-deep">
                      {tg.group}
                    </span>{" "}
                    <span className="font-bold text-ink">{tg.tag_name}</span>
                  </div>
                  <div className="font-semibold text-ink">
                    {tg.units_sold} шт. · {formatMoneyUah(tg.revenue_kopecks)}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {dashboard.zero_sales_products.length > 0 && (
            <section className="rounded-3xl border border-amber-200 bg-amber-50/60 p-4">
              <h3 className="font-display text-sm font-bold text-amber-950">
                💤 Активні товари без продажів ({dashboard.zero_sales_products.length})
              </h3>
              <p className="mt-0.5 text-xs text-amber-900/80">
                Рекомендація для маркетингу: оновіть головне фото або запустіть у
                Stories зі старою ціною
              </p>
              <div className="mt-2.5 flex flex-wrap gap-1.5">
                {dashboard.zero_sales_products.slice(0, 12).map((p) => (
                  <span
                    key={p.product_id}
                    className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-ink shadow-sm"
                  >
                    {p.product_name}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* 4. CUSTOMER CRM & LTV */}
      {subView === "crm" && (
        <div className="space-y-3">
          <div className="flex gap-1.5 overflow-x-auto pb-1">
            {[
              { key: "", label: "Усі клієнти" },
              { key: "vip", label: "👑 VIP" },
              { key: "repeat", label: "🔁 Постійні" },
              { key: "sleeping", label: "💤 Сплячі (>90 дн)" },
            ].map((seg) => (
              <button
                key={seg.key}
                type="button"
                onClick={() => setSegmentFilter(seg.key)}
                className={`min-h-[36px] shrink-0 rounded-full px-3 text-xs font-bold ${
                  segmentFilter === seg.key
                    ? "bg-ink text-white"
                    : "border border-line bg-white text-ink"
                }`}
              >
                {seg.label}
              </button>
            ))}
          </div>

          {customers.map((c) => {
            const badge = SEGMENT_BADGES[c.segment];
            return (
              <div
                key={c.phone}
                className="rounded-3xl border border-line bg-white p-4 shadow-sm"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${badge.className}`}
                    >
                      {badge.label}
                    </span>
                    <h4 className="mt-1 font-display text-sm font-bold text-ink">
                      {c.name} ·{" "}
                      <span className="text-muted">{c.phone}</span>
                    </h4>
                  </div>
                  <div className="text-right">
                    <div className="font-display text-base font-extrabold text-ink">
                      LTV: {formatMoneyUah(c.ltv_kopecks)}
                    </div>
                    <div className="text-[11px] text-muted">
                      {c.orders_count} зам. · Сер. чек{" "}
                      {formatMoneyUah(c.avg_order_value_kopecks)}
                    </div>
                  </div>
                </div>

                {c.favorite_items.length > 0 && (
                  <div className="mt-2 text-xs text-muted">
                    Купували: {c.favorite_items.join(", ")}
                  </div>
                )}

                <div className="mt-3 flex items-center justify-between border-t border-line pt-2.5 text-xs">
                  <span className="text-muted">
                    Останнє зам.: {c.days_since_last_order} дн. тому
                  </span>
                  <div className="flex gap-2">
                    <a
                      href={`viber://chat?number=%2B${cleanPhoneDigits(
                        c.phone
                      )}`}
                      className="inline-flex items-center gap-1 rounded-full bg-surface px-3 py-1 font-bold text-purple-900"
                    >
                      <MessageCircle className="h-3.5 w-3.5" /> Viber
                    </a>
                    <a
                      href={`https://t.me/+${cleanPhoneDigits(c.phone)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 rounded-full bg-surface px-3 py-1 font-bold text-sky-900"
                    >
                      <Send className="h-3.5 w-3.5" /> Telegram
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 5. ORDER ANNIVERSARY RADAR */}
      {subView === "anniversaries" && (
        <div className="space-y-3">
          <div className="rounded-3xl border border-rose/30 bg-accent-soft/40 p-4">
            <div className="flex items-center gap-2 text-rose-deep">
              <Sparkles className="h-5 w-5" />
              <h3 className="font-display text-sm font-bold">
                Радар річниць замовлень (найближчі 21 день)
              </h3>
            </div>
            <p className="mt-1 text-xs text-ink/80">
              Клієнти, які рівно рік тому замовляли кульки на День народження чи
              свято. Напишіть їм за 3–7 днів до дати — це дає найвищу конверсію у
              повторне замовлення!
            </p>
          </div>

          {anniversaries.length === 0 ? (
            <div className="rounded-3xl border border-line bg-white p-6 text-center text-xs text-muted">
              На найближчі 21 день річниць минулорічних замовлень не знайдено.
            </div>
          ) : (
            anniversaries.map((ann) => {
              const greetingText = encodeURIComponent(
                `Вітаємо, ${ann.customer_name}! 🎈 Рік тому ми готували для вас святкову композицію (${ann.items_summary}). До свята залишилось зовсім трохи — підготувати для вас свіжу добірку кульок зі знижкою 10% для постійних клієнтів?`
              );
              return (
                <div
                  key={`${ann.order_number}-${ann.anniversary_date}`}
                  className="rounded-3xl border border-line bg-white p-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="rounded-full bg-rose-deep px-2.5 py-0.5 text-[11px] font-bold text-white">
                        🎂 Через {ann.days_until} дн. ({ann.anniversary_date})
                      </span>
                      <h4 className="mt-1.5 font-display text-sm font-bold text-ink">
                        {ann.customer_name} · {ann.customer_phone}
                      </h4>
                      <p className="mt-0.5 text-xs text-muted">
                        {ann.years_ago} р. тому ({ann.original_date}):{" "}
                        <strong className="text-ink">
                          {ann.items_summary}
                        </strong>
                      </p>
                    </div>
                    <div className="font-display text-sm font-extrabold text-ink">
                      {formatMoneyUah(ann.total_kopecks)}
                    </div>
                  </div>

                  <div className="mt-3 flex gap-2 border-t border-line pt-2.5">
                    <a
                      href={`viber://chat?number=%2B${cleanPhoneDigits(
                        ann.customer_phone
                      )}&draft=${greetingText}`}
                      className="flex min-h-[40px] flex-1 items-center justify-center gap-1.5 rounded-full bg-purple-700 px-3 text-xs font-bold text-white"
                    >
                      <MessageCircle className="h-3.5 w-3.5" /> Нагадати у Viber
                    </a>
                    <a
                      href={`https://t.me/+${cleanPhoneDigits(
                        ann.customer_phone
                      )}?text=${greetingText}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex min-h-[40px] flex-1 items-center justify-center gap-1.5 rounded-full bg-sky-600 px-3 text-xs font-bold text-white"
                    >
                      <Send className="h-3.5 w-3.5" /> Нагадати у TG
                    </a>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
