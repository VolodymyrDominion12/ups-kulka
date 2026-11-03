"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";

import { useCart } from "@/features/cart/CartProvider";
import { ATTRIBUTION_STORAGE_KEY } from "@/features/marketing/UtmCapture";
import { checkoutApi } from "@/shared/api/storefront";
import { SHOP } from "@/shared/config/shop";
import {
  TIME_SLOTS,
  buildOrderBody,
  kyivToday,
  orderErrorMessage,
  validateCheckout,
  type CheckoutErrors,
  type CheckoutForm as FormState,
  type DeliveryMethod,
  type PaymentMethod,
} from "@/shared/lib/checkout";
import { formatUah } from "@/shared/lib/money";
import { parseStoredAttribution } from "@/shared/lib/utm";

const EMPTY: FormState = {
  name: "",
  phone: "",
  deliveryMethod: "pickup",
  address: "",
  date: "",
  timeSlot: "",
  comment: "",
  paymentMethod: "on_delivery",
};

const FIELD_OF: Partial<Record<keyof FormState, keyof CheckoutErrors>> = {
  name: "name",
  phone: "phone",
  address: "address",
  deliveryMethod: "address",
  date: "date",
};

const inputClass =
  "h-12 w-full min-w-0 rounded-2xl border border-line bg-surface px-4 outline-none transition focus:border-rose focus:bg-white aria-[invalid=true]:border-[#b3261e]";

export function CheckoutForm() {
  const cart = useCart();
  const router = useRouter();
  const [form, setForm] = useState<FormState>(EMPTY);
  const [errors, setErrors] = useState<CheckoutErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [onlineEnabled, setOnlineEnabled] = useState(false);
  const today = kyivToday();

  useEffect(() => {
    checkoutApi.options().then((o) => setOnlineEnabled(o.payment_methods.includes("online")));
  }, []);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((f) => ({ ...f, [key]: value }));
    // A field the customer is fixing no longer shows its old error.
    const field = FIELD_OF[key];
    if (field) setErrors((e) => ({ ...e, [field]: undefined }));
  };

  if (cart.ready && cart.lines.length === 0) {
    return (
      <div className="rounded-panel bg-white p-8 text-center">
        <p className="font-display text-xl font-bold">Кошик порожній</p>
        <p className="mt-2 text-muted">Додайте композицію з каталогу, щоб оформити замовлення.</p>
        <Link
          href="/kulky"
          className="mt-6 inline-flex h-12 items-center rounded-full bg-ink px-6 font-bold text-white"
        >
          До каталогу
        </Link>
      </div>
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const found = validateCheckout(form, cart.state, today);
    setErrors(found);
    setServerError(null);
    if (Object.keys(found).length > 0) {
      const first = Object.keys(found)[0];
      document.getElementById(`co-${first}`)?.focus();
      return;
    }
    setBusy(true);
    let marketing = null;
    try {
      marketing = parseStoredAttribution(window.sessionStorage.getItem(ATTRIBUTION_STORAGE_KEY));
    } catch {
      marketing = null;
    }
    const result = await checkoutApi.placeOrder(buildOrderBody(form, cart.state, marketing));
    if (!result.ok) {
      setServerError(orderErrorMessage(result.status, result.body));
      setBusy(false);
      return;
    }
    cart.clear();
    if (result.order.payment_url) {
      window.location.assign(result.order.payment_url);
      return;
    }
    router.push(`/diakuiemo?order=${result.order.number}`);
  }

  return (
    <form onSubmit={submit} noValidate className="grid gap-5 lg:grid-cols-[1fr_340px] lg:items-start">
      <div className="grid gap-5 rounded-panel bg-white p-5 sm:p-7">
        <fieldset className="grid gap-4">
          <legend className="mb-1 font-display text-lg font-bold">Контакти</legend>
          <Field id="co-name" label="Імʼя" error={errors.name}>
            <input
              id="co-name"
              className={inputClass}
              autoComplete="given-name"
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              aria-invalid={!!errors.name}
              aria-describedby={errors.name ? "co-name-err" : undefined}
            />
          </Field>
          <Field id="co-phone" label="Телефон" error={errors.phone}>
            <input
              id="co-phone"
              className={inputClass}
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="093 123 45 67"
              value={form.phone}
              onChange={(e) => set("phone", e.target.value)}
              aria-invalid={!!errors.phone}
              aria-describedby={errors.phone ? "co-phone-err" : undefined}
            />
          </Field>
        </fieldset>

        <fieldset className="grid gap-4">
          <legend className="mb-1 font-display text-lg font-bold">Отримання</legend>
          <Segmented<DeliveryMethod>
            label="Спосіб отримання"
            value={form.deliveryMethod}
            onChange={(v) => set("deliveryMethod", v)}
            options={[
              ["pickup", "Самовивіз"],
              ["taxi", "Таксі"],
            ]}
          />
          {form.deliveryMethod === "taxi" ? (
            <Field
              id="co-address"
              label="Адреса в Києві"
              error={errors.address}
              hint="Таксі викличемо ми, поїздку ви оплачуєте за тарифом таксі."
            >
              <input
                id="co-address"
                className={inputClass}
                autoComplete="street-address"
                placeholder="Вулиця, будинок, підʼїзд, квартира"
                value={form.address}
                onChange={(e) => set("address", e.target.value)}
                aria-invalid={!!errors.address}
                aria-describedby={`co-address-hint${errors.address ? " co-address-err" : ""}`}
              />
            </Field>
          ) : (
            <p className="text-sm text-muted">
              Після оформлення менеджер зателефонує й підкаже адресу та час, коли замовлення буде готове.
            </p>
          )}
          <div className="grid grid-cols-2 gap-3">
            <Field id="co-date" label="Дата" error={errors.date}>
              <input
                id="co-date"
                type="date"
                min={today}
                className={inputClass}
                value={form.date}
                onChange={(e) => set("date", e.target.value)}
                aria-invalid={!!errors.date}
              />
            </Field>
            <Field id="co-slot" label="Час">
              <select
                id="co-slot"
                className={inputClass}
                value={form.timeSlot}
                onChange={(e) => set("timeSlot", e.target.value)}
              >
                <option value="">Будь-коли</option>
                {TIME_SLOTS.map((slot) => (
                  <option key={slot} value={slot}>
                    {slot}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <Field id="co-comment" label="Коментар">
            <textarea
              id="co-comment"
              rows={3}
              maxLength={1000}
              className={`${inputClass} h-auto py-3`}
              placeholder="Колір, напис на кульці, побажання"
              value={form.comment}
              onChange={(e) => set("comment", e.target.value)}
            />
          </Field>
        </fieldset>

        <fieldset className="grid gap-3">
          <legend className="mb-1 font-display text-lg font-bold">Оплата</legend>
          {onlineEnabled ? (
            <Segmented<PaymentMethod>
              label="Спосіб оплати"
              value={form.paymentMethod}
              onChange={(v) => set("paymentMethod", v)}
              options={[
                ["on_delivery", "При отриманні"],
                ["online", "Картою онлайн"],
              ]}
            />
          ) : (
            <p>При отриманні: готівкою або карткою.</p>
          )}
        </fieldset>
      </div>

      <aside className="grid gap-4 rounded-panel bg-white p-5 sm:p-7 lg:sticky lg:top-24">
        <h2 className="font-display text-lg font-bold">Ваше замовлення</h2>
        <ul className="grid gap-2 text-sm">
          {cart.lines.map((line) => (
            <li key={line.product.id} className="flex justify-between gap-3">
              <span className="min-w-0">
                {line.product.name} × {line.quantity}
              </span>
              <span className="shrink-0 tabular-nums">
                {formatUah(line.product.priceKopecks * line.quantity)}
              </span>
            </li>
          ))}
        </ul>
        <div className="flex justify-between border-t border-line pt-3 text-lg font-extrabold">
          <span>За товари</span>
          <span className="tabular-nums">{formatUah(cart.totalKopecks)}</span>
        </div>
        {form.deliveryMethod === "taxi" && (
          <p className="-mt-2 text-sm text-muted">Таксі оплачується окремо.</p>
        )}
        {errors.cart && <p className="text-sm text-[#b3261e]">{errors.cart}</p>}
        {serverError && (
          <p role="alert" className="rounded-2xl bg-[#fdecea] px-4 py-3 text-sm text-[#8c1d18]">
            {serverError}{" "}
            {serverError.includes("кошик") && (
              <Link href="/koshyk" className="underline">
                Відкрити кошик
              </Link>
            )}
          </p>
        )}
        <button
          type="submit"
          disabled={busy || !cart.ready}
          className="h-12 rounded-full bg-ink font-bold text-white transition hover:bg-rose-deep disabled:opacity-50"
        >
          {busy
            ? "Надсилаємо…"
            : form.paymentMethod === "online"
              ? "Перейти до оплати"
              : "Підтвердити замовлення"}
        </button>
        <p className="text-center text-sm text-muted">
          Питання? Телефонуйте{" "}
          <a href={`tel:${SHOP.phone}`} className="font-semibold text-ink">
            {SHOP.phoneLabel}
          </a>
        </p>
      </aside>
    </form>
  );
}

function Field({
  id,
  label,
  error,
  hint,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div className="grid min-w-0 gap-1.5">
      <label htmlFor={id} className="text-sm font-semibold">
        {label}
      </label>
      {children}
      {hint && (
        <p id={`${id}-hint`} className="text-[13px] text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-err`} className="text-[13px] text-[#b3261e]">
          {error}
        </p>
      )}
    </div>
  );
}

function Segmented<T extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: T;
  onChange: (value: T) => void;
  options: [T, string][];
}) {
  return (
    <div role="radiogroup" aria-label={label} className="grid grid-cols-2 rounded-full bg-accent-soft p-1">
      {options.map(([v, text]) => (
        <button
          key={v}
          type="button"
          role="radio"
          aria-checked={value === v}
          onClick={() => onChange(v)}
          className={`h-11 rounded-full font-bold transition ${
            value === v ? "bg-white text-ink shadow-sm" : "text-rose-deep"
          }`}
        >
          {text}
        </button>
      ))}
    </div>
  );
}
