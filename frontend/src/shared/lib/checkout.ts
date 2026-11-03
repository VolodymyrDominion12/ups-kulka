/** Builds and validates the POST /api/v1/orders body (PlaceOrderIn in contracts/openapi.json). */

import type { CartState } from "./cart";
import { cartLines } from "./cart";
import { normalizeUaPhone } from "./phone";
import type { MarketingAttribution } from "./utm";

export type DeliveryMethod = "pickup" | "taxi";
export type PaymentMethod = "on_delivery" | "online";

export interface CheckoutForm {
  name: string;
  phone: string;
  deliveryMethod: DeliveryMethod;
  address: string;
  date: string; // yyyy-mm-dd or ""
  timeSlot: string;
  comment: string;
  paymentMethod: PaymentMethod;
}

export interface PlaceOrderBody {
  customer: { name: string; phone: string; comment: string };
  delivery: {
    method: DeliveryMethod;
    address: string | null;
    date: string | null;
    time_slot: string | null;
  };
  payment_method: PaymentMethod;
  items: { product_id: string; quantity: number }[];
  marketing: MarketingAttribution | null;
}

export type CheckoutField = "name" | "phone" | "address" | "date" | "cart";
export type CheckoutErrors = Partial<Record<CheckoutField, string>>;

export const TIME_SLOTS = ["10–12", "12–14", "14–16", "16–18", "18–20"] as const;

/** Today in Kyiv as yyyy-mm-dd: the earliest date a customer may choose. */
export function kyivToday(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Kyiv",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}

export function validateCheckout(
  form: CheckoutForm,
  cart: CartState,
  today: string = kyivToday(),
): CheckoutErrors {
  const errors: CheckoutErrors = {};
  if (cartLines(cart).length === 0) errors.cart = "Кошик порожній. Додайте композицію з каталогу.";
  if (!form.name.trim()) errors.name = "Вкажіть імʼя.";
  if (!normalizeUaPhone(form.phone)) errors.phone = "Вкажіть номер у форматі 093 123 45 67.";
  if (form.deliveryMethod === "taxi" && !form.address.trim()) {
    errors.address = "Вкажіть адресу, куди везти замовлення.";
  }
  if (form.date && form.date < today) errors.date = "Дата не може бути в минулому.";
  return errors;
}

export function buildOrderBody(
  form: CheckoutForm,
  cart: CartState,
  marketing: MarketingAttribution | null,
): PlaceOrderBody {
  const isTaxi = form.deliveryMethod === "taxi";
  return {
    customer: {
      name: form.name.trim(),
      phone: normalizeUaPhone(form.phone) ?? form.phone.trim(),
      comment: form.comment.trim(),
    },
    delivery: {
      method: form.deliveryMethod,
      address: isTaxi ? form.address.trim() : null,
      date: form.date || null,
      time_slot: form.timeSlot || null,
    },
    payment_method: form.paymentMethod,
    items: cartLines(cart).map((line) => ({
      product_id: line.product.id,
      quantity: line.quantity,
    })),
    marketing,
  };
}

/** Turns an API error body into a message for the customer. */
export function orderErrorMessage(status: number, body: unknown): string {
  const data = body as { code?: unknown; message?: unknown; detail?: unknown } | null;
  if (data && typeof data.message === "string" && data.message) {
    if (data.code === "product_unavailable") {
      return "Деяких товарів уже немає. Поверніться в кошик і приберіть їх.";
    }
    return data.message;
  }
  if (status === 422) return "Перевірте, будь ласка, поля форми.";
  if (status >= 500) return "Сервер тимчасово недоступний. Спробуйте ще раз за хвилину.";
  return `Не вдалося оформити замовлення (помилка ${status}).`;
}
